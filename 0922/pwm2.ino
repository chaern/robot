// DC Motor + Button + Potentiometer Control

const int ENABLE = 10;   // 모터 속도 제어 PWM
const int DIR1 = 9;      // 모터 방향 제어
const int DIR2 = 8;      // 모터 방향 제어

const int BUTTON = 3;    // 버튼
const int POT = A5;      // 가변저항

// 모터 상태
const int STOP = 0;
const int FORWARD_DIRECTION = 1;
const int BACKWARD_DIRECTION = 2;

int currentDirection = STOP;

// STOP 다음에 어느 방향으로 갈지 저장
int nextDirection = FORWARD_DIRECTION;


void setup()
{
  Serial.begin(9600);

  pinMode(ENABLE, OUTPUT);
  pinMode(DIR1, OUTPUT);
  pinMode(DIR2, OUTPUT);

  pinMode(BUTTON, INPUT);

  // 처음에는 모터 정지
  analogWrite(ENABLE, 0);
  digitalWrite(DIR1, LOW);
  digitalWrite(DIR2, LOW);

  Serial.println("=== DC Motor Control Start ===");
}


void loop()
{
  // 버튼을 눌렀을 때
  if (digitalRead(BUTTON) == HIGH)
  {
    delay(100);   // 채터링 방지

    // 버튼에서 손을 뗄 때까지 기다림
    while (digitalRead(BUTTON) == HIGH);

    delay(100);   // 채터링 방지


    // ==========================
    // 버튼을 누를 때마다 상태 변경
    // STOP -> FORWARD -> STOP
    // -> BACKWARD -> STOP ...
    // ==========================

    if (currentDirection == STOP)
    {
      currentDirection = nextDirection;
    }

    else if (currentDirection == FORWARD_DIRECTION)
    {
      currentDirection = STOP;
      nextDirection = BACKWARD_DIRECTION;
    }

    else if (currentDirection == BACKWARD_DIRECTION)
    {
      currentDirection = STOP;
      nextDirection = FORWARD_DIRECTION;
    }
  }


  // 가변저항 값 읽기 (0~1023)
  int pot_position = analogRead(POT);

  // PWM 값으로 변환 (0~255)
  int speed = map(pot_position, 0, 1023, 0, 255);


  // ==========================
  // 모터 동작
  // ==========================

  if (currentDirection == STOP)
  {
    analogWrite(ENABLE, 0);

    digitalWrite(DIR1, LOW);
    digitalWrite(DIR2, LOW);
  }

  else if (currentDirection == FORWARD_DIRECTION)
  {
    digitalWrite(DIR1, HIGH);
    digitalWrite(DIR2, LOW);

    analogWrite(ENABLE, speed);
  }

  else if (currentDirection == BACKWARD_DIRECTION)
  {
    digitalWrite(DIR1, LOW);
    digitalWrite(DIR2, HIGH);

    analogWrite(ENABLE, speed);
  }


  // ==========================
  // 시리얼 모니터 출력
  // ==========================

  Serial.print("POT = ");
  Serial.print(pot_position);

  Serial.print(" | PWM = ");
  Serial.print(speed);

  Serial.print(" | Direction = ");

  if (currentDirection == STOP)
  {
    Serial.println("STOP");
  }

  else if (currentDirection == FORWARD_DIRECTION)
  {
    Serial.println("FORWARD");
  }

  else if (currentDirection == BACKWARD_DIRECTION)
  {
    Serial.println("BACKWARD");
  }


  delay(200);
}