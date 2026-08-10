//+------------------------------------------------------------------+
//| Trading Signal Analyzer MT5 untuk Android                         |
//| Hanya memberikan sinyal BUY/SELL, TIDAK melakukan trading        |
//+------------------------------------------------------------------+
#property copyright "Trading Analyzer 2024"
#property link      "https://github.com"
#property version   "1.0"
#property strict
#property description "Signal Analyzer - Buy/Sell Signals Only"

//--- Input Parameters
input int      MovingAveragePeriod = 20;  // Moving Average Period
input int      RSIPeriod = 14;            // RSI Period
input double   RSIOverbought = 70;        // RSI Overbought Level
input double   RSIOversold = 30;          // RSI Oversold Level
input int      StochasticKPeriod = 5;    // Stochastic %K
input int      StochasticDPeriod = 3;    // Stochastic %D
input bool     EnableNotifications = true; // Aktifkan Notifikasi
input bool     EnableSoundAlert = true;   // Aktifkan Alert Suara
input bool     EnableArrows = true;       // Tampilkan Arrow di Chart
input int      CheckInterval = 5;         // Check setiap X detik

//--- Global Variables
int handle_ma, handle_rsi, handle_stochastic;
datetime last_signal_time = 0;
int signal_cooldown = 60; // Cooldown 60 detik antar signal

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    // Create Moving Average indicator
    handle_ma = iMA(_Symbol, _Period, MovingAveragePeriod, 0, MODE_SMA, PRICE_CLOSE);
    if(handle_ma == INVALID_HANDLE)
    {
        Alert("Error creating MA: ", GetLastError());
        return INIT_FAILED;
    }
    
    // Create RSI indicator
    handle_rsi = iRSI(_Symbol, _Period, RSIPeriod, PRICE_CLOSE);
    if(handle_rsi == INVALID_HANDLE)
    {
        Alert("Error creating RSI: ", GetLastError());
        return INIT_FAILED;
    }
    
    // Create Stochastic indicator
    handle_stochastic = iStochastic(_Symbol, _Period, StochasticKPeriod, StochasticDPeriod, 3, MODE_SMA, STO_LOWHIGH);
    if(handle_stochastic == INVALID_HANDLE)
    {
        Alert("Error creating Stochastic: ", GetLastError());
        return INIT_FAILED;
    }
    
    Print("═══════════════════════════════════════");
    Print("Trading Signal Analyzer Started!");
    Print("═══════════════════════════════════════");
    Print("Symbol: ", _Symbol, " | Timeframe: ", _Period);
    Print("MA Period: ", MovingAveragePeriod);
    Print("RSI Period: ", RSIPeriod, " (OB: ", RSIOverbought, " OS: ", RSIOversold, ")");
    Print("Stochastic: ", StochasticKPeriod, "/", StochasticDPeriod);
    Print("═══════════════════════════════════════");
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    // Release indicator handles
    if(handle_ma != INVALID_HANDLE)
        IndicatorRelease(handle_ma);
    if(handle_rsi != INVALID_HANDLE)
        IndicatorRelease(handle_rsi);
    if(handle_stochastic != INVALID_HANDLE)
        IndicatorRelease(handle_stochastic);
    
    Print("Trading Signal Analyzer Removed!");
}

//+------------------------------------------------------------------+
//| Expert tick function                                              |
//+------------------------------------------------------------------+
void OnTick()
{
    // Get current price values
    double close_price = iClose(_Symbol, _Period, 0);
    double ma_value = GetMA(0);
    double rsi_value = GetRSI(0);
    double stoch_k = GetStochasticK(0);
    double stoch_d = GetStochasticD(0);
    
    // Check if enough time has passed since last signal
    if((TimeCurrent() - last_signal_time) < signal_cooldown)
        return;
    
    // Analyze and generate signals
    AnalyzeMarket(close_price, ma_value, rsi_value, stoch_k, stoch_d);
}

//+------------------------------------------------------------------+
//| Analyze Market and Generate Signals                               |
//+------------------------------------------------------------------+
void AnalyzeMarket(double close, double ma, double rsi, double stoch_k, double stoch_d)
{
    // BUY Signal Conditions
    bool buy_signal = false;
    string buy_reason = "";
    
    // Condition 1: Price above MA + RSI Oversold
    if(close > ma && rsi < RSIOversold)
    {
        buy_signal = true;
        buy_reason = "Price > MA + RSI Oversold (" + DoubleToString(rsi, 2) + ")";
    }
    
    // Condition 2: Price above MA + Stochastic Oversold
    if(close > ma && stoch_k < 20)
    {
        buy_signal = true;
        buy_reason = "Price > MA + Stochastic Oversold (" + DoubleToString(stoch_k, 2) + ")";
    }
    
    // Condition 3: Stochastic Crossover (K above D)
    if(stoch_k > stoch_d && stoch_k < 50 && GetStochasticK(1) <= GetStochasticD(1))
    {
        buy_signal = true;
        buy_reason = "Stochastic Bullish Crossover";
    }
    
    // SELL Signal Conditions
    bool sell_signal = false;
    string sell_reason = "";
    
    // Condition 1: Price below MA + RSI Overbought
    if(close < ma && rsi > RSIOverbought)
    {
        sell_signal = true;
        sell_reason = "Price < MA + RSI Overbought (" + DoubleToString(rsi, 2) + ")";
    }
    
    // Condition 2: Price below MA + Stochastic Overbought
    if(close < ma && stoch_k > 80)
    {
        sell_signal = true;
        sell_reason = "Price < MA + Stochastic Overbought (" + DoubleToString(stoch_k, 2) + ")";
    }
    
    // Condition 3: Stochastic Crossover (K below D)
    if(stoch_k < stoch_d && stoch_k > 50 && GetStochasticK(1) >= GetStochasticD(1))
    {
        sell_signal = true;
        sell_reason = "Stochastic Bearish Crossover";
    }
    
    // Execute signals
    if(buy_signal && !sell_signal)
    {
        SendBuySignal(buy_reason, close, ma, rsi, stoch_k);
        last_signal_time = TimeCurrent();
    }
    else if(sell_signal && !buy_signal)
    {
        SendSellSignal(sell_reason, close, ma, rsi, stoch_k);
        last_signal_time = TimeCurrent();
    }
}

//+------------------------------------------------------------------+
//| Send BUY Signal                                                   |
//+------------------------------------------------------------------+
void SendBuySignal(string reason, double price, double ma, double rsi, double stoch)
{
    string message = "🟢 BUY SIGNAL\n";
    message += "Price: " + DoubleToString(price, _Digits) + "\n";
    message += "MA(" + IntegerToString(MovingAveragePeriod) + "): " + DoubleToString(ma, _Digits) + "\n";
    message += "RSI: " + DoubleToString(rsi, 2) + "\n";
    message += "Stochastic: " + DoubleToString(stoch, 2) + "\n";
    message += "Reason: " + reason + "\n";
    message += "Time: " + TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES);
    
    Print("═══════════════════════════════════════");
    Print(message);
    Print("═══════════════════════════════════════");
    
    // Send Notification
    if(EnableNotifications)
        SendNotification("🟢 BUY SIGNAL on " + _Symbol + " - " + reason);
    
    // Play Sound
    if(EnableSoundAlert)
        PlaySound("alert.wav");
    
    // Draw Arrow
    if(EnableArrows)
        DrawBuyArrow(price);
}

//+------------------------------------------------------------------+
//| Send SELL Signal                                                  |
//+------------------------------------------------------------------+
void SendSellSignal(string reason, double price, double ma, double rsi, double stoch)
{
    string message = "🔴 SELL SIGNAL\n";
    message += "Price: " + DoubleToString(price, _Digits) + "\n";
    message += "MA(" + IntegerToString(MovingAveragePeriod) + "): " + DoubleToString(ma, _Digits) + "\n";
    message += "RSI: " + DoubleToString(rsi, 2) + "\n";
    message += "Stochastic: " + DoubleToString(stoch, 2) + "\n";
    message += "Reason: " + reason + "\n";
    message += "Time: " + TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES);
    
    Print("═══════════════════════════════════════");
    Print(message);
    Print("═══════════════════════════════════════");
    
    // Send Notification
    if(EnableNotifications)
        SendNotification("🔴 SELL SIGNAL on " + _Symbol + " - " + reason);
    
    // Play Sound
    if(EnableSoundAlert)
        PlaySound("alert.wav");
    
    // Draw Arrow
    if(EnableArrows)
        DrawSellArrow(price);
}

//+------------------------------------------------------------------+
//| Draw BUY Arrow on Chart                                           |
//+------------------------------------------------------------------+
void DrawBuyArrow(double price)
{
    static int arrow_count = 0;
    arrow_count++;
    
    string arrow_name = "BUY_ARROW_" + IntegerToString(arrow_count);
    
    ObjectCreate(0, arrow_name, OBJ_ARROW, 0, TimeCurrent(), price);
    ObjectSetInteger(0, arrow_name, OBJPROP_ARROWCODE, 233); // Green up arrow
    ObjectSetInteger(0, arrow_name, OBJPROP_COLOR, clrGreen);
    ObjectSetInteger(0, arrow_name, OBJPROP_WIDTH, 2);
}

//+------------------------------------------------------------------+
//| Draw SELL Arrow on Chart                                          |
//+------------------------------------------------------------------+
void DrawSellArrow(double price)
{
    static int arrow_count = 0;
    arrow_count++;
    
    string arrow_name = "SELL_ARROW_" + IntegerToString(arrow_count);
    
    ObjectCreate(0, arrow_name, OBJ_ARROW, 0, TimeCurrent(), price);
    ObjectSetInteger(0, arrow_name, OBJPROP_ARROWCODE, 234); // Red down arrow
    ObjectSetInteger(0, arrow_name, OBJPROP_COLOR, clrRed);
    ObjectSetInteger(0, arrow_name, OBJPROP_WIDTH, 2);
}

//+------------------------------------------------------------------+
//| Get Moving Average Value                                          |
//+------------------------------------------------------------------+
double GetMA(int shift)
{
    double ma[];
    ArraySetAsSeries(ma, true);
    
    if(CopyBuffer(handle_ma, 0, shift, 1, ma) > 0)
        return ma[0];
    
    return 0;
}

//+------------------------------------------------------------------+
//| Get RSI Value                                                    |
//+------------------------------------------------------------------+
double GetRSI(int shift)
{
    double rsi[];
    ArraySetAsSeries(rsi, true);
    
    if(CopyBuffer(handle_rsi, 0, shift, 1, rsi) > 0)
        return rsi[0];
    
    return 0;
}

//+------------------------------------------------------------------+
//| Get Stochastic %K Value                                           |
//+------------------------------------------------------------------+
double GetStochasticK(int shift)
{
    double stoch[];
    ArraySetAsSeries(stoch, true);
    
    if(CopyBuffer(handle_stochastic, 0, shift, 1, stoch) > 0)
        return stoch[0];
    
    return 0;
}

//+------------------------------------------------------------------+
//| Get Stochastic %D Value                                           |
//+------------------------------------------------------------------+
double GetStochasticD(int shift)
{
    double stoch[];
    ArraySetAsSeries(stoch, true);
    
    if(CopyBuffer(handle_stochastic, 1, shift, 1, stoch) > 0)
        return stoch[0];
    
    return 0;
}

//+------------------------------------------------------------------+
//| Chart Event Handler                                               |
//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long& lparam, const double& dparam, const string& sparam)
{
    // Optional: Handle chart clicks or other events
}
