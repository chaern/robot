# Indy7 로봇 제어 실습

Neuromeka Indy7 협동로봇과 Python API를 이용하여 직선·원호 이동, 그리퍼 제어, 격자 좌표 생성, 반복 Pick & Place를 실습한 코드입니다.

## 실습 환경

- Robot: Neuromeka Indy7
- Language: Python
- Library: `neuromeka` (`IndyDCP3`)
- Communication: 로봇 IP 기반 DCP3 연결
- Motion: `MoveL`, `MoveC`
- End effector: Digital Output(DO) 기반 그리퍼

> 각 파일에는 실습 장비에서 사용한 IP, 작업 좌표, 속도, 가속도, DO 주소가 들어 있습니다. 다른 장비에서 실행할 때는 실제 환경에 맞게 반드시 수정해야 합니다.

## 파일 구성

| 파일 | 실습 내용 |
| --- | --- |
| `circle.py` | 현재 TCP 위치를 중심으로 XY 평면에 반지름 100 mm의 원 경로 생성 |
| `movec.py` | `MoveL`로 시작점에 이동한 뒤 `MoveC`로 360도 원호 이동 |
| `25repeat_1.py` | 5×5 격자의 25개 위치를 직접 정의하고 24회 Pick & Place 반복 |
| `25repeat.py` | 반복문으로 5×5 격자 좌표를 자동 생성하고 순차 Pick & Place 수행 |
| `input1.py` | 사용자 입력에 따라 3×2 안전 격자에 물체를 반복 적재 |

## 주요 실습 내용

### 1. 로봇 연결과 모션 완료 확인

`IndyDCP3` 객체에 로봇 IP를 전달하여 연결하고, 다음 명령을 보내기 전에 목표 위치 도달 여부를 확인했습니다.

```python
indy = IndyDCP3(ROBOT_IP)

def motion_done_check():
    indy.wait_for_motion_state("is_target_reached")
```

모션 명령 직후 완료 상태를 기다리면 여러 이동 명령이 순서대로 실행됩니다.

### 2. MoveL 직선 이동

`movel()`을 사용해 TCP를 목표 자세까지 직선으로 이동했습니다. 목표 자세는 `[X, Y, Z, RX, RY, RZ]` 형식입니다.

```python
indy.movel(
    ttarget=target_position,
    vel_ratio=MOVE_VEL,
    acc_ratio=MOVE_ACC,
)
```

### 3. 두 가지 원 운동 방법

#### 여러 점을 계산하는 방식 (`circle.py`)

현재 TCP 위치를 원의 중심으로 사용하고 삼각함수로 원주 위의 좌표를 계산했습니다.

```python
angle = 2.0 * math.pi * point_number / NUM_POINTS
x = center_x + RADIUS * math.cos(angle)
y = center_y + RADIUS * math.sin(angle)
```

- 반지름: 100 mm
- 분할점: 10개
- 이동 평면: XY 평면
- Z 좌표와 TCP 자세: 현재 값 유지

분할점 수를 늘리면 경로가 더 촘촘해지지만 이동 명령 수도 증가합니다.

#### MoveC 명령을 사용하는 방식 (`movec.py`)

시작점까지 `MoveL`로 이동한 뒤, 경유점과 끝점을 지정해 `MoveC` 원호 이동을 수행했습니다.

```python
indy.movec(
    tpos0=via_point,
    tpos1=end_point,
    angle=360,
    vel_ratio=MOVE_VEL,
    acc_ratio=MOVE_ACC,
)
```

두 파일을 통해 여러 직선 구간으로 원을 근사하는 방법과 로봇의 원호 명령을 이용하는 방법을 비교할 수 있습니다.

### 4. Digital Output을 이용한 그리퍼 제어

DO 상태를 변경하여 그리퍼를 열고 닫았습니다. `25repeat.py`와 `input1.py`는 열림과 닫힘에 각각 두 개의 DO를 사용합니다.

```python
# 열기: DO 0 ON, DO 1 OFF
# 닫기: DO 0 OFF, DO 1 ON
```

