import requests
import os
from datetime import datetime, timedelta
from twilio.rest import Client

# =====================
# FARM SETTINGS
# =====================
LAT = 17.0544053
LON = 74.6122866

HUM_MIN = 55
HUM_MAX = 75

# =====================
# SECRETS (FROM GITHUB)
# =====================
WEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]
TWILIO_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
FROM_WHATSAPP = os.environ["TWILIO_WHATSAPP_FROM"]
TO_WHATSAPP = os.environ["TWILIO_WHATSAPP_TO"]

client = Client(TWILIO_SID, TWILIO_TOKEN)


def get_weather():
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric"
    )
    data = requests.get(url, timeout=10).json()
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    return temp, humidity


def disease_risk(temp, hum):
    risks = []

    # 🌼 Chrysanthemum
    if hum > 70 and 18 <= temp <= 28:
        risks.append(
            "🌼 Chrysanthemum: HIGH risk (White rust, Leaf spot, Powdery mildew)"
        )

    # 🌹 Rose
    if hum > 75 and 20 <= temp <= 30:
        risks.append(
            "🌹 Rose: HIGH risk (Powdery mildew, Black spot, Downy mildew)"
        )

    return risks


def send_whatsapp(message):
    client.messages.create(
        body=message,
        from_=FROM_WHATSAPP,
        to=TO_WHATSAPP
    )


def is_daily_summary_time():
    # GitHub runs in UTC, IST = UTC + 5:30
    now_utc = datetime.utcnow()
    now_ist = now_utc + timedelta(hours=5, minutes=30)
    return now_ist.hour == 18  # 6 PM IST


def main():
    temp, hum = get_weather()
    now_utc = datetime.utcnow()
    now_ist = now_utc + timedelta(hours=5, minutes=30)

    message_parts = []

    # =====================
    # PRIORITY 1: DISEASE RISK
    # =====================
    risks = disease_risk(temp, hum)
    if risks:
        message_parts.append("🚨 Disease Risk Alert\n")
        message_parts.extend(risks)

    # =====================
    # PRIORITY 2: HUMIDITY ALERT
    # =====================
    if hum < HUM_MIN:
        message_parts.append(
            f"\n⚠️ Low Humidity Alert\nHumidity: {hum}% (Dry stress risk)"
        )
    elif hum > HUM_MAX:
        message_parts.append(
            f"\n⚠️ High Humidity Alert\nHumidity: {hum}% (Fungal risk)"
        )

    # =====================
    # PRIORITY 3: DAILY SUMMARY (6 PM IST)
    # =====================
    if is_daily_summary_time():
        message_parts.append(
            "\n📊 Daily Weather Summary – Sangli\n"
            f"🌡 Temperature: {temp}°C\n"
            f"💧 Humidity: {hum}%\n"
            "Advice:\n"
            "• Avoid late evening irrigation\n"
            "• Maintain air circulation\n"
            "• Monitor disease symptoms"
        )

    # =====================
    # SEND MESSAGE ONLY IF NEEDED
    # =====================
    if message_parts:
        final_message = (
            "📍 Farm Weather Alert (Sangli)\n"
            f"🕒 {now_ist.strftime('%d-%m-%Y %H:%M')}\n\n"
            + "\n".join(message_parts)
        )
        send_whatsapp(final_message)


if __name__ == "__main__":
    main()
