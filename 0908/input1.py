from time import sleep
from neuromeka import IndyDCP3
from neuromeka.common.utils import euler_to_rotm

# 로봇 및 모션 설정
ROBOT_IP = "192.168.3.6"
GRID_COLS = 3          # 가로 최대 3칸 (X축 방향: 58.41, 138.41, 218.41)
GRID_ROWS = 2          # 세로 최대 2줄 (Y축 방향: 352.35, 272.35 - 몸통 간섭 방지 안전 범위)
MAX_CELL = GRID_COLS * GRID_ROWS  # 총 6칸
CELL_PITCH = 80.0      # 80mm 간격 (그리퍼 간섭 방지)
APPROACH_HEIGHT = 100.0  # 툴 Z축 기준 접근/후퇴 높이 (mm)
TRANSIT_Z = 400.0        # Pick 후 이송 시 안전 Z 높이 (mm)

# 집게형 그리퍼 DO 설정 (DO 0: 열림, DO 1: 닫힘)
GRIPPER_OPEN_DO = 0
GRIPPER_CLOSE_DO = 1
GRIPPER_SETTLE_SEC = 0.5  # 그리퍼 동작 대기 시간 (초)

# 속도 및 가속도 비율 (%)
MOVE_VEL = 60
MOVE_ACC = 30

# 작업 기준 위치
PICK_TARGET = [189.19, 499.91, 252.13, -18.49, 176.03, 87.36]
DROP_TARGET = [58.41, 352.35, 306.07, 0.03, -179.46, 0.08]

# 5×5 격자 번호 ↔ 3×2 번호 매핑
MAP_GRID_TO_5X5 = {
    1: 1, 2: 3, 3: 5,
    4: 11, 5: 13, 6: 15
}

MAP_5X5_TO_GRID = {
    1: 1, 3: 2, 5: 3,
    11: 4, 13: 5, 15: 6
}

indy = None


# 로봇 연결
def connect_robot():
    global indy
    print(f"Indy7 연결 중: {ROBOT_IP}")
    indy = IndyDCP3(ROBOT_IP)
    print("Indy7 연결 완료")


def check_result(result, name):
    print(f"{name} result =", result)
    if not isinstance(result, dict):
        raise RuntimeError(f"{name} 응답 형식 오류: {result}")
    if str(result.get("code")) != "0":
        raise RuntimeError(f"{name} 명령 실패: {result}")


def motion_done_check():
    indy.wait_for_motion_state("is_target_reached")


def move_linear(target, name="이동"):
    print()
    print(name)
    print("Target =", [round(v, 4) for v in target])
    result = indy.movel(
        ttarget=target,
        blending_type=0,
        base_type=0,
        blending_radius=0.0,
        vel_ratio=MOVE_VEL,
        acc_ratio=MOVE_ACC,
    )
    check_result(result, name)
    motion_done_check()


def gripper_open():
    """그리퍼 열기 (DO 0=ON, DO 1=OFF)"""
    result = indy.set_do([
        (GRIPPER_OPEN_DO, True),
        (GRIPPER_CLOSE_DO, False),
    ])
    check_result(result, "Gripper OPEN")
    sleep(GRIPPER_SETTLE_SEC)


def gripper_close():
    """그리퍼 닫기 (DO 0=OFF, DO 1=ON)"""
    result = indy.set_do([
        (GRIPPER_OPEN_DO, False),
        (GRIPPER_CLOSE_DO, True),
    ])
    check_result(result, "Gripper CLOSE")
    sleep(GRIPPER_SETTLE_SEC)


def offset_pose_on_tool_z(target_pose, distance_mm):
    """UVW를 유지하고 타겟에서 TCP Z축 방향으로 떨어진 좌표를 생성"""
    offset_pose = list(target_pose)
    tool_z = euler_to_rotm(target_pose[3:6])[:, 2]
    for axis in range(3):
        offset_pose[axis] += float(tool_z[axis]) * distance_mm
    return offset_pose


# 칸 번호를 좌표로 변환
def cell_position(cell_number):
    """
    1~6번 칸 번호를 격자 좌표로 변환
    기준점: 1번 칸 = DROP_TARGET
    가로(Column, 한 줄 진행): +X 방향 (80mm 간격)
    세로(Row, 다음 줄 진행): -Y 방향 (80mm 간격)
    """
    index = cell_number - 1
    row = index // GRID_COLS
    column = index % GRID_COLS
    position = DROP_TARGET.copy()
    position[0] += column * CELL_PITCH  # 가로 진행: +X 방향
    position[1] -= row * CELL_PITCH     # 세로 줄 진행: -Y 방향
    return position


# Pick 동작
def pick(position):
    approach = offset_pose_on_tool_z(position, -APPROACH_HEIGHT)
    move_linear(approach, "Pick approach")
    move_linear(position, "Pick target")
    gripper_close()
    move_linear(approach, "Pick retract")

    # 물체와 부딪히지 않도록 안전 높이(TRANSIT_Z)로 수직 상승 후 이동
    transit_pose = list(approach)
    if transit_pose[2] < TRANSIT_Z:
        transit_pose[2] = TRANSIT_Z
        move_linear(transit_pose, "Pick lift (안전 이동 높이)")


# Place 동작
def place(position):
    approach = offset_pose_on_tool_z(position, -APPROACH_HEIGHT)
    move_linear(approach, "Place approach")
    move_linear(position, "Place target")
    gripper_open()
    move_linear(approach, "Place retract")


# 작업 위치 목록 생성
def create_work_positions(start_cell, col_count, row_count):
    # 5×5 격자 번호(1, 3, 5, 11, 13, 15)로 입력한 경우 자동 변환
    if start_cell in MAP_5X5_TO_GRID:
        start_cell = MAP_5X5_TO_GRID[start_cell]

    if not 1 <= start_cell <= MAX_CELL:
        raise ValueError(f"시작 칸 번호는 1~{MAX_CELL} 범위여야 합니다.")
    if not 1 <= col_count <= GRID_COLS:
        raise ValueError(f"가로(한 줄) 개수는 1~{GRID_COLS} 범위여야 합니다.")
    if not 1 <= row_count <= GRID_ROWS:
        raise ValueError(f"세로(줄 수) 개수는 1~{GRID_ROWS} 범위여야 합니다. (Y축 몸통 간섭 방지 안전 범위: 최대 2줄)")

    start_index = start_cell - 1
    start_row = start_index // GRID_COLS
    start_column = start_index % GRID_COLS
    positions = []
    for r in range(row_count):
        for c in range(col_count):
            row = start_row + r
            column = start_column + c
            if column >= GRID_COLS or row >= GRID_ROWS:
                raise ValueError(
                    f"가로({col_count}) × 세로({row_count}) 배치가 시작 칸({start_cell}번)에서 격자 범위를 벗어납니다. "
                    f"(row={row + 1}, column={column + 1})"
                )
            cell_number = row * GRID_COLS + column + 1
            position = cell_position(cell_number)
            orig_5x5_cell = MAP_GRID_TO_5X5.get(cell_number, cell_number)
            positions.append({
                "cell": cell_number,
                "orig_cell": orig_5x5_cell,
                "position": position
            })
    return positions


# 작업 위치 출력
def print_work_positions(positions, col_count=None, row_count=None):
    print()
    if col_count and row_count:
        print(f"적재 대상 위치 목록 (가로 {col_count} × 세로 {row_count} = 총 {len(positions)}개)")
    else:
        print("적재 대상 위치 목록")
    print("=" * 95)
    print(
        f"{'순서':^8}"
        f"{'격자 칸':^10}"
        f"{'5×5 원본':^10}"
        f"{'X(mm)':^15}"
        f"{'Y(mm)':^15}"
        f"{'Z(mm)':^15}"
    )
    print("-" * 95)
    for index, item in enumerate(positions):
        position = item["position"]
        print(
            f"{index + 1:^8}"
            f"{item['cell']:^10}"
            f"{item['orig_cell']:^10}"
            f"{position[0]:^15.4f}"
            f"{position[1]:^15.4f}"
            f"{position[2]:^15.4f}"
        )
    print("=" * 95)
    print("총 적재 위치 개수 =", len(positions))


# 격자 적재 실행
def run_grid_mode():
    col_count = int(input(f"가로(한 줄) 개수(1~{GRID_COLS}): "))
    row_count = int(input(f"세로(줄 수) 개수(1~{GRID_ROWS}): "))
    start_cell = int(input(f"시작 칸 번호(1~{MAX_CELL}): "))

    # 로봇에 연결하기 전에 모든 작업 좌표를 생성하고 검사
    positions = create_work_positions(start_cell, col_count, row_count)
    print_work_positions(positions, col_count, row_count)

    connect_robot()
    # 프로그램 시작 전 그리퍼 열림 상태로 초기화
    gripper_open()

    # 고정 PICK_TARGET에서 집은 뒤 각 격자 칸에 적재(Place)
    for index, item in enumerate(positions):
        drop_cell = item["cell"]
        orig_cell = item["orig_cell"]
        drop_pos = item["position"]
        print()
        print("=" * 60)
        print(f"STEP {index + 1}/{len(positions)}: PICK_TARGET → {drop_cell}번 칸 (5×5 {orig_cell}번 칸)")
        print("=" * 60)
        pick(PICK_TARGET)
        place(drop_pos)


# Center 위치로 이동
def move_to_center():
    # 격자 중앙(X=138.41, Y=312.35) 상공으로 안전 복귀
    center_pos = [
        DROP_TARGET[0] + CELL_PITCH,
        DROP_TARGET[1] - (CELL_PITCH / 2),
        DROP_TARGET[2],
        DROP_TARGET[3],
        DROP_TARGET[4],
        DROP_TARGET[5],
    ]
    center_approach = offset_pose_on_tool_z(center_pos, -APPROACH_HEIGHT)
    print()
    print("작업 종료: 중앙 안전 위치로 이동")
    move_linear(center_approach, "Center approach")


# 메인 함수
def main():
    print("Indy7 그리퍼 픽 앤 플레이스 (격자 적재 프로그램)")
    print(f"PICK_TARGET: {PICK_TARGET}")
    print(f"DROP_TARGET: {DROP_TARGET}")
    run_grid_mode()
    move_to_center()
    print()
    print("프로그램 완료")


# 프로그램 시작
if __name__ == "__main__":
    main()