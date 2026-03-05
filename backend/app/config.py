from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings
import os
from app.services.secrets_provider import get_secret_provider

class Settings(BaseSettings):
    ENV_NAME: str = Field(default="dev", description="Environment: dev, staging, prod")
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str | None = None

    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
        description="Comma-separated list of allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow credentials in CORS requests")
    CORS_ALLOW_METHODS: list = Field(default=["*"], description="Allowed HTTP methods")
    CORS_ALLOW_HEADERS: list = Field(
        default=["*"], 
        description="Allowed headers - use * for development, restrict in production"
    )
    
    # Secret provider configuration
    SECRETS_PROVIDER_TYPE: str = Field(default="env", description="Type of secret provider: env, aws, vault, azure")
    
    # Razorpay credentials (SecureStr to prevent logging)
    RAZORPAY_KEY_ID: SecretStr = Field(default=SecretStr(""), description="Razorpay API Key ID")
    RAZORPAY_KEY_SECRET: SecretStr = Field(default=SecretStr(""), description="Razorpay API Key Secret")

    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@womanly.com"

    class Config:
        env_file = ".env"

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@db:5432/{self.POSTGRES_DB}"
    
    def get_cors_origins(self) -> list:
        """Parse CORS origins from environment variable."""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
    def get_secret_provider(self):
        """Get configured secret provider instance."""
        try:
            return get_secret_provider(self.SECRETS_PROVIDER_TYPE)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize secret provider: {str(e)}")
    
    def get_sensitivity_label(self, field_name: str) -> str:
        """Determine if a field is sensitive (secrets should never be logged)."""
        sensitive_fields = {
            "SECRET_KEY", "RAZORPAY_KEY_SECRET", "RAZORPAY_KEY_ID", "SMTP_PASSWORD", 
            "POSTGRES_PASSWORD", "access_token", "refresh_token"
        }
        return "***REDACTED***" if field_name in sensitive_fields else "visible"

settings = Settings()
