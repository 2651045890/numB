"""Deep port of the Pine v5 strategy from batch_010.

Trading logic reproduced directly from source: Bollinger breakout + RSI + 200 EMA
trend filter + optional volume filter, with N-bar confirmation.  Each accepted
entry immediately installs ATR-priced stop/target orders computed from the
signal bar close, exactly as the Pine source does.
"""
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase

class SMB010_001_EnhancedBollingerBreakout(PinePortBase, IStrategy):
    timeframe = "2d"
    can_short = True
    source_file = "布林带趋势突破增强型量化策略结合指标动量过滤系统-Enhanced-Bollinger-Breakout-Quantitative-Strategy-with-Momentum-Filter-Integration-System.md"
    source_defaults = dict(length=20, mult=2.0, rsi_length=14, rsi_midline=50,
                           risk_reward_ratio=1.5, atr_multiplier=1.5,
                           volume_filter=True, trend_filter_length=200,
                           trade_direction="Both", confirm_candles=2)
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_initial_capital = 1_000_000.0
    source_pyramiding = 0
    source_commission_percent = 0.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "confirm_condition is reproduced as a rolling all-true window, including current bar.",
        "strategy.exit stop/limit levels are frozen from the signal bar close and ATR when submitted, as in source.",
        "Plots/tooltips are display-only and omitted."
    ]

    def pine_indicators(self, dataframe, params):
        close, volume = dataframe["close"], dataframe["volume"]
        basis = ta.pine_sma(close, int(params["length"]))
        dev = float(params["mult"]) * ta.pine_stdev(close, int(params["length"]))
        upper, lower = basis + dev, basis - dev
        rsi = ta.pine_rsi(close, int(params["rsi_length"]))
        atr = ta.pine_atr(dataframe, 14)
        vol_ok = volume > ta.pine_sma(volume, 20)
        ema = ta.pine_ema(close, int(params["trend_filter_length"]))
        vf = bool(params["volume_filter"])
        raw_long = (close > upper * 1.01) & (rsi > float(params["rsi_midline"])) & ((~vol_ok if False else vol_ok) if vf else True) & (close > ema)
        raw_short = (close < lower * 0.99) & (rsi < float(params["rsi_midline"])) & (vol_ok if vf else True) & (close < ema)
        n = int(params["confirm_candles"])
        long_sig = raw_long.astype(int).rolling(n, min_periods=n).sum().eq(n)
        short_sig = raw_short.astype(int).rolling(n, min_periods=n).sum().eq(n)
        dataframe["pine_upper"], dataframe["pine_lower"] = upper, lower
        dataframe["pine_rsi"], dataframe["pine_atr"], dataframe["pine_ema"] = rsi, atr, ema
        dataframe["pine_long"], dataframe["pine_short"] = long_sig, short_sig
        return dataframe

    def pine_context(self, dataframe, params):
        return {"close": dataframe["close"].to_numpy(float), "atr": dataframe["pine_atr"].to_numpy(float),
                "long": dataframe["pine_long"].to_numpy(bool), "short": dataframe["pine_short"].to_numpy(bool),
                "direction": params["trade_direction"], "atr_mult": float(params["atr_multiplier"]),
                "rr": float(params["risk_reward_ratio"])}

    def pine_script(self, broker, i, ctx):
        c, a = ctx["close"][i], ctx["atr"][i]
        if ctx["long"][i] and ctx["direction"] in ("Long", "Both"):
            broker.entry("Long", "long")
            broker.exit("Exit Long", "Long", stop=c-ctx["atr_mult"]*a, limit=c+ctx["atr_mult"]*ctx["rr"]*a)
        if ctx["short"][i] and ctx["direction"] in ("Short", "Both"):
            broker.entry("Short", "short")
            broker.exit("Exit Short", "Short", stop=c+ctx["atr_mult"]*a, limit=c-ctx["atr_mult"]*ctx["rr"]*a)
