import httpx
import os
from fastapi import HTTPException, status


NAVER_TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
NAVER_USERINFO_URL = "https://openapi.naver.com/v1/nid/me"


async def exchange_code_for_user(code: str, state: str) -> dict:
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Naver OAuth 설정이 없습니다. 환경변수를 확인하세요.",
        )

    async with httpx.AsyncClient() as client:
        # 1. code → access_token 교환
        token_resp = await client.post(
            NAVER_TOKEN_URL,
            params={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "state": state,
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Naver 토큰 교환 실패: {token_resp.text}",
            )
        access_token = token_resp.json().get("access_token")

        # 2. access_token → 사용자 정보 조회
        user_resp = await client.get(
            NAVER_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Naver 사용자 정보 조회 실패",
            )
        response_data = user_resp.json().get("response", {})

    return {
        "provider_id": response_data["id"],
        "email": response_data.get("email", f"naver_{response_data['id']}@naver.local"),
        "name": response_data.get("name") or response_data.get("nickname"),
        "picture": response_data.get("profile_image"),
    }
