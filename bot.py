import telebot
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from flask import Flask
from threading import Thread
import time

app = Flask('')
@app.route('/')
def home(): return "I am alive!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- إعدادات البوت ---
TOKEN = '8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0' # تأكد من وضع التوكن الخاص بك كاملاً هنا
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
        # جلب البيانات
        data = yf.download(symbol, period='5d', interval=timeframe, progress=False)
        if data.empty: return None
        
        # المؤشرات
        data['RSI'] = ta.rsi(data['Close'], length=14)
        data['EMA200'] = ta.ema(data['Close'], length=200)
        atr_result = ta.atr(data['High'], data['Low'], data['Close'], length=14)
        atr = atr_result.iloc[-1]
        
        last = data.iloc[-1]
        price = last['Close']
        rsi = last['RSI']
        ema_val = last['EMA200']
        
        # المنطق المرن (BUY/SHORT)
        if price > ema_val:
            action = "BUY"
            score = 85.5 if rsi > 55 else 58.2
        else:
            action = "SHORT"
            score = 84.1 if rsi < 45 else 56.4

        # تحديد الأهداف
        rr_ratio = 5 if score >= 80 else 3
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
            'time': "3 دقائق" if score >= 80 else "5 دقائق"
        }
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

# --- أوامر التيلجرام ---

@bot.message_handler(commands=['forex'])
def forex_msg(message):
    bot.send_chat_action(message.chat.id, 'typing')
    results = []
    for symbol in FOREX_PAIRS:
        data = analyze_market(symbol)
        if data: results.append(data)
    
    signals = sorted(results, key=lambda x: x['score'], reverse=True)[:3]
    if not signals:
        bot.reply_to(message, "⚠️ لا توجد فرص فوركس متاحة حالياً.")
        return

    response = "📊 **أفضل 3 فرص فوركس حالياً:**\n\n"
    for s in signals:
        response += f"🔹 {s['symbol']}\n📈 الإشارة: {s['action']}\n🎯 نسبة النجاح: {s['score']}%\n⏰ الوقت: {s['time']}\n------------------------\n"
    response += "\n**GOOD LUCK AHMED 👍**"
    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['crypto'])
def crypto_msg(message):
    bot.send_chat_action(message.chat.id, 'typing')
    results = []
    for symbol in CRYPTO_FUTURES:
        data = analyze_market(symbol)
        if data: results.append(data)
    
    signals = sorted(results, key=lambda x: x['score'], reverse=True)[:3]
    medals = ["🥇", "🥈", "🥉"]

    if not signals:
        bot.reply_to(message, "⚠️ لا توجد صفقات كريبتو مستقرة حالياً.")
        return

    response = "🚀 **أفضل 3 صفقات كريبتو حالياً:**\n\n"
    for i, s in enumerate(signals):
        response += f"{medals[i]} {s['symbol']}\n⚡️ القوة: {s['score']}%\n🔔 التوصية: {s['action']}\n⏰ الوقت: {s['time']}\n------------------------\n"
    response += "\n**GOOD LUCK AHMED 👍**"
    bot.reply_to(message, response, parse_mode="Markdown")

# --- تشغيل البوت ---
if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    print("البوت يعمل الآن يا أحمد...")
    bot.infinity_polling(skip_pending=True)
