import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from app.core.config import settings
from app.core.neo4j_client import neo4j_client
from app.models.schemas import UserIntolerancesUpdatedEvent, UserRegisteredEvent
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class KafkaConsumerService:
    def __init__(self):
        self.consumer = None
        self.producer = None
        self.task = None

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_USER_EVENTS_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda m: json.dumps(m).encode("utf-8")
        )
        await self.consumer.start()
        await self.producer.start()
        logger.info("Kafka consumer and producer (for DLQ) started.")
        self.task = asyncio.create_task(self._consume())

    async def stop(self):
        if self.task:
            self.task.cancel()
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        logger.info("Kafka consumer and producer stopped.")

    async def _consume(self):
        try:
            async for msg in self.consumer:
                await self._process_message(msg.value)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")

    async def _process_message(self, payload: dict):
        event_type = payload.get("event_type")
        data = payload.get("data", {})
        
        driver = neo4j_client.get_driver()

        try:
            if event_type == "UserRegistered":
                event = UserRegisteredEvent(**data)
                await self._handle_user_registered(driver, event)
            elif event_type == "UserIntolerancesUpdated":
                event = UserIntolerancesUpdatedEvent(**data)
                await self._handle_user_intolerances(driver, event)
            else:
                logger.warning(f"Unknown event_type: {event_type}")
        except ValidationError as e:
            logger.error(f"Validation error for event {event_type}: {e}. Sending to DLQ.")
            await self._send_to_dlq(payload, str(e))
        except Exception as e:
            logger.error(f"Error processing event {event_type}: {e}. Sending to DLQ.")
            await self._send_to_dlq(payload, str(e))

    async def _send_to_dlq(self, payload: dict, error: str):
        try:
            dlq_message = {
                "original_payload": payload,
                "error": error
            }
            await self.producer.send_and_wait(settings.KAFKA_USER_EVENTS_DLQ_TOPIC, dlq_message)
            logger.info(f"Message sent to DLQ topic {settings.KAFKA_USER_EVENTS_DLQ_TOPIC}")
        except Exception as e:
            logger.error(f"Failed to send message to DLQ: {e}")

    async def _handle_user_registered(self, driver, event: UserRegisteredEvent):
        query = """
        MERGE (u:User {email: $email})
        SET u.diet_type = $diet_type
        """
        async with driver.session() as session:
            await session.run(query, email=event.email, diet_type=event.diet_type)
            logger.info(f"User {event.email} registered in Neo4j.")

    async def _handle_user_intolerances(self, driver, event: UserIntolerancesUpdatedEvent):
        query = """
        MATCH (u:User {email: $user_id})
        // Remove existing intolerance relations
        OPTIONAL MATCH (u)-[r:HAS_INTOLERANCE]->()
        DELETE r
        WITH u
        UNWIND $intolerances AS allergen_name
        MERGE (a:Allergen {name: allergen_name})
        MERGE (u)-[:HAS_INTOLERANCE]->(a)
        """
        async with driver.session() as session:
            await session.run(query, user_id=event.user_id, intolerances=event.intolerances)
            logger.info(f"Updated intolerances for user {event.user_id} in Neo4j.")

kafka_consumer_service = KafkaConsumerService()
