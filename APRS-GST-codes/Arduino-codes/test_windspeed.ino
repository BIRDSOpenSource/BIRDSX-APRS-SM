const byte ledPin = 13;
const byte interruptPin = 2; //interruptPin now changed from 3 to 2
volatile byte state = LOW;

volatile uint32_t prev_mil = 0; //start measured time
volatile uint32_t cur_mil = 0;  //stop measured time

volatile int flag = 0;
//volatile bool flag = false;

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(interruptPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(interruptPin), blink, RISING);  //RISING is happened when the pulse of interrupt pin goes from low to high
  Serial.begin(115200);  
  prev_mil = millis();

  Serial.println("HIII");
}

void loop() 
{
  //digitalWrite(ledPin, state);
  if(flag == 1)
  {
    float sec = (float)(cur_mil-prev_mil)/1000; //1000 is to change from ms to s
    float _speed = 180 / sec;  //180 is the degree between 2 consecutive switch close (half turn)
    Serial.print(sec*2,3);  //*2 for full turn 
    Serial.println(" seconds per round");
    Serial.print(_speed,3);   // degree per second
    Serial.println(" degree per second");
    flag = 0;
    prev_mil = cur_mil;
  }
}

void blink()   //use blinking led to see whether variable state is correct or not
{
  cur_mil = millis();  //millis is the number of milisec passed
  flag = 1;
  state = !state;
  digitalWrite(ledPin, state);
}
