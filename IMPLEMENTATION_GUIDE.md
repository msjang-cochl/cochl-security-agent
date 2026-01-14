# Cochl Security Agent - 웹 데모 및 디바이스 연동 구현 가이드

## 현재 구현 상태

### ✅ 완료된 작업

1. **백엔드 리팩토링** - 모듈화된 구조로 재구성
   - `backend/models/` - 데이터 모델 (SoundEvent, EmergencyAlert)
   - `backend/services/` - 비즈니스 로직 (ManagerAgent, ZapierIntegration, CochlAPIClient)
   - `backend/routers/` - API 라우터 (webhook, health)
   - `backend/main.py` - 메인 애플리케이션 (CORS 설정 포함)

2. **Cochl Cloud API 클라이언트** - 기본 구조 구현
   - 실제 API와 Mock 버전 모두 제공
   - 파일 업로드 및 분석 지원

3. **디렉토리 구조** - Monorepo 구조 생성
   ```
   cochl-security-agent/
   ├── backend/          # FastAPI 백엔드
   ├── frontend/         # React 프론트엔드 (빈 폴더)
   ├── docs/            # 문서 (빈 폴더)
   └── samples/         # 샘플 파일 (빈 폴더)
   ```

### 🚧 다음 단계 (구현 필요)

다음은 계획에 따라 구현해야 할 주요 작업들입니다. 각 섹션에 구현 가이드를 제공합니다.

---

## Phase 1 (남은 작업): 파일 업로드 엔드포인트

### 1.1 파일 업로드 라우터 만들기

`backend/routers/file_upload.py` 파일을 생성하고 다음 코드를 추가하세요:

```python
"""
파일 업로드 및 분석 라우터
"""
import uuid
import logging
from typing import Dict
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.services.cochl_api import Mock

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["analysis"]
)

# 작업 상태 저장 (프로덕션에서는 Redis 사용 권장)
tasks: Dict[str, dict] = {}


class AnalyzeResponse(BaseModel):
    """파일 분석 응답 모델"""
    task_id: str
    status: str
    file_info: dict


def setup_file_upload_router(cochl_client):
    """파일 업로드 라우터 설정"""

    @router.post("/analyze", response_model=AnalyzeResponse)
    async def analyze_file(
        file: UploadFile = File(...),
        background_tasks: BackgroundTasks = None
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
            "results": None,
            "error": None
        }

        logger.info(f"파일 분석 시작: task_id={task_id}, filename={file.filename}")

        # 백그라운드에서 파일 분석 실행
        async def process_file():
            try:
                # Cochl API로 파일 분석
                results = await cochl_client.analyze_file(file_bytes, file.filename)

                # 결과 저장
                tasks[task_id]["status"] = "completed"
                tasks[task_id]["results"] = [
                    {
                        "event_id": r.event_id,
                        "tag": r.tag,
                        "confidence": r.confidence,
                        "start_time": r.start_time,
                        "end_time": r.end_time
                    }
                    for r in results
                ]

                logger.info(f"파일 분석 완료: task_id={task_id}")

            except Exception as e:
                logger.error(f"파일 분석 실패: task_id={task_id}, error={str(e)}")
                tasks[task_id]["status"] = "failed"
                tasks[task_id]["error"] = str(e)

        # 백그라운드 작업 시작
        background_tasks.add_task(process_file)

        return AnalyzeResponse(
            task_id=task_id,
            status="processing",
            file_info={
                "filename": file.filename,
                "size": len(file_bytes),
                "format": file.content_type
            }
        )

    @router.get("/analyze/{task_id}")
    async def get_analysis_result(task_id: str):
        """
        분석 결과 조회
        """
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")

        task = tasks[task_id]

        return {
            "task_id": task_id,
            "status": task["status"],
            "file_info": {
                "filename": task["filename"],
                "size": task["file_size"]
            },
            "results": task.get("results"),
            "error": task.get("error"),
            "summary": {
                "total_detections": len(task["results"]) if task["results"] else 0,
                "highest_severity": max([r.get("severity", 0) for r in (task["results"] or [])], default=0)
            } if task["results"] else None
        }

    @router.get("/samples")
    async def list_samples():
        """
        샘플 파일 목록
        """
        # samples/ 디렉토리에서 파일 목록 읽기
        import os
        import glob

        samples_dir = "samples"
        if not os.path.exists(samples_dir):
            return {"samples": []}

        sample_files = []
        for filepath in glob.glob(f"{samples_dir}/*.mp3") + glob.glob(f"{samples_dir}/*.wav"):
            filename = os.path.basename(filepath)
            sample_files.append({
                "id": filename.replace(".", "_"),
                "name": filename,
                "url": f"/samples/{filename}",
                "description": f"{filename} 샘플 파일"
            })

        return {"samples": sample_files}

    return router
```

### 1.2 백엔드 main.py 업데이트

`backend/main.py`에서 파일 업로드 라우터를 등록하세요:

```python
# ... 기존 import 문들 ...
from backend.routers import webhook, health, file_upload
from backend.services.cochl_api import MockCochlAPIClient

# ... 기존 코드 ...

# Cochl API 클라이언트 초기화 (Mock 버전 사용)
cochl_client = MockCochlAPIClient()

# ... 기존 라우터 설정 ...

# 파일 업로드 라우터 추가
file_upload_router = file_upload.setup_file_upload_router(cochl_client)
app.include_router(file_upload_router)
```

### 1.3 requirements.txt 업데이트

파일 업로드를 위한 의존성을 추가하세요:

```txt
# 기존 의존성
fastapi==0.109.0
uvicorn[standard]==0.27.0
requests==2.31.0
python-dotenv==1.0.0
pydantic==2.5.3
python-dateutil==2.8.2

# 새로운 의존성
python-multipart==0.0.6  # 파일 업로드 지원
httpx==0.26.0           # 비동기 HTTP 클라이언트
aiofiles==23.2.1        # 비동기 파일 처리
```

### 1.4 .env.example 업데이트

새로운 환경 변수를 추가하세요:

```env
# 기존 설정
COCHL_API_KEY=XsiwIgLDFTwYmUfUhrNcyT3n7GwlOBcEa/ft1sUryQI=
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/25940870/ugsb3ib/
SERVER_PORT=8000
EMERGENCY_THRESHOLD=7
SERVER_HOST=0.0.0.0

# 새로운 설정
COCHL_API_URL=https://api.cochl.ai/v1
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
MAX_FILE_SIZE_MB=50
ALLOWED_AUDIO_FORMATS=mp3,wav,ogg,m4a
ALLOWED_VIDEO_FORMATS=mp4,webm,avi
TASK_EXPIRY_SECONDS=3600
```

---

## Phase 2: 프론트엔드 기반 구축

### 2.1 Vite + React + TypeScript 프로젝트 초기화

```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# Vite로 React + TypeScript 프로젝트 생성
npm create vite@latest . -- --template react-ts

# 의존성 설치
npm install

# 추가 라이브러리 설치
npm install react-router-dom axios @tanstack/react-query
npm install wavesurfer.js react-dropzone clsx date-fns

# 개발 의존성 설치 (TailwindCSS)
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 2.2 TailwindCSS 설정

`tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

`src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 2.3 기본 구조 생성

디렉토리 구조:

```
frontend/src/
├── components/
│   ├── FileUpload/
│   │   └── FileUpload.tsx
│   ├── AudioVisualizer/
│   │   └── AudioVisualizer.tsx
│   ├── ResultsPanel/
│   │   └── ResultsPanel.tsx
│   └── Layout/
│       ├── Header.tsx
│       └── Footer.tsx
├── pages/
│   ├── Demo.tsx
│   └── Documentation.tsx
├── hooks/
│   ├── useFileUpload.ts
│   └── useDetectionResults.ts
├── services/
│   └── api.ts
├── types/
│   └── detection.ts
├── App.tsx
└── main.tsx
```

### 2.4 API 서비스 레이어 (`services/api.ts`)

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/v1/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getAnalysisResult = async (taskId: string) => {
  const response = await api.get(`/api/v1/analyze/${taskId}`);
  return response.data;
};

export const getSamples = async () => {
  const response = await api.get('/api/v1/samples');
  return response.data;
};
```

---

## Phase 3-5: UI 컴포넌트 구현

이 단계들은 React 컴포넌트를 만드는 작업으로, 시간이 많이 소요됩니다. 각 컴포넌트의 기본 구조를 제공합니다.

### FileUpload.tsx 예시

```typescript
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.ogg', '.m4a'],
      'video/*': ['.mp4', '.webm', '.avi']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: false
  });

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
        transition-colors duration-200
        ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
      `}
    >
      <input {...getInputProps()} />
      <div className="space-y-2">
        <p className="text-xl font-medium text-gray-700">
          {isDragActive ? '파일을 여기에 드롭하세요' : '오디오/비디오 파일을 드래그하거나 클릭하세요'}
        </p>
        <p className="text-sm text-gray-500">
          지원 형식: MP3, WAV, OGG, MP4, WebM
        </p>
        <p className="text-sm text-gray-500">
          최대 크기: 50MB
        </p>
      </div>
    </div>
  );
};
```

---

## Phase 6: 디바이스 연동 문서

디바이스 연동 가이드는 `docs/device-integration/` 디렉토리에 3개의 마크다운 파일로 작성합니다:

1. **CCTV_INTEGRATION.md** - CCTV 카메라 연동 가이드
2. **SMART_SPEAKER_INTEGRATION.md** - 스마트 스피커 연동 가이드
3. **MOBILE_INTEGRATION.md** - 모바일 앱 연동 가이드

각 가이드에는 다음 내용이 포함되어야 합니다:
- 아키텍처 다이어그램
- 단계별 설정 가이드
- 샘플 코드 (Python, Swift, Kotlin 등)
- 브랜드별 설정 차이점
- 트러블슈팅 가이드

---

## Phase 7: 샘플 파일 준비

### 7.1 샘플 오디오 파일 획득

로열티 프리 사운드를 다음 사이트에서 다운로드하세요:

- [Freesound](https://freesound.org/)
- [Zapsplat](https://www.zapsplat.com/)
- [BBC Sound Effects](https://sound-effects.bbcrewind.co.uk/)

필요한 샘플:
- `scream.mp3` - 비명 소리 (5-10초)
- `glass_break.mp3` - 유리 깨지는 소리 (3-5초)
- `siren.mp3` - 사이렌 소리 (5-10초)
- `gunshot.mp3` - 총성 (1-3초)
- `conversation.mp3` - 일반 대화 (10-20초)

### 7.2 metadata.json 생성

```json
{
  "samples": [
    {
      "id": "scream",
      "filename": "scream.mp3",
      "name": "Scream Sound",
      "description": "Emergency scream detection test",
      "expected_tag": "scream",
      "expected_severity": 9,
      "duration": 5.2
    },
    {
      "id": "glass_break",
      "filename": "glass_break.mp3",
      "name": "Glass Breaking",
      "description": "Glass break detection test",
      "expected_tag": "glass_break",
      "expected_severity": 8,
      "duration": 3.8
    }
  ]
}
```

---

## Phase 8: 테스팅 및 배포

### 8.1 로컬 테스트

```bash
# 백엔드 시작
cd backend
python main.py

# 프론트엔드 시작 (새 터미널)
cd frontend
npm run dev
```

브라우저에서 `http://localhost:5173` 접속하여 테스트

### 8.2 Docker 배포 (선택사항)

`docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - COCHL_API_KEY=${COCHL_API_KEY}
      - ZAPIER_WEBHOOK_URL=${ZAPIER_WEBHOOK_URL}
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

---

## 우선순위 작업 순서

전체 구현은 시간이 많이 소요되므로, 다음 순서로 우선 작업하세요:

1. ✅ **백엔드 리팩토링** (완료)
2. ✅ **Cochl API 클라이언트** (완료)
3. **파일 업로드 엔드포인트** (가이드 제공됨)
4. **프론트엔드 기본 설정** (가이드 제공됨)
5. **FileUpload 컴포넌트** (예시 코드 제공됨)
6. **디바이스 연동 문서** (구조 제공됨)
7. AudioVisualizer, ResultsPanel (선택사항)
8. E2E 테스팅 (선택사항)

## 참고 자료

- [Cochl API 문서](https://docs.cochl.ai/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [React 문서](https://react.dev/)
- [WaveSurfer.js 문서](https://wavesurfer.xyz/)
- [TailwindCSS 문서](https://tailwindcss.com/)

---

**중요**: 이 구현은 8주 분량의 작업이므로, 핵심 기능(파일 업로드, 탐지 결과 표시)에 집중하고 나머지는 점진적으로 추가하는 것을 권장합니다.
