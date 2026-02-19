"""Tests for alert endpoints."""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestCreateAlert:
    async def test_create_alert_success(
        self, async_client: AsyncClient, sample_alert_data: dict
    ):
        response = await async_client.post("/api/v1/alerts", json=sample_alert_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_alert_data["title"]
        assert data["severity"] == sample_alert_data["severity"]
        assert data["source"] == sample_alert_data["source"]
        assert data["status"] == "active"
        assert "_id" in data
        assert "created_at" in data

    async def test_create_alert_all_severities(self, async_client: AsyncClient):
        severities = ["info", "warning", "error", "critical"]
        for sev in severities:
            response = await async_client.post(
                "/api/v1/alerts",
                json={"title": f"Test {sev}", "severity": sev, "source": "test"},
            )
            assert response.status_code == 201, f"Failed for severity {sev}: {response.text}"

    async def test_create_alert_missing_required(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/alerts",
            json={"severity": "warning"},  # missing title and source
        )
        assert response.status_code == 422

    async def test_create_alert_with_labels(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/alerts",
            json={
                "title": "Labeled Alert",
                "source": "prod-node-1",
                "severity": "error",
                "labels": {"env": "production", "team": "infra"},
            },
        )
        assert response.status_code == 201
        assert response.json()["labels"]["env"] == "production"


class TestListAlerts:
    async def test_list_alerts_paginated(
        self, async_client: AsyncClient, sample_alert_data: dict
    ):
        await async_client.post("/api/v1/alerts", json=sample_alert_data)

        response = await async_client.get("/api/v1/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    async def test_list_alerts_filter_by_status(
        self, async_client: AsyncClient, sample_alert_data: dict
    ):
        await async_client.post("/api/v1/alerts", json=sample_alert_data)

        response = await async_client.get("/api/v1/alerts?status=active")
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["status"] == "active"

    async def test_list_alerts_pagination(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/alerts?page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert len(data["items"]) <= 5


class TestGetAlert:
    async def test_get_alert_by_id(
        self, async_client: AsyncClient, sample_alert_data: dict
    ):
        create_response = await async_client.post("/api/v1/alerts", json=sample_alert_data)
        alert_id = create_response.json()["_id"]

        response = await async_client.get(f"/api/v1/alerts/{alert_id}")
        assert response.status_code == 200
        assert response.json()["_id"] == alert_id

    async def test_get_alert_not_found(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/alerts/000000000000000000000000")
        assert response.status_code == 404


class TestAlertActions:
    async def test_acknowledge_alert(
        self,
        async_client: AsyncClient,
        sample_alert_data: dict,
        auth_headers: dict,
    ):
        create_response = await async_client.post("/api/v1/alerts", json=sample_alert_data)
        alert_id = create_response.json()["_id"]

        response = await async_client.post(
            f"/api/v1/alerts/{alert_id}/acknowledge",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "acknowledged"
        assert data["acknowledged_by"] is not None
        assert data["acknowledged_at"] is not None

    async def test_acknowledge_requires_auth(
        self, async_client: AsyncClient, sample_alert_data: dict
    ):
        create_response = await async_client.post("/api/v1/alerts", json=sample_alert_data)
        alert_id = create_response.json()["_id"]

        response = await async_client.post(f"/api/v1/alerts/{alert_id}/acknowledge")
        assert response.status_code == 403

    async def test_resolve_alert(
        self, async_client: AsyncClient, sample_alert_data: dict
    ):
        create_response = await async_client.post("/api/v1/alerts", json=sample_alert_data)
        alert_id = create_response.json()["_id"]

        response = await async_client.post(f"/api/v1/alerts/{alert_id}/resolve")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"
        assert data["resolved_at"] is not None

    async def test_acknowledge_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        response = await async_client.post(
            "/api/v1/alerts/000000000000000000000000/acknowledge",
            headers=auth_headers,
        )
        assert response.status_code == 404

    async def test_resolve_not_found(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/alerts/000000000000000000000000/resolve"
        )
        assert response.status_code == 404


class TestUpdateAlert:
    async def test_update_alert_status(
        self, async_client: AsyncClient, sample_alert_data: dict
    ):
        create_response = await async_client.post("/api/v1/alerts", json=sample_alert_data)
        alert_id = create_response.json()["_id"]

        response = await async_client.patch(
            f"/api/v1/alerts/{alert_id}",
            json={"severity": "critical"},
        )
        assert response.status_code == 200
        assert response.json()["severity"] == "critical"


class TestDeleteAlert:
    async def test_delete_alert_success(
        self, async_client: AsyncClient, sample_alert_data: dict
    ):
        create_response = await async_client.post("/api/v1/alerts", json=sample_alert_data)
        alert_id = create_response.json()["_id"]

        response = await async_client.delete(f"/api/v1/alerts/{alert_id}")
        assert response.status_code == 200

        get_response = await async_client.get(f"/api/v1/alerts/{alert_id}")
        assert get_response.status_code == 404

    async def test_delete_alert_not_found(self, async_client: AsyncClient):
        response = await async_client.delete("/api/v1/alerts/000000000000000000000000")
        assert response.status_code == 404


class TestAlertStats:
    async def test_get_alert_stats(
        self, async_client: AsyncClient, sample_alert_data: dict
    ):
        await async_client.post("/api/v1/alerts", json=sample_alert_data)

        response = await async_client.get("/api/v1/alerts/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_active" in data
        assert "total_acknowledged" in data
        assert "total_resolved" in data
        assert "by_severity" in data
        assert "by_source" in data


class TestAlertRules:
    async def test_create_alert_rule(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        response = await async_client.post(
            "/api/v1/alerts/rules",
            json={
                "name": "High CPU Rule",
                "description": "Fires when CPU > 80%",
                "severity": "warning",
                "conditions": [],
                "cooldown_minutes": 5,
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "High CPU Rule"
        assert "_id" in data

    async def test_create_alert_rule_requires_auth(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/alerts/rules",
            json={"name": "Test Rule", "severity": "warning"},
        )
        assert response.status_code == 403

    async def test_list_alert_rules(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        response = await async_client.get("/api/v1/alerts/rules", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    async def test_get_alert_rule(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        create_response = await async_client.post(
            "/api/v1/alerts/rules",
            json={"name": "Get Rule Test", "severity": "info"},
            headers=auth_headers,
        )
        rule_id = create_response.json()["_id"]

        response = await async_client.get(f"/api/v1/alerts/rules/{rule_id}")
        assert response.status_code == 200
        assert response.json()["_id"] == rule_id

    async def test_toggle_alert_rule(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        create_response = await async_client.post(
            "/api/v1/alerts/rules",
            json={"name": "Toggle Rule", "severity": "warning"},
            headers=auth_headers,
        )
        rule_id = create_response.json()["_id"]

        # Disable
        response = await async_client.post(
            f"/api/v1/alerts/rules/{rule_id}/toggle?enabled=false"
        )
        assert response.status_code == 200
        assert response.json()["enabled"] is False

        # Re-enable
        response = await async_client.post(
            f"/api/v1/alerts/rules/{rule_id}/toggle?enabled=true"
        )
        assert response.status_code == 200
        assert response.json()["enabled"] is True

    async def test_delete_alert_rule(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        create_response = await async_client.post(
            "/api/v1/alerts/rules",
            json={"name": "Delete Rule", "severity": "info"},
            headers=auth_headers,
        )
        rule_id = create_response.json()["_id"]

        response = await async_client.delete(f"/api/v1/alerts/rules/{rule_id}")
        assert response.status_code == 200

        get_response = await async_client.get(f"/api/v1/alerts/rules/{rule_id}")
        assert get_response.status_code == 404
