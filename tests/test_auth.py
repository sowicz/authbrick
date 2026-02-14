import os
from dotenv import load_dotenv

from auth.router import login
from tests.conftest import client

load_dotenv(".env.tests")  # Load test environment variables

ADMIN_LOGIN = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

import pytest


@pytest.mark.asyncio
async def test_login_success(client):
    response = await client.post("/auth/login", json={
        "login": ADMIN_LOGIN,
        "password": ADMIN_PASSWORD
    })

    # 1. Status check
    assert response.status_code == 200
    
    # 2. Check json response structure
    assert response.json() == {"status": "ok"}

    # 3. Check if tokens are set in cookies
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


@pytest.mark.asyncio
async def test_auth_me_requires_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_me_success(client):
    login = await client.post("/auth/login", json={
        "login": ADMIN_LOGIN,
        "password": ADMIN_PASSWORD
    })

    access_token = login.cookies.get("access_token")

    response = await client.post("/auth/login", json={
        "login": ADMIN_LOGIN,
        "password": ADMIN_PASSWORD
    })

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["login"] == ADMIN_LOGIN


@pytest.mark.asyncio
async def test_refresh_rotation(client):

    login_res = await client.post("/auth/login", json={
        "login": ADMIN_LOGIN,
        "password": ADMIN_PASSWORD
    })
    
    old_refresh = await login_res.cookies.get("refresh_token")


    refresh_response = await client.post("/auth/refresh")
    assert refresh_response.status_code == 200
    

    client.cookies.clear() 
    second_try = await client.post(
        "/auth/refresh", 
        cookies={"refresh_token": old_refresh}
    )

    assert second_try.status_code == 401