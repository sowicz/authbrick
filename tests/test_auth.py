import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_LOGIN = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


def test_login_success(client):
    response = client.post("/auth/login", json={
        "login": "testuser",
        "password": "testpassword"
    })

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data



def test_auth_me_requires_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401



def test_auth_me_success(client):
    login = client.post("/auth/login", json={
        "login": ADMIN_LOGIN,
        "password": ADMIN_PASSWORD
    })

    access_token = login.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert "login" in data
    assert "role" in data




def test_refresh_rotation(client):
    login = client.post("/auth/login", json={
        "login": ADMIN_LOGIN,
        "password": ADMIN_PASSWORD
    })

    refresh_token = login.json()["refresh_token"]

    refresh_response = client.post(
        "/auth/refresh",
        cookies={"refresh_token": refresh_token}
    )

    assert refresh_response.status_code == 200
    new_refresh = refresh_response.json()["refresh_token"]

    # Try using the old refresh token again - should fail
    second_try = client.post(
        "/auth/refresh",
        cookies={"refresh_token": refresh_token}
    )

    assert second_try.status_code == 401
