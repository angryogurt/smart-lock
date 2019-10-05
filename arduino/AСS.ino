#include <Wiegand.h>
#include <Adafruit_Fingerprint.h>

#define PIN_D0 2
#define PIN_D1 3

Wiegand wiegand;
SoftwareSerial mySerial(4, 5);

int ledPin = 6;
int val = 0;
int goReadFingerPin = 7;

Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

int fingerReadTime;

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(goReadFingerPin, INPUT);
  digitalWrite(ledPin, LOW);
  
  Serial.begin(9600);
  fingerReadTime = 0;
  
  wiegand.onReceive(receivedData, "Card readed: ");
  wiegand.onReceiveError(receivedDataError, "Card read error: ");
  wiegand.onStateChange(stateChanged, "State changed: ");
  wiegand.begin(Wiegand::LENGTH_ANY, true);
  
  pinMode(PIN_D0, INPUT);
  pinMode(PIN_D1, INPUT);
  
  attachInterrupt(digitalPinToInterrupt(PIN_D0), pinStateChanged, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_D1), pinStateChanged, CHANGE);
  
  finger.begin(57600);
  
  if (finger.verifyPassword()) {
    Serial.println("Found fingerprint sensor!");
  } else {
    Serial.println("Did not find fingerprint sensor :(");
    while (1) { delay(1); }
  }
  
  finger.getTemplateCount();
  Serial.print("Sensor contains "); Serial.print(finger.templateCount); Serial.println(" templates");
  Serial.println("Waiting for valid finger...");
  
  pinStateChanged();
}

void loop() {
  /*val = digitalRead(goReadFingerPin);
  digitalWrite(ledPin, val);
  if (val == HIGH) {
    digitalWrite(ledPin, HIGH);
    for (int i=0; i<100; i++) {
      getFingerprintID();
      delay(100);
    };
    digitalWrite(ledPin, LOW);
    Serial.println("Timeout reading finger");
  }
  else {
    noInterrupts();
    wiegand.flush();
    interrupts();
  };
  */
  getFingerprintID();
  delay(100);
}

void pinStateChanged() {
  wiegand.setPin0State(digitalRead(PIN_D0));
  wiegand.setPin1State(digitalRead(PIN_D1));
}

void stateChanged(bool plugged, const char* message) {
    Serial.print(message);
    Serial.println(plugged ? "CONNECTED" : "DISCONNECTED");
}

void receivedData(uint8_t* data, uint8_t bits, const char* message) {
    Serial.print(message);
    Serial.print(bits);
    Serial.print("bits / ");
    uint8_t bytes = (bits+7)/8;
    for (int i=0; i<bytes; i++) {
        Serial.print(data[i] >> 4, 16);
        Serial.print(data[i] & 0xF, 16);
    }
    Serial.println();
}

void receivedDataError(Wiegand::DataError error, uint8_t* rawData, uint8_t rawBits, const char* message) {
    Serial.print(message);
    Serial.print(Wiegand::DataErrorStr(error));
    Serial.print(" - Raw data: ");
    Serial.print(rawBits);
    Serial.print("bits / ");
    uint8_t bytes = (rawBits+7)/8;
    for (int i=0; i<bytes; i++) {
        Serial.print(rawData[i] >> 4, 16);
        Serial.print(rawData[i] & 0xF, 16);
    }
    Serial.println();
}

uint8_t getFingerprintID() {
  uint8_t p = finger.getImage();
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image taken");
      break;
    case FINGERPRINT_NOFINGER:
      Serial.println("No finger detected");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      return p;
    case FINGERPRINT_IMAGEFAIL:
      Serial.println("Imaging error");
      return p;
    default:
      Serial.println("Unknown error");
      return p;
  }
  p = finger.image2Tz();
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image converted");
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.println("Image too messy");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      return p;
    case FINGERPRINT_FEATUREFAIL:
      Serial.println("Could not find fingerprint features");
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.println("Could not find fingerprint features");
      return p;
    default:
      Serial.println("Unknown error");
      return p;
  }
  p = finger.fingerFastSearch();
  if (p == FINGERPRINT_OK) {
    Serial.println("Found a print match!");
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Communication error");
    return p;
  } else if (p == FINGERPRINT_NOTFOUND) {
    Serial.println("Did not find a match");
    return p;
  } else {
    Serial.println("Unknown error");
    return p;
  }
  Serial.print("Found ID #"); Serial.print(finger.fingerID); 
  // Serial.print(" with confidence of ");
  Serial.println(finger.confidence);
  return finger.fingerID;
}

int getFingerprintIDez() {
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK)  return -1;
  p = finger.image2Tz();
  if (p != FINGERPRINT_OK)  return -1;
  p = finger.fingerFastSearch();
  if (p != FINGERPRINT_OK)  return -1;
  Serial.print("Found ID #"); Serial.print(finger.fingerID); 
  Serial.print(" with confidence of "); Serial.println(finger.confidence);
  return finger.fingerID; 
}
