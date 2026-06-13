import re
from typing import List, Dict, Any
from backend.app.schemas.resume import ResumeContent, JDAnalysis

# List of strong action verbs popular on professional resumes
ACTION_VERBS = {
    "designed", "built", "implemented", "developed", "led", "managed", "optimized",
    "reduced", "increased", "created", "architected", "facilitated", "orchestrated",
    "spearheaded", "automated", "streamlined", "improved", "transformed", "delivered",
    "coordinated", "resolved", "pioneered", "initiated", "executed", "collaborated",
    "engineered", "accelerated", "maximized", "restructured", "integrated"
}

class ATSScorer:
    @staticmethod
    def _extract_full_text(resume: ResumeContent) -> str:
        """
        Flattens the structured resume into a single block of lowercased text for keyword searching.
        """
        parts = [
            resume.full_name,
            resume.summary,
            " ".join(s.name for s in resume.skills),
            " ".join(s.category or "" for s in resume.skills)
        ]
        
        for exp in resume.experience:
            parts.append(exp.company)
            parts.append(exp.position)
            parts.append(exp.description or "")
            parts.extend(exp.bullets)

        for proj in resume.projects:
            parts.append(proj.name)
            parts.append(proj.description or "")
            parts.extend(proj.bullets)

        for edu in resume.education:
            parts.append(edu.institution)
            parts.append(edu.degree)
            parts.append(edu.field_of_study)
            parts.append(edu.description or "")

        return " ".join(parts).lower()

    @classmethod
    def calculate_score(cls, resume: ResumeContent, jd_analysis: JDAnalysis) -> Dict[str, Any]:
        resume_text = cls._extract_full_text(resume)
        
        # 1. Keyword match score
        # Combine required skills and ATS keywords
        keywords_to_check = set(
            [k.lower() for k in jd_analysis.required_skills] +
            [k.lower() for k in jd_analysis.ats_keywords]
        )
        
        matched_keywords = []
        missing_keywords = []
        
        if keywords_to_check:
            for kw in keywords_to_check:
                # Use word boundaries for accurate keyword matching
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, resume_text):
                    matched_keywords.append(kw)
                else:
                    missing_keywords.append(kw)
            keyword_score = int((len(matched_keywords) / len(keywords_to_check)) * 100)
        else:
            keyword_score = 100

        # 2. Section completeness score (20 points per section)
        sections = {
            "summary": bool(resume.summary.strip()),
            "skills": len(resume.skills) > 0,
            "experience": len(resume.experience) > 0,
            "projects": len(resume.projects) > 0,
            "education": len(resume.education) > 0
        }
        completeness_score = sum(20 for val in sections.values() if val)
        weak_sections = [sec for sec, present in sections.items() if not present]

        # 3. Format score (No tables, no images, correct text sizes)
        # Since our LaTeX templates compile to standard single/two-column text sheets, the score is mostly 100.
        # However, we deduct points if contact information is completely missing.
        format_score = 100
        format_suggestions = []
        if not resume.email or not resume.phone:
            format_score -= 20
            format_suggestions.append("Ensure your email and phone number are clearly visible in the header.")

        # 4. Action verb score
        words = re.findall(r'\b[a-z]+\b', resume_text)
        action_verb_count = sum(1 for w in words if w in ACTION_VERBS)
        
        # Goal: At least 8 strong action verbs
        action_verb_score = min(int((action_verb_count / 8) * 100), 100)

        # 5. Overall weighted score
        # 40% Keyword match, 30% Completeness, 10% Format, 20% Action Verbs
        overall_score = int(
            (keyword_score * 0.40) +
            (completeness_score * 0.30) +
            (format_score * 0.10) +
            (action_verb_score * 0.20)
        )

        # Generate suggestions list
        suggestions = []
        if missing_keywords:
            suggestions.append(f"Incorporate these missing skills/keywords: {', '.join(missing_keywords[:6])}.")
        for sec in weak_sections:
            suggestions.append(f"Add a '{sec.capitalize()}' section to make your resume complete.")
        if action_verb_count < 8:
            suggestions.append(f"Use more strong action verbs (found {action_verb_count}, target is at least 8). Examples: SPEARHEADED, SYSTEMATIZED.")
        suggestions.extend(format_suggestions)

        return {
            "score": overall_score,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "weak_sections": weak_sections,
            "suggestions": suggestions,
            "format_score": format_score,
            "action_verb_score": action_verb_score
        }
