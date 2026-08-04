from unittest.mock import patch, AsyncMock
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.deps import get_current_admin

async def mock_admin_user():
    return "admin@test.com"

@pytest.mark.asyncio
@patch("app.models.user_repository.user_repository.get_recipes")
@patch("app.models.user_repository.user_repository.create_recipe")
async def test_create_recipe_endpoint(mock_create, mock_get):
    app.dependency_overrides[get_current_admin] = mock_admin_user
    try:
        mock_get.return_value = []
        recipe_payload = {
            "name": "Ensalada Proteica",
            "description": "Ensalada fresca",
            "ingredients": [
                {"name": "Pechuga de Pollo", "grams": 150.0}
            ]
        }
        mock_response = {
            "id": "r_123",
            "name": "Ensalada Proteica",
            "description": "Ensalada fresca",
            "ingredients": [{"name": "Pechuga de Pollo", "grams": 150.0}],
            "calories": 247.5,
            "protein_g": 46.5,
            "fat_g": 5.4,
            "carbs_g": 0.0
        }
        mock_create.return_value = mock_response

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/admin/recipes/",
                json=recipe_payload
            )
        assert response.status_code == 201
        assert response.json()["name"] == "Ensalada Proteica"
        assert response.json()["id"] == "r_123"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
@patch("app.models.user_repository.user_repository.get_recipes")
async def test_get_recipes_endpoint(mock_get):
    app.dependency_overrides[get_current_admin] = mock_admin_user
    try:
        mock_get.return_value = [
            {
                "id": "r_1",
                "name": "Pollo con Arroz",
                "description": "Plato clásico",
                "ingredients": [{"name": "Arroz", "grams": 100}],
                "calories": 130,
                "protein_g": 2.7,
                "fat_g": 0.3,
                "carbs_g": 28
            }
        ]
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/v1/admin/recipes/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Pollo con Arroz"
    finally:
        app.dependency_overrides.clear()
