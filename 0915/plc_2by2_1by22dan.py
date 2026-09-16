
# 2BY2_1BY22DAN
from neuromeka import IndyDCP3
from time import sleep
from pymcprotocol import Type3E
ROBOT_IP = "192.168.3.2"
indy = IndyDCP3(ROBOT_IP)
PLC_IP = "192.168.3.10"
PLC_PORT = 1026
plc = Type3E()
plc.connect(PLC_IP, PLC_PORT)
print("PLC 연결 성공")
SWITCH1 = "M100"   # 작업1 실행 신호
SWITCH2 = "M101"   # 작업2 실행 신호
DONE1 = "M110"     # 작업1 완료 신호
DONE2 = "M111"     # 작업2 완료 신호
print("로봇 연결 성공")
def move_done_check():
    print("이동 완료 대기...")
    indy.wait_for_motion_state(  "is_target_reached")
    print("이동 완료!")
# Grid 위치 생성
def generate_grid(base, grid_x,grid_y,offset_x, offset_y,layers=1,layer_h=0):
    coords = []
    for layer in range(layers):
        z = base[2] + layer * layer_h
        for i in range(grid_y):
            for j in range(grid_x):
                x = base[0] + j * offset_x
                y = base[1] + i * offset_y
                coords.append([x, y, z] )
    return coords
# 작업 1
# PICK 2×2 → PLACE 2×2
def task_pick2by2_place2by2():
    print("\n=== 작업1 시작: PICK 2×2 → PLACE 2×2 ==="  )
    PICK_BASE = [ 250.4689486, 333.77,  410.56    ]
    PLACE_BASE = [ 154.8543564, 326.10, 410.56    ]
    PICK_GRID_X = 2
    PICK_GRID_Y = 2
    PLACE_GRID_X = 2
    PLACE_GRID_Y = 2
    OFFSET_X = 40
    OFFSET_Y = 40
    RETRACT_Z = 50
    ROT_P = [ -175.85, 5.51,  169.58   ]
    ROT_R = [    1.96, -177.90, 3.90   ]
    # PICK 위치 생성
    pick_positions = generate_grid( PICK_BASE, PICK_GRID_X, PICK_GRID_Y, OFFSET_X, OFFSET_Y  )
    # PLACE 위치 생성
    place_positions = generate_grid(  PLACE_BASE, PLACE_GRID_X, PLACE_GRID_Y, OFFSET_X, OFFSET_Y    )
    # HOME 이동
    indy.move_home()
    move_done_check()
    # Pick & Place 반복
    for i in range(len(pick_positions)  ):
        pick = pick_positions[i]
        place = place_positions[i]
        print( f"\n>> STEP {i + 1}"  )
        # PICK 접근 위치
        indy.movel([ pick[0], pick[1], pick[2] + RETRACT_Z, *ROT_P  ] )
        move_done_check()
        # PICK 위치
        indy.movel([ pick[0], pick[1], pick[2],  *ROT_P  ]   )
        move_done_check()
        # 진공 ON
        indy.set_do( [ (2, True)  ]   )
        sleep(0.5)
        # PICK 상승
        indy.movel([pick[0], pick[1], pick[2] + RETRACT_Z, *ROT_P  ]  )
        move_done_check()
        # PLACE 접근 위치
        indy.movel( [ place[0], place[1], place[2] + RETRACT_Z, *ROT_R ] )
        move_done_check()
        # PLACE 위치
        indy.movel([place[0], place[1], place[2],*ROT_R  ]  )
        move_done_check()
        # 진공 OFF
        indy.set_do( [ (2, False)  ]   )
        sleep(0.5)
        # PLACE 상승
        indy.movel([ place[0], place[1],place[2] + RETRACT_Z, *ROT_R ] )
        move_done_check()
    # 작업 완료 후 HOME
    indy.move_home()
    move_done_check()
    print("작업1 완료")
# 작업 2
# PICK 1점 고정 → PLACE 1×2, 2단 팔레타이징
def task_pal_1by2_2layer():
    print("\n=== 작업2 시작: 1×2, 2단 팔레타이징 ==="   )
    PICK_BASE = [  250.468, 373.77,  413.56   ]
    PLACE_BASE = [  154.85,   321.60,   410.56    ]
    GRID_X = 1
    GRID_Y = 2
    NUM_LAYERS = 2
    OFFSET_X = 40
    OFFSET_Y = 40
    LAYER_H = 30
    RETRACT_Z = 50
    ROT_P = [ -175.85,  5.51,  169.58    ]
    ROT_R = [    1.96, -177.90,    3.90  ]
    # Place 좌표 생성
    place_positions = generate_grid( PLACE_BASE, GRID_X, GRID_Y,  OFFSET_X,
        OFFSET_Y,   NUM_LAYERS,    LAYER_H    )
    indy.move_home()
    move_done_check()
    # Palletizing
    for i, place in enumerate(place_positions    ):
        print(     f"\n>> STEP {i + 1}"     )
        # PICK 접근 위치
        indy.movel([ PICK_BASE[0], PICK_BASE[1],PICK_BASE[2] + RETRACT_Z,
                *ROT_P ]    )
        move_done_check()
        # PICK 위치
        indy.movel([ PICK_BASE[0], PICK_BASE[1], PICK_BASE[2], *ROT_P ] )
        move_done_check()
        # 진공 ON
        indy.set_do(  [  (2, True)   ]     )
        sleep(1)
        # PICK 상승
        indy.movel([ PICK_BASE[0],PICK_BASE[1],PICK_BASE[2] + RETRACT_Z,
                *ROT_P   ]      )
        # PLACE 접근 위치
        indy.movel([ place[0], place[1],place[2] + RETRACT_Z, *ROT_R ] )
        move_done_check()
        # PLACE 위치
        indy.movel([place[0], place[1], place[2],  *ROT_R  ]   )
        move_done_check()
        # 진공 OFF
        indy.set_do( [  (2, False)   ]    )
        sleep(1)
        # PLACE 상승
        indy.movel([place[0], place[1],place[2] + RETRACT_Z,*ROT_R ] )
        move_done_check()
    indy.move_home()
    move_done_check()
    print("작업2 완료")
print( "\n=== PLC 스위치 대기중… " "(스위치1=M100, 스위치2=M101) ===")
try:
    while True:
        # PLC 스위치 읽기
        sw1 = plc.batchread_bitunits(SWITCH1, 1 )[0]
        sw2 = plc.batchread_bitunits(SWITCH2, 1 )[0]
        # 스위치 1
        # M100 → 작업1 실행
        if sw1 == 1:
            print(   "\nM100 ON → 작업1 실행"       )
            task_pick2by2_place2by2()
            # 작업1 완료 신호 M110
            plc.batchwrite_bitunits( DONE1, [1]  )
            sleep(0.5)
            plc.batchwrite_bitunits( DONE1, [0]  )
            # M100 OFF 될 때까지 대기
            while plc.batchread_bitunits( SWITCH1,1 )[0] == 1:
                sleep(0.1)
        # 스위치 2
        # M101 → 작업2 실행
        if sw2 == 1:
            print("\nM101 ON → 작업2 실행"  )
            task_pal_1by2_2layer()
            # 작업2 완료 신호 M111
            plc.batchwrite_bitunits( DONE2,[1]   )
            sleep(0.5)
            plc.batchwrite_bitunits(DONE2,[0] )
            # M101 OFF 될 때까지 대기
            while plc.batchread_bitunits( SWITCH2,1 )[0] == 1:
                sleep(0.1)
        sleep(0.05)
except KeyboardInterrupt:
    print( "\n프로그램 종료" )
finally:
    plc.close()
    print( "연결 종료" )