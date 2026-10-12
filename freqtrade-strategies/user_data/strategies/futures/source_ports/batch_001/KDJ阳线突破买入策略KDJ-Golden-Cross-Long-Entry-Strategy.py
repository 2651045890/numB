"""Port of sources/SM_6abcdb3a367a934a.pine
(batch_001/KDJ阳线突破买入策略KDJ-Golden-Cross-Long-Entry-Strategy.md).

Pine v5 (`//@version=5`, `strategy('KDJ NVDA', shorttitle='KDJ')`). The source
carries its own smoothing function, and that function is NOT `ta.rma` -- see
below -- so the port implements the source's own recursion rather than
substituting the library one.

    bcwsma(s, l, m) =>
        _bcwsma = float(na)
        _s = s
        _l = l
        _m = m
        _bcwsma := (_m * _s + (_l - _m) * nz(_bcwsma[1])) / _l
        _bcwsma

    c = close
    h = ta.highest(high, ilong)
    l = ta.lowest(low, ilong)
    RSV = 100 * ((c - l) / (h - l))
    pK = bcwsma(RSV, isig, 1)
    pD = bcwsma(pK, isig, 1)
    pJ = 3 * pK - 2 * pD
    KDJ = math.avg(pD, pJ, pK)

    go_long = ta.crossunder(pD, pJ)

    if (inDateRange and go_long)
        strategy.entry("S", strategy.long, comment="C")
    if (inDateRange and pJ > 100)
        strategy.close("S", comment="TP")

`bcwsma(RSV, isig, 1)` is `(1*s + (l-1)*bcwsma[1]) / l`, i.e. Wilder's alpha
1/l -- but with the recursion seeded at `na` and `nz(na)` = 0, so the FIRST
valid value is `RSV / isig` rather than the SMA of the first `isig`
observations that `pine_ta.pine_rma` uses. The two agree only in the limit
(reproducing `pine_rma` here would shift every K/D value; rule 3 forbids the
substitution).

`go_long` is `ta.crossunder(pD, pJ)`: it fires on the bar where %D crosses
BELOW %J, which is the same bar %J crosses above %D -- the golden cross the md
describes. The port keeps the source's argument order.

`inDateRange` gates BOTH orders and is built from six `input.int` values:

    inDateRange = (time >= timestamp(syminfo.timezone, startYear,startMonth,
                    startDate, 0, 0))
                  and (time < timestamp(syminfo.timezone, endYear, endMonth,
                    endDate, 0, 0))

with defaults 2023-01-01 (inclusive) to 2024-01-01 (exclusive). It is a real
trading condition, so it is reproduced, not dropped: on the chain verifier's
default 2024 window every bar fails it and the port trades nothing. See
FIDELITY.

`strategy()` declares only `title` / `shorttitle` and the source has no
`overlay`, so every other property is Pine's documented default:
`default_qty_type=strategy.fixed`, `default_qty_value` 1 contract, initial
capital 1000000, commission 0%, `pyramiding=0`,
`process_orders_on_close=false`.

`can_short` is False: the only entry is `strategy.long`.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; `basePeriod: 1h` is the FMZ backtester's fill granularity.

FIDELITY:

* The commented-out `// strategy.exit("S", limit=c*profit_m, stop=c*stop_m,
  comment="SL/SP")` is NOT restored. The source's live behaviour has no exit
  level at all -- only the `pJ > 100` market close -- so `source_reproduce_stops`
  is False. The two inputs it would have read (`profit_m`, `stop_m`) are
  therefore computed-but-unused, exactly as in the source.
* The md's Chinese/English prose claims the strategy "采用止盈止损策略" (adopted
  take-profit/stop-loss) as an advantage. That describes the commented-out line
  only; the live code has no stop or limit. Recorded, not implemented.
* The md's `> Strategy Arguments` table lists the `Start Date` / `Start Month`
  / ... defaults as `true`/`true`/2023/`true`/`true`/2024, because the FMZ
  exporter rendered `input.int(defval=1, ...)` of a 1/0-flagged boolean-ish
  field oddly. The SOURCE is the authority: `startDate=1, startMonth=1,
  startYear=2023, endDate=1, endMonth=1, endYear=2024`, and the port uses those.
* `inDateRange` uses `syminfo.timezone`; the port evaluates it against the
  bar timestamps in UTC, which is the exchange timezone for BTC/USDT
  (PINE_SEMANTICS.md §3.4 records the general risk).
* The end of the window is EXCLUSIVE (`time < timestamp(...)`). The chain
  verifier's default range is 2024-01-01..2025-01-01, so with the source's
  defaults the date gate is false on every bar and the port trades nothing on
  that range. That is the source's behaviour, not a port defect; the defaults
  are not adjusted to make the window trade (rule 6: no re-tuning).
* `math.avg(pD, pJ, pK)` is a three-argument average; it feeds only `plot(KDJ)`
  and no condition, so it is computed for completeness and not used.
* `ta.highest` / `ta.lowest` return na until their window is full and na
  propagates, which is what `pine_ta` does; `RSV` is therefore na for the first
  `ilong - 1` bars. A zero high-low range would make `RSV` na (Pine's
  division-by-zero rule) and the port guards that explicitly.
* Contract-step quantity rounding and leverage/margin/funding are not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _bcwsma(source: pd.Series, length: int, m: float) -> pd.Series:
    """The source's own `bcwsma(s, l, m)` recursion, not `ta.rma`.

    `_bcwsma := (m * s + (l - m) * nz(_bcwsma[1])) / l`, with `_bcwsma`
    initialised to na and `nz(na)` = 0. An na observation in `s` makes the whole
    expression na again, so the state returns to na and the next valid
    observation restarts from `nz(na)` = 0 -- which is what makes the first
    valid value `m * s / l` instead of an SMA seed.
    """
    values = source.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    state = np.nan
    for i, s in enumerate(values):
        if not np.isfinite(s):
            out[i] = np.nan
            state = np.nan
            continue
        previous = 0.0 if not np.isfinite(state) else state
        state = (m * s + (length - m) * previous) / length
        out[i] = state
    return pd.Series(out, index=source.index, dtype=float)


class SMKdjGoldenCrossLongEntry_6abcdb(PinePortBase, IStrategy):
    source_id = "SM_6abcdb3a367a934a"
    source_file = "KDJ阳线突破买入策略KDJ-Golden-Cross-Long-Entry-Strategy.md"
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {
        # ilong = input(9, title='period'); isig = input(3, title='signal')
        "ilong": 9,
        "isig": 3,
        # profit_m / stop_m are read only by the commented-out strategy.exit.
        "profit_m": 1.20,
        "stop_m": 0.98,
        # The six date-range inputs, whose defaults bound the trading window to
        # [2023-01-01, 2024-01-01).
        "startDate": 1,
        "startMonth": 1,
        "startYear": 2023,
        "endDate": 1,
        "endMonth": 1,
        "endYear": 2024,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "bcwsma() is the source's own recursion, NOT pine_ta.pine_rma: it is "
        "seeded at nz(na)=0, so its first valid value is RSV/isig rather than "
        "the SMA seed ta.rma uses. Substituting the library function would "
        "shift every K/D value.",
        "The commented-out `// strategy.exit(\"S\", limit=c*profit_m, "
        "stop=c*stop_m)` is not restored; the live source has no exit level, so "
        "source_reproduce_stops is False and profit_m/stop_m stay unused.",
        "The md's claim that the strategy uses take-profit/stop-loss describes "
        "that commented-out line only; recorded, not implemented.",
        "The md's argument table renders Start Date/Month/End Date/Month as "
        "`true`; the source's input.int defvals are 1/1/2024/1 and are used.",
        "inDateRange gates both orders with default window "
        "[2023-01-01, 2024-01-01) in syminfo.timezone (UTC here). Reproduced "
        "literally, so on the verifier's default 2024 range the port trades "
        "nothing -- the defaults are not re-tuned to make the window trade.",
        "go_long = ta.crossunder(pD, pJ) keeps the source's argument order (it "
        "fires on the %D-below-%J bar, i.e. the %J golden cross the md "
        "describes).",
        "math.avg(pD, pJ, pK) feeds only plot(KDJ) and no condition; computed "
        "but not used.",
        "RSV is na where the high-low range is zero (Pine division by zero) and "
        "for the first ilong-1 bars (ta.highest/ta.lowest windows).",
        "strategy() declares only title/shorttitle and the source has no "
        "input() for the trading properties; fixed/1 contract, initial capital "
        "1000000, commission 0%, pyramiding 0 are Pine's defaults.",
        "Contract-step quantity rounding and leverage/margin/funding are not "
        "modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        # h = ta.highest(high, ilong); l = ta.lowest(low, ilong)
        highest = ta.pine_highest(high, int(params["ilong"]))
        lowest = ta.pine_lowest(low, int(params["ilong"]))

        # RSV = 100 * ((c - l) / (h - l)); Pine's division by zero yields na.
        span = highest - lowest
        rsv = 100.0 * (close - lowest) / span
        rsv = rsv.where(span != 0)

        # pK = bcwsma(RSV, isig, 1); pD = bcwsma(pK, isig, 1)
        # bcwsma(s, l, m) with l = isig and m = 1.
        p_k = _bcwsma(rsv, int(params["isig"]), 1.0)
        p_d = _bcwsma(p_k, int(params["isig"]), 1.0)
        # pJ = 3 * pK - 2 * pD
        p_j = 3.0 * p_k - 2.0 * p_d
        # KDJ = math.avg(pD, pJ, pK) -- display only.
        kdj = (p_d + p_j + p_k) / 3.0

        # go_long = ta.crossunder(pD, pJ)
        go_long = ta.pine_crossunder(p_d, p_j)

        # inDateRange = (time >= timestamp(syminfo.timezone, startYear,
        #                 startMonth, startDate, 0, 0))
        #               and (time < timestamp(syminfo.timezone, endYear,
        #                 endMonth, endDate, 0, 0))
        index = dataframe.index
        if not isinstance(index, pd.DatetimeIndex):
            index = pd.DatetimeIndex(dataframe["date"])
        times = pd.DatetimeIndex(index)
        if times.tz is None:
            times = times.tz_localize("UTC")
        window_start = pd.Timestamp(
            year=int(params["startYear"]), month=int(params["startMonth"]),
            day=int(params["startDate"]), tz="UTC",
        )
        window_end = pd.Timestamp(
            year=int(params["endYear"]), month=int(params["endMonth"]),
            day=int(params["endDate"]), tz="UTC",
        )
        in_date_range = (times >= window_start) & (times < window_end)

        dataframe["pine_pk"] = p_k
        dataframe["pine_pd"] = p_d
        dataframe["pine_pj"] = p_j
        dataframe["pine_kdj"] = kdj
        dataframe["pine_go_long"] = go_long.fillna(False)
        dataframe["pine_in_date_range"] = np.asarray(in_date_range, dtype=bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "p_j": dataframe["pine_pj"].to_numpy(dtype=float),
            "go_long": dataframe["pine_go_long"].to_numpy(dtype=bool),
            "in_date_range": dataframe["pine_in_date_range"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (inDateRange and go_long)
        #     strategy.entry("S", strategy.long, comment="C")
        if ctx["in_date_range"][i] and ctx["go_long"][i]:
            broker.entry("S", "long")
        # if (inDateRange and pJ > 100)
        #     strategy.close("S", comment="TP")
        if ctx["in_date_range"][i] and ctx["p_j"][i] > 100.0:
            broker.close("S")
