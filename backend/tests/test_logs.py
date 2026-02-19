"""Tests for log endpoints."""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestCreateLog:
    async def test_create_log_success(
        self, async_client: AsyncClient, sample_log_data: dict
    ):
        response = await async_client.post("/api/v1/logs", json=sample_log_data)
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == sample_log_data["message"]
        assert data["level"] == sample_log_data["level"]
        assert data["source"] == sample_log_data["source"]
        assert "_id" in data
        assert "timestamp" in data

    async def test_create_log_all_levels(self, async_client: AsyncClient):
        levels = ["debug", "info", "warning", "error", "critical"]
        for level in levels:
            response = await async_client.post(
                "/api/v1/logs",
                json={"message": f"Test {level} log", "level": level, "source": "test"},
            )
            assert response.status_code == 201, f"Failed for level {level}: {response.text}"

    async def test_create_log_invalid_level(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/logs",
            json={"message": "test", "level": "INVALID", "source": "test"},
        )
        assert response.status_code == 422

    async def test_create_log_missing_required(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/logs",
            json={"level": "info"},  # missing message and source
        )
        assert response.status_code == 422

    async def test_create_log_with_custom_timestamp(
        self, async_client: AsyncClient, sample_log_data: dict
    ):
        payload = {**sample_log_data, "timestamp": "2024-01-15T10:30:00Z"}
        response = await async_client.post("/api/v1/logs", json=payload)
        assert response.status_code == 201


class TestListLogs:
    async def test_list_logs_returns_paginated(
        self, async_client: AsyncClient, sample_log_data: dict
    ):
        await async_client.post("/api/v1/logs", json=sample_log_data)

        response = await async_client.get("/api/v1/logs")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    async def test_list_logs_filter_by_level(
        self, async_client: AsyncClient, sample_log_data: dict
    ):
        await async_client.post("/api/v1/logs", json=sample_log_data)

        response = await async_client.get("/api/v1/logs?level=info")
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["level"] == "info"

    async def test_list_logs_filter_by_source(
        self, async_client: AsyncClient, sample_log_data: dict
    ):
        await async_client.post("/api/v1/logs", json=sample_log_data)

        response = await async_client.get(
            f"/api/v1/logs?source={sample_log_data['source']}"
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["source"] == sample_log_data["source"]

    async def test_list_logs_search(self, async_client: AsyncClient):
        unique_msg = "unique_search_xyz_12345"
        await async_client.post(
            "/api/v1/logs",
            json={"message": unique_msg, "level": "info", "source": "search-test"},
        )

        response = await async_client.get(f"/api/v1/logs?search={unique_msg}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    async def test_list_logs_pagination(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/logs?page=1&page_size=3")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 3
        assert len(data["items"]) <= 3


class TestGetLog:
    async def test_get_log_by_id(
        self, async_client: AsyncClient, sample_log_data: dict
    ):
        create_response = await async_client.post("/api/v1/logs", json=sample_log_data)
        log_id = create_response.json()["_id"]

        response = await async_client.get(f"/api/v1/logs/{log_id}")
        assert response.status_code == 200
        assert response.json()["_id"] == log_id

    async def test_get_log_not_found(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/logs/000000000000000000000000")
        assert response.status_code == 404


class TestDeleteLog:
    async def test_delete_log_success(
        self, async_client: AsyncClient, sample_log_data: dict
    ):
        create_response = await async_client.post("/api/v1/logs", json=sample_log_data)
        log_id = create_response.json()["_id"]

        response = await async_client.delete(f"/api/v1/logs/{log_id}")
        assert response.status_code == 200

        get_response = await async_client.get(f"/api/v1/logs/{log_id}")
        assert get_response.status_code == 404

    async def test_delete_log_not_found(self, async_client: AsyncClient):
        response = await async_client.delete("/api/v1/logs/000000000000000000000000")
        assert response.status_code == 404


class TestLogStats:
    async def test_get_log_stats(
        self, async_client: AsyncClient, sample_log_data: dict
    ):
        await async_client.post("/api/v1/logs", json=sample_log_data)

        response = await async_client.get("/api/v1/logs/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_count" in data
        assert "by_level" in data
        assert "by_source" in data


class TestBatchCreateLogs:
    async def test_create_logs_batch(
        self, async_client: AsyncClient, sample_log_data: dict
    ):
        batch = {
            "logs": [
                sample_log_data,
                {**sample_log_data, "level": "error", "message": "Error log"},
            ]
        }
        response = await async_client.post("/api/v1/logs/batch", json=batch)
        assert response.status_code == 201
        assert "2" in response.json()["message"]
