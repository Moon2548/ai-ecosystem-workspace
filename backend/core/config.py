from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Backend API"
    DEBUG_MODE: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://myuser:mypassword@localhost:5433/labelstudio"
    JWT_SECRET_KEY: str = "change-this-secret-before-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
