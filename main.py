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
def home(): return "Bot is Live!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- إعدادات البوت المنظفة من أي حروف مخفية ---
def clean_env(value):
    if value:
        return re.sub(r'[^\x20-\x7E]', '', value).strip()
    return None

TOKEN = clean_env(os.getenv("TELEGRAM_TOKEN"))
API_KEY = clean_env(os.getenv("TWELVE_DATA_API"))

# التأكد من أن المفاتيح موجودة قبل التشغيل
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
            if df is None or df.empty: continue
            df = df.sort_index(ascending=True)
            
            # 1. حساب قوة الاتجاه (الشموع الخضراء مقابل الحمراء)
            recent_15 = df.iloc[-15:]
            green = len(recent_15[recent_15['close'] > recent_15['open']])
            red = len(recent_15[recent_15['close'] < recent_15['open']])
            trend_score = (max(green, red) / 15) * 100
            
            # 2. حساب الزخم (قوة الشموع الأخيرة - هل هي ممتلئة أم ذيول فقط؟)
            last_5 = df.iloc[-5:]
            body_size = abs(last_5['close'] - last_5['open']).sum()
            total_range = (last_5['high'] - last_5['low']).sum()
            momentum_score = (body_size / total_range) * 100 if total_range != 0 else 0
            
            # 3. الجودة الحقيقية (دمج الاتجاه مع الزخم بنسبة 60% للاتجاه و 40% للزخم)
            true_score = int((trend_score * 0.6) + (momentum_score * 0.4))
            
            # --- تصنيفاتك الجديدة بدقة ---
            if true_score >= 90:
                rank = "ممتازة 🏆"
            elif 80 <= true_score < 90:
                rank = "جيدة جداً ⭐"
            elif 70 <= true_score < 80:
                rank = "جيدة ✅"
            elif 60 <= true_score < 70:
                rank = "ضعيفة ⚠️"
            else:
                rank = "ضعيفة (لا أنصح بالدخول) ❌"
            
            trend = "BUY" if green > red else "SELL"
            all_results.append({
                "pair": s, "trend": trend, "score": true_score, 
                "rank": rank, "price": df.iloc[-1]['close'], 
                "emoji": "🟢" if trend == "BUY" else "🔴"
            })
        except: continue
    return sorted(all_results, key=lambda x: x['score'], reverse=True)


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
