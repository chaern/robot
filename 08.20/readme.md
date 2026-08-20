# 🐍 Python 기초 학습 기록: 변수부터 딕셔너리까지

오늘 배운 파이썬(Python)의 핵심 기본 자료형과 데이터 구조(List, Dictionary) 정리 노트입니다.

---

## 📌 오늘 배운 내용 Summary

| 개념 | 설명 | 예시 |
| :--- | :--- | :--- |
| **변수 (Variables)** | 데이터를 담는 상자 | `x = 10` |
| **기본 자료형** | 숫자형(int, float), 문자열(str), 불리언(bool) | `10`, `3.14`, `"Hello"`, `True` |
| **리스트 (List)** | 순서가 있는 데이터의 집합 (수정 가능) | `[1, 2, 3]` |
| **딕셔너리 (Dictionary)** | Key-Value 쌍으로 이루어진 구조 | `{"name": "Alice", "age": 20}` |

---

## 💻 코드 정리 및 실습

### 1. 변수와 기본 자료형 (Data Types)
- 다양한 종류의 데이터를 변수에 저장하고 출력하는 방법을 익혔습니다.

```python
# 숫자 및 문자열 변수 선언
age = 25
height = 168.5
name = "Python Student"
is_student = True

# Formatted String (f-string)을 활용한 출력
print(f"이름: {name}, 나이: {age}, 키: {height}cm")

```

---

### 2. 리스트 (List)

* 여러 항목을 하나의 변수로 묶어서 관리하며, 인덱스(Index)를 통해 접근합니다.

```python
# 리스트 생성 및 요소 추가/수정
sports = [" 축구", "농구", "야구"]

# 인덱싱 (Indexing)
print(sports[0])  # 첫 번째 요소 출력 ('축구')

# 리스트 요소 추가
sports.append("수영")
print(sports)  # ['축구', '농구', '야구', '수영']

```

---

### 3. 딕셔너리 (Dictionary)

* 키(Key)와 값(Value)의 쌍으로 데이터를 다루어 직관적으로 정보를 찾아볼 수 있습니다.

```python
# 딕셔너리 생성
user_info = {
    "name": "홍길동",
    "age": 20,
    "city": "서울"
}

# Key를 이용한 Value 조회
print(user_info["name"])  # '홍길동'

# 새로운 Key-Value 추가
user_info["job"] = "Developer"
print(user_info)

```

---

## 🔗 실습 노트 (Google Colab)

오늘 진행한 실습 코랩 노트:

* [👉 파이썬 기초 실습 보러가기](https://colab.research.google.com/drive/1cCN3ivBYfo-raiwVVCbY_bz8qQd75P56?usp=drive_link)

---

## 💡 Today I Learned (TIL)

* 리스트는 순서(인덱스)가 중요할 때, 딕셔너리는 데이터의 의미(Key)가 중요할 때 활용하면 효과적이라는 점을 배웠습니다.
* 파이썬 기본 데이터 구조의 특징을 다지며 기본기를 정립했습니다.

```

```
