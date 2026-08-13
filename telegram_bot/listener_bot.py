import os
import json
import asyncio
import requests
from datetime import datetime, timedelta, time as dtime
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")

# --- Opsional: isi ini di Railway Variables kalau mau hitung lot otomatis ---
ACCOUNT_BALANCE = float(os.environ.get("ACCOUNT_BALANCE", 0))  # contoh: 100 (USD)
RISK_PERCENT = float(os.environ.get("RISK_PERCENT", 1))        # contoh: 1 (%)

WATCHLIST = ["XAU/USD", "EUR/USD", "BTC/USD", "NDX", "GBP/USD", "USD/JPY"]
CHECK_INTERVAL_SECONDS = 15 * 60       # scan sinyal baru tiap 15 menit
MONITOR_INTERVAL_SECONDS = 5 * 60      # cek sinyal aktif (TP/SL) tiap 5 menit
SIGNAL_COOLDOWN_MINUTES = 120          # jeda minimal antar sinyal per simbol

DATA_FILE = "/tmp/bot_data.json"

last_signal = {}


# ============ PENYIMPANAN DATA (histori & sinyal aktif) ============

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"active_signals": [], "stats": {"win": 0, "loss": 0}}


def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Gagal simpan data: {e}")


# ============ AMBIL DATA HARGA (dengan retry) ============

def get_price_data(symbol, interval="15min", outputsize=210, retries=3):
    url = "https://api.twelvedata.com/time_series"
    params = {"symbol": symbol, "interval": interval, "outputsize": outputsize, "apikey": TWELVE_DATA_API_KEY}
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if "values" not in data:
                print(f"Data tidak valid untuk {symbol} ({interval}): {data.get('message', data)}")
                return None
            closes = [float(i["close"]) for i in reversed(data["values"])]
            highs = [float(i["high"]) for i in reversed(data["values"])]
            lows = [float(i["low"]) for i in reversed(data["values"])]
            return closes, highs, lows
        except Exception as e:
            print(f"Percobaan {attempt+1} gagal untuk {symbol}: {e}")
            if attempt < retries - 1:
                import time as _t
                _t.sleep(2)
    return None


def get_current_price(symbol, retries=3):
    url = "https://api.twelvedata.com/price"
    params = {"symbol": symbol, "apikey": TWELVE_DATA_API_KEY}
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if "price" in data:
                return float(data["price"])
        except Exception as e:
            print(f"Gagal ambil harga live {symbol}: {e}")
        import time as _t
        _t.sleep(1)
    return None


# ============ INDIKATOR ============

def calculate_sma(values, period):
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def calculate_ema(values, period):
    if len(values) < period:
        return None
    k = 2 / (period + 1)
    ema = sum(values[:period]) / period
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


def calculate_lot_size(entry, sl, symbol):
    if ACCOUNT_BALANCE <= 0:
        return None
    risk_amount = ACCOUNT_BALANCE * (RISK_PERCENT / 100)
    sl_distance = abs(entry - sl)
    if sl_distance == 0:
        return None
    if "XAU" in symbol:
        value_per_point_per_lot = 100
    elif "BTC" in symbol:
        value_per_point_per_lot = 1
    elif "NDX" in symbol:
        value_per_point_per_lot = 1
    else:
        value_per_point_per_lot = 100000 * 0.0001  # forex mayor, per pip standar lot

    lot = risk_amount / (sl_distance * value_per_point_per_lot)
    return round(max(lot, 0.01), 2)


# ============ ANALISA SINYAL (multi-timeframe) ============

def analyze(symbol):
    trend_data = get_price_data(symbol, interval="1h", outputsize=210)
    entry_data = get_price_data(symbol, interval="15min", outputsize=50)

    if trend_data is None or entry_data is None:
        return None, f"❌ Gagal ambil data {symbol}.", None

    trend_closes, _, _ = trend_data
    closes, highs, lows = entry_data

    ema200_h1 = calculate_ema(trend_closes, 200)
    price = closes[-1]
    ma20 = calculate_sma(closes, 20)
    rsi = calculate_rsi(closes, 14)
    stoch = calculate_stochastic(closes, highs, lows, 14)
    atr = calculate_atr(highs, lows, closes, 14)

    if None in (ema200_h1, ma20, rsi, stoch, atr):
        return None, f"❌ Data tidak cukup untuk {symbol}.", None

    uptrend = price > ema200_h1
    downtrend = price < ema200_h1

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

    trend_label = "Uptrend (H1) 📈" if uptrend else ("Downtrend (H1) 📉" if downtrend else "Sideways")

    msg = f"{emoji} <b>{signal} - {symbol}</b>\n\n"
    msg += f"Harga: <code>{price:.5f}</code>\nTren: {trend_label}\n"
    msg += f"MA(20) M15: <code>{ma20:.5f}</code>\n"
    msg += f"RSI(14): <code>{rsi:.2f}</code>\nStochastic: <code>{stoch:.2f}</code>\n"

    trade_info = None
    if signal != "WAIT":
        msg += f"\n📍 Entry: <code>{price:.5f}</code>\n🛑 SL: <code>{sl:.5f}</code>\n🎯 TP: <code>{tp:.5f}</code>\n"
        msg += f"(Risk:Reward ≈ 1:2)\n"
        lot_info = calculate_lot_size(price, sl, symbol)
        if lot_info:
            msg += f"📊 Saran lot (risk {RISK_PERCENT}%): <code>{lot_info}</code>\n"
        trade_info = (price, sl, tp)
    msg += "\n⚠️ Bukan saran finansial."

    return signal, msg, trade_info


# ============ AUTO-SCAN SINYAL BARU ============

async def auto_scan(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    now = datetime.utcnow()

    for symbol in WATCHLIST:
        signal, msg, trade_info = analyze(symbol)
        if signal is None:
            continue

        if signal in ("BUY", "SELL"):
            cd_key = f"cooldown_{symbol}"
            last_time_str = data.get(cd_key)
            if last_time_str:
                last_time = datetime.fromisoformat(last_time_str)
                if now - last_time < timedelta(minutes=SIGNAL_COOLDOWN_MINUTES):
                    last_signal[symbol] = signal
                    await asyncio.sleep(1)
                    continue

            if last_signal.get(symbol) != signal:
                await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg, parse_mode="HTML")
                data[cd_key] = now.isoformat()
                if trade_info:
                    price, sl, tp = trade_info
                    data["active_signals"].append({
                        "symbol": symbol, "signal": signal,
                        "entry": price, "sl": sl, "tp": tp,
                        "time": now.isoformat()
                    })
        last_signal[symbol] = signal
        await asyncio.sleep(2)

    save_data(data)


# ============ MONITOR SINYAL AKTIF (cek TP/SL tercapai) ============

async def monitor_signals(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    still_active = []

    for sig in data.get("active_signals", []):
        price = get_current_price(sig["symbol"])
        if price is None:
            still_active.append(sig)
            continue

        hit = None
        if sig["signal"] == "BUY":
            if price >= sig["tp"]:
                hit = "TP"
            elif price <= sig["sl"]:
                hit = "SL"
        else:
            if price <= sig["tp"]:
                hit = "TP"
            elif price >= sig["sl"]:
                hit = "SL"

        if hit == "TP":
            data["stats"]["win"] += 1
            await context.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"✅ TP tercapai! {sig['symbol']} ({sig['signal']}) — Entry {sig['entry']:.5f} → TP {sig['tp']:.5f}"
            )
        elif hit == "SL":
            data["stats"]["loss"] += 1
            await context.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"🛑 Kena SL. {sig['symbol']} ({sig['signal']}) — Entry {sig['entry']:.5f} → SL {sig['sl']:.5f}"
            )
        else:
            still_active.append(sig)

    data["active_signals"] = still_active
    save_data(data)


# ============ HEALTH CHECK HARIAN ============

async def health_check(context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    stats = data.get("stats", {"win": 0, "loss": 0})
    total = stats["win"] + stats["loss"]
    winrate = (stats["win"] / total * 100) if total > 0 else 0
    await context.bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=f"✅ Bot masih aktif.\n\n📊 Statistik: {stats['win']}W / {stats['loss']}L ({winrate:.1f}% win rate)"
    )


# ============ HANDLER PESAN ============

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
        await update.message.reply_text("🔍 Menganalisa (cek tren H1 + entry M15), tunggu sebentar...")
        _, msg, _ = analyze(symbol)
        await update.message.reply_text(msg, parse_mode="HTML")
    elif text == "/start":
        await update.message.reply_text(
            "🤖 Bot Analisa Trading Aktif!\n\n"
            "Ketik: analisa <symbol>\nContoh: analisa xauusd\n\n"
            "📡 Auto-scan tiap 15 menit untuk:\nXAUUSD, EURUSD, BTCUSD, NASDAQ, GBPUSD, USDJPY\n\n"
            "Sinyal pakai konfirmasi tren H1 + RSI + Stochastic, dengan cooldown 2 jam per simbol.\n\n"
            "Ketik /stats untuk lihat performa sinyal."
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    stats = data.get("stats", {"win": 0, "loss": 0})
    total = stats["win"] + stats["loss"]
    winrate = (stats["win"] / total * 100) if total > 0 else 0
    active = len(data.get("active_signals", []))
    msg = (
        f"📊 <b>Statistik Bot</b>\n\n"
        f"✅ Menang (TP): {stats['win']}\n"
        f"🛑 Kalah (SL): {stats['loss']}\n"
        f"📈 Win rate: {winrate:.1f}%\n"
        f"🔄 Sinyal aktif dipantau: {active}\n\n"
        f"<i>Catatan: statistik bisa reset jika bot di-redeploy.</i>"
    )
    await update.message.reply_text(msg, parse_mode="HTML")


# ============ MAIN ============

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.job_queue.run_repeating(auto_scan, interval=CHECK_INTERVAL_SECONDS, first=10)
    app.job_queue.run_repeating(monitor_signals, interval=MONITOR_INTERVAL_SECONDS, first=30)
    app.job_queue.run_daily(health_check, time=dtime(hour=8, minute=0))

    print("Bot berjalan: auto-scan 15 menit, monitor TP/SL 5 menit, health check harian jam 08:00...")
    app.run_polling()


if __name__ == "__main__":
    main()
