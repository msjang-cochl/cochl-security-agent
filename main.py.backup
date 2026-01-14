"""
자율형 비즈니스 보안 에이전트
Cochl.sense API를 활용한 실시간 소리 이벤트 모니터링 시스템
"""

# ============================================
# 필요한 라이브러리 가져오기
# ============================================
import os  # 운영체제 관련 기능 (파일, 환경변수 등)
import json  # JSON 데이터 처리
import logging  # 로그 기록용
from datetime import datetime  # 날짜/시간 처리
from typing import Dict, Any, Optional  # 타입 힌트용

# FastAPI: 웹 서버를 만들기 위한 프레임워크
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse

# Pydantic: 데이터 검증 및 구조화
from pydantic import BaseModel, Field

# Requests: HTTP 요청 (Zapier Webhook 호출용)
import requests

# python-dotenv: .env 파일에서 환경변수 읽어오기
from dotenv import load_dotenv

# ============================================
# 환경 변수 로드
# ============================================
# .env 파일에서 API 키와 설정값을 읽어옵니다
load_dotenv()

# ============================================
# 로깅 설정
# ============================================
# 시스템의 동작을 기록하기 위한 로거를 설정합니다
logging.basicConfig(
    level=logging.INFO,  # INFO 레벨 이상의 로그만 출력
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 로그 형식
    handlers=[
        logging.FileHandler('security_agent.log'),  # 파일에 로그 저장
        logging.StreamHandler()  # 콘솔에도 로그 출력
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# FastAPI 애플리케이션 생성
# ============================================
app = FastAPI(
    title="Cochl 보안 에이전트",
    description="실시간 소리 이벤트 모니터링 및 자동 대응 시스템",
    version="1.0.0"
)

# ============================================
# 환경 변수에서 설정값 가져오기
# ============================================
# Cochl API 키
COCHL_API_KEY = os.getenv("COCHL_API_KEY", "")
# Zapier Webhook URL
ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL", "")
# 긴급 상황 판단 기준 점수 (기본값: 7점)
EMERGENCY_THRESHOLD = int(os.getenv("EMERGENCY_THRESHOLD", "7"))
# 서버 포트
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
# 서버 호스트
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")

# ============================================
# 데이터 모델 정의 (Pydantic)
# ============================================

class SoundEvent(BaseModel):
    """
    Cochl API로부터 받는 소리 이벤트 데이터 구조
    실제 Cochl API의 응답 형식에 맞게 조정이 필요할 수 있습니다
    """
    # 이벤트 고유 ID
    event_id: Optional[str] = Field(None, description="이벤트 고유 식별자")

    # 감지된 소리 태그 (예: "scream", "siren", "glass_break")
    tag: str = Field(..., description="감지된 소리 종류")

    # 신뢰도 점수 (0.0 ~ 1.0)
    confidence: float = Field(..., description="감지 신뢰도", ge=0.0, le=1.0)

    # 감지 시각 (ISO 8601 형식)
    timestamp: Optional[str] = Field(None, description="이벤트 발생 시각")

    # 추가 메타데이터
    metadata: Optional[Dict[str, Any]] = Field(None, description="추가 정보")


class EmergencyAlert(BaseModel):
    """
    Zapier로 전송할 긴급 알림 데이터 구조
    """
    # 심각도 점수
    severity_score: int = Field(..., description="심각도 점수 (1-10)")

    # 감지된 소리
    sound_type: str = Field(..., description="감지된 소리 종류")

    # 신뢰도
    confidence: float = Field(..., description="감지 신뢰도")

    # 발생 시각
    timestamp: str = Field(..., description="이벤트 발생 시각")

    # 알림 메시지
    message: str = Field(..., description="알림 메시지")

    # 이벤트 ID
    event_id: Optional[str] = Field(None, description="이벤트 ID")


# ============================================
# Manager Agent: 소리 분석 및 심각도 평가
# ============================================

class ManagerAgent:
    """
    소리 이벤트를 분석하고 심각도를 평가하는 관리 에이전트
    """

    # 소리 종류별 기본 심각도 점수 (1-10)
    # 실제 비즈니스 환경에 맞게 조정하세요
    SOUND_SEVERITY_MAP = {
        # 긴급 상황 (8-10점)
        "scream": 9,           # 비명
        "gunshot": 10,         # 총성
        "explosion": 10,       # 폭발음
        "glass_break": 8,      # 유리 깨지는 소리
        "fire_alarm": 9,       # 화재 경보

        # 경고 상황 (5-7점)
        "siren": 7,            # 사이렌
        "car_alarm": 6,        # 차량 경보
        "dog_bark": 5,         # 개 짖는 소리
        "crying": 6,           # 울음소리
        "door_slam": 5,        # 문 쾅 닫히는 소리

        # 일반 상황 (1-4점)
        "footsteps": 2,        # 발소리
        "conversation": 1,     # 대화 소리
        "music": 2,            # 음악
        "traffic": 3,          # 교통 소음
        "machinery": 4,        # 기계 소음
    }

    def __init__(self):
        """
        Manager Agent 초기화
        """
        logger.info("Manager Agent 초기화 완료")

    def calculate_severity(self, sound_event: SoundEvent) -> int:
        """
        소리 이벤트의 심각도를 계산합니다

        매개변수:
            sound_event: Cochl로부터 받은 소리 이벤트

        반환값:
            심각도 점수 (1-10)
        """
        # 1. 소리 종류에 따른 기본 점수 가져오기
        base_score = self.SOUND_SEVERITY_MAP.get(
            sound_event.tag.lower(),  # 소문자로 변환하여 매칭
            5  # 매핑되지 않은 소리는 기본값 5점
        )

        # 2. 신뢰도를 반영하여 최종 점수 계산
        # 신뢰도가 높을수록 점수가 올라갑니다
        # 예: base_score=9, confidence=0.9 → 9 * 0.9 = 8.1 → 8점
        final_score = int(base_score * sound_event.confidence)

        # 3. 점수 범위를 1-10으로 제한
        final_score = max(1, min(10, final_score))

        # 4. 로그 기록
        logger.info(
            f"심각도 계산 완료: 소리={sound_event.tag}, "
            f"신뢰도={sound_event.confidence:.2f}, "
            f"기본점수={base_score}, 최종점수={final_score}"
        )

        return final_score

    def create_alert_message(self, sound_event: SoundEvent, severity: int) -> str:
        """
        알림 메시지를 생성합니다

        매개변수:
            sound_event: 소리 이벤트
            severity: 심각도 점수

        반환값:
            알림 메시지 문자열
        """
        # 심각도에 따른 이모지 설정
        if severity >= 8:
            emoji = "🚨"
            level = "긴급"
        elif severity >= 5:
            emoji = "⚠️"
            level = "경고"
        else:
            emoji = "ℹ️"
            level = "정보"

        # 메시지 생성
        message = (
            f"{emoji} [{level}] 보안 이벤트 감지\n"
            f"소리 종류: {sound_event.tag}\n"
            f"신뢰도: {sound_event.confidence * 100:.1f}%\n"
            f"심각도: {severity}/10\n"
            f"시각: {sound_event.timestamp or datetime.now().isoformat()}"
        )

        return message


# ============================================
# Zapier 통합: 외부 도구 연동
# ============================================

class ZapierIntegration:
    """
    Zapier Webhook을 통해 Slack, Jira 등과 연동하는 클래스
    """

    def __init__(self, webhook_url: str):
        """
        Zapier 통합 초기화

        매개변수:
            webhook_url: Zapier Webhook URL
        """
        self.webhook_url = webhook_url
        logger.info(f"Zapier 통합 초기화: {webhook_url[:50]}...")

    def send_alert(self, alert: EmergencyAlert) -> bool:
        """
        긴급 알림을 Zapier로 전송합니다

        매개변수:
            alert: 긴급 알림 데이터

        반환값:
            성공 여부 (True/False)
        """
        try:
            # 1. 알림 데이터를 JSON으로 변환
            payload = alert.model_dump()

            # 2. Zapier Webhook으로 POST 요청 전송
            logger.info(f"Zapier로 알림 전송 시작: severity={alert.severity_score}")

            response = requests.post(
                self.webhook_url,
                json=payload,  # JSON 형식으로 데이터 전송
                headers={"Content-Type": "application/json"},
                timeout=10  # 10초 타임아웃
            )

            # 3. 응답 확인
            response.raise_for_status()  # 에러 발생시 예외 발생

            # 4. 성공 로그
            logger.info(
                f"Zapier 알림 전송 성공: "
                f"status_code={response.status_code}, "
                f"response={response.text[:100]}"
            )

            return True

        except requests.exceptions.Timeout:
            # 타임아웃 에러 처리
            logger.error("Zapier 알림 전송 실패: 타임아웃")
            return False

        except requests.exceptions.RequestException as e:
            # 기타 네트워크 에러 처리
            logger.error(f"Zapier 알림 전송 실패: {str(e)}")
            return False

        except Exception as e:
            # 예상치 못한 에러 처리
            logger.error(f"Zapier 알림 전송 중 오류 발생: {str(e)}")
            return False


# ============================================
# 전역 인스턴스 생성
# ============================================

# Manager Agent 인스턴스
manager = ManagerAgent()

# Zapier 통합 인스턴스 (Webhook URL이 있을 때만)
zapier = ZapierIntegration(ZAPIER_WEBHOOK_URL) if ZAPIER_WEBHOOK_URL else None


# ============================================
# API 엔드포인트: Cochl Webhook 수신
# ============================================

@app.post("/webhook/cochl")
async def receive_cochl_event(request: Request):
    """
    Cochl API로부터 소리 이벤트를 수신하는 Webhook 엔드포인트

    Cochl 대시보드에서 이 URL을 Webhook으로 등록하세요:
    예: http://your-server.com:8000/webhook/cochl
    """
    try:
        # 1. 요청 데이터 파싱
        logger.info("=== Cochl Webhook 요청 수신 ===")

        # 원본 JSON 데이터 읽기
        body = await request.json()
        logger.info(f"수신 데이터: {json.dumps(body, indent=2, ensure_ascii=False)}")

        # 2. 데이터 검증 및 변환
        # 실제 Cochl API 응답 형식에 맞게 필드명을 조정해야 할 수 있습니다
        sound_event = SoundEvent(**body)

        # 3. Manager Agent로 심각도 분석
        logger.info(f"Manager Agent 분석 시작...")
        severity_score = manager.calculate_severity(sound_event)

        # 4. 알림 메시지 생성
        alert_message = manager.create_alert_message(sound_event, severity_score)

        # 5. 긴급 상황 판단 및 대응
        if severity_score >= EMERGENCY_THRESHOLD:
            # 긴급 상황: Zapier로 알림 전송
            logger.warning(
                f"🚨 긴급 상황 감지! (점수: {severity_score}/{EMERGENCY_THRESHOLD})"
            )

            # Zapier가 설정되어 있는지 확인
            if not zapier:
                logger.error("Zapier Webhook URL이 설정되지 않았습니다!")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "status": "error",
                        "message": "Zapier가 설정되지 않음",
                        "severity_score": severity_score
                    }
                )

            # 긴급 알림 데이터 생성
            alert = EmergencyAlert(
                severity_score=severity_score,
                sound_type=sound_event.tag,
                confidence=sound_event.confidence,
                timestamp=sound_event.timestamp or datetime.now().isoformat(),
                message=alert_message,
                event_id=sound_event.event_id
            )

            # Zapier로 알림 전송
            success = zapier.send_alert(alert)

            if success:
                logger.info("✅ 긴급 알림 전송 완료")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "status": "emergency_alert_sent",
                        "severity_score": severity_score,
                        "message": "긴급 알림이 전송되었습니다",
                        "alert": alert.model_dump()
                    }
                )
            else:
                logger.error("❌ 긴급 알림 전송 실패")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "status": "alert_failed",
                        "severity_score": severity_score,
                        "message": "알림 전송에 실패했습니다"
                    }
                )

        else:
            # 일반 상황: 로그만 기록
            logger.info(
                f"ℹ️ 일반 이벤트 (점수: {severity_score}/{EMERGENCY_THRESHOLD}) - "
                f"로그만 기록"
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "logged",
                    "severity_score": severity_score,
                    "message": "이벤트가 기록되었습니다",
                    "alert_message": alert_message
                }
            )

    except Exception as e:
        # 에러 처리
        logger.error(f"❌ Webhook 처리 중 오류 발생: {str(e)}", exc_info=True)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": f"처리 중 오류 발생: {str(e)}"
            }
        )


# ============================================
# API 엔드포인트: 헬스체크
# ============================================

@app.get("/")
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
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """
    시스템 상태를 확인하는 헬스체크 엔드포인트
    """
    # 설정 상태 확인
    config_status = {
        "cochl_api_configured": bool(COCHL_API_KEY),
        "zapier_configured": bool(ZAPIER_WEBHOOK_URL),
        "emergency_threshold": EMERGENCY_THRESHOLD
    }

    # 전체 상태 판단
    is_healthy = config_status["cochl_api_configured"] and config_status["zapier_configured"]

    return {
        "status": "healthy" if is_healthy else "degraded",
        "timestamp": datetime.now().isoformat(),
        "configuration": config_status
    }


# ============================================
# 메인 실행 함수
# ============================================

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
