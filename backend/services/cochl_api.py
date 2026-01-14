"""
Cochl Cloud API 클라이언트
"""
import logging
import asyncio
from typing import List, Optional
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class DetectionResult:
    """탐지 결과 데이터 클래스"""

    def __init__(self, tag: str, confidence: float, start_time: float = 0.0, end_time: float = 0.0):
        self.tag = tag
        self.confidence = confidence
        self.start_time = start_time
        self.end_time = end_time
        self.event_id = f"evt_{int(datetime.now().timestamp())}"


class CochlAPIClient:
    """
    Cochl Cloud API와 통신하는 클라이언트

    참고: 이 구현은 Cochl.sense Cloud API의 실제 엔드포인트와 스키마에 맞게
    조정이 필요합니다. 현재는 기본 구조만 제공합니다.
    """

    def __init__(self, api_key: str, api_url: str = "https://api.cochl.ai/v1"):
        """
        Cochl API 클라이언트 초기화

        매개변수:
            api_key: Cochl API 키
            api_url: Cochl API 베이스 URL
        """
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        logger.info(f"Cochl API 클라이언트 초기화: {api_url}")

    async def analyze_file(self, file_bytes: bytes, filename: str) -> List[DetectionResult]:
        """
        오디오/비디오 파일을 Cochl API로 전송하여 분석

        매개변수:
            file_bytes: 파일 바이트 데이터
            filename: 파일명

        반환값:
            DetectionResult 리스트
        """
        try:
            logger.info(f"Cochl API로 파일 분석 요청: {filename}")

            # 실제 Cochl API 엔드포인트 및 요청 형식에 맞게 조정 필요
            async with httpx.AsyncClient(timeout=60.0) as client:
                # 파일 업로드
                files = {"file": (filename, file_bytes)}

                # 실제 API 엔드포인트는 Cochl 문서 참조
                # 예시: POST https://api.cochl.ai/v1/analyze
                response = await client.post(
                    f"{self.api_url}/analyze",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files=files
                )

                response.raise_for_status()
                data = response.json()

                # 응답 파싱 (실제 Cochl API 응답 형식에 맞게 조정 필요)
                results = []

                # 예상 응답 형식:
                # {
                #     "detections": [
                #         {"tag": "scream", "confidence": 0.95, "start_time": 12.5, "end_time": 13.8}
                #     ]
                # }

                detections = data.get("detections", [])
                for detection in detections:
                    result = DetectionResult(
                        tag=detection.get("tag", "unknown"),
                        confidence=detection.get("confidence", 0.0),
                        start_time=detection.get("start_time", 0.0),
                        end_time=detection.get("end_time", 0.0)
                    )
                    results.append(result)

                logger.info(f"분석 완료: {len(results)}개의 사운드 이벤트 탐지")
                return results

        except httpx.HTTPStatusError as e:
            logger.error(f"Cochl API HTTP 에러: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Cochl API 요청 에러: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Cochl API 호출 중 예상치 못한 에러: {str(e)}")
            raise

    async def get_analysis_status(self, task_id: str) -> dict:
        """
        분석 작업 상태 조회 (비동기 처리용)

        매개변수:
            task_id: 작업 ID

        반환값:
            상태 정보 딕셔너리
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.api_url}/status/{task_id}",
                    headers=self.headers
                )

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"상태 조회 에러: {str(e)}")
            raise


class MockCochlAPIClient(CochlAPIClient):
    """
    테스트용 Mock Cochl API 클라이언트
    실제 API 호출 없이 더미 데이터를 반환합니다.
    """

    def __init__(self, api_key: str = "mock_key", api_url: str = "mock://api"):
        super().__init__(api_key, api_url)
        logger.info("Mock Cochl API 클라이언트 초기화 (테스트 모드)")

    async def analyze_file(self, file_bytes: bytes, filename: str) -> List[DetectionResult]:
        """
        Mock 분석 결과 반환
        """
        logger.info(f"Mock 분석 시작: {filename} ({len(file_bytes)} bytes)")

        # 짧은 지연 시뮬레이션
        await asyncio.sleep(1)

        # 더미 탐지 결과 반환
        # 파일명에 특정 키워드가 있으면 해당 사운드를 탐지한 것처럼 반환
        results = []

        filename_lower = filename.lower()

        if "scream" in filename_lower or "비명" in filename_lower:
            results.append(DetectionResult("scream", 0.95, 2.5, 3.8))

        if "glass" in filename_lower or "유리" in filename_lower:
            results.append(DetectionResult("glass_break", 0.88, 5.2, 6.0))

        if "siren" in filename_lower or "사이렌" in filename_lower:
            results.append(DetectionResult("siren", 0.92, 0.0, 10.0))

        if "gunshot" in filename_lower or "총" in filename_lower:
            results.append(DetectionResult("gunshot", 0.97, 1.2, 1.5))

        # 키워드가 없으면 랜덤 일반 소리 탐지
        if not results:
            results.append(DetectionResult("conversation", 0.65, 0.0, 30.0))

        logger.info(f"Mock 분석 완료: {len(results)}개 탐지")
        return results
