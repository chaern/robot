"""
========================================================
 텍스트 기반 스마트 카페 키오스크 시스템
========================================================
프로젝트 킥오프 문서 기준 구현.

[데이터 구조]
- 메뉴/재고: 중첩 딕셔너리 { "메뉴명": {"price": int, "stock": int} }
  -> 해시맵 기반 O(1) 조회/갱신
- 주문 내역: 리스트 (결제 완료된 개별 주문 객체를 순차 적재)
  -> 관리자 모드에서 정렬/집계하여 매출 통계, 베스트 메뉴 산출

[핵심 비즈니스 로직]
1) 실시간 재고 검증: 주문 수량 > 잔여 재고 시 강제 차단
2) 탐욕 알고리즘 기반 거스름돈 최적화 (1000원, 500원, 100원 단위, 화폐 개수 최소화)
3) 보안 기반 관리자 모드: 하드코딩 비밀번호로 세션 접근 제어
   - 매출 집계 / 베스트 메뉴 / 재고 대시보드

[예외 처리]
- 음수/문자열 등 비정상 금액 입력
- 존재하지 않는 메뉴 선택
- 재고 부족 시도
"""

import sys


# ---------------------------------------------------------
# 1. 데이터 모델
# ---------------------------------------------------------

# 메뉴 및 재고: 중첩 딕셔너리 스키마
# { "메뉴명": {"price": int, "stock": int} }
MENU: dict[str, dict[str, int]] = {
    "아메리카노": {"price": 2000, "stock": 20},
    "카페라떼": {"price": 3000, "stock": 15},
    "카푸치노": {"price": 3000, "stock": 10},
    "바닐라라떼": {"price": 3500, "stock": 12},
    "콜드브루": {"price": 3500, "stock": 8},
    "초코라떼": {"price": 3500, "stock": 10},
}

# 주문 트래킹: 순차 리스트 구조
# 각 원소는 결제 완료된 하나의 주문 객체(dict)
ORDER_HISTORY: list[dict] = []

# 거스름돈 계산에 사용할 화폐 단위 (큰 단위부터 그리디하게 소진)
COIN_UNITS = [1000, 500, 100]

# 관리자 모드 하드코딩 비밀번호
ADMIN_PASSWORD = "1234"


# ---------------------------------------------------------
# 2. 유틸리티 / 입력 검증
# ---------------------------------------------------------

def read_int(prompt: str) -> int | None:
    """정수 입력을 받되, 문자열 등 비정상 입력 시 None을 반환한다."""
    raw = input(prompt).strip()
    if not raw.lstrip("-").isdigit():
        print("⚠️  숫자만 입력해 주세요.")
        return None
    return int(raw)


def print_divider():
    print("-" * 46)


# ---------------------------------------------------------
# 3. 메뉴 출력
# ---------------------------------------------------------

def show_menu():
    print_divider()
    print("☕ 스마트 카페 메뉴판 ☕")
    print_divider()
    for idx, (name, info) in enumerate(MENU.items(), start=1):
        stock_tag = "품절" if info["stock"] <= 0 else f"재고 {info['stock']}개"
        print(f"{idx:>2}. {name:<10} {info['price']:>6,}원   ({stock_tag})")
    print_divider()


# ---------------------------------------------------------
# 4. 실시간 재고 검증 및 상태 관리
# ---------------------------------------------------------

def select_menu_by_number(number: int) -> str | None:
    """번호로 메뉴명을 찾는다. 존재하지 않으면 None."""
    names = list(MENU.keys())
    if 1 <= number <= len(names):
        return names[number - 1]
    return None


def validate_order(menu_name: str, qty: int) -> tuple[bool, str]:
    """
    주문 유효성 검증.
    - 존재하지 않는 메뉴
    - 수량 <= 0 (비정상 값)
    - 주문 수량 > 잔여 재고 ('품절 후 결제' 방지)
    반환: (성공 여부, 메시지)
    """
    if menu_name not in MENU:
        return False, "존재하지 않는 메뉴입니다."
    if qty <= 0:
        return False, "수량은 1개 이상이어야 합니다."
    remaining_stock = MENU[menu_name]["stock"]
    if qty > remaining_stock:
        return False, f"재고 부족: 현재 '{menu_name}' 재고는 {remaining_stock}개입니다."
    return True, "OK"


def deduct_stock(menu_name: str, qty: int):
    """검증 통과 후 실제 재고 차감."""
    MENU[menu_name]["stock"] -= qty


# ---------------------------------------------------------
# 5. 탐욕 알고리즘 기반 거스름돈 최적화
# ---------------------------------------------------------

def calc_change(amount: int) -> dict[int, int]:
    """
    잔돈을 화폐 단위별 최소 개수로 반환하는 탐욕 알고리즘.
    수량 = 남은 금액 // 화폐 단위 (Floor Division)
    남은 금액 = 남은 금액 % 화폐 단위 (Modulo)
    """
    result = {}
    remaining = amount
    for unit in COIN_UNITS:
        count = remaining // unit
        remaining = remaining % unit
        if count > 0:
            result[unit] = count
    return result


def print_change(change: dict[int, int]):
    if not change:
        print("거슬러 드릴 금액이 없습니다.")
        return
    print("💰 거스름돈 안내:")
    for unit, count in change.items():
        print(f"   {unit:,}원 x {count}개")


# ---------------------------------------------------------
# 6. 주문 / 결제 플로우
# ---------------------------------------------------------

def process_order():
    show_menu()
    number = read_int("주문할 메뉴 번호를 입력하세요 (0: 취소): ")
    if number is None:
        return
    if number == 0:
        print("주문을 취소했습니다.")
        return

    menu_name = select_menu_by_number(number)
    if menu_name is None:
        print("⚠️  존재하지 않는 메뉴 번호입니다.")
        return

    qty = read_int(f"'{menu_name}' 수량을 입력하세요: ")
    if qty is None:
        return

    ok, msg = validate_order(menu_name, qty)
    if not ok:
        print(f"❌ 주문 실패: {msg}")
        return

    price = MENU[menu_name]["price"]
    total = price * qty
    print(f"\n총 결제 금액: {total:,}원")

    paid = read_int("투입 금액을 입력하세요: ")
    if paid is None:
        return
    if paid < 0:
        print("⚠️  투입 금액은 음수가 될 수 없습니다.")
        return
    if paid < total:
        print(f"❌ 금액이 부족합니다. (부족액: {total - paid:,}원)")
        return

    # 재고 차감 + 결제 완료 처리
    deduct_stock(menu_name, qty)
    change_amount = paid - total
    change_breakdown = calc_change(change_amount)

    order_record = {
        "menu": menu_name,
        "qty": qty,
        "unit_price": price,
        "total": total,
        "paid": paid,
        "change": change_amount,
    }
    ORDER_HISTORY.append(order_record)

    print("\n✅ 결제가 완료되었습니다!")
    print(f"   메뉴: {menu_name} x {qty}")
    print(f"   결제 금액: {total:,}원")
    print_change(change_breakdown)


# ---------------------------------------------------------
# 7. 관리자 모드 (Admin Intelligence)
# ---------------------------------------------------------

def admin_login() -> bool:
    pw = input("관리자 비밀번호를 입력하세요: ").strip()
    return pw == ADMIN_PASSWORD


def admin_total_sales():
    """주문 리스트 전체를 순회하여 총 매출 산출."""
    total = sum(order["total"] for order in ORDER_HISTORY)
    count = len(ORDER_HISTORY)
    print_divider()
    print(f"📊 총 매출: {total:,}원 (총 {count}건)")
    print_divider()


def admin_best_menu():
    """주문 내역에서 메뉴별 판매 수량을 집계하여 베스트 메뉴 도출."""
    if not ORDER_HISTORY:
        print("아직 주문 내역이 없습니다.")
        return

    tally: dict[str, int] = {}
    for order in ORDER_HISTORY:
        tally[order["menu"]] = tally.get(order["menu"], 0) + order["qty"]

    ranked = sorted(tally.items(), key=lambda x: x[1], reverse=True)

    print_divider()
    print("🏆 베스트 메뉴 순위")
    print_divider()
    for rank, (name, qty) in enumerate(ranked, start=1):
        print(f"{rank}. {name} - {qty}개 판매")
    print_divider()


def admin_stock_dashboard():
    """딕셔너리의 현재 stock 상태를 전수 출력."""
    print_divider()
    print("📦 재고 대시보드")
    print_divider()
    for name, info in MENU.items():
        status = "⚠️ 품절" if info["stock"] <= 0 else ""
        print(f"{name:<10} 재고 {info['stock']:>3}개  {status}")
    print_divider()


def admin_mode():
    if not admin_login():
        print("❌ 비밀번호가 일치하지 않습니다.")
        return

    print("\n🔐 관리자 모드에 진입했습니다.")
    while True:
        print("\n[관리자 메뉴]")
        print("1. 매출 집계")
        print("2. 베스트 메뉴")
        print("3. 재고 대시보드")
        print("0. 나가기")
        choice = input("선택: ").strip()

        if choice == "1":
            admin_total_sales()
        elif choice == "2":
            admin_best_menu()
        elif choice == "3":
            admin_stock_dashboard()
        elif choice == "0":
            print("관리자 모드를 종료합니다.")
            break
        else:
            print("⚠️  올바른 번호를 선택해 주세요.")


# ---------------------------------------------------------
# 8. 메인 루프
# ---------------------------------------------------------

def main():
    print("=" * 46)
    print("   스마트 카페 키오스크 시스템에 오신 것을 환영합니다")
    print("=" * 46)

    while True:
        print("\n[메인 메뉴]")
        print("1. 주문하기")
        print("2. 관리자 모드")
        print("0. 종료")
        choice = input("선택: ").strip()

        if choice == "1":
            process_order()
        elif choice == "2":
            admin_mode()
        elif choice == "0":
            print("이용해 주셔서 감사합니다. 시스템을 종료합니다.")
            sys.exit(0)
        else:
            print("⚠️  올바른 번호를 선택해 주세요.")


if __name__ == "__main__":
    main()