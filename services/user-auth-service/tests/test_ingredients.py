from unittest.mock import patch, AsyncMock
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.deps import get_current_admin

async def mock_admin_user():
    return "admin@test.com"

@pytest.mark.asyncio
@patch("app.models.user_repository.user_repository.get_ingredients")
@patch("app.models.user_repository.user_repository.create_ingredient")
async def test_create_ingredient_endpoint(mock_create, mock_get):
    app.dependency_overrides[get_current_admin] = mock_admin_user
    try:
        mock_get.return_value = []
        ingredient_payload = {
            "name": "Manzana Verde",
            "calorias_100g": 52.0,
            "proteinas_100g": 0.3,
            "grasas_100g": 0.2,
            "carbohidratos_100g": 14.0,
            "origen": "vegetal",
            "categoria": "Frutas",
            "allergens": []
        }
        mock_create.return_value = ingredient_payload
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/admin/ingredients/",
                json=ingredient_payload
            )
        assert response.status_code == 201
        assert response.json()["name"] == "Manzana Verde"
    finally:
        app.dependency_overrides.clear()
