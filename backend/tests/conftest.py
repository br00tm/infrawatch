"""Pytest configuration and fixtures."""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio

# Set test env vars BEFORE importing app modules so settings are picked up correctly
os.environ.setdefault("MONGODB_URL", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DB_NAME", "infrawatch_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

from httpx import ASGITransport, AsyncClient  # noqa: E402
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.main import app  # noqa: E402

settings = get_settings()
_TEST_DB_NAME = "infrawatch_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Session-scoped event loop (required by pytest-asyncio)."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def mongo_client() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Single MongoDB client shared across the test session."""
    client = AsyncIOMotorClient(settings.mongodb_url)
    yield client
    await client.drop_database(_TEST_DB_NAME)
    client.close()


@pytest_asyncio.fixture(scope="session")
async def test_db(mongo_client: AsyncIOMotorClient) -> AsyncIOMotorDatabase:
    """Test database, session-scoped for performance."""
    return mongo_client[_TEST_DB_NAME]


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client that talks to the FastAPI app in-process."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def registered_user(async_client: AsyncClient) -> dict:
    """Register a unique test user per test and return credentials."""
    import uuid
    uid = uuid.uuid4().hex[:8]
    payload = {
        "email": f"test_{uid}@example.com",
        "username": f"testuser_{uid}",
        "password": "TestPass123!",
        "full_name": "Test User",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return {**payload, "response": response.json()}


@pytest_asyncio.fixture
async def auth_headers(async_client: AsyncClient, registered_user: dict) -> dict:
    """Return Authorization Bearer headers for an authenticated user."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_user_data() -> dict:
    return {
        "email": "fixture@example.com",
        "username": "fixture_user",
        "password": "TestPass123!",
        "full_name": "Fixture User",
    }


@pytest.fixture
def sample_metric_data() -> dict:
    return {
        "name": "cpu_usage",
        "metric_type": "cpu",
        "value": 75.5,
        "unit": "percent",
        "source": "test-pod-1",
        "namespace": "default",
        "cluster": "test-cluster",
        "labels": {"app": "test"},
    }


@pytest.fixture
def sample_log_data() -> dict:
    return {
        "message": "Test log message",
        "level": "info",
        "source": "test-container",
        "namespace": "default",
        "cluster": "test-cluster",
        "pod_name": "test-pod-1",
        "container_name": "test-container",
    }


@pytest.fixture
def sample_alert_data() -> dict:
    return {
        "title": "High CPU Usage",
        "description": "CPU usage exceeded 80%",
        "severity": "warning",
        "source": "test-pod-1",
        "namespace": "default",
        "cluster": "test-cluster",
    }
