# telegram_bot/news_signal.py
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

FF_JSON_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
FF_CALENDAR_PAGE = "https://www.forexfactory.com/calendar"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

WATCHED_CURRENCIES = ["USD", "EUR", "GBP", "JPY"]

CURRENCY_MAP = {
    "USD": [("XAUUSD", False), ("EURUSD", False), ("GBPUSD", False), ("USDJPY", True)],
    "EUR": [("EURUSD", True)],
    "GBP": [("GBPUSD", True)],
    "JPY": [("USDJPY", False)],
}

INVERSE_KEYWORDS = ["unemployment", "jobless", "claims"]

processed_events = set()


def _to_float(v):
    try:
        return float(str(v).replace("%", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def fetch_today_schedule():
    try:
        resp = requests.get(FF_JSON_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[news_signal] Gagal ambil jadwal event (fetch_today_schedule): {e}")
        return []

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

    print(f"[news_signal] Jadwal hari ini: {len(events)} event high-impact ditemukan "
          f"({', '.join(ev['title'] for ev in events) if events else '-'})")
    return events


def scrape_actual(event):
    try:
        resp = requests.get(FF_CALENDAR_PAGE, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"[news_signal] Gagal load halaman kalender FF untuk '{event['title']}': {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("tr.calendar__row")
    if not rows:
        print("[news_signal] Peringatan: 0 baris kalender ditemukan di halaman FF "
              "(kemungkinan diblokir/struktur HTML berubah)")
        return None

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

    print(f"[news_signal] Belum ketemu actual untuk '{event['title']}' ({event['currency']}) — "
          f"kemungkinan belum rilis atau judul tidak match persis")
    return None


def interpret(event, actual):
    forecast = event["forecast"]
    if actual is None or forecast is None:
        return None

    is_inverse = any(k in event["title"].lower() for k in INVERSE_KEYWORDS)
    if actual == forecast:
        return None

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
    schedule = context.bot_data.get("news_schedule", [])
    if not schedule:
        # Tidak print tiap 5 menit biar log tidak banjir; cukup diam kalau memang kosong
        return

    now = datetime.now(timezone.utc)

    for event in schedule:
        if event["id"] in processed_events:
            continue
        if now < event["time"].astimezone(timezone.utc):
            continue
        if now > event["time"].astimezone(timezone.utc) + timedelta(minutes=20):
            processed_events.add(event["id"])
            print(f"[news_signal] Lewat 20 menit tanpa actual, skip: {event['title']}")
            continue

        try:
            actual = scrape_actual(event)
        except Exception as e:
            print(f"[news_signal] Error saat scrape_actual untuk '{event['title']}': {e}")
            continue

        if actual is None:
            continue

        processed_events.add(event["id"])
        signals = interpret(event, actual)
        if signals:
            msg = build_message(event, actual, signals)
            try:
                await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
                print(f"[news_signal] Terkirim: {event['title']} actual={actual}")
            except Exception as e:
                print(f"[news_signal] Gagal kirim pesan Telegram: {e}")
        else:
            print(f"[news_signal] '{event['title']}' actual={actual} sama dengan forecast "
                  f"atau tidak bisa diinterpretasi, tidak ada sinyal")


async def refresh_schedule_job(context):
    try:
        context.bot_data["news_schedule"] = fetch_today_schedule()
        processed_events.clear()
    except Exception as e:
        print(f"[news_signal] Error di refresh_schedule_job: {e}")
        context.bot_data.setdefault("news_schedule", [])
