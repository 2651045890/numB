"""Port of sources/SM_d01496d51f1fdcf2.pine
(batch_001/EMA追踪趋势交易策略EMA-Trend-Following-Trading-Strategy.md).

Pine v5, on the `/*backtest` header's 10m period. A 12/26 EMA cross pair with
one entry and one market exit:

    fastEMA = ta.ema(close, 12) ; slowEMA = ta.ema(close, 26)
    longCondition = ta.crossover(fastEMA, slowEMA)
    if longCondition and inTradeWindow
        strategy.entry("buy", strategy.long)
    if ta.crossunder(ta.ema(close, 12), ta.ema(close, 26)) and inTradeWindow
        strategy.close("buy")
    if not inTradeWindow and inTradeWindow[1]
        strategy.cancel_all()
        strategy.close_all(comment="Date Range Exit")

`strategy()` declares `initial_capital = 1`, `commission_type =
strategy.commission.percent` (with no `commission_value`, hence Pine's 0%
default) and `currency = currency.BTC`. `default_qty_type` is not declared, so
it is Pine's `strategy.fixed` with `default_qty_value = 1` -- one contract per
entry. `pyramiding` is not declared, so 0.

Two things the SOURCE does that the prose md does not:

* `can_short` is False. The md's "Strategy Logic" item 4 and item 5 describe
  short entries and a death-cross exit, but the source has no short entry at
  all -- the second branch closes the long. There is nothing to port as a short.
* The date filter is inert. `useDateFilter`, `backtestStartDate` and
  `backtestEndDate` are declared inputs but never compared against `time`
  anywhere; the gate the two order branches actually test is
  `inTradeWindow`, which is assigned the literal `true` on its own line. So the
  third block (`not inTradeWindow and inTradeWindow[1]`) can never be entered,
  `strategy.cancel_all` / `strategy.close_all` are dead code, and the backtest
  window the source advertises is not applied by the strategy. Reproduced as
  written, not as advertised.

FIDELITY:

* `source_initial_capital = 1.0` is the source's literal `initial_capital = 1`,
  but the source also declares `currency = currency.BTC`: its account is one
  BITCOIN, not one USDT. Pine's equity, its `default_qty_value = 1` contract and
  its 0% commission are all denominated in that unit. A Freqtrade wallet cannot
  be denominated in BTC, so the port hands the framework the number 1 and the
  framework reads it as 1 USDT. The number is faithful; its unit is not, and
  that gap is a property of the framework boundary (PINE_SEMANTICS.md 2.4, 2.6)
  rather than something the port can close. See BLOCKERS in the docstring tail.
* `inTradeWindow` is modelled as the constant `True` it is assigned, and the
  `not inTradeWindow and inTradeWindow[1]` branch is therefore emitted as a
  guarded block that can never fire, so the two dead calls stay visible in the
  order script instead of being silently dropped.
* `ta.crossunder(ta.ema(close, 12), ta.ema(close, 26))` recomputes the two EMAs
  that `fastEMA` / `slowEMA` already hold. Pine evaluates them as one series
  each, and so does this port: the same two `pine_ema` columns feed both the
  crossover and the crossunder. No second, separately seeded EMA is created.
* TradingView does not publish `ta.ema`'s seeding rule; `pine_ta.pine_ema` seeds
  with the first non-na observation (PINE_SEMANTICS.md 3.1). Both crosses are
  computed from those shared series with `pine_crossover` / `pine_crossunder`,
  whose na handling is Pine's (`a > b and a[1] <= b[1]`, na compares false).
* The source has no stop, limit, trail or `strategy.exit` call at all, so
  `source_reproduce_stops` is False and the only exit is the market
  `strategy.close("buy")`.
* `plot()` calls are display-only and are not reproduced.
* `input(timestamp("1 Jan 2021"))` / `input(timestamp("1 Jan 2022"))` yield
  epoch milliseconds in Pine; they are recorded in `source_defaults` as ISO-8601
  strings because they are never read by the strategy's logic and Pine's
  millisecond integers would carry no more meaning here. Recorded rather than
  resolved.
* PINE_SEMANTICS.md 2.8 (`input.time` does not trim the frame) applies and is
  moot: these inputs do not trim anything in the source either.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaTrendFollowing_d01496(PinePortBase, IStrategy):
    source_id = "SM_d01496d51f1fdcf2"
    source_file = "EMA追踪趋势交易策略EMA-Trend-Following-Trading-Strategy.md"
    timeframe = "10m"
    # The source has NO short entry: the md describes one, the code does not.
    can_short = False
    source_defaults: dict = {
        "useDateFilter": True,
        "backtestStartDate": "2021-01-01T00:00:00",
        "backtestEndDate": "2022-01-01T00:00:00",
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "can_short is False: the source declares no short entry. The md's "
        "'dead cross -> short entry' item is NOT implemented by the code, and "
        "the code is authoritative.",
        "The date filter is inert: useDateFilter / backtestStartDate / "
        "backtestEndDate are declared but never compared, and the gate the "
        "order branches test is `inTradeWindow = true`, a literal. The "
        "`not inTradeWindow and inTradeWindow[1]` branch is dead code; it is "
        "kept as a never-entered guarded block rather than dropped.",
        "source_initial_capital = 1.0 is the source's literal "
        "`initial_capital = 1`, but the source also declares "
        "`currency = currency.BTC`, so its account unit is one BITCOIN. A "
        "Freqtrade wallet is USDT-denominated, so the number is faithful and "
        "its unit is not; the framework reads the 1 as 1 USDT.",
        "`strategy()` declares commission_type = percent without a "
        "commission_value, so Pine's 0% default stands.",
        "default_qty_type is undeclared -> Pine's strategy.fixed with "
        "default_qty_value = 1, one contract per entry; pyramiding undeclared "
        "-> 0.",
        "The crossunder recomputes ta.ema(close,12) / ta.ema(close,26); both "
        "calls share the same columns as fastEMA/slowEMA, so exactly one EMA "
        "series pair exists, as in Pine.",
        "ta.ema seeding is TradingView-internal and unpublished; pine_ta "
        "seeds with the first non-na observation (PINE_SEMANTICS.md 3.1).",
        "No stop/limit/trail/strategy.exit exists, so source_reproduce_stops "
        "is False and the market strategy.close('buy') is the only exit.",
        "timestamp() inputs are recorded as ISO-8601 strings; they are never "
        "read by the logic, so no behaviour depends on the representation.",
        "plot() is display-only and is not reproduced.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # fastEMA = ta.ema(close,12), slowEMA = ta.ema(close,26)
        fast_ema = ta.pine_ema(close, 12)
        slow_ema = ta.pine_ema(close, 26)
        dataframe["pine_fast_ema"] = fast_ema
        dataframe["pine_slow_ema"] = slow_ema
        # longCondition = ta.crossover(fastEMA, slowEMA)
        dataframe["pine_long_condition"] = ta.pine_crossover(fast_ema, slow_ema)
        # ta.crossunder(ta.ema(close, 12), ta.ema(close, 26)) -- same EMAs
        dataframe["pine_close_condition"] = ta.pine_crossunder(fast_ema, slow_ema)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "close_condition": dataframe["pine_close_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # inTradeWindow is assigned the literal `true` and never reassigned;
        # the date inputs above it are never read.
        in_trade_window = True
        # if (longCondition) and inTradeWindow
        #     strategy.entry("buy", strategy.long)
        if ctx["long_condition"][i] and in_trade_window:
            broker.entry("buy", "long")
        # if ta.crossunder(ta.ema(close, 12), ta.ema(close, 26)) and inTradeWindow
        #     strategy.close("buy")
        if ctx["close_condition"][i] and in_trade_window:
            broker.close("buy")
        # if not inTradeWindow and inTradeWindow[1]
        #     strategy.cancel_all()
        #     strategy.close_all(comment="Date Range Exit")
        # `inTradeWindow` is a constant true, so this branch is unreachable;
        # it is kept (and evaluated) to mirror the source's call order.
        if (not in_trade_window) and in_trade_window:
            broker.cancel_all()
            broker.close_all()
