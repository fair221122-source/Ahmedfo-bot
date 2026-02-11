import telebot
import yfinance as yf
import pandas as pd
from flask import Flask
from threading import Thread
import time

app = Flask('')
@app.route('/')
def home(): return "Forex Momentum Bot is Online!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- إعدادات البوت ---
TOKEN = '8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0'
bot = telebot.TeleBot(TOKEN)

# قائمة العملات (26 زوجاً)
FOREX_PAIRS = [
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'NZDUSD=X', 
    'USDCAD=X', 'USDCHF=X', 'EURJPY=X', 'GBPJPY=X', 'AUDJPY=X', 
    'CADJPY=X', 'CHFJPY=X', 'NZDJPY=X', 'EURAUD=X', 'EURCAD=X', 
    'EURCHF=X', 'EURGBP=X', 'EURNZD=X', 'GBPAUD=X', 'GBPCAD=X', 
    'GBPNZD=X', 'AUDCAD=X', 'AUDCHF=X', 'AUDNZD=X', 'CADCHF=X', 'NZDCHF=X'
]

def get_signal_details(score):
    if score >= 85: return "ممتااازة", "3 دقائق"
    elif score >= 70: return "جيدة جداً", "3 دقائق"
    elif score >= 65: return "جيدة", "5 دقائق"
    elif score >= 40: return "مقبولة", "10 دقائق"
    else: return "ضعيفة", "10 دقائق"

def analyze_momentum(symbol):
    try:
        data = yf.download(symbol, period='1d', interval='5m', progress=False)
        if data.empty or len(data) < 10: return None
        
        last_5 = data.tail(5)
        bullish = all(last_5['Close'].iloc[i] > last_5['Open'].iloc[i] for i in range(-3, 0))
        bearish = all(last_5['Close'].iloc[i] < last_5['Open'].iloc[i] for i in range(-3, 0))
        
        if not (bullish or bearish): return None
        
        last_candle = last_5.iloc[-1]
        body = abs(last_candle['Close'] - last_candle['Open'])
        total = last_candle['High'] - last_candle['Low']
        wick_ratio = (total - body) / total if total != 0 else 0
        
        score = 90 if wick_ratio < 0.15 else 60
        # التعديل هنا: SELL بدلاً من SHORT
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
    
    results = [analyze_momentum(s) for s in FOREX_PAIRS]
    signals = sorted([r for r in results if r], key=lambda x: x['score'], reverse=True)[:3]
    
    if not signals:
        bot.edit_message_text("عفواً ... لا توجد إشارات نشطة حالياً ...", chat_id=message.chat.id, message_id=wait_msg.message_id)
        return

    response = "🎯 أفضل 3 إشارات متوفرة حالياً:\n"
    for s in signals:
        emoji = "🟢" if "BUY" in s['action'] else "🔴"
        response += f"\n{emoji} {s['symbol']}\n📈 {s['action'].split()[0]}\n💰 {s['price']}\n💪 قوة الإشارة: {s['label']} {s['score']}%\n⏱️ الوقت: {s['time']}\n"
        # السطر الفاصل هنا بعد كل إشارة
        response += "----------------------------------------\n"
    
    response += "GOOD LUCK AHMED 👍"
    bot.edit_message_text(response, chat_id=message.chat.id, message_id=wait_msg.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(skip_pending=True)
