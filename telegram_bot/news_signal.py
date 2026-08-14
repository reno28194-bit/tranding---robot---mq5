# telegram_bot/news_signal.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

FF_JSON_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
FF_CALENDAR_PAGE = "https://www.forexfactory.com/calendar"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

WATCHED_CURRENCIES = ["USD", "EUR", "GBP", "JPY"]

# currency -> pair yang dipengaruhi, dan arah "sama" (True) atau "kebalikan" (False)
# True = kalau currency menguat, pair ini naik. False = kalau currency menguat, pair ini turun.
CURRENCY_MAP = {
    "USD": [("XAUUSD", False), ("EURUSD", False), ("GBPUSD", False), ("USDJPY", True)],
    "EUR": [("EURUSD", True)],
    "GBP": [("GBPUSD", True)],
    "JPY": [("USDJPY", False)],
}

# indikator yang sifatnya kebalikan: actual lebih RENDAH dari forecast = currency menguat
INVERSE_KEYWORDS = ["unemployment", "jobless", "claims", "cpi" ]  # cpi sengaja masuk contoh ambigu, lihat catatan di bawah

processed_events = set()


def _to_float(v):
    try:
        return float(str(v).replace("%", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def fetch_today_schedule():
    """Ambil jadwal event high-impact hari ini (1x panggil per hari)."""
    resp = requests.get(FF_JSON_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    today = datetime.now(timezone.utc).date()
    events = []
    for e in data:
        if e.get("impact") != "High":
            continue
        if e.get("country") not in WATCHED_CURRENCIES:
            continue
        try:
            event_time = datetime.fromisoformat(e["date"])
        except (ValueError, KeyError):
            continue
        if event_time.astimezone(timezone.utc).date() != today:
            continue
        events.append({
            "id": f"{e['country']}_{e['title']}_{e['date']}",
            "title": e["title"],
            "currency": e["country"],
            "time": event_time,
            "forecast": _to_float(e.get("forecast")),
            "previous": _to_float(e.get("previous")),
        })
    return events


def scrape_actual(event):
    """Cari nilai 'actual' event tertentu di halaman kalender FF."""
    resp = requests.get(FF_CALENDAR_PAGE, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    rows = soup.select("tr.calendar__row")
    for row in rows:
        title_el = row.select_one(".calendar__event")
        currency_el = row.select_one(".calendar__currency")
        actual_el = row.select_one(".calendar__actual")
        if not title_el or not currency_el or not actual_el:
            continue
        if currency_el.get_text(strip=True) != event["currency"]:
            continue
        if event["title"].lower() not in title_el.get_text(strip=True).lower():
            continue
        actual_text = actual_el.get_text(strip=True)
        if actual_text:
            return _to_float(actual_text)
    return None


def interpret(event, actual):
    forecast = event["forecast"]
    if actual is None or forecast is None:
        return None

    is_inverse = any(k in event["title"].lower() for k in INVERSE_KEYWORDS)
    if actual == forecast:
        return None  # sesuai ekspektasi, tidak ada kejutan -> skip

    surprised_up = actual > forecast
    currency_stronger = (not surprised_up) if is_inverse else surprised_up

    signals = []
    for pair, same_direction in CURRENCY_MAP.get(event["currency"], []):
        direction = "BUY" if (currency_stronger == same_direction) else "SELL"
        signals.append((pair, direction))
    return signals


def build_message(event, actual, signals):
    lines = [
        f"📰 NEWS SIGNAL — {event['title']} ({event['currency']})",
        f"Actual: {actual} | Forecast: {event['forecast']} | Previous: {event['previous']}",
        "",
    ]
    for pair, direction in signals:
        lines.append(f"➡️ {pair}: peluang {direction}")
    lines.append("\n⚠️ Bukan saran finansial. Sinyal berdasarkan reaksi data vs ekspektasi, cek chart sebelum entry.")
    return "\n".join(lines)


async def news_scan_job(context):
    """Dipanggil tiap 5 menit lewat job_queue."""
    schedule = context.bot_data.get("news_schedule", [])
    now = datetime.now(timezone.utc)

    for event in schedule:
        if event["id"] in processed_events:
            continue
        if now < event["time"].astimezone(timezone.utc):
            continue
        if now > event["time"].astimezone(timezone.utc) + timedelta(minutes=20):
            processed_events.add(event["id"])  # kadaluarsa, lewati
            continue

        actual = scrape_actual(event)
        if actual is None:
            continue  # belum rilis, coba lagi 5 menit berikutnya

        processed_events.add(event["id"])
        signals = interpret(event, actual)
        if signals:
            msg = build_message(event, actual, signals)
            await context.bot.send_message(chat_id=context.job.chat_id, text=msg)


async def refresh_schedule_job(context):
    """Dipanggil 1x sehari untuk ambil jadwal event hari ini."""
    context.bot_data["news_schedule"] = fetch_today_schedule()
    processed_events.clear()
