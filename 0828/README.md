# Python 실습 정리

## 1. 동기 / 비동기 프로그래밍

### 동기 프로그래밍

동기 방식은 하나의 작업이 끝난 뒤 다음 작업을 실행하는 방식이다.

```python
def find_users_sync(n):
    for i in range(1, n+1):
        print(f'{n}명중 {i}번 째 사용자 조회 중 ...')
        time.sleep(1)
```

여러 함수를 순서대로 실행하면 앞의 작업이 끝날 때까지 다음 작업은 실행되지 않는다.

```python
find_users_sync(3)
find_users_sync(2)
find_users_sync(1)
```

### 비동기 프로그래밍

`asyncio`를 이용하면 여러 작업의 대기 시간을 겹쳐서 처리할 수 있다.

```python
async def find_users_async(n):
    for i in range(1, n+1):
        print(f'{n}명중 {i}번 째 사용자 조회 중 ...')
        await asyncio.sleep(2)
```

비동기 함수를 정의할 때는 `async def`를 사용하고, 비동기 작업을 기다릴 때는 `await`를 사용한다.

### asyncio.gather()

여러 비동기 작업을 동시에 실행하기 위해 `asyncio.gather()`를 사용할 수 있다.

```python
await asyncio.gather(
    find_users_async(5),
    find_users_async(7),
    find_users_async(1),
)
```

### asyncio.run()

비동기 함수를 실행할 때 사용한다.

```python
asyncio.run(process_async())
```

### 핵심 정리

* `async def` : 비동기 함수 선언
* `await` : 비동기 작업이 완료될 때까지 대기
* `asyncio.sleep()` : 다른 작업에 실행 기회를 주면서 대기
* `asyncio.gather()` : 여러 비동기 작업을 함께 실행
* `asyncio.run()` : 비동기 함수 실행

---

## 2. 2차원 리스트와 Checker Board

Python의 2차원 리스트를 이용하여 `10 × 10` 형태의 배열을 생성하고 체커보드 패턴을 구현했다.

### 2차원 리스트 생성

```python
table = []

for row in range(10):
    table += [[0] * 10]
```

결과적으로 다음과 같은 형태의 2차원 리스트가 만들어진다.

```text
0 0 0 0 0 ...
0 0 0 0 0 ...
0 0 0 0 0 ...
```

### 체커보드 패턴 만들기

행과 열의 인덱스를 더한 값을 이용한다.

```python
if (row + col) % 2 == 0:
    table[row][col] = 1
```

`row + col`이 짝수인 위치에 `1`을 넣으면 교차된 패턴을 만들 수 있다.

### 2차원 리스트 출력

```python
def printList(mylist):
    for row in range(len(mylist)):
        for col in range(len(mylist[0])):
            print(mylist[row][col], end=" ")
        print()
```

### 핵심 정리

* 리스트 내부에 리스트를 넣어 2차원 배열 표현 가능
* `mylist[row][col]` 형태로 특정 위치 접근
* 중첩 `for`문으로 행과 열 순회
* `(row + col) % 2`를 이용하여 체커보드 패턴 구현

---

## 3. 클래스 상속 - Vehicle / Truck

기존 클래스의 속성과 기능을 새로운 클래스에서 물려받는 **상속(Inheritance)**을 실습했다.

### 부모 클래스

```python
class Vehicle:
    def __init__(self, make, model, color, price):
        self.make = make
        self.model = model
        self.color = color
        self.price = price
```

`Vehicle` 클래스는 제조사, 모델, 색상, 가격 정보를 가진다.

### 자식 클래스

```python
class Truck(Vehicle):
```

`Truck` 클래스가 `Vehicle` 클래스를 상속받는다.

따라서 `Truck`은 `Vehicle`이 가지고 있는 속성을 사용할 수 있다.

### super()

```python
super().__init__(
    vehicle.make,
    vehicle.model,
    vehicle.color,
    vehicle.price
)
```

`super()`를 이용하여 부모 클래스인 `Vehicle`의 생성자를 호출했다.

추가로 `Truck`만의 속성인 `payload`를 정의했다.

```python
self.payload = payload
```

### 메서드 오버라이딩

부모 클래스와 같은 이름의 메서드를 자식 클래스에서 다시 정의할 수 있다.

```python
def getdesc(self):
    return super().getdesc()[:-1] + f", {self.payload})"
```

부모 클래스의 `getdesc()` 결과를 가져온 뒤 `payload` 정보를 추가했다.

### 핵심 정리

* `class Truck(Vehicle)` : Vehicle 클래스 상속
* `super()` : 부모 클래스의 메서드 호출
* 자식 클래스에서 새로운 속성 추가 가능
* 부모 클래스의 메서드를 재정의할 수 있음

---

## 4. 클래스 상속 - 게임 유닛 구현

게임의 기본 유닛과 공격 가능한 유닛을 클래스로 구현하며 상속 구조를 실습했다.

### 기본 Unit 클래스

```python
class Unit:
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp
```

모든 유닛이 공통적으로 가지는 이름과 체력을 정의했다.

### AttackUnit 클래스

```python
class AttackUnit(Unit):
```

`AttackUnit`은 `Unit`을 상속받는다.

```python
Unit.__init__(self, name, hp)
```

부모 클래스의 생성자를 호출하여 `name`, `hp`를 초기화한다.

추가로 공격력을 나타내는 `damage` 속성을 정의했다.

```python
self.damage = damage
```

### 공격 기능

```python
def attack(self, location):
    print("{0}:{1} 방향으로 공격합니다 [공격력{2}]"
          .format(self.name, location, self.damage))
```

공격 방향과 공격력을 출력한다.

### 피해 처리

```python
def damaged(self, damage):
    self.hp -= damage
```

공격받은 만큼 HP를 감소시킨다.

```python
if self.hp <= 0:
    print("{0} 파괴 되었습니다.".format(self.name))
```

체력이 `0 이하`가 되면 유닛이 파괴된 것으로 처리한다.

### 핵심 정리

* 공통 속성은 부모 클래스에 정의
* 추가 기능이 필요한 클래스에서 상속하여 확장
* 공격과 피해 처리 등 객체의 행동을 메서드로 표현
* 상속을 통해 코드 중복을 줄일 수 있음

---

## 5. Tkinter 이벤트 처리

`Tkinter`를 이용하여 키보드 입력 이벤트를 감지하는 방법을 실습했다.

### bind()

GUI에서 특정 이벤트가 발생했을 때 실행할 함수를 연결한다.

```python
win.bind("<KeyPress>", key_down)
```

아무 키를 눌렀을 때 `key_down()` 함수가 실행된다.

### 주요 키보드 이벤트

```text
<KeyPress>          아무 키를 눌렀을 때
<KeyRelease>        아무 키를 뗐을 때
<KeyPress-a>        a 키를 눌렀을 때
<KeyRelease-Return> Enter 키를 뗐을 때
```

### 주요 마우스 이벤트

```text
<Button-1>          왼쪽 클릭
<Button-2>          마우스 휠 클릭
<Button-3>          오른쪽 클릭
<Double-Button-1>   왼쪽 더블클릭
<ButtonRelease-1>   왼쪽 버튼을 뗐을 때
<Motion>            마우스를 움직일 때
```

### event 객체

이벤트 함수는 이벤트 정보를 담고 있는 객체를 전달받는다.

```python
def key_down(a):
    global key
    key = a.keysym
```

주요 속성은 다음과 같다.

```text
event.keysym   눌린 키의 이름
event.keycode  키보드 키 코드
event.char     실제 입력 문자
event.x        위젯 기준 마우스 X 좌표
event.y        위젯 기준 마우스 Y 좌표
event.x_root   화면 기준 마우스 X 좌표
event.y_root   화면 기준 마우스 Y 좌표
```

### after()

```python
win.after(1000, ain_proc)
```

`1000ms`, 즉 1초 후 `ain_proc()` 함수를 다시 실행하도록 예약한다.

이를 반복 호출하면 일정 시간 간격으로 GUI의 내용을 갱신할 수 있다.

### Tkinter 기본 실행 구조

```python
win = Tk()

label = Label(win, text="키 입력 전")
label.pack()

win.mainloop()
```

* `Tk()` : 메인 윈도우 생성
* `Label()` : 문자열 표시
* `pack()` : 위젯 배치
* `mainloop()` : GUI 이벤트 처리 시작


