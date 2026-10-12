"""Port of sources/SM_1414e5da76504c15.pine (batch_002/T7-JNSAR量化交易策略T7-JNSAR-Quantitative-Trading-Strategy.md).

Pine v2. The JNSAR line -- a 5-period EMA of high, low and close taken at five
consecutive lags, all fifteen values summed and divided by 15, then ROUNDED to
a whole number -- gates a two-sided trend entry: close above the line is long,
close below it is short.

    sum = ema(high,5) + ema(low,5) + ema(close,5)
    sum := sum + ema(high[1],5) + ema(low[1],5) + ema(close[1],5)
    ...                                                 // lags 2, 3 and 4
    jnsar = round(sum/15)

    buy   = close > jnsar
    short = close < jnsar

    if backtest != 0
        strategy.entry("JNSARLong",  strategy.long,  comment="JNSARLong",  when=buy!=0)
        strategy.entry("JNSARShort", strategy.short, comment="JNSARShort", when=short!=0)

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. Neither entry
passes a `qty`, so both take the strategy-level default.

There is NO exit call. A position is closed only by the opposite entry
reversing it, so `source_reproduce_stops` is False and a position open at the
end of the window stays open. Both entries fire on every bar as calls; the
source gates them with `when=`, and so does the port.

FIDELITY:

* `ema(high[1], 5)` is the EMA of the SHIFTED series, not the lagged EMA
  `ema(high, 5)[1]`. The two share a recursion but not a seed: modelled with
  `pine_ema`'s first-value seeding, the shift form is seeded at bar k with
  the first observation of the shifted series, so the lagged form would pin a
  different starting value. The source's form is the one reproduced, with the
  shift applied BEFORE the EMA.
* v2's bare `ema` is taken to be `ta.ema` and is translated by
  `pine_ta.pine_ema`; the seed is that layer's MODELLED CHOICE (first non-na
  observation, na does not advance the recursion) and PINE_SEMANTICS.md
  section 3.1 records that TradingView's exact seeding rule is unpublished and
  uncompared. The warm-up of the JNSAR line inherits that risk.
* `round(sum/15)` is Pine v2's `round(x)` -- nearest whole number, ties away
  from zero -- not banker's rounding; `pine_ta.pine_round(x, 0)` implements
  exactly that. Because the level is rounded to a whole price unit, the
  comparison `close > jnsar` is a comparison against an integer, and up to
  0.5 of absolute price is discarded from the level on every bar. That is the
  source's own arithmetic, kept literal.
* The na warm-up is structural, not incidental: the lag-k term is na until bar
  k (all of `high[4]` / `low[4]` / `close[4]` are), so `jnsar` is na for the
  first four bars, and both tests are then false rather than true.
* `close == jnsar` satisfies neither test, so a position is held across an
  exact touch. Preserved: the source uses strict `>` and `<`.
* `sum` is built with v2's `:=` reassignment (the manifest flags this file
  `persistent_state`), but every bar recomputes `sum` from its first line, so
  no value is carried from one bar to the next and no state column is needed.
* The `backtest` input (`input(title="Enable Backtest", type=bool, defval=1)`,
  the md's table row `v_input_1|true`) gates the entry block. In Pine v2 `true`
  behaves as 1, so `backtest != 0` holds at its default and the entries run;
  the port tests the flag for truth rather than translating `!= 0` literally,
  because Python's `True != 0` is False (bool is an int subclass here) and
  would invert the source's meaning.
* DISAGREEMENT (code followed, both sides recorded): the md prose calls this a
  DAILY NIFTY index system ("5日高低收", "当日收盘价", "只交易NIFTY指数"),
  while the `/*backtest` header -- the source's own backtest declaration --
  says `period: 1h` on `Futures_Binance BTC_USDT`. The port takes `timeframe`
  from the header, "1h", and the chain check runs it on BTC/USDT:USDT. The
  header's `basePeriod: 15m` is FMZ's own granularity for filling those 1h
  bars, not the strategy's period. The md's other claims (entry at the next
  open after the signal, exit on the reverse signal, every signal traded) do
  match the code.
* `plot(jnsar, color=green, linewidth=4)` is display-only and places no
  condition.
* Slippage, leverage, margin, liquidation and funding are not modelled; the
  venue's contract-step rounding is not modelled by the engine either (the
  chain verifier measures it separately).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMT7Jnsar_1414e5(PinePortBase, IStrategy):
    source_id = "SM_1414e5da76504c15"
    source_file = "T7-JNSAR量化交易策略T7-JNSAR-Quantitative-Trading-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {"backtest": True}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`ema(high[1], 5)` is the EMA of the SHIFTED series, not the lagged "
        "EMA; the shift is applied BEFORE the EMA, so the seed is the first "
        "observation of the shifted series.",
        "v2's bare `ema` is translated by pine_ta.pine_ema, whose first-value "
        "seed is a MODELLED CHOICE (PINE_SEMANTICS.md 3.1) -- TradingView's "
        "exact seeding is unpublished and uncompared. The JNSAR warm-up "
        "inherits that risk.",
        "`round(sum/15)` is v2's round() -- nearest whole number, ties away "
        "from zero, NOT banker's rounding -- via pine_ta.pine_round(x, 0). The "
        "level is therefore an integer price and up to 0.5 of price is "
        "discarded from it on every bar; that is the source's own arithmetic.",
        "The lag-k term is na until bar k, so jnsar is na for the first four "
        "bars and both tests are false there.",
        "`close == jnsar` satisfies neither test; a position is held across an "
        "exact touch. Strict `>` and `<` are preserved.",
        "`sum` uses v2's `:=` reassignment (the manifest flags this file "
        "persistent_state), but each bar recomputes it from its first line, so "
        "nothing is carried across bars.",
        "The `backtest` input (default true) gates the entry block. In Pine v2 "
        "`true` behaves as 1 so `backtest != 0` holds; the port tests the flag "
        "for truth instead of translating `!= 0` literally, because Python's "
        "`True != 0` is False and would invert the source's meaning.",
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False and a position open "
        "at the end of the window stays open.",
        "pyramiding is undeclared (Pine default 0), so a repeated "
        "same-direction entry while a position is open is ignored at creation "
        "and suppressed from the projected signal too.",
        "DISAGREEMENT (code followed): the md calls this a daily NIFTY system, "
        "while the source's own `/*backtest` header declares `period: 1h` on "
        "Futures_Binance BTC_USDT. timeframe comes from the header; basePeriod "
        "15m is FMZ's fill granularity, not the strategy's period.",
        "plot(jnsar, ...) is display-only.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        # sum = ema(high,5) + ema(low,5) + ema(close,5)
        # sum := sum + ema(high[k],5) + ema(low[k],5) + ema(close[k],5)   k=1..4
        total = None
        for lag in range(5):
            term = (
                ta.pine_ema(high.shift(lag), 5)
                + ta.pine_ema(low.shift(lag), 5)
                + ta.pine_ema(close.shift(lag), 5)
            )
            total = term if total is None else total + term
        # jnsar = round(sum/15)
        jnsar = ta.pine_round(total / 15.0, 0)
        dataframe["pine_jnsar"] = jnsar
        # buy = close > jnsar  /  short = close < jnsar
        dataframe["pine_long_condition"] = close > jnsar
        dataframe["pine_short_condition"] = close < jnsar
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "jnsar": dataframe["pine_jnsar"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "backtest_enabled": bool(params["backtest"]),
        }

    def pine_script(self, broker, i, ctx):
        # if backtest != 0
        if ctx["backtest_enabled"]:
            # strategy.entry("JNSARLong", strategy.long, comment="JNSARLong",
            #                 when=buy!=0)
            broker.entry("JNSARLong", "long",
                         when=bool(ctx["long_condition"][i]))
            # strategy.entry("JNSARShort", strategy.short, comment="JNSARShort",
            #                 when=short!=0)
            broker.entry("JNSARShort", "short",
                         when=bool(ctx["short_condition"][i]))
