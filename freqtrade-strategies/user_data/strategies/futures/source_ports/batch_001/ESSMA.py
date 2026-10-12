"""Port of sources/SM_c5d1d53e8c82d004.pine (batch_001/ESSMA.md).

Pine v5. The file declares an INDICATOR -- `indicator("ESSMA", overlay=true)` --
and a converter tool appended an order block to it (PINE_SEMANTICS.md 1.17).
Pine v5 does not compile `strategy.entry` inside an `indicator()`, so the
"original strategy" is the indicator PLUS the appended block, and the trading
behaviour it defines is entry-only:

    if up
        strategy.entry("Enter Long", strategy.long)
    else if down
        strategy.entry("Enter Short", strategy.short)

The indicator is bhavishya's weighted "ESSMA": an average of five differently
weighted moving averages of the same source, each divided by its own weight,
with the bar's open and close folded in, smoothed once more by a WMA, and
crossed against that smoothed line:

    smma(src, length) =>
        smma = 0.0
        smma := na(smma[2]) ? ta.sma(src, length) : (smma[2]*(length-1)+src)/length
        smma

    essma(src, length) =>
        essma = 0.0
        smma = smma(src * w4, length)
        ema  = ta.ema(src * w2, length)
        sma  = ta.sma(src * w1, length)
        wma  = ta.wma(src * w3, length)
        rma  = ta.rma(src * w5, length)
        essma := (smma/w4 + ema/w2 + sma/w1 - wma/w3 - rma/w5 + open + close) / 3
        essma

    atr       = ta.atr(atrLen)
    usesource = useatr ? atr : source
    essma1    = essma(usesource, length1)
    sessma1   = ta.wma(essma1, length1)
    up   = crossover(essma1, sessma1)
    down = crossunder(essma1, sessma1)

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, and not even a commented-out one. A position is therefore only
ever left by the opposite entry, which the engine models as a reversal.
`pyramiding` keeps Pine's default of 0, so a repeated signal while already
positioned that way is ignored.

FIDELITY:

* The `smma` helper is reproduced LITERALLY, including its unusual `smma[2]`
  (TWO bars back, not the usual `smma[1]`) seed test. That offset splits the
  series into two interleaved recursions that each read their own value two
  bars earlier, so it is NOT the same as `ta.rma` and must not be replaced by
  one (`pine_rma` exists in pine_ta and is deliberately NOT used here). The
  helper is written out as a local loop so the recurrence is on the record.
  `na(smma[2])` is true on bars 0 and 1 (no history) and then again until
  `ta.sma` has a value, so the series is seeded from the SMA and only starts
  recursing once a two-bar-old value exists.
* The five component series use `src * w_i` as their input and are then divided
  by `w_i` again, so with the default weights of 2.0 each they are the plain
  moving averages; the weights are kept as parameters because the source
  exposes them, not folded away.
* The final `+ open + close` terms read the bar's RAW open/close, not the
  selected `source` -- so with Use ATR on, the MAs follow the ATR while these
  two terms still follow price. Transcribed as written.
* `atr = ta.atr(atrLen)` is computed unconditionally but only consumed when
  `useatr` is true (default false, so it is dead by default); it is kept as a
  ledger column so the formula is on the record.
* `bool up = na` / `bool down = na` are NOT `var`, so they are re-initialised
  every bar and `up` is true only on a bar where the crossover fires; the port
  reads the crossover/crossunder series directly. If both could fire on one bar
  `up` would win the `if/else if`, which the port's `elif` also does.
* `plot(...)` / `plotshape(...)` / `alertcondition(...)` are display- or
  alert-only and place no order; dropped.
* The source declares `indicator(...)`, so no strategy() properties exist and
  Pine's documented defaults apply: fixed size 1, 0% commission, pyramiding 0,
  initial capital 1000000 USD.
* `ta.atr` is `ta.rma(ta.tr(true), atrLen)` with pine_ta's documented Wilder
  seeding (SMA of the first `atrLen` true ranges), an unpublished TradingView
  rule; PINE_SEMANTICS.md 3.7 records that pine_ta's `pine_tr` gives the first
  bar `high-low` where Pine's default `ta.tr` is na, shifting the ATR seed by
  one bar. The default path (`useatr=false`) never reads ATR, so the shipped
  behaviour is unaffected; the flag is exposed and this is recorded.
* The `ta.ema` seed is the modelled first-observation seed (PINE_SEMANTICS.md
  3.1); TradingView does not publish its own.
* MD-vs-SOURCE: the md front matter names the author as "ChaoZhang" and gives
  the full argument table; the source file's header reads "(c) bhavishya". The
  md records the fmz uploader, the source the original author. No effect on
  behaviour; recorded, not reconciled. `v_input_float_3|2|WMA Weight` in the md
  table is the same 2.0 the source declares. The md's embedded source block is
  verbatim identical to the .pine source.
* The header's backtest window (2022-04-11 to 2022-05-10) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. The header's
  `basePeriod: 15m` is the host's intrabar granularity for filling 1h bars, not
  the strategy's period; the header's `period: 1h` is what `timeframe` uses.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_smma(source: pd.Series, length: int) -> pd.Series:
    """The source's local `smma`, reproduced literally.

        smma =  0.0
        smma := na(smma[2]) ? ta.sma(src, length) : (smma[2]*(length-1)+src)/length

    The recursion reads smma[2] -- TWO bars back -- which is why this is not
    ta.rma (Wilder, which reads one bar back). Bars 0 and 1 have no [2] value,
    so they take the SMA branch; the SMA is itself na until `length` bars have
    elapsed, so the whole series is na until then.
    """
    values = source.to_numpy(dtype=float)
    sma = ta.pine_sma(source, length).to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    for i in range(len(values)):
        previous = out[i - 2] if i >= 2 else np.nan
        if np.isnan(previous):
            out[i] = sma[i]
        else:
            out[i] = (previous * (length - 1) + values[i]) / length
    return pd.Series(out, index=source.index, dtype=float)


class SMEssma_c5d1d5(PinePortBase, IStrategy):
    source_id = "SM_c5d1d53e8c82d004"
    source_file = "ESSMA.md"
    timeframe = "1h"
    can_short = True
    # Input defaults exactly as written. `source` is Pine's `input.source`; the
    # string name is the default the source declares and is resolved through
    # pine_ta.pine_source.
    source_defaults: dict = {
        "source": "close",
        "length1": 50,
        "w1": 2.0,
        "w2": 2.0,
        "w3": 2.0,
        "w4": 2.0,
        "w5": 2.0,
        "useatr": False,
        "atrLen": 14,
    }
    # indicator(...), not strategy(...): Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "Converter-appended source: the file declares an indicator "
        "(`indicator(\"ESSMA\", overlay=true)`) and the tool appended `if up / "
        "strategy.entry(\"Enter Long\", strategy.long) else if down / "
        "strategy.entry(\"Enter Short\", strategy.short)`. The port reproduces "
        "the indicator PLUS that appended block, i.e. entry-only behaviour "
        "(PINE_SEMANTICS.md 1.17).",
        "The appended block's conditions are BOOLEANS (`up` / `down`), not the "
        "`? -1 : 0` integer this family usually carries, so the 1.17 "
        "truthiness trap does not apply; the port keeps them as booleans.",
        "smma is reproduced LITERALLY, including the unusual `smma[2]` seed "
        "test (two bars back, not one). It is NOT ta.rma and is NOT replaced "
        "by pine_rma; the recurrence is written out as a local loop. The "
        "two-bar offset interleaves two recursions that each read their own "
        "value two bars earlier.",
        "The five weighted MAs use src*w_i as input and are divided by w_i "
        "again, so at the default weights of 2.0 they are the plain MAs. The "
        "weights stay as parameters because the source exposes them.",
        "`+ open + close` in the essma formula reads the bar's RAW open and "
        "close, not the selected source, so with Use ATR on the MAs follow the "
        "ATR while these two terms still follow price. Transcribed as written.",
        "atr = ta.atr(atrLen) is computed even when useatr is false (the "
        "default), where it is dead; kept as a ledger column for the record.",
        "`bool up = na` / `bool down = na` are not `var` declarations, so they "
        "reset every bar and `up` is true only on the crossover bar. The port "
        "reads the crossover/crossunder series, which is the same thing; if "
        "both fired on one bar `up` would win the if/else-if, and the port's "
        "elif does too.",
        "No exit of any kind exists: no strategy.close, no strategy.exit, no "
        "stop or limit, no commented-out exit line. A position is only left by "
        "the opposite entry (a reverse fill); source_reproduce_stops is False.",
        "The source declares indicator(...), so no strategy() properties exist "
        "and Pine's documented defaults are used: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD.",
        "ta.atr is ta.rma(ta.tr(true), atrLen) with pine_ta's Wilder seeding; "
        "PINE_SEMANTICS.md 3.7 records that pine_tr differs from Pine's default "
        "ta.tr on the first bar (high-low instead of na), shifting the ATR "
        "seed by one bar. The default path never reads ATR, so the shipped "
        "behaviour is unaffected.",
        "The ta.ema seed is the modelled first-observation seed "
        "(PINE_SEMANTICS.md 3.1); TradingView does not publish its own.",
        "MD-vs-SOURCE: the md names the author 'ChaoZhang'; the source header "
        "reads '(c) bhavishya' -- the md records the fmz uploader, the source "
        "the original author. Recorded, not reconciled.",
        "`plot` / `plotshape` / `alertcondition` are display- or alert-only and "
        "place no order; dropped.",
        "The header's backtest window is extraction metadata, not an "
        "input.time filter, so the port runs on whatever range the caller "
        "supplies; basePeriod: 15m is the host's intrabar fill granularity, "
        "not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        length1 = int(params["length1"])
        w1 = float(params["w1"])
        w2 = float(params["w2"])
        w3 = float(params["w3"])
        w4 = float(params["w4"])
        w5 = float(params["w5"])
        useatr = bool(params["useatr"])
        open_ = dataframe["open"]
        close = dataframe["close"]

        # atr = ta.atr(atrLen) -- dead unless useatr, computed either way.
        atr = ta.pine_atr(dataframe, int(params["atrLen"]))
        # usesource = useatr ? atr : source
        selected = ta.pine_source(dataframe, str(params["source"]))
        usesource = atr if useatr else selected

        # essma(usesource, length1)
        smma_term = _pine_smma(usesource * w4, length1)
        ema_term = ta.pine_ema(usesource * w2, length1)
        sma_term = ta.pine_sma(usesource * w1, length1)
        wma_term = ta.pine_wma(usesource * w3, length1)
        rma_term = ta.pine_rma(usesource * w5, length1)
        essma1 = (
            smma_term / w4 + ema_term / w2 + sma_term / w1
            - wma_term / w3 - rma_term / w5 + open_ + close
        ) / 3.0

        # sessma1 = ta.wma(essma1, length1)
        sessma1 = ta.pine_wma(essma1, length1)

        dataframe["pine_atr"] = atr
        dataframe["pine_essma"] = essma1
        dataframe["pine_essma_smooth"] = sessma1
        # bool up = na ... up := true on crossover; likewise down.
        dataframe["pine_up"] = ta.pine_crossover(essma1, sessma1)
        dataframe["pine_down"] = ta.pine_crossunder(essma1, sessma1)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "up": dataframe["pine_up"].to_numpy(),
            "down": dataframe["pine_down"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if up
        #     strategy.entry("Enter Long", strategy.long)
        # else if down
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["up"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["down"][i]:
            broker.entry("Enter Short", "short")
