#!/usr/bin/env python3
"""
보안 에이전트 테스트 스크립트
다양한 소리 이벤트를 시뮬레이션하여 시스템 동작을 확인합니다
"""

import requests
import json
import time
from datetime import datetime

# 서버 URL
SERVER_URL = "http://localhost:8000"

# 색상 코드 (터미널 출력용)
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_header(text):
    """헤더 출력"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    """성공 메시지 출력"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_warning(text):
    """경고 메시지 출력"""
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_error(text):
    """에러 메시지 출력"""
    print(f"{RED}❌ {text}{RESET}")

def print_info(text):
    """정보 메시지 출력"""
    print(f"{BLUE}ℹ️  {text}{RESET}")

def send_sound_event(event_data):
    """
    소리 이벤트를 서버로 전송

    Args:
        event_data: 이벤트 데이터 딕셔너리

    Returns:
        응답 데이터
    """
    try:
        response = requests.post(
            f"{SERVER_URL}/webhook/cochl",
            json=event_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def test_emergency_event():
    """긴급 상황 테스트 (비명 소리)"""
    print_header("테스트 1: 긴급 상황 (비명 소리 - 심각도 9점)")

    event = {
        "event_id": "test_emergency_001",
        "tag": "scream",
        "confidence": 0.95,
        "timestamp": datetime.now().isoformat(),
        "metadata": {"location": "Building A, Floor 3"}
    }

    print_info(f"전송 데이터: {json.dumps(event, indent=2, ensure_ascii=False)}")
    print_info("요청 전송 중...")

    result = send_sound_event(event)

    if result["success"]:
        data = result["data"]
        print_success(f"응답 코드: {result['status_code']}")
        print_success(f"처리 상태: {data.get('status')}")
        print_success(f"심각도 점수: {data.get('severity_score')}/10")
        print_success(f"메시지: {data.get('message')}")

        if data.get('severity_score', 0) >= 7:
            print_warning("🚨 긴급 알림이 Zapier로 전송되었습니다! (테스트 URL)")

        return True
    else:
        print_error(f"요청 실패: {result['error']}")
        return False

def test_warning_event():
    """경고 상황 테스트 (사이렌 소리)"""
    print_header("테스트 2: 경고 상황 (사이렌 소리 - 심각도 7점)")

    event = {
        "event_id": "test_warning_001",
        "tag": "siren",
        "confidence": 0.85,
        "timestamp": datetime.now().isoformat(),
        "metadata": {"location": "Parking Lot"}
    }

    print_info(f"전송 데이터: {json.dumps(event, indent=2, ensure_ascii=False)}")
    print_info("요청 전송 중...")

    result = send_sound_event(event)

    if result["success"]:
        data = result["data"]
        print_success(f"응답 코드: {result['status_code']}")
        print_success(f"처리 상태: {data.get('status')}")
        print_success(f"심각도 점수: {data.get('severity_score')}/10")
        print_success(f"메시지: {data.get('message')}")

        # 7점이므로 긴급 알림 발송됨
        if data.get('severity_score', 0) >= 7:
            print_warning("🚨 긴급 알림이 Zapier로 전송되었습니다!")

        return True
    else:
        print_error(f"요청 실패: {result['error']}")
        return False

def test_normal_event():
    """일반 상황 테스트 (발소리)"""
    print_header("테스트 3: 일반 상황 (발소리 - 심각도 2점)")

    event = {
        "event_id": "test_normal_001",
        "tag": "footsteps",
        "confidence": 0.80,
        "timestamp": datetime.now().isoformat(),
        "metadata": {"location": "Hallway"}
    }

    print_info(f"전송 데이터: {json.dumps(event, indent=2, ensure_ascii=False)}")
    print_info("요청 전송 중...")

    result = send_sound_event(event)

    if result["success"]:
        data = result["data"]
        print_success(f"응답 코드: {result['status_code']}")
        print_success(f"처리 상태: {data.get('status')}")
        print_success(f"심각도 점수: {data.get('severity_score')}/10")
        print_success(f"메시지: {data.get('message')}")

        if data.get('severity_score', 0) < 7:
            print_info("ℹ️  심각도가 낮아 로그만 기록되었습니다 (알림 없음)")

        return True
    else:
        print_error(f"요청 실패: {result['error']}")
        return False

def test_glass_break_event():
    """긴급 상황 테스트 (유리 깨지는 소리)"""
    print_header("테스트 4: 긴급 상황 (유리 깨짐 - 심각도 8점)")

    event = {
        "event_id": "test_glass_001",
        "tag": "glass_break",
        "confidence": 0.92,
        "timestamp": datetime.now().isoformat(),
        "metadata": {"location": "Main Entrance"}
    }

    print_info(f"전송 데이터: {json.dumps(event, indent=2, ensure_ascii=False)}")
    print_info("요청 전송 중...")

    result = send_sound_event(event)

    if result["success"]:
        data = result["data"]
        print_success(f"응답 코드: {result['status_code']}")
        print_success(f"처리 상태: {data.get('status')}")
        print_success(f"심각도 점수: {data.get('severity_score')}/10")
        print_success(f"메시지: {data.get('message')}")

        if data.get('severity_score', 0) >= 7:
            print_warning("🚨 긴급 알림이 Zapier로 전송되었습니다!")

        return True
    else:
        print_error(f"요청 실패: {result['error']}")
        return False

def test_low_confidence_event():
    """낮은 신뢰도 이벤트 테스트"""
    print_header("테스트 5: 낮은 신뢰도 이벤트 (비명 but 낮은 신뢰도)")

    event = {
        "event_id": "test_low_conf_001",
        "tag": "scream",  # 심각한 소리지만
        "confidence": 0.40,  # 신뢰도가 낮음
        "timestamp": datetime.now().isoformat(),
        "metadata": {"note": "Low confidence detection"}
    }

    print_info(f"전송 데이터: {json.dumps(event, indent=2, ensure_ascii=False)}")
    print_info("요청 전송 중...")

    result = send_sound_event(event)

    if result["success"]:
        data = result["data"]
        print_success(f"응답 코드: {result['status_code']}")
        print_success(f"처리 상태: {data.get('status')}")
        print_success(f"심각도 점수: {data.get('severity_score')}/10")
        print_info("📊 신뢰도가 낮아서 점수가 조정되었습니다")

        return True
    else:
        print_error(f"요청 실패: {result['error']}")
        return False

def check_server_status():
    """서버 상태 확인"""
    print_header("서버 상태 확인")

    try:
        # 루트 엔드포인트 확인
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"서버 상태: {data.get('status')}")
            print_success(f"서비스: {data.get('service')}")
            print_success(f"버전: {data.get('version')}")
        else:
            print_error(f"서버 응답 코드: {response.status_code}")
            return False

        # 헬스체크 확인
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"헬스 상태: {data.get('status')}")
            print_success(f"설정 상태: {json.dumps(data.get('configuration'), indent=2)}")

        return True

    except requests.exceptions.ConnectionError:
        print_error("서버에 연결할 수 없습니다!")
        print_info("다음 명령어로 서버를 시작하세요:")
        print_info("  cd /Users/minseojang/cochl-security-agent")
        print_info("  ./venv/bin/python3 main.py")
        return False
    except Exception as e:
        print_error(f"오류 발생: {str(e)}")
        return False

def main():
    """메인 함수"""
    print(f"\n{BOLD}{'='*60}")
    print(f"🔊 Cochl 보안 에이전트 테스트 스크립트")
    print(f"{'='*60}{RESET}\n")

    # 서버 상태 확인
    if not check_server_status():
        return

    print("\n잠시 후 테스트를 시작합니다...\n")
    time.sleep(2)

    # 테스트 실행
    tests = [
        test_emergency_event,      # 긴급 (비명)
        test_warning_event,         # 경고 (사이렌)
        test_normal_event,          # 일반 (발소리)
        test_glass_break_event,     # 긴급 (유리 깨짐)
        test_low_confidence_event,  # 낮은 신뢰도
    ]

    results = []

    for test_func in tests:
        result = test_func()
        results.append(result)
        time.sleep(1.5)  # 테스트 간 대기

    # 결과 요약
    print_header("테스트 결과 요약")

    success_count = sum(results)
    total_count = len(results)

    print(f"{BOLD}총 테스트: {total_count}개{RESET}")
    print(f"{GREEN}성공: {success_count}개{RESET}")
    print(f"{RED}실패: {total_count - success_count}개{RESET}")

    if success_count == total_count:
        print(f"\n{GREEN}{BOLD}🎉 모든 테스트가 성공했습니다!{RESET}")
    else:
        print(f"\n{YELLOW}{BOLD}⚠️  일부 테스트가 실패했습니다.{RESET}")

    # 로그 파일 확인 안내
    print_header("로그 확인")
    print_info("상세한 로그를 확인하려면:")
    print(f"  {BOLD}cat security_agent.log{RESET}")
    print_info("또는 실시간 로그를 보려면:")
    print(f"  {BOLD}tail -f security_agent.log{RESET}")

    print(f"\n{BOLD}{'='*60}{RESET}\n")

if __name__ == "__main__":
    main()
