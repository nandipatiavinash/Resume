from typing import Optional
from backend.app.services.ai.base import AIProvider
from backend.app.services.ai.openai import OpenAIProvider
from backend.app.services.ai.claude import ClaudeProvider
from backend.app.services.ai.gemini import GeminiProvider
from backend.app.services.ai.deepseek import DeepSeekProvider
from backend.app.services.ai.openrouter import OpenRouterProvider
from backend.app.core.security import decrypt_api_key

class ProviderFactory:
    @staticmethod
    def get_provider(
        provider_name: str, encrypted_api_key: str, api_base: Optional[str] = None
    ) -> AIProvider:
        """
        Decrypts API key and returns concrete provider class.
        """
        provider_lower = provider_name.lower()
        if provider_lower not in ["openai", "claude", "anthropic", "gemini", "google", "deepseek", "openrouter"]:
            raise ValueError(f"Unsupported AI Provider: {provider_name}")

        api_key = decrypt_api_key(encrypted_api_key)
        
        if provider_lower == "openai":
            return OpenAIProvider(api_key=api_key, api_base=api_base)
        elif provider_lower == "claude" or provider_lower == "anthropic":
            return ClaudeProvider(api_key=api_key, api_base=api_base)
        elif provider_lower == "gemini" or provider_lower == "google":
            return GeminiProvider(api_key=api_key, api_base=api_base)
        elif provider_lower == "deepseek":
            return DeepSeekProvider(api_key=api_key, api_base=api_base)
        elif provider_lower == "openrouter":
            return OpenRouterProvider(api_key=api_key, api_base=api_base)
