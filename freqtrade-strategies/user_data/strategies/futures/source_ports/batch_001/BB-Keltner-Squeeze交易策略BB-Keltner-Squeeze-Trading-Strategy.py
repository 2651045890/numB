"""Port of sources/SM_ffaec53ecc8f6ef2.pine
(batch_001/BB-Keltner-Squeeze交易策略BB-Keltner-Squeeze-Trading-Strategy.md).

Pine v4 "BB Keltner Squeeze Strategy". A Bollinger/Keltner squeeze gates the
regime and a position is opened only on the bar the squeeze RELEASES:

    B2basis = sma(src, length)
    B2upper = B2basis + B2mult * stdev(src, length)
    Kma     = ema(src, length)
    Krange  = useTrueRange ? tr : high - low
    Kupper  = Kma + ema(Krange, length) * Kmult

    squeeze = Kupper > B2upper                       // true = squeezed
    midc    = squeeze ? 0 : close > B2basis ? 1 : 2  // 0 squeezed, 1 up, 2 down

    direction := midc[1]
    if direction == 0
        if midc[1] == 0 and midc == 1
            strategy.entry("LONG", strategy.long)
        else if midc[1] == 0 and midc == 2
            strategy.entry("SHORT", strategy.short)
    else if direction != midc
        strategy.close_all()

`strategy()` declares `initial_capital=10000` and `currency='USD'`; it does NOT
declare `default_qty_type` / `default_qty_value`, so sizing is Pine's
documented default `strategy.fixed` / 1 contract, commission 0% and pyramiding 0.
The `/*backtest` header declares `period: 30m` on Futures_Binance BTC_USDT, so
`timeframe` is "30m"; `basePeriod: 15m` is the FMZ backtester's own granularity
for filling 30m bars, not the strategy's period.

THE `direction := 1` / `:= 2` / `:= 0` ASSIGNMENTS INSIDE THE IF BLOCK ARE DEAD.
The source re-initialises `direction = 0` at the top of every bar and then
overwrites it with `direction := midc[1]` before the block, so the value the
block reads is always `midc[1]`, and anything the block writes is discarded by
the next bar's `direction = 0`. The port therefore evaluates the block against
`midc[1]` and carries no `direction` state of its own; that is the source's
behaviour, not a simplification of it.

`midc` is NOT sticky -- it is recomputed from `squeeze` on every bar -- so the
gate is "the previous bar was squeezed and this bar is not", which is what opens
a position. Once a position is on, the only exit is `close_all` on the bar
`midc` changes away from the value it had when the position was opened. (A
re-entry in the opposite direction is impossible without that `close_all`
firing first, because `midc[1] == 0` and `midc == 1 or 2` requires a squeeze
release, and any position held through it is closed by the `direction != midc`
branch on the bar `midc` moves.)

FIDELITY:

* `squeeze` is a comparison against possibly-na operands, and a comparison
  against na is false in Pine, so before the EMA/`stdev` windows fill the
  regime reads "not squeezed" and `midc` falls through to the `close > B2basis`
  test. Not special-cased.
* `tr` is Pine v4's builtin true range. `pine_ta.pine_tr` returns `high - low`
  on the first bar where Pine's `ta.tr` is na (PINE_SEMANTICS.md 3.7), which
  also seeds `ema(tr, length)` one bar early; recorded, not corrected -- the
  shared layer is not modified for it.
* `ema` is seeded with its first non-na observation (PINE_SEMANTICS.md 3.1);
  TradingView does not publish its seeding rule, so the first bars of
  `Kma`/`Krangema` are a modelled choice.
* `Krange = useTrueRange ? tr : high - low` is kept as a live branch on the
  input (default true) rather than folded, so overriding it behaves.
* The `strategy()` call declares only `title` / `overlay` / `initial_capital` /
  `currency`; the port reports `source_initial_capital = 10000.0` and keeps
  Pine's default `fixed` / 1 for sizing.
* `e1`, `osc`, `diff`, `osc_color`, `mid_color`, `fromYear`, `toYear`,
  `midcolor`, the `plot`s and the `bgcolor` are display-only and are not
  reproduced. `bband()` / `keltner()` are defined but only ever feed `diff`,
  which is itself unused, so they have no effect on orders and are not
  reproduced either.
* md vs code (recorded, code followed): the md's principle 3 describes entries
  as price breaking OUT of the Bollinger bands with the Keltner channel
  narrowing. The code never tests a price break; it opens on the bar the
  squeeze (Keltner upper ABOVE the Bollinger upper) releases, and takes the
  direction from `close` against `B2basis`. The code is followed.
* md vs code (recorded): the md describes the strategy as mean-reverting and
  mentions MACD histogram colouring, neither of which appears in the code.
* md vs code (recorded): the md's argument table omits `initial_capital`, which
  the source's `strategy()` call does set (10000, not Pine's 1000000 default).
* There is no stop / limit / trail / `strategy.exit` anywhere: exits are
  `close_all` only, so `source_reproduce_stops` is False.
* `can_short` is True: the source has a real `strategy.entry("SHORT",
  strategy.short)`.
* `initial_capital = 10000` with `fixed` / 1 contract asks for roughly one BTC
  of notional per entry, which is far above the framework's wallet, so the
  chain verifier is expected to report stake vetoes (PINE_SEMANTICS.md 1.5 /
  1.6) rather than a clean match. The value is the source's and is not adjusted
  to make the comparison pass.
* Leverage, margin, liquidation, funding, `request.security` and the venue's
  contract-step rounding are not modelled.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBBKeltnerSqueeze_ffaec5(PinePortBase, IStrategy):
    source_id = "SM_ffaec53ecc8f6ef2"
    source_file = "BB-Keltner-Squeeze交易策略BB-Keltner-Squeeze-Trading-Strategy.md"
    timeframe = "30m"
    can_short = True
    # input() defaults, in source order. `src` is `input(close)` and is
    # resolved through pine_ta.pine_source, so an override picks a different
    # OHLCV-derived series the same way the platform's dropdown would.
    source_defaults: dict = {
        "length": 20,
        "src": "close",
        "B2mult": 2.0,
        "useTrueRange": True,
        "Kmult": 1.5,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 10_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source re-initialises `direction = 0` each bar and then assigns "
        "`direction := midc[1]`, so the value the if-block reads is always "
        "midc[1] and its own `direction := 1/2/0` writes are dead. The port "
        "evaluates the block against midc[1] and keeps no direction state.",
        "`midc` is recomputed every bar (not sticky): 0 while squeezed "
        "(Kupper > B2upper), else 1 when close > B2basis, else 2. Entries only "
        "happen on a squeeze release; the only exit is close_all on the bar "
        "midc changes away from its value at entry.",
        "`tr` is Pine v4's builtin true range; pine_ta.pine_tr gives high-low on "
        "the first bar where Pine's ta.tr is na (PINE_SEMANTICS.md 3.7), which "
        "also seeds ema(tr, length) one bar early. Recorded, not corrected.",
        "pine_ema is seeded with its first non-na observation "
        "(PINE_SEMANTICS.md 3.1); TradingView's seeding rule is unspecified, so "
        "the early Kma / Krangema bars are a modelled choice.",
        "`Krange = useTrueRange ? tr : high - low` is kept as a live branch on "
        "the input (default true).",
        "`src` is input(close) and is resolved through pine_ta.pine_source, so "
        "an override selects another OHLCV-derived series, matching the input's "
        "own dropdown. The regime test `close > B2basis` always uses `close`, as "
        "in the source.",
        "The source's strategy() declares initial_capital=10000 and "
        "currency='USD' and nothing else, so sizing is Pine's default fixed / 1 "
        "contract with 0% commission and pyramiding 0.",
        "e1 / osc / diff / osc_color / mid_color / fromYear / toYear / midcolor "
        "and all plot / bgcolor calls are display-only. bband() and keltner() "
        "feed only `diff`, which is unused, so they do not affect orders.",
        "md vs code (recorded, code followed): the md describes entries on a "
        "Bollinger breakout with a Keltner squeeze; the code tests no breakout "
        "and opens only when the squeeze RELEASES, with the direction taken "
        "from close vs B2basis.",
        "md vs code (recorded): the md calls the strategy mean-reverting and "
        "mentions MACD histogram colouring; neither appears in the code.",
        "md vs code (recorded): the md's argument table omits initial_capital, "
        "which the source sets to 10000 (not Pine's 1000000 default).",
        "Exit is close_all only -- no strategy.exit / stop / limit / trail -- so "
        "source_reproduce_stops is False.",
        "Leverage, margin, liquidation, funding, request.security and "
        "contract-step rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]
        length = int(params["length"])
        src = ta.pine_source(dataframe, str(params["src"]))
        b2mult = float(params["B2mult"])
        use_true_range = bool(params["useTrueRange"])
        kmult = float(params["Kmult"])

        # ---- Bollinger side ----------------------------------------------
        b2_basis = ta.pine_sma(src, length)
        b2_dev = b2mult * ta.pine_stdev(src, length)
        b2_upper = b2_basis + b2_dev

        # ---- Keltner side ------------------------------------------------
        k_ma = ta.pine_ema(src, length)
        if use_true_range:
            k_range = ta.pine_tr(dataframe)
        else:
            k_range = high - low
        k_range_ma = ta.pine_ema(k_range, length)
        k_upper = k_ma + k_range_ma * kmult

        # squeeze = Kupper > B2upper; an na comparison is false in Pine.
        squeeze = (k_upper > b2_upper).fillna(False).to_numpy(dtype=bool)
        # midc := squeeze ? 0 : close > B2basis ? 1 : 2
        close_values = close.to_numpy(dtype=float)
        basis_values = b2_basis.to_numpy(dtype=float)
        midc = np.where(squeeze, 0, np.where(close_values > basis_values, 1, 2))

        dataframe["pine_b2basis"] = b2_basis
        dataframe["pine_b2upper"] = b2_upper
        dataframe["pine_kupper"] = k_upper
        dataframe["pine_squeeze"] = squeeze
        dataframe["pine_midc"] = midc
        return dataframe

    def pine_context(self, dataframe, params):
        midc = dataframe["pine_midc"].to_numpy(dtype=float)
        return {"midc": midc, "midc_prev": np.concatenate(([np.nan], midc[:-1]))}

    def pine_script(self, broker, i, ctx):
        midc = ctx["midc"][i]
        # direction := midc[1]
        direction = ctx["midc_prev"][i]
        if np.isnan(direction):
            # `direction == 0` and `direction != midc` are both false for na.
            return
        if direction == 0:
            # if midc[1] == 0 and midc == 1
            if midc == 1:
                broker.entry("LONG", "long")
            # else if midc[1] == 0 and midc == 2
            elif midc == 2:
                broker.entry("SHORT", "short")
        # else if direction != midc
        elif direction != midc:
            broker.close_all()
