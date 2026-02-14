import os
import re
import telebot
from twelvedata import TDClient
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

# --- إرضاء ريندر (Web Service) ---
app = Flask('')
@app.route('/')
def home(): 
    return "Bot is Live!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- إعدادات البوت المنظفة ---
def clean_env(value):
    if value:
        return re.sub(r'[^\x20-\x7E]', '', value).strip()
    return None

TOKEN = clean_env(os.getenv("TELEGRAM_TOKEN"))
API_KEY = clean_env(os.getenv("TWELVE_DATA_API"))

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is missing or invalid!")

bot = telebot.TeleBot(TOKEN)
td = TDClient(apikey=API_KEY)

FOREX_PAIRS = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'GBP/JPY', 'EUR/JPY', 'AUD/JPY', 'USD/CAD', 'EUR/GBP', 'GBP/AUD', 'CAD/JPY', 'CHF/JPY', 'EUR/CAD', 'GBP/CAD']

def analyze_logic(symbols):
    all_results = []
    for s in symbols:
        try:
            ts = td.time_series(symbol=s, interval="5min", outputsize=20)
            df = ts.as_pandas()
            if df is None or df.empty: 
                continue
            df = df.sort_index(ascending=True)
            
            recent_15 = df.iloc[-15:]
            last_4 = df.iloc[-4:]
            
            green = len(recent_15[recent_15['close'] > recent_15['open']])
            red = len(recent_15[recent_15['close'] < recent_15['open']])
            trend = "BUY" if green > red else "SELL"
            
            # حساب السكور
            score = int(((max(green, red)/15)*50) + (abs(last_4['close']-last_4['open']).sum()/(last_4['high']-last_4['low']).sum()*50))
            
            # --- التصنيف والوقت حسب طلبك ---
            if score >= 90:
                rank, trade_time = "ممتازة 🏆", "3 دقائق"
            elif score >= 80:
                rank, trade_time = "جيدة جداً ⭐", "3 دقائق"
            elif score >= 70:
                rank, trade_time = "جيدة ✅", "5 دقائق"
            else:
                rank, trade_time = "ضعيفة ⚠️", "10 دقائق"

            all_results.append({
                "pair": s, "trend": trend, "score": score, "rank": rank, 
                "time": trade_time, "price": df.iloc[-1]['close'], 
                "emoji": "🟢" if trend == "BUY" else "🔴"
            })
        except: 
            continue
    return sorted(all_results, key=lambda x: x['score'], reverse=True)[:3]

@bot.message_handler(func=lambda message: message.text == "1")
def handle_message(message):
    signals = analyze_logic(FOREX_PAIRS)
    if not signals:
        bot.reply_to(message, "⚠️ لا توجد إشارات حالياً.")
        return

    # استخدام أول وأقوى إشارة
    s = signals[0]
    riyadh_time = datetime.utcnow() + timedelta(hours=3)
    
    msg = (
        f"أفضل إشارة متوفرة حاليا:\n"
        f"------------------------------------\n"
        f"{s['emoji']} {s['pair']}\n"
        f"📈 {s['trend']}\n"
        f"💰 {s['price']:.5f}\n"
        f"قوة الإشارة: {s['rank']} {s['score']}%\n"
        f"⏱️ الوقت: {s['time']}\n"
        f"📅 {riyadh_time.strftime('%Y-%m-%d | %I:%M:%S %p')}\n"
        f"---------------------------------------\n"
        f"GOOD LUCK AHMED 👍"
    )
    bot.send_message(message.chat.id, msg)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
