"""
Webhook 라우터: Cochl API 웹훅 처리
"""
import json
import logging
from datetime import datetime
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from backend.models.sound_event import SoundEvent, EmergencyAlert
from backend.services.manager_agent import ManagerAgent
from backend.services.zapier_integration import ZapierIntegration

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/webhook",
    tags=["webhook"]
)


def setup_webhook_router(manager: ManagerAgent, zapier: ZapierIntegration, emergency_threshold: int):
    """웹훅 라우터에 의존성 주입"""

    @router.post("/cochl")
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
            if severity_score >= emergency_threshold:
                # 긴급 상황: Zapier로 알림 전송
                logger.warning(
                    f"🚨 긴급 상황 감지! (점수: {severity_score}/{emergency_threshold})"
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
                    f"ℹ️ 일반 이벤트 (점수: {severity_score}/{emergency_threshold}) - "
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

    return router
