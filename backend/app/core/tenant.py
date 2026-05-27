from fastapi import Header, HTTPException


def normalize_tenant_id(value: str | None) -> str:
    tenant_id = (value or "").strip()

    if not tenant_id:
        raise HTTPException(status_code=400, detail="Missing tenant id")

    return tenant_id


def get_tenant_id(x_tenant_id: str | None = Header(default="demo")) -> str:
    return normalize_tenant_id(x_tenant_id)