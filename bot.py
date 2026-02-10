import os
from flask import Flask
import threading
import yfinance as yf
import telebot
import pandas as pd
import numpy as np
import time

# ============================
# إعداد السيرفر لـ Render
# ============================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running on Yahoo Finance Data"

def run_flask():
    # حل مشكلة Port Binding في Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# ============================
# إعدادات التلجرام
# ============================
TELEGRAM_TOKEN = "8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# قائمة العملات بتنسيق ياهو فينانس (بدون تكرار)
SYMBOLS = [
    'AUDCAD=X', 'AUDCHF=X', 'AUDJPY=X', 'AUDNZD=X', 'AUDUSD=X',
    'CADCHF=X', 'CADJPY=X', 'CHFJPY=X', 'EURAUD=X', 'EURCAD=X',
    'EURCHF=X', 'EURGBP=X', 'EURJPY=X', 'EURNZD=X', 'EURUSD=X',
    'GBPAUD=X', 'GBPCAD=X', 'GBPJPY=X', 'GBPNZD=X', 'GBPUSD=X',
    'NZDCHF=X', 'NZDJPY=X', 'NZDUSD=X', 'USDCAD=X', 'USDCHF=X',
    'USDJPY=X'
]

# ============================
# جلب البيانات من Yahoo Finance
# ============================
def get_candles(symbol):
    try:
        # جلب بيانات الدقيقة لآخر يوم (بيانات حية)
        df = yf.download(tickers=symbol, period='1d', interval='1m', progress=False)
        
        if df.empty or len(df) < 15:
            return None
            
        # تنسيق الأعمدة
        df = df[['Open', 'High', 'Low', 'Close']]
        df.columns = ['open', 'high', 'low', 'close']
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

# ============================
# استراتيجية التحليل (Momentum + Trend)
# ============================
def get_signal(symbol):
    df = get_candles(symbol)
    if df is None:
        return None

    closes = df["close"]
    opens = df["open"]
    current_price = float(closes.iloc[-1])
    
    # تحديد الاتجاه بناءً على المتوسط المتحرك البسيط
    sma = closes.rolling(window=14).mean().iloc[-1]
    trend_up = current_price > sma
    trend_down = current_price < sma

    # حساب قوة الشمعة الأخيرة (Momentum)
    bodies = (closes - opens).iloc[-10:]
    avg_body = np.mean(np.abs(bodies.iloc[:-1])) + 0.000001
    current_body = abs(closes.iloc[-1] - opens.iloc[-1])
    
    momentum_score = current_body / avg_body

    # معايير القوة والوقت
    if momentum_score >= 1.5:
        strength, trade_time = "قوية جداً 🔥", "1-2 min"
    elif momentum_score >= 1.0:
        strength, trade_time = "متوسطة ⚡", "3 min"
    else:
        # إذا كان الزخم ضعيف جداً لا نرسل إشارة
        return None

    name = symbol.replace("=X", "").replace("/", "")

    if trend_up:
        msg = f"🟢 **{name}**\n📈 **BUY (شراء)**\n💰 السعر: {current_price:.5f}\n💪 القوة: {strength}\n⏱️ الوقت: {trade_time}"
        return {"msg": msg, "score": momentum_score}
    
    if trend_down:
        msg = f"🔴 **{name}**\n📉 **SELL (بيع)**\n💰 السعر: {current_price:.5f}\n💪 القوة: {strength}\n⏱️ الوقت: {trade_time}"
        return {"msg": msg, "score": momentum_score}

    return None

# ============================
# أوامر البوت
# ============================
@bot.message_handler(commands=['signals', 'start'])
def handle(message):
    bot.send_message(message.chat.id, "🔎 جاري فحص 26 زوجاً من العملات عبر Yahoo Finance...")
    
    results = []
    for s in SYMBOLS:
        res = get_signal(s)
        if res:
            results.append(res)
        # لا نحتاج لانتظار طويل هنا لأن ياهو سريع
        time.sleep(0.05) 

    if not results:
        bot.send_message(message.chat.id, "⚠️ السوق هادئ حالياً ولا توجد فرص واضحة.")
        return

    # ترتيب النتائج لإعطاء أفضل 3 فرص من حيث الزخم
    top_signals = sorted(results, key=lambda x: x["score"], reverse=True)[:3]
    
    final_text = "🎯 **أفضل 3 فرص تداول الآن:**\n\n"
    for item in top_signals:
        final_text += item["msg"] + "\n" + "-------------------" + "\n"
        
    bot.send_message(message.chat.id, final_text, parse_mode="Markdown")

def run_bot():
    print("✅ Bot is Live and ready!")
    bot.infinity_polling()

if __name__ == "__main__":
    run_bot()
