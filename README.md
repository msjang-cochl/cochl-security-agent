# 자율형 비즈니스 보안 에이전트

Cochl.sense API를 활용한 실시간 소리 이벤트 모니터링 및 자동 대응 시스템입니다.

## 시스템 개요

이 시스템은 다음과 같이 동작합니다:

1. **Trigger**: Cochl API로부터 실시간 소리 이벤트를 Webhook으로 수신
2. **Manager Agent**: 소리(비명, 사이렌, 유리 깨짐 등)를 분석하고 심각도를 1-10점으로 평가
3. **Decision**: 7점 이상이면 '긴급 상황'으로 판단하고 Zapier Webhook 호출, 미만이면 로그만 기록
4. **Tools**: Zapier를 통해 Slack 알림과 Jira 티켓 자동 생성

---

## 목차

1. [사전 준비](#사전-준비)
2. [설치 방법](#설치-방법)
3. [설정 방법](#설정-방법)
4. [실행 방법](#실행-방법)
5. [Webhook 연동 설정](#webhook-연동-설정)
6. [테스트 방법](#테스트-방법)
7. [문제 해결](#문제-해결)

---

## 사전 준비

### 1. Python 설치 확인

터미널(Mac) 또는 명령 프롬프트(Windows)를 열고 다음 명령어를 입력하세요:

```bash
python3 --version
```

Python 3.8 이상이 설치되어 있어야 합니다. 설치되어 있지 않다면:
- **Mac**: [Python 공식 사이트](https://www.python.org/downloads/)에서 다운로드
- **Windows**: Microsoft Store에서 "Python 3.11" 검색 후 설치

### 2. 필요한 계정 및 정보

다음 정보를 미리 준비하세요:

- ✅ **Cochl.sense API 키**: [Cochl 대시보드](https://dashboard.cochl.ai/)에서 발급
- ✅ **Zapier 계정**: [Zapier](https://zapier.com/) 가입 (무료 플랜 가능)
- ✅ **Slack Workspace** (선택): 알림을 받을 Slack 채널
- ✅ **Jira 계정** (선택): 티켓을 생성할 Jira 프로젝트

---

## 설치 방법

### 1단계: 프로젝트 폴더로 이동

터미널을 열고 프로젝트 폴더로 이동합니다:

```bash
cd /Users/minseojang/cochl-security-agent
```

### 2단계: 가상 환경 생성 (권장)

가상 환경을 만들면 프로젝트별로 라이브러리를 독립적으로 관리할 수 있습니다.

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
# Mac/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

가상 환경이 활성화되면 터미널 앞에 `(venv)`가 표시됩니다.

### 3단계: 필요한 라이브러리 설치

```bash
pip install -r requirements.txt
```

다음과 같은 메시지가 표시되면 성공입니다:
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 requests-2.31.0 ...
```

---

## 설정 방법

### 1단계: .env 파일 생성

`.env.example` 파일을 복사하여 `.env` 파일을 만듭니다:

```bash
# Mac/Linux:
cp .env.example .env

# Windows:
copy .env.example .env
```

### 2단계: .env 파일 편집

텍스트 편집기로 `.env` 파일을 열고 실제 값을 입력합니다:

```bash
# Mac:
open -e .env

# Windows:
notepad .env
```

다음 항목을 수정하세요:

```env
# Cochl API 키 (필수)
COCHL_API_KEY=your_actual_cochl_api_key_here

# Zapier Webhook URL (필수)
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/123456/abcdef/

# 서버 포트 (선택, 기본값: 8000)
SERVER_PORT=8000

# 긴급 상황 기준 점수 (선택, 기본값: 7)
EMERGENCY_THRESHOLD=7
```

**중요**: `.env` 파일은 절대 공유하거나 Git에 업로드하지 마세요!

---

## 실행 방법

### 1단계: 서버 시작

터미널에서 다음 명령어를 실행합니다:

```bash
python3 main.py
```

다음과 같은 메시지가 표시되면 성공입니다:

```
============================================================
자율형 비즈니스 보안 에이전트 시작
============================================================
✅ Cochl API 키 확인: sk_test_xxx...
✅ Zapier Webhook 확인: https://hooks.zapier.com/hooks/...
✅ 긴급 상황 기준 점수: 7/10
✅ 서버 시작: http://0.0.0.0:8000
============================================================
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 2단계: 서버 상태 확인

브라우저를 열고 다음 주소로 접속합니다:

```
http://localhost:8000
```

다음과 같은 JSON 응답이 표시되면 정상 작동 중입니다:

```json
{
  "service": "Cochl 보안 에이전트",
  "status": "running",
  "version": "1.0.0"
}
```

### 3단계: 헬스체크 확인

```
http://localhost:8000/health
```

설정이 올바르게 되어 있는지 확인할 수 있습니다.

---

## Webhook 연동 설정

### A. Cochl 대시보드 설정

1. [Cochl 대시보드](https://dashboard.cochl.ai/)에 로그인
2. **Settings** > **Webhooks** 메뉴로 이동
3. **Add Webhook** 클릭
4. Webhook URL 입력:
   ```
   http://your-server-ip:8000/webhook/cochl
   ```

   **로컬 테스트용**:
   - [ngrok](https://ngrok.com/) 사용 (무료)
   - ngrok 설치 후: `ngrok http 8000`
   - 생성된 URL 사용: `https://abc123.ngrok.io/webhook/cochl`

5. **이벤트 선택**: 모니터링할 소리 이벤트 선택 (예: scream, siren, glass_break)
6. **Save** 클릭

### B. Zapier Zap 생성

#### 1단계: Zapier에 로그인

[Zapier](https://zapier.com/)에 로그인하고 **Create Zap** 클릭

#### 2단계: Trigger 설정

- **Trigger**: "Webhooks by Zapier" 선택
- **Event**: "Catch Hook" 선택
- **Webhook URL 복사**: 생성된 URL을 `.env` 파일의 `ZAPIER_WEBHOOK_URL`에 입력

#### 3단계: Action 1 - Slack 알림 (선택)

- **Action**: "Slack" 선택
- **Event**: "Send Channel Message" 선택
- **계정 연결**: Slack 계정 연결
- **Channel**: 알림을 받을 채널 선택 (예: #security-alerts)
- **Message Text**:
  ```
  🚨 긴급 보안 알림

  심각도: {{severity_score}}/10
  소리 종류: {{sound_type}}
  신뢰도: {{confidence}}
  시각: {{timestamp}}

  메시지: {{message}}
  ```

#### 4단계: Action 2 - Jira 티켓 생성 (선택)

- **Action**: "Jira" 선택
- **Event**: "Create Issue" 선택
- **계정 연결**: Jira 계정 연결
- **Project**: 티켓을 생성할 프로젝트 선택
- **Issue Type**: "Task" 또는 "Bug" 선택
- **Summary**: `보안 이벤트 - {{sound_type}} ({{severity_score}}/10)`
- **Description**:
  ```
  심각도: {{severity_score}}/10
  소리 종류: {{sound_type}}
  신뢰도: {{confidence}}
  감지 시각: {{timestamp}}

  상세:
  {{message}}
  ```

#### 5단계: Zap 활성화

- **Test & Review** 클릭하여 테스트
- 문제가 없으면 **Publish** 클릭

---

## 테스트 방법

### 1. 수동 테스트 (cURL 사용)

터미널에서 다음 명령어를 실행하여 테스트 이벤트를 전송합니다:

#### 긴급 상황 테스트 (심각도 9점 - 알림 전송됨)

```bash
curl -X POST http://localhost:8000/webhook/cochl \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "test_001",
    "tag": "scream",
    "confidence": 0.95,
    "timestamp": "2026-01-13T10:30:00Z",
    "metadata": {}
  }'
```

예상 결과:
- Slack에 알림이 전송됩니다
- Jira에 티켓이 생성됩니다
- 로그 파일에 기록됩니다

#### 일반 상황 테스트 (심각도 2점 - 로그만 기록)

```bash
curl -X POST http://localhost:8000/webhook/cochl \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "test_002",
    "tag": "footsteps",
    "confidence": 0.80,
    "timestamp": "2026-01-13T10:35:00Z",
    "metadata": {}
  }'
```

예상 결과:
- 로그 파일에만 기록됩니다 (알림 없음)

### 2. 로그 확인

실시간 로그 확인:

```bash
# Mac/Linux:
tail -f security_agent.log

# Windows:
type security_agent.log
```

---

## 문제 해결

### 문제 1: "ModuleNotFoundError"

**증상**: `ModuleNotFoundError: No module named 'fastapi'`

**해결**:
```bash
# 가상 환경이 활성화되어 있는지 확인
# 터미널 앞에 (venv)가 있어야 함

# 라이브러리 재설치
pip install -r requirements.txt
```

### 문제 2: "Address already in use"

**증상**: `[Errno 48] Address already in use`

**해결**:
```bash
# 포트 8000을 사용 중인 프로세스 찾기
# Mac/Linux:
lsof -i :8000

# 프로세스 종료
kill -9 [PID]

# 또는 .env 파일에서 다른 포트 사용
SERVER_PORT=8001
```

### 문제 3: Zapier로 알림이 전송되지 않음

**확인 사항**:
1. `.env` 파일의 `ZAPIER_WEBHOOK_URL`이 올바른지 확인
2. Zapier Zap이 "On" 상태인지 확인
3. 로그 파일에서 에러 메시지 확인:
   ```bash
   grep "ERROR" security_agent.log
   ```

### 문제 4: Cochl Webhook이 수신되지 않음

**확인 사항**:
1. 서버가 외부에서 접근 가능한지 확인 (방화벽 설정)
2. ngrok 사용 시: ngrok이 실행 중인지 확인
3. Cochl 대시보드에서 Webhook URL이 올바른지 확인

---

## 심각도 점수 커스터마이징

비즈니스 환경에 맞게 소리별 점수를 조정하려면 [main.py](main.py) 파일의 `SOUND_SEVERITY_MAP`을 수정하세요:

```python
# main.py 파일의 86-105줄
SOUND_SEVERITY_MAP = {
    # 긴급 상황 (8-10점)
    "scream": 9,           # 비명 → 9점으로 유지
    "glass_break": 8,      # 유리 깨짐 → 8점으로 유지

    # 경고 상황 (5-7점)
    "siren": 7,            # 사이렌 → 7점으로 유지
    "dog_bark": 5,         # 개 짖음 → 3점으로 낮춤 (예시)

    # 새로운 소리 추가
    "door_kick": 9,        # 문 발로 차는 소리 추가
}
```

수정 후 서버를 재시작하세요:
```bash
# Ctrl+C로 서버 종료 후
python3 main.py
```

---

## 서버를 백그라운드에서 실행하기

### Mac/Linux

```bash
# nohup 사용
nohup python3 main.py > output.log 2>&1 &

# 프로세스 확인
ps aux | grep main.py

# 종료
kill [PID]
```

### 영구적으로 실행 (systemd - Linux)

`/etc/systemd/system/cochl-agent.service` 파일 생성:

```ini
[Unit]
Description=Cochl Security Agent
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/Users/minseojang/cochl-security-agent
Environment="PATH=/Users/minseojang/cochl-security-agent/venv/bin"
ExecStart=/Users/minseojang/cochl-security-agent/venv/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

실행:
```bash
sudo systemctl start cochl-agent
sudo systemctl enable cochl-agent  # 부팅 시 자동 시작
sudo systemctl status cochl-agent  # 상태 확인
```

---

## API 문서

서버가 실행 중일 때, 브라우저에서 다음 주소로 접속하면 자동 생성된 API 문서를 볼 수 있습니다:

```
http://localhost:8000/docs
```

Swagger UI로 모든 엔드포인트를 테스트할 수 있습니다.

---

## 보안 권장 사항

1. **환경 변수 보호**: `.env` 파일을 절대 공유하지 마세요
2. **HTTPS 사용**: 프로덕션에서는 HTTPS를 사용하세요 (Let's Encrypt 무료)
3. **인증 추가**: Webhook에 인증 토큰을 추가하세요
4. **방화벽 설정**: 불필요한 포트는 닫으세요
5. **로그 로테이션**: 로그 파일이 너무 커지지 않도록 관리하세요

---

## 지원 및 문의

문제가 발생하면:
1. [security_agent.log](security_agent.log) 파일을 확인하세요
2. GitHub Issues에 질문을 올려주세요
3. [Cochl 문서](https://docs.cochl.ai/)를 참고하세요

---

## 라이선스

MIT License

---

## 변경 이력

- **v1.0.0** (2026-01-13): 초기 릴리스
  - Cochl Webhook 수신
  - Manager Agent 심각도 분석
  - Zapier 통합 (Slack, Jira)
