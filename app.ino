#include <ESP32Servo.h>

Servo myservoh;
Servo myservov;

int servopinh = 2;
int servopinv = 4;
int posh = 55;
int posv = 55;
int poshr;
int posvr;
char incoming;
unsigned long startMillis;
unsigned long currentMillis;
const unsigned long period = 30;

void controlServo(char dir){
  poshr = myservoh.read();
  posvr = myservov.read();
      
  switch(dir){
    default:
      break;
      
    case '1':
      myservoh.write(posh);
      currentMillis = millis();
      if(currentMillis - startMillis >= period) {
        if(poshr <= 120) posh++;
        startMillis = currentMillis;
        }
     break;
       
     case '2':      
      myservoh.write(posh);
      currentMillis = millis();
      if(currentMillis - startMillis >= period) {
        if(poshr >= 30) posh--;
        startMillis = currentMillis;
        }
     break;

     case '3':
      myservov.write(posv);
      currentMillis = millis();
      if(currentMillis - startMillis >= period) {
        if(posvr >= 30) posv--;
        startMillis = currentMillis;
        }
      break;

      case '4':
      myservov.write(posv);
      currentMillis = millis();
      if(currentMillis - startMillis >= period) {
        if(posvr <= 120) posv++;
        startMillis = currentMillis;
        }
      break;

      case '5':
      myservoh.write(posh);
      myservov.write(posv);
      currentMillis = millis();
      if(currentMillis - startMillis >= period) {
        if(poshr <= 120) posh++;
        if(posvr >= 30) posv--;
        startMillis = currentMillis;
        }
      break;

      case '6':
      myservoh.write(posh);
      myservov.write(posv);
      currentMillis = millis();
      if(currentMillis - startMillis >= period) {
        if(poshr <= 120) posh++;
        if(posvr <= 120) posv++;
        startMillis = currentMillis;
        }
      break;

      case '7':
      myservoh.write(posh);
      myservov.write(posv);
      currentMillis = millis();
      if(currentMillis - startMillis >= period) {
        if(poshr >= 30) posh--;
        if(posvr >= 30) posv--;
        startMillis = currentMillis;
        }
      break;

      case '8':
      myservoh.write(posh);
      myservov.write(posv);
      currentMillis = millis();
      if(currentMillis - startMillis >= period) {
        if(poshr >= 30) posh--;
        if(posvr <= 120) posv++;        
        startMillis = currentMillis;
        }
      break;              
  }
}

void setup() {
  Serial.begin(115200);
  myservoh.attach(servopinh);
  myservov.attach(servopinv);
  startMillis = millis();
  myservoh.write(posh);
  myservov.write(posv);
}
 

void loop(){
  if(Serial.available() > 0){
    incoming = char(Serial.read());
    controlServo(incoming);
    //this part is for check bytes and position of servos
    Serial.print("Byte: ");
    Serial.print(incoming);
    Serial.print(" Pos H: ");
    Serial.print(myservoh.read());
    Serial.print(" Pos V: ");
    Serial.println(myservov.read());
    Serial.flush();    
    }
}
