from unittest.mock import patch

import pytest
from app.main import app
from app.schemas.user import UserResponse
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200

@pytest.mark.asyncio
@patch("app.api.endpoints.auth.register_user")
async def test_register(mock_register):
    # Mocking the service layer
    mock_register.return_value = UserResponse(email="test@test.com", first_name="Test")
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/users/register",
            json={"email": "test@test.com", "password": "securepassword123", "first_name": "Test"}
        )
    assert response.status_code == 201
    assert response.json()["email"] == "test@test.com"
