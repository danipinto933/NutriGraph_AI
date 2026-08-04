import pytest
from app.core.config import settings
from neo4j import AsyncGraphDatabase


@pytest.fixture(autouse=True)
async def setup_db(neo4j_container):
    # Insert seed data for tests
    driver = AsyncGraphDatabase.driver(neo4j_container.get_connection_url(), auth=("neo4j", "testpassword"))
    query = """
    MATCH (n) DETACH DELETE n;
    
    CREATE (lactosa:Allergen {name: 'Lactosa'})
    CREATE (gluten:Allergen {name: 'Gluten'})
    
    CREATE (pollo:Ingredient {name: 'Pechuga de Pollo', calorias_100g: 165, proteinas_100g: 31, grasas_100g: 3.6, carbohidratos_100g: 0})
    CREATE (arroz:Ingredient {name: 'Arroz Blanco', calorias_100g: 130, proteinas_100g: 2.7, grasas_100g: 0.3, carbohidratos_100g: 28})
    CREATE (leche:Ingredient {name: 'Leche Entera', calorias_100g: 42, proteinas_100g: 3.4, grasas_100g: 1, carbohidratos_100g: 5})-[:CONTAINS_ALLERGEN]->(lactosa)
    
    CREATE (vegan:DietType {name: 'Vegana'})-[:EXCLUDES]->(pollo)
    CREATE (vegan)-[:EXCLUDES]->(leche)
    
    CREATE (r1:Recipe {id: 'r1', name: 'Pollo con Arroz', description: 'desc'})
    CREATE (r1)-[:CONTAINS_INGREDIENT {grams: 200}]->(pollo)
    CREATE (r1)-[:CONTAINS_INGREDIENT {grams: 100}]->(arroz)
    
    CREATE (r2:Recipe {id: 'r2', name: 'Batido con Leche', description: 'desc'})
    CREATE (r2)-[:CONTAINS_INGREDIENT {grams: 300}]->(leche)
    
    CREATE (r3:Recipe {id: 'r3', name: 'Arroz Solo', description: 'desc'})
    CREATE (r3)-[:CONTAINS_INGREDIENT {grams: 200}]->(arroz)
    
    CREATE (u1:User {id: 1, email: 'user1@test.com'}) // Normal
    CREATE (u2:User {id: 2, email: 'user2@test.com'})-[:HAS_INTOLERANCE]->(lactosa)
    CREATE (u3:User {id: 3, email: 'user3@test.com', diet_type: 'Vegana'})
    """
    async with driver.session() as session:
        await session.run(query)
    await driver.close()

@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_macros_sum_correctly(async_client):
    # u1 can see all recipes
    response = await async_client.get("/api/v1/recipes/recommendations?user_id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    pollo_arroz = next(r for r in data if r["recipe_id"] == "r1")
    # 200g pollo (165*2 = 330) + 100g arroz (130*1 = 130) = 460
    assert pollo_arroz["macros"]["calories"] == 460.0
    # 200g pollo (31*2=62) + 100g arroz (2.7) = 64.7
    assert pollo_arroz["macros"]["protein_g"] == 64.7

@pytest.mark.asyncio
async def test_allergen_exclusion(async_client):
    # u2 is lactose intolerant, cannot see r2 (Batido con leche)
    response = await async_client.get("/api/v1/recipes/recommendations?user_id=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    recipe_ids = [r["recipe_id"] for r in data]
    assert "r2" not in recipe_ids

@pytest.mark.asyncio
async def test_diet_type_exclusion(async_client):
    # u3 is vegan, excludes pollo and leche
    response = await async_client.get("/api/v1/recipes/recommendations?user_id=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["recipe_id"] == "r3"
