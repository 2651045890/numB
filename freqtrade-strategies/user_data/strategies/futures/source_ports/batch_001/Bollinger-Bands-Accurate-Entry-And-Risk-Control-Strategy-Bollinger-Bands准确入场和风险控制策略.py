"""Port of sources/SM_45e4375cf0376402.pine (batch_001/Bollinger-Bands-Accurate-Entry-And-Risk-Control-Strategy-Bollinger-Bands准确入场和风险控制策略.md).

Pine v5. `strategy("Bollinger Bands Strategy", overlay=true)` declares no
sizing, no commission and no pyramiding, so all three stay at Pine's documented
defaults (fixed / 1 contract, 0%, pyramiding 0 -- see the attributes below).

    src    = input(close)                  (source input, defval = close)
    length = input.int(34, minval=1)
    mult   = input.float(2.0, minval=0.001, maxval=50)
    basis  = ta.sma(src, length)
    dev    = ta.stdev(src, length)
    dev2   = mult * dev
    upper1 = basis + dev      lower1 = basis - dev
    upper2 = basis + dev2     lower2 = basis - dev2
    longCondition  = close > upper1
    shortCondition = close < lower1

Note that the source's `mult` only ever reaches `upper2` / `lower2`, which are
computed and then never used: the traded bands are the ONE-standard-deviation
`upper1` / `lower1`. The port reproduces both band pairs and trades the ones the
conditions actually name.

    strategy.entry("Long",  strategy.long,  when = longCondition)
    strategy.entry("Short", strategy.short, when = shortCondition)
    strategy.close("Long",  when = shortCondition)
    strategy.close("Short", when = longCondition)

`close > upper1` and `close < lower1` cannot both hold (upper1 > lower1), so the
two entries never fire on the same bar; a reversal therefore always arrives as
an entry next to a close for the opposite id, settled on the next bar's open in
source order.

FIDELITY:

* `ta.stdev` is Pine's POPULATION standard deviation (ddof = 0);
  `pine_ta.pine_stdev` implements exactly that, so it is used rather than a
  same-named library function with the sample (ddof = 1) convention.
* `input(close)` in v5 is a `source` input whose default is the `close` series;
  it is carried as the source name "close" and resolved through
  `pine_ta.pine_source`, so a caller can still override it.
* `minval` / `maxval` are input constraints, not strategy behaviour; they are
  recorded with the defaults and are not enforced at run time.
* No stop / limit / trail exit exists, so `source_reproduce_stops` is False; a
  position is only ever closed by the opposite `strategy.close` or reversed by
  the opposite entry, and one still open at the window's end stays open.
* The three `plot` calls are display-only and are not reproduced.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are unmodelled (PINE_SEMANTICS.md section 2); the chain verifier measures the
  rounding separately rather than the port reproducing it.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsAccurate_45e437(PinePortBase, IStrategy):
    source_id = "SM_45e4375cf0376402"
    source_file = (
        "Bollinger-Bands-Accurate-Entry-And-Risk-Control-Strategy-"
        "Bollinger-Bands准确入场和风险控制策略.md"
    )
    timeframe = "1d"
    can_short = True
    # Every input() in the source, with its defval (and its minval/maxval, which
    # are documented here but are not strategy behaviour).
    source_defaults: dict = {
        "src": "close",      # input(close), source input
        "length": 34,        # input.int(34, minval=1)
        "mult": 2.0,         # input.float(2.0, minval=0.001, maxval=50)
    }
    # strategy("Bollinger Bands Strategy", overlay=true) states no sizing,
    # commission or pyramiding, so Pine's documented defaults apply: fixed / 1,
    # 0%, pyramiding 0, initial capital 1000000, process_orders_on_close=false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`mult` only reaches upper2/lower2, which are computed and then never "
        "read: the traded bands are the one-standard-deviation upper1/lower1.",
        "`dev` is Pine's POPULATION stdev (ddof=0), matching "
        "pine_ta.pine_stdev, not a sample-stdev library default.",
        "`input(close)` is a v5 source input (default = the close series), "
        "carried as the source name \"close\" so it stays overridable.",
        "`minval`/`maxval` on the two numeric inputs are recorded but are input "
        "constraints, not run-time strategy behaviour.",
        "No stop/limit/trail exit exists: source_reproduce_stops is False and a "
        "position open at the end of the window stays open.",
        "plot() calls are display-only. Leverage/margin/liquidation/funding and "
        "the venue's contract-step rounding are unmodelled (PINE_SEMANTICS.md "
        "section 2).",
    ]

    def pine_indicators(self, dataframe, params):
        src = ta.pine_source(dataframe, params["src"])
        length = int(params["length"])
        mult = float(params["mult"])

        basis = ta.pine_sma(src, length)
        dev = ta.pine_stdev(src, length)
        dev2 = mult * dev

        upper1 = basis + dev
        lower1 = basis - dev
        upper2 = basis + dev2
        lower2 = basis - dev2

        close = dataframe["close"]
        long_condition = (close > upper1).fillna(False)
        short_condition = (close < lower1).fillna(False)

        dataframe["pine_basis"] = basis
        dataframe["pine_dev"] = dev
        dataframe["pine_upper1"] = upper1
        dataframe["pine_lower1"] = lower1
        dataframe["pine_upper2"] = upper2
        dataframe["pine_lower2"] = lower2
        dataframe["pine_long_condition"] = long_condition
        dataframe["pine_short_condition"] = short_condition
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Long", strategy.long, when = longCondition)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # strategy.entry("Short", strategy.short, when = shortCondition)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
        # strategy.close("Long", when = shortCondition)
        if ctx["short_condition"][i]:
            broker.close("Long")
        # strategy.close("Short", when = longCondition)
        if ctx["long_condition"][i]:
            broker.close("Short")
