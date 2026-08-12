import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Nutrition Graph Service"
    API_V1_STR: str = "/api/v1"
    SEED_DB_ON_STARTUP: bool = False
    
    # Neo4j Settings
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    # Kafka Settings
    KAFKA_BOOTSTRAP_SERVERS: str = ""
    KAFKA_USER_EVENTS_TOPIC: str = "user-events"
    KAFKA_USER_EVENTS_DLQ_TOPIC: str = "user-events-dlq"
    KAFKA_CONSUMER_GROUP: str = "nutrition-graph-service-group"

    model_config = SettingsConfigDict(env_file=[".env", "../../.env"], env_file_encoding="utf-8", extra="ignore")

settings = Settings()
