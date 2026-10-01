//const int buttonPin1 = 8;      //  8 번핀 스위치 입력 테스트 (PLC의 ready신호)
char LEDpin1 = 11;    //  OK LED 포트 설정
char LEDpin2 = 12;    //  NG
void setup() {
  Serial.begin(9600);              //  시리얼 통신의 시작, 보레이트 입력
  //pinMode(buttonPin1, INPUT);  //  스위치 내부풀업저항 입력포트로 셋팅.
  pinMode(LEDpin1, OUTPUT);           //  OK, NG LED 출력포트 지정.
  pinMode(LEDpin2, OUTPUT);}
void loop() {
  if(Serial.available())
  {
  char c = Serial.read();           //  PC로부터온 값을 읽음.
   if( c == 'A')
  { digitalWrite(LEDpin1, HIGH);  
    Serial.print("led1on\n");
  }
   else if( c == 'B')
  {  digitalWrite(LEDpin1, LOW); 
     Serial.print("led1off\n");}
 else if( c == 'C')
  {  digitalWrite(LEDpin2, HIGH); 
     Serial.print("led2on\n");}
  else if( c == 'D')
  {  digitalWrite(LEDpin2, LOW);    
     Serial.print("led2off\n");}
}
}
