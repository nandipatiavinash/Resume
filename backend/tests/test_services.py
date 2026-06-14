import pytest
import uuid
from app.services.ats_scorer import ATSScorer
from app.services.matcher import ProjectMatcher
from app.services.latex_renderer import LaTeXRenderer
from app.services.ai.factory import ProviderFactory
from app.schemas.resume import ResumeContent, JDAnalysis

# --- ATS Scorer Tests ---

def test_ats_scorer_score_calculation(mock_resume_content, mock_jd_analysis):
    report = ATSScorer.calculate_score(mock_resume_content, mock_jd_analysis)
    
    assert "score" in report
    assert 0 <= report["score"] <= 100
    assert "matched_keywords" in report
    assert "missing_keywords" in report
    assert "suggestions" in report
    assert len(report["suggestions"]) > 0

    # Ensure "fastapi" is identified as a matched keyword since it is in our skills and JD
    matched_kws = [k.lower() for k in report["matched_keywords"]]
    assert "fastapi" in matched_kws or "python" in matched_kws

# --- Project Matcher Tests ---

def test_project_matcher_ranking(mock_jd_analysis):
    projects = [
        {
            "name": "Java Backend",
            "description": "Enterprise Java application using Spring Boot and Oracle database.",
            "github_url": None
        },
        {
            "name": "FastAPI Web App",
            "description": "Python based async microservice backend with FastAPI, redis cache, and docker deployments.",
            "github_url": None
        }
    ]

    ranked = ProjectMatcher.rank_projects(
        projects=projects,
        jd_text="Looking for a Python developer with FastAPI and Docker experience.",
        jd_analysis=mock_jd_analysis,
        top_n=2
    )

    assert len(ranked) == 2
    # The FastAPI project should have a higher match score than the Java one
    assert ranked[0][0]["name"] == "FastAPI Web App"
    assert ranked[0][1] > ranked[1][1]

# --- LaTeX Renderer Tests ---

def test_latex_escape():
    assert LaTeXRenderer.escape_latex("Python & JavaScript") == "Python \\& JavaScript"
    assert LaTeXRenderer.escape_latex("100% Cotton") == "100\\% Cotton"
    assert LaTeXRenderer.escape_latex("Cost: $5.00") == "Cost: \\$5.00"
    assert LaTeXRenderer.escape_latex("user_name") == "user\\_name"

def test_latex_renderer_validation():
    incomplete_context = {
        "full_name": "John",
        "email": "john@test.com"
        # Missing summary, skills, experience, projects, education
    }
    
    with pytest.raises(ValueError) as excinfo:
        LaTeXRenderer.validate_placeholders(incomplete_context)
    
    assert "Missing mandatory resume fields" in str(excinfo.value)

# --- Provider Factory Tests ---

def test_provider_factory_invalid_provider():
    with pytest.raises(ValueError) as excinfo:
        ProviderFactory.get_provider("invalid_provider_name", "encrypted_key_abc")
    assert "Unsupported AI Provider" in str(excinfo.value)
