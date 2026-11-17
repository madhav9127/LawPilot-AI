import os
from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    app_name: str = "LawPilot AI"
    tagline: str = "Navigate Legal Challenges. Know Your Rights. Take Action."
    app_version: str = "1.0.0"
    
    # LLM Settings
    llm_provider: str = os.getenv("LLM_PROVIDER", "demo").lower()
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Server settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    
    # Upload limits
    max_upload_size_mb: int = 5
    allowed_extensions: list = [".pdf", ".txt", ".md", ".docx", ".png", ".jpg", ".jpeg"]
    
    @property
    def active_provider(self) -> str:
        """Determines the active provider based on availability of keys."""
        if self.gemini_api_key and self.gemini_api_key.strip():
            return "gemini"
        elif self.openai_api_key and self.openai_api_key.strip():
            return "openai"
        elif self.anthropic_api_key and self.anthropic_api_key.strip():
            return "anthropic"
        return "demo"
    
    @property
    def is_demo_mode(self) -> bool:
        return self.active_provider == "demo"

settings = Settings()
