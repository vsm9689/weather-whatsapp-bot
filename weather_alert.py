import requests
import os
from datetime import datetime
from twilio.rest import Client

# =====================
# USER SETTINGS
# =====================
LAT = 17.0544053
LON = 74.6122866

HUM_MIN = 55
HUM_MAX = 75

# =====================
# SECRETS FROM GITHUB
# =====================
WEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]
TWILIO_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
FROM_WHATSAPP = os.environ["TWILIO_WHATSAPP_FROM"]
TO_WHATSAPP = os.environ["TWILIO_WHATSAPP_TO"]


def get_weather():
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric"
    )
    data = requests.get(url).json()
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    return temp, humidity


def disease_risk(crop, humidity):
    if crop == "chrysanthemum" and humidity > 70:
        return "⚠ High risk of Leaf Spot & Powdery Mildew"
    if crop == "rose" and humidity > 75:
        return "⚠ High risk of Black Spot & Downy Mildew"
    return "✅ Disease risk low"


def send_whatsapp(message):
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(
        body=message,
        from_=FROM_WHATSAPP,
        to=TO_WHATSAPP
    )


def main():
    temp, hum = get_weather()
    time = datetime.now().strftime("%d-%m-%Y %H:%M")

    alert = ""
    if hum < HUM_MIN or hum > HUM_MAX:
        alert = "🚨 HUMIDITY ALERT!"

    message = (
        "📍 Weather Report\n"
        f"🕒 {time}\n\n"
        f"🌡 Temperature: {temp}°C\n"
        f"💧 Humidity: {hum}%\n\n"
        f"{alert}\n\n"
        f"🌼 Chrysanthemum: {disease_risk('chrysanthemum', hum)}\n"
        f"🌹 Rose: {disease_risk('rose', hum)}"
    )

    send_whatsapp(message)


if __name__ == "__main__":
    main()
