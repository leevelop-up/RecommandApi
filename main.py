from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import os

app = FastAPI(
    title="Recommand Stock API",
    description="주식 추천 및 데이터 제공 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API 루트"""
    return {
        "service": "Recommand Stock API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """헬스체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/stocks")
async def get_stocks(
    market: Optional[str] = Query(None, description="시장 구분 (KOSPI, KOSDAQ, NASDAQ)"),
    limit: int = Query(100, ge=1, le=1000)
):
    """종목 목록 조회"""
    # TODO: 실제 데이터베이스 연동
    return {
        "stocks": [],
        "total": 0,
        "market": market,
        "limit": limit
    }

@app.get("/api/v1/stocks/{ticker}")
async def get_stock_detail(ticker: str):
    """종목 상세 정보"""
    # TODO: 실제 데이터베이스 연동
    return {
        "ticker": ticker,
        "name": "종목명",
        "current_price": 0,
        "change": 0,
        "change_percent": 0
    }

@app.get("/api/v1/recommendations")
async def get_recommendations(
    type: Optional[str] = Query("all", description="추천 타입 (ai, rule, growth)"),
    limit: int = Query(10, ge=1, le=100)
):
    """AI 추천 종목"""
    # TODO: 실제 추천 데이터 연동
    return {
        "recommendations": [],
        "type": type,
        "generated_at": datetime.now().isoformat()
    }

@app.get("/api/v1/market/indices")
async def get_market_indices():
    """시장 지수"""
    # TODO: 실제 시장 지수 데이터
    return {
        "indices": [
            {"name": "KOSPI", "value": 0, "change": 0},
            {"name": "KOSDAQ", "value": 0, "change": 0},
            {"name": "NASDAQ", "value": 0, "change": 0}
        ]
    }

@app.get("/api/v1/news")
async def get_news(
    ticker: Optional[str] = Query(None, description="종목 코드"),
    limit: int = Query(20, ge=1, le=100)
):
    """뉴스 목록"""
    # TODO: 실제 뉴스 데이터
    return {
        "news": [],
        "ticker": ticker,
        "total": 0
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
