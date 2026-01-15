"""
파일 업로드 및 분석 라우터
"""
import uuid
import logging
from typing import Dict
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.models.sound_event import SoundEvent
from backend.services.manager_agent import ManagerAgent
from backend.services.llm_analyzer import LLMAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["analysis"]
)

# 작업 상태 저장 (프로덕션에서는 Redis 사용 권장)
tasks: Dict[str, dict] = {}


class FileInfo(BaseModel):
    """파일 정보"""
    filename: str
    size: int
    format: str


class AnalyzeResponse(BaseModel):
    """파일 분석 응답 모델"""
    task_id: str
    status: str
    file_info: FileInfo


class DetectionResultModel(BaseModel):
    """탐지 결과 모델"""
    event_id: str
    tag: str
    confidence: float
    start_time: float
    end_time: float
    severity_score: int
    message: str


def setup_file_upload_router(
    cochl_client,
    manager_agent: ManagerAgent,
    emergency_threshold: int,
    llm_analyzer: LLMAnalyzer = None
):
    """파일 업로드 라우터 설정"""

    @router.post("/analyze", response_model=AnalyzeResponse)
    async def analyze_file(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...)
    ):
        """
        오디오/비디오 파일 업로드 및 분석

        지원 형식: mp3, wav, ogg, m4a, mp4, webm
        최대 크기: 50MB
        """
        # 파일 크기 검증 (50MB)
        MAX_FILE_SIZE = 50 * 1024 * 1024
        file_bytes = await file.read()

        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="파일 크기가 50MB를 초과합니다")

        # 파일 형식 검증
        allowed_formats = [".mp3", ".wav", ".ogg", ".m4a", ".mp4", ".webm", ".avi"]
        if not any(file.filename.lower().endswith(fmt) for fmt in allowed_formats):
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_formats)}"
            )

        # 작업 ID 생성
        task_id = str(uuid.uuid4())

        # 작업 상태 초기화
        tasks[task_id] = {
            "status": "processing",
            "filename": file.filename,
            "file_size": len(file_bytes),
            "content_type": file.content_type or "unknown",
            "results": None,
            "error": None
        }

        logger.info(f"파일 분석 시작: task_id={task_id}, filename={file.filename}, size={len(file_bytes)} bytes")

        # 백그라운드에서 파일 분석 실행
        async def process_file():
            try:
                # Cochl API로 파일 분석
                logger.info(f"Cochl API 호출 중... task_id={task_id}")
                cochl_results = await cochl_client.analyze_file(file_bytes, file.filename)

                # Manager Agent로 심각도 계산
                processed_results = []
                for cochl_result in cochl_results:
                    # SoundEvent 객체 생성
                    sound_event = SoundEvent(
                        event_id=cochl_result.event_id,
                        tag=cochl_result.tag,
                        confidence=cochl_result.confidence,
                        timestamp=datetime.now().isoformat(),
                        metadata={
                            "start_time": cochl_result.start_time,
                            "end_time": cochl_result.end_time
                        }
                    )

                    # 심각도 계산
                    severity_score = manager_agent.calculate_severity(sound_event)
                    alert_message = manager_agent.create_alert_message(sound_event, severity_score)

                    processed_results.append({
                        "event_id": cochl_result.event_id,
                        "tag": cochl_result.tag,
                        "confidence": cochl_result.confidence,
                        "start_time": cochl_result.start_time,
                        "end_time": cochl_result.end_time,
                        "severity_score": severity_score,
                        "message": alert_message,
                        "is_emergency": severity_score >= emergency_threshold,
                        "interpretation": None  # 초기값
                    })

                # LLM 분석 추가 (새로 추가)
                if llm_analyzer and len(processed_results) > 0:
                    logger.info(f"🤖 LLM 상황 분석 시작... ({len(processed_results)}개 이벤트)")
                    for result in processed_results:
                        interpretation = await llm_analyzer.analyze_event(result, processed_results)
                        result["interpretation"] = interpretation
                    logger.info("✅ LLM 상황 분석 완료")

                # 요약 정보 계산
                summary = {
                    "total_detections": len(processed_results),
                    "highest_severity": max([r["severity_score"] for r in processed_results], default=0),
                    "emergency_count": sum(1 for r in processed_results if r["is_emergency"])
                }

                # 결과 저장
                tasks[task_id]["status"] = "completed"
                tasks[task_id]["results"] = processed_results
                tasks[task_id]["summary"] = summary

                logger.info(f"파일 분석 완료: task_id={task_id}, detections={len(processed_results)}")

            except Exception as e:
                logger.error(f"파일 분석 실패: task_id={task_id}, error={str(e)}", exc_info=True)
                tasks[task_id]["status"] = "failed"
                tasks[task_id]["error"] = str(e)

        # 백그라운드 작업 시작
        background_tasks.add_task(process_file)

        return AnalyzeResponse(
            task_id=task_id,
            status="processing",
            file_info=FileInfo(
                filename=file.filename,
                size=len(file_bytes),
                format=file.content_type or "unknown"
            )
        )

    @router.get("/analyze/{task_id}")
    async def get_analysis_result(task_id: str):
        """
        분석 결과 조회
        """
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")

        task = tasks[task_id]

        response = {
            "task_id": task_id,
            "status": task["status"],
            "file_info": {
                "filename": task["filename"],
                "size": task["file_size"],
                "format": task["content_type"]
            }
        }

        if task["status"] == "completed" and task["results"]:
            response["results"] = task["results"]
            response["summary"] = {
                "total_detections": len(task["results"]),
                "highest_severity": max([r.get("severity_score", 0) for r in task["results"]], default=0),
                "emergency_count": sum(1 for r in task["results"] if r.get("is_emergency", False))
            }
        elif task["status"] == "failed":
            response["error"] = task.get("error")

        return response

    @router.get("/samples")
    async def list_samples():
        """
        샘플 파일 목록
        """
        import os
        import glob

        samples_dir = "samples"
        if not os.path.exists(samples_dir):
            return {"samples": []}

        sample_files = []
        for filepath in glob.glob(f"{samples_dir}/*.mp3") + glob.glob(f"{samples_dir}/*.wav"):
            filename = os.path.basename(filepath)
            file_size = os.path.getsize(filepath)
            sample_files.append({
                "id": filename.replace(".", "_"),
                "name": filename,
                "url": f"/samples/{filename}",
                "description": f"{filename} 샘플 파일",
                "size": file_size
            })

        return {"samples": sample_files}

    return router
