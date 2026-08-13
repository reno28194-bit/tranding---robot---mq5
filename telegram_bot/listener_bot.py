import os
import asyncio
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")

WATCHLIST = ["XAU/USD", "EUR/USD", "BTC/USD", "NDX", "GBP/USD", "USD/JPY"]
CHECK_INTERVAL_SECONDS = 15 * 60  # 15 menit
last_signal = {}


def get_price_data(symbol, interval="15min", outputsize=210):
    # outputsize dinaikkan jadi 210 supaya cukup data untuk hitung EMA200
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


def calculate_ema(values, period):
    if len(values) < period:
        return None
    k = 2 / (period + 1)
    ema = sum(values[:period]) / period  # mulai dari SMA sebagai basis
    for price in values[period:]:
        ema = price * k + ema * (1 - k)
    return ema


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
        return None, f"❌ Gagal ambil data {symbol}."
    closes, highs, lows = result

    price = closes[-1]
    ma20 = calculate_sma(closes, 20)
    ema200 = calculate_ema(closes, 200)
    rsi = calculate_rsi(closes, 14)
    stoch = calculate_stochastic(closes, highs, lows, 14)
    atr = calculate_atr(highs, lows, closes, 14)

    if None in (ma20, ema200, rsi, stoch, atr):
        return None, f"❌ Data tidak cukup untuk {symbol} (butuh histori lebih panjang)."

    # --- Filter tren utama: EMA200 ---
    uptrend = price > ema200
    downtrend = price < ema200

    # --- Sinyal hanya searah tren, dengan konfirmasi RSI + Stochastic ---
    signal = "WAIT"
    if uptrend and price > ma20 and 40 < rsi < 65 and stoch > 20:
        signal = "BUY"
    elif downtrend and price < ma20 and 35 < rsi < 60 and stoch < 80:
        signal = "SELL"

    if signal == "BUY":
        sl, tp, emoji = price - (1.5 * atr), price + (3 * atr), "🟢"
    elif signal == "SELL":
        sl, tp, emoji = price + (1.5 * atr), price - (3 * atr), "🔴"
    else:
        sl = tp = None
        emoji = "⚪"

    trend_label = "Uptrend 📈" if uptrend else ("Downtrend 📉" if downtrend else "Sideways")

    msg = f"{emoji} <b>{signal} - {symbol}</b>\n\n"
    msg += f"Harga: <code>{price:.5f}</code>\nTren (EMA200): {trend_label}\n"
    msg += f"MA(20): <code>{ma20:.5f}</code>\n"
    msg += f"RSI(14): <code>{rsi:.2f}</code>\nStochastic: <code>{stoch:.2f}</code>\n"
    if signal != "WAIT":
        msg += f"\n📍 Entry: <code>{price:.5f}</code>\n🛑 SL: <code>{sl:.5f}</code>\n🎯 TP: <code>{tp:.5f}</code>\n"
        msg += f"(Risk:Reward ≈ 1:2)\n"
    msg += "\n⚠️ Bukan saran finansial."
    return signal, msg


async def auto_scan(context: ContextTypes.DEFAULT_TYPE):
    for symbol in WATCHLIST:
        signal, msg = analyze(symbol)
        if signal in ("BUY", "SELL") and last_signal.get(symbol) != signal:
            await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg, parse_mode="HTML")
        last_signal[symbol] = signal
        await asyncio.sleep(2)


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
        elif symbol == "BTCUSD":
            symbol = "BTC/USD"
        elif symbol == "NASDAQ":
            symbol = "NDX"
        elif len(symbol) == 6:
            symbol = symbol[:3] + "/" + symbol[3:]
        await update.message.reply_text("🔍 Menganalisa, tunggu sebentar...")
        _, msg = analyze(symbol)
        await update.message.reply_text(msg, parse_mode="HTML")
    elif text == "/start":
        await update.message.reply_text(
            "🤖 Bot Analisa Trading Aktif!\n\n"
            "Ketik: analisa <symbol>\nContoh: analisa xauusd\n\n"
            "📡 Auto-scan aktif tiap 15 menit untuk:\nXAUUSD, EURUSD, BTCUSD, NASDAQ, GBPUSD, USDJPY\n\n"
            "Sinyal hanya dikirim jika searah tren utama (EMA200) dan sudah lolos konfirmasi RSI + Stochastic."
        )


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.job_queue.run_repeating(auto_scan, interval=CHECK_INTERVAL_SECONDS, first=10)
    print("Bot berjalan dengan auto-scan tiap 15 menit...")
    app.run_polling()


if __name__ == "__main__":
    main()
