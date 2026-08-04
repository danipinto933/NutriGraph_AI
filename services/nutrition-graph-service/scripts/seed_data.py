import asyncio
import os
import sys

# Permitir importación del módulo app si se ejecuta desde distintos directorios
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from neo4j import AsyncGraphDatabase
from app.core.seed import run_seed
from app.core.config import settings

async def seed_data():
    print(f"Conectando a {settings.NEO4J_URI}...")
    driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI, 
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )
    
    try:
        await run_seed(driver)
    finally:
        await driver.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
