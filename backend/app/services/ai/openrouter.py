import json
import re
from typing import Optional
import httpx
from app.services.ai.base import AIProvider
from app.schemas.resume import JDAnalysis, ResumeContent
import logging

logger = logging.getLogger("openrouter_provider")

class OpenRouterProvider(AIProvider):
    def __init__(self, api_key: str, api_base: Optional[str] = None):
        self.api_key = api_key
        self.api_base = api_base or "https://openrouter.ai/api/v1"
        self.model = "meta-llama/llama-3-8b-instruct:free"

    def _clean_json_string(self, text: str) -> str:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    async def _call_ai_json(self, system_prompt: str, user_prompt: str) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://resumeplatform.com",
            "X-Title": "Resume Platform",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                res_data = response.json()
                raw_text = res_data["choices"][0]["message"]["content"]
                clean_text = self._clean_json_string(raw_text)
                return json.loads(clean_text)
            except Exception as e:
                logger.error(f"OpenRouter API call failed: {e}")
                raise RuntimeError(f"OpenRouter error: {str(e)}")

    async def _call_ai_text(self, system_prompt: str, user_prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://resumeplatform.com",
            "X-Title": "Resume Platform",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                res_data = response.json()
                return res_data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.error(f"OpenRouter API call failed: {e}")
                raise RuntimeError(f"OpenRouter error: {str(e)}")

    async def analyze_jd(self, jd_text: str) -> JDAnalysis:
        system_prompt = (
            "You are an expert ATS recruiter. Analyze the job description and extract data. "
            "Output JSON format exactly like: "
            '{"required_skills": ["skill1", ...], "preferred_skills": ["skill2", ...], '
            '"ats_keywords": ["keyword1", ...], "responsibilities": ["resp1", ...], '
            '"role_summary": "overall role objective"}. '
            "Only output the JSON block, no other text."
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
            "}. Only output the JSON block, no other text."
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
            '{"summary": "...", "bullets": ["...", ...], "business_impact": "...", "complexity_score": 7, "technologies": ["...", ...]}. '
            "Only output the JSON block, no other text."
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
