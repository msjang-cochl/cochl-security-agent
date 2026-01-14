"""
헬스체크 라우터
"""
from datetime import datetime
from fastapi import APIRouter

router = APIRouter(tags=["health"])


def setup_health_router(cochl_api_key: str, zapier_webhook_url: str, emergency_threshold: int):
    """헬스체크 라우터 설정"""

    @router.get("/")
    async def root():
        """
        서버 상태 확인용 엔드포인트
        브라우저에서 http://localhost:8000 접속시 표시됩니다
        """
        return {
            "service": "Cochl 보안 에이전트",
            "status": "running",
            "version": "1.0.0",
            "endpoints": {
                "webhook": "/webhook/cochl",
                "health": "/health",
                "docs": "/docs",
                "api": "/api/v1"
            }
        }

    @router.get("/health")
    async def health_check():
        """
        시스템 상태를 확인하는 헬스체크 엔드포인트
        """
        # 설정 상태 확인
        config_status = {
            "cochl_api_configured": bool(cochl_api_key),
            "zapier_configured": bool(zapier_webhook_url),
            "emergency_threshold": emergency_threshold
        }

        # 전체 상태 판단
        is_healthy = config_status["cochl_api_configured"] and config_status["zapier_configured"]

        return {
            "status": "healthy" if is_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "configuration": config_status
        }

    return router
