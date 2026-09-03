from neuromeka import IndyDCP3
import time
# 1. Indy7 연결
ROBOT_IP = "192.168.3.6"
indy = IndyDCP3(ROBOT_IP)
# 2. Waypoint 정의
#    Joint 좌표 [J1, J2, J3, J4, J5, J6]
#    단위 : degree
WAYPOINT1 = [0, 0, -90, 0, -90, 0]
WAYPOINT2 = [-30, 20, -70, 30, -80, -50]
WAYPOINT3 = [30, 10, -60, -20, -70, 40]
# 3. 이동 완료 확인 함수
def wait_move_done():
    print("이동 완료 대기 중...")
    while True:
        motion_data = indy.get_motion_data()
        movedone = motion_data['is_target_reached']
        print("movedone =", movedone)
        if movedone == True:
            break
        time.sleep(0.1)
    print("이동 완료!")
# 4. Home 이동
print("Home 이동")
indy.move_home()
wait_move_done()