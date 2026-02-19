"""Tests for metrics endpoints."""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestCreateMetric:
    async def test_create_metric_success(
        self, async_client: AsyncClient, sample_metric_data: dict
    ):
        response = await async_client.post("/api/v1/metrics", json=sample_metric_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_metric_data["name"]
        assert data["value"] == sample_metric_data["value"]
        assert data["metric_type"] == sample_metric_data["metric_type"]
        assert data["source"] == sample_metric_data["source"]
        assert "_id" in data
        assert "timestamp" in data

    async def test_create_metric_missing_required_fields(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/metrics",
            json={"name": "cpu_usage"},  # missing value, source, metric_type
        )
        assert response.status_code == 422

    async def test_create_metric_invalid_type(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/metrics",
            json={
                "name": "test",
                "metric_type": "not_a_real_type",
                "value": 1.0,
                "source": "host",
            },
        )
        assert response.status_code == 422

    async def test_create_metric_all_types(self, async_client: AsyncClient):
        types = ["cpu", "memory", "disk", "network", "custom"]
        for mtype in types:
            response = await async_client.post(
                "/api/v1/metrics",
                json={
                    "name": f"{mtype}_test",
                    "metric_type": mtype,
                    "value": 42.0,
                    "source": "test-host",
                },
            )
            assert response.status_code == 201, f"Failed for type {mtype}: {response.text}"


class TestListMetrics:
    async def test_list_metrics_returns_paginated(
        self, async_client: AsyncClient, sample_metric_data: dict
    ):
        # Create a metric first
        await async_client.post("/api/v1/metrics", json=sample_metric_data)

        response = await async_client.get("/api/v1/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert isinstance(data["items"], list)

    async def test_list_metrics_filter_by_type(
        self, async_client: AsyncClient, sample_metric_data: dict
    ):
        await async_client.post("/api/v1/metrics", json=sample_metric_data)

        response = await async_client.get("/api/v1/metrics?metric_type=cpu")
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["metric_type"] == "cpu"

    async def test_list_metrics_filter_by_source(
        self, async_client: AsyncClient, sample_metric_data: dict
    ):
        await async_client.post("/api/v1/metrics", json=sample_metric_data)

        response = await async_client.get(
            f"/api/v1/metrics?source={sample_metric_data['source']}"
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["source"] == sample_metric_data["source"]

    async def test_list_metrics_pagination(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/metrics?page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["items"]) <= 5

    async def test_list_metrics_invalid_pagination(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/metrics?page=0")
        assert response.status_code == 422


class TestGetMetric:
    async def test_get_metric_by_id(
        self, async_client: AsyncClient, sample_metric_data: dict
    ):
        create_response = await async_client.post("/api/v1/metrics", json=sample_metric_data)
        metric_id = create_response.json()["_id"]

        response = await async_client.get(f"/api/v1/metrics/{metric_id}")
        assert response.status_code == 200
        assert response.json()["_id"] == metric_id

    async def test_get_metric_not_found(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/metrics/000000000000000000000000")
        assert response.status_code == 404


class TestDeleteMetric:
    async def test_delete_metric_success(
        self, async_client: AsyncClient, sample_metric_data: dict
    ):
        create_response = await async_client.post("/api/v1/metrics", json=sample_metric_data)
        metric_id = create_response.json()["_id"]

        response = await async_client.delete(f"/api/v1/metrics/{metric_id}")
        assert response.status_code == 200

        # Verify it's gone
        get_response = await async_client.get(f"/api/v1/metrics/{metric_id}")
        assert get_response.status_code == 404

    async def test_delete_metric_not_found(self, async_client: AsyncClient):
        response = await async_client.delete("/api/v1/metrics/000000000000000000000000")
        assert response.status_code == 404


class TestMetricAggregations:
    async def test_get_aggregations(
        self, async_client: AsyncClient, sample_metric_data: dict
    ):
        await async_client.post("/api/v1/metrics", json=sample_metric_data)

        response = await async_client.get("/api/v1/metrics/aggregations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_aggregations_by_type(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/metrics/aggregations?metric_type=cpu")
        assert response.status_code == 200


class TestMetricsBySource:
    async def test_get_metrics_by_source(
        self, async_client: AsyncClient, sample_metric_data: dict
    ):
        await async_client.post("/api/v1/metrics", json=sample_metric_data)

        response = await async_client.get(
            f"/api/v1/metrics/source/{sample_metric_data['source']}"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestBatchCreate:
    async def test_create_batch(self, async_client: AsyncClient, sample_metric_data: dict):
        batch = {"metrics": [sample_metric_data, {**sample_metric_data, "value": 80.0}]}
        response = await async_client.post("/api/v1/metrics/batch", json=batch)
        assert response.status_code == 201
        assert "2" in response.json()["message"]

    async def test_create_empty_batch(self, async_client: AsyncClient):
        response = await async_client.post("/api/v1/metrics/batch", json={"metrics": []})
        # Empty batch: either 201 with 0 or 422 — both acceptable
        assert response.status_code in (201, 422)
