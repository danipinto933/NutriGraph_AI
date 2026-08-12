from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Agent Service"
    API_V1_STR: str = "/api/v1"
    
    # URL del servicio de grafos
    NUTRITION_GRAPH_SERVICE_URL: str
    
    # LLM Settings
    OPENAI_API_KEY: str
    OPENAI_API_BASE: str
    LLM_MODEL: str
    
    # Redis Settings
    REDIS_URL: str
    
    # Neo4j Settings
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    # Kafka Settings (opcional / resiliencia)
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_RECIPE_EVENTS_TOPIC: str
    KAFKA_CONSUMER_GROUP: str

    model_config = SettingsConfigDict(env_file=[".env", "../../.env"], env_file_encoding="utf-8", extra="ignore")

settings = Settings()
