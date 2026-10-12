"""Port of sources/SM_ef50066d12cc2bc6.pine (batch_001/50资金50仓位动态平衡量化策略Dynamic-Balancing-Strategy-with-50-Funds-and-50-Positions.md).

Pine v4. A fixed-income style cash/position rebalancer: buy half the capital
once, then top up with 2.5% of the remaining funds (or trim 2.5% of the
unrealized P&L) on every new calendar day, and liquidate everything once the
sell date arrives:

    capital = 1000000
    start_date = timestamp(2020, 11, 4)
    next_date  = timestamp(2020, 11, 5)
    sell_date  = timestamp(2023, 10, 24)

    in_trade_period   = true
    realized_profit_loss = strategy.netprofit
    open_profit_loss  = strategy.position_size * open
    remaining_funds   = capital + realized_profit_loss
                        - (strategy.position_size * strategy.position_avg_price)
    first_buy  = time >= start_date and time <= next_date
    buy_condition = in_trade_period and dayofmonth != dayofmonth[1]
    sell_all   = time >= sell_date

    if first_buy
        strategy.order("First", strategy.long, qty = capital / 2 / open)
    if buy_condition
        strategy.order("Buy",  strategy.long,  when = add_logic,
                       qty = remaining_funds * 0.025 / open)
    if buy_condition
        strategy.order("Sell", strategy.short, when = sub_logic,
                       qty = open_profit_loss * 0.025 / open)
    strategy.order("Sell_all", strategy.short, when = sell_all,
                   qty = strategy.position_size)

`strategy()` declares `initial_capital = 1000000` explicitly and nothing else,
so the remaining properties are Pine's documented defaults: `strategy.fixed` /
1 contract, commission 0%, `pyramiding 0`, `process_orders_on_close=false`.
Every order carries an explicit `qty`, so the default qty value is never used;
`initial_capital` is echoed by the port because the framework's wallet has to
start where the source's does.

The `/*backtest` header declares `period: 1m` on Futures_Binance BTC_USDT, so
`timeframe` is "1m"; its `basePeriod: 1m` agrees. There is no local 1m futures
history in this repository, so the chain verifier reports this port as
`skipped_no_local_data` rather than comparing it.

BOTH SIDES OF THIS SOURCE PLACE SHORT ORDERS (`"Sell"` and `"Sell_all"`), so
`can_short` is True. Neither is an exit: `strategy.order` with an opposing
direction is what Pine uses here to reverse or to go flat.

FIDELITY:

* THE SOURCE NEVER OPENS A POSITION IN THE WINDOW IT DECLARES, and the port
  reproduces that. Two independent reasons, both from the code:
  1. `first_buy` is `time` inside 2020-11-04..2020-11-05, while the header
     declares the backtest window as 2023-12-17..2023-12-18. The one order that
     opens the initial 50% can never fire.
  2. `remaining_funds` subtracts `strategy.position_size *
     strategy.position_avg_price`. Pine documents `position_avg_price` as na
     while the position is flat, and `0 * na` is na, so `remaining_funds` is na
     on every flat bar -- `add_logic` (`remaining_funds > open_profit_loss *
     1.05`) is na and falsy, and the daily `"Buy"` never fires either.
     `sell_all` does fire on every bar of that window (`time` >= 2023-10-24 is
     already true), but it passes `qty = strategy.position_size`, which is 0
     while flat, and the engine drops a zero-quantity entry rather than
     booking it.
  The alternative reading -- a platform that returns 0 rather than na for
  `position_avg_price` while flat -- would make `remaining_funds` 1000000 on
  the first flat bar and fire the daily `"Buy"` from the first new day onward,
  i.e. a completely different (and trading) strategy. Which one the FMZ
  backtester does is not knowable offline; the port follows the documented
  Pine semantics, and this is the single unresolved point that decides whether
  the source trades at all. Recorded, not guessed.
* `strategy.netprofit` is mapped to the engine's `realized_profit` (the running
  total of closed-trade P&L net of commission), which is the same quantity
  Pine's `strategy.netprofit` reports.
* `dayofmonth != dayofmonth[1]` is na on the first bar of the frame (there is
  no `[1]`), and Pine treats a na boolean as false, so bar 0 is never a "new
  day". The port masks that bar explicitly; a plain pandas `!=` would have
  returned True against the NaN and fired on bar 0.
* `time` is the bar's opening time in milliseconds, and `timestamp(y, m, d)`
  without a timezone argument resolves in the exchange's timezone. The local
  frames are UTC, so the port compares UTC milliseconds; a non-UTC venue would
  need the offset applied here.
* `end_date = timestamp(2023, 10, 25)` is assigned by the source and never
  read. It is recomputed and kept as a column so the formula stays on the
  record, and is not consumed by the script.
* `in_trade_period = true` is a literal, so `buy_condition` reduces to the
  new-day test; the port keeps the literal in the expression rather than
  simplifying it away.
* The md's prose ("initialise 1 million, split 50/50", "add 2.5% of remaining
  funds each open", "close all at the end") matches the code. The md's claim
  that the position/cash split is *maintained* is looser than the code, which
  only ever adds or trims around the ratio.
* `bgcolor`, `plot` and `shorttitle` are display-only and not reproduced.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the venue's rounding can differ from the engine's float quantity,
  which the chain verifier measures separately.
"""
from datetime import datetime, timezone

import pandas as pd

from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase

# The source's own literals, kept as module constants so the arithmetic below
# reads like the script it came from.
CAPITAL = 1_000_000.0
START_DATE_MS = datetime(2020, 11, 4, tzinfo=timezone.utc).timestamp() * 1000.0
NEXT_DATE_MS = datetime(2020, 11, 5, tzinfo=timezone.utc).timestamp() * 1000.0
END_DATE_MS = datetime(2023, 10, 25, tzinfo=timezone.utc).timestamp() * 1000.0
SELL_DATE_MS = datetime(2023, 10, 24, tzinfo=timezone.utc).timestamp() * 1000.0


class SMDynamicBalancing50_ef5006(PinePortBase, IStrategy):
    source_id = "SM_ef50066d12cc2bc6"
    source_file = (
        "50资金50仓位动态平衡量化策略"
        "Dynamic-Balancing-Strategy-with-50-Funds-and-50-Positions.md"
    )
    timeframe = "1m"
    can_short = True
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "UNRESOLVED, DECIDES WHETHER THE SOURCE TRADES AT ALL: "
        "`remaining_funds` subtracts `strategy.position_size * "
        "strategy.position_avg_price`, and Pine documents position_avg_price as "
        "na while flat, so remaining_funds is na on every flat bar and the "
        "daily \"Buy\" never becomes true. A platform returning 0 there would "
        "instead fire it from the first new day. Documented Pine semantics are "
        "followed; the port places no orders in the declared window.",
        "`first_buy` tests `time` against 2020-11-04..2020-11-05 while the "
        "/*backtest header declares 2023-12-17..2023-12-18, so the one call "
        "that opens the initial 50% can never fire in the declared window.",
        "`strategy.netprofit` is mapped to the engine's realized_profit "
        "(closed-trade P&L net of commission), the same quantity.",
        "`dayofmonth != dayofmonth[1]` is na on bar 0 (no previous bar) and a "
        "na boolean is false in Pine; the port masks bar 0 explicitly instead "
        "of letting pandas compare against NaN and return True.",
        "`time` / `timestamp()` are compared as UTC milliseconds; the local "
        "frames are UTC, a non-UTC venue would need its offset here.",
        "`end_date` is assigned by the source and never read; it is recomputed "
        "and kept as a column, and the script does not consume it.",
        "`in_trade_period = true` is a literal and is kept in the expression "
        "rather than simplified out of `buy_condition`.",
        "Both \"Sell\" and \"Sell_all\" are SHORT strategy.order calls, so "
        "can_short is True; neither is an exit.",
        "No stop, limit or trailing exit exists, so source_reproduce_stops is "
        "False.",
        "bgcolor / plot / shorttitle are display-only and not reproduced.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        index = pd.DatetimeIndex(dataframe.index)
        frame_index = dataframe.index

        # dayofmonth: Pine's day-of-month of the bar's own time.
        day_of_month = pd.Series(index.day, index=frame_index, dtype=float)
        previous_day = day_of_month.shift(1)
        # `dayofmonth != dayofmonth[1]` is na on the first bar -> false.
        dataframe["pine_dayofmonth"] = day_of_month
        dataframe["pine_new_day"] = (day_of_month != previous_day) & previous_day.notna()

        # `time`: the bar's opening time in milliseconds.
        bar_time_ms = pd.Series(
            index.astype("int64") // 10**6, index=frame_index, dtype=float
        )
        dataframe["pine_bar_time_ms"] = bar_time_ms

        # first_buy = time >= start_date and time <= next_date
        dataframe["pine_first_buy"] = (
            (bar_time_ms >= START_DATE_MS) & (bar_time_ms <= NEXT_DATE_MS)
        )
        # sell_all = time >= sell_date
        dataframe["pine_sell_all"] = bar_time_ms >= SELL_DATE_MS
        # end_date is computed by the source and never read; kept for the record.
        dataframe["pine_end_date_ms"] = END_DATE_MS
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "open": dataframe["open"].to_numpy(),
            "new_day": dataframe["pine_new_day"].to_numpy(),
            "first_buy": dataframe["pine_first_buy"].to_numpy(),
            "sell_all": dataframe["pine_sell_all"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        open_ = float(ctx["open"][i])

        # capital = 1000000
        capital = CAPITAL
        # realized_profit_loss = strategy.netprofit
        realized_profit_loss = float(broker.realized_profit)
        # open_profit_loss = strategy.position_size * open
        open_profit_loss = broker.position_size * open_
        # remaining_funds = capital + realized_profit_loss
        #                   - (strategy.position_size * strategy.position_avg_price)
        # `position_avg_price` is na while flat (Pine's rule, and the engine's),
        # so this is na on every flat bar and both logic tests below are falsy.
        remaining_funds = (
            capital + realized_profit_loss
            - (broker.position_size * broker.position_avg_price)
        )

        # add_logic = remaining_funds > open_profit_loss * 1.05
        add_logic = remaining_funds > open_profit_loss * 1.05
        # sub_logic = open_profit_loss > remaining_funds * 1.05
        sub_logic = open_profit_loss > remaining_funds * 1.05

        # if first_buy
        #     strategy.order("First", strategy.long, qty = capital/2/open)
        if ctx["first_buy"][i]:
            broker.order("First", "long", qty=capital / 2.0 / open_)

        # buy_condition = in_trade_period and dayofmonth != dayofmonth[1]
        # (in_trade_period is the literal `true`)
        if ctx["new_day"][i]:
            # strategy.order("Buy", strategy.long, when = add_logic,
            #                qty = remaining_funds * 0.025 / open)
            broker.order(
                "Buy", "long", when=bool(add_logic),
                qty=remaining_funds * 0.025 / open_,
            )
            # strategy.order("Sell", strategy.short, when = sub_logic,
            #                qty = open_profit_loss * 0.025 / open)
            broker.order(
                "Sell", "short", when=bool(sub_logic),
                qty=open_profit_loss * 0.025 / open_,
            )

        # strategy.order("Sell_all", strategy.short, when = sell_all,
        #                qty = strategy.position_size)
        broker.order(
            "Sell_all", "short", when=bool(ctx["sell_all"][i]),
            qty=broker.position_size,
        )
