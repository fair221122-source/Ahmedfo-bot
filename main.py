import os
import telebot
from twelvedata import TDClient
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

# --- إرضاء ريندر (Web Service) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Live!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- إعدادات البوت ---
TOKEN = os.getenv("8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0")
API_KEY = os.getenv("5a983de3d79043e9bfb2ec2e8618f905")
bot = telebot.TeleBot(TOKEN)
td = TDClient(apikey=API_KEY)

FOREX_PAIRS = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'GBP/JPY', 'EUR/JPY', 'AUD/JPY', 'USD/CAD', 'EUR/GBP', 'GBP/AUD', 'CAD/JPY', 'CHF/JPY', 'EUR/CAD', 'GBP/CAD']

def analyze_logic(symbols):
    all_results = []
    for s in symbols:
        try:
            ts = td.time_series(symbol=s, interval="5min", outputsize=20)
            df = ts.as_pandas()
            if df is None or df.empty: continue
            df = df.sort_index(ascending=True)
            
            recent_15 = df.iloc[-15:]
            last_4 = df.iloc[-4:]
            
            green = len(recent_15[recent_15['close'] > recent_15['open']])
            red = len(recent_15[recent_15['close'] < recent_15['open']])
            trend = "BUY" if green > red else "SELL"
            
            score = int(((max(green, red)/15)*50) + (abs(last_4['close']-last_4['open']).sum()/(last_4['high']-last_4['low']).sum()*50))
            
            all_results.append({"pair": s, "trend": trend, "score": score, "price": df.iloc[-1]['close'], "emoji": "🟢" if trend == "BUY" else "🔴"})
        except: continue
    return sorted(all_results, key=lambda x: x['score'], reverse=True)[:1] # يجلب الأفضل فقط

@bot.message_handler(func=lambda m: m.text.isdigit() or m.text.lower() == 'gold')
def handle_request(message):
    symbols = ['GOLD'] if message.text.lower() == 'gold' else FOREX_PAIRS
    signals = analyze_logic(symbols)
    
    if not signals:
        bot.reply_to(message, "⚠️ فشل جلب البيانات. تأكد من إعدادات TwelveData و Render.")
        return

    s = signals[0]
    riyadh_time = datetime.utcnow() + timedelta(hours=3)
    label = "ممتازة" if s['score'] >= 85 else "جيدة"
    
    msg = (f"أفضل إشارة متوفرة حاليا:\n------------------------------------\n"
           f"{s['emoji']} {s['pair']}\n📈 {s['trend']}\n💰 {s['price']:.5f}\n"
           f"قوة الإشارة: {label} {s['score']}%\n⏱️ الوقت: 3 دقائق\n"
           f"📅 {riyadh_time.strftime('%Y-%m-%d | %I:%M:%S %p')}\n---------------------------------------\n"
           f"GOOD LUCK AHMED 👍")
    bot.send_message(message.chat.id, msg)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
