import jwt
from fastapi import Header, HTTPException

from app.core.config import settings


def normalize_tenant_id(value: str | None) -> str:
    tenant_id = (value or "").strip()

    if not tenant_id:
        raise HTTPException(status_code=400, detail="Missing tenant id")

    return tenant_id


def _decode_jwt_tenant(authorization: str) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format",
        )

    token = authorization.removeprefix("Bearer ").strip()

    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    if not settings.jwt_secret_key:
        raise HTTPException(
            status_code=401,
            detail="JWT authentication not configured",
        )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="JWT has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid JWT")

    tenant_id = payload.get("tenant_id")

    if not tenant_id:
        raise HTTPException(
            status_code=401,
            detail="JWT missing tenant_id claim",
        )

    return normalize_tenant_id(tenant_id)


def get_tenant_id(
    authorization: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default="demo"),
) -> str:
    if authorization:
        return _decode_jwt_tenant(authorization)

    if settings.auth_dev_mode:
        return normalize_tenant_id(x_tenant_id)

    raise HTTPException(
        status_code=401,
        detail="Authentication required",
    )