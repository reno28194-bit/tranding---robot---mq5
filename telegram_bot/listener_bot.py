import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")

def get_price_data(symbol, interval="15min", outputsize=50):
    url = "https://api.twelvedata.com/time_series"
    params = {"symbol": symbol, "interval": interval, "outputsize": outputsize, "apikey": TWELVE_DATA_API_KEY}
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    if "values" not in data:
        return None
    closes = [float(i["close"]) for i in reversed(data["values"])]
    highs = [float(i["high"]) for i in reversed(data["values"])]
    lows = [float(i["low"]) for i in reversed(data["values"])]
    return closes, highs, lows

def calculate_sma(values, period):
    if len(values) < period:
        return None
    return sum(values[-period:]) / period

def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        change = closes[i] - closes[i-1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_stochastic(closes, highs, lows, period=14):
    if len(closes) < period:
        return None
    hi, lo = max(highs[-period:]), min(lows[-period:])
    if hi == lo:
        return 50
    return ((closes[-1] - lo) / (hi - lo)) * 100

def calculate_atr(highs, lows, closes, period=14):
    if len(closes) < period + 1:
        return None
    trs = []
    for i in range(1, len(closes)):
        tr = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
        trs.append(tr)
    return sum(trs[-period:]) / period

def analyze(symbol):
    result = get_price_data(symbol)
    if result is None:
        return f"❌ Gagal ambil data {symbol}. Cek nama symbol."
    closes, highs, lows = result
    price = closes[-1]
    ma = calculate_sma(closes, 20)
    rsi = calculate_rsi(closes, 14)
    stoch = calculate_stochastic(closes, highs, lows, 14)
    atr = calculate_atr(highs, lows, closes, 14)
    if None in (ma, rsi, stoch, atr):
        return f"❌ Data tidak cukup untuk {symbol}."

    signal = "WAIT"
    if price > ma and rsi < 40:
        signal = "BUY"
    elif price < ma and rsi > 60:
        signal = "SELL"

    if signal == "BUY":
        sl, tp, emoji = price - (1.5*atr), price + (3*atr), "🟢"
    elif signal == "SELL":
        sl, tp, emoji = price + (1.5*atr), price - (3*atr), "🔴"
    else:
        sl = tp = None
        emoji = "⚪"

    msg = f"{emoji} <b>{signal} - {symbol.upper()}</b>\n\n"
    msg += f"Harga: <code>{price:.5f}</code>\nMA(20): <code>{ma:.5f}</code>\n"
    msg += f"RSI(14): <code>{rsi:.2f}</code>\nStochastic: <code>{stoch:.2f}</code>\n"
    if signal != "WAIT":
        msg += f"\n📍 Entry: <code>{price:.5f}</code>\n🛑 SL: <code>{sl:.5f}</code>\n🎯 TP: <code>{tp:.5f}</code>\n"
    else:
        msg += "\n⏳ Belum ada sinyal jelas, tunggu momentum."
    msg += "\n⚠️ Bukan saran finansial. Lakukan analisa tambahan."
    return msg

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    if text.startswith("analisa"):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("Format: analisa <symbol>\nContoh: analisa xauusd")
            return
        symbol = parts[1].upper()
        if symbol == "XAUUSD":
            symbol = "XAU/USD"
        elif len(symbol) == 6:
            symbol = symbol[:3] + "/" + symbol[3:]
        await update.message.reply_text("🔍 Menganalisa, tunggu sebentar...")
        await update.message.reply_text(analyze(symbol), parse_mode="HTML")
    elif text == "/start":
        await update.message.reply_text("🤖 Bot Analisa Trading Aktif!\n\nKetik: analisa <symbol>\nContoh: analisa xauusd")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    print("Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
