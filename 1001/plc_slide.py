
from pymcprotocol import Type3E
from neuromeka import IndyDCP3
from time import sleep
PLC_IP = "192.168.3.100"
PLC_PORT = 1026
plc = Type3E()
plc.connect(PLC_IP, PLC_PORT)
print("MELSEC PLC 연결 성공")
ROBOT_IP = "192.168.3.2"
MOVE_VEL = 10
MOVE_ACC = 10
GRID_SIZE = 5
MAX_CELL = 25
CELL_PITCH = 40.0
APPROACH_HEIGHT = 50.0
VACUUM_DO = 2
indy = IndyDCP3(ROBOT_IP)
print("Indy7 DCP3 연결 성공")
# PLC → Python
START = "M100"
RESET = "M101"
# Python → PLC
DONE = "M200"
WORKING = "M201"
ERROR = "M202"
# Word 영역
MODE_ADDR = "D100"
X_ADDR = "D101"
Y_ADDR = "D102"
Z_ADDR = "D103"
PICK_ADDR = "D104"
# 선택모드 셀 번호
SELECT_ADDR = "D110"
# Python → PLC 결과
RESULT_ADDR = "D200"
pos_first = [15.748302, 321.56088, 404.73798,5.210189,179.86049,33.689323]
center = [108.16866,389.27124, 471.23288, 1.4016397, 178.99274,13.599214]
SLIDE_TARGET = [320.10547, 535.0671, 331.04337,-175.54137,-35.291645, 149.9351]
SLIDE_APPROACH = SLIDE_TARGET.copy()
SLIDE_APPROACH[2] += APPROACH_HEIGHT
SLIDE_RETRACT = SLIDE_TARGET.copy()
SLIDE_RETRACT[2] += APPROACH_HEIGHT
def read_bit(address):
    data = plc.batchread_bitunits( headdevice=address,  readsize=1  )
    return data[0]
def write_bit(address, value):
    plc.batchwrite_bitunits( headdevice=address, values=[value]    )
def read_word(address):
    data = plc.batchread_wordunits( headdevice=address, readsize=1    )
    return data[0]
def write_word(address, value):
    plc.batchwrite_wordunits( headdevice=address, values=[value]  )
# 로봇 이동 완료 확인
def motion_done_check():
    indy.wait_for_motion_state("is_target_reached"    )
# MoveL
def move_linear(target_position, name="MoveL"):
    print()
    print(name, "=", target_position)
    result = indy.movel(ttarget=target_position, vel_ratio=MOVE_VEL,acc_ratio=MOVE_ACC  )
    print("MoveL result =", result)
    motion_done_check()
# Vacuum ON
def vacuum_on():
    result = indy.set_do([{"address": VACUUM_DO, "state": True } ])
    print("Vacuum ON =", result)
    sleep(2)
# Vacuum OFF
def vacuum_off():
    result = indy.set_do([ { "address": VACUUM_DO, "state": False  } ])
    print("Vacuum OFF =", result)
    sleep(1)
# 셀 번호 → 좌표 계산
def cal_po(cell_number):
    if cell_number < 1 or cell_number > MAX_CELL:
        raise ValueError( f"잘못된 셀 번호입니다 : {cell_number}"  )
    cell_index = cell_number - 1
    row_index = cell_index // GRID_SIZE
    column_index = cell_index % GRID_SIZE
    x_distance = CELL_PITCH * row_index
    y_distance = CELL_PITCH * column_index
    selected_position = pos_first.copy()
    selected_position[0] += x_distance
    selected_position[1] += y_distance
    return selected_position
# Approach 좌표 생성
def make_approach(target_position):
    approach = target_position.copy()
    approach[2] += APPROACH_HEIGHT
    return approach
# GRID Pick
def pick_grid(cell_number):
    target = cal_po(cell_number)
    approach = make_approach(target)
    retract = make_approach(target)
    print()
    print("============================")
    print(f"GRID PICK : {cell_number}번 셀")
    print("============================")
    print("Approach =", approach)
    print("Target   =", target)
    print("Retract  =", retract)
    move_linear( approach, "Pick Approach"  )
    move_linear( target,   "Pick Target"    )
    vacuum_on()
    move_linear( retract, "Pick Retract"    )
# GRID Place
def place_grid(cell_number):
    target = cal_po(cell_number)
    approach = make_approach(target)
    retract = make_approach(target)
    print()
    print("============================")
    print(f"GRID PLACE : {cell_number}번 셀")
    print("============================")
    print("Approach =", approach)
    print("Target   =", target)
    print("Retract  =", retract)
    move_linear( approach,  "Place Approach"    )
    move_linear( target,    "Place Target"    )
    vacuum_off()
    move_linear( retract,   "Place Retract"    )
# 미끄럼틀 Pick
def pick_slide():
    print()
    print("============================")
    print("SLIDE PICK")
    print("============================")
    print("Approach =", SLIDE_APPROACH)
    print("Target   =", SLIDE_TARGET)
    print("Retract  =", SLIDE_RETRACT)
    move_linear(SLIDE_APPROACH,  "Slide Approach"    )
    move_linear(SLIDE_TARGET,  "Slide Target"    )
    vacuum_on()
    move_linear(SLIDE_RETRACT,  "Slide Retract"    )
# 셀 → 행/열
def get_row_col(cell_number):
    if cell_number < 1 or cell_number > MAX_CELL:
        raise ValueError("셀 번호는 1~25 사이여야 합니다.")
    index = cell_number - 1
    row = index // GRID_SIZE
    col = index % GRID_SIZE
    return row, col
# 행/열 → 셀
def row_col_to_cell(row, col):
    if row < 0 or row >= GRID_SIZE:
        raise ValueError(  "작업 위치가 5×5 작업판의 행을 초과합니다."   )
    if col < 0 or col >= GRID_SIZE:
        raise ValueError( "작업 위치가 5×5 작업판의 열을 초과합니다."   )
    return row * GRID_SIZE + col + 1
# 일반모드
# 작업판 → 작업판
def normal_grid_mode(x, y, z):
    start_row, start_col = get_row_col(z)
    if start_col + x > GRID_SIZE:
        raise ValueError( "한 줄 작업 개수가 작업판 범위를 초과합니다." )
    rows_needed = (y + x - 1) // x
    if start_row + rows_needed > GRID_SIZE:
        raise ValueError( "작업 범위가 25번 셀을 초과합니다."   )
    remaining = y
    for row_offset in range(rows_needed):
        cells_this_row = min( x, remaining )
        print()
        print( f"===== {row_offset + 1}행 작업 ====="   )
        for col_offset in range( cells_this_row - 1 ):
            pick_row = start_row + row_offset
            pick_col = ( start_col + col_offset     )
            place_col = pick_col + 1
            pick_cell = row_col_to_cell(pick_row, pick_col   )
            place_cell = row_col_to_cell( pick_row, place_col     )
            print()
            print(  f"{pick_cell}번 → {place_cell}번"      )
            pick_grid(pick_cell)
            place_grid(place_cell)
        remaining -= cells_this_row
# 일반모드
# 미끄럼틀 → 작업판
def normal_slide_mode(x, y, z):
    start_row, start_col = get_row_col(z)
    if start_col + x > GRID_SIZE:
        raise ValueError( "한 줄 작업 개수가 작업판 범위를 초과합니다."   )
    rows_needed = (y + x - 1) // x
    if start_row + rows_needed > GRID_SIZE:
        raise ValueError("작업 범위가 25번 셀을 초과합니다." )
    for i in range(y):
        row_offset = i // x
        col_offset = i % x
        row = start_row + row_offset
        col = start_col + col_offset
        place_cell = row_col_to_cell( row,   col  )
        print()
        print("============================")
        print(f"제품 {i + 1} / {y}")
        print("Place Cell =", place_cell)
        print("============================")
        pick_slide()
        place_grid(place_cell)
# D110 ~ D134
# D110 = 1
# D111 = 5
# D112 = 10
# D113 = 0

def selected_mode():
    print()
    print("PLC 선택모드 데이터 읽기")
    cell_data = plc.batchread_wordunits( headdevice=SELECT_ADDR, readsize=25  )
    place_info = []
    for value in cell_data:
        # 0을 만나면 선택 목록 종료
        if value == 0:
            break
        if 1 <= value <= MAX_CELL:
            place_info.append(value)
        else:
            raise ValueError( f"잘못된 선택 셀 번호 : {value}"    )
    if len(place_info) == 0:
        raise ValueError( "선택된 셀이 없습니다."        )
    print("선택한 셀 =", place_info)
    for index, cell_number in enumerate( place_info ):
        print()
        print( f"선택 작업 {index + 1}"    )
        print( "Place Cell =", cell_number   )
        pick_slide()
        place_grid( cell_number   )
def run_plc_command():
    # D100~D104를 한 번에 읽기
    command_data = plc.batchread_wordunits(headdevice="D100", readsize=5 )
    mode = command_data[0]
    x = command_data[1]
    y = command_data[2]
    z = command_data[3]
    start_po = command_data[4]
    print()
    print("PLC 작업 명령")
    print("D100 MODE =", mode)
    print("D101 X    =", x)
    print("D102 Y    =", y)
    print("D103 Z    =", z)
    print("D104 PICK =", start_po)
    if mode == 1:
        if x <= 0 or x > GRID_SIZE:
            raise ValueError( "한 줄 작업 개수는 1~5 사이여야 합니다."  )
        if y <= 0:
            raise ValueError( "총 작업 개수는 1 이상이어야 합니다."    )
        if z < 1 or z > MAX_CELL:
            raise ValueError( "시작 셀은 1~25 사이여야 합니다."  )
        if start_po == 1:
            print()
            print("작업판 → 작업판 모드")
            normal_grid_mode( x,  y,  z )
        elif start_po == 2:
            print()
            print("미끄럼틀 → 작업판 모드")
            normal_slide_mode( x, y,  z   )
        else:
            raise ValueError("D104는 1 또는 2이어야 합니다."    )
    elif mode == 2:
        print()
        print("선택 모드")
        selected_mode()
    else:
        raise ValueError( "D100 MODE는 1 또는 2이어야 합니다."   )
# PLC 상태 초기화
def reset_status():
    write_bit(DONE, 0)
    write_bit(WORKING, 0)
    write_bit(ERROR, 0)
    write_word(RESULT_ADDR, 0)
    print("PLC 상태 초기화 완료")
def main():
    print()
    print("PLC + Indy7 자동운전 프로그램")
    reset_status()
    vacuum_off()
    previous_start = 0
    try:
        while True:
            # RESET 확인
            reset_signal = read_bit(RESET)
            if reset_signal == 1:
                print()
                print("PLC RESET 신호")
                reset_status()
                vacuum_off()
                sleep(0.2)
                continue
            # START 읽기
            start_signal = read_bit(START)
            # M100 상승 Edge
            if ( start_signal == 1  and    previous_start == 0   ):
                print()
                print("================================")
                print("M100 START 감지")
                print("================================")
                # 작업 시작
                write_bit(DONE, 0)
                write_bit(ERROR, 0)
                write_bit(WORKING, 1)
                write_word( RESULT_ADDR,  0     )
                try:
                    run_plc_command()
                    print()
                    print( "===== 작업 종료 위치 이동 ====="  )
                    move_linear(  center,  "Center"    )
                    # 정상 완료
                    write_bit( WORKING,  0      )
                    write_bit( DONE,     1      )
                    write_word( RESULT_ADDR,   0    )
                    print()
                    print( "================================"    )
                    print(  "작업 정상 완료"  )
                    print(  "M200 DONE = ON" )
                    print( "================================"    )
                # 작업 중 오류
                except Exception as e:
                    print()
                    print("작업 오류 :",  e     )
                    try:
                        vacuum_off()
                    except:
                        pass
                    write_bit( WORKING,  0   )
                    write_bit( DONE,   0     )
                    write_bit( ERROR,   1    )
                    # 65535 = -1 표현
                    write_word( RESULT_ADDR,  65535   )
            # 이전 START 상태 저장
            previous_start = start_signal
            sleep(0.1)
    except KeyboardInterrupt:

        print()
        print("키보드 입력으로 프로그램 종료"  )
    except Exception as e:

        print()
        print(  "프로그램 오류 :",     e    )
    finally:
        try:
            vacuum_off()
        except Exception as e:
            print(  "Vacuum OFF 오류 :",   e   )
        try:
            write_bit(  WORKING,     0     )
        except:
            pass
        print()
        print("프로그램 종료")
if __name__ == "__main__":

    main()