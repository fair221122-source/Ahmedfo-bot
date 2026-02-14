import os
import re
import telebot
from twelvedata import TDClient
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread
import pandas as pd

# --- Flask Server ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Live!"

def run():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# --- إعدادات البوت ---
def clean_env(value):
    return re.sub(r'[^\x20-\x7E]', '', value).strip() if value else None

TOKEN = clean_env(os.getenv("TELEGRAM_TOKEN"))
API_KEY = clean_env(os.getenv("TWELVE_DATA_API"))
bot = telebot.TeleBot(TOKEN)
td = TDClient(apikey=API_KEY)

FOREX_PAIRS = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'GBP/JPY', 'EUR/JPY', 'AUD/JPY', 'USD/CAD', 'EUR/GBP', 'GBP/AUD', 'CAD/JPY', 'CHF/JPY', 'EUR/CAD', 'GBP/CAD']

def analyze_logic(symbols):
    all_results = []
    for s in symbols:
        try:
            ts = td.time_series(symbol=s, interval="5min", outputsize=50)
            df = ts.as_pandas()
            if df is None or df.empty: continue
            df = df.sort_index(ascending=True)
            
            df['rsi'] = ta.rsi(df['close'], length=14)
            df['ema200'] = ta.ema(df['close'], length=200)
            
            last_row = df.iloc[-1]
            prev_row = df.iloc[-2]
            
            score = 60
            
            if last_row['close'] > last_row['open']:
                trend = "BUY"
                score += 15 if prev_row['close'] > prev_row['open'] else 5
            else:
                trend = "SELL"
                score += 15 if prev_row['close'] < prev_row['open'] else 5

            if trend == "BUY" and last_row['rsi'] > 70: score -= 20
            if trend == "SELL" and last_row['rsi'] < 30: score -= 20
            
            candle_body = abs(last_row['close'] - last_row['open'])
            upper_wick = last_row['high'] - max(last_row['close'], last_row['open'])
            lower_wick = min(last_row['close'], last_row['open']) - last_row['low']
            
            if trend == "BUY" and upper_wick > candle_body: score -= 15
            if trend == "SELL" and lower_wick > candle_body: score -= 15

            score = max(0, min(100, int(score)))

            if score >= 90:
                rank, trade_time = "ممتازة 🏆", "3 دقائق"
            elif 80 <= score < 90:
                rank, trade_time = "جيدة جداً ⭐", "3 دقائق"
            elif 70 <= score < 80:
                rank, trade_time = "جيدة ✅", "5 دقائق"
            elif 60 <= score < 70:
                rank, trade_time = "ضعيفة ⚠️", "10 دقائق"
            else:
                rank, trade_time = "ضعيفة (لا أنصح بالدخول) ❌", "10 دقائق"

            all_results.append({
                "pair": s, "trend": trend, "score": score, "rank": rank, 
                "time": trade_time, "price": last_row['close'], 
                "emoji": "🟢" if trend == "BUY" else "🔴"
            })
        except: continue
    return sorted(all_results, key=lambda x: x['score'], reverse=True)

@bot.message_handler(func=lambda message: message.text.isdigit() and 1 <= int(message.text) <= 13)
def handle_numbers(message):
    count = int(message.text)
    signals = analyze_logic(FOREX_PAIRS)
    top_signals = signals[:count]
    if not top_signals:
        bot.reply_to(message, "⚠️ لا توجد بيانات حالياً.")
        return
    for s in top_signals:
        send_formatted_msg(message.chat.id, s)

@bot.message_handler(func=lambda message: message.text.lower() == "gold")
def handle_gold(message):
    signals = analyze_logic(["XAU/USD"])
    if signals:
        send_formatted_msg(message.chat.id, signals[0])
    else:
        bot.reply_to(message, "⚠️ تعذر تحليل الذهب.")

def send_formatted_msg(chat_id, s):
    riyadh_time = datetime.utcnow() + timedelta(hours=3)
    msg = (f"{s['pair']}:\n"
           f"------------------------------------\n"
           f"{s['emoji']} الاتجاه: {s['trend']}\n💰 السعر: {s['price']:.5f}\n"
           f"قوة الإشارة: {s['rank']} {s['score']}%\n⏱️ الوقت: {s['time']}\n"
           f"📅 {riyadh_time.strftime('%Y-%m-%d | %I:%M:%S %p')}\n"
           f"---------------------------------------\n"
           f"GOOD LUCK AHMED 👍")
    bot.send_message(chat_id, msg)

if __name__ == "__main__":
    # تشغيل السيرفر في خلفية منفصلة
    t = Thread(target=run)
    t.daemon = True
    t.start()
    
    # حذف أي تعارض أو طلبات قديمة (Error 409)
    bot.remove_webhook()
    # تشغيل البوت مع تجاهل الطلبات المتراكمة
    bot.infinity_polling(skip_pending=True)
