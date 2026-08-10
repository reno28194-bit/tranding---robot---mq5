//+------------------------------------------------------------------+
//| Custom Trading Indicator - Signal Combination                     |
//| Menggabungkan MA, RSI, Stochastic, MACD                          |
//+------------------------------------------------------------------+
#property copyright "Custom Indicator 2024"
#property link      "https://github.com"
#property version   "1.0"
#property strict
#property indicator_chart_window
#property indicator_buffers 4
#property indicator_plots   4

//--- Input Parameters
input int MA_Period = 20;
input int RSI_Period = 14;
input int StochK_Period = 5;
input int StochD_Period = 3;

//--- Buffers
double BuySignal[];
double SellSignal[];
double SignalStrength[];
double NeutralZone[];

//--- Indicator handles
int handle_ma, handle_rsi, handle_stochastic, handle_macd;

//+------------------------------------------------------------------+
//| Custom indicator initialization function                          |
//+------------------------------------------------------------------+
int OnInit()
{
    // Set buffer properties
    SetIndexBuffer(0, BuySignal, INDICATOR_DATA);
    SetIndexBuffer(1, SellSignal, INDICATOR_DATA);
    SetIndexBuffer(2, SignalStrength, INDICATOR_DATA);
    SetIndexBuffer(3, NeutralZone, INDICATOR_DATA);
    
    // Set plot properties
    PlotIndexSetInteger(0, PLOT_TYPE, PLOT_TYPE_HISTOGRAM);
    PlotIndexSetInteger(0, PLOT_COLOR_INDEXES, 1);
    PlotIndexSetInteger(0, PLOT_LINE_COLOR, 0, clrGreen);
    PlotIndexSetInteger(0, PLOT_LINE_WIDTH, 2);
    
    PlotIndexSetInteger(1, PLOT_TYPE, PLOT_TYPE_HISTOGRAM);
    PlotIndexSetInteger(1, PLOT_COLOR_INDEXES, 1);
    PlotIndexSetInteger(1, PLOT_LINE_COLOR, 0, clrRed);
    PlotIndexSetInteger(1, PLOT_LINE_WIDTH, 2);
    
    PlotIndexSetInteger(2, PLOT_TYPE, PLOT_TYPE_LINE);
    PlotIndexSetInteger(2, PLOT_COLOR_INDEXES, 1);
    PlotIndexSetInteger(2, PLOT_LINE_COLOR, 0, clrBlue);
    PlotIndexSetInteger(2, PLOT_LINE_WIDTH, 1);
    
    PlotIndexSetInteger(3, PLOT_TYPE, PLOT_TYPE_LINE);
    PlotIndexSetInteger(3, PLOT_COLOR_INDEXES, 1);
    PlotIndexSetInteger(3, PLOT_LINE_COLOR, 0, clrGray);
    PlotIndexSetInteger(3, PLOT_LINE_WIDTH, 1);
    
    // Create indicators
    handle_ma = iMA(_Symbol, _Period, MA_Period, 0, MODE_SMA, PRICE_CLOSE);
    handle_rsi = iRSI(_Symbol, _Period, RSI_Period, PRICE_CLOSE);
    handle_stochastic = iStochastic(_Symbol, _Period, StochK_Period, StochD_Period, 3, MODE_SMA, STO_LOWHIGH);
    handle_macd = iMACD(_Symbol, _Period, 12, 26, 9, PRICE_CLOSE);
    
    IndicatorSetString(INDICATOR_SHORTNAME, "Signal Analyzer");
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Custom indicator iteration function                               |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
    if(rates_total < 100)
        return rates_total;
    
    for(int i = prev_calculated; i < rates_total; i++)
    {
        // Get indicator values
        double ma = iMAOnArray(close, i, MA_Period);
        double rsi = GetRSIValue(i);
        double stoch_k = GetStochasticValue(0, i);
        double stoch_d = GetStochasticValue(1, i);
        double macd = GetMACDValue(0, i);
        
        // Calculate signal strength (0-100)
        double buy_strength = CalculateBuySignal(close[i], ma, rsi, stoch_k, stoch_d, macd);
        double sell_strength = CalculateSellSignal(close[i], ma, rsi, stoch_k, stoch_d, macd);
        
        // Set buffer values
        if(buy_strength > sell_strength)
        {
            BuySignal[i] = buy_strength;
            SellSignal[i] = 0;
            SignalStrength[i] = buy_strength;
        }
        else if(sell_strength > buy_strength)
        {
            BuySignal[i] = 0;
            SellSignal[i] = sell_strength;
            SignalStrength[i] = -sell_strength;
        }
        else
        {
            BuySignal[i] = 0;
            SellSignal[i] = 0;
            SignalStrength[i] = 0;
        }
        
        NeutralZone[i] = 0;
    }
    
    return rates_total;
}

//+------------------------------------------------------------------+
//| Calculate BUY Signal Strength (0-100)                             |
//+------------------------------------------------------------------+
double CalculateBuySignal(double close, double ma, double rsi, double stoch_k, double stoch_d, double macd)
{
    double score = 0;
    
    // Price above MA = 20 points
    if(close > ma)
        score += 20;
    
    // RSI Oversold = 30 points
    if(rsi < 30)
        score += 30;
    else if(rsi < 40)
        score += 15;
    
    // Stochastic Oversold = 25 points
    if(stoch_k < 20)
        score += 25;
    else if(stoch_k < 30)
        score += 12;
    
    // Stochastic K > D = 15 points
    if(stoch_k > stoch_d)
        score += 15;
    
    // MACD Positive = 10 points
    if(macd > 0)
        score += 10;
    
    return MathMin(score, 100);
}

//+------------------------------------------------------------------+
//| Calculate SELL Signal Strength (0-100)                            |
//+------------------------------------------------------------------+
double CalculateSellSignal(double close, double ma, double rsi, double stoch_k, double stoch_d, double macd)
{
    double score = 0;
    
    // Price below MA = 20 points
    if(close < ma)
        score += 20;
    
    // RSI Overbought = 30 points
    if(rsi > 70)
        score += 30;
    else if(rsi > 60)
        score += 15;
    
    // Stochastic Overbought = 25 points
    if(stoch_k > 80)
        score += 25;
    else if(stoch_k > 70)
        score += 12;
    
    // Stochastic K < D = 15 points
    if(stoch_k < stoch_d)
        score += 15;
    
    // MACD Negative = 10 points
    if(macd < 0)
        score += 10;
    
    return MathMin(score, 100);
}

//+------------------------------------------------------------------+
//| Helper: Moving Average on Array                                   |
//+------------------------------------------------------------------+
double iMAOnArray(const double &array[], int index, int period)
{
    if(index < period)
        return 0;
    
    double sum = 0;
    for(int i = 0; i < period; i++)
        sum += array[index - i];
    
    return sum / period;
}

//+------------------------------------------------------------------+
//| Get RSI Value                                                    |
//+------------------------------------------------------------------+
double GetRSIValue(int shift)
{
    double rsi[];
    ArraySetAsSeries(rsi, true);
    
    if(CopyBuffer(handle_rsi, 0, shift, 1, rsi) > 0)
        return rsi[0];
    
    return 50;
}

//+------------------------------------------------------------------+
//| Get Stochastic Value                                              |
//+------------------------------------------------------------------+
double GetStochasticValue(int buffer, int shift)
{
    double stoch[];
    ArraySetAsSeries(stoch, true);
    
    if(CopyBuffer(handle_stochastic, buffer, shift, 1, stoch) > 0)
        return stoch[0];
    
    return 50;
}

//+------------------------------------------------------------------+
//| Get MACD Value                                                   |
//+------------------------------------------------------------------+
double GetMACDValue(int buffer, int shift)
{
    double macd[];
    ArraySetAsSeries(macd, true);
    
    if(CopyBuffer(handle_macd, buffer, shift, 1, macd) > 0)
        return macd[0];
    
    return 0;
}
