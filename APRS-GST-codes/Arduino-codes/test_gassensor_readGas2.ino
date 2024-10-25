#include "DFRobot_MultiGasSensor.h"

// Enabled by default, use IIC communication at this time. Use UART communication when disabled
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

unsigned long previousMillis = 0;
const unsigned long interval = 5000; // 5 seconds interval

float gasConcentrationSum = 0.0;
int readingsCount = 0;

void setup() {
  Serial.begin(115200);

  while (!gas.begin()) {
    Serial.println("NO Devices !");
  }

  gas.setTempCompensation(gas.ON);
  gas.changeAcquireMode(gas.INITIATIVE);
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    if (gas.dataIsAvailable()) {
      // Add the gas concentration to the sum
      gasConcentrationSum += AllDataAnalysis.gasconcentration;
      readingsCount++;

      if (readingsCount >= 5) { // Print average every 5 seconds
        float averageGasConcentration = gasConcentrationSum / readingsCount;
        printGasData(averageGasConcentration);
        gasConcentrationSum = 0.0;
        readingsCount = 0;
      }
    }
  }
}

void printGasData(float gasConcentration) {
  Serial.println("========================");
  Serial.print("gastype:");
  Serial.println(AllDataAnalysis.gastype);
  Serial.println("------------------------");
  Serial.print("Average gas concentration:");
  Serial.print(gasConcentration);
  if (AllDataAnalysis.gastype.equals("O2"))
    Serial.println(" %VOL");
  else
    Serial.println(" PPM");
  Serial.println("------------------------");
  Serial.print("temp:");
  Serial.print(AllDataAnalysis.temp);
  Serial.println(" ℃");
  Serial.println("========================");
}
