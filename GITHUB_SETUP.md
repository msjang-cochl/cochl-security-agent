# GitHub에 프로젝트 올리기 가이드

## 방법 1: GitHub 웹사이트에서 저장소 생성 (추천)

### 1단계: GitHub에 새 저장소 만들기

1. [GitHub](https://github.com)에 로그인
2. 오른쪽 상단 `+` 버튼 클릭 → `New repository` 선택
3. 저장소 정보 입력:
   - **Repository name**: `cochl-security-agent`
   - **Description**: `Cochl.sense API를 활용한 자율형 비즈니스 보안 에이전트`
   - **Public/Private**: 원하는 대로 선택
   - ⚠️ **중요**: "Add a README file", "Add .gitignore", "Choose a license" 옵션을 **모두 체크 해제**
4. `Create repository` 버튼 클릭

### 2단계: 원격 저장소 연결 및 푸시

GitHub에서 저장소를 만들면 안내 페이지가 나타납니다.
다음 명령어를 터미널에서 실행하세요:

```bash
# 1. 프로젝트 폴더로 이동
cd /Users/minseojang/cochl-security-agent

# 2. GitHub 저장소 연결 (저장소 URL을 실제 URL로 변경)
git remote add origin https://github.com/minseojang/cochl-security-agent.git

# 3. 기본 브랜치를 main으로 설정 (이미 되어 있음)
git branch -M main

# 4. GitHub에 푸시
git push -u origin main
```

**참고**: GitHub 인증이 필요할 수 있습니다.
- Personal Access Token을 사용하거나
- GitHub CLI (`gh`)를 사용하거나
- SSH 키를 설정하면 됩니다

---

## 방법 2: GitHub CLI 사용 (더 쉬움)

GitHub CLI가 설치되어 있다면 한 번에 가능합니다:

```bash
# 1. GitHub CLI 설치 확인
gh --version

# 만약 설치되지 않았다면:
# brew install gh  (Mac)

# 2. GitHub 로그인
gh auth login

# 3. 저장소 생성 및 푸시
gh repo create cochl-security-agent --public --source=. --remote=origin --push
```

---

## 인증 방법

### A. Personal Access Token 사용

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. `Generate new token (classic)` 클릭
3. 권한 선택:
   - ✅ `repo` (모든 하위 항목)
4. 토큰 생성 후 복사 (⚠️ 다시 볼 수 없으니 안전한 곳에 저장!)
5. Git 푸시할 때 비밀번호 대신 토큰 입력

### B. SSH 키 사용

```bash
# 1. SSH 키 생성
ssh-keygen -t ed25519 -C "mineislucky@gmail.com"

# 2. SSH 키 복사
cat ~/.ssh/id_ed25519.pub

# 3. GitHub → Settings → SSH and GPG keys → New SSH key
# 복사한 키를 붙여넣기

# 4. 저장소 URL을 SSH로 변경
git remote set-url origin git@github.com:minseojang/cochl-security-agent.git
```

---

## 다른 컴퓨터에서 작업하기

GitHub에 올린 후, 다른 컴퓨터에서는:

```bash
# 1. 저장소 클론
git clone https://github.com/minseojang/cochl-security-agent.git
cd cochl-security-agent

# 2. 가상 환경 생성
python3 -m venv venv

# 3. 가상 환경 활성화
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. 라이브러리 설치
pip install -r requirements.txt

# 5. 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 실제 API 키 입력

# 6. 서버 실행
python3 main.py
```

---

## 변경 사항 푸시하기

파일을 수정한 후 GitHub에 올리는 방법:

```bash
# 1. 변경된 파일 확인
git status

# 2. 변경 사항 스테이징
git add .

# 3. 커밋
git commit -m "변경 사항 설명"

# 4. GitHub에 푸시
git push
```

---

## 다른 컴퓨터에서 최신 버전 가져오기

```bash
# 1. 프로젝트 폴더로 이동
cd cochl-security-agent

# 2. 최신 변경 사항 가져오기
git pull
```

---

## 문제 해결

### "remote origin already exists" 에러

```bash
# 기존 원격 저장소 확인
git remote -v

# 잘못된 경우 삭제 후 다시 추가
git remote remove origin
git remote add origin https://github.com/minseojang/cochl-security-agent.git
```

### 인증 실패

```bash
# GitHub CLI 사용 (가장 쉬움)
gh auth login

# 또는 SSH 키 설정 (위 참고)
```

### 푸시 거부 (rejected)

```bash
# 강제 푸시 (주의: 원격의 변경 사항이 덮어씌워짐)
git push -f origin main
```

---

## 현재 상태

✅ Git 저장소 초기화 완료
✅ 첫 커밋 완료 (6개 파일, 1398줄)
✅ 브랜치: main
⏳ GitHub 원격 저장소 연결 대기 중

다음 단계: 위의 방법 1 또는 방법 2를 따라 GitHub에 푸시하세요!
