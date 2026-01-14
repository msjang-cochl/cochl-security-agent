"""
Manager Agent: 소리 분석 및 심각도 평가
"""
import logging
from datetime import datetime
from backend.models.sound_event import SoundEvent

logger = logging.getLogger(__name__)


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
