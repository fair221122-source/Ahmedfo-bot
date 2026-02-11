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
TOKEN = '8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0'
bot = telebot.TeleBot(TOKEN)

# --- قوائم العملات (20 فوركس + 15 كريبتو فيوتشرز) ---
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
        # التحليل على فريم الساعة لضمان قوة الاتجاه
        data = yf.download(symbol, period='5d', interval=timeframe, progress=False)
        if data.empty: return None
        
        # المؤشرات الفنية المعتمدة
        data['RSI'] = ta.rsi(data['Close'], length=14)
        data['EMA200'] = ta.ema(data['Close'], length=200)
        atr = ta.atr(data['High'], data['Low'], data['Close'], length=14).iloc[-1]
        
        last = data.iloc[-1]
        price = last['Close']
        rsi = last['RSI']
        ema_val = last['EMA200']
        
        action = None
        score = 0
        
        # منطق تحديد القوة والنوع (حسب طلبك: 55-70 ضعيف، 70-85 متوسط، +85 قوي)
        if price > ema_val and rsi > 52:
            action = "BUY"
            if rsi > 70: score = 92.5 # قوية
            elif rsi > 60: score = 78.2 # متوسطة
            else: score = 64.8 # ضعيفة
        elif price < ema_val and rsi < 48:
            action = "SHORT"
            if rsi < 30: score = 91.8 # قوية
            elif rsi < 40: score = 76.4 # متوسطة
            else: score = 61.2 # ضعيفة

        if not action or score < 55: return None

        # إدارة وقت الصفقة بناءً على القوة (حسب طلبك للفوركس والكريبتو)
        if score >= 85:
            time_val, rr_ratio = "3 دقائق", 5
        elif 70 <= score < 85:
            time_val, rr_ratio = "3 دقائق", 4
        else:
            time_val, rr_ratio = "5 دقائق", 3

        # حساب إدارة المخاطر (ATR Dynamic SL/TP)
        sl_dist = atr * 1.5
        sl = price - sl_dist if action == "BUY" else price + sl_dist
        tp = price + (sl_dist * rr_ratio) if action == "BUY" else price - (sl_dist * rr_ratio)

        return {
            'symbol': symbol.replace('=X', '').replace('-USD', ''),
            'action': action,
            'price': round(price, 5),
            'tp': round(tp, 5),
            'sl': round(sl, 5),
            'score': score,
            'rr': f"1:{rr_ratio}",
            'time': time_val
        }
    except:
        return None

# --- أوامر التيلجرام ---

# --- دالة تحليل الفوركس المحدثة ---
@bot.message_handler(commands=['forex'])
def forex_msg(message):
    results = []
    # سنقوم بتحليل أزواج العملات
    for symbol in FOREX_PAIRS:
        data = analyze_market(symbol)
        if data:
            results.append(data)
    
    # ترتيب حسب القوة واختيار أفضل 3 فقط (حتى لو القوة قليلة)
    signals = sorted(results, key=lambda x: x['score'], reverse=True)[:3]

    response = "📊 **أفضل 3 فرص فوركس حالياً:**\n\n"
    for s in signals:
        # تحويل السكور لنسبة مئوية (مثلاً 80 يصبح 80%)
        success_rate = f"{s['score']}%"
        response += f"🔹 {s['pair']}\n"
        response += f"📈 الإشارة: {s['signal']}\n"
        response += f"🎯 نسبة النجاح المتوقعة: {success_rate}\n"
        response += "------------------------\n"
    
    response += "\n**GOOD LUCK AHMED 👍**"
    bot.reply_to(message, response, parse_mode="Markdown")

# --- دالة تحليل الكريبتو المحدثة ---
@bot.message_handler(commands=['crypto'])
def crypto_msg(message):
    results = []
    for symbol in CRYPTO_PAIRS:
        data = analyze_market(symbol)
        if data:
            results.append(data)
    
    # ترتيب حسب القوة واختيار أفضل 3 مع الميداليات
    signals = sorted(results, key=lambda x: x['score'], reverse=True)[:3]
    medals = ["🥇", "🥈", "🥉"]

    response = "🚀 **أفضل 3 صفقات كريبتو حالياً:**\n\n"
    for i, s in enumerate(signals):
        success_rate = f"{s['score']}%"
        response += f"{medals[i]} {s['pair']}\n"
        response += f"⚡️ قوة الإشارة: {success_rate}\n"
        response += f"🔔 التوصية: {s['signal']}\n"
        response += "------------------------\n"
    
    response += "\n**GOOD LUCK AHMED 👍**"
    bot.reply_to(message, response, parse_mode="Markdown")

# --- تشغيل البوت ---
if __name__ == "__main__":
    print("البوت يعمل الآن يا أحمد... ابحث عن الإشارات!")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
    
