#define windDir A0

int sensorExp[] = {66,84,93,126,184,244,287,406,461,599,630,702,785,827,886,945};
float dirDeg[]  = {112.5,67.5,90,157.5,135,202.5,180,22.5,45,247.5,225,337.5,0,292.5,315,270};
char* dirCard[] = {"ESE", "ENE", "E", "SSE", "SE", "SSW", "S", "NNE", "NE", "WSW", "SW", "NNW", "N", "WNW", "NW", "W"};

int sensorMin[] = {63,80,89,120,175,232,273,385,438,569,613,667,746,812,869,931};
int sensorMax[] = {69,88,98,133,194,257,301,426,484,612,661,737,811,868,930,993};

int incoming = 0;
float angle = 0;

void setup(){
  Serial.begin(9600);
}

void loop(){
  incoming = analogRead(windDir);

  for (int i=0; i<=15; i++) {
    if(incoming >= sensorMin[i] && incoming <= sensorMax[i]){
      angle = dirDeg[i];
      break;
    }
  }

  Serial.print(angle);
  Serial.println(":");
  delay(250);
}
