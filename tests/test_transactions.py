import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db

# ─── Test Database ────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///./test_temp.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override করো
app.dependency_overrides[get_db] = override_get_db

# Tables বানাও
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# ─── Helper Functions ─────────────────────────────────────────

def register_and_login(username="testuser1", password="pass123"):
    """Register + Login → token header return করো"""
    
    # Register (already exist হলেও চলবে)
    client.post("/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": password
    })

    # Login
    response = client.post("/auth/login", json={
        "username": username,
        "password": password
    })

    assert response.status_code == 200, f"Login failed: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_sample_transaction(headers):
    """একটা transaction বানাও"""
    response = client.post("/transactions", json={
        "title": "Grocery Shopping",
        "amount": 500.0,
        "type": "expense",
        "category": "Food",
        "date": "2024-01-15"
    }, headers=headers)
    return response

# ─── Test Cases ───────────────────────────────────────────────

def test_get_all_transactions():
    """সব transactions পাওয়ার test"""
    headers = register_and_login("user_getall", "pass123")
    create_sample_transaction(headers)

    response = client.get("/transactions", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    print("✅ Get all transactions - PASSED")


def test_get_specific_transaction():
    """নির্দিষ্ট transaction পাওয়ার test"""
    headers = register_and_login("user_getone", "pass123")
    created = create_sample_transaction(headers)

    assert created.status_code == 201
    transaction_id = created.json()["id"]

    response = client.get(f"/transactions/{transaction_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == transaction_id
    print("✅ Get specific transaction - PASSED")


def test_create_transaction():
    """Transaction create করার test"""
    headers = register_and_login("user_create", "pass123")

    response = client.post("/transactions", json={
        "title": "Monthly Salary",
        "amount": 50000.0,
        "type": "income",
        "category": "Job",
        "date": "2024-01-01"
    }, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Monthly Salary"
    assert data["amount"] == 50000.0
    assert data["type"] == "income"
    print("✅ Create transaction - PASSED")


def test_update_transaction():
    """Transaction update করার test"""
    headers = register_and_login("user_update", "pass123")
    created = create_sample_transaction(headers)

    assert created.status_code == 201
    transaction_id = created.json()["id"]

    response = client.put(
        f"/transactions/{transaction_id}",
        json={
            "title": "Updated Title",
            "amount": 999.0
        },
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["amount"] == 999.0
    print("✅ Update transaction - PASSED")


def test_delete_transaction():
    """Transaction delete করার test"""
    headers = register_and_login("user_delete", "pass123")
    created = create_sample_transaction(headers)

    assert created.status_code == 201
    transaction_id = created.json()["id"]

    # Delete করো
    response = client.delete(
        f"/transactions/{transaction_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

    # আবার get করলে 404 আসবে
    get_response = client.get(
        f"/transactions/{transaction_id}",
        headers=headers
    )
    assert get_response.status_code == 404
    print("✅ Delete transaction - PASSED")