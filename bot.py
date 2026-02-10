import os
from flask import Flask
import threading
import requests
import telebot
import pandas as pd
import numpy as np
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_flask():
    # الحل هنا: قراءة المنفذ من متغيرات البيئة الخاصة بـ Render
    port = int(os.environ.get("PORT", 10000))
    # استماع على 0.0.0.0 ضروري جداً للمنصات السحابية
    app.run(host="0.0.0.0", port=port)

# تشغيل Flask في خيط منفصل
threading.Thread(target=run_flask, daemon=True).start()

# ============================
# إعدادات البوت والعملات
# ============================
TELEGRAM_TOKEN = "8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

API_KEY = "5a983de3d79043e9bfb2ec2e8618f905"

# قائمة العملات المستخرجة من الصور (بدون تكرار وبالتنسيق المطلوب)
SYMBOLS = [
    "AUD/CAD", "AUD/CHF", "AUD/JPY", "AUD/NZD", "AUD/USD",
    "CAD/CHF", "CAD/JPY", "CHF/JPY", "EUR/AUD", "EUR/CAD",
    "EUR/CHF", "EUR/GBP", "EUR/JPY", "EUR/NZD", "EUR/USD",
    "GBP/AUD", "GBP/CAD", "GBP/JPY", "GBP/NZD", "GBP/USD",
    "NZD/CHF", "NZD/JPY", "NZD/USD", "USD/CAD", "USD/CHF", "USD/JPY"
]

# ============================
# دالة جلب البيانات
# ============================
def get_candles(symbol):
    intervals = ["1min", "3min", "5min"]
    for interval in intervals:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=15&apikey={API_KEY}"
        try:
            r = requests.get(url, timeout=7).json()
            if "values" in r and r["values"]:
                df = pd.DataFrame(r["values"])
                for col in ["open", "close", "high", "low"]:
                    df[col] = df[col].astype(float)
                return df.iloc[::-1]
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            continue
    return None

def ema20(series):
    return series.ewm(span=20, adjust=False).mean().iloc[-1]

# ============================
# تحليل الإشارة
# ============================
def get_signal(symbol):
    df = get_candles(symbol)
    if df is None or len(df) < 10:
        return None

    closes = df["close"]
    opens = df["open"]
    current = closes.iloc[-1]
    
    # حساب EMA بسيط للاتجاه
    ema = closes.mean() 
    trend_up = current > ema
    trend_down = current < ema

    # حساب المومنتوم (الزخم)
    bodies = (closes - opens).iloc[-10:]
    avg_body = np.mean(np.abs(bodies.iloc[:-1])) + 0.00001
    current_body = abs(closes.iloc[-1] - opens.iloc[-1])
    momentum_score = current_body / avg_body

    if momentum_score >= 1.8:
        strength, trade_time = "قوية 💪", "1 min"
    elif momentum_score >= 1.2:
        strength, trade_time = "متوسطة ⚡", "3 min"
    else:
        strength, trade_time = "ضعيفة ⚠️", "5 min"

    name = symbol.replace("/", "")
    if trend_up:
        msg = f"🟢 {name}\n📈 BUY\n💰 Price: {current}\n💪 Signal: {strength}\n⏱️ Time: {trade_time}"
        return {"msg": msg, "score": momentum_score}
    elif trend_down:
        msg = f"🔴 {name}\n📉 SELL\n💰 Price: {current}\n💪 Signal: {strength}\n⏱️ Time: {trade_time}"
        return {"msg": msg, "score": momentum_score}
    return None

# ============================
# تشغيل أوامر التلجرام
# ============================
@bot.message_handler(commands=['signals', 'start'])
def handle(message):
    bot.send_message(message.chat.id, "🔍 جاري فحص السوق وتحليل أفضل الفرص...")
    results = []
    for s in SYMBOLS:
        res = get_signal(s)
        if res: results.append(res)
        time.sleep(0.1) # لتجنب ضغط الـ API

    if not results:
        bot.send_message(message.chat.id, "السوق حالياً هادئ جداً، لا توجد إشارات قوية.")
        return

    top3 = sorted(results, key=lambda x: x["score"], reverse=True)[:3]
    final_text = "🎯 أفضل 3 إشارات حالياً:\n\n" + "\n\n---\n\n".join([item["msg"] for item in top3])
    bot.send_message(message.chat.id, final_text)

def run_bot():
    print("✅ البوت يعمل الآن ويراقب السوق...")
    bot.infinity_polling()

if __name__ == "__main__":
    # تشغيل البوت في الخيط الرئيسي
    run_bot()
