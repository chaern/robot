============================================
 텍스트 기반 스마트 카페 키오스크 시스템
============================================
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
## 🐍 사용한 Python 기능

스마트 카페 키오스크 시스템을 구현하면서 Python의 기본 문법과 자료구조를 실제 주문·재고 관리 기능에 적용했습니다.

### 1. 변수와 자료형

메뉴 가격, 재고 수량, 주문 수량, 결제 금액 등의 데이터를 변수에 저장하여 사용했습니다.

```python
price = MENU[menu_name]["price"]
total = price * qty
change_amount = paid - total
```

주로 `int`, `str`, `bool` 자료형을 사용했습니다.

---

### 2. 딕셔너리(Dictionary)

메뉴별 가격과 재고를 관리하기 위해 **중첩 딕셔너리**를 사용했습니다.

```python
MENU = {
    "아메리카노": {"price": 2000, "stock": 20},
    "카페라떼": {"price": 3000, "stock": 15},
}
```

메뉴명을 Key로 사용하여 가격과 재고 정보를 쉽게 조회하고 수정할 수 있도록 구성했습니다.

```python
MENU[menu_name]["stock"] -= qty
```

---

### 3. 리스트(List)

결제가 완료된 주문 정보를 순서대로 저장하기 위해 리스트를 사용했습니다.

```python
ORDER_HISTORY = []
```

주문이 완료되면 주문 정보를 딕셔너리 형태로 생성한 뒤 리스트에 추가합니다.

```python
ORDER_HISTORY.append(order_record)
```

또한 거스름돈 계산에 사용할 화폐 단위도 리스트로 관리했습니다.

```python
COIN_UNITS = [1000, 500, 100]
```

---

### 4. 조건문 `if / elif / else`

사용자의 입력과 주문 상태에 따라 서로 다른 동작을 수행하기 위해 조건문을 사용했습니다.

예를 들어 주문 수량이 현재 재고보다 많으면 주문을 차단합니다.

```python
if qty > remaining_stock:
    return False, "재고가 부족합니다."
```

메인 메뉴와 관리자 메뉴에서도 사용자가 입력한 번호에 따라 기능을 구분했습니다.

```python
if choice == "1":
    process_order()
elif choice == "2":
    admin_mode()
elif choice == "0":
    sys.exit(0)
else:
    print("올바른 번호를 선택해 주세요.")
```

---

### 5. 반복문 `for`

여러 개의 메뉴나 주문 데이터를 순서대로 처리할 때 `for`문을 사용했습니다.

메뉴판 출력:

```python
for idx, (name, info) in enumerate(MENU.items(), start=1):
    print(name, info)
```

메뉴별 판매량 집계:

```python
for order in ORDER_HISTORY:
    tally[order["menu"]] = tally.get(order["menu"], 0) + order["qty"]
```

거스름돈 계산:

```python
for unit in COIN_UNITS:
    count = remaining // unit
    remaining = remaining % unit
```

---

### 6. 반복문 `while`

키오스크가 사용자가 종료하기 전까지 계속 실행되도록 `while True` 반복문을 사용했습니다.

```python
while True:
    print("1. 주문하기")
    print("2. 관리자 모드")
    print("0. 종료")
```

관리자 모드 역시 사용자가 `0. 나가기`를 선택하기 전까지 계속 사용할 수 있도록 구현했습니다.

---

### 7. 함수(Function)

기능별로 코드를 분리하여 관리하기 위해 `def`를 사용해 함수를 작성했습니다.

```python
def show_menu():
    ...

def validate_order(menu_name, qty):
    ...

def calc_change(amount):
    ...

def process_order():
    ...

def admin_mode():
    ...
```

메뉴 출력, 주문 검증, 재고 차감, 결제, 거스름돈 계산, 관리자 기능 등을 각각 함수로 분리하여 코드의 가독성과 재사용성을 높였습니다.

---

### 8. 사용자 입력과 출력

`input()`을 사용하여 메뉴 번호, 주문 수량, 결제 금액, 관리자 비밀번호 등을 입력받았습니다.

```python
choice = input("선택: ").strip()
```

`print()`를 사용하여 메뉴판, 주문 결과, 결제 금액, 재고 현황 등을 화면에 출력했습니다.

```python
print(f"총 결제 금액: {total:,}원")
```

---

### 9. 문자열 처리

입력값의 불필요한 공백을 제거하기 위해 `strip()`을 사용했습니다.

```python
input("선택: ").strip()
```

입력값이 숫자인지 확인하기 위해 `isdigit()`도 활용했습니다.

```python
if not raw.lstrip("-").isdigit():
    print("숫자만 입력해 주세요.")
```

또한 f-string을 사용하여 변수 값을 문자열 안에 쉽게 출력했습니다.

```python
print(f"{menu_name} x {qty}")
```

---

### 10. 산술 및 비교 연산자

결제 금액과 거스름돈 계산 등에 산술 연산자를 사용했습니다.

```python
total = price * qty
change_amount = paid - total
```

거스름돈 계산에는 몫과 나머지 연산을 사용했습니다.

```python
count = remaining // unit
remaining = remaining % unit
```

재고 확인에는 비교 연산자를 활용했습니다.

```python
if qty > remaining_stock:
```

---

### 11. `break`와 `return`

반복문이나 함수의 실행을 종료하기 위해 사용했습니다.

```python
if choice == "0":
    break
```

잘못된 입력이나 주문이 들어오면 `return`을 사용하여 해당 기능을 즉시 종료했습니다.

```python
if number is None:
    return
```

---

### 12. `enumerate()`

메뉴와 판매 순위에 번호를 자동으로 붙이기 위해 사용했습니다.

```python
for idx, (name, info) in enumerate(MENU.items(), start=1):
```

이를 통해 별도의 번호 변수를 만들지 않고 `1, 2, 3 ...` 형태의 번호를 출력했습니다.

---

### 13. `len()`과 `sum()`

주문 개수를 계산할 때 `len()`을 사용했습니다.

```python
count = len(ORDER_HISTORY)
```

전체 주문 금액을 더하여 총 매출을 계산할 때 `sum()`을 사용했습니다.

```python
total = sum(order["total"] for order in ORDER_HISTORY)
```

---

### 14. 정렬 `sorted()`과 `lambda`

관리자 모드에서 메뉴별 판매량을 기준으로 베스트 메뉴 순위를 만들기 위해 사용했습니다.

```python
ranked = sorted(
    tally.items(),
    key=lambda x: x[1],
    reverse=True
)
```

판매 수량이 높은 메뉴부터 내림차순으로 정렬하여 출력하도록 구현했습니다.

---

## 💡 프로젝트에서 활용한 핵심 Python 문법

| Python 기능          | 프로젝트 활용                |
| ------------------ | ---------------------- |
| 변수                 | 가격, 수량, 결제 금액 저장       |
| Dictionary         | 메뉴 가격 및 재고 관리          |
| List               | 주문 내역 및 화폐 단위 관리       |
| `if / elif / else` | 주문 검증, 메뉴 선택, 재고 확인    |
| `for`              | 메뉴 출력, 판매량 집계, 거스름돈 계산 |
| `while`            | 키오스크와 관리자 메뉴 반복 실행     |
| 함수 `def`           | 기능별 코드 분리              |
| `input()`          | 사용자 입력                 |
| `print()`          | 메뉴 및 결과 출력             |
| `return`           | 함수 결과 반환 및 조기 종료       |
| `break`            | 반복문 종료                 |
| `enumerate()`      | 메뉴 번호 및 순위 생성          |
| `len()`            | 주문 건수 계산               |
| `sum()`            | 총 매출 계산                |
| `sorted()`         | 판매 순위 정렬               |
| `lambda`           | 판매 수량 기준 정렬            |
| `//`, `%`          | 거스름돈 화폐 개수 계산          |
| f-string           | 주문·가격 정보 출력            |

## 🚀 주요 구현 포인트

* **딕셔너리를 활용한 메뉴 및 재고 관리**
* **리스트를 활용한 주문 내역 저장**
* **if문을 활용한 실시간 재고 검증**
* **for문과 나눗셈 연산을 활용한 거스름돈 계산**
* **while문을 활용한 반복 실행형 키오스크 구현**
* **함수를 활용한 주문·결제·관리자 기능 분리**
* **관리자 모드에서 주문 데이터를 활용한 매출 및 베스트 메뉴 집계**
* **비정상 입력, 존재하지 않는 메뉴, 재고 부족 등의 입력 검증 구현**
