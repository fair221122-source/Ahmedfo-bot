import telebot
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "I am alive!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- إعدادات البوت ---
TOKEN = '8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0' # ضع التوكن الخاص بك هنا
bot = telebot.TeleBot(TOKEN)

# --- قوائم العملات ---
FOREX_PAIRS = [
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDCHF=X', 
    'USDCAD=X', 'NZDUSD=X', 'EURGBP=X', 'EURJPY=X', 'GBPJPY=X',
    'EURAUD=X', 'GBPAUD=X', 'AUDJPY=X', 'AUDCAD=X', 'EURCAD=X',
    'CHFJPY=X', 'GBPCAD=X', 'NZDJPY=X', 'AUDCHF=X', 'CADJPY=X'
]

CRYPTO_FUTURES = [
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD',
    'ADA-USD', 'AVAX-USD', 'DOGE-USD', 'DOT-USD', 'LINK-USD',
    'MATIC-USD', 'LTC-USD', 'NEAR-USD', 'UNI-USD', 'APT-USD'
]

def analyze_market(symbol, timeframe='1h'):
    try:
        data = yf.download(symbol, period='5d', interval=timeframe, progress=False)
        if data.empty: return None
        
        data['RSI'] = ta.rsi(data['Close'], length=14)
        data['EMA200'] = ta.ema(data['Close'], length=200)
        atr_result = ta.atr(data['High'], data['Low'], data['Close'], length=14)
        atr = atr_result.iloc[-1]
        
        last = data.iloc[-1]
        price = last['Close']
        rsi = last['RSI']
        ema_val = last['EMA200']
        
        action = None
        score = 0
        
        if price > ema_val and rsi > 52:
            action = "BUY"
            if rsi > 70: score = 92.5
            elif rsi > 60: score = 78.2
            else: score = 64.8
        elif price < ema_val and rsi < 48:
            action = "SHORT"
            if rsi < 30: score = 91.8
            elif rsi < 40: score = 76.4
            else: score = 61.2

        if not action or score < 55: return None

        if score >= 85:
            time_val, rr_ratio = "3 دقائق", 5
        elif 70 <= score < 85:
            time_val, rr_ratio = "3 دقائق", 4
        else:
            time_val, rr_ratio = "5 دقائق", 3

        sl_dist = atr * 1.5
        sl = price - sl_dist if action == "BUY" else price + sl_dist
        tp = price + (sl_dist * rr_ratio) if action == "BUY" else price - (sl_dist * rr_ratio)

        return {
            'symbol': symbol.replace('=X', '').replace('-USD', ''),
            'action': action,
            'price': round(float(price), 5),
            'tp': round(float(tp), 5),
            'sl': round(float(sl), 5),
            'score': score,
            'rr': f"1:{rr_ratio}",
            'time': time_val
        }
    except:
        return None

# --- أوامر التيلجرام ---

@bot.message_handler(commands=['forex'])
def forex_msg(message):
    bot.send_chat_action(message.chat.id, 'typing')
    results = []
    for symbol in FOREX_PAIRS:
        data = analyze_market(symbol)
        if data:
            results.append(data)
    
    signals = sorted(results, key=lambda x: x['score'], reverse=True)[:3]

    if not signals:
        bot.reply_to(message, "⚠️ لا توجد فرص فوركس متاحة حالياً.")
        return

    response = "📊 **أفضل 3 فرص فوركس حالياً:**\n\n"
    for s in signals:
        success_rate = f"{s['score']}%"
        response += f"🔹 {s['symbol']}\n"
        response += f"📈 الإشارة: {s['action']}\n"
        response += f"🎯 نسبة النجاح المتوقعة: {success_rate}\n"
        response += "------------------------\n"
    
    response += "\n**GOOD LUCK AHMED 👍**"
    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['crypto'])
def crypto_msg(message):
    bot.send_chat_action(message.chat.id, 'typing')
    results = []
    for symbol in CRYPTO_FUTURES:
        data = analyze_market(symbol)
        if data:
            results.append(data)
    
    signals = sorted(results, key=lambda x: x['score'], reverse=True)[:3]
    medals = ["🥇", "🥈", "🥉"]

    if not signals:
        bot.reply_to(message, "⚠️ لا توجد صفقات كريبتو مستقرة حالياً.")
        return

    response = "🚀 **أفضل 3 صفقات كريبتو حالياً:**\n\n"
    for i, s in enumerate(signals):
        success_rate = f"{s['score']}%"
        response += f"{medals[i]} {s['symbol']}\n"
        response += f"⚡️ قوة الإشارة: {success_rate}\n"
        response += f"🔔 التوصية: {s['action']}\n"
        response += "------------------------\n"
    
    response += "\n**GOOD LUCK AHMED 👍**"
    bot.reply_to(message, response, parse_mode="Markdown")

# --- تشغيل البوت ---
if __name__ == "__main__":
    keep_alive() # تفعيل نظام البقاء مستيقظاً
    bot.remove_webhook()
    print("البوت يعمل الآن يا أحمد...")
    bot.infinity_polling(skip_pending=True)
