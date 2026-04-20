from fastapi import Depends, HTTPException, Request
from app.domain.auth.entities import OAuth2UserInfo


async def get_current_user(request: Request) -> OAuth2UserInfo:
    user_info = getattr(request.state, "user_info", None)
    if not user_info:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_info


async def require_superuser(user: OAuth2UserInfo = Depends(get_current_user)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user
