# Cochl 보안 에이전트 - 웹 데모 빠른 시작 가이드

## 구현 완료 기능 ✅

1. **백엔드 API**
   - 파일 업로드 엔드포인트 (`POST /api/v1/analyze`)
   - 분석 결과 조회 (`GET /api/v1/analyze/{task_id}`)
   - Mock Cochl API 클라이언트 (실제 API 키 불필요)
   - 심각도 자동 계산 및 긴급 이벤트 판단

2. **웹 인터페이스**
   - 간단한 HTML 데모 페이지
   - 드래그 앤 드롭 파일 업로드
   - 실시간 분석 상태 표시
   - 탐지 결과 시각화 (심각도, 신뢰도, 시간대)

## 설치 및 실행

### 1. 의존성 설치

```bash
# 새로운 의존성 설치
pip install -r requirements.txt
```

새로 추가된 패키지:
- `python-multipart` - 파일 업로드 지원
- `httpx` - 비동기 HTTP 클라이언트
- `aiofiles` - 비동기 파일 처리

### 2. 백엔드 서버 실행

```bash
# 백엔드 디렉토리에서 실행
cd backend
python main.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

확인:
- API 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/health

### 3. 웹 데모 열기

브라우저에서 `frontend/demo.html` 파일을 열면 됩니다:

```bash
# 방법 1: 직접 파일 열기
open frontend/demo.html

# 방법 2: 간단한 HTTP 서버 실행 (선택사항)
cd frontend
python -m http.server 8080
# 그 다음 브라우저에서 http://localhost:8080/demo.html 접속
```

## 사용 방법

### 웹 데모 사용

1. **파일 업로드**
   - 드래그 앤 드롭 또는 클릭하여 파일 선택
   - 지원 형식: MP3, WAV, OGG, MP4, WebM
   - 최대 크기: 50MB

2. **분석 진행**
   - 업로드 후 자동으로 분석 시작
   - 2초마다 결과 확인 (최대 60초)
   - 진행 상황 표시

3. **결과 확인**
   - 요약: 총 탐지 수, 최고 심각도, 긴급 이벤트 수
   - 개별 이벤트: 소리 종류, 신뢰도, 시간대, 심각도
   - 긴급 이벤트는 빨간색으로 강조 표시

### API 직접 호출 (cURL 예시)

```bash
# 1. 파일 업로드
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "file=@your_audio_file.mp3"

# 응답 예시:
# {
#   "task_id": "550e8400-e29b-41d4-a716-446655440000",
#   "status": "processing",
#   "file_info": {...}
# }

# 2. 결과 조회
curl "http://localhost:8000/api/v1/analyze/550e8400-e29b-41d4-a716-446655440000"

# 응답 예시:
# {
#   "task_id": "...",
#   "status": "completed",
#   "results": [
#     {
#       "tag": "scream",
#       "confidence": 0.95,
#       "severity_score": 9,
#       "is_emergency": true,
#       ...
#     }
#   ]
# }
```

## Mock 클라이언트 동작 방식

현재는 실제 Cochl API 대신 **Mock 클라이언트**를 사용합니다:

- 파일명에 키워드가 있으면 해당 사운드를 "탐지"합니다
- 예시:
  - `scream.mp3` → scream 탐지 (심각도 9)
  - `glass_break.wav` → glass_break 탐지 (심각도 8)
  - `siren.mp3` → siren 탐지 (심각도 7)
  - `gunshot.mp3` → gunshot 탐지 (심각도 10)
  - 기타 파일 → conversation 탐지 (심각도 1)

### 실제 Cochl API 사용하기

`backend/main.py`에서 다음과 같이 변경하세요:

```python
# 기존 (Mock 클라이언트)
from backend.services.cochl_api import MockCochlAPIClient
cochl_client = MockCochlAPIClient()

# 변경 (실제 API 클라이언트)
from backend.services.cochl_api import CochlAPIClient
cochl_client = CochlAPIClient(
    api_key=COCHL_API_KEY,
    api_url=os.getenv("COCHL_API_URL", "https://api.cochl.ai/v1")
)
```

**주의**: 실제 Cochl API를 사용하려면 Cochl API 문서를 참고하여 `backend/services/cochl_api.py`의 `CochlAPIClient.analyze_file()` 메서드를 실제 API 스키마에 맞게 수정해야 합니다.

## API 엔드포인트

### POST /api/v1/analyze
파일 업로드 및 분석 시작

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (파일)

**Response:**
```json
{
  "task_id": "uuid",
  "status": "processing",
  "file_info": {
    "filename": "audio.mp3",
    "size": 1024000,
    "format": "audio/mpeg"
  }
}
```

### GET /api/v1/analyze/{task_id}
분석 결과 조회

**Response:**
```json
{
  "task_id": "uuid",
  "status": "completed",
  "file_info": {...},
  "results": [
    {
      "event_id": "evt_123",
      "tag": "scream",
      "confidence": 0.95,
      "start_time": 2.5,
      "end_time": 3.8,
      "severity_score": 9,
      "message": "🚨 [긴급] 보안 이벤트 감지\n...",
      "is_emergency": true
    }
  ],
  "summary": {
    "total_detections": 3,
    "highest_severity": 9,
    "emergency_count": 1
  }
}
```

### GET /api/v1/samples
샘플 파일 목록 (아직 샘플 파일 없음)

## 테스트 파일 만들기

테스트를 위해 간단한 오디오 파일을 만들 수 있습니다:

```bash
# macOS에서 간단한 음성 파일 생성
say "This is a scream test" -o samples/scream_test.m4a

# 또는 온라인에서 무료 사운드 다운로드
# https://freesound.org/
# https://www.zapsplat.com/
```

파일명에 `scream`, `glass`, `siren`, `gunshot` 등의 키워드를 포함하면 Mock 클라이언트가 해당 사운드를 탐지합니다.

## 문제 해결

### 1. 파일 업로드 실패 (413 에러)
- 파일 크기가 50MB를 초과하는지 확인하세요
- 지원하는 형식인지 확인하세요

### 2. CORS 에러
- 백엔드가 `http://localhost:8000`에서 실행 중인지 확인
- `.env` 파일의 `CORS_ORIGINS` 설정 확인

### 3. 분석 결과가 나오지 않음
- 브라우저 개발자 도구 (F12) → Console 탭에서 에러 확인
- 백엔드 로그 (`security_agent.log`) 확인

### 4. 백엔드가 시작되지 않음
```bash
# 의존성 재설치
pip install -r requirements.txt

# Python 경로 문제 해결
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python backend/main.py
```

## 다음 단계

### 님이 작업할 부분 📝

1. **샘플 파일 추가** (`samples/` 디렉토리)
   - scream.mp3
   - glass_break.mp3
   - siren.mp3
   - gunshot.mp3
   - conversation.mp3

2. **디바이스 연동 문서 작성** (`docs/device-integration/`)
   - CCTV_INTEGRATION.md
   - SMART_SPEAKER_INTEGRATION.md
   - MOBILE_INTEGRATION.md

### 추가 개선 사항 (선택사항)

1. **React 프론트엔드**
   - [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) 참조
   - 더 세련된 UI/UX
   - AudioVisualizer (파형 표시)

2. **실제 Cochl API 연동**
   - `backend/services/cochl_api.py` 수정
   - 실제 API 스키마에 맞게 조정

3. **데이터베이스 추가**
   - 작업 결과 영구 저장
   - 분석 히스토리

4. **인증 추가**
   - API 키 기반 인증
   - 사용자 계정

## 프로젝트 구조

```
cochl-security-agent/
├── backend/
│   ├── main.py                      # ✅ 메인 애플리케이션
│   ├── models/
│   │   └── sound_event.py           # ✅ 데이터 모델
│   ├── services/
│   │   ├── manager_agent.py         # ✅ 심각도 분석
│   │   ├── zapier_integration.py    # ✅ Zapier 연동
│   │   └── cochl_api.py             # ✅ Cochl API 클라이언트
│   └── routers/
│       ├── webhook.py               # ✅ 웹훅 라우터
│       ├── health.py                # ✅ 헬스체크
│       └── file_upload.py           # ✅ 파일 업로드 (신규)
├── frontend/
│   └── demo.html                    # ✅ 데모 웹페이지 (신규)
├── docs/                            # 📝 님이 작업할 부분
│   └── device-integration/
├── samples/                         # 📝 님이 작업할 부분
├── requirements.txt                 # ✅ 업데이트됨
├── .env.example                     # ✅ 업데이트됨
└── IMPLEMENTATION_GUIDE.md          # ✅ 전체 구현 가이드
```

## 참고 자료

- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Cochl API 문서](https://docs.cochl.ai/)
- [전체 구현 가이드](IMPLEMENTATION_GUIDE.md)
- [계획 문서](/Users/minseojang/.claude/plans/toasty-purring-allen.md)
