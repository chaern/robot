const int steps[4] = {2, 3, 4, 5};const int totalStepsCW = 128;
const int totalStepsCCW = 256; const int circle = 512;
int sw1=7,sw2=8;

void setup()
{
  for(int i=0;i<4;i++)
  {
    pinMode(steps[i],OUTPUT);
  }
  pinMode(sw1,INPUT);  pinMode(sw2,INPUT);
}

void moveMotorClockwise()
{
  for (int i = 0; i < totalStepsCW; i++)
  {
    for (int j = 0; j < 4; j++)
    {
      digitalWrite(steps[0], (j == 0) ? HIGH : LOW);
      digitalWrite(steps[1], (j == 1) ? HIGH : LOW);
      digitalWrite(steps[2], (j == 2) ? HIGH : LOW);
      digitalWrite(steps[3], (j == 3) ? HIGH : LOW);
      delay(10);
    }
  }
  stopMotor();
}

void moveMotorCounterClockwise() {
  for (int i = 0; i < totalStepsCCW; i++) {
    for (int j = 3; j >= 0; j--) {
      digitalWrite(steps[0], (j == 0) ? HIGH : LOW);
      digitalWrite(steps[1], (j == 1) ? HIGH : LOW);
      digitalWrite(steps[2], (j == 2) ? HIGH : LOW);
      digitalWrite(steps[3], (j == 3) ? HIGH : LOW);
      delay(10);
    }
  }
  stopMotor();
}

void stopMotor() {
  for (int k = 0; k < 4; k++)
    digitalWrite(steps[k], LOW);
}

void Clockwisef()
{
  for (int i = 0; i <circle ; i++) {
    for (int j = 0; j <= 3; j++) {
      digitalWrite(steps[0], (j == 0) ? HIGH : LOW);
      digitalWrite(steps[1], (j == 1) ? HIGH : LOW);
      digitalWrite(steps[2], (j == 2) ? HIGH : LOW);
      digitalWrite(steps[3], (j == 3) ? HIGH : LOW);
      delay(10);
    }
  }
  stopMotor();
}

void Clockwiser()
{
  for (int i = 0; i <circle ; i++) {
    for (int j = 3; j >= 0; j--) {
      digitalWrite(steps[0], (j == 0) ? HIGH : LOW);
      digitalWrite(steps[1], (j == 1) ? HIGH : LOW);
      digitalWrite(steps[2], (j == 2) ? HIGH : LOW);
      digitalWrite(steps[3], (j == 3) ? HIGH : LOW);
      delay(10);
    }
  }
  stopMotor();
}

void loop()
{
  sw1= digitalRead(7);    
  sw2= digitalRead(8);

  if(sw1==1)
  {
    moveMotorClockwise();        
    delay(1000);
    moveMotorCounterClockwise(); 
    delay(1000);
  }
  else if(sw2==1)
  {
    Clockwisef();        
    delay(1000);
    Clockwiser();        
    delay(1000);
  }
}