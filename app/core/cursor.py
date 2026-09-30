import base64
import json
from datetime import datetime

from fastapi import HTTPException, status


def encode_cursor(
    created_at: datetime,
    product_id: int,
) -> str:
    payload = {
        "created_at": created_at.isoformat(),
        "id": product_id,
    }

    json_data = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    return base64.urlsafe_b64encode(json_data).decode()


def decode_cursor(cursor: str) -> tuple[datetime, int]:
    try:
        json_data = base64.urlsafe_b64decode(cursor.encode())
        payload = json.loads(json_data)

        created_at = datetime.fromisoformat(
            payload["created_at"]
        )
        product_id = int(payload["id"])

        return created_at, product_id

    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid cursor",
        )