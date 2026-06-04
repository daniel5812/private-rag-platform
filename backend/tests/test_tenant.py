import time
from unittest.mock import patch

import jwt
import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.core.tenant import get_tenant_id, normalize_tenant_id

TEST_SECRET = "test-secret"
TEST_ALGORITHM = "HS256"

def make_token(claims: dict, secret: str = TEST_SECRET, expired: bool = False) -> str:
    payload = dict(claims)

    if expired:
        payload["exp"] = int(time.time()) - 60
    else:
        payload["exp"] = int(time.time()) + 3600

    return jwt.encode(payload, secret, algorithm=TEST_ALGORITHM)

def test_get_tenant_id_returns_tenant_from_valid_jwt():
    token = make_token({"tenant_id": "company-a"})

    with patch.object(settings, "jwt_secret_key", TEST_SECRET):
        with patch.object(settings, "jwt_algorithm", TEST_ALGORITHM):
            tenant_id = get_tenant_id(
                authorization=f"Bearer {token}",
                x_tenant_id="demo",
            )

    assert tenant_id == "company-a"

def test_get_tenant_id_jwt_wins_over_x_tenant_id():
    token = make_token({"tenant_id": "company-a"})

    with patch.object(settings, "jwt_secret_key", TEST_SECRET):
        with patch.object(settings, "jwt_algorithm", TEST_ALGORITHM):
            tenant_id = get_tenant_id(
                authorization=f"Bearer {token}",
                x_tenant_id="company-b",
            )

    assert tenant_id == "company-a"

def test_get_tenant_id_falls_back_to_x_tenant_id_without_authorization():
    tenant_id = get_tenant_id(
        authorization=None,
        x_tenant_id="company-b",
    )

    assert tenant_id == "company-b"

def test_get_tenant_id_rejects_invalid_jwt():
    invalid_token = "not-a-valid-token"

    with patch.object(settings, "jwt_secret_key", TEST_SECRET):
        with pytest.raises(HTTPException) as exc_info:
            get_tenant_id(
                authorization=f"Bearer {invalid_token}",
                x_tenant_id="company-b",
            )

    assert exc_info.value.status_code == 401

def test_get_tenant_id_rejects_jwt_missing_tenant_id():
    token = make_token({"sub": "user-123"})

    with patch.object(settings, "jwt_secret_key", TEST_SECRET):
        with patch.object(settings, "jwt_algorithm", TEST_ALGORITHM):
            with pytest.raises(HTTPException) as exc_info:
                get_tenant_id(
                    authorization=f"Bearer {token}",
                    x_tenant_id="company-b",
                )

    assert exc_info.value.status_code == 401

def test_get_tenant_id_rejects_bearer_when_secret_not_configured():
    token = make_token({"tenant_id": "company-a"})

    with patch.object(settings, "jwt_secret_key", None):
        with pytest.raises(HTTPException) as exc_info:
            get_tenant_id(
                authorization=f"Bearer {token}",
                x_tenant_id="company-b",
            )

    assert exc_info.value.status_code == 401

def test_get_tenant_id_rejects_invalid_authorization_format():
    with pytest.raises(HTTPException) as exc_info:
        get_tenant_id(
            authorization="Token abc",
            x_tenant_id="company-b",
        )

    assert exc_info.value.status_code == 401

