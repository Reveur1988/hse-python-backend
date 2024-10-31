from base64 import b64encode
from http import HTTPStatus
import pytest
from async_asgi_testclient import TestClient

from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.core.users import UserRole, password_is_longer_than_8

def get_auth_header(username: str, password: str) -> dict:
    credentials = b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {credentials}"}

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
def admin_headers():
    return get_auth_header("admin", "superSecretAdminPassword123")

@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "name": "Test User",
        "birthdate": "2000-01-01T00:00:00",
        "password": "password123"
    }

@pytest.fixture
def test_user_headers():
    return get_auth_header("testuser", "password123")

@pytest.mark.asyncio
async def test_initialize(app, admin_headers):
    async with TestClient(app) as client:
        response = await client.post(
            "/user-get?id=1",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert response.json()["username"] == "admin"
        assert response.json()["role"] == UserRole.ADMIN

@pytest.mark.asyncio
async def test_password_validation():
    assert password_is_longer_than_8("longpassword123")
    assert not password_is_longer_than_8("short")
    assert not password_is_longer_than_8("")

@pytest.mark.asyncio
async def test_register_user_success(app, test_user_data):
    async with TestClient(app) as client:
        response = await client.post("/user-register", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert "uid" in data
        assert data["username"] == test_user_data["username"]
        assert data["role"] == UserRole.USER

@pytest.mark.asyncio
@pytest.mark.parametrize("password,expected_status", [
    ("short123", HTTPStatus.BAD_REQUEST),
    ("password_without_number", HTTPStatus.BAD_REQUEST),
])
async def test_register_user_invalid_password(app, test_user_data, password, expected_status):
    async with TestClient(app) as client:
        invalid_data = test_user_data.copy()
        invalid_data["password"] = password
        response = await client.post("/user-register", json=invalid_data)
        assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_register_existed_user(app, test_user_data):
    async with TestClient(app) as client:
        await client.post("/user-register", json=test_user_data)
        response = await client.post("/user-register", json=test_user_data)
        assert response.status_code == HTTPStatus.BAD_REQUEST

@pytest.mark.asyncio
async def test_get_user_success(app, test_user_data, test_user_headers):
    async with TestClient(app) as client:
        register_response = await client.post("/user-register", json=test_user_data)
        user_id = register_response.json()["uid"]

        response = await client.post(
            f"/user-get?id={user_id}",
            headers=test_user_headers
        )
        assert response.status_code == 200
        assert response.json()["username"] == test_user_data["username"]

        response = await client.post(
            f"/user-get?username={test_user_data['username']}",
            headers=test_user_headers
        )
        assert response.status_code == 200
        assert response.json()["username"] == test_user_data["username"]

@pytest.mark.asyncio
@pytest.mark.parametrize("username,expected_status", [
    ("unknown", HTTPStatus.NOT_FOUND),
    ("", HTTPStatus.NOT_FOUND),
])
async def test_get_user_not_found(app, admin_headers, username, expected_status):
    async with TestClient(app) as client:
        response = await client.post(
            f"/user-get?username={username}",
            headers=admin_headers
        )
        assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_get_user_validation(app, admin_headers):
    async with TestClient(app) as client:
        response = await client.post(
            "/user-get?id=1&username=testuser",
            headers=admin_headers
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST

        response = await client.post(
            "/user-get",
            headers=admin_headers
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST

@pytest.mark.asyncio
@pytest.mark.parametrize("auth_header,expected_status", [
    ("YWRtaW46d3JvbmdwYXNzd29yZA==", HTTPStatus.UNAUTHORIZED),
    ("aW52YWxpZF91c2VyOnN0cm9uZ3Bhc3N3b3JkMTIz", HTTPStatus.UNAUTHORIZED),
])
async def test_user_invalid_creds(app, auth_header, expected_status):
    async with TestClient(app) as client:
        response = await client.post(
            "/user-get?id=1",
            headers={"Authorization": f"Basic {auth_header}"}
        )
        assert response.status_code == expected_status

@pytest.mark.asyncio
async def test_promote_user_success(app, test_user_data, admin_headers):
    async with TestClient(app) as client:
        register_response = await client.post("/user-register", json=test_user_data)
        user_id = register_response.json()["uid"]

        response = await client.post(
            f"/user-promote?id={user_id}",
            headers=admin_headers
        )
        assert response.status_code == 200

        verify_response = await client.post(
            f"/user-get?id={user_id}",
            headers=admin_headers
        )
        assert verify_response.json()["role"] == UserRole.ADMIN

@pytest.mark.asyncio
async def test_promote_user_errors(app, test_user_data, test_user_headers, admin_headers):
    async with TestClient(app) as client:
        register_response = await client.post("/user-register", json=test_user_data)
        user_id = register_response.json()["uid"]

        response = await client.post(
            f"/user-promote?id={user_id}",
            headers=test_user_headers
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        response = await client.post(
            "/user-promote?id=999",
            headers=admin_headers
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
