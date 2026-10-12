"""Port of sources/SM_e908bd64214c26ac.pine (batch_001/HalfTrend多空趋势追踪止损限价买入策略-HalfTrend-Bullish-and-Bearish-Trend-Following-Stop-Limit-Buy-Strategy.md).

Pine v5 long-only state machine. Two literals drive it -- `length = 1` (which
the source never reads) and `amplitude = 2.0` -- plus two `var` series that
carry across bars (`dir`, `trend`). One local pair (`ph`, `pl`) is re-declared
`na` on every bar, so the two updates that would read them (`if high > ph`,
`if low < pl`) compare against na and write nothing back:

    float ph = na                  // not var: na at the start of EVERY bar
    float pl = na
    var float dir = na
    var float trend = na

    if na(trend)
        trend := close
        ph := high
        pl := low
        dir := na
    else
        if high > ph               // ph is na here -> always false, no-op
            ph := high
        if low < pl                // pl is na here -> always false, no-op
            pl := low
        if close > trend and na(dir)
            dir := 1
            trend := close
            ph := high
            pl := low
        if close < trend and na(dir)
            dir := -1
            trend := close
            ph := high
            pl := low
        if dir == 1 and close < trend - amplitude
            dir := -1
            trend := close
            ph := high
            pl := low
        if dir == -1 and close > trend + amplitude
            dir := 1
            trend := close
            ph := high
            pl := low

    buySignal = dir == 1 and ta.valuewhen(dir == -1, trend, 0)

    if (buySignal)
        stopPrice = ta.valuewhen(dir == -1, trend, 0)
        strategy.entry("HalfTrend Buy", strategy.long, stop=stopPrice, comment="HalfTrend Buy")

`ph` / `pl` are write-only: they are re-initialised to na at the top of every
bar, so the only two reads of them happen while they are na and never take
effect. They are modelled as the no-ops they are (see FIDELITY).

`strategy()` declares only `title` and `overlay`, so Pine's documented defaults
apply: `default_qty_type = fixed`, `default_qty_value = 1`, `commission_value
= 0`, `pyramiding = 0`, initial capital 1000000 and `process_orders_on_close
= false`. The `/*backtest` header declares `period: 1d` on Futures_Binance
BTC_USDT, so `timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's
own intrabar granularity, not the strategy's period. There is no input() at
all in the source, hence an empty `source_defaults`.

FIDELITY:

* `ph` and `pl` are modelled as absent, which is what they are: each is
  declared without `var`, so it is na at the top of every bar, and the only two
  statements that read them (`if high > ph`, `if low < pl`) sit in the `else`
  branch where both are still na. Their comparisons are false, and every other
  assignment to them is never read. The state machine above therefore depends
  only on `dir` and `trend` -- reproducing the two no-op comparisons would add
  nothing but noise.
* `length = 1` is declared and never used by the source. It is not given a
  meaning here; there is no HalfTrend lookback in this source's arithmetic.
* `amplitude = 2.0` is a source literal, not an input, so it stays a literal.
* `stopPrice` is taken from the same `ta.valuewhen(dir == -1, trend, 0)` series
  the top-level `buySignal` line already computes, i.e. the `trend` value of
  the most recent bar on which `dir` was -1, carried forward -- which is what
  the strategy description says the order waits for ("record the HalfTrend
  value when the trend turns bearish ... place a stop-limit buy order at that
  position"). It is na until the first bearish bar, so the first bullish
  signal carries no entry (see the next note).
* MODELLED CHOICE, unresolved: Pine executes a `ta.*` call inside an `if`
  block only on the bars the block runs, so a compiler that treats the
  `stopPrice` call as its own series would have it accumulate history only on
  `buySignal` bars -- where `dir == 1` -- and therefore return na on every one
  of them, turning every entry into a market order. The port does NOT adopt
  that reading: it uses the value the identical top-level expression produces,
  which is the reading the source's own `buySignal` line and the strategy
  description both describe, and the one every other port in this repository
  uses for `ta.valuewhen`. The two readings differ only in the order type of
  the entry (resting stop vs market), never in the signal bar. Recorded, not
  resolved -- the original platform's trade list would settle it.
* The entry is a RESTING STOP order (`stop=stopPrice`), which the framework
  cannot express: PINE_SEMANTICS §二-11. The signal projection emits
  `enter_long` on the bar the order was placed, so the framework buys at the
  next open while the engine fills at `max(stop, open)` of a later bar -- the
  two coincide whenever the next bar opens above the stop. This is a framework
  boundary, not a port defect, and it is the reason this port cannot be
  expected to compare as `match`.
* The source has no exit call and no stop-loss of its own, so
  `source_reproduce_stops` is False and a long opened near the end of the
  window stays open. With `pyramiding = 0`, a further `strategy.entry` while
  the position is open is refused at order creation (Pine's own rule).
* `dir == 1` / `dir == -1` are exact float comparisons against the integers the
  source assigns; `dir` only ever holds na, 1 or -1, so no tolerance is
  involved on either side.
* `plot(...)` is display-only and is not reproduced.
* The md calls the order a "stop-limit" buy and speaks of "limit order"
  advantages, but the source passes only `stop=`; no `limit=` appears. The
  source wins: the port places a stop order with no limit leg. Recorded, not
  "corrected".
* Contract-step rounding, leverage, margin, liquidation and funding are not
  modelled (PINE_SEMANTICS §1.6, §二-4).
"""
import numpy as np

from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


class SMHalftrendStopLimit_e908bd(PinePortBase, IStrategy):
    source_id = "SM_e908bd64214c26ac"
    source_file = (
        "HalfTrend多空趋势追踪止损限价买入策略-HalfTrend-Bullish-and-Bearish-"
        "Trend-Following-Stop-Limit-Buy-Strategy.md"
    )
    timeframe = "1d"
    can_short = False
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "ph / pl are declared without var, so they are na at the top of every "
        "bar and both of their readers (`if high > ph`, `if low < pl`) compare "
        "against na and never write. They are modelled as absent; the state "
        "machine depends only on `dir` and `trend`.",
        "`length = 1` is declared by the source and never read; no HalfTrend "
        "lookback exists in this source's arithmetic.",
        "`amplitude = 2.0` is a source literal, not an input, and stays one.",
        "stopPrice reuses the same `ta.valuewhen(dir == -1, trend, 0)` series "
        "the top-level buySignal line computes: the most recent bearish trend "
        "value, carried forward. It is na until the first bearish bar.",
        "MODELLED CHOICE, unresolved: a compiler that treats the conditional "
        "`ta.valuewhen` call as its own series would build its history only on "
        "buySignal bars (where dir == 1) and so return na every time, making "
        "every entry a market order. Not adopted -- the source's own top-level "
        "expression and the strategy description both describe the carried "
        "forward value. Recorded, not resolved.",
        "The entry is a resting stop order, which the framework cannot express "
        "(PINE_SEMANTICS §二-11); the projected signal lands on the placement "
        "bar and the framework buys at the next open, while the engine fills "
        "at max(stop, open) of a later bar. Framework boundary, not a port "
        "defect.",
        "No exit call and no stop-loss in the source, so source_reproduce_stops "
        "is False and a long open at the window's end stays open. With "
        "pyramiding=0 a further entry while the position is open is refused at "
        "creation, per Pine's own rule.",
        "The md calls the order a stop-limit buy and praises 'limit order' "
        "fills, but the source passes only `stop=`. The source wins: no limit "
        "leg is placed. Recorded, not corrected.",
        "strategy() declares only title/overlay, so Pine's defaults apply: "
        "qty_type fixed, qty_value 1, commission 0, pyramiding 0, initial "
        "capital 1000000, process_orders_on_close false.",
        "The header's `basePeriod: 1h` asks the platform for 1h intrabar fills; "
        "the engine resolves every order against the 1d bar alone.",
        "Contract-step rounding, leverage, margin, liquidation and funding are "
        "not modelled (PINE_SEMANTICS §1.6, §二-4).",
    ]

    def pine_indicators(self, dataframe, params):
        # amplitude = 2.0 is a literal in the source.
        amplitude = 2.0
        close = dataframe["close"].to_numpy(dtype=float)
        n = len(close)

        dir_state = np.nan
        trend_state = np.nan
        valuewhen_state = np.nan
        dir_out = np.full(n, np.nan)
        trend_out = np.full(n, np.nan)
        stop_out = np.full(n, np.nan)

        for i in range(n):
            current = close[i]
            if np.isnan(trend_state):
                # if na(trend): trend := close ; ph := high ; pl := low ; dir := na
                trend_state = current
                dir_state = np.nan
            else:
                # `if high > ph` / `if low < pl` are no-ops: ph and pl are na
                # here (neither is declared with `var`), so they are omitted.
                if np.isnan(dir_state) and current > trend_state:
                    dir_state = 1.0
                    trend_state = current
                if np.isnan(dir_state) and current < trend_state:
                    dir_state = -1.0
                    trend_state = current
                if dir_state == 1.0 and current < trend_state - amplitude:
                    dir_state = -1.0
                    trend_state = current
                if dir_state == -1.0 and current > trend_state + amplitude:
                    dir_state = 1.0
                    trend_state = current
            # ta.valuewhen(dir == -1, trend, 0): the trend of the most recent
            # bar whose dir is -1, carried forward.
            if dir_state == -1.0:
                valuewhen_state = trend_state
            dir_out[i] = dir_state
            trend_out[i] = trend_state
            stop_out[i] = valuewhen_state

        dataframe["pine_dir"] = dir_out
        dataframe["pine_trend"] = trend_out
        dataframe["pine_stop_price"] = stop_out
        # buySignal = dir == 1 and ta.valuewhen(dir == -1, trend, 0)
        dataframe["pine_buy_signal"] = (
            (dataframe["pine_dir"] == 1.0) & dataframe["pine_stop_price"].notna()
        ).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "stop_price": dataframe["pine_stop_price"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (buySignal)
        #     stopPrice = ta.valuewhen(dir == -1, trend, 0)
        #     strategy.entry("HalfTrend Buy", strategy.long, stop=stopPrice, ...)
        if ctx["buy_signal"][i]:
            broker.entry(
                "HalfTrend Buy",
                "long",
                stop=float(ctx["stop_price"][i]),
            )
