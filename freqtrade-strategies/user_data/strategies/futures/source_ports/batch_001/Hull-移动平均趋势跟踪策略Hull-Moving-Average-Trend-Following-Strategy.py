"""Port of sources/SM_45fc926c15c668a7.pine (batch_001/Hull-移动平均趋势跟踪策略Hull-Moving-Average-Trend-Following-Strategy.md).

Pine **v2** (`//@version=2`, bare builtins: `sma`, `ema`, `highest`, `lowest`,
`cross`, `rising`, `falling`, `valuewhen`, `security`). The conversion station
appended the order block, and it is the whole trade behaviour
(PINE_SEMANTICS.md 1.17):

    longCondition = direction > 0 and direction2 > 0
    if (longCondition)
        strategy.entry("BUY", strategy.long)
    shortCondition = direction < 0 and direction2 < 0
    if (shortCondition)
        strategy.entry("SELL", strategy.short)

Note the shape: TWO SEPARATE `if` statements, not an if/else-if, so the source's
writing order is BUY first and SELL second, and the port keeps that order. There
is no `strategy.close`/`strategy.exit`/stop anywhere, so entries never exit
except by an opposing entry netting them.

The only inputs that reach an order are the two EMA lengths:

    ema0     = ema(close, len0)          # len0  = input(13)
    direction  = rising(ema0, 2)  ? +1 : falling(ema0, 2)  ? -1 : 0
    ema02    = ema(close, len02)         # len02 = input(21)
    direction2 = rising(ema02, 2) ? +1 : falling(ema02, 2) ? -1 : 0

Everything else the source computes -- the SMA candle-body channel (`out`,
`last8h`, `lastl8`), the support/resistance lines (`RSTT`, `RSTB`), the Hull MA
(`hullma`, `dif_close_hull`, `Percent_dif`) and the two `security(syminfo.tickerid,
Piriod, ...)` fetches -- is read only by `plot()` calls and places no order.
They are computed and kept as ledger columns for the record, except the
`security()` fetches, which the engine does not model at all
(PINE_SEMANTICS.md 二.1) and which are therefore not reproduced.

`strategy()` is present in the file but COMMENTED OUT -- line 11
`// strategy(title='HULLMiguel 2019/ Strategy v3', ..., pyramiding=0,
default_qty_value=1000, initial_capital=1000, currency=currency.USD)`. A
commented-out call declares nothing, so every `source_*` property below is
Pine's DOCUMENTED DEFAULT (fixed / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0), not the values inside the comment. The commented
values are recorded, not applied (rule 2).

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the host backtester's own
granularity for filling those 1h bars, not the strategy's period.

FIDELITY:

* THE `security()` CALLS ARE NOT REPRODUCED. `ch1 = security(syminfo.tickerid,
  Piriod, open)` and `ch2 = security(..., close)` with `Piriod = input('720')`
  request a 720-minute series; the engine does not resample and does not model
  `request.security` (PINE_SEMANTICS.md 二.1). Both results are consumed only by
  `plot(ch1, ...)`, and the source's own commented-out long/short conditions
  that would have used them (`//longCondition = crossover(security(...), ...)`)
  are commented out, so no order depends on them. Nothing is approximated in
  their place.
* `rising`/`falling` are not exposed by pine_ta and are translated here as
  Pine's documented test ("is now rising for `length` bars long"): strictly
  higher (lower) on EACH of the last `length` steps, consecutive, with equality
  breaking the run, and na comparisons false. This is the same reading already
  used by batch_001/3EMA.py (SM3Ema_c5893b). HOWEVER, this source is Pine v2
  while 3EMA is v5; the reference text for `ta.rising` also says "greater than
  any previous value for `length` bars back", which for `length = 2` would be
  `x > x[1] and x > x[2]` rather than `x > x[1] and x[1] > x[2]`. The two
  readings differ on bars where the series is above its 2-bars-ago value but
  not above the previous bar. The consecutive reading is used for consistency
  with the existing verified port; the ambiguity is recorded, not resolved.
* v2 `cross(close, out) == 1` is v2's `crossover` returning an integer 0/1;
  `pine_ta.pine_crossover` supplies the modelled boolean, and `== 1` on a
  boolean is the same test. It appears only in the `bearish`/`bullish`
  variables, which no order reads (they are unused in the source beyond being
  assigned).
* `valuewhen(high >= highest(high, RST), high, 0)` and its low-side mirror feed
  `plot()` only, so the S/R lines are display-only.
* `hullma(src, length) => wma(2*wma(src, length/2) - wma(src, length),
  round(sqrt(length)))` with `length = hma_base_length + hma_length_scalar*6 =
  76` feeds `plot()` and `dif_close_hull`/`Percent_dif`, which are themselves
  only assigned (their `plot` line is commented out). Reproduced for the record;
  `length/2` is Pine's automatic float-to-int cast, so 76/2 -> 38.
* The `channel2` input switches the candle-body channel between "always plot"
  and "only while the level is unchanged" inside the `plot()` calls; display
  only, so the port computes the levels and ignores the switch.
* `sma`/`highest`/`lowest`/`valuewhen` return na until their window is full, so
  every condition built on them is false during warmup; na propagates rather
  than being filled. `ta.ema` is seeded with the first non-na observation
  (pine_ta's documented model); TradingView's seeding rule is unpublished
  (PINE_SEMANTICS.md 3.1), so the two EMAs differ from the original platform's
  until they converge.
* Division by zero and na arithmetic propagate as in Pine; no guard is added.
* No exit of any kind exists, so `source_reproduce_stops` is False and a
  position open at the end of the window stays open.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _rising(series: pd.Series, length: int) -> pd.Series:
    """Pine `rising`: strictly higher on each of the last `length` steps.

    Pine's documented test is "is now rising for `length` bars long", and the
    steps must be CONSECUTIVE -- equality breaks the run. na on either side of
    a comparison makes it false, as Pine treats na comparisons.
    """
    rising = pd.Series(True, index=series.index)
    for step in range(int(length)):
        rising &= series.shift(step) > series.shift(step + 1)
    return rising


def _falling(series: pd.Series, length: int) -> pd.Series:
    """Pine `falling`: strictly lower on each of the last `length` steps."""
    falling = pd.Series(True, index=series.index)
    for step in range(int(length)):
        falling &= series.shift(step) < series.shift(step + 1)
    return falling


class SMHullMovingAverageTrendFollowing_45fc92(PinePortBase, IStrategy):
    source_id = "SM_45fc926c15c668a7"
    source_file = "Hull-移动平均趋势跟踪策略Hull-Moving-Average-Trend-Following-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "src": "close",
        "channel2": False,
        "RST": 15,
        "len0": 13,
        "len02": 21,
        "show_hma": False,
        "hma_src": "close",
        "hma_base_length": 16,
        "hma_length_scalar": 10,
        "Piriod": "720",
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The file is a v2 indicator plus an order block APPENDED by the "
        "conversion station: `longCondition = direction > 0 and direction2 > "
        "0` with `strategy.entry(\"BUY\", long)`, then a SEPARATE `if` for "
        "`shortCondition = direction < 0 and direction2 < 0` with "
        "`strategy.entry(\"SELL\", short)`. That is the whole trade behaviour "
        "and there is no exit call (PINE_SEMANTICS.md 1.17).",
        "The two entries are two separate `if` statements, not an if/else-if; "
        "the port keeps the source's writing order (BUY placed first, SELL "
        "second).",
        "`request.security(syminfo.tickerid, Piriod, open/close)` with "
        "`Piriod = '720'` is NOT reproduced: the engine does not resample and "
        "does not model request.security (PINE_SEMANTICS.md 二.1). Both results "
        "feed only `plot(ch1, ...)`, and the source's conditions that would "
        "have used them are commented out, so no order depends on them and "
        "nothing is substituted in their place.",
        "`rising`/`falling` are expanded in this file as 'strictly higher "
        "(lower) on EACH of the last `length` steps, consecutive, equality "
        "breaks the run' -- the reading already used by batch_001/3EMA.py. "
        "This source is Pine v2 and the published wording ('greater than any "
        "previous value for `length` bars back') would instead give "
        "`x > x[1] and x > x[2]` for `length = 2`; the two differ on bars that "
        "are above the 2-bars-ago value but not above the previous bar. The "
        "consecutive reading is used for consistency with the existing port; "
        "the ambiguity is recorded, not resolved.",
        "v2 `cross(close, out) == 1` is v2's integer-valued crossover; it "
        "feeds `bearish`/`bullish`, which no order reads.",
        "The `strategy(...)` line is COMMENTED OUT, so no strategy() property "
        "is declared and Pine's documented defaults apply: fixed / 1 "
        "contract, initial capital 1000000, commission 0%, pyramiding 0. The "
        "commented line's values (default_qty_value=1000, initial_capital=1000) "
        "are NOT applied -- a comment places nothing.",
        "Display-only and reproduced for the record but never read by an "
        "order: the SMA candle-body channel (`out`, `last8h`, `lastl8`), the "
        "support/resistance levels (`RSTT`, `RSTB`), and the Hull MA set "
        "(`hullma`, `dif_close_hull`, `Percent_dif`).",
        "`hullma`'s length is `hma_base_length + hma_length_scalar*6 = 76` and "
        "its inner `length/2` is Pine's automatic float-to-int cast (76 -> 38); "
        "the outer `round(sqrt(76))` is 9.",
        "The `channel2` display switch decides whether the body channel is "
        "plotted unconditionally or only while unchanged; it does not change "
        "the level, and no order reads it.",
        "sma/highest/lowest/valuewhen are na until their window is full, so "
        "every condition built on them is false during warmup; na propagates "
        "rather than being filled.",
        "ta.ema is seeded with the first non-na observation (pine_ta's "
        "documented model); TradingView's seeding rule is unpublished, so both "
        "EMAs differ from the original platform's until they converge "
        "(PINE_SEMANTICS.md 3.1).",
        "No exit exists, so source_reproduce_stops is False and a position "
        "open at the window's end stays open; only an opposing entry nets it "
        "(PINE_SEMANTICS.md 1.1).",
        "md-vs-source: the md describes the system as 'Hull MA cross plus EMA "
        "agreement plus a candle-body channel filter', but the code trades "
        "only the two EMA-derived `direction` values -- the Hull MA and the "
        "body channel feed plots, not orders. The code is followed; the "
        "disagreement is recorded.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        # ------------------ display-only: candle body resistance channel -----
        len_channel = 34  # literal in the source, not an input
        out = ta.pine_sma(ta.pine_source(dataframe, str(params["src"])), len_channel)
        dataframe["pine_body_sma"] = out
        dataframe["pine_last8h"] = ta.pine_highest(close, 13)
        dataframe["pine_lastl8"] = ta.pine_lowest(close, 13)

        # ------------------ display-only: support / resistance ---------------
        rst = int(params["RST"])
        rstt = ta.pine_valuewhen(high >= ta.pine_highest(high, rst), high, 0)
        rstb = ta.pine_valuewhen(low <= ta.pine_lowest(low, rst), low, 0)
        dataframe["pine_rstt"] = rstt
        dataframe["pine_rstb"] = rstb

        # ------------------ display-only: Hull MA set ------------------------
        hma_length = int(params["hma_base_length"]) + int(params["hma_length_scalar"]) * 6
        half = int(hma_length / 2)
        hma_src = ta.pine_source(dataframe, str(params["hma_src"]))
        hullma = ta.pine_wma(
            2.0 * ta.pine_wma(hma_src, half) - ta.pine_wma(hma_src, hma_length),
            int(ta.pine_round(np.sqrt(hma_length), 0)),
        )
        dif_close_hull = (close - hullma) / close
        dataframe["pine_hullma"] = hullma
        dataframe["pine_dif_close_hull"] = dif_close_hull
        dataframe["pine_percent_dif"] = dif_close_hull / hullma

        # ------------------ the trading indicators ---------------------------
        len0 = int(params["len0"])
        ema0 = ta.pine_ema(close, len0)
        rising0 = _rising(ema0, 2)
        falling0 = _falling(ema0, 2)
        # direction = rising(ema0, 2) ? +1 : falling(ema0, 2) ? -1 : 0
        direction = pd.Series(
            np.where(rising0, 1, np.where(falling0, -1, 0)), index=close.index
        )

        len02 = int(params["len02"])
        ema02 = ta.pine_ema(close, len02)
        rising02 = _rising(ema02, 2)
        falling02 = _falling(ema02, 2)
        direction2 = pd.Series(
            np.where(rising02, 1, np.where(falling02, -1, 0)), index=close.index
        )

        dataframe["pine_ema0"] = ema0
        dataframe["pine_direction"] = direction
        dataframe["pine_ema02"] = ema02
        dataframe["pine_direction2"] = direction2

        # longCondition = direction > 0 and direction2 > 0
        # shortCondition = direction < 0 and direction2 < 0
        dataframe["pine_long_condition"] = ((direction > 0) & (direction2 > 0))
        dataframe["pine_short_condition"] = ((direction < 0) & (direction2 < 0))
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if (longCondition)
        #     strategy.entry("BUY", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("BUY", "long")
        # if (shortCondition)
        #     strategy.entry("SELL", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("SELL", "short")
