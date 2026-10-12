"""Port of sources/SM_d2b8785249f68c77.pine (batch_001/Hull-4ema.md).

Pine v4. The file declares `study("Hull-4ema", overlay=true)`, NOT
`strategy(...)`: the two `strategy.entry` calls in the middle of the file are
an order block APPENDED to the indicator by the converter site that published
it (fmz.com/strategy/362327, named in the md's Detail link). Pine does not
compile `strategy.entry` inside `study()`, so the "original strategy" is the
indicator PLUS that appended block, and the trading behaviour it defines is
entry-only:

    if crossover(HMA, saveMA_Min)
        strategy.entry("Enter Long", strategy.long)
    else if crossunder(HMA, saveMA_Max)
        strategy.entry("Enter Short", strategy.short)

The indicator is a Hull moving average whose support/resistance pivot prices
are carried forward:

    HMA         = hma(price, HMA_Length)                 # price defaults to hl2
    MA_Min      = HMA > HMA[1] and HMA[1] < HMA[2] ? HMA[1] : na
    MA_Max      = HMA < HMA[1] and HMA[1] > HMA[2] ? HMA[1] : na
    saveMA_Min  = valuewhen(HMA > HMA[1] and HMA[1] < HMA[2], HMA[1], 0)
    saveMA_Max  = valuewhen(HMA < HMA[1] and HMA[1] > HMA[2], HMA[1], 0)

`MA_Min` marks a bar where the Hull line turned UP (`HMA[1]` was the local
minimum of the three), `MA_Max` a bar where it turned DOWN; the `saveMA_*`
series carry the most recent such turning price forward with `valuewhen(...,
0)`. The appended block buys when the Hull line crosses above the last saved
minimum and sells when it crosses below the last saved maximum.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, and no commented-out exit line either. A position is
therefore only ever left by the opposite entry, which the engine models as a
reversal. `pyramiding` keeps Pine's default of 0, so a repeated signal while
already positioned that way is ignored.

FIDELITY:

* `hma()` is not in pine_ta, so the port writes the Pine v4 built-in out:
  `WMA(2*WMA(src, length/2) - WMA(src, length), round(sqrt(length)))`. The
  half-length is FLOORED (`length/2` is a float in Pine and the WMA length is
  an int, so it truncates) and the outer length is `math.round`ed -- both are
  MODELLING CHOICES about TradingView internals that the platform does not
  document; for HMA_Length 21 they give 10 and 5 respectively. `pine_ta.pine_wma`
  has no na-skipping rule, so an na anywhere in the window makes the WMA na;
  TradingView's reference remarks say na values are "ignored", which would
  differ near the warmup. Recorded, not worked around.
* `price` is an `input` defaulting to `hl2` and is resolved through
  `pine_ta.pine_source`, so hl2/high/low/open/close/hlc3/hlcc4/ohlc4 are all
  selectable without touching the port's logic.
* The file is a CONCATENATION of three indicator sources: the Hull block, a
  "4 EMA" block (len1..len4) and a "Bollinger Bands color" block (length,
  src1, len, mult). Only the FIRST block has an appended order block; the other
  two are display-only code whose variables are read by `plot`/`fill` and by
  nothing else. Their formulas are still reproduced (the port emits the four
  EMAs and the band columns) so that nothing the source computes is dropped,
  but they place no order and cannot affect the result. The md's 16-row
  argument table is these three blocks' inputs concatenated, which is
  independent evidence for the concatenation.
* The Hull block's `concavity`, `delta`, `delta_per_bar`, `next_bar`,
  `divergence`, `divergenceColor`, `labelText`, `divergenceLabel`, `O_R`,
  `DG_G` feed only `plot` / `plotshape` / `label.new` -- display-only, no
  order. `concavity` is `? 1 : -1`; it is compared (`concavity != -1`) and
  never used as a bare condition, and it places no order, so the
  PINE_SEMANTICS.md 1.17 trap does not arise.
* `label.new(...)` under `ShowDivergenceLabel`, `plotshape(ShowBuySellArrows
  ? ...)`, `trackprice=ExtendSupResLines` and `ShowHullSupResLines` only switch
  drawing on and off (all four default to false); they place no order and are
  not reproduced as behaviour.
* `alertcondition` is alert-only and places no order.
* The source declares `study(...)`, so no strategy() properties exist and
  Pine's documented defaults apply: market orders of `fixed` size 1 contract,
  initial capital 1000000, commission 0%, pyramiding 0,
  process_orders_on_close=false.
* The header's backtest window (2022-05-02 to 2022-05-08) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. Its
  `basePeriod: 1m` is the host's intrabar granularity for filling 5m bars, not
  the strategy's period.
* The md's prose ("this is a test just trying out pine script / 4EMA indicator
  has been created for everyone") describes the concatenated 4EMA block, not
  the Hull block that carries the orders. Prose is not followed; the code is.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding
  separately).
"""
import math

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _hma(source: pd.Series, length: int) -> pd.Series:
    """Pine v4 built-in `hma(src, length)`.

    `hma` is not part of pine_ta, so it is written out here exactly as the
    platform's documented formula reads:

        WMA(2 * WMA(src, length/2) - WMA(src, length), round(sqrt(length)))

    The half-length truncates (`length/2` is a float in Pine while the WMA
    length is an int) and the outer length rounds half away from zero, which is
    what `pine_ta.pine_round` does. Both are modelling choices about
    undocumented TradingView internals -- see the module FIDELITY notes.
    """
    half = int(length / 2)
    outer = int(ta.pine_round(math.sqrt(length), 0))
    difference = 2.0 * ta.pine_wma(source, half) - ta.pine_wma(source, length)
    return ta.pine_wma(difference, outer)


class SMHull4ema_d2b878(PinePortBase, IStrategy):
    source_id = "SM_d2b8785249f68c77"
    source_file = "Hull-4ema.md"
    timeframe = "5m"
    can_short = True
    # Input defaults exactly as written. The last nine belong to the two
    # display-only indicator blocks concatenated after the Hull block; they are
    # declared because the source declares them, and they place no order.
    source_defaults: dict = {
        "price": "hl2",
        "HMA_Length": 21,
        "lookback": 2,
        "ShowHullSupResLines": False,
        "ShowBuySellArrows": False,
        "ShowDivergenceLabel": False,
        "ExtendSupResLines": False,
        "len1": 8,
        "len2": 13,
        "len3": 21,
        "len4": 55,
        "src": "close",
        "length": 50,
        "src1": "close",
        "len": 2,
        "mult": 2.0,
    }
    # The source declares study(...), not strategy(...), so no strategy()
    # properties exist and Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The file declares study(...), not strategy(...): the strategy.entry "
        "pair in the middle is an order block appended by the converter site "
        "(fmz.com/strategy/362327 per the md's Detail link). The port "
        "reproduces the Hull indicator PLUS that appended block, i.e. "
        "entry-only behaviour.",
        "hma() is not in pine_ta and is written out here as the documented "
        "built-in: WMA(2*WMA(src, length/2) - WMA(src, length), "
        "round(sqrt(length))). The half-length is FLOORED and the outer length "
        "is ROUNDED -- both are modelling choices about undocumented "
        "TradingView internals (for HMA_Length 21 they give 10 and 5). A "
        "TradingView rule that instead rounds length/2 to 11 would give a "
        "different Hull line.",
        "pine_ta.pine_wma returns na if ANY value in its window is na. "
        "TradingView's ta.hma reference remarks say na values in the source "
        "are 'ignored', which would change the first bars of the Hull line; "
        "the shared layer is not modified from a port (PINE_SEMANTICS.md "
        "3.2 records the general na-window question).",
        "The file is a CONCATENATION of three indicator sources -- Hull, a "
        "'4 EMA' block and a 'Bollinger Bands color' block -- and only the "
        "Hull block carries an appended order block. The other two blocks' "
        "outputs feed plot()/fill()/transp only, so they place no order. Their "
        "formulas are still computed (four EMAs plus the basis/upper/lower "
        "bands) rather than dropped, but they cannot affect the trading "
        "result. The md's 16-row argument table is those three blocks' inputs "
        "concatenated.",
        "The Hull block computes concavity / delta / delta_per_bar / next_bar "
        "/ divergence / divergenceColor / labelText / divergenceLabel / O_R / "
        "DG_G, all of which feed only plot, plotshape or label.new. "
        "concavity is `? 1 : -1` but is only COMPARED (concavity != -1) and "
        "places no order, so the PINE_SEMANTICS.md 1.17 trap does not arise.",
        "`saveMA_Min`/`saveMA_Max` use valuewhen(condition, HMA[1], 0), i.e. "
        "the most recent turning price carried forward from that bar onward, "
        "and the entries cross against the CARRIED series (not the raw "
        "MA_Min/MA_Max, which are na except on the turning bar itself). "
        "pine_ta.pine_valuewhen reproduces occurrence=0 with carry-forward.",
        "ShowHullSupResLines / ShowBuySellArrows / ShowDivergenceLabel / "
        "ExtendSupResLines all default to false and only gate drawing calls; "
        "alertcondition is alert-only. None places an order.",
        "`price` is an input.source defaulting to hl2, resolved through "
        "pine_ta.pine_source, so hl2/high/low/open/close/hlc3/hlcc4/ohlc4 are "
        "all selectable without changing the port's logic.",
        "The source has no exit of any kind: no strategy.close, no "
        "strategy.exit, no stop or limit order, and no commented-out exit "
        "line. A position is only left by the opposite entry, which the engine "
        "models as a reverse fill. source_reproduce_stops is False "
        "accordingly.",
        "The source declares study(...), so no strategy() properties exist and "
        "Pine's documented defaults are used: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD.",
        "The md's prose ('this is a test just trying out pine script / 4EMA "
        "indicator has been created for everyone') describes the concatenated "
        "4EMA block, not the Hull block that carries the orders. The CODE is "
        "followed. The md's argument table and its embedded source block are "
        "verbatim identical to the .pine source.",
        "The header's backtest window is extraction metadata, not an "
        "input.time filter, so the port runs on whatever range the caller "
        "supplies; basePeriod: 1m is the host's intrabar fill granularity, "
        "not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        price = ta.pine_source(dataframe, str(params["price"]))
        hma_length = int(params["HMA_Length"])
        lookback = int(params["lookback"])

        hma = _hma(price, hma_length)

        # delta = HMA[1] - HMA[lookback + 1]; next_bar = HMA[1] + delta/lookback
        # (concavity is derived from next_bar but is display-only.)
        previous = hma.shift(1)

        # MA_Min / MA_Max and the valuewhen series the orders cross against.
        min_turn = (hma > hma.shift(1)) & (hma.shift(1) < hma.shift(2))
        max_turn = (hma < hma.shift(1)) & (hma.shift(1) > hma.shift(2))
        save_ma_min = ta.pine_valuewhen(min_turn, hma.shift(1), 0)
        save_ma_max = ta.pine_valuewhen(max_turn, hma.shift(1), 0)

        dataframe["pine_hma"] = hma
        dataframe["pine_ma_min"] = hma.shift(1).where(min_turn)
        dataframe["pine_ma_max"] = hma.shift(1).where(max_turn)
        dataframe["pine_save_ma_min"] = save_ma_min
        dataframe["pine_save_ma_max"] = save_ma_max
        # if crossover(HMA, saveMA_Min) / else if crossunder(HMA, saveMA_Max)
        dataframe["pine_long_condition"] = ta.pine_crossover(hma, save_ma_min)
        dataframe["pine_short_condition"] = ta.pine_crossunder(hma, save_ma_max)

        # The two concatenated display-only blocks. Neither places an order and
        # neither is read by the Hull block; they are computed so that nothing
        # the source evaluates is dropped.
        ema_src = ta.pine_source(dataframe, str(params["src"]))
        dataframe["pine_ema_entry"] = ta.pine_ema(ema_src, int(params["len1"]))
        dataframe["pine_ema_fast"] = ta.pine_ema(ema_src, int(params["len2"]))
        dataframe["pine_ema_medium"] = ta.pine_ema(ema_src, int(params["len3"]))
        dataframe["pine_ema_slow"] = ta.pine_ema(ema_src, int(params["len4"]))
        band_length = int(params["length"])
        band_basis = ta.pine_sma(ema_src, band_length)
        band_dev = float(params["mult"]) * ta.pine_stdev(ema_src, band_length)
        dataframe["pine_band_basis"] = band_basis
        dataframe["pine_band_upper"] = band_basis + band_dev
        dataframe["pine_band_lower"] = band_basis - band_dev
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "hma": dataframe["pine_hma"].to_numpy(),
            "save_ma_min": dataframe["pine_save_ma_min"].to_numpy(),
            "save_ma_max": dataframe["pine_save_ma_max"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if crossover(HMA, saveMA_Min)
        #     strategy.entry("Enter Long", strategy.long)
        # else if crossunder(HMA, saveMA_Max)
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
