#!/usr/bin/env python3

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

import jwt


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a local development JWT for Private RAG Platform."
    )
    parser.add_argument(
        "--tenant",
        default="demo",
        help="Tenant ID to include in the JWT. Default: demo",
    )
    parser.add_argument(
        "--sub",
        default="dev-user",
        help="Subject/user identifier. Default: dev-user",
    )
    parser.add_argument(
        "--expires-minutes",
        type=int,
        default=120,
        help="Token expiration time in minutes. Default: 120",
    )

    args = parser.parse_args()

    secret = os.getenv("JWT_SECRET_KEY")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    if not secret:
        print(
            "JWT_SECRET_KEY is not set. Export it before creating a token.",
            file=sys.stderr,
        )
        return 1

    now = datetime.now(timezone.utc)

    payload = {
        "sub": args.sub,
        "tenant_id": args.tenant,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=args.expires_minutes)).timestamp()),
    }

    token = jwt.encode(payload, secret, algorithm=algorithm)
    print(token)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())