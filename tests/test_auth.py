import os
import pytest
from dotenv import load_dotenv

load_dotenv(".env.tests")

ADMIN_LOGIN = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

@pytest.mark.anyio
async def test_login_success(client):
    response = await client.post("/auth/login", json={
        "login": ADMIN_LOGIN,
        "password": ADMIN_PASSWORD
    })

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

@pytest.mark.anyio
async def test_auth_me_requires_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_auth_me_success(client):
    login = await client.post("/auth/login", json={
        "login": ADMIN_LOGIN,
        "password": ADMIN_PASSWORD
    })

    access_token = login.cookies.get("access_token")

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert "login" in data
    assert "role" in data

    

@pytest.mark.anyio
async def test_refresh_rotation(client):
    login = await client.post("/auth/login", json={
        "login": ADMIN_LOGIN,
        "password": ADMIN_PASSWORD
    })

    refresh_token = login.cookies.get("refresh_token")

    refresh_response = await client.post(
        "/auth/refresh",
        cookies={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200

    client.cookies.clear()
    
    
    second_try = await client.post(
        "/auth/refresh",
        cookies={"refresh_token": refresh_token}
    )
    assert second_try.status_code == 401
