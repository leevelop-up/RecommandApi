import httpx
import os
from fastapi import HTTPException, status


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


async def exchange_code_for_user(code: str, redirect_uri: str) -> dict:
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth 설정이 없습니다. 환경변수를 확인하세요.",
        )

    async with httpx.AsyncClient() as client:
        # 1. code → access_token 교환
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google 토큰 교환 실패: {token_resp.text}",
            )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")

        # 2. access_token → 사용자 정보 조회
        user_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google 사용자 정보 조회 실패",
            )
        user_info = user_resp.json()

    return {
        "provider_id": user_info["id"],
        "email": user_info.get("email", ""),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
    }
