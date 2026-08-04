import pytest


@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_chat_stream_empty_message(async_client):
    response = await async_client.post(
        "/api/v1/chat/stream",
        json={"user_id": "1", "session_id": "test_session", "message": "   "}
    )
    assert response.status_code == 422
    assert response.json()["message"] == "Message cannot be empty"
