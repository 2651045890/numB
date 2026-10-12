"""Port of sources/SM_00e193a1cd7e5b89.pine (4H Engulfing Candle Strategy).

Pine v5. The live body is two mirrored blocks:

    bullishEngulfing = close > open[1] and open < close[1] and open <= open[1] and close >= close[1]
    bearishEngulfing = close < open[1] and open > close[1] and open >= open[1] and close <= close[1]

    if bullishEngulfing
        tpPrice := close + (close - open) * tpMultiplier
        slPrice := close - slTicks * syminfo.mintick
        strategy.entry("Buy", strategy.long)
        strategy.exit("TP/SL", "Buy", limit=tpPrice, stop=slPrice)
    if bearishEngulfing
        tpPrice := close - (open - close) * tpMultiplier
        slPrice := close + slTicks * syminfo.mintick
        strategy.entry("Sell", strategy.short)
        strategy.exit("TP/SL", "Sell", limit=tpPrice, stop=slPrice)

So: a two-candle body-engulfing pattern on the chart's own period fires a market
entry in the direction of the engulfing candle, with an OCA exit resting at a
take-profit one body-length away and a stop `slTicks` ticks away. Both orders
are placed while the script evaluates the signal bar's close, so -- Pine's
default timing -- the entry fills at the NEXT bar's open while the two exit legs
are already resting and can trigger on that same fill bar.

The take-profit distance uses the SIGNAL bar's body (`close - open` of the
engulfing candle, i.e. before the fill), not the fill price; the stop distance
is a fixed tick count, so it does not scale with price at all. Both are
reproduced verbatim.

`strategy()` declares default_qty_type = strategy.percent_of_equity with
default_qty_value = 10, so each entry commits 10% of strategy.equity as of the
signal bar's close (Pine freezes the quantity before the next bar opens). No
commission_type/value is declared, so Pine's documented 0% applies; pyramiding
is not declared, so Pine's documented default of 0 applies (an entry placed
while a same-direction position is open is refused). The backtest header gives
initial_capital 1000000 (the strategy() call does not override it).

FIDELITY -- translation choices and source/original mismatches:

1. TIMEFRAME. The `/*backtest` header says `period: 1d` (with `basePeriod: 1h`),
   and that is what this port declares -- but the strategy's title, its code
   comments ("on 4H timeframe", "Compute ... on the 4H series") and every prose
   section of the source md describe a 4-HOUR strategy. The header and the name
   disagree; the header is authoritative for a backtest, so `timeframe = "1d"`.
   A port cannot honour both, and the engulfing conditions are evaluated on
   whatever period the chart carries, so the declared period changes which
   candles are being compared.
2. `syminfo.mintick` is exchange metadata, not a value the source pins down.
   The source was backtested on Futures_Binance BTC_USDT, whose tick is 0.1, so
   the port uses the base class's `source_mintick = 0.1` (the same value its
   PineBrokerConfig receives). With `slTicks = 100` that is a stop 10 USDT from
   the signal close REGARDLESS of the price level -- about 0.02% at the prices
   in the local history, i.e. far inside any bar's range. The stop distance is
   therefore highly sensitive to a tick size the source never states, and a
   different venue tick would change every trade. Not silently adjusted.
3. `slPrice := entryPrice - slTicks * syminfo.mintick` where `entryPrice` was
   just assigned `close` -- so it IS `close - slTicks * mintick`. Substituted,
   no behaviour change.
4. `var float entryPrice/tpPrice/slPrice` persist across bars and are plotted as
   steplines. The three `plot()` calls are display-only (Pine's plots have no
   order effect) and are not reproduced; the variables only ever feed the exits
   placed in the same block that assigns them, so carrying them at their
   previous-bar value has no trading effect.
5. Both directions use the SAME exit id ("TP/SL"). Pine keeps one order per id,
   so a bearish signal REPLACES a resting bullish exit (and vice versa) rather
   than adding a second one; pine_engine models this in `_place`. The reversal
   itself is Pine's normal netting entry, also modelled by the engine.
6. The take-profit is a resting LIMIT and the stop a resting STOP: both fill
   INSIDE a bar on the original platform. pine_engine evaluates them together
   as an OCA group on the fill bar and every bar after, and exposes the levels
   as `pine_limit_level` / `pine_stop_level`; run_pine emits no next-open exit
   signal for them. The port base mirrors the stop into `custom_stoploss` and
   the limit into the ROI hooks, so a Freqtrade backtest reaches the same
   levels.
7. Within-bar ordering is a modelled choice (PINE_SEMANTICS.md section 2): when
   one bar's range spans both legs, the engine takes the price worse for the
   position, and it does not model `basePeriod: 1h` intrabar fills.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta  # noqa: F401  (no ta.* builtin is used by this source)
from pine_port_base import PinePortBase


class SMEngulfing4h_00e193(PinePortBase, IStrategy):
    source_id = "SM_00e193a1cd7e5b89"
    source_file = (
        "4小时时间框架上的吞没形态交易策略与动态止盈止损优化-"
        "4-Hour-Timeframe-Engulfing-Pattern-Trading-Strategy-with-"
        "Dynamic-Take-Profit-and-Stop-Loss-Optimization.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults = {
        # input.float(1.0, "Take Profit Multiplier", step=0.1)
        "tpMultiplier": 1.0,
        # input.int(100, "Stop Loss Ticks")
        "slTicks": 100,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 10.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # syminfo.mintick: the source's own exchange (Futures_Binance BTC_USDT)
    # quotes in 0.1. Declared so the stop distance and the engine's
    # PineBrokerConfig.mintick cannot drift apart.
    source_mintick = 0.1
    source_fidelity_notes = [
        "TIMEFRAME MISMATCH IN THE SOURCE: the /*backtest header says "
        "`period: 1d`, while the title, the code comments ('on 4H timeframe') "
        "and the whole prose description call it a 4-hour strategy. The header "
        "is authoritative for a backtest, so this port is 1d; on a 4h chart the "
        "same conditions compare different candles. Not silently switched.",
        "syminfo.mintick is exchange metadata the source never states. The port "
        "uses 0.1 (BTC_USDT futures tick), so slTicks=100 is a stop 10 USDT from "
        "the signal close regardless of price level -- about 0.02% at the local "
        "history's prices, i.e. inside any bar's range. A different venue tick "
        "would change every trade; this is the single largest parity risk.",
        "The entry's take-profit is `close + (close - open) * tpMultiplier` using "
        "the SIGNAL bar's body, and the stop is a fixed tick distance -- neither "
        "is anchored to the fill price, which is the next bar's open. Reproduced "
        "as written.",
        "The take-profit is a resting LIMIT exit and the stop a resting STOP "
        "exit: pine_engine fills them INSIDE the bar and exposes them as "
        "pine_limit_level / pine_stop_level, and run_pine emits no next-open exit "
        "signal for them. The port base mirrors the stop into custom_stoploss and "
        "the limit into the ROI hooks.",
        "Both directions place their OCA exit under the SAME order id ('TP/SL'). "
        "Pine keeps one order per id, so the newer signal REPLACES the resting "
        "exit of the other direction; pine_engine models that replacement.",
        "`var float entryPrice/tpPrice/slPrice` persist across bars and are "
        "plotted as steplines; the plots are display-only and the variables never "
        "outlive the block that assigns them, so no display logic is carried.",
        "intrabar sequencing inside a bar (the header's basePeriod: 1h) is not "
        "modelled: pine_engine resolves both OCA legs against the daily bar only, "
        "and on a bar spanning both takes the price worse for the position.",
    ]

    def pine_indicators(self, dataframe, params):
        open_, close = dataframe["open"], dataframe["close"]

        # bullishBodySize = close - open / bearishBodySize = open - close
        # Pine compares against `open[1]` / `close[1]`; on the first bar those
        # are na and the whole conjunction is false, which is what a float
        # comparison against NaN already yields here.
        bullish_engulfing = (
            (close > open_.shift(1))
            & (open_ < close.shift(1))
            & (open_ <= open_.shift(1))
            & (close >= close.shift(1))
        )
        bearish_engulfing = (
            (close < open_.shift(1))
            & (open_ > close.shift(1))
            & (open_ >= open_.shift(1))
            & (close <= close.shift(1))
        )
        dataframe["pine_bullish_engulfing"] = bullish_engulfing.astype(bool)
        dataframe["pine_bearish_engulfing"] = bearish_engulfing.astype(bool)

        # The levels are computed inside the two `if` blocks in the source; per
        # bar they are pure functions of that bar's open/close and the two
        # inputs, so they are materialised for every bar and only READ on a
        # signal bar -- same values, no condition change.
        bullish_body = close - open_
        bearish_body = open_ - close
        dataframe["tp_price_long"] = close + bullish_body * float(params["tpMultiplier"])
        dataframe["sl_price_long"] = close - float(params["slTicks"]) * float(self.source_mintick)
        dataframe["tp_price_short"] = close - bearish_body * float(params["tpMultiplier"])
        dataframe["sl_price_short"] = close + float(params["slTicks"]) * float(self.source_mintick)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "bullish_engulfing": dataframe["pine_bullish_engulfing"].to_numpy(),
            "bearish_engulfing": dataframe["pine_bearish_engulfing"].to_numpy(),
            "tp_price_long": dataframe["tp_price_long"].to_numpy(),
            "sl_price_long": dataframe["sl_price_long"].to_numpy(),
            "tp_price_short": dataframe["tp_price_short"].to_numpy(),
            "sl_price_short": dataframe["sl_price_short"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if bullishEngulfing
        #     entryPrice := close; tpPrice := close + bullishBodySize * tpMultiplier
        #     slPrice := entryPrice - slTicks * syminfo.mintick
        #     strategy.entry("Buy", strategy.long)
        #     strategy.exit("TP/SL", "Buy", limit=tpPrice, stop=slPrice)
        if ctx["bullish_engulfing"][i]:
            broker.entry("Buy", "long")
            broker.exit("TP/SL", "Buy",
                        limit=float(ctx["tp_price_long"][i]),
                        stop=float(ctx["sl_price_long"][i]))

        # if bearishEngulfing ... strategy.entry("Sell", strategy.short) ...
        # (the source tests the bullish block first; only one can be true, since
        # `close > open[1]` and `close < open[1]` are mutually exclusive, but
        # the order is kept as written)
        if ctx["bearish_engulfing"][i]:
            broker.entry("Sell", "short")
            broker.exit("TP/SL", "Sell",
                        limit=float(ctx["tp_price_short"][i]),
                        stop=float(ctx["sl_price_short"][i]))
