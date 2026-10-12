"""Port of sources/SM_8b2e5bfa9b6599c7.pine (batch_001/CCI零点反转交易策略CCI-Zero-Cross-Trading-Strategy.md).

Pine v2. The Commodity Channel Index against its own +/-100 levels. Both
entries are resting STOP orders, and each is cancelled again on any bar its
cross did not occur:

    CCIlength     = input(20, minval=1, title="CCI Period Length")
    CCIoverSold   = -100          // literal, not an input
    CCIoverBought = 100           // literal, not an input
    CCI  = cci(hlc3, CCIlength)
    price = hlc3
    vcci = cci(price, CCIlength)  // identical to CCI; used only by the guard

    if (not na(vcci))
        if (crossover(CCI, CCIoverSold))
            strategy.entry("CCI_L", strategy.long,  stop=CCIoverSold)
        else
            strategy.cancel(id="CCI_L")
        if (crossunder(CCI, CCIoverBought))
            strategy.entry("CCI_S", strategy.short, stop=CCIoverBought)
        else
            strategy.cancel(id="CCI_S")

`strategy()` declares only `title`, `shorttitle` and `overlay`, so Pine's
documented defaults apply: `default_qty_type = strategy.fixed`,
`default_qty_value = 1`, `commission_value = 0`, `pyramiding = 0`, initial
capital 1000000 and `process_orders_on_close = false`. The `/*backtest` header
declares `period: 1d` on Futures_Binance BTC_USDT, so `timeframe` is "1d"; its
`basePeriod: 1h` is the FMZ backtester's own granularity for filling those
daily bars, not the strategy's period.

FIDELITY:

* The md's "策略原理" says the entries trigger on CCI crossing the ZERO line
  ("CCI从下向上穿过零线时产生做多信号"), with the -100/100 levels used only as
  stops. The source does the opposite: the entry events are
  `crossover(CCI, -100)` / `crossunder(CCI, 100)` and the CCI overbought /
  oversold levels ARE the trigger levels. The source wins; recorded, not
  corrected. A 0-line crossover never fires in this port.
* `CCIoverSold`, `CCIoverBought` and `CCIzeroLine` are plain assignments in the
  source, not `input()`s, so they stay literals (`-100` / `100` / `0`). The md's
  argument table lists a single input (`v_input_1 = 20`), matching the source.
* `cci` is Pine's builtin and is transcribed from its documented definition --
  `(source - sma(source, n)) / (0.015 * sma(abs(source - sma(source, n)), n))`,
  i.e. a MEAN ABSOLUTE DEVIATION, not a standard deviation. `pine_ta` carries no
  `cci`, and a library CCI would differ in both the deviation and the smoothing
  factor, so the formula is written out rather than substituted.
* `sma` keeps Pine's window semantics (na until the window is full, na inside
  the window propagates), which is what `pine_ta.pine_sma` models. The inner
  `abs(source - sma)` therefore needs a second full window, so `CCI` is na for
  the first `2 * length - 1 = 39` bars, and `not na(vcci)` skips the whole block
  on those bars exactly as the source does.
* `crossover` / `crossunder` are Pine's event forms and are false whenever
  either operand is na.
* The entry stop levels are the CCI band values (-100 / +100) passed as PRICE
  levels, as the source writes them. On an instrument quoted far above zero the
  two arms are NOT symmetric, and the asymmetry is the source's own:
  a buy-stop at -100 is already through the market, so `high >= -100` holds on
  every bar and it fills at the next open -- it behaves as a market order; a
  sell-stop at +100 triggers when the price FALLS to the level, and `low <= 100`
  never holds on BTC, so the short arm never fills at all. The engine models
  exactly that, and the port passes both levels through verbatim, so a
  hypothetical instrument trading near zero would fill them as the source would.
* Consequence of the above, measured rather than assumed: on BTC/USDT:USDT 1d
  2024 the engine books 0 closed trades and holds one long (its `CCI_L` filled
  at 64928.5) while the framework closes one SHORT (opened 2024-02-20 at
  51784.4). The engine's short order is never reached; the framework's is
  projected. `run_pine` emits `enter_short` for a resting stop entry on the bar
  it was PLACED, whether or not the level is reachable -- the §二-11 boundary --
  and the framework acts on it. The engine ledger is the faithful side.
* `not na(vcci)` and the two `strategy.cancel` calls make the whole block run
  every bar, so each stop order normally rests for exactly one bar before the
  `else` branch cancels it (unreached orders never accumulate).
* `strategy.cancel(id=...)` runs on every bar its cross did not occur (inside
  the `not na(vcci)` guard), so each stop order normally rests for exactly one
  bar. `broker.cancel` reproduces it and never touches the position.
* `buyEntry` / `sellEntry` compare `close` against -100/+100 and are computed
  and never used; `plot(...)` and `p1`/`p2`/`p3` are display-only. All dropped.
* There is no exit call in the source: a position is closed only by the opposite
  entry reversing it, so `source_reproduce_stops` is False and a position open
  at the end of the window stays open.
* Contract-step rounding, leverage, margin, liquidation and funding are not
  modelled (PINE_SEMANTICS §1.6, §二-4).
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_cci(source, length):
    """Pine's `cci(source, length)`.

    Transcribed from TradingView's own definition rather than substituted:

        ma    = sma(source, length)
        dev   = sma(abs(source - ma), length)   # MEAN absolute deviation
        cci   = (source - ma) / (0.015 * dev)

    Pine's `dev()` is the mean absolute deviation, not a standard deviation, and
    the 0.015 divisor is what scales the result into the usual +/-100 band.
    """
    basis = ta.pine_sma(source, length)
    deviation = ta.pine_sma((source - basis).abs(), length)
    return (source - basis) / (0.015 * deviation)


class SMCCIZeroCross_8b2e5b(PinePortBase, IStrategy):
    source_id = "SM_8b2e5bfa9b6599c7"
    source_file = "CCI零点反转交易策略CCI-Zero-Cross-Trading-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {"CCIlength": 20}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The md's principle section says the entries fire on CCI crossing the "
        "ZERO line, with -100/100 as stops; the source's events are "
        "crossover(CCI, -100) and crossunder(CCI, 100), with the bands as the "
        "trigger levels. The source wins; recorded, not corrected.",
        "CCIoverSold / CCIoverBought / CCIzeroLine are plain assignments, not "
        "input()s, so they stay the literals -100 / 100 / 0. The only input is "
        "CCIlength = 20, which the md's argument table confirms.",
        "cci is transcribed from its definition, (source - sma) / (0.015 * "
        "sma(abs(source - sma), n)) -- a MEAN ABSOLUTE DEVIATION, not a "
        "standard deviation. It is not swapped for a library CCI.",
        "pine_sma propagates na and returns na until its window is full, so the "
        "inner abs(source - sma) needs a second window and CCI is na for the "
        "first 2*length-1 = 39 bars; not na(vcci) skips the block on those bars "
        "as written.",
        "crossover / crossunder are Pine's event forms, false while either "
        "operand is na.",
        "The entries are resting STOP orders at the CCI band VALUES (-100, "
        "+100) used as PRICE levels, exactly as the source writes them, and on "
        "an instrument quoted far above zero the two arms are NOT symmetric: "
        "the buy-stop at -100 is already through the market (high >= -100 on "
        "every bar) so it fills at the next open like a market order, while the "
        "sell-stop at +100 triggers only when the price FALLS to 100 (low <= "
        "100), which never happens on BTC -- so the short arm never fills. The "
        "engine models both correctly and both levels are passed through "
        "verbatim.",
        "Consequence, measured on BTC/USDT:USDT 1d 2024: the engine books 0 "
        "closed trades and holds one long (CCI_L filled 64928.5) while the "
        "framework closes one SHORT opened 2024-02-20 at 51784.4. run_pine "
        "projects a resting stop entry as enter_short on the bar it was PLACED "
        "whether or not the level is reachable (PINE_SEMANTICS §二-11), and the "
        "framework acts on it; the engine ledger is the faithful side. This is "
        "the framework boundary, not a port defect.",
        "strategy.cancel(id=...) runs on every bar the matching cross did not "
        "occur (inside the not na(vcci) guard), so each stop order normally "
        "rests one bar; broker.cancel reproduces it and never touches the "
        "position.",
        "buyEntry / sellEntry (close against -100/+100) are computed and never "
        "used; plot/p1/p2/p3 are display-only. Dropped.",
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False and a position open "
        "at the window end stays open.",
        "strategy() declares only title/shorttitle/overlay, so Pine's defaults "
        "apply: qty_type fixed, qty_value 1, commission 0, pyramiding 0, "
        "initial capital 1000000, process_orders_on_close false.",
        "Contract-step rounding, leverage, margin, liquidation and funding are "
        "not modelled (PINE_SEMANTICS §1.6, §二-4).",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["CCIlength"])
        hlc3 = (dataframe["high"] + dataframe["low"] + dataframe["close"]) / 3.0
        cci = _pine_cci(hlc3, length)
        over_sold = -100.0   # literal in the source
        over_bought = 100.0  # literal in the source

        dataframe["pine_hlc3"] = hlc3
        dataframe["pine_cci"] = cci
        dataframe["pine_cross_up_oversold"] = ta.pine_crossover(cci, over_sold)
        dataframe["pine_cross_dn_overbought"] = ta.pine_crossunder(cci, over_bought)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "cci": dataframe["pine_cci"].to_numpy(dtype=float),
            "cross_up_oversold": dataframe["pine_cross_up_oversold"].to_numpy(dtype=bool),
            "cross_dn_overbought": dataframe["pine_cross_dn_overbought"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (not na(vcci))  -- vcci is cci(hlc3, CCIlength), identical to CCI
        if not np.isnan(ctx["cci"][i]):
            # if (crossover(CCI, CCIoverSold))
            #     strategy.entry("CCI_L", strategy.long, stop=CCIoverSold)
            if ctx["cross_up_oversold"][i]:
                broker.entry("CCI_L", "long", stop=-100.0)
            else:
                # strategy.cancel(id="CCI_L")
                broker.cancel("CCI_L")
            # if (crossunder(CCI, CCIoverBought))
            #     strategy.entry("CCI_S", strategy.short, stop=CCIoverBought)
            if ctx["cross_dn_overbought"][i]:
                broker.entry("CCI_S", "short", stop=100.0)
            else:
                # strategy.cancel(id="CCI_S")
                broker.cancel("CCI_S")
