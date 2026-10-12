"""Port of sources/SM_5aced235fcdfc0c3.pine (batch_001/30分钟震荡交易策略30-Minute-Swing-Trading-Strategy.md).

Pine v2. The file is "cowboy30minswing" -- an INDICATOR-style script whose only
declaration is COMMENTED OUT (`// strategy("cowboy30minswing", overlay=true,
default_qty_type=strategy.cash, default_qty_value=10000, scale=true,
initial_capital=10000, currency=currency.USD)`) -- plus a converter-appended
order block at the end. The trading behaviour IS that block:

    n     = input(70)
    n2ma  = 2*wma(close,   round(n/2))      nma  = wma(close,   n)
    diff  = n2ma - nma                      sqn  = round(sqrt(n))
    n2ma1 = 2*wma(close[1], round(n/2))     nma1 = wma(close[1], n)
    diff1 = n2ma1 - nma1
    n1    = wma(diff,  sqn)                 # a Hull-style trend line
    n2    = wma(diff1, sqn)                 # the same line one bar earlier
    condDown = n2 >= n1
    condUp   = condDown != true

    if condUp
        strategy.entry("Enter Long", strategy.long)
    else if condDown
        strategy.entry("Enter Short", strategy.short)

Because `diff1` is built from `close[1]`, `n2` is `n1` delayed by one bar, so
`condUp` means "the trend line is rising" and `condDown` means "it is flat or
falling" -- the whole strategy is a direction vote on that line.

The commented declaration is NOT a declaration: Pine's documented defaults are
used instead -- `default_qty_type` fixed, `default_qty_value` 1 CONTRACT,
`initial_capital` 1000000, commission 0%, `pyramiding` 0. The commented
`cash`/10000/10000 sizing is recorded in `source_fidelity_notes` so the reading
hides nothing. (The same reading is applied in the other direction: nothing
commented out in this file is restored.)

FIDELITY:

* na semantics, and this is the delicate part. Pine's `>=` / `!=` PROPAGATE na:
  `n2 >= n1` is na while either WMA is undefined (both are na for the first ~77
  bars: `wma(close, 70)` needs 70 bars, `wma(close[1], 70)` one more, and
  `wma(diff, 8)` eight more). `condDown != true` is then na as well, and an
  `if` on na does not execute its branch, so NEITHER side fires during warm-up.
  A literal pandas translation would silently invert this -- `nan >= nan` is
  False, and `False != True` is True -- and would open a LONG on every warm-up
  bar the source never traded. The port therefore requires both operands to be
  defined before either condition is treated as true. This is the only
  modelling latitude in the file and it changes at most the first ~77 bars,
  before the trend line exists at all.
* All the declared-and-unused pieces are kept visible rather than deleted:
  `length`/`overSold`/`overBought`/`fastLength`/`fastLengthL`/`slowLength`/
  `slowLengthL`/`sl` are inputs, `point` and `dev` are constants,
  `mafast`/`mafastL`/`maslow`/`maslowL`/`vrsi`/`cShort` are computed, and
  `sl`/`Stop`/`Q` are computed. NONE of them appears in the appended order
  block, so none of them can change a trade. The EMAs, `vrsi` and `cShort` are
  computed anyway (columns `pine_*`) so the port does not look like it dropped
  a formula; the port's orders read only `condUp` / `condDown`.
* `round(...)` is Pine's `math.round` -- half away from zero -- which is what
  pine_ta.pine_round does. For this source both rounds are unambiguous:
  round(70/2) = 35 and round(sqrt(70)) = 8.
* `wma` is pine_ta.pine_wma (weights 1..length, newest heaviest, na while the
  window is short or contains na -- PINE_SEMANTICS.md section 3.2 records the na
  window rule as a modelled choice).
* `ema` (in the unused block) is pine_ta.pine_ema, and `rsi` is
  pine_ta.pine_rsi; both are irrelevant to orders here.
* There is NO exit: the source's `sl`/`Stop` never reach a `strategy.exit`, and
  no `strategy.close` exists, so a position is only replaced by an opposite
  entry and one open at the end of the window stays open
  (`source_reproduce_stops = False`).
* `c = n1>n2?green:red`, `plot(n1, color=col, linewidth=3)` and the commented
  `//plot(strategy.equity, ...)` are display only.
* The header says `period: 2h` even though the file is named "30 minute swing";
  the header is what the FMZ backtest ran on, so `timeframe` is "2h" (recorded
  as a name-vs-header inconsistency of the source, not silently corrected).
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
import math

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SM30MinuteSwingTrading_5aced2(PinePortBase, IStrategy):
    source_id = "SM_5aced235fcdfc0c3"
    source_file = "30分钟震荡交易策略30-Minute-Swing-Trading-Strategy.md"
    timeframe = "2h"
    can_short = True
    source_defaults: dict = {
        "n": 70,
        "length": 14,
        "overSold": 70,
        "overBought": 30,
        "fastLength": 59,
        "fastLengthL": 82,
        "slowLength": 96,
        "slowLengthL": 95,
        "sl": 75,
    }
    # The file's only strategy() call is COMMENTED OUT, so it declares nothing
    # and Pine's documented defaults apply -- see the docstring and notes.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit / strategy.close anywhere; `sl` and `Stop` are computed
    # and then never used.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Converter-appended source: the only declaration in the file is a "
        "COMMENTED-OUT strategy() call, and a tool appended the block `if "
        "condUp / strategy.entry(\"Enter Long\", strategy.long) else if "
        "condDown / strategy.entry(\"Enter Short\", strategy.short)`. The port "
        "reproduces what the appended block does: entries only.",
        "The commented `// strategy(\"cowboy30minswing\", overlay=true, "
        "default_qty_type=strategy.cash, default_qty_value=10000, scale=true, "
        "initial_capital=10000, currency=currency.USD)` is NOT a declaration -- "
        "commented code places nothing, exactly as a commented-out exit places "
        "no exit. Pine's documented defaults are used instead: fixed sizing, "
        "qty 1 CONTRACT, initial capital 1000000, commission 0%, pyramiding 0, "
        "process_orders_on_close=false. The commented values are listed here so "
        "the choice is visible.",
        "na semantics are modelled explicitly. Pine propagates na through `>=` "
        "and `!=`, and an `if` on na executes no branch, so during the first "
        "~77 bars -- while `wma(close, 70)` / `wma(close[1], 70)` / "
        "`wma(diff, 8)` are still undefined -- NEITHER entry fires. A literal "
        "pandas translation (`nan >= nan` is False, `False != true` is True) "
        "would instead open a LONG on every one of those bars. The port "
        "requires both operands to be defined. This is the file's only "
        "modelling latitude; it can only affect bars before the trend line "
        "exists.",
        "`condUp = condDown != true` is not rewritten as `n2 < n1` in the code "
        "path; it is evaluated as the negation of a defined `condDown`, which "
        "is what the source's bool comparison means in Pine v2 (and avoids the "
        "bool-as-number trap of PINE_SEMANTICS.md section 1.16).",
        "The whole RSI / EMA family (`mafast`, `mafastL`, `maslow`, `maslowL`, "
        "`vrsi`, `cShort`) and the constants `point`, `dev`, `Stop`, `Q` are "
        "declared/computed by the source but never read by the appended order "
        "block, so they cannot change a trade. They are still computed as "
        "`pine_*` columns rather than deleted, so no formula is dropped.",
        "`sl` (75) never reaches a strategy.exit: there is no exit call in the "
        "file, live or commented out. A position is closed only by an opposite "
        "entry reversing it, so source_reproduce_stops is False and a position "
        "open at the end of the window stays open.",
        "`n2` is `n1` delayed one bar (`diff1` is built from `close[1]`), so "
        "condUp means the trend line is rising and condDown means flat or "
        "falling. Equality goes to condDown, as the source's `>=` says.",
        "`round()` is pine_ta.pine_round (half away from zero); `wma` is "
        "pine_ta.pine_wma, whose na-in-window rule is a modelled choice "
        "(PINE_SEMANTICS.md section 3.2).",
        "The header says `period: 2h` while the file is named '30 minute "
        "swing' -- a source name-vs-header inconsistency, recorded and NOT "
        "silently corrected; timeframe follows the header.",
        "md-vs-source inconsistency (reading, not behaviour): the md's Strategy "
        "Logic prose describes RSI overbought/oversold entries ('Consider swing "
        "trade opportunities at extreme RSI levels') and 'Enter trades with "
        "reasonable stop loss for risk control'. The appended order block uses "
        "NO RSI and sets NO stop: it votes on the WMA trend line only, and `sl` "
        "/ `Stop` never reach an order. The md's prose is the author's intent; "
        "the source's block is the behaviour, and the latter is reproduced.",
        "md-vs-source inconsistency (provenance only): the md's Author field "
        "says ChaoZhang; the source carries no copyright line.",
        "`c = n1>n2?green:red`, `plot(n1, ...)` and the commented "
        "`//plot(strategy.equity, ...)` are display only.",
        "Leverage, margin, liquidation and funding are not modelled; the "
        "venue's contract-step rounding is not modelled either (the chain "
        "verifier measures that separately).",
    ]

    def pine_indicators(self, dataframe, params):
        n = int(params["n"])
        close = dataframe["close"]
        previous_close = close.shift(1)

        # n2ma = 2*wma(close, round(n/2)) ; nma = wma(close, n) ; diff = n2ma - nma
        # sqn = round(sqrt(n))
        half_n = int(ta.pine_round(n / 2))
        sqn = int(ta.pine_round(math.sqrt(n)))
        n2ma = 2 * ta.pine_wma(close, half_n)
        nma = ta.pine_wma(close, n)
        diff = n2ma - nma
        # n2ma1 = 2*wma(close[1], round(n/2)) ; nma1 = wma(close[1], n)
        n2ma1 = 2 * ta.pine_wma(previous_close, half_n)
        nma1 = ta.pine_wma(previous_close, n)
        diff1 = n2ma1 - nma1
        # n1 = wma(diff, sqn) ; n2 = wma(diff1, sqn)
        n1 = ta.pine_wma(diff, sqn)
        n2 = ta.pine_wma(diff1, sqn)

        # condDown = n2 >= n1 ; condUp = condDown != true
        # Pine propagates na through the comparison and an `if` on na runs no
        # branch, so a bar where either line is undefined produces neither
        # signal; pandas would read `nan >= nan` as False and then
        # `False != True` as True, i.e. a long on every warm-up bar.
        defined = n1.notna() & n2.notna()
        trend_down = (n2 >= n1) & defined
        trend_up = (~(n2 >= n1)) & defined

        dataframe["pine_n1"] = n1
        dataframe["pine_n2"] = n2
        dataframe["pine_trend_up"] = trend_up
        dataframe["pine_trend_down"] = trend_down

        # Declared by the source, computed by the source, and read by NOTHING in
        # the appended order block. Carried as columns so the formulas survive
        # the port; no order reads them.
        dataframe["pine_mafast"] = ta.pine_ema(close, int(params["fastLength"]))
        dataframe["pine_mafastL"] = ta.pine_ema(close, int(params["fastLengthL"]))
        dataframe["pine_maslow"] = ta.pine_ema(close, int(params["slowLength"]))
        dataframe["pine_maslowL"] = ta.pine_ema(close, int(params["slowLengthL"]))
        dataframe["pine_vrsi"] = ta.pine_rsi(close, int(params["length"]))
        dataframe["pine_cShort"] = ta.pine_crossunder(
            dataframe["pine_vrsi"], float(params["overBought"])
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "trend_up": dataframe["pine_trend_up"].to_numpy(),
            "trend_down": dataframe["pine_trend_down"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if condUp
        #     strategy.entry("Enter Long", strategy.long)
        # else if condDown
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["trend_up"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["trend_down"][i]:
            broker.entry("Enter Short", "short")
