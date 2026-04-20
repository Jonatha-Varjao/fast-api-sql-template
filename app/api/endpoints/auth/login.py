from fastapi import APIRouter, Query
from starlette.responses import RedirectResponse
from app.config import settings

router = APIRouter()


@router.get("/login")
async def login():
    auth_url = (
        f"{settings.oauth2_server_url}realms/{settings.oauth2_realm}/protocol/openid-connect/auth"
        f"?client_id={settings.oauth2_client_id}&response_type=code&scope=openid+email"
    )
    return RedirectResponse(auth_url)


@router.get("/login/callback")
async def login_callback(code: str = Query(...)):
    # Exchange code for tokens via provider's token endpoint
    # This is a placeholder - implement token exchange with provider
    return {"message": "Token exchange not implemented", "code": code}


@router.get("/logout")
async def logout():
    return {"message": "Logged out"}
