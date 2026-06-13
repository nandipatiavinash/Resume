from abc import ABC, abstractmethod
from backend.app.schemas.resume import JDAnalysis, ResumeContent
from backend.app.schemas.profile import ProjectAnalysisResponse
import uuid

class AIProvider(ABC):
    
    @abstractmethod
    async def analyze_jd(self, jd_text: str) -> JDAnalysis:
        """
        Analyze the job description and extract required skills, preferred skills,
        ATS keywords, and key responsibilities.
        """
        pass

    @abstractmethod
    async def generate_resume(
        self, profile_data: dict, jd_analysis: JDAnalysis, template_name: str
    ) -> ResumeContent:
        """
        Generate optimized, tailored resume content combining user's master profile,
        matched projects, and JD analysis.
        """
        pass

    @abstractmethod
    async def analyze_github_project(self, repo_meta: dict, files_content: dict) -> dict:
        """
        Analyze a GitHub repository based on its metadata and file contents.
        Returns a dictionary containing summary, bullets, business_impact, complexity_score, and technologies.
        """
        pass

    @abstractmethod
    async def generate_cover_letter(
        self, profile_data: dict, jd_text: str, tone: str
    ) -> str:
        """
        Generate a tailored cover letter matching the profile and job description with specified tone.
        """
        pass

    @abstractmethod
    async def improve_text(self, text: str, context: str) -> str:
        """
        Improve a block of text given the editing context.
        """
        pass
