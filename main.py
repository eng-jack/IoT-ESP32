#include <WiFi.h>
#include <DHT.h>
#include <LiquidCrystal_I2C.h>

// -------- Wi-Fi 設定 --------
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// -------- 感測器設定 --------
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);
#define LDR_PIN 34
#define FIRE_PIN 35
#define LED_PIN 2

// -------- LCD 初始化 --------
LiquidCrystal_I2C lcd(0x27, 16, 2);  // 如果沒顯示，請試 0x3F

// -------- Web Server --------
WiFiServer server(80);

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  lcd.begin();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Connecting WiFi");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi connected.");
  Serial.println(WiFi.localIP());
  lcd.clear();
  lcd.print("WiFi Ready");
  lcd.setCursor(0, 1);
  lcd.print(WiFi.localIP());

  server.begin();
}

void loop() {
  float temp = dht.readTemperature();
  float humi = dht.readHumidity();
  int light = analogRead(LDR_PIN);
  int fire = analogRead(FIRE_PIN);

  // 顯示在 LCD
  lcd.setCursor(0, 0);
  lcd.print("T:");
  lcd.print(temp, 1);
  lcd.print("C ");
  lcd.setCursor(0, 1);
  lcd.print("H:");
  lcd.print(humi, 1);
  lcd.print("%");

  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client Connected.");
    String req = client.readStringUntil('\r');
    client.read(); // '\n'
    Serial.println(req);

    // 控制 LED 開關
    if (req.indexOf("GET /LED=ON") >= 0) {
      digitalWrite(LED_PIN, HIGH);
    }
    if (req.indexOf("GET /LED=OFF") >= 0) {
      digitalWrite(LED_PIN, LOW);
    }

    // 建立回傳網頁
    client.println("HTTP/1.1 200 OK");
    client.println("Content-type:text/html\r\n");
    client.println("<!DOCTYPE html><html>");
    client.println("<head><meta charset='utf-8'><title>ESP32 控制面板</title></head>");
    client.println("<body>");
    client.println("<h1>ESP32 感測器資料</h1>");
    client.println("<p>溫度: " + String(temp) + " °C</p>");
    client.println("<p>濕度: " + String(humi) + " %</p>");
    client.println("<p>光照值: " + String(light) + "</p>");
    client.println("<p>火焰感測: " + String(fire) + "</p>");
    client.println("<hr>");
    client.println("<p><a href=\"/LED=ON\"><button>開啟 LED</button></a></p>");
    client.println("<p><a href=\"/LED=OFF\"><button>關閉 LED</button></a></p>");
    client.println("</body></html>");

    client.stop();
    Serial.println("Client disconnected.");
  }

  delay(2000);
}
