# 🤖 Telegram Trading Signal Bot

Bot untuk mengirim sinyal BUY/SELL trading ke Telegram secara manual atau otomatis dari MT5.

## 📋 Fitur

✅ **Kirim Sinyal Manual**
- BUY Signal dengan analisis
- SELL Signal dengan analisis
- Custom message

✅ **Riwayat Sinyal**
- Simpan semua sinyal ke file
- Lihat riwayat sinyal
- Statistik sinyal

✅ **Test Koneksi**
- Validasi token bot
- Validasi chat ID
- Test pengiriman pesan

## 🚀 Quick Start

### 1. Setup Konfigurasi

**Edit file `config.py`:**

```python
# Ganti dengan token bot Anda
BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567"

# Ganti dengan chat ID Anda
CHAT_ID = "987654321"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Bot

**Untuk menu interaktif:**
```bash
python interactive_bot.py
```

**Untuk test:**
```bash
python simple_bot.py
```

## 📝 Cara Mendapatkan Token & Chat ID

### 🔑 Mendapatkan Bot Token

1. Buka Telegram → Cari `@BotFather`
2. Ketik `/newbot`
3. Ikuti langkah-langkah
4. Copy token yang diberikan
5. Paste ke `config.py`

### 🆔 Mendapatkan Chat ID

1. Cari bot Anda di Telegram
2. Ketik `/start`
3. Buka URL ini di browser (ganti TOKEN):
   ```
   https://api.telegram.org/botTOKEN/getUpdates
   ```
4. Cari `"chat":{"id": xxxxxx}`
5. Copy ID tersebut
6. Paste ke `config.py`

## 📖 Cara Menggunakan

### Menu Interaktif

```
1. 🟢 Kirim BUY Signal
   - Input symbol, price, MA, RSI, Stochastic
   - Input reason
   - Sinyal dikirim ke Telegram

2. 🔴 Kirim SELL Signal
   - Sama seperti BUY Signal

3. 📊 Lihat Riwayat Sinyal
   - Tampilkan semua sinyal yang pernah dikirim

4. 📈 Statistik Sinyal
   - Total BUY/SELL signals
   - Persentase distribusi

5. 🔍 Test Koneksi
   - Validasi bot token & chat ID
   - Test pengiriman pesan

6. 🗑️  Hapus Riwayat
   - Hapus semua data riwayat
```

## 💻 Contoh Pesan Telegram

### BUY Signal:
```
🟢 BUY SIGNAL

Symbol: EURUSD
Price: 1.0850
MA(20): 1.0820
RSI: 28.5
Stochastic: 18.2

Reason: Price > MA + RSI Oversold
Time: 2024-08-10 15:30:45

⚠️ Lakukan analisa manual sebelum trade!
```

### SELL Signal:
```
🔴 SELL SIGNAL

Symbol: EURUSD
Price: 1.0920
MA(20): 1.0950
RSI: 72.5
Stochastic: 82.1

Reason: Price < MA + RSI Overbought
Time: 2024-08-10 16:45:12

⚠️ Lakukan analisa manual sebelum trade!
```

## 📂 Struktur File

```
telegram_bot/
├── config.py              # Konfigurasi (isi token & chat ID)
├── simple_bot.py          # Core bot logic
├── interactive_bot.py     # Menu interaktif
├── requirements.txt       # Dependencies
├── README.md             # Dokumentasi
└── signals_history.json  # Riwayat sinyal (auto-created)
```

## 🔄 Integrasi dengan MT5

### Opsi 1: Manual Input
- Jalankan bot di PC
- Input sinyal manual dari chart MT5
- Sinyal langsung dikirim ke Telegram

### Opsi 2: Webhook (Advanced)
- Setup server untuk menerima sinyal dari MT5
- MT5 send HTTP request ke bot
- Bot forward ke Telegram

### Opsi 3: File Monitoring
- MT5 write sinyal ke file
- Bot monitor file
- Bot send ke Telegram otomatis

## ⚙️ Konfigurasi Lanjutan

**Edit `config.py` untuk mengubah:**

```python
DEFAULT_SYMBOL = "EURUSD"  # Symbol default
DEFAULT_TIMEFRAME = "M15"   # Timeframe default
PARSE_MODE = "HTML"         # Format pesan
ENABLE_NOTIFICATIONS = True  # Aktifkan notifikasi
```

## 🔘 Troubleshooting

### ❌ "Bot token atau Chat ID belum dikonfigurasi"
**Solusi:**
- Edit file `config.py`
- Isi BOT_TOKEN dan CHAT_ID dengan benar
- Save file
- Run ulang bot

### ❌ "Koneksi gagal"
**Solusi:**
- Periksa koneksi internet
- Periksa bot token valid
- Periksa chat ID valid
- Coba `python simple_bot.py` untuk test

### ❌ "Pesan tidak diterima di Telegram"
**Solusi:**
- Pastikan bot sudah di-add ke Telegram
- Pastikan chat ID benar
- Coba kirim pesan test dari menu

## 📱 Kompatibilitas

- ✅ Windows
- ✅ macOS
- ✅ Linux
- ✅ Python 3.7+

## 📦 Dependencies

- `requests` - HTTP library untuk API Telegram

## ⚠️ Disclaimer

- Bot ini hanya untuk **notifikasi sinyal**
- **TIDAK melakukan auto-trading**
- Anda harus **manual confirm** sebelum trade
- Gunakan akun **demo dulu** untuk testing
- **Risk management** adalah tanggung jawab Anda

## 🤝 Support

Untuk pertanyaan atau bug report:
1. Buka GitHub issues
2. Atau hubungi developer

---

**Happy Trading! 📈**
