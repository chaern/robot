## 1. 스레드(Thread)란?

스레드는 하나의 프로그램 안에서 실행되는 **작업의 흐름**입니다.

여러 개의 스레드를 사용하면 하나의 프로그램에서 여러 작업을 동시에 실행하는 것처럼 처리할 수 있습니다.

예를 들어,

* 메인 스레드 → 프로그램의 주요 작업 수행
* 작업 스레드 → 별도의 함수 실행
* 백그라운드 스레드 → 보조 작업 수행

과 같이 사용할 수 있습니다.

---

## 2. 기본 스레드 생성

```python
import threading

def worker():
    print("Worker thread running")

thread = threading.Thread(target=worker)
thread.start()
```

### 주요 코드

```python
threading.Thread(target=worker)
```

새로운 스레드 객체를 생성합니다.

`target=worker`는 해당 스레드가 실행할 함수를 지정합니다.

```python
thread.start()
```

생성한 스레드를 실제로 실행합니다.

---

## 3. `time.sleep()`

```python
import time

time.sleep(1)
```

현재 실행 중인 스레드를 지정한 시간만큼 일시 정지합니다.

위 코드에서는 현재 스레드가 **1초 동안 대기**합니다.

각 스레드는 독립적으로 실행되기 때문에 한 스레드가 `sleep()` 중이어도 다른 스레드는 계속 실행될 수 있습니다.

---

## 4. 데몬 스레드(Daemon Thread)

데몬 스레드는 **메인 프로그램이 종료되면 함께 종료되는 스레드**입니다.

```python
import threading
import time

def daemon_worker():
    while True:
        print("Daemon thread running")
        time.sleep(1)

thread = threading.Thread(target=daemon_worker)
thread.daemon = True

thread.start()

time.sleep(2)

print("Main thread finished")
```

### 핵심

```python
thread.daemon = True
```

해당 스레드를 데몬 스레드로 설정합니다.

또는 생성할 때 바로 설정할 수도 있습니다.

```python
thread = threading.Thread(
    target=daemon_worker,
    daemon=True
)
```

데몬 스레드는 계속 실행 중이더라도 메인 스레드가 종료되면 같이 종료됩니다.

---

## 5. `join()`

`join()`은 **메인 스레드가 다른 스레드의 종료를 기다리도록 하는 함수**입니다.

```python
import threading
import time

def worker():
    print("Worker thread started")

    time.sleep(2)

    print("Worker thread finished")

thread = threading.Thread(target=worker)

thread.start()

print("Main thread waiting for worker thread")

thread.join()

print("Main thread finished")
```

### 실행 흐름

```text
Worker thread started
Main thread waiting for worker thread

2초 대기

Worker thread finished
Main thread finished
```

### 핵심

```python
thread.start()
```

스레드를 시작합니다.

```python
thread.join()
```

해당 스레드가 끝날 때까지 메인 스레드가 기다립니다.

즉,

* `start()` → 작업 시작
* `join()` → 작업이 끝날 때까지 기다림

으로 이해할 수 있습니다.

---

## 6. `join()`이 없는 경우

```python
import threading
import time

def worker():
    print("Worker thread started")

    time.sleep(2)

    print("Worker thread finished")

thread = threading.Thread(
    target=worker,
    daemon=True
)

thread.start()

print("Main thread finished")
```

`join()`이 없기 때문에 메인 스레드는 worker 스레드가 끝나는 것을 기다리지 않습니다.

또한 `daemon=True`이기 때문에 메인 스레드가 먼저 종료되면 worker 스레드도 함께 종료될 수 있습니다.

따라서 다음 출력이 나오지 않을 수도 있습니다.

```text
Worker thread finished
```

---

## 7. 거북이와 토끼 스레드 예제

```python
import threading
import time


def turtle_run():

    print("거북이 출발")

    for i in range(1, 21):

        time.sleep(0.9)

        print("거북이 -> %dm" % i)

    print("거북이 -> 20m 도착")


def rabbit_run():

    print("토끼 출발")

    for i in range(1, 14):

        time.sleep(0.35)

        print("토끼 -> %dm" % i)

    print("토끼 -> %dm 낮잠" % i)

    time.sleep(11)

    print("토끼 -> %dm 잠 깸" % i)

    for i in range(14, 21):

        time.sleep(0.55)

        print("토끼 -> %dm" % i)

    print("토끼 -> 20m 도착")


t1 = threading.Thread(
    target=turtle_run,
    daemon=True
)

t2 = threading.Thread(
    target=rabbit_run,
    daemon=True
)


t1.start()
t2.start()


t1.join()
t2.join()


print("메인 스레드 종료 전 1초 대기...")

time.sleep(1)

print("메인 스레드 종료")
```

---

## 8. 실행 구조

거북이와 토끼는 각각 다른 스레드에서 실행됩니다.

```text
                Main Thread
                     │
            ┌────────┴────────┐
            │                 │
        t1.start()         t2.start()
            │                 │
       turtle_run()       rabbit_run()
            │                 │
         거북이 실행          토끼 실행
            │                 │
            └────────┬────────┘
                     │
                  join()
                     │
            두 스레드 종료 대기
                     │
               Main 종료
```

두 스레드는 동시에 실행되기 때문에 출력 순서는 상황에 따라 달라질 수 있습니다.

---

## 9. `daemon=True`와 `join()` 비교

| 기능            | 의미                     |
| ------------- | ---------------------- |
| `start()`     | 스레드 실행 시작              |
| `daemon=True` | 메인 스레드가 종료되면 같이 종료     |
| `join()`      | 해당 스레드가 종료될 때까지 기다림    |
| `sleep()`     | 현재 실행 중인 스레드를 일정 시간 정지 |

### `daemon=True`

```text
메인 스레드 종료
       ↓
데몬 스레드도 종료
```

### `join()`

```text
작업 스레드 실행
       ↓
메인 스레드가 기다림
       ↓
작업 스레드 종료
       ↓
메인 스레드 계속 실행
```

---

## 10. 핵심 정리

```python
thread = threading.Thread(target=worker)
```

→ 스레드 생성

```python
thread.start()
```

→ 스레드 실행

```python
thread.join()
```

→ 스레드가 끝날 때까지 기다림

```python
thread.daemon = True
```

또는

```python
threading.Thread(target=worker, daemon=True)
```

→ 메인 프로그램 종료 시 함께 종료되는 데몬 스레드로 설정

```python
time.sleep(1)
```

→ 현재 실행 중인 스레드를 1초 동안 일시 정지

---

## 한 줄 요약

> **Thread는 하나의 프로그램 안에서 여러 작업 흐름을 실행할 수 있게 하며, `start()`로 시작하고 `join()`으로 종료를 기다리며 `daemon=True`를 사용하면 메인 프로그램 종료 시 함께 종료되도록 설정할 수 있다.**

