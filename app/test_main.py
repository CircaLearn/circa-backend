# Run testing file with `pytest`
# See stdout on passed tests with `pytest -s`
# More info: https://fastapi.tiangolo.com/advanced/async-tests/#in-detail
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app, API_PREFIX

transport = ASGITransport(app=app)


def async_client():
    return AsyncClient(transport=transport, base_url="http://test")


# Helper function to delete a user if it already exists
async def ensure_user_does_not_exist(ac, email):
    response = await ac.get(f"{API_PREFIX}/users/email/{email}")
    if response.status_code == 200:
        user = response.json()
        user_id = user["id"]
        await ac.delete(f"{API_PREFIX}/users/{user_id}")


# Helper function to ensure user is created
async def ensure_user_exists(ac, email, username, password):
    await ensure_user_does_not_exist(ac, email)
    response = await ac.post(
        f"{API_PREFIX}/users",
        json={
            "email": email,
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio(scope="session")
async def test_create_user():
    async with async_client() as ac:
        await ensure_user_does_not_exist(ac, "testuser@example.com")

        response = await ac.post(
            f"{API_PREFIX}/users",
            json={
                "email": "testuser@example.com",
                "username": "testuser",
                "password": "testpassword",
            },
        )
    assert response.status_code == 201
    assert response.json()["email"] == "testuser@example.com"
    assert "hashed_password" not in response.json()


@pytest.mark.asyncio(scope="session")
async def test_get_user_by_email():
    async with async_client() as ac:
        await ensure_user_exists(ac, "testuser@example.com", "testuser", "testpassword")

        response = await ac.get(f"{API_PREFIX}/users/email/testuser@example.com")
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"


@pytest.mark.asyncio(scope="session")
async def test_get_user_by_id():
    async with async_client() as ac:
        user_id = await ensure_user_exists(
            ac, "testuser@example.com", "testuser", "testpassword"
        )

        response = await ac.get(f"{API_PREFIX}/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "testuser@example.com"


@pytest.mark.asyncio(scope="session")
async def test_update_user():
    async with async_client() as ac:
        user_id = await ensure_user_exists(
            ac, "testuser@example.com", "testuser", "testpassword"
        )

        response = await ac.put(
            f"{API_PREFIX}/users/{user_id}",
            json={"username": "updateduser", "password": "newpassword"},
        )
    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"


@pytest.mark.asyncio(scope="session")
async def test_delete_user():
    async with async_client() as ac:
        user_id = await ensure_user_exists(
            ac, "testuser@example.com", "testuser", "testpassword"
        )

        response = await ac.delete(f"{API_PREFIX}/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["message"] == f"User with id='{user_id}' deleted"


@pytest.mark.asyncio(scope="session")
async def test_login():
    async with async_client() as ac:
        await ensure_user_exists(ac, "testuser@example.com", "testuser", "testpassword")

        response = await ac.post(
            f"{API_PREFIX}/token",
            data={"username": "testuser@example.com", "password": "testpassword"},
        )
    # Successful login
    assert response.status_code == 200
    assert "access_token" in response.json()

    async with async_client() as ac:
        response = await ac.post(
            f"{API_PREFIX}/token",
            data={"username": "testuser@example.com", "password": "WRONGPASSWORD"},
        )
    # Failed login
    assert response.status_code == 400
