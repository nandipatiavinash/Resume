import asyncio
import uuid
from celery import Celery
from app.core.config import settings
from app.services.resume_pipeline import ResumePipeline
from app.services.github_analyzer import github_analyzer
from app.services.ai.factory import ProviderFactory
from app.core.database import SessionLocal
from app.models import Project, ProjectAnalysis, AIProviderConfig
from sqlalchemy.future import select
import logging

logger = logging.getLogger("celery_tasks")

# Initialize Celery app
celery_app = Celery(
    "resume_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Helper function to run async tasks in sync celery worker threads
def run_async(coro):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Running inside an active loop (e.g. testing)
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result()
    else:
        return asyncio.run(coro)

@celery_app.task(name="tasks.generate_resume")
def generate_resume_task(generation_id_str: str) -> None:
    """
    Background worker task to orchestrate the 9-step resume builder.
    """
    logger.info(f"Starting Celery resume generation task for ID: {generation_id_str}")
    generation_id = uuid.UUID(generation_id_str)
    
    async def async_wrapper():
        await ResumePipeline.run(generation_id)
        
    run_async(async_wrapper())
    logger.info(f"Finished Celery resume generation task for ID: {generation_id_str}")

@celery_app.task(name="tasks.analyze_github_project")
def analyze_github_task(project_id_str: str, user_id_str: str) -> None:
    """
    Background worker task to perform GitHub repository code analysis.
    """
    logger.info(f"Starting Celery GitHub analysis task for project: {project_id_str}")
    project_id = uuid.UUID(project_id_str)
    user_id = uuid.UUID(user_id_str)

    async def async_wrapper():
        async with SessionLocal() as db:
            # 1. Fetch Project Details
            proj_stmt = select(Project).where(Project.id == project_id)
            proj_res = await db.execute(proj_stmt)
            project = proj_res.scalar_one_or_none()
            if not project or not project.github_url:
                logger.error(f"Project {project_id_str} not found or lacks GitHub URL.")
                return

            # 2. Get active AI Provider Config for user
            provider_stmt = select(AIProviderConfig).where(
                AIProviderConfig.user_id == user_id,
                AIProviderConfig.is_active == True
            )
            provider_res = await db.execute(provider_stmt)
            provider_config = provider_res.scalar_one_or_none()

            # Dynamic fallback for testing if API keys aren't configured in DB
            if not provider_config:
                import os
                openai_key = os.getenv("OPENAI_API_KEY")
                if openai_key:
                    from app.core.security import encrypt_api_key
                    encrypted_key = encrypt_api_key(openai_key)
                    provider_config = AIProviderConfig(
                        provider_name="openai",
                        encrypted_api_key=encrypted_key,
                        api_base=os.getenv("OPENAI_API_BASE")
                    )
                else:
                    logger.error(f"Cannot run GitHub analysis: AI provider config missing for user {user_id_str}")
                    return

            ai_provider = ProviderFactory.get_provider(
                provider_name=provider_config.provider_name,
                encrypted_api_key=provider_config.encrypted_api_key,
                api_base=provider_config.api_base
            )

            # 3. Trigger GitHub Analysis
            try:
                analysis_dict = await github_analyzer.analyze_repo(
                    repo_url=project.github_url,
                    ai_provider=ai_provider,
                    github_token=settings.GITHUB_TOKEN if settings.GITHUB_TOKEN else None
                )
            except Exception as e:
                logger.exception(f"Error during GitHub analysis for project {project_id_str}: {e}")
                return

            # 4. Save analysis record
            analysis_stmt = select(ProjectAnalysis).where(ProjectAnalysis.project_id == project_id)
            analysis_res = await db.execute(analysis_stmt)
            analysis = analysis_res.scalar_one_or_none()

            if not analysis:
                analysis = ProjectAnalysis(
                    project_id=project_id,
                    summary=analysis_dict["summary"],
                    bullets=analysis_dict["bullets"],
                    business_impact=analysis_dict["business_impact"],
                    complexity_score=analysis_dict["complexity_score"],
                    technologies=analysis_dict["technologies"]
                )
                db.add(analysis)
            else:
                analysis.summary = analysis_dict["summary"]
                analysis.bullets = analysis_dict["bullets"]
                analysis.business_impact = analysis_dict["business_impact"]
                analysis.complexity_score = analysis_dict["complexity_score"]
                analysis.technologies = analysis_dict["technologies"]

            await db.commit()
            logger.info(f"GitHub analysis successfully saved to database for project {project_id_str}")

    run_async(async_wrapper())
