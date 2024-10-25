//This code will display Wind Direction and Gas results in a common interval, and display the AVERAGE Wind Speed results in another interval 

//-------------------WIND DIRECTION SETUP-----------------

#define windDir A0 // analogPin for wind direction    

int sensorExp[] = {66, 84, 93, 126, 184, 244, 287, 406, 461, 599, 630, 702, 785, 827, 886, 945};
float dirDeg[] = {112.5, 67.5, 90, 157.5, 135, 202.5, 180, 22.5, 45, 247.5, 225, 337.5, 0, 292.5, 315, 270};
char* dirCard[] = {"ESE", "ENE", "E", "SSE", "SE", "SSW", "S", "NNE", "NE", "WSW", "SW", "NNW", "N", "WNW", "NW", "W"};

int sensorMin[] = {63, 80, 89, 120, 175, 232, 273, 385, 438, 569, 613, 667, 746, 812, 869, 931};
int sensorMax[] = {69, 88, 98, 133, 194, 257, 301, 426, 484, 612, 661, 737, 811, 868, 930, 993};

int incoming = 0;
float angle = 0;

//-------------------WIND SPEED SETUP-----------------

const byte ledPin = 13;
const byte interruptPin = 2; // interruptPin now changed from 3 to 2
volatile byte state = LOW;

volatile uint32_t prev_mil = 0; // start measured time
volatile uint32_t cur_mil = 0;  // stop measured time

volatile int flag = 0;

const float radius = 0.091; // metre

//-------------------GAS SETUP-----------------
#include "DFRobot_MultiGasSensor.h"

//Enabled by default, use IIC communication at this time. Use UART communication when disabled
#define I2C_COMMUNICATION

#ifdef I2C_COMMUNICATION
#define I2C_ADDRESS 0x74
DFRobot_GAS_I2C gas(&Wire, I2C_ADDRESS);
#else
#if (!defined ARDUINO_ESP32_DEV) && (!defined __SAMD21G18A__)
/**
  UNO:pin_2-----RX
      pin_3-----TX
*/
SoftwareSerial mySerial(2, 3);
DFRobot_GAS_SoftWareUart gas(&mySerial);
#else
/**
  ESP32:IO16-----RX
        IO17-----TX
*/
DFRobot_GAS_HardWareUart gas(&Serial2); //ESP32HardwareSerial
#endif
#endif

//----------------- THERMAL SETUP------------------------
#include <Wire.h>
#include <Adafruit_MLX90614.h>

Adafruit_MLX90614 mlx = Adafruit_MLX90614();


//----------------- MEASUREMENT SETUP-----------------

void setup() {

  //--------------Wind Speed Setup--------------------
  pinMode(ledPin, OUTPUT);
  pinMode(interruptPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(interruptPin), blink, RISING); // RISING is happened when the pulse of interrupt pin goes from low to high
  Serial.begin(9600);
  prev_mil = millis();
  
//  Serial.println("HIII");

  //--------------Gas Setup--------------------
  while(!gas.begin())
  {
    Serial.println("NO Devices !");
  }

  gas.setTempCompensation(gas.ON);  
  gas.changeAcquireMode(gas.INITIATIVE);

  //--------------Thermal Setup-------------------- 
  mlx.begin(); 
}

// Define a common update interval for wind direction data
const unsigned long updateInterval = 10000; // 1000ms = 1 second
unsigned long lastUpdate = 0;

// Variables for calculating average wind speed
float windSpeedSum = 0.0;
int windSpeedCount = 0;
unsigned long windSpeedLastPrint = 0;

// Variables for calculating average data
//float windDirectionSum = 0.0;
float gasConcentrationSum = 0.0;
float thermalDataSum = 0.0;
int dataCount = 0;

// Define a print interval for average data
const unsigned long printInterval = 10000; // 30 seconds
unsigned long lastPrint = 0;


//----------------- MEASUREMENT EXECUTION-----------------

// Define a trend recording interval for temperature and gas concentration
const unsigned long trendInterval = 10000; // 10 seconds
unsigned long lastTrendRecord = 0;

// Variables for recording trend
float lastTemperature = 0.0;
float lastGasConcentration = 0.0;

void loop()
{
  unsigned long currentMillis = millis();
  unsigned long currentMillis_ws = millis();
  
  // Wind direction, Gas, and Thermal data are sampled every 1 second
  if (currentMillis - lastUpdate >= updateInterval) {
    lastUpdate = currentMillis;

    //-------------Wind direction----------
    incoming = analogRead(windDir);
    for (int i = 0; i <= 15; i++) {
      if (incoming >= sensorMin[i] && incoming <= sensorMax[i]) {
        angle = dirDeg[i];
        break;
      }
    }
    if (angle >= 0 && angle <= 9) {
      Serial.print("00");
    } 
    else if (angle >= 10 && angle <= 99) {
      Serial.print("0");
    }
    Serial.print(int(angle));
    Serial.print("/");

  
  //-------------Gas ----------------------
    if(true==gas.dataIsAvailable())
      {
//        Serial.print("G");
//        Serial.print(AllDataAnalysis.gasconcentration); Serial.print(";");
          gasConcentrationSum += AllDataAnalysis.gasconcentration;
      }

      //-------------Thermal----------------------
//      Serial.print("T");
//      Serial.print(mlx.readAmbientTempC()); Serial.println(";");
        thermalDataSum += mlx.readAmbientTempC();
    
        dataCount++;
  }

  // Print the average data after 30 seconds
  if (currentMillis - lastPrint >= printInterval) {
    lastPrint = currentMillis;
    Serial.print("g000");
    if (dataCount > 0) {

      Serial.print("t");
      if (thermalDataSum / dataCount >= 0 && thermalDataSum / dataCount <= 9) {
      Serial.print("00");
    } 
    else if (thermalDataSum / dataCount >= 10 && thermalDataSum / dataCount <= 99) {
      Serial.print("0");
    }
      Serial.print(int(thermalDataSum / dataCount));
      
      Serial.print("g");
      Serial.print(gasConcentrationSum / dataCount);
      Serial.print("ta");
      Serial.println(thermalDataSum / dataCount);
     
    }

    // Reset the sum and count for the next 30-second interval
    gasConcentrationSum = 0.0;
    thermalDataSum = 0.0;
    dataCount = 0;
  }

  // Record trend every 120 seconds
      if (currentMillis - lastTrendRecord >= trendInterval) {
        lastTrendRecord = currentMillis;
        float temperatureChange = mlx.readAmbientTempC() - lastTemperature;
        float gasConcentrationChange = (gasConcentrationSum / dataCount) - lastGasConcentration;
        
//        if (temperatureChange > 0 )
//           Serial.println("Temperature increased !");
//        else if (temperatureChange < 0 )
//           Serial.println("Temperature decreased !");

//        if (gasConcentrationChange > 0 )
//           Serial.println("SO2 density increased !");
//        else if (gasConcentrationChange < 0 )
//           Serial.println("SO2 density decreased !");

//        Serial.print("Temperature Change=");
//        Serial.print(temperatureChange);
//        Serial.print(", Gas Concentration Change=");
//        Serial.println(gasConcentrationChange);

        // Update last recorded values
        lastTemperature = mlx.readAmbientTempC();
        lastGasConcentration = gasConcentrationSum / dataCount;
      }

   //-------------Wind speed----------
    if (flag == 1) {
    float sec = (float)(cur_mil - prev_mil) / 1000; // 1000 is to change from ms to s
    float _speed = 180 / sec; // 180 is the degree between 2 consecutive switch close (half turn)
    float linearSpeed = (_speed / 180) * PI * radius; // metres per second
    windSpeedSum += linearSpeed; // Add the current reading to the sum
    windSpeedCount++; // Increment the count of readings

    if (currentMillis_ws - windSpeedLastPrint >= 10000) {
      // Print the average wind speed every 5 seconds
      float avgWindSpeed = windSpeedSum / windSpeedCount;
      
      if (round(avgWindSpeed) >= 0 && round(avgWindSpeed) <= 9) {
          Serial.print("00");
      }
      else if (round(avgWindSpeed) >= 10 && round(avgWindSpeed) <= 99)  {
          Serial.print("0");
      }
      
      Serial.println(round(avgWindSpeed * 1.943844)); // knot

      Serial.println(avgWindSpeed);
      
      // Reset the sum and count for the next 5-second interval
      windSpeedSum = 0.0;
      windSpeedCount = 0;
      windSpeedLastPrint = currentMillis_ws;
    }

    flag = 0;
    prev_mil = cur_mil;
  }
  
}

//----------------- CHECK OUT INTERRUPT PIN STATUS (FOR WIN SPEED MEAS) ------------
void blink() {
  cur_mil = millis();
  flag = 1;
  state = !state;
  digitalWrite(ledPin, state);
}
