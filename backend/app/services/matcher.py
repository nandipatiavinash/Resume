import re
import math
from typing import List, Dict, Tuple, Any
from app.schemas.resume import JDAnalysis

# List of simple English stop words to filter out
STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'arent', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'cant', 'cannot', 'could',
    'did', 'didnt', 'do', 'does', 'doesnt', 'doing', 'dont', 'down', 'during', 'each', 'few', 'for', 'from', 'further',
    'had', 'hadnt', 'has', 'hasnt', 'have', 'havent', 'having', 'he', 'hed', 'hell', 'hes', 'her', 'here', 'heres',
    'hers', 'herself', 'him', 'himself', 'his', 'how', 'hows', 'i', 'id', 'ill', 'im', 'ive', 'if', 'in', 'into', 'is',
    'isnt', 'it', 'its', 'itself', 'lets', 'me', 'more', 'most', 'mustnt', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off',
    'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shant', 'she',
    'shed', 'shell', 'shes', 'should', 'shouldnt', 'so', 'some', 'such', 'than', 'that', 'thats', 'the', 'their', 'theirs',
    'them', 'themselves', 'then', 'there', 'theres', 'these', 'they', 'theyd', 'theyll', 'theyre', 'theyve', 'this',
    'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasnt', 'we', 'wed', 'well', 'were', 'weve',
    'werent', 'what', 'whats', 'when', 'whens', 'where', 'wheres', 'which', 'while', 'who', 'whos', 'whom', 'why', 'whys',
    'with', 'wont', 'would', 'wouldnt', 'you', 'youd', 'youll', 'youre', 'youve', 'your', 'yours', 'yourself', 'yourselves'
}

class ProjectMatcher:
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """
        Cleans text, splits into words, removes stop words.
        """
        if not text:
            return []
        # Remove punctuation, lowercase, split
        words = re.findall(r'[a-zA-Z0-9\-\_]+', text.lower())
        return [w for w in words if w not in STOP_WORDS]

    @staticmethod
    def _term_frequency(tokens: List[str]) -> Dict[str, int]:
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        return tf

    @classmethod
    def _cosine_similarity(cls, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        Calculates cosine similarity between two word frequency vectors.
        """
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum(vec1[x] * vec2[x] for x in intersection)

        sum1 = sum(val ** 2 for val in vec1.values())
        sum2 = sum(val ** 2 for val in vec2.values())
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return float(numerator) / denominator

    @classmethod
    def score_project(cls, project: dict, jd_tokens: List[str], jd_analysis: JDAnalysis) -> float:
        """
        Scores a project 0-100 against JD using TF-IDF word vectors & semantic overlap of skills/keywords.
        """
        # Combine project metadata
        proj_text = f"{project.get('name', '')} {project.get('description', '')}"
        
        # Include analysis bullets/technologies if project was already analyzed
        if project.get("analysis"):
            analysis = project["analysis"]
            proj_text += " " + " ".join(analysis.get("bullets", []))
            proj_text += " " + analysis.get("summary", "")
            proj_text += " " + " ".join(analysis.get("technologies", []))

        proj_tokens = cls._tokenize(proj_text)
        
        # 1. Cosine similarity score (TF-IDF vector representation)
        proj_tf = cls._term_frequency(proj_tokens)
        jd_tf = cls._term_frequency(jd_tokens)
        cosine_score = cls._cosine_similarity(proj_tf, jd_tf)

        # 2. Key matching score (Skills + Keywords match)
        skills_keywords = set(
            [s.lower() for s in jd_analysis.required_skills] +
            [s.lower() for s in jd_analysis.preferred_skills] +
            [k.lower() for k in jd_analysis.ats_keywords]
        )
        
        if not skills_keywords:
            skills_score = 0.0
        else:
            proj_tokens_set = set(proj_tokens)
            matched_keys = skills_keywords & proj_tokens_set
            skills_score = len(matched_keys) / len(skills_keywords)

        # Weighted combination: 40% TF-IDF Cosine, 60% Specific Skills/Keywords Overlap
        final_score = (cosine_score * 0.4 + skills_score * 0.6) * 100
        return min(max(final_score, 0.0), 100.0)

    @classmethod
    def rank_projects(cls, projects: List[dict], jd_text: str, jd_analysis: JDAnalysis, top_n: int = 3) -> List[Tuple[dict, float]]:
        """
        Ranks projects by score and returns the top N projects with scores.
        """
        jd_tokens = cls._tokenize(jd_text)
        scored_projects = []

        for project in projects:
            score = cls.score_project(project, jd_tokens, jd_analysis)
            scored_projects.append((project, score))

        # Sort descending by score
        scored_projects.sort(key=lambda item: item[1], reverse=True)
        return scored_projects[:top_n]
