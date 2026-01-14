"""
자율형 비즈니스 보안 에이전트
Cochl.sense API를 활용한 실시간 소리 이벤트 모니터링 시스템
"""
import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.services.manager_agent import ManagerAgent
from backend.services.zapier_integration import ZapierIntegration
from backend.services.cochl_api import MockCochlAPIClient
from backend.routers import webhook, health, file_upload

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 환경 변수에서 설정값 가져오기
COCHL_API_KEY = os.getenv("COCHL_API_KEY", "")
ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL", "")
EMERGENCY_THRESHOLD = int(os.getenv("EMERGENCY_THRESHOLD", "7"))
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="Cochl 보안 에이전트",
    description="실시간 소리 이벤트 모니터링 및 자동 대응 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 인스턴스 생성
manager = ManagerAgent()
zapier = ZapierIntegration(ZAPIER_WEBHOOK_URL) if ZAPIER_WEBHOOK_URL else None
cochl_client = MockCochlAPIClient()  # Mock 클라이언트 사용 (실제 API 키 불필요)

# 라우터 설정 및 등록
webhook_router = webhook.setup_webhook_router(manager, zapier, EMERGENCY_THRESHOLD)
health_router = health.setup_health_router(COCHL_API_KEY, ZAPIER_WEBHOOK_URL, EMERGENCY_THRESHOLD)
file_upload_router = file_upload.setup_file_upload_router(cochl_client, manager, EMERGENCY_THRESHOLD)

app.include_router(webhook_router)
app.include_router(health_router)
app.include_router(file_upload_router)


if __name__ == "__main__":
    # 시작 전 설정 확인
    logger.info("=" * 60)
    logger.info("자율형 비즈니스 보안 에이전트 시작")
    logger.info("=" * 60)

    # 필수 설정 확인
    if not COCHL_API_KEY:
        logger.warning("⚠️ COCHL_API_KEY가 설정되지 않았습니다!")
    else:
        logger.info(f"✅ Cochl API 키 확인: {COCHL_API_KEY[:10]}...")

    if not ZAPIER_WEBHOOK_URL:
        logger.warning("⚠️ ZAPIER_WEBHOOK_URL이 설정되지 않았습니다!")
    else:
        logger.info(f"✅ Zapier Webhook 확인: {ZAPIER_WEBHOOK_URL[:50]}...")

    logger.info(f"✅ 긴급 상황 기준 점수: {EMERGENCY_THRESHOLD}/10")
    logger.info(f"✅ CORS Origins: {CORS_ORIGINS}")
    logger.info(f"✅ 서버 시작: http://{SERVER_HOST}:{SERVER_PORT}")
    logger.info("=" * 60)

    # Uvicorn 서버 실행
    import uvicorn
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info"
    )
