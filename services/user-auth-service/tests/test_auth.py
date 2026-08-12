from unittest.mock import patch

import pytest
from app.main import app
from app.schemas.auth import Token
from app.schemas.user import UserRegisterResponse
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
    mock_register.return_value = UserRegisterResponse(
        message="Usuario registrado correctamente",
        email="test@test.com",
        is_verified=False
    )
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/users/register",
            json={"email": "test@test.com", "password": "securepassword123", "first_name": "Test"}
        )
    assert response.status_code == 201
    assert response.json()["email"] == "test@test.com"

@pytest.mark.asyncio
@patch("app.api.endpoints.auth.verify_user_email")
async def test_verify_email(mock_verify):
    mock_verify.return_value = Token(access_token="fake_token", token_type="bearer")
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/users/verify-email?token=valid_token")
    assert response.status_code == 200
    assert response.json()["access_token"] == "fake_token"

@pytest.mark.asyncio
@patch("app.api.endpoints.auth.resend_verification_email")
async def test_resend_verification(mock_resend):
    mock_resend.return_value = {"message": "Correo de verificación reenviado con éxito."}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/users/resend-verification",
            json={"email": "test@test.com"}
        )
    assert response.status_code == 200
    assert response.json()["message"] == "Correo de verificación reenviado con éxito."

@pytest.mark.asyncio
@patch("app.services.email_service.email_service._send_email_smtp_sync")
async def test_email_service_notifications(mock_send):
    mock_send.return_value = True
    from app.services.email_service import email_service
    
    # Test user verification email
    res1 = await email_service.send_verification_email("newuser@test.com", "TestUser", "dummy_token")
    assert res1 is True
    
    # Test admin notification email
    res2 = await email_service.send_admin_notification("newuser@test.com", "TestUser")
    assert res2 is True


