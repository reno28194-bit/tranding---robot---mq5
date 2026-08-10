#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading Signal Bot - Interactive Menu
Menu interaktif untuk mengirim sinyal manual ke Telegram
"""

import json
import os
from datetime import datetime
from simple_bot import (
    send_buy_signal,
    send_sell_signal,
    send_custom_message,
    send_test_message,
    validate_config
)
from config import SIGNAL_HISTORY_FILE, DEFAULT_SYMBOL

def clear_screen():
    """Clear console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def save_signal(signal_data):
    """Simpan sinyal ke file JSON"""
    try:
        with open(SIGNAL_HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(signal_data, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        print(f"❌ Error menyimpan: {e}")
        return False

def load_signals():
    """Load riwayat sinyal dari file"""
    try:
        signals = []
        if os.path.exists(SIGNAL_HISTORY_FILE):
            with open(SIGNAL_HISTORY_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        signals.append(json.loads(line))
        return signals
    except Exception as e:
        print(f"❌ Error membaca file: {e}")
        return []

def manual_buy_signal():
    """Input manual untuk BUY signal"""
    clear_screen()
    print("\n" + "="*60)
    print("🟢 INPUT SINYAL BUY MANUAL")
    print("="*60)
    
    try:
        symbol = input(f"\nSymbol (default: {DEFAULT_SYMBOL}): ").strip().upper() or DEFAULT_SYMBOL
        price = input("Price sekarang: ").strip() or "0.0000"
        ma = input("Moving Average (MA): ").strip() or "0.0000"
        rsi = input("RSI Value (0-100): ").strip() or "50"
        stoch = input("Stochastic Value (0-100): ").strip() or "50"
        reason = input("Reason/Alasan: ").strip() or "Manual BUY Signal"
        
        print("\n📤 Mengirim sinyal BUY...")
        if send_buy_signal(symbol, price, reason, ma, rsi, stoch):
            signal_data = {
                "timestamp": datetime.now().isoformat(),
                "type": "BUY",
                "symbol": symbol,
                "price": price,
                "ma": ma,
                "rsi": rsi,
                "stoch": stoch,
                "reason": reason
            }
            save_signal(signal_data)
            print("\n✅ BUY Signal terkirim dan disimpan!")
        else:
            print("\n❌ Gagal mengirim sinyal")
    
    except KeyboardInterrupt:
        print("\n⚠️ Dibatalkan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\n\nTekan ENTER untuk lanjut...")

def manual_sell_signal():
    """Input manual untuk SELL signal"""
    clear_screen()
    print("\n" + "="*60)
    print("🔴 INPUT SINYAL SELL MANUAL")
    print("="*60)
    
    try:
        symbol = input(f"\nSymbol (default: {DEFAULT_SYMBOL}): ").strip().upper() or DEFAULT_SYMBOL
        price = input("Price sekarang: ").strip() or "0.0000"
        ma = input("Moving Average (MA): ").strip() or "0.0000"
        rsi = input("RSI Value (0-100): ").strip() or "50"
        stoch = input("Stochastic Value (0-100): ").strip() or "50"
        reason = input("Reason/Alasan: ").strip() or "Manual SELL Signal"
        
        print("\n📤 Mengirim sinyal SELL...")
        if send_sell_signal(symbol, price, reason, ma, rsi, stoch):
            signal_data = {
                "timestamp": datetime.now().isoformat(),
                "type": "SELL",
                "symbol": symbol,
                "price": price,
                "ma": ma,
                "rsi": rsi,
                "stoch": stoch,
                "reason": reason
            }
            save_signal(signal_data)
            print("\n✅ SELL Signal terkirim dan disimpan!")
        else:
            print("\n❌ Gagal mengirim sinyal")
    
    except KeyboardInterrupt:
        print("\n⚠️ Dibatalkan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\n\nTekan ENTER untuk lanjut...")

def view_history():
    """Lihat riwayat sinyal"""
    clear_screen()
    print("\n" + "="*60)
    print("📊 RIWAYAT SINYAL")
    print("="*60)
    
    signals = load_signals()
    
    if not signals:
        print("\n❌ Tidak ada riwayat sinyal")
    else:
        for i, signal in enumerate(signals, 1):
            timestamp = signal.get('timestamp', 'N/A')
            signal_type = signal.get('type', 'N/A')
            symbol = signal.get('symbol', 'N/A')
            price = signal.get('price', 'N/A')
            reason = signal.get('reason', 'N/A')
            
            print(f"\n{i}. [{signal_type}] {symbol}")
            print(f"   Time: {timestamp}")
            print(f"   Price: {price}")
            print(f"   Reason: {reason}")
    
    input("\n\nTekan ENTER untuk lanjut...")

def test_connection():
    """Test koneksi ke Telegram"""
    clear_screen()
    print("\n" + "="*60)
    print("🔍 TEST KONEKSI")
    print("="*60)
    
    print("\n📤 Mengirim pesan test...")
    if send_test_message():
        print("\n✅ Koneksi berhasil!")
        print("   Bot siap digunakan.")
    else:
        print("\n❌ Koneksi gagal!")
        print("   Periksa:")
        print("   - Bot token valid?")
        print("   - Chat ID valid?")
        print("   - Koneksi internet aktif?")
    
    input("\n\nTekan ENTER untuk lanjut...")

def clear_history():
    """Hapus riwayat sinyal"""
    clear_screen()
    print("\n" + "="*60)
    print("🗑️  HAPUS RIWAYAT")
    print("="*60)
    
    confirm = input("\n⚠️  Apakah Anda yakin ingin menghapus semua riwayat? (y/n): ").lower()
    
    if confirm == 'y':
        try:
            if os.path.exists(SIGNAL_HISTORY_FILE):
                os.remove(SIGNAL_HISTORY_FILE)
                print("\n✅ Riwayat dihapus!")
            else:
                print("\n❌ File riwayat tidak ditemukan")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print("\n⚠️  Dibatalkan")
    
    input("\n\nTekan ENTER untuk lanjut...")

def show_statistics():
    """Tampilkan statistik sinyal"""
    clear_screen()
    print("\n" + "="*60)
    print("📈 STATISTIK SINYAL")
    print("="*60)
    
    signals = load_signals()
    
    if not signals:
        print("\n❌ Tidak ada data sinyal")
    else:
        buy_count = sum(1 for s in signals if s.get('type') == 'BUY')
        sell_count = sum(1 for s in signals if s.get('type') == 'SELL')
        total_count = len(signals)
        
        print(f"\n📊 Total Sinyal: {total_count}")
        print(f"🟢 BUY Signals: {buy_count}")
        print(f"🔴 SELL Signals: {sell_count}")
        
        if total_count > 0:
            buy_percent = (buy_count / total_count) * 100
            sell_percent = (sell_count / total_count) * 100
            print(f"\n📉 Distribusi:")
            print(f"   BUY: {buy_percent:.1f}%")
            print(f"   SELL: {sell_percent:.1f}%")
    
    input("\n\nTekan ENTER untuk lanjut...")

def main_menu():
    """Menu utama"""
    if not validate_config():
        print("\n❌ Konfigurasi tidak lengkap!")
        print("\nSilakan edit file: telegram_bot/config.py")
        print("Dan isi BOT_TOKEN dan CHAT_ID Anda\n")
        return
    
    while True:
        clear_screen()
        print("\n" + "="*60)
        print("🤖 TELEGRAM TRADING SIGNAL BOT")
        print("="*60)
        print("\n1. 🟢 Kirim BUY Signal")
        print("2. 🔴 Kirim SELL Signal")
        print("3. 📊 Lihat Riwayat Sinyal")
        print("4. 📈 Statistik Sinyal")
        print("5. 🔍 Test Koneksi")
        print("6. 🗑️  Hapus Riwayat")
        print("7. ❌ Exit")
        print("\n" + "="*60)
        
        choice = input("\nPilih menu (1-7): ").strip()
        
        if choice == "1":
            manual_buy_signal()
        elif choice == "2":
            manual_sell_signal()
        elif choice == "3":
            view_history()
        elif choice == "4":
            show_statistics()
        elif choice == "5":
            test_connection()
        elif choice == "6":
            clear_history()
        elif choice == "7":
            clear_screen()
            print("\n👋 Terima kasih telah menggunakan Trading Signal Bot!\n")
            break
        else:
            print("\n❌ Input tidak valid! Silakan coba lagi.")
            input("\nTekan ENTER untuk lanjut...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Program dihentikan oleh user\n")
    except Exception as e:
        print(f"\n\n❌ Error: {e}\n")
