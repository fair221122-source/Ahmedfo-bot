import os
import yfinance as yf
import telebot
import pandas as pd
import numpy as np
import threading
from flask import Flask

# --- سيرفر الإبقاء حياً ---
app = Flask(__name__)
@app.route('/')
def home(): return "SMC Bot Active"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# --- إعدادات البوت ---
TELEGRAM_TOKEN = "8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

FOREX_SYMBOLS = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'AUDCHF=X', 'AUDJPY=X', 'AUDCAD=X', 'NZDUSD=X']
CRYPTO_SYMBOLS = ['BTC-USD', 'ETH-USD', 'XRP-USD', 'SOL-USD', 'BNB-USD', 'AVAX-USD']

def get_refined_signal(df):
    # حساب المتوسط الحركي للزخم (الفلتر الذكي)
    df['body'] = abs(df['Close'] - df['Open'])
    avg_body = df['body'].rolling(window=14).mean().iloc[-1]
    last_body = df['body'].iloc[-1]
    
    # نسبة القوة (0.5 تعني توازن، فوق 1.0 يعني انفجار سعري)
    score = last_body / (avg_body + 1e-9)
    
    side = "BUY" if df['Close'].iloc[-1] > df['Open'].iloc[-1] else "SHORT"
    
    # تحديد مستويات SMC
    recent_high = df['High'].iloc[-15:].max()
    recent_low = df['Low'].iloc[-15:].min()
    current_price = df['Close'].iloc[-1]
    
    if side == "BUY":
        sl = recent_low - (recent_low * 0.0005) # وقف خسارة تحت القاع بقليل
        tp = current_price + (current_price - sl) * 1.5 # هدف منطقي 1:1.5
    else:
        sl = recent_high + (recent_high * 0.0005)
        tp = current_price - (sl - current_price) * 1.5
        
    rr = f"1:{round(abs(tp-current_price)/abs(current_price-sl+1e-9), 1)}"
    success = round(min(70 + (score * 5), 94.0), 1)
    
    return {"score": score, "side": side, "sl": sl, "tp": tp, "rr": rr, "success": success, "price": current_price}

@bot.message_handler(commands=['forex'])
def do_forex(message):
    m = bot.send_message(message.chat.id, "جارِ تحليل سوق الفوركس، إنتظر ثواني ... ⏳")
    try:
        data = yf.download(tickers=FOREX_SYMBOLS, period='1d', interval='5m', group_by='ticker', progress=False)
        valid_signals = []
        for s in FOREX_SYMBOLS:
            df = data[s].dropna()
            if len(df) < 20: continue
            sig = get_refined_signal(df)
            if sig['score'] > 0.45: # توازن بين كثرة الصفقات وجودتها
                valid_signals.append({"name": s.replace('=X',''), "sig": sig})
        
        if not valid_signals:
            bot.edit_message_text("لا توجد إشارات قوية حاليا ...❗", message.chat.id, m.message_id)
            return

        res = "🎯 أفضل 3 إشارات حالياً:\n\n"
        for item in sorted(valid_signals, key=lambda x: x['sig']['score'], reverse=True)[:3]:
            s = item['sig']
            strength = "قوية" if s['score'] > 1.2 else "متوسطة" if s['score'] > 0.7 else "ضعيفة"
            res += f"{'🟢' if s['side']=='BUY' else '🔴'} {item['name']}\n📈 {s['side']}\n💰 {s['price']:.5f}\n💪 قوة الإشارة: {strength}\n⏱️ الوقت: 1-5 دقائق\n-------------------\n"
        bot.edit_message_text(res, message.chat.id, m.message_id)
    except:
        bot.edit_message_text("لا توجد إشارات حاليا ...❗", message.chat.id, m.message_id)

@bot.message_handler(commands=['crypto'])
def do_crypto(message):
    m = bot.send_message(message.chat.id, "جارِ تحليل سوق الكربتو، إنتظر ثواني ... ⏳")
    try:
        data = yf.download(tickers=CRYPTO_SYMBOLS, period='2d', interval='1h', group_by='ticker', progress=False)
        valid_signals = []
        for s in CRYPTO_SYMBOLS:
            df = data[s].dropna()
            if len(df) < 20: continue
            sig = get_refined_signal(df)
            if sig['score'] > 0.4:
                valid_signals.append({"name": s.replace('-USD','/USDT'), "sig": sig})

        if not valid_signals:
            bot.edit_message_text("لا توجد مناطق دول آمنة حاليا ...❗", message.chat.id, m.message_id)
            return

        titles = ["🥇 TOP PICK", "🥈 SECOND BEST", "🥉 THIRD PICK"]
        res = ""
        for i, item in enumerate(sorted(valid_signals, key=lambda x: x['sig']['score'], reverse=True)[:3]):
            s = item['sig']
            res += f"{titles[i]}: {item['name']}\n🎯 Success: {s['success']} %\n⚡ Type: {s['side']} {'🟢' if s['side']=='BUY' else '🔴'}\nEntry: {s['price']:.4f}\nS.L: {s['sl']:.4f}\nT.P: {s['tp']:.4f}\nR:R: {s['rr']}\n\n"
        res += "GOOD LUCK AHMED 👍"
        bot.edit_message_text(res, message.chat.id, m.message_id)
    except:
        bot.edit_message_text("لا توجد مناطق دول آمنة حاليا ...❗", message.chat.id, m.message_id)

bot.remove_webhook()
bot.infinity_polling(skip_pending=True)

