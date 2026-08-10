import logging
from typing import Any
from datetime import datetime
import pytz

from app.core.config import settings
from neo4j import AsyncDriver, AsyncGraphDatabase

logger = logging.getLogger(__name__)

class ChatRepository:
    def __init__(self):
        self.driver: AsyncDriver | None = None

    async def connect(self):
        logger.info(f"[NEO4J AUTH DEBUG] ai-agent-service usando NEO4J_USER='{settings.NEO4J_USER}', NEO4J_PASSWORD='{settings.NEO4J_PASSWORD}', NEO4J_URI='{settings.NEO4J_URI}'")
        print(f"[NEO4J AUTH DEBUG] ai-agent-service usando NEO4J_USER='{settings.NEO4J_USER}', NEO4J_PASSWORD='{settings.NEO4J_PASSWORD}', NEO4J_URI='{settings.NEO4J_URI}'", flush=True)
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        logger.info(f"Connected to Neo4j at {settings.NEO4J_URI}")

    async def close(self):
        if self.driver:
            await self.driver.close()
            logger.info("Closed Neo4j connection")

    async def save_message(self, user_id: str, session_id: str, role: str, content: str, title: str = None) -> bool:
        """Saves a message to a conversation. Creates the conversation if it doesn't exist."""
        timestamp = datetime.now(pytz.utc).isoformat()
        
        # If title is provided (first message), we set it. Otherwise, we don't update title.
        query = """
        MATCH (u:User {email: $user_id})
        MERGE (u)-[:HAS_CONVERSATION]->(c:Conversation {session_id: $session_id})
        ON CREATE SET c.created_at = $timestamp, c.updated_at = $timestamp, c.title = $title
        ON MATCH SET c.updated_at = $timestamp
        CREATE (c)-[:HAS_MESSAGE]->(m:Message {
            role: $role,
            content: $content,
            timestamp: $timestamp
        })
        RETURN id(m) as message_id
        """
        async with self.driver.session() as session:
            result = await session.run(
                query, 
                user_id=user_id, 
                session_id=session_id, 
                role=role, 
                content=content, 
                timestamp=timestamp,
                title=title or "Nueva conversación"
            )
            record = await result.single()
            return record is not None

    async def get_user_conversations(self, user_id: str) -> list[dict[str, Any]]:
        """Gets all conversations for a user, ordered by most recently updated."""
        query = """
        MATCH (u:User {email: $user_id})-[:HAS_CONVERSATION]->(c:Conversation)
        RETURN c.session_id AS session_id, 
               c.title AS title, 
               c.created_at AS created_at, 
               c.updated_at AS updated_at
        ORDER BY c.updated_at DESC
        """
        async with self.driver.session() as session:
            result = await session.run(query, user_id=user_id)
            records = await result.data()
            return records

    async def get_conversation_messages(self, session_id: str) -> list[dict[str, Any]]:
        """Gets all messages for a specific conversation session, ordered by timestamp."""
        query = """
        MATCH (c:Conversation {session_id: $session_id})-[:HAS_MESSAGE]->(m:Message)
        RETURN m.role AS role, m.content AS content, m.timestamp AS timestamp
        ORDER BY m.timestamp ASC
        """
        async with self.driver.session() as session:
            result = await session.run(query, session_id=session_id)
            records = await result.data()
            return records

    async def get_ai_analytics(self, latencies_list: list[float] = None) -> dict[str, Any]:
        """Obtiene analítica del agente conversacional: mensajes, latencias y términos más preguntados."""
        query_totals = """
        MATCH (m:Message)
        RETURN count(m) AS total_messages,
               count(CASE WHEN m.role = 'user' THEN 1 END) AS user_messages,
               count(CASE WHEN m.role = 'ai' THEN 1 END) AS ai_responses
        """
        
        query_convs = """
        MATCH (c:Conversation)
        RETURN count(c) AS total_conversations
        """
        
        query_top_keywords = """
        MATCH (m:Message {role: 'user'})
        WITH toLower(m.content) AS text
        UNWIND ['pollo', 'huevo', 'leche', 'arroz', 'atun', 'queso', 'aguacate', 'pan', 'carne', 'pescado', 'avena', 'manzana', 'plátano', 'tomate', 'espinaca', 'garbanzos', 'lentejas', 'proteína', 'calorías'] AS ing
        WITH ing, count(CASE WHEN text CONTAINS ing THEN 1 END) AS occurrences
        WHERE occurrences > 0
        RETURN ing AS keyword, occurrences AS count
        ORDER BY count DESC
        LIMIT 10
        """

        avg_lat = 0.0
        p95_lat = 0.0
        if latencies_list and len(latencies_list) > 0:
            avg_lat = round(sum(latencies_list) / len(latencies_list), 2)
            sorted_lat = sorted(latencies_list)
            idx = int(len(sorted_lat) * 0.95)
            p95_lat = round(sorted_lat[min(idx, len(sorted_lat) - 1)], 2)

        async with self.driver.session() as session:
            res_tot = await session.run(query_totals)
            tot_data = dict(await res_tot.single() or {})
            
            res_conv = await session.run(query_convs)
            conv_data = dict(await res_conv.single() or {})

            res_kw = await session.run(query_top_keywords)
            kw_data = [dict(record) for record in await res_kw.data()]

        return {
            "total_conversations": conv_data.get("total_conversations", 0),
            "total_messages": tot_data.get("total_messages", 0),
            "user_messages": tot_data.get("user_messages", 0),
            "ai_responses": tot_data.get("ai_responses", 0),
            "average_latency_ms": avg_lat,
            "p95_latency_ms": p95_lat,
            "top_asked_ingredients": kw_data
        }

chat_repository = ChatRepository()

