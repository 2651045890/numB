"""Port of sources/SM_15700225ef7b4213.pine
(batch_001/Bollinger-Bands-Breakout-Strategy-布林线突破策略.md).

Pine v5. Bollinger Bands, entered against the bands in both directions, plus a
third block that asks for an extra entry while `strategy.opentrades` is below
the `pyramiding` INPUT:

    length = input(20, title="Bollinger Bands Length")
    multiplier = input(2.0, title="Multiplier")
    pyramiding = input(5, title="Pyramiding")

    basis = ta.sma(close, length)
    dev = multiplier * ta.stdev(close, length)
    upper_band = basis + dev
    lower_band = basis - dev

    buy_signal  = close <= lower_band
    sell_signal = close >= upper_band

    if (buy_signal)
        strategy.entry("Buy", strategy.long)
    if (sell_signal)
        strategy.entry("Sell", strategy.short)

    if (strategy.opentrades < pyramiding)
        strategy.entry("Buy", strategy.long)
    else if (strategy.opentrades > pyramiding)
        strategy.entry("Sell", strategy.short)

THE NAME `pyramiding` IS NOT THE STRATEGY'S PYRAMIDING SETTING. The
`strategy(...)` call declares only `title` and `overlay`, so Pine's own default
`pyramiding = 0` applies and the engine's limit is 0; the input named
`Pyramiding` (default 5) is an ordinary input read by the two comparisons in the
third block. Both are reproduced as written: the input stays in
`source_defaults` and is used in the comparisons, while `source_pyramiding` is
0. The consequence -- measured, and the reason this matters -- is that the third
block cannot stack anything: while a position is open in the same direction the
engine refuses the extra entry, and the block only ever opens a position when
`strategy.opentrades` is 0, i.e. when the strategy is flat.

`strategy()` declares nothing else, so every other property is Pine's
documented default: `default_qty_type = strategy.fixed` with
`default_qty_value = 1`, commission 0%, initial capital 1000000,
process_orders_on_close false, calc_on_order_fills false. No `qty=` is passed,
so every entry is one contract.

ORDER OF THE THREE BLOCKS is kept exactly: the buy_signal entry, then the
sell_signal entry, then the opentrades comparison (an if / ELSE-IF, so a bar
that is flat can only take the first branch of the third block). Both of the
first two blocks can be true on one bar -- `close <= lower_band` and
`close >= upper_band` are mutually exclusive only while the bands are not
degenerate -- and on a flat bar the third block adds a second Buy entry behind
them.

MEASURED, 2024-01-01..2025-01-01 BTC/USDT:USDT 1h (`verify_chain.py --port
SM_15700225ef7b4213`): `match` -- 808 trades on both sides, 0 open-date, 0
close-date and 0 direction mismatches, `max_price_gap` 0.0, and no stake vetoes.
Measured on the same window: 537 buy signals and 601 sell signals over 8785
bars, and the bands first become valid at bar 19 (a 20-bar window).

FIDELITY:

* `ta.sma` / `ta.stdev` are `pine_ta.pine_sma` / `pine_ta.pine_stdev`, which is
  the POPULATION standard deviation (ddof=0), the definition Pine's ta.stdev
  uses; na until `length` bars have elapsed, so the first 19 bars have no bands
  and both signals are false there.
* `strategy.opentrades < pyramiding` and `> pyramiding` are read from the broker
  at RUN time, not precomputed: the value changes as fills arrive, so a
  precomputed column would not be the same condition.
* `sell_signal = close >= upper_band` and `buy_signal = close <= lower_band` are
  reproduced with the source's own comparison directions. Note the inversion
  against the usual "breakout" reading of the name: the long entry is at the
  LOWER band and the short entry at the UPPER band.
* MD-vs-CODE, recorded not reconciled: the prose describes the entries as
  "价格突破上轨...可以做多;突破下轨...可以做空" (break above the upper band ->
  long, below the lower -> short), which is the OPPOSITE of the code's
  `close <= lower_band -> Buy` / `close >= upper_band -> Sell`. The code is
  followed.
* MD-vs-CODE, recorded not reconciled: the prose presents pyramiding as the
  strategy's core mechanism ("当持仓数量未达到设定的最大值时,会继续按原有方向加仓",
  adds on in the original direction while the count is below the maximum) and
  the source's third block does ask for that, but the `strategy()` call does not
  declare `pyramiding`, so Pine's default 0 forbids the added entry. The
  prose's described behaviour cannot occur; both the input and the block are
  kept as written and the divergence is recorded rather than resolved.
* With the default input of 5 and the default strategy pyramiding of 0 the
  engine holds at most one entry at a time, so `strategy.opentrades` is 0 or 1
  and the `> pyramiding` (i.e. > 5) branch of the else-if is unreachable on the
  defaults. It is reproduced anyway; a caller overriding the input can reach it.
* The three `plot` calls (basis, upper_band, lower_band) are display-only.
* `can_short` is True: the source opens short positions.
* No stop, no take-profit, no `strategy.exit`, no `strategy.close` and no
  trailing stop exist anywhere in the source, so `source_reproduce_stops` is
  False and a position ends only when an opposite entry reverses it.
* The /*backtest header declares period: 1h on Futures_Binance BTC_USDT, so
  `timeframe` is "1h"; `basePeriod: 15m` is the FMZ backtester's own granularity
  for filling the 1h bars.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the last of those separately.
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsBreakout_157002(PinePortBase, IStrategy):
    source_id = "SM_15700225ef7b4213"
    source_file = "Bollinger-Bands-Breakout-Strategy-布林线突破策略.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        # `pyramiding` is an INPUT here, not the strategy() setting; see the
        # module docstring.
        "length": 20,
        "multiplier": 2.0,
        "pyramiding": 5,
    }
    # strategy("Bollinger Bands Breakout Strategy", overlay=true) declares
    # neither sizing nor pyramiding, so Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop anywhere in the source.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The input named `pyramiding` (default 5) is NOT the strategy's "
        "pyramiding setting. strategy() declares only title and overlay, so "
        "Pine's default pyramiding = 0 is what the engine enforces; the input is "
        "used only by the two comparisons in the third block. Both are "
        "reproduced as written.",
        "Because the strategy pyramiding is 0, the third block's "
        "`strategy.entry(\"Buy\", strategy.long)` cannot stack an entry on an "
        "open long: the engine refuses it, so the block only acts on a flat bar. "
        "The `opentrades > 5` branch is unreachable with the default input, "
        "since opentrades never exceeds 1; it is kept because a caller "
        "overriding the input can reach it.",
        "`strategy.opentrades` is read from the broker at run time in both "
        "comparisons, not precomputed as a column.",
        "ta.stdev is the POPULATION standard deviation (ddof=0) in pine_ta, which "
        "is Pine's definition; the bands are na until 20 bars have elapsed.",
        "Both entries are plain market orders with no qty argument, so the fixed "
        "default of 1 contract sizes them and the engine fills them at the next "
        "bar's open.",
        "MD-vs-CODE, recorded not reconciled: the prose says a break ABOVE the "
        "upper band is the long signal and a break BELOW the lower band the "
        "short one; the code is the opposite (close <= lower_band -> Buy, "
        "close >= upper_band -> Sell). Code followed.",
        "MD-vs-CODE, recorded not reconciled: the prose presents pyramiding as "
        "the strategy's core mechanism, but strategy() does not declare it, so "
        "Pine's default 0 forbids the added entry the third block asks for. The "
        "described behaviour cannot occur with the source's own defaults.",
        "The two independent entry ifs (buy_signal, sell_signal) are kept "
        "separate and in source order even though the conditions are mutually "
        "exclusive on non-degenerate bands; the third block keeps its else-if.",
        "There is no exit of any kind -- no strategy.close, no strategy.exit, no "
        "stop or limit -- so a position is only ever left by the opposite entry "
        "reversing it, and source_reproduce_stops is False.",
        "The three plot calls are display-only.",
        "The md's argument table has three rows (20 / 2 / 5) and the source has "
        "three input() calls; the defaults recorded here are the code's "
        "(multiplier is 2.0, which the table renders as 2).",
        "The /*backtest header declares period: 1h; basePeriod: 15m is the FMZ "
        "backtester's own filling granularity, not the strategy's period.",
        "Leverage, margin, liquidation, funding and venue contract-step rounding "
        "are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        length = int(params["length"])

        # basis = ta.sma(close, length); dev = multiplier * ta.stdev(close, length)
        basis = ta.pine_sma(close, length)
        dev = float(params["multiplier"]) * ta.pine_stdev(close, length)
        upper_band = basis + dev
        lower_band = basis - dev

        # buy_signal = close <= lower_band ; sell_signal = close >= upper_band
        buy_signal = close <= lower_band
        sell_signal = close >= upper_band

        dataframe["pine_basis"] = basis
        dataframe["pine_dev"] = dev
        dataframe["pine_upper_band"] = upper_band
        dataframe["pine_lower_band"] = lower_band
        dataframe["pine_buy_signal"] = buy_signal.fillna(False)
        dataframe["pine_sell_signal"] = sell_signal.fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(dtype=bool),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(dtype=bool),
            # The input, not source_pyramiding -- see the module docstring.
            "pyramiding": int(params["pyramiding"]),
        }

    def pine_script(self, broker, i, ctx):
        # if (buy_signal)
        #     strategy.entry("Buy", strategy.long)
        if ctx["buy_signal"][i]:
            broker.entry("Buy", "long")

        # if (sell_signal)
        #     strategy.entry("Sell", strategy.short)
        if ctx["sell_signal"][i]:
            broker.entry("Sell", "short")

        # if (strategy.opentrades < pyramiding)
        #     strategy.entry("Buy", strategy.long)
        # else if (strategy.opentrades > pyramiding)
        #     strategy.entry("Sell", strategy.short)
        if broker.open_trades < ctx["pyramiding"]:
            broker.entry("Buy", "long")
        elif broker.open_trades > ctx["pyramiding"]:
            broker.entry("Sell", "short")
