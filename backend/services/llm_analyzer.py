"""
LLM 기반 상황 분석 서비스 (Claude API)
"""
import logging
import os
from typing import List, Dict, Optional
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """
    Claude API를 사용하여 소리 이벤트의 시간적 순서를 분석하고 상황을 해석
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None

        if self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                logger.info("✅ LLM Analyzer 초기화 완료 (Claude API)")
            except Exception as e:
                logger.error(f"❌ Claude API 초기화 실패: {e}")
                self.client = None
        else:
            logger.warning("⚠️ ANTHROPIC_API_KEY가 설정되지 않았습니다. LLM 분석 비활성화")

    async def analyze_event(self, event: Dict, all_events: List[Dict]) -> Optional[str]:
        """
        개별 이벤트에 대한 상황 해석 생성

        Args:
            event: 현재 분석할 이벤트
            all_events: 전체 이벤트 리스트 (시간적 컨텍스트 제공)

        Returns:
            상황 해석 문자열 또는 None (실패 시)
        """
        if not self.client:
            return None

        try:
            # 시간순 정렬
            sorted_events = sorted(all_events, key=lambda x: x['start_time'])

            # 컨텍스트 구성
            context_lines = []
            for idx, e in enumerate(sorted_events, 1):
                # 현재 분석 중인 이벤트 표시
                marker = "→ " if e['event_id'] == event['event_id'] else "  "
                context_lines.append(
                    f"{marker}{idx}. {e['tag']} (신뢰도: {e['confidence']*100:.1f}%, "
                    f"시간: {e['start_time']:.1f}초~{e['end_time']:.1f}초)"
                )

            context = "\n".join(context_lines)

            # 프롬프트 구성
            prompt = f"""다음은 오디오 파일에서 탐지된 소리 이벤트들입니다:

{context}

화살표(→)로 표시된 이벤트: {event['tag']}

위 이벤트들의 시간적 순서를 고려하여, 화살표로 표시된 이벤트가 보안 관점에서 어떤 상황을 의미하는지 간결하게 해석해주세요.

요구사항:
1. 다른 이벤트들과의 시간적 관계를 명시 (예: "~초 후", "~직전")
2. 보안 위협 수준 평가
3. 2-3문장으로 간결하게
4. 한국어로 작성
5. 전문적이고 명확한 어조"""

            # Claude API 호출
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=300,  # 비용 절감
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            interpretation = message.content[0].text.strip()
            logger.info(f"✅ LLM 분석 완료: event_id={event['event_id']}")
            return interpretation

        except Exception as e:
            logger.error(f"❌ LLM 분석 실패: {e}", exc_info=True)
            return None
