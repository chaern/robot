from neuromeka import IndyDCP3
from time import sleep

# 로봇 연결 및 모션 설정
ROBOT_IP = "192.168.3.6"
MOVE_VEL = 10
MOVE_ACC = 10
GRID_SIZE = 5
CELL_PITCH = 40.0
APPROACH_HEIGHT = 50.0

# 집게형 그리퍼 DO 설정 (DO 0: 열림, DO 1: 닫힘)
GRIPPER_OPEN_DO = 0
GRIPPER_CLOSE_DO = 1
GRIPPER_SETTLE_SEC = 0.7

# 5×5 그리드 중심 좌표 (gripper.py 팔렛 영역 기준 정중앙)
# X 범위 (58.41 ~ 138.41)의 중심 = 98.41
# Y 범위 (272.35 ~ 352.35)의 중심 = 312.35
CENTER_X = 98.41
CENTER_Y = 312.35
TARGET_Z = 306.07  # 집게형 그리퍼 작업 높이
RX = 0.03
RY = -179.46
RZ = 0.08

indy = IndyDCP3(ROBOT_IP)


def motion_done_check():
    indy.wait_for_motion_state("is_target_reached")


def move_linear(target_position):
    indy.movel(ttarget=target_position, vel_ratio=MOVE_VEL, acc_ratio=MOVE_ACC)
    motion_done_check()


def gripper_open():
    """그리퍼 열기 (DO 0=ON, DO 1=OFF)"""
    indy.set_do([
        {"address": GRIPPER_OPEN_DO, "state": True},
        {"address": GRIPPER_CLOSE_DO, "state": False},
    ])
    sleep(GRIPPER_SETTLE_SEC)
    print("Gripper OPEN")


def gripper_close():
    """그리퍼 닫기 (DO 0=OFF, DO 1=ON)"""
    indy.set_do([
        {"address": GRIPPER_OPEN_DO, "state": False},
        {"address": GRIPPER_CLOSE_DO, "state": True},
    ])
    sleep(GRIPPER_SETTLE_SEC)
    print("Gripper CLOSE")


# Pick 동작
# 접근 → 타겟 → 그리퍼 닫기(집기) → 리트랙트
def pick(cell_index):
    move_linear(pos[cell_index][0])
    move_linear(pos[cell_index][1])
    gripper_close()
    move_linear(pos[cell_index][2])


# Place 동작
# 접근 → 타겟 → 그리퍼 열기(놓기) → 리트랙트
def place(cell_index):
    move_linear(pos[cell_index][0])
    move_linear(pos[cell_index][1])
    gripper_open()
    move_linear(pos[cell_index][2])


def create_grid_positions():
    position_list = []
    for row_index in range(GRID_SIZE):
        for column_index in range(GRID_SIZE):
            x = CENTER_X + (row_index - 2) * CELL_PITCH
            y = CENTER_Y + (column_index - 2) * CELL_PITCH
            approach_position = [
                x,
                y,
                TARGET_Z + APPROACH_HEIGHT,
                RX,
                RY,
                RZ,
            ]
            target_position = [x, y, TARGET_Z, RX, RY, RZ]
            retract_position = [
                x,
                y,
                TARGET_Z + APPROACH_HEIGHT,
                RX,
                RY,
                RZ,
            ]
            position_list.append([approach_position, target_position, retract_position])
    return position_list


pos = create_grid_positions()
print("총 그리드 셀 개수:", len(pos))
print("1번 셀 타겟 좌표:", pos[0][1])
print("중심 셀 타겟 좌표:", pos[12][1])

# 시작 전 그리퍼 열림 상태로 초기화
gripper_open()

indy.move_home()
motion_done_check()

# 1번 → 2번, 2번 → 3번, ... , 24번 → 25번
# 총 24회의 Pick & Place 수행
for cell_index in range(len(pos) - 1):
    pick(cell_index)
    current_position = indy.get_control_state()["p"]
    print("Pick 완료 위치:", current_position)
    place(cell_index + 1)
    current_position = indy.get_control_state()["p"]
    print("Place 완료 위치:", current_position)

move_linear(pos[12][0])
motion_done_check()
indy.movel(ttarget=pos[12][1])
