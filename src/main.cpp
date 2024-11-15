// Libraries
#include <DHT.h> // DHT22

// Pins
#define ledPin 23
#define btnKPin 19
#define btnPPin 18
#define relayPin 16
#define dhtPin 22
#define dhtType DHT22
#define ldrPin 34

//  DHT sensor
DHT dht(dhtPin, dhtType);

//  Default State
bool ledState = false;
bool btnPState = false;
bool btnKState = false;

// Function to validate sensor readings
bool validateSensors(float humidity, float temperature, float light) {
  return (humidity >= 30 && humidity <= 80) &&
         (temperature >= 10 && temperature <= 50) &&
         (light >= 0 && light <= 700);
}

// Function to control both LED and relay
void setOutputState(bool state)
{
  digitalWrite(relayPin, state ? HIGH : LOW);
  digitalWrite(ledPin, state ? HIGH : LOW);
}

// Setup
void setup()
{
  Serial.begin(9600); // Initialize serial communication

  pinMode(ledPin, OUTPUT);
  pinMode(btnKPin, INPUT_PULLUP);
  pinMode(btnPPin, INPUT_PULLUP);
  pinMode(relayPin, OUTPUT);
  pinMode(ldrPin, INPUT);
}

// Loop
void loop()
{
  // Read sensors
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  float light = analogRead(ldrPin);

  // Set LED and Relay according to button presses
  btnPState = !digitalRead(btnPPin);
  btnKState = !digitalRead(btnKPin);

  // Validate all conditions
  bool isValid = validateSensors(humidity, temperature, light);
  bool buttonActive = (btnPState || btnKState);

  // Print all data in JSON format
  Serial.print("{");
  Serial.print("\"sensors\":{");
  Serial.print("\"humidity\":");
  Serial.print(humidity);
  Serial.print(",\"temperature\":");
  Serial.print(temperature);
  Serial.print(",\"light\":");
  Serial.print(light);
  Serial.print("},");
  Serial.print("\"buttons\":{");
  Serial.print("\"btnP\":");
  Serial.print(btnPState ? "true" : "false");
  Serial.print(",\"btnK\":");
  Serial.print(btnKState ? "true" : "false");
  Serial.println("};");
  Serial.println("---");
  Serial.print("{\"validation\":{");
  Serial.print("\"sensorsValid\":");
  Serial.print(isValid ? "true" : "false");
  Serial.print(",\"buttonActive\":");
  Serial.print(buttonActive ? "true" : "false");
  Serial.println("};");
  Serial.println("===");

  // Only activate if both sensors are valid and a button is pressed
  setOutputState(isValid && buttonActive);

  delay(1000);
}
