from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "User & Auth Service"
    API_V1_STR: str = "/api/v1"
    
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    NEO4J_URI: str
    NEO4J_AUTH: str
    
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_CLIENT_ID: str = "user-auth-service"
    
    RESEND_API_KEY: str
    FRONTEND_URL: str
    EMAIL_FROM: str
    
    model_config = SettingsConfigDict(env_file="../../.env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
