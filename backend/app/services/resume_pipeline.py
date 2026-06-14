import json
import uuid
import logging
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import SessionLocal
from app.models import (
    User, Profile, AIProviderConfig, Template, ResumeGeneration, JobDescription, ATSReport, Project
)
from app.services.ai.factory import ProviderFactory
from app.services.matcher import ProjectMatcher
from app.services.latex_renderer import LaTeXRenderer
from app.services.pdf_compiler import PDFCompiler
from app.services.s3_service import s3_service
from app.services.ats_scorer import ATSScorer
from app.schemas.resume import JDAnalysis, ResumeContent

logger = logging.getLogger("resume_pipeline")

class ResumePipeline:
    @classmethod
    async def run(cls, generation_id: uuid.UUID) -> None:
        """
        Executes the 9-step resume generation pipeline.
        """
        async with SessionLocal() as db:
            # Load the generation record
            stmt = select(ResumeGeneration).where(ResumeGeneration.id == generation_id)
            result = await db.execute(stmt)
            gen_record = result.scalar_one_or_none()
            if not gen_record:
                logger.error(f"ResumeGeneration record {generation_id} not found.")
                return

            try:
                # Update status to processing
                gen_record.status = "processing"
                await db.commit()
                await db.refresh(gen_record)

                user_id = gen_record.user_id
                jd_id = gen_record.jd_id
                template_id = gen_record.template_id

                # 1. Load full user profile from DB
                logger.info(f"[Step 1] Loading master profile for user {user_id}")
                profile_stmt = select(Profile).where(Profile.user_id == user_id).options(
                    selectinload(Profile.educations),
                    selectinload(Profile.skills),
                    selectinload(Profile.experiences),
                    selectinload(Profile.certifications),
                    selectinload(Profile.achievements),
                    selectinload(Profile.projects).selectinload(Project.analysis)
                )
                profile_res = await db.execute(profile_stmt)
                profile = profile_res.scalar_one_or_none()
                if not profile:
                    raise ValueError("Master profile not found. Please create your profile before generating resumes.")

                # Load Job Description
                jd_stmt = select(JobDescription).where(JobDescription.id == jd_id)
                jd_res = await db.execute(jd_stmt)
                jd_record = jd_res.scalar_one_or_none()
                if not jd_record:
                    raise ValueError(f"Job Description {jd_id} not found.")

                # Load Template
                template_stmt = select(Template).where(Template.id == template_id)
                template_res = await db.execute(template_stmt)
                template_record = template_res.scalar_one_or_none()
                if not template_record:
                    raise ValueError(f"Template {template_id} not found.")

                # Get AI Provider Config
                provider_stmt = select(AIProviderConfig).where(
                    AIProviderConfig.user_id == user_id,
                    AIProviderConfig.is_active == True
                )
                provider_res = await db.execute(provider_stmt)
                provider_config = provider_res.scalar_one_or_none()
                
                # Dynamic fallback for testing if user API keys are missing
                if not provider_config:
                    import os
                    openai_key = os.getenv("OPENAI_API_KEY")
                    if openai_key:
                        logger.info("No active provider config in DB. Falling back to system OPENAI_API_KEY.")
                        from app.core.security import encrypt_api_key
                        encrypted_key = encrypt_api_key(openai_key)
                        provider_config = AIProviderConfig(
                            provider_name="openai",
                            encrypted_api_key=encrypted_key,
                            api_base=os.getenv("OPENAI_API_BASE")
                        )
                    else:
                        raise ValueError(
                            "AI Provider API key is not configured. Please add an API key in settings."
                        )

                ai_provider = ProviderFactory.get_provider(
                    provider_name=provider_config.provider_name,
                    encrypted_api_key=provider_config.encrypted_api_key,
                    api_base=provider_config.api_base
                )

                # 2. Call ai.analyze_jd() if it hasn't been analyzed yet
                logger.info("[Step 2] Analyzing Job Description")
                if not jd_record.analyzed_skills or not jd_record.analyzed_keywords:
                    jd_analysis = await ai_provider.analyze_jd(jd_record.jd_text)
                    jd_record.analyzed_skills = jd_analysis.required_skills + jd_analysis.preferred_skills
                    jd_record.analyzed_keywords = jd_analysis.ats_keywords
                    jd_record.parsed_jd_json = jd_analysis.model_dump()
                    await db.commit()
                else:
                    jd_analysis = JDAnalysis(**jd_record.parsed_jd_json)

                # 3. Score each project 0-100 and select top N
                logger.info("[Step 3] Ranking projects against Job Description")
                all_projects = [
                    {
                        "id": p.id,
                        "name": p.name,
                        "description": p.description,
                        "url": p.url,
                        "github_url": p.github_url,
                        "analysis": {
                            "summary": p.analysis.summary,
                            "bullets": p.analysis.bullets,
                            "business_impact": p.analysis.business_impact,
                            "complexity_score": p.analysis.complexity_score,
                            "technologies": p.analysis.technologies,
                        } if p.analysis else None
                    } for p in profile.projects
                ]
                
                # Rank and select top 3 projects
                top_n = gen_record.generation_metadata.get("top_n_projects", 3)
                ranked_projects = ProjectMatcher.rank_projects(all_projects, jd_record.jd_text, jd_analysis, top_n=top_n)
                logger.info(f"Selected {len(ranked_projects)} projects. High-score project: {[p[0]['name'] for p in ranked_projects]}")

                # Build profile structure with only ranked projects
                profile_dict = {
                    "full_name": profile.full_name,
                    "email": profile.email,
                    "phone": profile.phone,
                    "website": profile.website,
                    "github_url": profile.github_url,
                    "linkedin_url": profile.linkedin_url,
                    "summary": profile.summary,
                    "education": [
                        {
                            "institution": e.institution,
                            "degree": e.degree,
                            "field_of_study": e.field_of_study,
                            "start_date": e.start_date,
                            "end_date": e.end_date,
                            "gpa": e.gpa,
                            "description": e.description
                        } for e in profile.educations
                    ],
                    "skills": [
                        {
                            "name": s.name,
                            "category": s.category,
                            "proficiency": s.proficiency
                        } for s in profile.skills
                    ],
                    "experience": [
                        {
                            "company": ex.company,
                            "position": ex.position,
                            "location": ex.location,
                            "start_date": ex.start_date,
                            "end_date": ex.end_date,
                            "description": ex.description,
                            "bullets": ex.bullets
                        } for ex in profile.experiences
                    ],
                    "certifications": [
                        {
                            "name": c.name,
                            "issuer": c.issuer,
                            "issue_date": c.issue_date,
                            "expiration_date": c.expiration_date,
                            "url": c.url
                        } for c in profile.certifications
                    ],
                    "achievements": [
                        {
                            "title": a.title,
                            "description": a.description,
                            "date": a.date
                        } for a in profile.achievements
                    ],
                    "projects": [
                        {
                            "name": p["name"],
                            "description": p["description"],
                            "url": p["url"],
                            "github_url": p["github_url"],
                            "bullets": p["analysis"]["bullets"] if p["analysis"] else [p["description"] or ""]
                        } for p, score in ranked_projects
                    ]
                }

                # 4. Call ai.generate_resume()
                logger.info("[Step 4] Requesting AI optimized resume content")
                resume_content = await ai_provider.generate_resume(
                    profile_data=profile_dict,
                    jd_analysis=jd_analysis,
                    template_name=template_record.name
                )

                # 5. Call latex_renderer.py
                logger.info("[Step 5] Rendering LaTeX template")
                rendered_tex = LaTeXRenderer.render_template(
                    template_source=template_record.latex_source,
                    resume_content=resume_content
                )

                # 6. Call pdf_compiler.py
                logger.info("[Step 6] Compiling PDF via XeLaTeX")
                gen_record.status = "compiling"
                await db.commit()
                
                pdf_bytes = await PDFCompiler.compile_tex(rendered_tex)

                # 7. Upload PDF + .tex + .json to S3
                logger.info("[Step 7] Uploading files to storage")
                pdf_key = f"resumes/{user_id}/{generation_id}.pdf"
                tex_key = f"resumes/{user_id}/{generation_id}.tex"
                json_key = f"resumes/{user_id}/{generation_id}.json"

                await s3_service.upload_file(pdf_bytes, pdf_key, "application/pdf")
                await s3_service.upload_file(rendered_tex.encode("utf-8"), tex_key, "application/x-tex")
                await s3_service.upload_file(resume_content.model_dump_json().encode("utf-8"), json_key, "application/json")

                # 8. Save ResumeGeneration record to DB
                logger.info("[Step 8] Updating generation metadata")
                gen_record.latex_content = rendered_tex
                gen_record.pdf_s3_url = pdf_key
                gen_record.tex_s3_url = tex_key
                gen_record.json_s3_url = json_key
                gen_record.status = "completed"

                # 9. Compute ATS score and save ATSReport
                logger.info("[Step 9] Calculating ATS compatibility")
                ats_report_data = ATSScorer.calculate_score(resume_content, jd_analysis)
                
                # Check for existing report
                report_stmt = select(ATSReport).where(ATSReport.resume_generation_id == generation_id)
                report_res = await db.execute(report_stmt)
                ats_report = report_res.scalar_one_or_none()
                
                if not ats_report:
                    ats_report = ATSReport(
                        resume_generation_id=generation_id,
                        user_id=user_id,
                        score=ats_report_data["score"],
                        matched_keywords=ats_report_data["matched_keywords"],
                        missing_keywords=ats_report_data["missing_keywords"],
                        weak_sections=ats_report_data["weak_sections"],
                        suggestions=ats_report_data["suggestions"],
                        format_score=ats_report_data["format_score"],
                        action_verb_score=ats_report_data["action_verb_score"]
                    )
                    db.add(ats_report)
                else:
                    ats_report.score = ats_report_data["score"]
                    ats_report.matched_keywords = ats_report_data["matched_keywords"]
                    ats_report.missing_keywords = ats_report_data["missing_keywords"]
                    ats_report.weak_sections = ats_report_data["weak_sections"]
                    ats_report.suggestions = ats_report_data["suggestions"]
                    ats_report.format_score = ats_report_data["format_score"]
                    ats_report.action_verb_score = ats_report_data["action_verb_score"]

                await db.commit()
                logger.info(f"Resume optimization pipeline completed successfully for task {generation_id}")

            except Exception as e:
                logger.error(f"ResumePipeline failed on execution {generation_id}: {e}", exc_info=True)
                # Rollback changes and update status to failed
                await db.rollback()
                
                # Re-fetch session-independent object to set status
                stmt = select(ResumeGeneration).where(ResumeGeneration.id == generation_id)
                result = await db.execute(stmt)
                gen_record = result.scalar_one_or_none()
                if gen_record:
                    gen_record.status = "failed"
                    gen_record.error_message = str(e)
                    await db.commit()
                raise
