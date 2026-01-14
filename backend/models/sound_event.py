"""
소리 이벤트 데이터 모델
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


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
