from fastapi import Request, Depends, FastAPI, HTTPException
from app.middleware.api_key_auth import verify_api_key

app = FastAPI(dependencies=[Depends(verify_api_key)])

@app.get("/health")
def health():
    return {"status": "UP"}

def require_scope(scope: str):
    async def checker(request: Request):
        key_info = getattr(request.state, "api_key", None)
        if not key_info or scope not in key_info.get("scopes", []):
            raise HTTPException(status_code=403, detail=f"Missing required scope: {scope}")
    return checker