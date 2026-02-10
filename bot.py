from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_flask():
    app.run(host="0.0.0.0", port=10000)
threading.Thread(target=run_flask).start()

import requests
import telebot
import pandas as pd
import numpy as np
import time

# ============================
# ضع التوكن هنا
TELEGRAM_TOKEN = "8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# مفتاح TwelveData
API_KEY = "5a983de3d79043e9bfb2ec2e8618f905"
# ============================

# جميع الأزواج الأصلية بصيغة TwelveData
SYMBOLS = [
    "AUD/CAD","AUD/CHF","AUD/JPY","AUD/NZD","AUD/USD",
    "CAD/CHF","CAD/JPY","CHF/JPY",
    "EUR/CAD","EUR/CHF","EUR/GBP","EUR/JPY","EUR/USD",
    "GBP/AUD","GBP/CAD","GBP/CHF","GBP/JPY","GBP/NZD","GBP/USD",
    "NZD/CAD","NZD/CHF","NZD/JPY","NZD/USD",
    "USD/CAD","USD/CHF","USD/JPY",
    "XAU/USD"
]

# جلب الشموع من TwelveData
def get_candles(symbol):
    intervals = ["1min", "3min", "5min"]  # جرب 3 فواصل زمنية

    for interval in intervals:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=10&apikey={API_KEY}"

        try:
            r = requests.get(url, timeout=5).json()
        except Exception as e:
            print(f"API Error for {symbol} ({interval}):", e)
            continue

        if "values" not in r:
            print(f"{symbol} ({interval}) => no values")
            continue

        df = pd.DataFrame(r["values"])
        df["open"] = df["open"].astype(float)
        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)

        df = df.iloc[::-1]  # ترتيب الشموع
        print(f"{symbol} using interval {interval}")
        return df

    print(f"{symbol} => no interval worked")
    return None

# EMA20
def ema20(series):
    return series.ewm(span=20, adjust=False).mean().iloc[-1]

# تحليل الإشارة
def get_signal(symbol):
    df = get_candles(symbol)
    if df is None or len(df) < 20:
        return None

    closes = df["close"]
    opens = df["open"]

    current = closes.iloc[-1]
    ema = ema20(closes)

    trend_up = current > ema
    trend_down = current < ema

    # حساب الزخم
    bodies = (closes - opens).iloc[-15:]
    avg_body = np.mean(np.abs(bodies.iloc[:-1]))
    current_body = abs(closes.iloc[-1] - opens.iloc[-1])

    if avg_body == 0:
        avg_body = 0.00001

    momentum_score = current_body / avg_body

    # قوة الإشارة
    if momentum_score >= 1.8:
        strength = "قوية"
        trade_time = "1 دقيقة"
    elif momentum_score >= 1.2:
        strength = "متوسطة"
        trade_time = "3 دقائق"
    else:
        strength = "ضعيفة"
        trade_time = "5 دقائق"

    name = symbol.replace("/", "")

    if trend_up:
        msg = f"""🟢 {name}
📈 BUY
💰 {current}
💪 قوة الإشارة: {strength}
⏱️ الوقت: {trade_time}"""
        return {"msg": msg, "score": momentum_score}

    if trend_down:
        msg = f"""🔴 {name}
📉 SELL
💰 {current}
💪 قوة الإشارة: {strength}
⏱️ الوقت: {trade_time}"""
        return {"msg": msg, "score": momentum_score}

    return None

# ============================
# تشغيل البوت
# ============================
@bot.message_handler(commands=['signals', 'start'])
def handle(message):
    bot.send_message(message.chat.id, "جاري تحليل السوق…")

    results = []

    for s in SYMBOLS:
        res = get_signal(s)
        print(s, "=>", "Signal" if res else "No signal")
        if res:
            results.append(res)
        time.sleep(0.2)

    # ضمان 3 إشارات
    while len(results) < 3:
        results.append({
            "msg": "⚠️ لا توجد بيانات كافية لهذا الزوج",
            "score": 0
        })

    # أفضل 3 إشارات
    top3 = sorted(results, key=lambda x: x["score"], reverse=True)[:3]

    blocks = []
    for item in top3:
        blocks.append(item["msg"])
        blocks.append("-------------------")

    final_text = "🎯 أفضل 3 إشارات حالياً:\n\n" + "\n".join(blocks[:-1])
    bot.send_message(message.chat.id, final_text)

print("✅ البوت يعمل الآن باستخدام TwelveData + جميع الأزواج")

def run_bot():
    bot.infinity_polling()

bot_thread = threading.Thread(target=run_bot)
bot_thread.start()

app.run(host="0.0.0.0", port=10000)
