#7번 김채린

import time
from neuromeka import IndyDCP3

indy = IndyDCP3("192.168.3.6")

# 티칭값: task 좌표 [x, y, z, rx, ry, rz] (mm, degree)
PICK = [231.58292, 513.9421, 346.49518, -179.57152, -20.195204, 175.96294]
PALLET_ORIGIN = [51.25, 291.967, 407.7642, 0.1349501, -179.99442, 0.13298981]  # 2번 위치

# 매거진 번호별 (X, Y) 오프셋. 장비 방향이 다르면 부호를 바꾼다.
PALLET_OFFSETS = {2: (0, 0), 4: (0, 80), 8: (40, 40), 10: (40, 120)}

APPROACH_Z = 100.0
VEL = ACC = 15.0

VACUUM_OUTPUT = 2        # 디지털 출력 D2
VACUUM_ON_DELAY = 0.5    # 흡착 안정 시간
VACUUM_OFF_DELAY = 0.3   # 흡착 해제 안정 시간


def above(pose):
    """Z축으로 APPROACH_Z만큼 높은 접근 자세."""
    return pose[:2] + [pose[2] + APPROACH_Z] + pose[3:]


def pallet_pose(number):
    dx, dy = PALLET_OFFSETS[number]
    pose = list(PALLET_ORIGIN)
    pose[0] += dx
    pose[1] += dy
    return pose


def vacuum(on):
    indy.set_do([(VACUUM_OUTPUT, on)])
    time.sleep(VACUUM_ON_DELAY if on else VACUUM_OFF_DELAY)


def check(response, name):
    code = response.get("response", response).get("code", 0) if isinstance(response, dict) else 0
    if code not in (0, "0"):
        raise RuntimeError("{} 실패: {}".format(name, response))


def run_and_wait(command, name, timeout=60.0):
    """모션 명령을 실행하고 새 모션이 시작되어 끝날 때까지 기다린다."""
    prev_id = indy.get_motion_data().get("motion_id")
    check(command(), name)

    deadline = time.monotonic() + timeout
    started = False
    while time.monotonic() < deadline:
        motion = indy.get_motion_data()
        if motion.get("motion_id") != prev_id or motion.get("is_in_motion"):
            started = True
        if started and motion.get("is_target_reached") and not motion.get("is_in_motion"):
            return
        time.sleep(0.02)
    raise TimeoutError("로봇 이동 완료 대기 시간 초과")


def move_home():
    run_and_wait(indy.move_home, "move_home")


def move(pose):
    run_and_wait(lambda: indy.movel(pose, blending_type=0, base_type=0, blending_radius=0.0,
                                    vel_ratio=VEL, acc_ratio=ACC), "movel")


def pick():
    move(above(PICK))
    move(PICK)
    vacuum(True)
    move(above(PICK))


def place(number):
    target = pallet_pose(number)
    move(above(target))
    move(target)
    vacuum(False)
    move(above(target))


def main():
    indy.set_do([(VACUUM_OUTPUT, False)])  # 시작 시 흡착 OFF
    move_home()
    for number in (2, 4, 8, 10):
        pick()
        place(number)
    move_home()


if __name__ == "__main__":
    main()
