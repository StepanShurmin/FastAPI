import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("kot@pes.com", "kotopes", 200),
        ("kot@pes.com", "kot0pes", 409),
        ("pes@kot.com", "pesakot", 200),
        ("peskot", "pesakot", 422),
    ],
)
async def test_register_user(email, password, status_code, ac: AsyncClient):
    responce = await ac.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert responce.status_code == status_code


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("test1@example.com", "test1", 200),
        ("test2@example.com", "test2", 200),
        ("other2@example.com", "other", 401),
    ],
)
async def test_login_user(email, password, status_code, ac: AsyncClient):
    responce = await ac.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert responce.status_code == status_code
