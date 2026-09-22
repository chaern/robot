// DC Motor + Button + Potentiometer Control

const int ENABLE = 10;   // 모터 속도 제어 PWM
const int DIR1 = 9;      // 모터 방향 제어
const int DIR2 = 8;      // 모터 방향 제어

const int BUTTON = 3;    // 버튼
const int POT = A5;      // 가변저항

// 모터 상태
const int STOP = -1;
const int FORWARD_DIRECTION = 0;
const int BACKWARD_DIRECTION = 1;

int currentDirection = STOP;


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

    // 현재 상태에 따라 방향 변경
    if (currentDirection == STOP)
    {
      currentDirection = FORWARD_DIRECTION;
    }
    else if (currentDirection == FORWARD_DIRECTION)
    {
      currentDirection = BACKWARD_DIRECTION;
    }
    else
    {
      currentDirection = FORWARD_DIRECTION;
    }
  }


  // 가변저항 읽기
  int pot_position = analogRead(POT);

  // 0~1023 → 0~255로 변환
  int speed = map(pot_position, 0, 1023, 0, 255);


  // 모터 동작
  if (currentDirection == STOP)
  {
    analogWrite(ENABLE, 0);

    digitalWrite(DIR1, LOW);
    digitalWrite(DIR2, LOW);

    Serial.println("STOP");
  }

  else if (currentDirection == FORWARD_DIRECTION)
  {
    digitalWrite(DIR1, HIGH);
    digitalWrite(DIR2, LOW);

    analogWrite(ENABLE, speed);

    Serial.println("FORWARD");
  }

  else
  {
    digitalWrite(DIR1, LOW);
    digitalWrite(DIR2, HIGH);

    analogWrite(ENABLE, speed);

    Serial.println("BACKWARD");
  }

  delay(50);
}