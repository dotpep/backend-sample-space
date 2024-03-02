from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import Base, DBItem, app, get_db

client = TestClient(app)

# Setup the in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


# Dependency to override the get_db depedency in the main app
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


# API Endpoints Testing
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Server is running"


def test_create_item():
    response = client.post(
        "/items",
        json={
            "name": "Test Item",
            "description": "This is a test item",
        }
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "This is a test item"
    assert "id" in data


def test_read_item():
    item_id = 100
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "This is a test item"
    assert data["id"] == item_id


def test_update_item():
    item_id = 100
    response = client.put(
        f"/items/{item_id}",
        json={
            "name": "Updated Test Item",
            "description": "This is an updated test item",
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Updated Test Item"
    assert data["description"] == "This is an updated test item"
    assert data["id"] == item_id


def test_delete_item():
    item_id = 100
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Updated Test Item"
    assert data["description"] == "This is an updated test item"
    assert data["id"] == item_id
    # Try to get the deleted item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 404, response.text


def setup():
    # Create the tables in the teest database
    Base.metadata.create_all(bind=engine)
    
    # create test items
    session = TestingSessionLocal()
    db_item = DBItem(id=100, name="Test Item", description="This is a test item")
    session.add(db_item)
    session.commit()
    session.close()


def teardown():
    # Drop the tables in the test database
    Base.metadata.drop_all(bind=engine)
