import re
from jinja2 import Environment, BaseLoader
from typing import Any, Dict, List
from app.schemas.resume import ResumeContent

class LaTeXRenderer:
    # Top-level placeholders required in our Jinja2 templates
    REQUIRED_PLACEHOLDERS = [
        "full_name",
        "email",
        "summary",
        "skills",
        "experience",
        "projects",
        "education"
    ]

    @staticmethod
    def escape_latex(text: str) -> str:
        """
        Escapes LaTeX special characters to prevent compilation failures and injection.
        """
        if not isinstance(text, str):
            return text
        
        # Mapping of special LaTeX characters to their escaped versions
        latex_escapes = {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }
        
        # Regex to match any of the keys in latex_escapes
        # Backslash is processed first to avoid double-escaping
        regex = re.compile(
            "|".join(re.escape(str(key)) for key in sorted(latex_escapes.keys(), key=lambda item: -len(item)))
        )
        return regex.sub(lambda match: latex_escapes[match.group()], text)

    @classmethod
    def sanitize_context(cls, data: Any) -> Any:
        """
        Recursively walks dictionary or list data to escape all string elements for LaTeX.
        """
        if isinstance(data, dict):
            return {k: cls.sanitize_context(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.sanitize_context(x) for x in data]
        elif isinstance(data, str):
            return cls.escape_latex(data)
        else:
            return data

    @classmethod
    def validate_placeholders(cls, context: Dict[str, Any]) -> None:
        """
        Ensures all key sections are populated before compilation.
        """
        missing = []
        for field in cls.REQUIRED_PLACEHOLDERS:
            if field not in context or not context[field]:
                missing.append(field)
        
        if missing:
            raise ValueError(f"Missing mandatory resume fields: {', '.join(missing)}")

    @classmethod
    def render_template(cls, template_source: str, resume_content: ResumeContent) -> str:
        """
        Renders the LaTeX source from raw template string and ResumeContent.
        """
        # Convert schema to raw dict and sanitize string fields
        raw_data = resume_content.model_dump()
        sanitized_context = cls.sanitize_context(raw_data)
        
        # Validate that required placeholders are present
        cls.validate_placeholders(sanitized_context)
        
        # Initialize Jinja2 environment
        # We can use standard Jinja2 block syntax, but we override delimiters if necessary.
        # We use standard Jinja2 block syntax as requested
        env = Environment(
            loader=BaseLoader(),
            autoescape=False, # LaTeX handles its own escaping
        )
        
        template = env.from_string(template_source)
        rendered_tex = template.render(**sanitized_context)
        return rendered_tex
