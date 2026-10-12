"""Port of sources/SM_1207d52783e7f3b4.pine (batch_001/BB-RSI-ADX-Entry-Points.md).

Pine v5. The file declares `indicator(...)`, NOT `strategy(...)`: the two
`strategy.entry` calls at the bottom are an order block APPENDED to the
indicator by the converter site that published it (fmz.com/strategy/362403,
named in the md's Detail link). Pine v5 does not compile `strategy.entry`
inside `indicator()`, so the "original strategy" is the indicator PLUS that
appended block, and the trading behaviour it defines is entry-only:

    enter_long  = (low < lower) and (bbr > 0) and (rsi > 30) and (rsi < 50)
                  and (adxStr > 25)  ? 1 : 0
    enter_short = (high > upper) and (bbr < 1) and (rsi > 50) and (rsi < 70)
                  and (adxStr > 25)  ? -1 : 0

    if enter_long
        strategy.entry("Enter Long", strategy.long)
    else if enter_short
        strategy.entry("Enter Short", strategy.short)

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, not even a commented-out one (only two commented `plotarrow`
calls). A position is therefore only ever left by the opposite entry, which the
engine models as a reversal. `pyramiding` keeps Pine's default of 0, so a
repeated signal while already positioned that way is ignored.

The `else if` is kept as `elif`: the two conditions are mutually exclusive
except in the degenerate case of a zero-width band (stdev 0 makes
upper == lower, and `low < X < high` is then satisfiable), where Pine would
still place only the long order.

FIDELITY:

* `-1` truthiness. `enter_short` is `... ? -1 : 0` and the source tests it as a
  BARE condition (`else if enter_short`). Pine and Python both treat -1 as
  true, so the direct translation is the faithful one. The column is kept as
  integers (-1 / 0) and tested with a plain `elif`, deliberately NOT rewritten
  as `== 1` / `> 0`, which would silently switch every short entry off
  (PINE_SEMANTICS.md 1.17).
* `ta.stdev` is Pine's population (biased) standard deviation; pine_ta's
  `pine_stdev` uses ddof=0 to match.
* `bbr` is computed off the stDev-1 bands (`devMinOne`), as the md's note says.
* The RSI here is written out exactly as the source writes it rather than
  routed through `pine_ta.pine_rsi`: same formula (`ta.rma` of the gains and of
  the losses), same two edge rules (`rsiDown == 0 -> 100`, `rsiUp == 0 -> 0`)
  and the same na propagation.
* `dirmov()` / `adx()` are the source's own ADX, not a library substitute: `up`
  and `down` are changes of the raw high/low, the DMs carry an explicit na on
  the first bar, `ta.tr` is used WITHOUT `handle_na`, and both DI lines go
  through `fixnan`. See the fidelity notes for the one known boundary
  divergence (`ta.tr` on bar 0, PINE_SEMANTICS.md 3.7).
* `ta.rma` is pine_ta's documented Wilder model (SMA-seeded over the first
  `length` non-na observations), an unpublished TradingView rule
  (PINE_SEMANTICS.md 3.1/3.2).
* The `plot` / `fill` calls, the two commented `plotarrow` calls and the
  `src` / `rsiSourceInput` inputs' menu alternatives are display-only; they
  place no order. Both source inputs default to `close` and are read back
  through `pine_source`.
* The md's "Enter SHORT Conditions" list omits the source's `rsi > 50` term
  (it lists only BB %B < 1, RSI < 70, ADX > 25). The CODE is followed; the
  prose is incomplete, and this is recorded rather than reconciled.
* The md's "work best on a 3 minute timeframe" is prose; the header declares
  `period: 1h`, so `timeframe` is "1h". The header's `basePeriod: 15m` is the
  host's intrabar granularity, not the strategy's period.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* The header's backtest window (2022-04-10 to 2022-05-09) is extraction
  metadata, not an `input.time` filter, so no data is trimmed.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_div(numerator, denominator):
    """Pine division: a zero denominator yields na, not inf."""
    return numerator / denominator.replace(0.0, np.nan)


def _fixnan(series: pd.Series) -> pd.Series:
    """Pine `fixnan`: replace na with the closest non-na value on the left."""
    return series.ffill()


def _dirmov(dataframe: pd.DataFrame, length: int):
    """Pine `dirmov(len)` from the source, returning (plus, minus).

    `up = ta.change(high)`, `down = -ta.change(low)`, and each DM is na on the
    bar whose change is na (the first), otherwise the directional move when it
    dominates and is positive. `ta.rma(ta.tr, len)` -- note `ta.tr` with
    handle_na left at its default false -- is the denominator, and both ratios
    go through `fixnan`.
    """
    up = ta.pine_change(dataframe["high"])
    down = -ta.pine_change(dataframe["low"])
    plus_dm = pd.Series(
        np.where(up.isna(), np.nan, np.where((up > down) & (up > 0.0), up, 0.0)),
        index=dataframe.index,
        dtype=float,
    )
    minus_dm = pd.Series(
        np.where(down.isna(), np.nan, np.where((down > up) & (down > 0.0), down, 0.0)),
        index=dataframe.index,
        dtype=float,
    )
    true_range = ta.pine_rma(ta.pine_tr(dataframe), length)
    plus = _fixnan(_pine_div(100.0 * ta.pine_rma(plus_dm, length), true_range))
    minus = _fixnan(_pine_div(100.0 * ta.pine_rma(minus_dm, length), true_range))
    return plus, minus


def _adx(dataframe: pd.DataFrame, di_length: int, adx_length: int) -> pd.Series:
    """Pine `adx(dilen, adxlen)` from the source: the smoothed |DI+ - DI-|."""
    plus, minus = _dirmov(dataframe, di_length)
    total = plus + minus
    # `sum == 0 ? 1 : sum` -- an na sum stays na, which is not a division by zero.
    denominator = total.mask(total == 0.0, 1.0)
    return 100.0 * ta.pine_rma((plus - minus).abs() / denominator, adx_length)


class SMBbRsiAdxEntryPoints_1207d5(PinePortBase, IStrategy):
    source_id = "SM_1207d52783e7f3b4"
    source_file = "BB-RSI-ADX-Entry-Points.md"
    timeframe = "1h"
    can_short = True
    # Input defaults, exactly as written in the source.
    source_defaults: dict = {
        "bbLength": 9,
        "src": "close",
        "stDev": 2.0,
        "rsiLength": 14,
        "rsiSourceInput": "close",
        "adxlen": 14,
        "dilen": 14,
        "c_adx_min_str": 25,
        "c_enter_long_bbr": 0,
        "c_enter_long_rsi_min": 30,
        "c_enter_long_rsi_max": 50,
        "c_enter_short_bbr": 1,
        "c_enter_short_rsi_min": 50,
        "c_enter_short_rsi_max": 70,
    }
    # The source declares indicator(...), not strategy(...), so no strategy()
    # properties exist and Pine's documented defaults apply: market orders of
    # `fixed` size 1 contract, initial capital 1000000, commission 0%,
    # pyramiding 0, process_orders_on_close=false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere in the
    # source -- not even a commented-out one.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The source declares indicator(...) and appends strategy.entry calls, so "
        "it has no strategy() properties; Pine's documented defaults are what "
        "the source_* attributes record (fixed size 1, 0% commission, "
        "pyramiding 0, initial capital 1000000). On TradingView strategy.entry "
        "inside an indicator does not compile; the host named by the source's "
        "/*backtest header and the md's Detail link (fmz.com/strategy/362403) "
        "is what ran the appended block, and that platform's Pine dialect -- "
        "not TradingView -- is the behaviour this port reproduces.",
        "`enter_short` is `... ? -1 : 0` and the source tests it as a bare "
        "condition (`else if enter_short`). -1 is true in both Pine and Python, "
        "so the direct translation is faithful and the column keeps its integer "
        "values (-1 / 0). It is deliberately NOT rewritten to `== 1` or `> 0`, "
        "which would silently disable every short entry (PINE_SEMANTICS.md "
        "1.17). enter_long stays `? 1 : 0`.",
        "The source has no exit at all: no strategy.close, no strategy.exit, no "
        "stop/limit/trail, and no commented-out exit line either (only two "
        "commented plotarrow calls). A position is left only by the opposite "
        "entry, which the engine models as a reversal; source_reproduce_stops "
        "is False accordingly.",
        "ta.tr is used with handle_na at its default (false), so on the ORIGINAL "
        "platform bar 0 of ta.tr is na and the ta.rma denominator starts "
        "seeding one bar later. pine_ta.pine_tr gives high-low on bar 0 instead "
        "and cannot be changed from a port (it is shared layer), so the "
        "truerange seeding -- and with it every DI/ADX value, converging "
        "afterwards -- can be offset by one bar near the warmup. Recorded, not "
        "worked around; PINE_SEMANTICS.md 3.7.",
        "ta.rma uses pine_ta's documented Wilder model (SMA-seeded over the "
        "first `length` non-na observations, na skipped without advancing the "
        "recursion). TradingView does not publish its seeding rule, so the "
        "RSI and the ADX inherit that unverified choice "
        "(PINE_SEMANTICS.md 3.1/3.2/3.3).",
        "The DI lines are passed through fixnan, which is modelled as a "
        "forward-fill (the closest non-na value to the left). This is what "
        "makes `adxStr` defined on any bar where the divisibility broke down.",
        "Division: Pine yields na for a zero denominator, so the port's "
        "_pine_div replaces a zero denominator with na rather than letting "
        "pandas produce +-inf. The `sum == 0 ? 1 : sum` guard in the ADX is "
        "reproduced literally.",
        "ta.stdev is Pine's population (biased) standard deviation; "
        "pine_ta.pine_stdev uses ddof=0 to match. The md's note that the BB %B "
        "is calculated off the stDev-1 bands matches the code's devMinOne.",
        "The md's 'Enter SHORT Conditions' list omits the source's `rsi > 50` "
        "term (it names only BB %B < 1, RSI < 70, ADX > 25). The code is "
        "followed; the prose is incomplete. Recorded, not reconciled.",
        "The md says the strategy works best on a 3 minute timeframe; the "
        "/*backtest header declares period: 1h, so timeframe is '1h'. The "
        "header's basePeriod: 15m is the host's intrabar granularity for "
        "filling 1h bars, not the strategy's period.",
        "The plot/fill calls, the two commented plotarrow calls and the "
        "colour/menu inputs are display-only and place no order; the src and "
        "rsiSource inputs both default to close and are read back through "
        "pine_source.",
        "The backtest window in the header (2022-04-10 to 2022-05-09) is "
        "extraction metadata, not an input.time filter, so the port runs on "
        "whatever range the caller supplies.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        src = ta.pine_source(dataframe, str(params["src"]))
        st_dev = float(params["stDev"])
        bb_length = int(params["bbLength"])

        # basis / dev / devMinOne / upper-lower / upperMinOne-lowerMinOne
        basis = ta.pine_sma(src, bb_length)
        stdev = ta.pine_stdev(src, bb_length)
        dev = st_dev * stdev
        dev_min_one = (st_dev - 1.0 if st_dev > 1.0 else 1.0) * stdev
        upper = basis + dev
        lower = basis - dev
        upper_min_one = basis + dev_min_one
        lower_min_one = basis - dev_min_one
        # bbr = (src - lowerMinOne) / (upperMinOne - lowerMinOne)
        bb_percent_b = _pine_div(src - lower_min_one, upper_min_one - lower_min_one)

        # rsiUp / rsiDown / rsi, written exactly as the source writes them.
        rsi_source = ta.pine_source(dataframe, str(params["rsiSourceInput"]))
        rsi_length = int(params["rsiLength"])
        change = ta.pine_change(rsi_source)
        rsi_up = ta.pine_rma(change.clip(lower=0.0), rsi_length)
        rsi_down = ta.pine_rma((-change).clip(lower=0.0), rsi_length)
        ratio = _pine_div(rsi_up, rsi_down)
        rsi = 100.0 - 100.0 / (1.0 + ratio)
        # rsiDown == 0 ? 100 : rsiUp == 0 ? 0 : <the expression above>
        rsi = rsi.mask(rsi_down == 0.0, 100.0)
        rsi = rsi.mask((rsi_down != 0.0) & (rsi_up == 0.0), 0.0)

        adx_str = _adx(dataframe, int(params["dilen"]), int(params["adxlen"]))

        dataframe["pine_basis"] = basis
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        dataframe["pine_bb_percent_b"] = bb_percent_b
        dataframe["pine_rsi"] = rsi
        dataframe["pine_adx_str"] = adx_str

        # enter_long = (low < lower) and (bbr > min) and (rsi > rsi_min)
        #              and (rsi < rsi_max) and (adxStr > adx_min) ? 1 : 0
        long_condition = (
            (dataframe["low"] < lower)
            & (bb_percent_b > float(params["c_enter_long_bbr"]))
            & (rsi > float(params["c_enter_long_rsi_min"]))
            & (rsi < float(params["c_enter_long_rsi_max"]))
            & (adx_str > float(params["c_adx_min_str"]))
        )
        # enter_short = (high > upper) and (bbr < max) and (rsi > rsi_min)
        #               and (rsi < rsi_max) and (adxStr > adx_min) ? -1 : 0
        short_condition = (
            (dataframe["high"] > upper)
            & (bb_percent_b < float(params["c_enter_short_bbr"]))
            & (rsi > float(params["c_enter_short_rsi_min"]))
            & (rsi < float(params["c_enter_short_rsi_max"]))
            & (adx_str > float(params["c_adx_min_str"]))
        )
        # Integer columns, not booleans: -1 must stay -1 (PINE_SEMANTICS.md 1.17).
        dataframe["pine_enter_long"] = np.where(long_condition.to_numpy(), 1, 0)
        dataframe["pine_enter_short"] = np.where(short_condition.to_numpy(), -1, 0)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "enter_long": dataframe["pine_enter_long"].to_numpy(),
            "enter_short": dataframe["pine_enter_short"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if enter_long
        #     strategy.entry("Enter Long", strategy.long)
        # else if enter_short
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["enter_long"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["enter_short"][i]:
            broker.entry("Enter Short", "short")
