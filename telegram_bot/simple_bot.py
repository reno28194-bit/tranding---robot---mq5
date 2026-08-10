#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading Signal Bot - Telegram
Bot untuk mengirim sinyal BUY/SELL trading ke Telegram
"""

import requests
import json
from datetime import datetime
from config import BOT_TOKEN, CHAT_ID, TELEGRAM_API_URL, PARSE_MODE

BOT_API = f"{TELEGRAM_API_URL}/bot{BOT_TOKEN}/sendMessage"

def validate_config():
    """Validasi konfigurasi bot"""
    if "MASUKKAN" in BOT_TOKEN or "MASUKKAN" in CHAT_ID:
        print("\n❌ ERROR: Bot token atau Chat ID belum dikonfigurasi!")
        print("\n📝 Langkah setup:")
        print("1. Buka file: telegram_bot/config.py")
        print("2. Ganti BOT_TOKEN dengan token Anda")
        print("3. Ganti CHAT_ID dengan chat ID Anda")
        print("4. Save file")
        return False
    return True

def send_telegram_message(message, silent=False):
    """Kirim pesan ke Telegram"""
    try:
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": PARSE_MODE
        }
        response = requests.post(BOT_API, json=payload, timeout=10)
        
        if response.status_code == 200:
            if not silent:
                print("✅ Pesan terkirim ke Telegram!")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Timeout: Koneksi internet lambat")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Error: Tidak ada koneksi internet")
        return False
    except Exception as e:
        print(f"❌ Error pengiriman: {e}")
        return False

def create_buy_signal(symbol, price, reason, ma, rsi, stoch):
    """Buat pesan sinyal BUY"""
    message = f"""
🟢 <b>BUY SIGNAL</b>

<b>Symbol:</b> <code>{symbol}</code>
<b>Price:</b> <code>{price}</code>
<b>MA(20):</b> <code>{ma}</code>
<b>RSI:</b> <code>{rsi}</code>
<b>Stochastic:</b> <code>{stoch}</code>

<b>Reason:</b> {reason}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<i>⚠️ Lakukan analisa manual sebelum trade!</i>
"""
    return message

def create_sell_signal(symbol, price, reason, ma, rsi, stoch):
    """Buat pesan sinyal SELL"""
    message = f"""
🔴 <b>SELL SIGNAL</b>

<b>Symbol:</b> <code>{symbol}</code>
<b>Price:</b> <code>{price}</code>
<b>MA(20):</b> <code>{ma}</code>
<b>RSI:</b> <code>{rsi}</code>
<b>Stochastic:</b> <code>{stoch}</code>

<b>Reason:</b> {reason}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<i>⚠️ Lakukan analisa manual sebelum trade!</i>
"""
    return message

def send_buy_signal(symbol, price, reason, ma, rsi, stoch):
    """Kirim sinyal BUY ke Telegram"""
    if not validate_config():
        return False
    message = create_buy_signal(symbol, price, reason, ma, rsi, stoch)
    return send_telegram_message(message)

def send_sell_signal(symbol, price, reason, ma, rsi, stoch):
    """Kirim sinyal SELL ke Telegram"""
    if not validate_config():
        return False
    message = create_sell_signal(symbol, price, reason, ma, rsi, stoch)
    return send_telegram_message(message)

def send_custom_message(text):
    """Kirim pesan custom ke Telegram"""
    if not validate_config():
        return False
    return send_telegram_message(text)

def send_test_message():
    """Kirim pesan test ke Telegram"""
    if not validate_config():
        return False
    
    test_message = """
✅ <b>Bot Telegram Aktif!</b>

<b>Status:</b> ✓ Koneksi OK
<b>Time:</b> {}

📊 Bot siap menerima sinyal trading!
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    return send_telegram_message(test_message)

# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 Trading Signal Bot - Test Mode")
    print("="*60)
    
    if not validate_config():
        print("\n❌ Setup belum selesai!\n")
        exit(1)
    
    # Test koneksi
    print("\n📤 Mengirim test message...")
    if send_test_message():
        print("✅ Test berhasil!\n")
    else:
        print("❌ Test gagal!\n")
        exit(1)
    
    # Test BUY Signal
    print("\n📤 Mengirim BUY Signal...")
    send_buy_signal(
        symbol="EURUSD",
        price="1.0850",
        reason="Price > MA + RSI Oversold",
        ma="1.0820",
        rsi="28.5",
        stoch="18.2"
    )
    
    import time
    print("\nMenunggu 2 detik...\n")
    time.sleep(2)
    
    # Test SELL Signal
    print("📤 Mengirim SELL Signal...")
    send_sell_signal(
        symbol="EURUSD",
        price="1.0920",
        reason="Price < MA + RSI Overbought",
        ma="1.0950",
        rsi="72.5",
        stoch="82.1"
    )
    
    print("\n✅ Test selesai!\n")
