# 빠른 시작 가이드

## 다른 컴퓨터에서 시작하기

### 1. 저장소 클론

```bash
git clone https://github.com/meanmin/cochl-security-agent.git
cd cochl-security-agent
```

### 2. 가상 환경 설정

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (실제 API 키 입력)
# Mac:
open -e .env
# Linux:
nano .env
# Windows:
notepad .env
```

`.env` 파일에서 다음 항목 수정:
```env
COCHL_API_KEY=your_actual_api_key
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/your/webhook/
```

### 5. 서버 실행

```bash
python3 main.py
```

### 6. 테스트

```bash
# 새 터미널에서
python3 test_events.py
```

---

## 변경 사항 Git에 올리기

코드를 수정한 후:

```bash
# 변경 사항 확인
git status

# 모든 변경 사항 추가
git add .

# 커밋
git commit -m "변경 내용 설명"

# GitHub에 푸시
git push
```

**첫 푸시 시 인증 필요**:
- Username: `meanmin`
- Password: Personal Access Token 입력

---

## 다른 컴퓨터에서 최신 버전 받기

```bash
cd cochl-security-agent
git pull
```

라이브러리가 업데이트된 경우:
```bash
pip install -r requirements.txt
```

---

## 유용한 명령어

### 서버 관련
```bash
# 백그라운드 실행
nohup python3 main.py > output.log 2>&1 &

# 실행 중인 프로세스 확인
ps aux | grep main.py

# 로그 실시간 확인
tail -f security_agent.log

# 서버 종료
pkill -f main.py
```

### Git 관련
```bash
# 현재 브랜치 확인
git branch

# 커밋 히스토리 보기
git log --oneline

# 특정 파일의 변경 사항 취소
git checkout -- filename

# 최근 커밋 취소 (변경사항은 유지)
git reset --soft HEAD~1
```

---

## 문제 해결

### Git 인증 실패

```bash
# Credential helper 설정
git config credential.helper store

# 또는 SSH 키 사용
ssh-keygen -t ed25519 -C "mineislucky@gmail.com"
cat ~/.ssh/id_ed25519.pub
# 출력된 키를 GitHub → Settings → SSH Keys에 등록
git remote set-url origin git@github.com:meanmin/cochl-security-agent.git
```

### 가상 환경 활성화 안 됨

터미널 프롬프트에 `(venv)`가 표시되어야 합니다.
표시되지 않으면:
```bash
source venv/bin/activate  # Mac/Linux
```

### 포트 사용 중 에러

```bash
# 포트 8000 사용 프로세스 찾기
lsof -i :8000

# 프로세스 종료
kill -9 [PID]
```

---

## 프로젝트 구조

```
cochl-security-agent/
├── main.py              # 메인 애플리케이션
├── test_events.py       # 테스트 스크립트
├── requirements.txt     # Python 패키지 목록
├── .env.example         # 환경 변수 템플릿
├── .env                 # 환경 변수 (Git 제외)
├── .gitignore          # Git 제외 파일 목록
├── README.md           # 상세 가이드
├── QUICK_START.md      # 빠른 시작 가이드
└── GITHUB_SETUP.md     # GitHub 설정 가이드
```

---

## GitHub 저장소

🔗 **저장소 URL**: https://github.com/meanmin/cochl-security-agent

브라우저에서 저장소를 확인하고, 다른 사람과 공유할 수 있습니다.

---

## 다음 단계

1. **Cochl API 연동**: 실제 Cochl API 키로 `.env` 파일 업데이트
2. **Zapier 설정**: README.md의 Zapier 섹션 참고
3. **서버 배포**: 실제 서버에 배포하거나 ngrok 사용
4. **커스터마이징**: `main.py`의 `SOUND_SEVERITY_MAP`에서 점수 조정

---

도움이 필요하면 README.md를 참고하거나 GitHub Issues를 활용하세요!
