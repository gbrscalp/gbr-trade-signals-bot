import os
import threading
import time
import requests
from flask import Flask
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater, CallbackContext

TOKEN = "7976649472:AAFW5j66scpRAQKxrIakwarQ3WY-UCgrP2w"
COINS = ["PEPEUSDT", "WTCUSDT", "FARTCOINUSDT", "HOMEUSDT", "DOGEUSDT", "ADAUSDT", "XRPUSDT", "SOLUSDT"]
INTERVALS = ["5m", "1h"]

bot = Bot(token=TOKEN)
app = Flask(__name__)
user_chat_ids = set()

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
                msg = None
                if rsi >= 70:
                    msg = f"🔻 SHORT SIGNAL: {coin} RSI ({interval}) = {rsi}"
                elif rsi <= 20:
                    msg = f"🔺 LONG SIGNAL: {coin} RSI ({interval}) = {rsi}"
                if msg:
                    for chat_id in user_chat_ids:
                        try:
                            bot.send_message(chat_id=chat_id, text=msg)
                        except Exception as e:
                            print(f"Error: {e}")
        time.sleep(300)

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_chat_ids.add(chat_id)
   context.bot.send_message(chat_id=chat_id, text='✅ Bot aktywowany.')
Twój chat_id to: {chat_id}
Otrzymasz sygnały RSI.")

def keep_alive():
    while True:
        try:
            requests.get("https://gbr-trade-signals-bot-gwks.onrender.com/ping")
        except:
            pass
        time.sleep(240)

@app.route("/")
def home():
    return "Bot działa."

@app.route("/ping")
def ping():
    return "pong"

def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()

if __name__ == "__main__":
    threading.Thread(target=monitor).start()
    threading.Thread(target=keep_alive).start()
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)
