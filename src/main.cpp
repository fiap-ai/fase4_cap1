// Libraries
#include <DHT.h>           // DHT22 sensor
#include <Wire.h>          // I2C communication
#include <LiquidCrystal_I2C.h> // LCD display

// Pin Definitions
const uint8_t LED_PIN = 23;
const uint8_t BTN_K_PIN = 19;
const uint8_t BTN_P_PIN = 18;
const uint8_t RELAY_PIN = 16;
const uint8_t DHT_PIN = 15;  // Changed from 22 to avoid conflict with I2C
const uint8_t LDR_PIN = 34;
const uint8_t SDA_PIN = 21;  // I2C Data
const uint8_t SCL_PIN = 22;  // I2C Clock

// Constants for sensor validation
const uint8_t HUMIDITY_MIN = 30;
const uint8_t HUMIDITY_MAX = 80;
const int8_t TEMP_MIN = 10;
const int8_t TEMP_MAX = 50;
const uint16_t LIGHT_MIN = 0;
const uint16_t LIGHT_MAX = 700;

// LCD Configuration (0x27 is the default I2C address, adjust if needed)
LiquidCrystal_I2C lcd(0x27, 16, 2); // 16x2 LCD display

// DHT sensor configuration
DHT dht(DHT_PIN, DHT22);

// Global variables using optimized data types
struct {
    bool ledState = false;
    bool btnPState = false;
    bool btnKState = false;
    float humidity = 0.0f;
    float temperature = 0.0f;
    uint16_t light = 0;
    bool isValid = false;
    bool buttonActive = false;
} sensorData;

// Function prototypes
void initializeLCD();
void updateLCD();
bool validateSensors();
void setOutputState(bool state);
void readSensors();
void printJSONData();

void setup() {
    // Initialize serial communication
    Serial.begin(9600);
    
    // Initialize I2C and LCD
    Wire.begin(SDA_PIN, SCL_PIN);
    initializeLCD();
    
    // Initialize DHT sensor
    dht.begin();
    
    // Configure pins
    pinMode(LED_PIN, OUTPUT);
    pinMode(BTN_K_PIN, INPUT_PULLUP);
    pinMode(BTN_P_PIN, INPUT_PULLUP);
    pinMode(RELAY_PIN, OUTPUT);
    pinMode(LDR_PIN, INPUT);
}

void loop() {
    // Read all sensors
    readSensors();
    
    // Validate sensor readings
    sensorData.isValid = validateSensors();
    
    // Update outputs
    setOutputState(sensorData.isValid && sensorData.buttonActive);
    
    // Update LCD display
    updateLCD();
    
    // Print JSON data to serial
    printJSONData();
    
    // Delay for stability and LCD refresh rate
    delay(1000);
}

void initializeLCD() {
    lcd.init();
    lcd.backlight();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("FarmTech System");
    delay(2000);
    lcd.clear();
}

void updateLCD() {
    // First row: Temperature and Humidity
    lcd.setCursor(0, 0);
    lcd.print(String(sensorData.temperature, 1));
    lcd.print("C ");
    lcd.print(String(sensorData.humidity, 1));
    lcd.print("%");
    
    // Second row: Light and System Status
    lcd.setCursor(0, 1);
    lcd.print("L:");
    lcd.print(sensorData.light);
    lcd.print(" ");
    lcd.print(sensorData.isValid && sensorData.buttonActive ? "ON " : "OFF");
}

bool validateSensors() {
    return (sensorData.humidity >= HUMIDITY_MIN && sensorData.humidity <= HUMIDITY_MAX) &&
           (sensorData.temperature >= TEMP_MIN && sensorData.temperature <= TEMP_MAX) &&
           (sensorData.light >= LIGHT_MIN && sensorData.light <= LIGHT_MAX);
}

void setOutputState(bool state) {
    digitalWrite(RELAY_PIN, state ? HIGH : LOW);
    digitalWrite(LED_PIN, state ? HIGH : LOW);
}

void readSensors() {
    // Read DHT22 sensor
    sensorData.humidity = dht.readHumidity();
    sensorData.temperature = dht.readTemperature();
    
    // Read LDR sensor
    sensorData.light = analogRead(LDR_PIN);
    
    // Read buttons
    sensorData.btnPState = !digitalRead(BTN_P_PIN);
    sensorData.btnKState = !digitalRead(BTN_K_PIN);
    sensorData.buttonActive = (sensorData.btnPState || sensorData.btnKState);
}

void printJSONData() {
    // Print sensor data JSON
    Serial.print("{\"sensors\":{");
    Serial.print("\"humidity\":");
    Serial.print(sensorData.humidity);
    Serial.print(",\"temperature\":");
    Serial.print(sensorData.temperature);
    Serial.print(",\"light\":");
    Serial.print(sensorData.light);
    Serial.print("},\"buttons\":{");
    Serial.print("\"btnP\":");
    Serial.print(sensorData.btnPState ? "true" : "false");
    Serial.print(",\"btnK\":");
    Serial.print(sensorData.btnKState ? "true" : "false");
    Serial.println("}}");
    
    // Print validation data JSON
    Serial.print("{\"validation\":{");
    Serial.print("\"sensorsValid\":");
    Serial.print(sensorData.isValid ? "true" : "false");
    Serial.print(",\"buttonActive\":");
    Serial.print(sensorData.buttonActive ? "true" : "false");
    Serial.println("}}");
    
    // Print separator for serial plotter
    Serial.println("---");
    
    // Print data for serial plotter in CSV format
    Serial.print(sensorData.temperature);
    Serial.print(",");
    Serial.print(sensorData.humidity);
    Serial.print(",");
    Serial.println(sensorData.light);
}
