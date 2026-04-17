import os

import httpx
from fastapi import HTTPException, Request

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5241")

async def verify_api_key(request: Request):
    if request.url.path == "/health":
        return

    api_key = request.headers.get("X-API-KEY") or _extract_bearer(request)

    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVICE_URL}/api-keys/verify", 
            json={"raw_key": api_key})
    
    if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid API key")

    request.state.api_key_metadata = response.json()
    return request.state.api_key_metadata


def _extract_bearer(request: Request):
    auth = request.headers.get("Authorization", "")
    bearer = "bearer "
    if auth.lower().startswith(bearer):
        return auth[len(bearer):].strip()
    return None
