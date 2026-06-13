import json
import google.generativeai as genai
from typing import Optional
from backend.app.services.ai.base import AIProvider
from backend.app.schemas.resume import JDAnalysis, ResumeContent
import logging

logger = logging.getLogger("gemini_provider")

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, api_base: Optional[str] = None):
        genai.configure(api_key=api_key)
        self.model_name = "gemini-1.5-flash"

    async def _call_ai_json(self, system_prompt: str, user_prompt: str) -> dict:
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt
            )
            # Use generate_content_async for async support
            response = await model.generate_content_async(
                user_prompt,
                generation_config={"response_mime_type": "application/json", "temperature": 0.2}
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise RuntimeError(f"Gemini error: {str(e)}")

    async def _call_ai_text(self, system_prompt: str, user_prompt: str) -> str:
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt
            )
            response = await model.generate_content_async(
                user_prompt,
                generation_config={"temperature": 0.7}
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise RuntimeError(f"Gemini error: {str(e)}")

    async def analyze_jd(self, jd_text: str) -> JDAnalysis:
        system_prompt = (
            "You are an expert ATS recruiter. Analyze the job description and extract data. "
            "Output a JSON object conforming exactly to this structure: "
            '{"required_skills": ["skill1", ...], "preferred_skills": ["skill2", ...], '
            '"ats_keywords": ["keyword1", ...], "responsibilities": ["resp1", ...], '
            '"role_summary": "overall role objective"}'
        )
        user_prompt = f"Job Description:\n{jd_text}"
        data = await self._call_ai_json(system_prompt, user_prompt)
        return JDAnalysis(**data)

    async def generate_resume(
        self, profile_data: dict, jd_analysis: JDAnalysis, template_name: str
    ) -> ResumeContent:
        system_prompt = (
            "You are a professional resume writer. Given a master profile and a job description analysis, "
            "generate an optimized, tailored resume. Align projects, experience details, and skills to highlight "
            "relevance, using strong action verbs and quantified impact where possible. "
            "Output the results in strict JSON conforming to this structure: "
            "{"
            '"full_name": "...", "email": "...", "phone": "...", "website": "...", "github_url": "...", "linkedin_url": "...", '
            '"summary": "professional summary matching role objectives", '
            '"education": [{"institution": "...", "degree": "...", "field_of_study": "...", "start_date": "...", "end_date": "...", "gpa": "...", "description": "..."}], '
            '"skills": [{"name": "...", "category": "Languages|Frameworks|Tools|etc.", "proficiency": "..."}], '
            '"experience": [{"company": "...", "position": "...", "location": "...", "start_date": "...", "end_date": "...", "description": "...", "bullets": ["quantified action statement", ...]}], '
            '"certifications": [{"name": "...", "issuer": "...", "issue_date": "...", "expiration_date": "...", "url": "..."}], '
            '"achievements": [{"title": "...", "description": "...", "date": "..."}], '
            '"projects": [{"name": "...", "description": "...", "url": "...", "github_url": "...", "start_date": "...", "end_date": "...", "bullets": ["bullet detail", ...]}]'
            "}"
        )
        user_prompt = f"Master Profile:\n{json.dumps(profile_data)}\n\nJD Analysis:\n{jd_analysis.model_dump_json()}"
        data = await self._call_ai_json(system_prompt, user_prompt)
        return ResumeContent(**data)

    async def analyze_github_project(self, repo_meta: dict, files_content: dict) -> dict:
        system_prompt = (
            "You are a technical analyst. Review the repository files and metadata to extract: "
            "1. A 2-sentence project summary. "
            "2. 4-6 resume-style, highly professional bullet points highlighting technologies, actions, and simulated business/technical metrics. "
            "3. A single business impact statement. "
            "4. A complexity score from 1 to 10. "
            "5. A list of detected technologies. "
            "Output must be a JSON object with keys: "
            '{"summary": "...", "bullets": ["...", ...], "business_impact": "...", "complexity_score": 7, "technologies": ["...", ...]}'
        )
        user_prompt = f"Repo Meta:\n{json.dumps(repo_meta)}\n\nFiles Content:\n{json.dumps(files_content)}"
        return await self._call_ai_json(system_prompt, user_prompt)

    async def generate_cover_letter(
        self, profile_data: dict, jd_text: str, tone: str
    ) -> str:
        system_prompt = f"You are a cover letter writer. Tone requested: {tone}."
        user_prompt = f"Profile:\n{json.dumps(profile_data)}\n\nJob Description:\n{jd_text}"
        return await self._call_ai_text(system_prompt, user_prompt)

    async def improve_text(self, text: str, context: str) -> str:
        system_prompt = f"Improve this resume text for a professional context: {context}. Keep the output concise."
        return await self._call_ai_text(system_prompt, text)
