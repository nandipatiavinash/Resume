import re
import json
import httpx
import redis
from typing import Optional, Dict, Any, List
from backend.app.core.config import settings
from backend.app.services.ai.base import AIProvider
import logging

logger = logging.getLogger("github_analyzer")

class GitHubAnalyzer:
    def __init__(self):
        # Configure Redis cache with fallback
        self.redis_client = None
        if settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
            except Exception as e:
                logger.warning(f"Could not connect to Redis: {e}. Falling back to in-memory caching.")
        
        self.memory_cache = {} # fallback in-memory cache

    def _get_cache(self, key: str) -> Optional[str]:
        if self.redis_client:
            try:
                val = self.redis_client.get(key)
                return val.decode() if val else None
            except Exception as e:
                logger.error(f"Redis get failed: {e}")
        return self.memory_cache.get(key)

    def _set_cache(self, key: str, value: str, ttl: int = 3600) -> None:
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, value)
                return
            except Exception as e:
                logger.error(f"Redis set failed: {e}")
        self.memory_cache[key] = value

    @staticmethod
    def parse_repo_url(url: str) -> Optional[Tuple[str, str]]:
        """
        Extracts owner and repo name from GitHub URL.
        """
        pattern = r"github\.com/([a-zA-Z0-9\-_\.]+)/([a-zA-Z0-9\-_\.]+)"
        match = re.search(pattern, url)
        if match:
            # Strip trailing slash or .git
            owner = match.group(1)
            repo = match.group(2)
            if repo.endswith(".git"):
                repo = repo[:-4]
            return owner, repo
        return None

    async def fetch_file_content(self, client: httpx.AsyncClient, owner: str, repo: str, path: str, headers: dict) -> Optional[str]:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "content" in data:
                    # Content is base64 encoded
                    import base64
                    decoded = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                    return decoded
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch {path} from {owner}/{repo}: {e}")
            return None

    async def analyze_repo(
        self, repo_url: str, ai_provider: AIProvider, github_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a GitHub repository. Caches intermediate API calls.
        """
        parsed = self.parse_repo_url(repo_url)
        if not parsed:
            raise ValueError("Invalid GitHub repository URL format.")
        
        owner, repo = parsed
        cache_key = f"github_repo:{owner}:{repo}"
        
        # Check cache
        cached_result = self._get_cache(cache_key)
        if cached_result:
            logger.info(f"Returning cached GitHub analysis for {owner}/{repo}")
            return json.loads(cached_result)

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Resume-Intelligence-Platform"
        }
        if github_token:
            headers["Authorization"] = f"token {github_token}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            # 1. Fetch Repository Metadata
            repo_api_url = f"https://api.github.com/repos/{owner}/{repo}"
            meta_res = await client.get(repo_api_url, headers=headers)
            if meta_res.status_code != 200:
                raise RuntimeError(f"GitHub API returned status {meta_res.status_code}: {meta_res.text}")
            
            repo_meta = meta_res.json()
            
            # 2. Fetch target files to analyze project details
            files_to_check = [
                "README.md",
                "package.json",
                "requirements.txt",
                "pom.xml",
                "Dockerfile",
                ".github/workflows/ci.yml",
                "docker-compose.yml"
            ]
            
            files_content = {}
            for path in files_to_check:
                content = await self.fetch_file_content(client, owner, repo, path, headers)
                if content:
                    # Truncate content if too long to save context space
                    files_content[path] = content[:4000]

            # 3. Request analysis from AI Provider
            meta_summary = {
                "name": repo_meta.get("name"),
                "description": repo_meta.get("description"),
                "language": repo_meta.get("language"),
                "topics": repo_meta.get("topics", [])
            }
            
            analysis_dict = await ai_provider.analyze_github_project(meta_summary, files_content)
            
            # Ensure output is fully structured
            required_keys = ["summary", "bullets", "business_impact", "complexity_score", "technologies"]
            for key in required_keys:
                if key not in analysis_dict:
                    if key == "bullets":
                        analysis_dict[key] = []
                    elif key == "complexity_score":
                        analysis_dict[key] = 5
                    elif key == "technologies":
                        analysis_dict[key] = []
                    else:
                        analysis_dict[key] = ""

            # Cache the completed analysis
            self._set_cache(cache_key, json.dumps(analysis_dict), ttl=3600)
            return analysis_dict

github_analyzer = GitHubAnalyzer()
