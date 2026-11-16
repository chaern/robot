# Indy7 MQTT / PLC 제어 실습 (11월 16일)

Mosquitto MQTT 브로커를 이용해 PowerShell 또는 PLC에서 명령을 보내고, Python 프로그램이 명령을 해석해 Indy7을 제어하는 예제입니다.

## 구성

```text
PowerShell / PLC
       ↓
Mosquitto MQTT Broker (192.168.3.81:1883)
       ↓
mqttrobot.py 또는 mqttrobotplc.py
       ↓
Indy7
```

Mosquitto는 로봇을 직접 움직이지 않고 `indy7/command`와 `indy7/status` 메시지를 중계합니다.

## 네트워크 설정

| 장치 | IP / 포트 |
| --- | --- |
| MQTT 브로커 PC | `192.168.3.81:1883` |
| Indy7 (`mqttrobot.py`) | `192.168.3.6` |
| Indy7 (`mqttrobotplc.py`) | `192.168.3.2` |
| PLC | `192.168.3.100:1026` |

장비 구성에 따라 IP를 실제 주소로 수정해야 합니다.

## 설치

```powershell
python -m pip install paho-mqtt neuromeka pymcprotocol
```

Windows용 Mosquitto도 설치되어 있어야 합니다.

## Mosquitto 실행

이 폴더의 설정 파일을 사용합니다.

```powershell
& "C:\Program Files\Mosquitto\mosquitto.exe" -c ".\mosquitto.conf" -v
```

`mosquitto.conf`는 실습을 위해 익명 연결을 허용합니다. 신뢰할 수 없는 네트워크나 운영 환경에서는 계정과 비밀번호를 설정해야 합니다.

## Indy7 MQTT 프로그램 실행

```powershell
python .\mqttrobot.py
```

정상 연결 시 다음과 비슷하게 표시됩니다.

```text
Indy7 연결 완료
MQTT Broker 연결 중 : 192.168.3.81
MQTT Broker 연결 완료
구독 Topic = indy7/command
```

이후 출력이 멈춘 것처럼 보이는 것은 오류가 아니라 명령을 기다리는 정상 상태입니다.

## 명령 전송

로봇 주변의 사람과 장애물을 확인하고 비상정지 버튼을 사용할 수 있는 상태에서 실행합니다.

```powershell
& "C:\Program Files\Mosquitto\mosquitto_pub.exe" -h 192.168.3.81 -t "indy7/command" -m "POS1"
```

지원 명령:

| 명령 | 동작 |
| --- | --- |
| `HOME` | 홈 위치로 이동 |
| `POS1` | POS1 좌표로 이동 |
| `POS2` | POS2 좌표로 이동 |
| `VACUUM_ON` | 진공 출력 켜기 |
| `VACUUM_OFF` | 진공 출력 끄기 |

상태 메시지 확인:

```powershell
& "C:\Program Files\Mosquitto\mosquitto_sub.exe" -h 192.168.3.81 -t "indy7/status" -v
```

## PLC 통합 프로그램

```powershell
python .\mqttrobotplc.py
```

PLC 명령 주소는 `D100`, 결과 주소는 `D200`입니다.

| D100 | 명령 |
| ---: | --- |
| 1 | HOME |
| 2 | POS1 |
| 3 | POS2 |
| 4 | VACUUM_ON |
| 5 | VACUUM_OFF |

PLC가 꺼져 있거나 부팅 중이면 프로그램이 종료되지 않고 3초 간격으로 연결을 다시 시도하도록 수정했습니다.

## 문제 해결 기록

### `[WinError 10061] 연결을 거부했습니다`

Mosquitto가 기본 설정으로 `127.0.0.1:1883`에서만 수신하고 있었습니다. `mosquitto.conf`에서 `192.168.3.81:1883` 리스너를 열어 해결했습니다.

확인 명령:

```powershell
Test-NetConnection 192.168.3.81 -Port 1883
```

### PLC 연결 타임아웃

`192.168.3.100:1026`이 Ping과 ARP에 응답하지 않아 발생했습니다. 다음을 확인합니다.

- PLC 및 스위치의 LINK/ACT LED
- PLC의 실제 IP와 서브넷
- GX Works의 MC Protocol/SLMP TCP 포트 `1026` 설정
- 랜 케이블과 스위치 포트

### POS1 명령을 보냈지만 움직이지 않음

당시 로봇 현재 좌표가 POS1과 거의 동일해서 이동이 보이지 않았습니다. MQTT 명령 전달과 `POS1_MOVING`, `POS1_DONE` 발행은 정상적으로 처리되었습니다.

## 파일

- `mqttrobot.py`: MQTT 명령으로 Indy7 제어
- `mqttrobotplc.py`: MQTT와 PLC 명령을 함께 처리
- `mqttrobotplc.gxw`: GX Works 프로젝트
- `mosquitto.conf`: 실습용 MQTT 브로커 설정

