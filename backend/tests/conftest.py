import pytest
import uuid
from typing import Dict, Any
from backend.app.schemas.resume import ResumeContent, EducationContent, SkillContent, ExperienceContent, JDAnalysis, ProjectContent

@pytest.fixture
def mock_profile() -> Dict[str, Any]:
    return {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "+1234567890",
        "website": "https://janedoe.com",
        "github_url": "github.com/janedoe",
        "linkedin_url": "linkedin.com/in/janedoe",
        "summary": "Experienced Full Stack Engineer with strong TypeScript and Python skills.",
        "educations": [
            {
                "institution": "Stanford University",
                "degree": "B.S.",
                "field_of_study": "Computer Science",
                "start_date": "2018",
                "end_date": "2022",
                "gpa": "3.9",
                "description": "Graduated with Honors."
            }
        ],
        "skills": [
            {"name": "Python", "category": "Languages", "proficiency": "Expert"},
            {"name": "FastAPI", "category": "Frameworks", "proficiency": "Expert"},
            {"name": "TypeScript", "category": "Languages", "proficiency": "Intermediate"}
        ],
        "experiences": [
            {
                "company": "Tech Corp",
                "position": "Software Engineer II",
                "location": "San Francisco, CA",
                "start_date": "2022",
                "end_date": "Present",
                "description": "Building microservices.",
                "bullets": ["Led development of user auth service.", "Reduced query latencies by 35% through Redis caching."]
            }
        ],
        "projects": [
            {
                "id": uuid.uuid4(),
                "name": "E-Commerce Pipeline",
                "description": "High throughput checkout backend.",
                "github_url": "https://github.com/janedoe/checkout-pipeline",
                "start_date": "2023",
                "end_date": "2023"
            }
        ]
    }

@pytest.fixture
def mock_jd_analysis() -> JDAnalysis:
    return JDAnalysis(
        required_skills=["Python", "FastAPI", "Redis", "Docker"],
        preferred_skills=["TypeScript", "AWS"],
        ats_keywords=["Microservices", "Query latency", "Auth", "Scalability"],
        responsibilities=["Develop and scale web APIs", "Maintain cloud deployments"],
        role_summary="Backend Software Engineer to scale real-time API integrations."
    )

@pytest.fixture
def mock_resume_content() -> ResumeContent:
    return ResumeContent(
        full_name="Jane Doe",
        email="jane@example.com",
        phone="+1234567890",
        website="https://janedoe.com",
        github_url="github.com/janedoe",
        linkedin_url="linkedin.com/in/janedoe",
        summary="Experienced Full Stack Engineer with strong TypeScript and Python skills.",
        education=[
            EducationContent(
                institution="Stanford University",
                degree="B.S.",
                field_of_study="Computer Science",
                start_date="2018",
                end_date="2022",
                gpa="3.9",
                description="Graduated with Honors."
            )
        ],
        skills=[
            SkillContent(name="Python", category="Languages", proficiency="Expert"),
            SkillContent(name="FastAPI", category="Frameworks", proficiency="Expert"),
            SkillContent(name="TypeScript", category="Languages", proficiency="Intermediate")
        ],
        experience=[
            ExperienceContent(
                company="Tech Corp",
                position="Software Engineer II",
                location="San Francisco, CA",
                start_date="2022",
                end_date="Present",
                description="Building microservices.",
                bullets=["Led development of user auth service.", "Reduced query latencies by 35% through Redis caching."]
            )
        ],
        certifications=[],
        achievements=[],
        projects=[
            ProjectContent(
                name="E-Commerce Pipeline",
                description="High throughput checkout backend.",
                url=None,
                github_url="https://github.com/janedoe/checkout-pipeline",
                start_date="2023",
                end_date="2023",
                bullets=["Built high throughput checkout backend processing 10k req/min.", "Utilized FastAPI, Python, and Redis."]
            )
        ]
    )
