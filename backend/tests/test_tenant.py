import pytest
from fastapi import HTTPException

from app.core.tenant import normalize_tenant_id


def test_normalize_tenant_id_defaults_to_demo_when_given_demo():
    assert normalize_tenant_id("demo") == "demo"


def test_normalize_tenant_id_returns_header_value():
    assert normalize_tenant_id("company-a") == "company-a"


def test_normalize_tenant_id_strips_whitespace():
    assert normalize_tenant_id("  company-a  ") == "company-a"


def test_normalize_tenant_id_rejects_empty_value():
    with pytest.raises(HTTPException):
        normalize_tenant_id("   ")


def test_normalize_tenant_id_rejects_none():
    with pytest.raises(HTTPException):
        normalize_tenant_id(None)