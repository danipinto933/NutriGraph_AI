import json
import logging

from aiokafka import AIOKafkaProducer
from app.core.config import settings

logger = logging.getLogger(__name__)

class KafkaEventProducer:
    def __init__(self):
        self.producer = None

    async def start(self):
        try:
            logger.info(f"Starting Kafka Producer at {settings.KAFKA_BOOTSTRAP_SERVERS}")
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id=settings.KAFKA_CLIENT_ID,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.producer.start()
            logger.info("Kafka Producer started successfully.")
        except Exception as e:
            logger.warning(f"Failed to start Kafka Producer: {e}. Running in HTTP-only mode.")
            self.producer = None

    async def stop(self):
        if self.producer:
            try:
                logger.info("Stopping Kafka Producer")
                await self.producer.stop()
            except Exception as e:
                logger.warning(f"Error stopping Kafka Producer: {e}")
            finally:
                self.producer = None

    async def send_event(self, topic: str, value: dict, key: str | None = None):
        if not self.producer:
            logger.warning(f"Kafka producer is not initialized. Skipping event emission to topic '{topic}'.")
            return
        try:
            key_bytes = key.encode('utf-8') if key else None
            await self.producer.send_and_wait(topic, value=value, key=key_bytes)
            logger.info(f"Event sent to topic {topic} with key {key}")
        except Exception as e:
            logger.error(f"Failed to send event to topic {topic}: {e}")

producer = KafkaEventProducer()
