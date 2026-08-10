# 📱 Trading Signal Analyzer - MT5 Android

**Hanya Analisa & Sinyal - TIDAK Ada Trading Otomatis!**

Aplikasi ini hanya memberikan notifikasi kapan harus BUY atau SELL berdasarkan analisa indikator.

## 🎯 Fitur

✅ **Sinyal BUY/SELL Real-time**
- Analisa kombinasi 4 indikator
- Notifikasi push ke HP
- Alert suara
- Arrow di chart

✅ **Indikator yang Digunakan**
- Moving Average (MA)
- Relative Strength Index (RSI)
- Stochastic Oscillator
- MACD

✅ **Multiple Timeframe**
- M1, M5, M15, M30, H1, H4, D1

✅ **Tidak Ada Trading Otomatis**
- Hanya signal
- Anda yang ambil keputusan
- Manual trading

## 🚀 Cara Pakai

### Step 1: Install di MT5 Android

```
1. Buka MT5 → Menu → MetaEditor
2. Buat file baru → Expert Advisor
3. Copy paste kode: TradingAnalyzer.mq5
4. Compile (Ctrl+F9)
5. Attach ke chart
```

### Step 2: Aktifkan Notifications

```
1. Chart → Menu → Settings
2. Notifications → ON
3. Sound Alert → ON
4. Allow notifications di Android Settings
```

### Step 3: Monitor Sinyal

```
Tunggu notifikasi BUY atau SELL muncul:
- 🟢 Warna HIJAU = BUY Signal
- 🔴 Warna MERAH = SELL Signal
```

## ⚙️ Parameter yang Bisa Diatur

| Parameter | Default | Keterangan |
|-----------|---------|----------|
| MovingAveragePeriod | 20 | Periode MA |
| RSIPeriod | 14 | Periode RSI |
| RSIOverbought | 70 | RSI overbought threshold |
| RSIOversold | 30 | RSI oversold threshold |
| StochasticKPeriod | 5 | Stochastic K period |
| StochasticDPeriod | 3 | Stochastic D period |
| EnableNotifications | true | Notifikasi push |
| EnableSoundAlert | true | Alert suara |
| EnableArrows | true | Arrow di chart |

## 📊 Sinyal BUY

🟢 **BUY terjadi ketika:**
- Harga > Moving Average
- RSI < 30 (Oversold)
- ATAU Harga > MA + Stochastic < 20

**Contoh Notifikasi:**
```
🟢 BUY SIGNAL on EURUSD
Price: 1.0850
MA(20): 1.0820
RSI: 28.5
Stochastic: 18.2
Reason: Price > MA + RSI Oversold
Time: 2024.08.10 15:30:45
```

## 📊 Sinyal SELL

🔴 **SELL terjadi ketika:**
- Harga < Moving Average
- RSI > 70 (Overbought)
- ATAU Harga < MA + Stochastic > 80

**Contoh Notifikasi:**
```
🔴 SELL SIGNAL on EURUSD
Price: 1.0920
MA(20): 1.0950
RSI: 72.5
Stochastic: 82.1
Reason: Price < MA + RSI Overbought
Time: 2024.08.10 16:45:12
```

## 🎨 Custom Indicator (Optional)

Juga ada indikator custom yang menampilkan signal strength:
- **Bar Hijau** = Strong BUY
- **Bar Merah** = Strong SELL
- **Biru** = Signal strength (naik turun)

Cara install:
```
1. Copy kode: CustomIndicator.mq5
2. Buka MetaEditor
3. Compile dan attach ke chart
4. Akan muncul di window bawah
```

## 💡 Tips Penggunaan

1. **Jangan langsung execute**
   - Dapat signal BUY/SELL
   - Analisa manual juga
   - Konfirmasi sebelum trade

2. **Gunakan Multiple Timeframe**
   - Contoh: M5 untuk signal, H1 untuk trend
   - Hindari counter-trend trading

3. **Set Risk Management**
   - Tentukan SL & TP sebelum trade
   - Jangan all-in
   - Manage position size

4. **Keep Log**
   - Catat setiap signal
   - Catat entry & exit Anda
   - Review setiap minggu

## ⚠️ Disclaimer

- **Ini hanya tool bantu**, bukan garansi profit
- **Forex trading sangat berisiko**
- Bisa kehilangan modal
- Gunakan demo dulu
- Trade dengan uang yang Anda siap rugi

## 🔧 Troubleshooting

**Q: Tidak dapat notifikasi?**
A: 
- Pastikan EnableNotifications = true
- Check Android notification settings
- MT5 app permission di Allow notifications

**Q: Alert suara tidak terdengar?**
A:
- Set EnableSoundAlert = true
- Check volume HP
- File "alert.wav" ada di sistem

**Q: Tidak ada sinyal sama sekali?**
A:
- Check indikator values di journal
- Mungkin market sedang neutral
- Coba timeframe berbeda

---

**Happy Trading! 📈**
