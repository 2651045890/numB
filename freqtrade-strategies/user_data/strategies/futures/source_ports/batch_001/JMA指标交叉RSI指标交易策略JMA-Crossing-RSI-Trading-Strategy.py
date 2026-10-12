"""Port of sources/SM_e6612c9e09655aea.pine (batch_001/JMA指标交叉RSI指标交易策略JMA-Crossing-RSI-Trading-Strategy.md).

Pine v4. A hand-written RSI(14) is fed through a hand-written JMA(7, 50, 2)
and the two series are crossed against each other:

    up   = rma(max(change(src), 0), 14)
    down = rma(-min(change(src), 0), 14)
    rsi  = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))

    phaseRatio = _phase < -100 ? 0.5 : _phase > 100 ? 2.5 : _phase / 100 + 1.5
    beta  = 0.45 * (_length - 1) / (0.45 * (_length - 1) + 2)
    alpha = pow(beta, _power)
    e0 := (1 - alpha) * rsi + alpha * nz(e0[1])
    e1 := (rsi - e0) * (1 - beta) + beta * nz(e1[1])
    e2 := (e0 + phaseRatio * e1 - nz(jma[1])) * pow(1 - alpha, 2) + pow(alpha, 2) * nz(e2[1])
    jma := e2 + nz(jma[1])

    goLong()  = crossover(rsi, jma)     killLong()  = crossunder(rsi, jma)
    goShort() = killLong()              killShort() = goLong()

    strategy.entry("Buy",  strategy.long,  when = goLong())
    strategy.close("Buy",  when = killLong() and close > long_price)
    strategy.entry("Sell", strategy.short, when = goShort() and close < short_price)
    strategy.close("Sell", when = killShort())
    strategy.exit("XLS", from_entry = "Buy",  stop = strategy.position_avg_price / 1.08)
    strategy.exit("XSS", from_entry = "Sell", stop = strategy.position_avg_price * 1.08)

`strategy()` declares `currency = currency.EUR`, `default_qty_type = strategy.cash`
and `default_qty_value = 5000`; every other property is Pine's documented default:
initial capital 1000000, commission 0%, pyramiding 0, process_orders_on_close
false. No `qty=` is passed anywhere, so the 5000-cash default sizes every entry.

FIDELITY -- what is preserved and what is a modelling choice:

* The RSI is the SOURCE's own expression, not `pine_ta.pine_rsi`, because the
  source writes the boundary tests itself (`down == 0 -> 100`, `up == 0 -> 0`).
  The two agree on the formula and on those boundaries, but the source's form is
  reproduced literally so the na propagation stays visible.
* The JMA is a stateful recursion over `rsi`, and `rsi` is na for the first
  `len` bars. Pine computes `nz(x[1])` (na -> 0) on the history terms while
  arithmetic on na stays na, so the recursion starts on the first bar whose rsi
  is available and every earlier bar is na. Reproduced bar-by-bar in the same
  way rather than being vectorised into a one-bar-off filter.
* Pine's `rsi` here is `close`-driven; `change(src)` is na on the first bar and
  na propagates through math.max/min and both rma's.
* `long_price` / `short_price` are declared `=` at global scope (`long_price =
  0.0`), NOT `var`, so Pine re-initialises them to 0.0 on every bar and the only
  assignment inside the `if` applies to that same bar. They are reproduced as
  per-bar expressions, which is what the source's scoping gives (PINE_SEMANTICS
  records the same shape on batch_008/多均线交叉辅助RSI...).
* CONSEQUENCE OF THE ABOVE, and the reason `can_short` is False: on the bar
  `goShort()` is true, `short_price := close` assigns the CURRENT bar's close,
  and the entry's `when` is `goShort() and close < short_price` -- i.e.
  `close < close`, which is never true. The "Sell" entry is therefore
  UNREACHABLE in the source as written, and no short position can ever be
  opened. The line is still reproduced verbatim (so the source's shape is on
  the record) but it can never fire. The `strategy.close("Sell", ...)` and
  `strategy.exit("XSS", ...)` legs are equally unreachable.
* The same scoping makes the long close's guard vacuous: `killLong()` and
  `goLong()` are mutually exclusive on one bar, so `long_price` is 0.0 whenever
  `killLong()` holds and `close > long_price` is always true. Reproduced as
  written rather than simplified away.
* `startTime = true` and `endTime = true` are literal variables in the source,
  NOT the `sYear`/`sMonth`/... `input()`s: those ten inputs are read by nothing.
  The `if (startTime and endTime)` gate is therefore always true and the port
  drops the dead branch but keeps every input in `source_defaults`.
* `strategy.exit("XLS", ...)` is called unconditionally, so when the account is
  flat `strategy.position_avg_price` is na and the stop is na. Pine's na means
  the parameter is unset and the exit does nothing, so the port carries the na
  through as a NaN level: the engine sees a leg that can never trigger and the
  level is never published (PINE_SEMANTICS 1.15 warns that a no-leg exit must
  not become a framework market exit). The call itself is still made on every
  bar, so the same-id replacement of the resting order keeps its Pine timing.
* `currency = currency.EUR` is the source's account currency, while the venue is
  Futures_Binance BTC_USDT. Cross-currency conversion is not modelled by
  pine_engine (it has no exchange-rate feed), so the port's figures are in the
  quote currency, USDT. The relative behaviour is unaffected; the currency
  translation itself is not reproduced.
* `highlightMovements`, `jmaColor`, `plot` and `hline` are display-only and
  place no order.
* The md PROSE describes the opposite crossing ("JMA crosses above RSI -> buy")
  and mentions a profit-ratio target; the code crosses `rsi` against `jma`
  (`crossover(rsi, jma)`) and has no take-profit at all, only the 8% stop. The
  code wins; recorded, not "corrected".
* The md's "Strategy Tester Start/End Time" section matches the dead inputs
  above, and its "内置止损机制... 可自定义盈利比例" overstates the code, which
  exposes only `useStop` for the stop and nothing for a profit target.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the last of those separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# `strategy.exit("XLS", from_entry = "Buy",  stop = strategy.position_avg_price / 1.08)`
# `strategy.exit("XSS", from_entry = "Sell", stop = strategy.position_avg_price * 1.08)`
STOP_DIVISOR = 1.08
STOP_MULTIPLIER = 1.08


def _jma(source: pd.Series, length: int, phase: int, power: int) -> pd.Series:
    """The source's own Jurik MA recursion, bar by bar.

    `nz(x[1])` is na -> 0 on the history terms, while any na in the current
    bar's arithmetic makes the whole expression na -- so the recursion begins
    on the first bar whose `source` (the RSI) is available and everything
    before it is na.
    """
    phase_ratio = 0.5 if phase < -100 else (2.5 if phase > 100 else phase / 100 + 1.5)
    beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2)
    alpha = beta**power
    values = source.to_numpy(dtype=float)
    n = len(values)
    e0 = np.full(n, np.nan)
    e1 = np.full(n, np.nan)
    e2 = np.full(n, np.nan)
    jma = np.full(n, np.nan)
    for i in range(n):
        current = values[i]
        if np.isnan(current):
            continue
        prev_e0 = 0.0 if i == 0 or np.isnan(e0[i - 1]) else e0[i - 1]
        prev_e1 = 0.0 if i == 0 or np.isnan(e1[i - 1]) else e1[i - 1]
        prev_e2 = 0.0 if i == 0 or np.isnan(e2[i - 1]) else e2[i - 1]
        prev_jma = 0.0 if i == 0 or np.isnan(jma[i - 1]) else jma[i - 1]
        e0[i] = (1 - alpha) * current + alpha * prev_e0
        e1[i] = (current - e0[i]) * (1 - beta) + beta * prev_e1
        e2[i] = (e0[i] + phase_ratio * e1[i] - prev_jma) * (1 - alpha) ** 2 + alpha**2 * prev_e2
        jma[i] = e2[i] + prev_jma
    return pd.Series(jma, index=source.index, dtype=float)


class SMJmaCrossingRsi_e6612c(PinePortBase, IStrategy):
    source_id = "SM_e6612c9e09655aea"
    source_file = "JMA指标交叉RSI指标交易策略JMA-Crossing-RSI-Trading-Strategy.md"
    timeframe = "1d"
    # The only `strategy.short` call is unreachable: its `when` is
    # `goShort() and close < short_price`, and `short_price` is assigned the
    # same bar's close. See the module docstring.
    can_short = False
    source_defaults: dict = {
        "sYear": 2019,
        "sMonth": 6,
        "sDay": 1,
        "sHour": 0,
        "sMinute": 0,
        "eYear": 2019,
        "eMonth": 12,
        "eDay": 1,
        "eHour": 0,
        "eMinute": 0,
        "len": 14,
        "_length": 7,
        "_phase": 50,
        "_power": 2,
        "highlightMovements": True,
        "useStop": True,
    }
    source_qty_type = "cash"
    source_qty_value = 5000.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "The RSI is the source's own rma-based expression with its own boundary "
        "tests (`down == 0 -> 100`, `up == 0 -> 0`) rather than pine_ta.pine_rsi; "
        "the two agree on the formula and the boundaries, and the source's form "
        "is reproduced literally.",
        "The JMA is a stateful recursion (e0/e1/e2/jma with one-bar feedback); it "
        "is evaluated bar by bar with Pine's `nz(x[1])` (na -> 0) on the history "
        "terms, and is na on every bar where the RSI is na.",
        "`long_price` and `short_price` are declared `=` at global scope, not "
        "`var`, so they are re-initialised to 0.0 on every bar and only take a "
        "value inside the same bar's `if`. Reproduced as per-bar expressions.",
        "Because of that scoping the `Sell` entry's `when` is `close < close` on "
        "the bar goShort() fires, which is never true: the short entry, its "
        "`strategy.close(\"Sell\")` and `strategy.exit(\"XSS\")` are unreachable "
        "and can_short is False. The calls are still written verbatim.",
        "The same scoping makes the long close's `close > long_price` guard "
        "vacuous (long_price is 0.0 whenever killLong() holds); written as-is "
        "rather than simplified.",
        "`startTime = true` / `endTime = true` are literals, not the ten "
        "Strategy-Tester date inputs, which nothing reads; the gate is always "
        "true and all ten inputs are still carried in source_defaults.",
        "`strategy.exit` is called every bar; flat, strategy.position_avg_price is "
        "na and so is the stop. Pine's `stop = na` is an unset parameter that "
        "does nothing; it is carried through as a NaN level, which the engine "
        "treats as an untriggerable leg and never publishes, rather than as a "
        "no-leg exit the projection layer would turn into a market exit "
        "(PINE_SEMANTICS 1.15). The call is still made on every bar.",
        "`currency = currency.EUR` is not modelled: pine_engine has no exchange "
        "rate, so the account is kept in the quote currency. Relative behaviour "
        "is unchanged; the currency translation is not reproduced.",
        "`highlightMovements`, `jmaColor`, `plot`, `hline` are display-only.",
        "The md PROSE says the LONG fires when JMA crosses above RSI (the code "
        "crosses rsi against jma) and lists a profit-ratio target (the code has "
        "no take-profit, only the 8% stop). Code is authoritative; differences "
        "recorded, not corrected.",
        "Leverage, margin, liquidation, funding and venue contract-step rounding "
        "are not modelled; the chain verifier measures the last separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        length = int(params["len"])
        change = ta.pine_change(close)
        up = ta.pine_rma(np.maximum(change, 0.0), length)
        down = ta.pine_rma(-np.minimum(change, 0.0), length)
        with np.errstate(divide="ignore", invalid="ignore"):
            rsi = pd.Series(
                np.where(
                    down == 0,
                    100.0,
                    np.where(up == 0, 0.0, 100.0 - (100.0 / (1.0 + up / down))),
                ),
                index=close.index,
                dtype=float,
            )
        jma = _jma(rsi, int(params["_length"]), int(params["_phase"]), int(params["_power"]))

        go_long = ta.pine_crossover(rsi, jma)
        kill_long = ta.pine_crossunder(rsi, jma)
        # `if (goLong()) long_price := close` / `if (goShort()) short_price := close`,
        # both re-initialised to 0.0 on every bar.
        long_price = close.where(go_long, 0.0)
        short_price = close.where(kill_long, 0.0)

        dataframe["pine_rsi"] = rsi
        dataframe["pine_jma"] = jma
        dataframe["pine_go_long"] = go_long
        dataframe["pine_kill_long"] = kill_long
        dataframe["pine_long_price"] = long_price
        dataframe["pine_short_price"] = short_price
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(),
            "go_long": dataframe["pine_go_long"].to_numpy(dtype=bool),
            "kill_long": dataframe["pine_kill_long"].to_numpy(dtype=bool),
            "long_price": dataframe["pine_long_price"].to_numpy(),
            "short_price": dataframe["pine_short_price"].to_numpy(),
            "use_stop": bool(params["useStop"]),
        }

    def pine_script(self, broker, i, ctx):
        go_long = bool(ctx["go_long"][i])
        kill_long = bool(ctx["kill_long"][i])
        close = ctx["close"][i]

        # if(startTime and endTime)          // both are literal `true`
        #     strategy.entry("Buy", strategy.long, when = goLong())
        broker.entry("Buy", "long", when=go_long)
        #     strategy.close("Buy", when = killLong() and close > long_price)
        broker.close("Buy", when=kill_long and close > ctx["long_price"][i])

        #     strategy.entry("Sell", strategy.short,
        #                    when = goShort() and close < short_price)
        broker.entry("Sell", "short",
                     when=kill_long and close < ctx["short_price"][i])
        #     strategy.close("Sell", when = killShort())     // killShort() = goLong()
        broker.close("Sell", when=go_long)

        # if (useStop)
        #   strategy.position_avg_price is na while flat, so the source's
        #   `stop = na / 1.08` is na as well. Pine's na means the stop parameter
        #   is unset and the exit does nothing; the na is carried through as a
        #   NaN level, which the engine treats as a leg that can never trigger
        #   and never publishes (PINE_SEMANTICS 1.15). The call itself is still
        #   made on every bar, as in the source, so the same-id replacement of
        #   the resting exit order keeps its Pine semantics.
        if ctx["use_stop"]:
            average = broker.position_avg_price
            if not np.isfinite(average):
                average = np.nan
            # strategy.exit("XLS", from_entry = "Buy",  stop = avg / 1.08)
            broker.exit("XLS", from_entry="Buy", stop=average / STOP_DIVISOR)
            # strategy.exit("XSS", from_entry = "Sell", stop = avg * 1.08)
            broker.exit("XSS", from_entry="Sell", stop=average * STOP_MULTIPLIER)
