"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings
from app.main import app

settings = get_settings()


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Create a test database."""
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client["infrawatch_test"]

    yield db

    # Cleanup - drop test database
    await client.drop_database("infrawatch_test")
    client.close()


@pytest.fixture
def client() -> Generator:
    """Create a test client."""
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user data for tests."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User",
    }


@pytest.fixture
def sample_metric_data() -> dict:
    """Sample metric data for tests."""
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
    """Sample log data for tests."""
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
    """Sample alert data for tests."""
    return {
        "title": "High CPU Usage",
        "description": "CPU usage exceeded 80%",
        "severity": "warning",
        "source": "test-pod-1",
        "namespace": "default",
        "cluster": "test-cluster",
    }
