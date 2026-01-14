"""
Zapier 통합: 외부 도구 연동
"""
import logging
import requests
from backend.models.sound_event import EmergencyAlert

logger = logging.getLogger(__name__)


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
