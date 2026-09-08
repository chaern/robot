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

`25repeat_1.py`는 DO 2 하나를 `True` 또는 `False`로 전환하는 방식입니다. 실제 결선에 따라 DO 주소와 신호 방식을 맞춰야 합니다.

### 5. Pick & Place 동작 구성

Pick과 Place를 각각 함수로 나누고 다음 순서로 동작하게 구성했습니다.

```text
Pick  : 접근 위치 → 작업 위치 → 그리퍼 닫기 → 후퇴 위치
Place : 접근 위치 → 작업 위치 → 그리퍼 열기 → 후퇴 위치
```

작업 위치에 바로 접근하지 않고 Z축 방향의 접근·후퇴 위치를 거치도록 하여 주변 물체와 충돌할 가능성을 줄였습니다.

### 6. 5×5 격자 반복 작업

`25repeat_1.py`는 각 셀의 접근·작업·후퇴 좌표를 직접 입력합니다. `25repeat.py`는 중심 좌표와 셀 간격을 기준으로 25개 셀을 반복문으로 생성합니다.

```python
for row_index in range(GRID_SIZE):
    for column_index in range(GRID_SIZE):
        x = CENTER_X + (row_index - 2) * CELL_PITCH
        y = CENTER_Y + (column_index - 2) * CELL_PITCH
```

생성된 위치를 이용해 `1번 → 2번`, `2번 → 3번`, ..., `24번 → 25번` 순서로 총 24회의 Pick & Place를 수행합니다.

좌표를 직접 나열하는 방식과 계산으로 생성하는 방식을 비교하면서 반복 코드의 함수화와 일반화 과정을 확인할 수 있습니다.

### 7. 사용자 입력 기반 격자 적재

`input1.py`에서는 사용자가 다음 값을 입력합니다.

- 가로 적재 개수: 1~3
- 세로 적재 줄 수: 1~2
- 시작 칸 번호: 1~6

입력값으로 작업 위치를 먼저 계산하고 격자 범위를 벗어나는지 검사한 후 로봇에 연결합니다. 고정된 `PICK_TARGET`에서 물체를 집어 계산된 위치에 차례대로 내려놓습니다.

또한 Euler 각도로부터 회전행렬을 구해 TCP의 Tool Z축 방향 접근 좌표를 계산했습니다.

```python
tool_z = euler_to_rotm(target_pose[3:6])[:, 2]
offset_pose[axis] += float(tool_z[axis]) * distance_mm
```

이 방식은 베이스 좌표계의 Z값만 단순히 변경하는 것보다 기울어진 툴 자세를 반영할 수 있습니다.

## 프로그램 흐름

```text
사용자 입력 또는 작업 좌표 생성
        ↓
입력 범위와 목표 좌표 확인
        ↓
로봇 연결 및 그리퍼 초기화
        ↓
접근 → Pick → 안전 높이 이동
        ↓
접근 → Place → 후퇴
        ↓
다음 격자 위치에서 반복
        ↓
중앙 안전 위치로 이동
```

## 실행 방법

1. PC와 Indy7을 같은 네트워크에 연결합니다.
2. 코드의 `ROBOT_IP`를 실제 로봇 IP로 수정합니다.
3. 목표 좌표, 그리퍼 DO 주소, 속도와 가속도를 장비 환경에 맞게 확인합니다.
4. 실행할 파일을 선택합니다.

```bash
python circle.py
python movec.py
python 25repeat_1.py
python 25repeat.py
python input1.py
```

`input1.py`는 실행 후 가로 개수, 세로 개수, 시작 칸 번호를 입력합니다.

## 실행 전 안전 확인

- 목표 자세 `[X, Y, Z, RX, RY, RZ]`가 로봇의 작업 범위 안에 있는지 확인합니다.
- 로봇 IP가 파일마다 다를 수 있으므로 실제 장비 주소와 일치하는지 확인합니다.
- 그리퍼의 DO 주소와 ON/OFF 신호가 실제 결선과 일치하는지 확인합니다.
- 낮은 속도에서 접근점, 작업점, 후퇴점을 먼저 검증합니다.
- 비상정지 장치에 즉시 접근할 수 있는 상태에서 시험합니다.
- 사람, 지그, 팔레트 및 로봇 몸체와의 충돌 가능성을 확인합니다.

## 배운 점

- 로봇 TCP 자세를 6개 값으로 표현하고 목표 좌표로 이동시키는 방법
- `MoveL`과 `MoveC`의 역할 및 원 경로를 만드는 두 가지 방법
- 삼각함수로 원주 좌표를 생성하는 방법
- 디지털 출력으로 그리퍼를 제어하는 방법
- 접근·작업·후퇴 위치로 Pick & Place 시퀀스를 구성하는 방법
- 중첩 반복문과 좌표 간격을 이용해 격자 위치를 자동 생성하는 방법
- 사용자 입력값과 작업 영역을 실행 전에 검증하는 방법
- 반복되는 로봇 동작을 함수로 분리하여 재사용하는 방법

## 개선 및 확인할 부분

- `25repeat.py`의 마지막 중심 작업 위치 이동 후에는 모션 완료 대기와 종료 동작을 명확히 추가할 수 있습니다.
- `25repeat_1.py`에는 3행 좌표 정의가 한 번 더 반복되어 있으므로 중복 부분을 정리할 수 있습니다.
- 장비별로 `set_do()` 인자 형식이 튜플 또는 딕셔너리로 다르게 작성되어 있으므로 설치된 `neuromeka` 라이브러리 버전에 맞춰 통일할 필요가 있습니다.
- 예외 발생 시 정지 명령과 안전 위치 복귀를 공통 처리하도록 개선할 수 있습니다.

## 참고

이 저장소의 좌표와 IP는 실습 장비 기준입니다. 실제 로봇에서 실행하기 전에는 티칭 좌표와 주변 환경을 다시 확인해야 합니다.
```

