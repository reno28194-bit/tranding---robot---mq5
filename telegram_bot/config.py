import os

# ==========================================
# KONFIGURASI BOT TELEGRAM
# ==========================================

# Ambil dari environment variable (GitHub Secrets), fallback ke manual jika kosong
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "MASUKKAN_TOKEN_DISINI")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "MASUKKAN_CHAT_ID_DISINI")

# ==========================================
# KONFIGURASI TRADING
# ==========================================

DEFAULT_SYMBOL = "EURUSD"
DEFAULT_TIMEFRAME = "M15"
SIGNAL_HISTORY_FILE = "signals_history.json"

# ==========================================
# API SETTINGS
# ==========================================

TELEGRAM_API_URL = "https://api.telegram.org"
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY", "")

# ==========================================
# NOTIFIKASI SETTINGS
# ==========================================

ENABLE_NOTIFICATIONS = True
PARSE_MODE = "HTML"
