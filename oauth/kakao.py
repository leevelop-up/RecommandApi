import httpx
import os
from fastapi import HTTPException, status


KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USERINFO_URL = "https://kapi.kakao.com/v2/user/me"


async def exchange_code_for_user(code: str, redirect_uri: str) -> dict:
    client_id = os.getenv("KAKAO_CLIENT_ID")
    client_secret = os.getenv("KAKAO_CLIENT_SECRET", "")  # 선택적

    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Kakao OAuth 설정이 없습니다. 환경변수를 확인하세요.",
        )

    async with httpx.AsyncClient() as client:
        # 1. code → access_token 교환
        token_data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code": code,
        }
        if client_secret:
            token_data["client_secret"] = client_secret

        token_resp = await client.post(
            KAKAO_TOKEN_URL,
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Kakao 토큰 교환 실패: {token_resp.text}",
            )
        access_token = token_resp.json().get("access_token")

        # 2. access_token → 사용자 정보 조회
        user_resp = await client.get(
            KAKAO_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kakao 사용자 정보 조회 실패",
            )
        user_info = user_resp.json()

    kakao_account = user_info.get("kakao_account", {})
    profile = kakao_account.get("profile", {})
    email = kakao_account.get("email", f"kakao_{user_info['id']}@kakao.local")

    return {
        "provider_id": str(user_info["id"]),
        "email": email,
        "name": profile.get("nickname"),
        "picture": profile.get("profile_image_url"),
    }
