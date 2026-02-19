"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestRegister:
    async def test_register_success(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "StrongPass123!",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "password" not in data
        assert "_id" in data

    async def test_register_duplicate_email(self, async_client: AsyncClient, registered_user: dict):
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": registered_user["email"],
                "username": "different_username",
                "password": "StrongPass123!",
                "full_name": "Duplicate",
            },
        )
        assert response.status_code == 400

    async def test_register_invalid_email(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "someuser",
                "password": "StrongPass123!",
                "full_name": "Bad Email",
            },
        )
        assert response.status_code == 422

    async def test_register_missing_fields(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/register",
            json={"email": "partial@example.com"},
        )
        assert response.status_code == 422


class TestLogin:
    async def test_login_success(self, async_client: AsyncClient, registered_user: dict):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": registered_user["password"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, async_client: AsyncClient, registered_user: dict):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": "WrongPassword!"},
        )
        assert response.status_code == 401

    async def test_login_unknown_email(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "Pass123!"},
        )
        assert response.status_code == 401

    async def test_login_missing_fields(self, async_client: AsyncClient):
        response = await async_client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422


class TestGetCurrentUser:
    async def test_get_me_authenticated(
        self, async_client: AsyncClient, registered_user: dict, auth_headers: dict
    ):
        response = await async_client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == registered_user["email"]

    async def test_get_me_unauthenticated(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 403

    async def test_get_me_invalid_token(self, async_client: AsyncClient):
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer this-is-not-a-valid-token"},
        )
        assert response.status_code == 401


class TestRefreshToken:
    async def test_refresh_success(self, async_client: AsyncClient, registered_user: dict):
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": registered_user["email"], "password": registered_user["password"]},
        )
        refresh_token = login_response.json()["refresh_token"]

        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    async def test_refresh_invalid_token(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-refresh-token"},
        )
        assert response.status_code == 401
