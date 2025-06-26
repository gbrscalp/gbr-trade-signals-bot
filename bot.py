import threading
import time
import requests
import os
from flask import Flask
from telegram import Bot
from datetime import datetime

app = Flask(__name__)

TELEGRAM_TOKEN = "7976649472:AAFW5j66scpRAQKxrIakwarQ3WY-UCgrP2w"
CHAT_ID = None  # jeśli potrzebujesz na sztywno, wstaw tutaj ID

bot = Bot(token=TELEGRAM_TOKEN)

# Lista coinów i interwałów do sprawdzania RSI
COINS = ["PEPEUSDT", "WTCUSDT", "FARTCOINUSDT", "HOMEUSDT", "DOGEUSDT", "ADAUSDT", "XRPUSDT", "SOLUSDT"]
INTERVALS = ["5m", "1h"]

def get_rsi(symbol, interval):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=14"
        data = requests.get(url).json()
        closes = [float(x[4]) for x in data]
        gains = [max(closes[i+1] - closes[i], 0) for i in range(len(closes)-1)]
        losses = [max(closes[i] - closes[i+1], 0) for i in range(len(closes)-1)]
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
    except:
        return None

def monitor():
    while True:
        for coin in COINS:
            for interval in INTERVALS:
                rsi = get_rsi(coin, interval)
                if rsi is None:
                    continue
                message = None
                if rsi >= 80:
                    message = f"🔻 SHORT SIGNAL: {coin} RSI ({interval}) = {rsi}"
                elif rsi <= 20:
                    message = f"🔺 LONG SIGNAL: {coin} RSI ({interval}) = {rsi}"
                if message:
                    try:
                        bot.send_message(chat_id=CHAT_ID or "@yourchannel", text=message)
                    except Exception as e:
                        print(f"Error sending message: {e}")
        time.sleep(300)

@app.route("/")
def home():
    return f"Bot is running. {datetime.utcnow()}"

@app.route("/ping")
def ping():
    return f"pong {datetime.utcnow()}"

def keep_alive():
    while True:
        try:
            requests.get("https://gbr-trade-signals-bot.onrender.com/ping")
        except:
            pass
        time.sleep(240)

if __name__ == "__main__":
    threading.Thread(target=monitor).start()
    threading.Thread(target=keep_alive).start()
    app.run(host="0.0.0.0", port=10000)
