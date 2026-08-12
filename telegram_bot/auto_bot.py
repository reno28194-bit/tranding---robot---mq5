#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Bot - Versi otomatis tanpa input manual
Untuk dijalankan di GitHub Actions
"""

from simple_bot import send_test_message, validate_config

if __name__ == "__main__":
    print("🤖 Menjalankan Auto Bot...")
    
    if not validate_config():
        print("❌ Konfigurasi tidak lengkap!")
        exit(1)
    
    if send_test_message():
        print("✅ Test message berhasil dikirim!")
    else:
        print("❌ Gagal mengirim pesan.")
        exit(1)
