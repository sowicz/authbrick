import pytest
from main import app
from auth.dependency import get_current_user

# --- MOCK ROLE ---
async def mock_admin():
    return {"id": "1", "role_id": 1}

async def mock_regular_user():
    return {"id": "2", "role_id": 2}

# --- DANE TESTOWE ---
VALID_PAYLOAD = {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "test@test.pl",
    "smtp_password": "password123",
    "from_email": "test@test.pl",
    "use_tls": True,
    "is_active": True
}

# --- TESTY ---
@pytest.mark.anyio
async def test_create_config_as_admin_success(client):
    """Check if admin can create SMTP config."""
    app.dependency_overrides[get_current_user] = mock_admin
    
    response = await client.post("/admin/smtp/config", json=VALID_PAYLOAD)
    
    assert response.status_code in (200, 201)
    app.dependency_overrides = {}


@pytest.mark.anyio
async def test_create_config_as_user_forbidden(client):
    """Check if regular user gets 403."""
    app.dependency_overrides[get_current_user] = mock_regular_user
    
    response = await client.post("/admin/smtp/config", json=VALID_PAYLOAD)
    
    assert response.status_code == 403
    app.dependency_overrides = {}


@pytest.mark.anyio
async def test_get_config_requires_auth(client):
    """Check if missing authorization returns 401."""

    response = await client.get("/admin/smtp/config")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_update_smtp_logic(client):
    """Testing full update flow: create config, then update it."""
    app.dependency_overrides[get_current_user] = mock_admin
    
    create_res = await client.get("/admin/smtp/config")
    config_id = create_res.json().get("id")

    update_payload = {
        "id": config_id,
        "smtp_host": "new.smtp.pl"
    }
    update_res = await client.put("/admin/smtp/config", json=update_payload)
    
    assert update_res.status_code == 200
    app.dependency_overrides = {}