import os
from flask import Flask
import threading
import yfinance as yf
import telebot
import pandas as pd
import numpy as np
import time

# ============================
# 1. إعداد السيرفر (Render Port Fix)
# ============================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running with Bulk Mode"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# ============================
# 2. إعدادات التلجرام والعملات
# ============================
TELEGRAM_TOKEN = "8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

SYMBOLS = [
    'AUDCAD=X', 'AUDCHF=X', 'AUDJPY=X', 'AUDNZD=X', 'AUDUSD=X',
    'CADCHF=X', 'CADJPY=X', 'CHFJPY=X', 'EURAUD=X', 'EURCAD=X',
    'EURCHF=X', 'EURGBP=X', 'EURJPY=X', 'EURNZD=X', 'EURUSD=X',
    'GBPAUD=X', 'GBPCAD=X', 'GBPCHF=X', 'GBPJPY=X', 'GBPNZD=X', 
    'GBPUSD=X', 'NZDCHF=X', 'NZDJPY=X', 'NZDUSD=X', 'USDCAD=X', 
    'USDCHF=X', 'USDJPY=X'
]

# ============================
# 3. الدالة الجديدة (Bulk Download)
# ============================
@bot.message_handler(commands=['signals', 'start'])
def handle(message):
    bot.send_message(message.chat.id, "🔎 جاري فحص السوق ...")
    
    try:
        # طلب بيانات جميع العملات بطلقة واحدة فقط (لتجنب الـ Rate Limit)
        data = yf.download(tickers=SYMBOLS, period='1d', interval='1m', group_by='ticker', progress=False)
        
        results = []
        for s in SYMBOLS:
            # استخراج بيانات كل عملة من الطلب الموحد
            df = data[s] if len(SYMBOLS) > 1 else data
            df = df.dropna() # تنظيف البيانات من القيم الفارغة
            
            if df.empty or len(df) < 15:
                continue
            
            closes = df['Close'].astype(float)
            opens = df['Open'].astype(float)
            current = float(closes.iloc[-1])
            
            # حساب الزخم (Momentum)
            body = abs(closes.iloc[-1] - opens.iloc[-1])
            avg_body = np.mean(np.abs(closes - opens).iloc[-15:-1]) + 1e-9
            score = body / avg_body
            
            # فلتر الإشارة (يمكنك تعديل 0.8 في الصباح إلى 1.2)
            if score > 0.8:
                # تحديد الاتجاه بناءً على أخر 5 دقائق
                trend_up = current > closes.iloc[-5:].mean()
                direction = "🟢 شراء (BUY)" if trend_up else "🔴 بيع (SELL)"
                
                results.append({
                    "msg": f"{direction} | **{s.replace('=X','')}**\n💰 السعر: {current:.5f}\n💪 القوة: {score:.2f}",
                    "score": score
                })

        if not results:
            bot.send_message(message.chat.id, "⚠️ لا توجد فرص قوية حالياً. انتظر حركة السوق.")
        else:
            # ترتيب أفضل 3 إشارات
            top = sorted(results, key=lambda x: x["score"], reverse=True)[:3]
            final_msg = "🎯 **أفضل 3 فرص حالياً:**\n\n" + "\n\n---\n\n".join([i["msg"] for i in top])
            bot.send_message(message.chat.id, final_msg, parse_mode="Markdown")

    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(message.chat.id, "❌ خطأ في جلب البيانات من ياهو. يرجى المحاولة لاحقاً.")

# ============================
# 4. تشغيل البوت
# ============================
def run_bot():
    print("✅ البوت يعمل بنظام الطلب الموحد...")
    bot.remove_webhook()
    bot.infinity_polling(timeout=20, long_polling_timeout=10)

if __name__ == "__main__":
    run_bot()
