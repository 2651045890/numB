"""Port of sources/SM_6db99d2409ac19a2.pine (50 EMA Crossover With Monthly DCA).

Pine v5. A long-only trend/DCA hybrid on the chart's own period:

    emaValue     = ta.ema(close, 50)
    longCondition  = close > emaValue
    exitCondition  = close < emaValue

    if longCondition
        if strategy.opentrades == 0
            strategy.order("Open Order", strategy.long, qty = (strategy.equity + cash_reserve) / close)
            cash_reserve := 0
        if time_since_last_investment >= month_seconds
            strategy.order("DCA Buy", strategy.long, qty = dca_amount / close)
            last_investment_time := time
    if time_since_last_investment >= month_seconds
        last_investment_time := time
    if exitCondition
        strategy.close_all()

`time_since_last_investment` is `na(last_investment_time) ? 30 days : (time -
last_investment_time) / 1000`, so it is na-driven on the first bar (which then
counts as a monthly tick) and thereafter purely a function of the bar
timestamps: the tick fires on the first bar at least 30 days after the previous
tick. Nothing about it depends on fills, so the whole cadence is reproduced as a
precomputed per-bar series rather than as run-time state.

`strategy()` declares initial_capital = 100000, default_qty_type =
strategy.cash and process_orders_on_close = true, plus slippage = 1.
default_qty_value is not declared, so Pine's documented default of 1 applies --
but it is never used, because BOTH orders pass an explicit `qty=`. pyramiding is
not declared, so Pine's documented default of 0 applies, and 0% commission is
Pine's documented default (no commission_type/value is given).

FIDELITY -- translation choices and source/original mismatches:

1. `process_orders_on_close = true` COULD NOT BE REPRODUCED. Pine fills this
   script's market orders at the CLOSE of the bar that placed them; pine_engine
   models only Pine's default timing, filling a market order at the NEXT bar's
   OPEN (PINE_SEMANTICS.md section 1). The fill is NOT silently moved to the next
   bar on the port's initiative -- the port expresses the `strategy.*` calls and
   the engine applies its own timing -- but the consequence must be stated: the
   quantity is still computed off `strategy.equity` at the signal bar's close
   (which the engine does reproduce, since it sizes off the equity of the bar
   the order was placed on), while the FILL PRICE is the next bar's open instead
   of the signal bar's close. On daily bars that is the overnight gap, and it
   moves both the entry price and (through `dca_amount / close`, which is fixed
   in coins rather than in money) the size of every DCA order.
2. `slippage = 1` (one tick of slippage on market orders) is not modelled by
   pine_engine, which fills at the bar's open/level with no slippage.
3. The PROSE says the strategy "adds a fixed amount to a cash reserve each
   month" while the price is below the EMA. The CODE never adds anything:
   `cash_reserve` is initialised to 0 and the only assignment to it is
   `cash_reserve := 0` in the re-investment branch. The commented-out plot on
   the last lines is the only other mention. So `strategy.equity + cash_reserve`
   is identically `strategy.equity`, and the daily-cost-averaging reserve is
   never funded. The code wins: the port reproduces a full-equity entry, and
   cash_reserve is not invented into existence.
4. `time_since_last_investment >= month_seconds` is evaluated with `time` in
   milliseconds and a divisor of 1000, so the threshold is 30 days exactly. With
   daily bars every difference is a whole number of seconds and the integer/float
   question is moot; the port compares float seconds.
5. The first bar of the run counts as a tick (`na(last_investment_time)` branch),
   so the monthly cadence is anchored to the first bar of the DATA, not to a
   calendar month. The source's FMZ header starts 2024-10-23; a backtest window
   that starts elsewhere shifts every subsequent DCA date. Not corrected.
6. `strategy.opentrades == 0` is read at the signal bar's close, i.e. after the
   fills of that bar's open. `broker.open_trades` is the engine's equivalent
   (the number of open entry lots).
7. The source's `strategy.order` calls pass an explicit qty, so
   `default_qty_type = strategy.cash` is never exercised; with pyramiding = 0 the
   monthly "DCA Buy" is refused whenever a position is already open (`_can_add`
   in pine_engine), which is Pine's own pyramiding rule. Nothing was added to
   make that happen.
8. `ta.ema` seeding: pine_ta.pine_ema seeds the recursion with the first non-na
   observation, which PINE_SEMANTICS.md records as an unresolved parity risk
   against TradingView's unpublished seeding. `close` has no na values here.
9. `var float total_invested` is declared and never read, and the `label` block
   at the end is display-only; neither has any order effect and neither is
   carried.
10. can_short is False: nothing in the source ever sells short.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

MONTH_SECONDS = 30 * 24 * 60 * 60  # month_seconds = 30 * 24 * 60 * 60


def monthly_ticks(index) -> np.ndarray:
    """`time_since_last_investment >= month_seconds`, bar by bar.

    Pine's state update (`last_investment_time := time`) happens at the END of
    every bar the tick fired on -- in both the DCA branch and the standalone
    block -- so the tick is a pure forward recursion over bar timestamps and can
    be materialised once. `time` is milliseconds, and the source divides the
    difference by 1000, so the comparison is in seconds.
    """
    # `time` in Pine is milliseconds since the epoch; the frame's timestamps are
    # UTC (the base class indexes by the candle's `date`), so a plain UTC
    # conversion is the same instant the source read. Spelled out rather than
    # taken from Index.view, whose unit is the index's own resolution.
    stamps = np.asarray(index, dtype="datetime64[ms]").astype("int64")
    previous = None
    ticks = np.zeros(len(stamps), dtype=bool)
    for position, stamp in enumerate(stamps):
        if previous is None:
            # na(last_investment_time) -> month_seconds -> the tick fires.
            elapsed = float(MONTH_SECONDS)
        else:
            elapsed = float(stamp - previous) / 1000.0
        if elapsed >= MONTH_SECONDS:
            ticks[position] = True
            previous = stamp
    return ticks


class SM50EmaDca_6db99d(PinePortBase, IStrategy):
    source_id = "SM_6db99d2409ac19a2"
    source_file = (
        "50周期指数移动平均线交叉结合月度定投的双重优化趋势跟踪策略-"
        "50-Period-EMA-Crossover-with-Monthly-Dollar-Cost-Averaging-"
        "Dual-Optimization-Trend-Following-Strategy.md"
    )
    timeframe = "1d"
    can_short = False
    source_defaults = {
        # input.int(100000, title="DCA Investment Amount ($)", minval=1)
        "dca_amount": 100000,
    }
    source_qty_type = "cash"
    # default_qty_value is not declared -> Pine's documented default. It is
    # never used: both orders pass an explicit qty=.
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100_000.0
    source_fidelity_notes = [
        "process_orders_on_close=true COULD NOT BE REPRODUCED. Pine fills these "
        "market orders at the CLOSE of the bar that placed them; pine_engine "
        "models only the default timing (next bar's OPEN), so the fill price is "
        "the following bar's open. The port does not move the fill itself -- it "
        "expresses the strategy.* calls and the engine applies its timing -- but "
        "the difference is real: the sizing equity is still the signal bar's "
        "close (which the engine does reproduce), while the fill price, and with "
        "it the coin quantity of every `dca_amount / close` order, is the gap "
        "bar's open.",
        "slippage=1 (one tick on market orders) is not modelled; pine_engine "
        "fills at the bar's open with no slippage.",
        "SOURCE PROSE vs CODE: the description says a fixed amount is added to a "
        "cash reserve every month WHILE THE PRICE IS BELOW the EMA, and that the "
        "reserve is then deployed when price breaks above. The code does neither: "
        "the monthly order sits inside `if longCondition` (price ABOVE the EMA) "
        "and BUYS into the market, and nothing ever adds to `cash_reserve` -- it is "
        "0 and the only assignment to it is `cash_reserve := 0`. So "
        "`strategy.equity + cash_reserve` is identically `strategy.equity` and the "
        "'Open Order' is a full-equity entry. The code wins: the reserve the prose "
        "describes is not invented into existence.",
        "The monthly cadence is anchored to the FIRST BAR OF THE DATA (bar 0 "
        "satisfies the `na(last_investment_time)` branch) rather than to a "
        "calendar month, and `month_seconds` is a flat 30 days. A different "
        "backtest start date shifts every later DCA date; nothing was re-anchored.",
        "Both orders pass an explicit qty=, so default_qty_type=strategy.cash "
        "and its default_qty_value=1 are never exercised. With pyramiding=0 (Pine's "
        "default, not declared) the monthly 'DCA Buy' is refused while a position "
        "is open, which is Pine's own rule and is modelled by pine_engine.",
        "ta.ema seeding follows pine_ta.pine_ema (first non-na observation seeds "
        "the recursion); TradingView's internal seeding is not publicly specified "
        "and remains a parity risk. `close` carries no na values here.",
        "`var float total_invested` is declared and never read; the label block "
        "at the end is display-only. Neither has an order effect and neither is "
        "carried into the port.",
        "can_short is False: the source never sells short.",
    ]

    def pine_indicators(self, dataframe, params):
        # emaValue = ta.ema(close, 50) -- the length is hard-coded; the
        # `ema_length` input is commented out in the source.
        dataframe["emaValue"] = ta.pine_ema(dataframe["close"], 50)

        # longCondition = close > emaValue / exitCondition = close < emaValue.
        # While the EMA is na both comparisons are false, as in Pine.
        dataframe["pine_long_condition"] = (dataframe["close"] > dataframe["emaValue"]).astype(bool)
        dataframe["pine_exit_condition"] = (dataframe["close"] < dataframe["emaValue"]).astype(bool)
        dataframe["pine_monthly_tick"] = monthly_ticks(dataframe.index)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "exit_condition": dataframe["pine_exit_condition"].to_numpy(),
            "monthly_tick": dataframe["pine_monthly_tick"].to_numpy(),
            # dca_amount is an input, so it must follow source_parameters();
            # broadcast per bar so pine_script reads it like any Pine series.
            "dca_amount": np.full(len(dataframe), float(params["dca_amount"])),
        }

    def pine_script(self, broker, i, ctx):
        close = ctx["close"][i]
        tick = bool(ctx["monthly_tick"][i])

        # var float cash_reserve = 0 -- the source never assigns anything else
        # to it, so the "reserve" is identically zero (see source_fidelity_notes).
        cash_reserve = 0.0

        # if longCondition
        if ctx["long_condition"][i]:
            #     if strategy.opentrades == 0
            #         strategy.order("Open Order", strategy.long,
            #                        qty = (strategy.equity + cash_reserve) / close)
            #         cash_reserve := 0
            if broker.open_trades == 0:
                broker.order("Open Order", "long",
                             qty=(broker.equity + cash_reserve) / close)

            #     if time_since_last_investment >= month_seconds
            #         strategy.order("DCA Buy", strategy.long, qty = dca_amount / close)
            #         last_investment_time := time
            if tick:
                broker.order("DCA Buy", "long",
                             qty=float(ctx["dca_amount"][i]) / close)

        # if time_since_last_investment >= month_seconds
        #     last_investment_time := time
        # This is the source's unconditional state update; it places no order and
        # is already encoded in `pine_monthly_tick` (which is computed from the
        # same forward recursion), so there is nothing to express here.

        # if exitCondition
        #     strategy.close_all()
        if ctx["exit_condition"][i]:
            broker.close_all()
