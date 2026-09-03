"""Indy DCP3 그리퍼 픽 앤 플레이스 프로그램(1회 동작).

실행하기 전에 로봇 IP, DO 채널, TCP/툴 프레임, 픽 및 팔렛 좌표를
저속으로 검증해야 합니다. 작업 좌표의 단위는 [mm, mm, mm, deg, deg, deg]입니다.
"""

import time

from neuromeka import IndyDCP3
from neuromeka.common.utils import euler_to_rotm


# 로봇 및 모션 설정 ----------------------------------------------------------
ROBOT_IP = "192.168.3.6"

PICK_TARGET = [189.19, 499.91, 252.13, -18.49, 176.03, 87.36]
DROP_TARGET = [58.41, 352.35, 306.07, 0.03, -179.46, 0.08]

# 팔레타이징 설정: 2열(X) × 2행(Y) × 2단(Z) = 총 8개
PALLET_COLUMNS = 2
PALLET_ROWS = 2
PALLET_LAYERS = 2
# 기준점에서 X는 +80 mm, Y는 -80 mm 방향으로 배열합니다.
PALLET_SPACING_X_MM = 80.0
PALLET_SPACING_Y_MM = -80.0
PALLET_LAYER_HEIGHT_MM = 30.0

# TCP +Z는 공구 끝이 물체로 접근하는 방향이므로, 접근/후퇴 시에는
# 반대 방향인 TCP -Z로 아래 거리만큼 이동합니다.
APPROACH_DISTANCE_MM = 100.0
VELOCITY_RATIO = 30.0       # 경로 확인 후 필요하면 단계적으로 조정합니다.
ACCELERATION_RATIO = 30.0
MOTION_TIMEOUT_SEC = 60.0
GRIPPER_SETTLE_SEC = 0.7

# 그리퍼 출력: DO 0=열림, DO 1=닫힘
# 두 출력을 동시에 켜지 않도록 항상 반대 상태로 명령합니다.
GRIPPER_OPEN_DO = 0
GRIPPER_CLOSE_DO = 1


indy = IndyDCP3(ROBOT_IP)


def check_response(response, command_name):
    """DCP3 명령의 응답 코드가 0이 아니면 예외를 발생시킵니다."""
    if not isinstance(response, dict):
        return

    result = response.get("response", response)
    code = result.get("code") if isinstance(result, dict) else None
    if code not in (None, 0, "0"):
        raise RuntimeError(f"{command_name} failed: {response}")


def wait_until_motion_done(previous_motion_id, timeout=MOTION_TIMEOUT_SEC):
    """새 모션이 실제로 등록된 것을 확인한 다음 완료될 때까지 기다립니다."""
    deadline = time.monotonic() + timeout
    motion_started = False

    while time.monotonic() < deadline:
        motion = indy.get_motion_data()
        current_motion_id = motion.get("motion_id")

        # 이전 명령의 is_target_reached가 남아 있더라도 완료로 오인하지 않습니다.
        if current_motion_id != previous_motion_id or motion.get("is_in_motion"):
            motion_started = True

        if (
            motion_started
            and motion.get("is_target_reached")
            and not motion.get("is_in_motion")
        ):
            return
        time.sleep(0.02)

    raise TimeoutError(f"Motion did not finish within {timeout:.1f} seconds")


def move_linear(target, name):
    if len(target) != 6:
        raise ValueError(f"{name} must contain six values: {target}")

    previous_motion_id = indy.get_motion_data().get("motion_id")
    print(f"{name}: {[round(value, 3) for value in target]}")
    response = indy.movel(
        target,
        blending_type=0,       # 블렌딩 없음(BlendingType.NONE)
        base_type=0,           # 절대 작업 좌표(TaskBaseType.ABSOLUTE)
        blending_radius=0.0,
        vel_ratio=VELOCITY_RATIO,
        acc_ratio=ACCELERATION_RATIO,
    )
    check_response(response, name)
    wait_until_motion_done(previous_motion_id)


def move_home():
    """팔레타이징 완료 후 로봇의 설정된 Home 관절 위치로 이동합니다."""
    previous_motion_id = indy.get_motion_data().get("motion_id")
    print("Home 이동")
    response = indy.move_home()
    check_response(response, "move_home")
    wait_until_motion_done(previous_motion_id)
    print("Home 도착")


def offset_pose_on_tool_z(target_pose, distance_mm):
    """UVW를 유지하고 타겟에서 TCP Z축 방향으로 떨어진 좌표를 만듭니다."""
    offset_pose = list(target_pose)

    # Neuromeka 자세 회전 순서: Rz(rz) @ Ry(ry) @ Rx(rx)
    # 회전행렬의 세 번째 열은 베이스 좌표계에서 본 TCP +Z 단위벡터입니다.
    tool_z = euler_to_rotm(target_pose[3:6])[:, 2]
    for axis in range(3):
        offset_pose[axis] += float(tool_z[axis]) * distance_mm

    return offset_pose


def generate_pallet_targets():
    """각 층을 지정된 동일 순서로 채우는 팔렛 타겟을 생성합니다."""
    if PALLET_COLUMNS != 2 or PALLET_ROWS != 2:
        raise ValueError("현재 적재 순서는 2×2 배열 전용입니다.")

    # 베이스 좌표 평면에서 본 적재 순서:
    # 기준점 → X+80 → Y-80 → X-80
    pallet_order = [
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1),
    ]
    targets = []

    for layer in range(PALLET_LAYERS):
        for column, row in pallet_order:
            target = list(DROP_TARGET)
            target[0] += column * PALLET_SPACING_X_MM
            target[1] += row * PALLET_SPACING_Y_MM
            target[2] += layer * PALLET_LAYER_HEIGHT_MM
            targets.append({
                "pose": target,
                "column": column + 1,
                "row": row + 1,
                "layer": layer + 1,
            })

    return targets


def gripper_open():
    """그리퍼를 열고 출력 상태를 유지합니다."""
    response = indy.set_do([
        (GRIPPER_OPEN_DO, True),
        (GRIPPER_CLOSE_DO, False),
    ])
    check_response(response, "gripper_open")
    time.sleep(GRIPPER_SETTLE_SEC)
    print("Gripper OPEN")


def gripper_close():
    """그리퍼를 닫고 출력 상태를 유지합니다."""
    response = indy.set_do([
        (GRIPPER_OPEN_DO, False),
        (GRIPPER_CLOSE_DO, True),
    ])
    check_response(response, "gripper_close")
    time.sleep(GRIPPER_SETTLE_SEC)
    print("Gripper CLOSE")


def initialize_gripper():
    """픽 동작 전에 그리퍼를 열린 상태로 초기화합니다."""
    gripper_open()


def execute_pick_and_place():
    # TCP +Z는 공구 끝이 물체를 향하는 방향입니다.
    # 접근과 회수는 반대 방향인 TCP -Z로 100 mm 떨어진 좌표를 사용합니다.
    pick_approach = offset_pose_on_tool_z(PICK_TARGET, -APPROACH_DISTANCE_MM)
    pick_retract = list(pick_approach)
    pick_offset = [pick_approach[i] - PICK_TARGET[i] for i in range(3)]
    print(f"Pick TCP -Z offset:   {[round(value, 3) for value in pick_offset]}")

    initialize_gripper()

    pallet_targets = generate_pallet_targets()
    print(f"총 적재 개수: {len(pallet_targets)}")

    for index, pallet_target in enumerate(pallet_targets, start=1):
        drop_target = pallet_target["pose"]
        drop_approach = offset_pose_on_tool_z(
            drop_target,
            -APPROACH_DISTANCE_MM,
        )
        drop_retract = list(drop_approach)

        print(
            f"\n===== {index}/{len(pallet_targets)}: "
            f"{pallet_target['layer']}단, "
            f"{pallet_target['row']}행, "
            f"{pallet_target['column']}열 ====="
        )

        # 타겟으로 직접 이동하지 않고 반드시 TCP 접근점과 회수점을 거칩니다.
        move_linear(pick_approach, f"{index}-1. Pick 접근")
        move_linear(PICK_TARGET, f"{index}-2. Pick 타겟")
        gripper_close()
        move_linear(pick_retract, f"{index}-3. Pick 회수")

        move_linear(drop_approach, f"{index}-4. Drop 접근")
        move_linear(drop_target, f"{index}-5. Drop 타겟")
        gripper_open()
        move_linear(drop_retract, f"{index}-6. Drop 회수")

    print("2×2×2 팔레타이징 완료")
    move_home()


def stop_safely():
    """그리퍼 상태는 바꾸지 않고 로봇 모션만 정지합니다."""
    try:
        check_response(indy.stop_motion(), "stop_motion")
    except Exception as error:
        print(f"Motion stop failed: {error}")

    # 자동으로 그리퍼를 열면 작업물이 떨어질 수 있으므로 DO 상태를 유지합니다.


if __name__ == "__main__":
    print(f"Current task pose: {indy.get_control_state().get('p')}")
    print(f"Pick target:       {PICK_TARGET}")
    print(f"Drop target:       {DROP_TARGET}")
    print("WARNING: Confirm the workspace is clear and use low-speed test mode first.")

    try:
        execute_pick_and_place()
    except KeyboardInterrupt:
        print("Stopped by operator")
        stop_safely()
    except Exception as error:
        print(f"Robot error: {error}")
        stop_safely()
        raise
