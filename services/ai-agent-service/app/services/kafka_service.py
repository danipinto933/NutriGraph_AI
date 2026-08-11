import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer
from app.core.config import settings

logger = logging.getLogger(__name__)

class KafkaConsumerService:
    def __init__(self):
        self.consumer = None
        self.task = None

    async def start(self):
        try:
            self.consumer = AIOKafkaConsumer(
                settings.KAFKA_RECIPE_EVENTS_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_CONSUMER_GROUP,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
            )
            await self.consumer.start()
            logger.info("Kafka consumer started in AI Agent Service.")
            self.task = asyncio.create_task(self._consume())
        except Exception as e:
            logger.warning(f"Failed to start Kafka consumer in AI Agent Service: {e}. Running in HTTP-only mode.")
            self.consumer = None

    async def stop(self):
        if self.task:
            self.task.cancel()
        if self.consumer:
            try:
                await self.consumer.stop()
                logger.info("Kafka consumer stopped in AI Agent Service.")
            except Exception as e:
                logger.warning(f"Error stopping Kafka consumer: {e}")
            finally:
                self.consumer = None

    async def _consume(self):
        if not self.consumer:
            return
        try:
            async for msg in self.consumer:
                await self._process_message(msg.value)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error consuming messages in AI Agent Service: {e}")

    async def _process_message(self, payload: dict):
        event_type = payload.get("event") or payload.get("event_type")
        logger.info(f"AI Agent Service received Kafka event: {event_type}")

kafka_service = KafkaConsumerService()
