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
def home(): return "Bot is Online!"

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

def analyze_momentum(symbol):
    try:
        # فك الخناق: جلب آخر شمعتين فقط
        data = yf.download(symbol, period='1d', interval='5m', progress=False)
        if data.empty or len(data) < 2: return None
        
        last_candle = data.iloc[-1]
        
        # شرط بسيط جداً: إذا كانت الشمعة الحالية صاعدة أو هابطة بوضوح
        bullish = last_candle['Close'] > last_candle['Open']
        bearish = last_candle['Close'] < last_candle['Open']
        
        # حساب قوة الشمعة (الجسم مقابل الذيول)
        body = abs(last_candle['Close'] - last_candle['Open'])
        total_range = last_candle['High'] - last_candle['Low']
        score = int((body / total_range) * 100) if total_range != 0 else 0
        
        # تصنيف القوة
        if score >= 70: label, t = "ممتازة", "3 دقائق"
        elif score >= 50: label, t = "جيدة جداً", "3 دقائق"
        else: label, t = "جيدة", "5 دقائق"
        
        action = "BUY 🟢" if bullish else "SELL 🔴"
        
        return {
            'symbol': symbol.replace('=X', ''),
            'action': action, 'price': round(last_candle['Close'], 5),
            'label': label, 'score': score, 'time': t
        }
    except: return None

@bot.message_handler(commands=['start', 'signals'])
def send_signals(message):
    wait_msg = bot.reply_to(message, "جارِ تحليل السوق، إنتظر ثواني ...⏳")
    results = []
    
    for s in FOREX_PAIRS:
        res = analyze_momentum(s)
        if res: results.append(res)
        time.sleep(0.5) # سرعة أكبر مع حماية من الحظر
    
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
    bot.infinity_polling(skip_pending=True)
