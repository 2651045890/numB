"""Port of sources/SM_f2da7bf42e755eee.pine (batch_001/Bollinger-Awesome-Alert-R1.md).

Pine v4. The file declares `study(shorttitle="BBAWE", title="Bollinger Awesome
Alert R1.1 by JustUncleL", overlay=true)`, NOT `strategy(...)`: the two
`strategy.entry` calls at the bottom are an order block APPENDED to the
indicator by the converter site that published it (fmz.com/strategy/365419,
named in the md's Detail link). Pine does not compile `strategy.entry` inside
`study()`, so the "original strategy" is the indicator PLUS that appended block,
and the trading behaviour it defines is entry-only:

    if break_up
        strategy.entry("Enter Long", strategy.long)
    else if break_down
        strategy.entry("Enter Short", strategy.short)

The indicator is JustUncleL's Bollinger-Band / Awesome-Oscillator scalping
system:

    bb_basis   = bb_use_ema ? ema(bb_source, bb_length) : sma(bb_source, bb_length)
    fast_ma    = ema(bb_source, fast_ma_len)
    dev        = stdev(bb_source, bb_length)            # population, ddof=0
    bb_upper   = bb_basis + bb_mult * dev
    bb_lower   = bb_basis - bb_mult * dev
    xSMA1_SMA2 = sma(hl2, nLengthFast) - sma(hl2, nLengthSlow)
    AO         = xSMA1_SMA2 >= 0 ? (xSMA1_SMA2 > xSMA1_SMA2[1] ? 1 : 2)
                                 : (xSMA1_SMA2 > xSMA1_SMA2[1] ? -1 : -2)
    spread     = bb_upper - bb_lower
    bb_squeeze = spread / sma(spread, sqz_length) * 100

    break_down = crossunder(fast_ma, bb_basis) and close < bb_basis and abs(AO) == 2
                 and (not bb_filter or close > bb_lower)
                 and (not sqz_filter or bb_squeeze > sqz_threshold)
    break_up   = crossover(fast_ma, bb_basis) and close > bb_basis and abs(AO) == 1
                 and (not bb_filter or close < bb_upper)
                 and (not sqz_filter or bb_squeeze > sqz_threshold)

`abs(AO) == 1` means AO is exactly +1 -- the fast hl2 average above the slow one
AND rising -- and `abs(AO) == 2` means AO is +2 or -2, i.e. NOT rising. The
non-zero magnitude is what selects "the AO has turned up" vs "the AO is not
turning up"; it is not a magnitude threshold.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, no stop / limit / trail, and not even a commented-out exit
line. A position is only ever left by the opposite entry, which the engine
models as a reversal. `pyramiding` keeps Pine's default of 0, so a repeated
signal while already positioned that way is ignored.

FIDELITY:

* The appended block is the trading behaviour to reproduce (rule 2: the source
  is authoritative, not the author's prose). The md's Strategy Description
  prescribes a take-profit ("10-20 pips depending on pair or When Awesome
  Oscillator turns a different colour") that the source simply does not
  contain -- see the note on the md/source conflict below.
* AO's na handling is reproduced literally. A nested Pine ternary whose
  condition is na takes the FALSE branch, and `na > na` is false too, so on
  every warm-up bar (where xSMA1_SMA2 is na) AO evaluates to -2 and
  `abs(AO) == 2` holds. The port keeps that exact value rather than NaN. It
  cannot produce a signal there -- the cross of `fast_ma` against `bb_basis`
  needs both series to exist -- but the value is part of the source's
  expression and is not "cleaned up".
* `stdev` is Pine's population standard deviation (ddof=0), which is what
  `pine_ta.pine_stdev` computes; `ema` / `sma` / `crossover` / `crossunder` map
  onto the library's Pine models.
* `abs(AO) == 1` / `abs(AO) == 2` are integer comparisons on the AO series, not
  boolean flags. There is no `? -1 : 0` anywhere in this source, so the
  PINE_SEMANTICS.md 1.17 trap does not arise; `break_up` / `break_down` are
  ordinary Pine booleans.
* `bb_offset = atr(14) * 0.5`, `bb_sqz_upper`, `bb_sqz_lower`, the four
  `fill()` calls, the four `plot()` calls, the two `plotshape()` calls and the
  three `alertcondition()` calls are display- or alert-only: they place no
  order and feed no condition. They are not reproduced.
* `bb_filter` and `sqz_filter` are two more optional terms inside the two
  entry conditions; the port keeps them live (they are inputs), so overriding
  either one restores exactly the source's expression.
* The source declares `study(...)`, so no `strategy()` properties exist and
  Pine's documented defaults apply: market orders of `fixed` size 1 contract,
  initial capital 1000000, commission 0%, pyramiding 0,
  process_orders_on_close=false.
* There is no exit call of any kind, so `source_reproduce_stops` is False and a
  position still open at the end of the window stays open.
* md-vs-source: the md's argument table matches the source's input defaults
  exactly (bb_use_ema false, bb_filter false, sqz_filter false, bb_length 20,
  bb_source close, bb_mult 2.0, fast_ma_len 3, nLengthSlow 34, nLengthFast 5,
  sqz_length 100, sqz_threshold 50). Its PROSE, however, describes only the
  indicator and adds a take-profit rule the source does not implement. Per
  rule 2 the source wins: the port has no take-profit. The conflict is
  recorded, not resolved in favour of the prose.
* The header's backtest window (2022-04-23 to 2022-05-22) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. Its
  `basePeriod: 15m` is the host's intrabar granularity for filling 1h bars.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerAwesomeAlertR1_f2da7b(PinePortBase, IStrategy):
    source_id = "SM_f2da7bf42e755eee"
    source_file = "Bollinger-Awesome-Alert-R1.md"
    timeframe = "1h"
    can_short = True
    # Input defaults exactly as written in the source.
    source_defaults: dict = {
        "bb_use_ema": False,
        "bb_filter": False,
        "sqz_filter": False,
        "bb_length": 20,
        "bb_source": "close",
        "bb_mult": 2.0,
        "fast_ma_len": 3,
        "nLengthSlow": 34,
        "nLengthFast": 5,
        "sqz_length": 100,
        "sqz_threshold": 50,
    }
    # The source declares study(...), not strategy(...), so Pine's documented
    # defaults apply: fixed size 1, initial capital 1000000, commission 0%,
    # pyramiding 0, process_orders_on_close=false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere, and no
    # commented-out exit line either.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The file's study(shorttitle='BBAWE', ...) declaration means the "
        "strategy.entry pair at the bottom is an order block APPENDED by the "
        "converter site (fmz.com/strategy/365419 per the md's Detail link). The "
        "port reproduces the indicator PLUS that appended block, i.e. "
        "entry-only behaviour: if break_up -> long, else if break_down -> short.",
        "There is NO exit of any kind in the source: no strategy.close, no "
        "strategy.exit, no stop/limit/trail, and no commented-out exit line. A "
        "position is only left by the opposite entry, which the engine models "
        "as a reversal. source_reproduce_stops is False accordingly.",
        "md-vs-source CONFLICT (recorded, not silently resolved): the md's "
        "Strategy Description prescribes a take-profit ('10-20 pips depending "
        "on pair or When Awesome Oscillator turns a different colour') and "
        "describes only the indicator. The source contains no take-profit and "
        "no exit at all. Per rule 2 the source is authoritative, so the port "
        "has no take-profit; the prose rule is deliberately NOT restored.",
        "AO's na handling is reproduced literally: a nested ternary with an na "
        "condition takes the false branch and `na > na` is false, so AO = -2 on "
        "every warm-up bar (where xSMA1_SMA2 is na) and abs(AO) == 2 holds "
        "there. The port keeps that value instead of NaN. It cannot fire a "
        "signal on those bars because the fast/basis cross needs both series, "
        "but the value is part of the source's expression.",
        "abs(AO) == 1 selects AO == +1 (fast hl2 average above the slow one AND "
        "rising); abs(AO) == 2 selects AO == +2 or -2, i.e. NOT rising. The "
        "comparison is on the integer AO series, not on a boolean flag.",
        "There is no `? -1 : 0` and no bare-integer condition in this source "
        "(break_up / break_down are ordinary Pine booleans), so the "
        "PINE_SEMANTICS.md 1.17 trap does not arise here.",
        "stdev is Pine's POPULATION standard deviation (ddof=0); the port uses "
        "pine_ta.pine_stdev, which computes exactly that. The sma/crossover/"
        "crossunder models in pine_ta match Pine's definitions.",
        "pine_ta.pine_ema seeds the recursion with the first non-na observation "
        "(PINE_SEMANTICS.md 3.1): TradingView does not publish ta.ema's seeding "
        "rule, so the port inherits a public-layer MODELLING CHOICE it does not "
        "override. It applies to fast_ma (length 3) and to bb_basis only when "
        "`bb_use_ema` is overridden to true (the default is sma). The two "
        "smoothers converge after a few bars, so the exposure is the warm-up; "
        "it is not certified equivalent to the source platform.",
        "bb_offset = atr(14) * 0.5, bb_sqz_upper, bb_sqz_lower, the four "
        "fill() calls, the four plot() calls, the two plotshape() calls and the "
        "three alertcondition() calls are display- or alert-only and place no "
        "order: not reproduced.",
        "bb_filter and sqz_filter are optional terms INSIDE the two entry "
        "conditions; both are kept live so an override restores exactly the "
        "source's expression. With their defaults (false) the terms vanish, "
        "which is the source's own short-circuit.",
        "The source declares study(...), so no strategy() properties exist and "
        "Pine's documented defaults apply: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD, process_orders_on_close false.",
        "The md's argument table matches the source's input defaults exactly "
        "(false/false/false/20/close/2.0/3/34/5/100/50); only the md's prose "
        "adds behaviour the source lacks (see the CONFLICT note above).",
        "The header's backtest window (2022-04-23 to 2022-05-22) is extraction "
        "metadata, not an input.time filter, so the port runs on whatever range "
        "the caller supplies; basePeriod: 15m is the host's intrabar fill "
        "granularity, not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        hl2 = (dataframe["high"] + dataframe["low"]) / 2.0
        bb_source = ta.pine_source(dataframe, str(params["bb_source"]))
        bb_length = int(params["bb_length"])
        fast_ma_len = int(params["fast_ma_len"])
        bb_mult = float(params["bb_mult"])
        sqz_length = int(params["sqz_length"])
        sqz_threshold = float(params["sqz_threshold"])
        bb_filter = bool(params["bb_filter"])
        sqz_filter = bool(params["sqz_filter"])

        # ema_1 / sma_1 / bb_basis = bb_use_ema ? ema_1 : sma_1
        ema_1 = ta.pine_ema(bb_source, bb_length)
        sma_1 = ta.pine_sma(bb_source, bb_length)
        bb_basis = ema_1 if bool(params["bb_use_ema"]) else sma_1

        # fast_ma = ema(bb_source, fast_ma_len)
        fast_ma = ta.pine_ema(bb_source, fast_ma_len)

        # dev = stdev(bb_source, bb_length); bb_dev = bb_mult * dev
        bb_dev = bb_mult * ta.pine_stdev(bb_source, bb_length)
        bb_upper = bb_basis + bb_dev
        bb_lower = bb_basis - bb_dev

        # Awesome Oscillator, verbatim nested ternary.
        x_sma1_hl2 = ta.pine_sma(hl2, int(params["nLengthFast"]))
        x_sma2_hl2 = ta.pine_sma(hl2, int(params["nLengthSlow"]))
        x_sma1_sma2 = x_sma1_hl2 - x_sma2_hl2
        previous = x_sma1_sma2.shift(1)
        # `na >= 0` and `na > na` are both false in Pine, so an na value falls
        # to the outer false branch and then to -2. Keep that literal.
        non_negative = (x_sma1_sma2 >= 0).fillna(False).astype(bool)
        rising = (x_sma1_sma2 > previous).fillna(False).astype(bool)
        ao = pd.Series(
            np.where(
                non_negative.to_numpy(),
                np.where(rising.to_numpy(), 1.0, 2.0),
                np.where(rising.to_numpy(), -1.0, -2.0),
            ),
            index=dataframe.index,
        )

        # spread = bb_upper - bb_lower; avgspread = sma(spread, sqz_length)
        spread = bb_upper - bb_lower
        bb_squeeze = spread / ta.pine_sma(spread, sqz_length) * 100.0

        # break_down / break_up, written in the source's own order.
        cross_down = ta.pine_crossunder(fast_ma, bb_basis)
        cross_up = ta.pine_crossover(fast_ma, bb_basis)
        bb_ok_down = True if not bb_filter else (close > bb_lower)
        bb_ok_up = True if not bb_filter else (close < bb_upper)
        sqz_ok = True if not sqz_filter else (bb_squeeze > sqz_threshold)

        break_down = (
            cross_down
            & (close < bb_basis)
            & (ao.abs() == 2)
            & bb_ok_down
            & sqz_ok
        )
        break_up = (
            cross_up
            & (close > bb_basis)
            & (ao.abs() == 1)
            & bb_ok_up
            & sqz_ok
        )

        dataframe["pine_bb_basis"] = bb_basis
        dataframe["pine_fast_ma"] = fast_ma
        dataframe["pine_bb_upper"] = bb_upper
        dataframe["pine_bb_lower"] = bb_lower
        dataframe["pine_ao"] = ao
        dataframe["pine_bb_squeeze"] = bb_squeeze
        dataframe["pine_break_down"] = break_down.fillna(False).astype(bool)
        dataframe["pine_break_up"] = break_up.fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "break_down": dataframe["pine_break_down"].to_numpy(),
            "break_up": dataframe["pine_break_up"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if break_up
        #     strategy.entry("Enter Long", strategy.long)
        # else if break_down
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["break_up"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["break_down"][i]:
            broker.entry("Enter Short", "short")
