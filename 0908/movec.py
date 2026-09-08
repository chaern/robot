#옆으로원운동
from neuromeka import IndyDCP3
import time
ROBOT_IP = "192.168.3.6"
MOVE_VEL = 5
MOVE_ACC = 5
indy = IndyDCP3(ROBOT_IP)
def move_done_check():
    print("이동 완료 대기 중...")
    indy.wait_for_motion_state(   "is_target_reached"    )
    print("이동 완료")
# MoveL 함수
def move_linear(target_position):
    print()
    print("==============================")
    print("MoveL")
    print("==============================")
    print("Target Position =")
    print(target_position)
    result = indy.movel(   ttarget=target_position,   vel_ratio=MOVE_VEL,     acc_ratio=MOVE_ACC    )
    print("MoveL Result =", result)
    move_done_check()
# MoveC 함수
def move_circle(via_point, end_point, angle):
    print()
    print("==============================")
    print("MoveC")
    print("==============================")
    print("Via Point =")
    print(via_point)
    print("End Point =")
    print(end_point)
    print("Angle =", angle)
    result = indy.movec( tpos0=via_point,  tpos1=end_point,  angle=angle,  vel_ratio=MOVE_VEL,  acc_ratio=MOVE_ACC    )
    print("MoveC Result =", result)
    move_done_check()
def main():
    print()
    print("====================================")
    print("Indy7 MoveC 원 운동 시작")
    print("====================================")
    # 원 운동 시작 위치
    start_pos = [ 400.83,   -61.27,   647.45,    0.07,   179.96,     8.78    ]
    # Via Point
    via_point = [  201.66,   -51.11,   644.20,   0.0,   180.0,   23.36    ]
    # End Point
    end_point = [  401.53,  -47.74,    647.50,  0.0,     180.0,    23.37    ]
    # 시작 위치 이동
    print()
    print("STEP 1 : Start Position 이동")
    move_linear(start_pos)
    # 원 운동
    print()
    print("STEP 2 : 360도 원 운동")
    move_circle( via_point,  end_point,   360    )
    print()
    print("====================================")
    print("MoveC 원 운동 완료")
    print("====================================")
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("프로그램 오류 발생")
        print(e)
        try:
            indy.stop_motion()
        except Exception:
            pass