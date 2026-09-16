
from pymcprotocol import Type3E
import time
PLC_IP = "192.168.3.130"
PLC_PORT = 1026
MAX_LENGTH = 20
plc = Type3E()
try:
    plc.connect(PLC_IP, PLC_PORT)
    print("PLC 연결 성공")
    while True:
        print()
        print("=" * 50)
        message = input("PLC로 보낼 문자를 입력하세요 (종료: exit) : " )
        if message.lower() == "exit":
            print("프로그램을 종료합니다.")
            break
        if len(message) == 0:
            print("문자를 입력하세요.")
            continue
        if len(message) > MAX_LENGTH:
            print(f"최대 {MAX_LENGTH}자까지 입력할 수 있습니다.")
            continue
        # 문자 → ASCII 코드
        try:
            send_data = [ord(c) for c in message]
        except Exception as e:
            print("문자 변환 오류 :", e)
            continue
        length = len(send_data)
        print()
        print("전송 문자열 :", message)
        print("문자 개수   :", length)
        print("전송 데이터 :", send_data)
        # 이전 Handshake 초기화
        plc.batchwrite_bitunits(headdevice="M100", values=[0] )
        time.sleep(0.1)
        # D90에 문자 개수 기록
        plc.batchwrite_wordunits( headdevice="D90",  values=[length]    )
        # D100부터 문자 데이터 기록
        plc.batchwrite_wordunits( headdevice="D100", values=send_data   )
        print("Python → PLC 데이터 전송 완료")
        # 실제 PLC에 들어갔는지 확인
        check_data = plc.batchread_wordunits( headdevice="D100",readsize=length     )
        print("D100 데이터 :", check_data)
        # M100 ON
        # PLC에게 처리 요청
        plc.batchwrite_bitunits( headdevice="M100", values=[1]    )
        print("M100 ON → PLC 처리 요청")
        # M101 응답 대기
        timeout = 5.0
        start_time = time.time()
        while True:
            done = plc.batchread_bitunits(headdevice="M101", readsize=1  )
            if done[0] == 1:
                print("M101 ON → PLC 응답 완료")
                break
            if time.time() - start_time > timeout:
                raise TimeoutError( "PLC 응답(M101) 대기 시간 초과"   )
            time.sleep(0.1)
        # PLC가 반환한 문자 개수 읽기
        receive_length = plc.batchread_wordunits( headdevice="D90",readsize=1  )[0]
        # D200부터 반환 데이터 읽기
        receive_data = plc.batchread_wordunits( headdevice="D200", readsize=receive_length     )
        print("PLC 반환 데이터 :", receive_data)
        # ASCII → 문자
        receive_message = ''.join(chr(value) for value in receive_data )
        print()
        print("Python → PLC :", message)
        print("PLC → Python :", receive_message)
        # M100 OFF
        plc.batchwrite_bitunits(headdevice="M100", values=[0]     )
        print("M100 OFF")
        # PLC가 M101을 Reset할 시간
        time.sleep(0.2)
except Exception as e:
    print()
    print("통신 오류 :", e)
finally:
    try:
        plc.close()
        print("PLC 연결 종료")
    except:
        pass

# Network 1 : Python 요청 처리

#      M100        M101
# ----| |---------|/|-------------[ BMOV D100 D200 K20 ]
#                     |
#                     +------------[ SET M101 ]


# Network 2 : Handshake Reset

#      M100
# ----|/|--------------------------[ RST M101 ]