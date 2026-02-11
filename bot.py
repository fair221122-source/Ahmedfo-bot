import os
import telebot
import yfinance as yf
import pandas as pd
import requests
from flask import Flask
from threading import Thread
import time

# --- إعداد السيرفر ---
app = Flask('')
@app.route('/')
def home(): return "Forex Bot is Online!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive(): Thread(target=run).start()

# --- إعدادات البوت ---
TOKEN = '8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0'
bot = telebot.TeleBot(TOKEN)

FOREX_PAIRS = [
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'NZDUSD=X', 
    'USDCAD=X', 'USDCHF=X', 'EURJPY=X', 'GBPJPY=X', 'AUDJPY=X', 
    'CADJPY=X', 'CHFJPY=X', 'NZDJPY=X', 'EURAUD=X', 'EURCAD=X', 
    'EURCHF=X', 'EURGBP=X', 'EURNZD=X', 'GBPAUD=X', 'GBPCAD=X', 
    'GBPNZD=X', 'AUDCAD=X', 'AUDCHF=X', 'AUDNZD=X', 'CADCHF=X', 'NZDCHF=X'
]

def get_signal_details(score):
    if score >= 80: return "ممتااازة", "3 دقائق"
    elif score >= 60: return "جيدة جداً", "3 دقائق"
    elif score >= 40: return "جيدة", "5 دقائق"
    else: return "مقبولة", "10 دقائق"

def analyze_momentum(symbol):
    try:
        # فحص آخر 5 شموع
        data = yf.download(symbol, period='1d', interval='5m', progress=False)
        if data.empty or len(data) < 2: return None
        
        last_candle = data.iloc[-1]
        prev_candle = data.iloc[-2]
        
        # تبسيط: إذا كانت آخر شمعة بنفس اتجاه التي قبلها
        bullish = last_candle['Close'] > last_candle['Open'] and prev_candle['Close'] > prev_candle['Open']
        bearish = last_candle['Close'] < last_candle['Open'] and prev_candle['Close'] < prev_candle['Open']
        
        if not (bullish or bearish): return None
        
        # حساب الجسد مقابل الذيل بمرونة عالية جداً (50%)
        body = abs(last_candle['Close'] - last_candle['Open'])
        total_range = last_candle['High'] - last_candle['Low']
        ratio = body / total_range if total_range != 0 else 0
        
        score = int(ratio * 100)
        action = "BUY 🟢" if bullish else "SELL 🔴"
        label, signal_time = get_signal_details(score)
        
        return {
            'symbol': symbol.replace('=X', ''),
            'action': action, 'price': round(last_candle['Close'], 5),
            'label': label, 'score': score, 'time': signal_time
        }
    except: return None

@bot.message_handler(commands=['start', 'signals'])
def send_signals(message):
    wait_msg = bot.reply_to(message, "جارِ تحليل السوق، إنتظر ثواني ...⏳")
    
    results = []
    for s in FOREX_PAIRS:
        res = analyze_momentum(s)
        if res: results.append(res)
    
    # اختيار أفضل 3 حتى لو كانت النتيجة قليلة
    signals = sorted(results, key=lambda x: x['score'], reverse=True)[:3]
    
    if not signals:
        bot.edit_message_text("عفواً ... لا توجد إشارات نشطة حالياً ...", chat_id=message.chat.id, message_id=wait_msg.message_id)
        return

    response = "🎯 أفضل 3 إشارات متوفرة حالياً:\n"
    for s in signals:
        emoji = "🟢" if "BUY" in s['action'] else "🔴"
        response += f"\n{emoji} {s['symbol']}\n📈 {s['action'].split()[0]}\n💰 {s['price']}\n💪 قوة الإشارة: {s['label']} {s['score']}%\n⏱️ الوقت: {s['time']}\n"
        response += "----------------------------------------\n"
    
    response += "GOOD LUCK AHMED 👍"
    bot.edit_message_text(response, chat_id=message.chat.id, message_id=wait_msg.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(skip_pending=True)
