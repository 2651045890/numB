"""Port of sources/SM_fb8dd12eb9fad002.pine (batch_002/Relative-Strength-Index-strategy.md).

Pine v3. QuantNomad's RSI cross strategy: a 3-period RSI crossed UP through
an oversold LEVEL of 47 is taken long, and crossed DOWN through an overbought
LEVEL of 56 is taken short:

    vrsi = rsi(price, length)                       // price = close, length = 3
    if (not na(vrsi))
        if (crossover(vrsi, overSold))              // overSold   = 47
            strategy.entry("RsiLE", strategy.long, comment="RsiLE")
        if (crossunder(vrsi, overBought))           // overBought = 56
            strategy.entry("RsiSE", strategy.short, comment="RsiSE")

The two levels are NOT a conventional oversold/overbought pair: 47 sits BELOW
56, so the long trigger is a cross above a mid-range level and the short
trigger a cross below a higher one. That is the source's own parameterisation
and it is carried literally.

`strategy()` declares `default_qty_type = strategy.percent_of_equity` and
`default_qty_value = 100`, so both entries size off the full Pine equity;
everything else is Pine's documented default: initial capital 1000000,
commission 0%, `pyramiding` 0, `process_orders_on_close=false`. Neither entry
passes a `qty`, so both take the strategy-level default.

There is NO exit call anywhere in the source. A position is closed only by the
opposite entry reversing it, so `source_reproduce_stops` is False and a
position open at the end of the window stays open.

FIDELITY:

* `strategy.entry(strategy.short)` exists, so the port is two-sided and
  `can_short` is True.
* `rsi` is Pine's Wilder-smoothed RSI -- `100 - 100/(1 + rma(gain)/rma(loss))`
  -- reproduced by `pine_ta.pine_rsi` rather than by a re-derived average.
  PINE_SEMANTICS.md section 3.3 records the boundary model (100 when there
  were no losses in the window, na until the Wilder warm-up has formed) as an
  equivalence risk that has not been compared bar by bar with the platform.
* The `if (not na(vrsi))` guard is preserved even though it places no
  condition: `pine_crossover` / `pine_crossunder` already yield False while
  either side is na (Pine treats na comparisons as false), so the guard can
  only ever skip work that would not have placed an order.
* `percent_of_equity` sizing is reproduced from the engine's own recorded fill
  notional, not re-derived from the live wallet (PINE_SEMANTICS.md 1.4). The
  source leaves `initial_capital` at Pine's default 1000000, which is the row
  of PINE_SEMANTICS.md 1.6's table where venue contract-step rounding is
  negligible; the sizing-the-basis exposure of 1.4 is therefore the only one
  of the two that applies here.
* `pyramiding` is undeclared, i.e. Pine's default 0, so a repeated
  same-direction entry while a position is already open is ignored at CREATION
  by the engine and suppressed from the projected signal alike.
* The source's `plot(strategy.equity, ...)` line is COMMENTED OUT in the
  source and is display-only in any case; it is not restored.
* The `crossover` / `crossunder` here are Pine v3's bare builtins; the port
  calls `pine_ta.pine_crossover` / `pine_crossunder`, which model exactly the
  documented `a > b and a[1] <= b[1]` / `a < b and a[1] >= b[1]` definitions.
* DISAGREEMENT (code followed, both sides recorded): the `strategy()` title
  and the md prose describe an LTCUSDT 5-MINUTE chart, while the `/*backtest`
  header -- the source's own declaration of what was backtested -- says
  `period: 1d` on `Futures_Binance BTC_USDT`. The port takes `timeframe` from
  the header, "1d", and the chain check runs it on BTC/USDT:USDT. The header's
  `basePeriod: 1h` is the FMZ backtester's own granularity for filling those
  1d bars, not the strategy's period.
* The md's description of the mechanics ("crosses over the oversold level ...
  crosses under the overbought level") and its argument table (3 / 47 / 56)
  agree with the code; no disagreement there.
* Slippage, leverage, margin, liquidation and funding are not modelled; the
  venue's contract-step rounding is not modelled by the engine either (the
  chain verifier measures it separately).
"""
from freqtrade.strategy import IStrategy

import numpy as np

import pine_ta as ta
from pine_port_base import PinePortBase


class SMRelativeStrengthIndex_fb8dd1(PinePortBase, IStrategy):
    source_id = "SM_fb8dd12eb9fad002"
    source_file = "Relative-Strength-Index-strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {"length": 3, "overSold": 47, "overBought": 56}
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The two levels are not a conventional oversold/overbought pair: "
        "overSold=47 sits BELOW overBought=56, so the long trigger is a cross "
        "above 47 and the short trigger a cross below 56. Carried literally.",
        "`rsi` is Wilder-smoothed (pine_ta.pine_rsi). PINE_SEMANTICS.md 3.3 "
        "records the na/100 boundary model as an uncompared equivalence risk.",
        "The `if (not na(vrsi))` guard is preserved although it places no "
        "condition: pine_crossover/pine_crossunder are already false while "
        "either side is na.",
        "percent_of_equity sizing comes from the engine's recorded fill "
        "notional (PINE_SEMANTICS.md 1.4), not from the live wallet. Initial "
        "capital is Pine's default 1000000, the row of PINE_SEMANTICS.md "
        "1.6's table where contract-step rounding is negligible.",
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False and a position open "
        "at the end of the window stays open.",
        "pyramiding is undeclared (Pine default 0), so a repeated "
        "same-direction entry while a position is open is ignored at creation "
        "and suppressed from the projected signal too.",
        "The source's `plot(strategy.equity, ...)` is commented out and "
        "display-only; it is not restored.",
        "DISAGREEMENT (code followed): the strategy title and the md describe "
        "an LTCUSDT 5-minute chart, while the source's own `/*backtest` header "
        "declares `period: 1d` on Futures_Binance BTC_USDT. timeframe is taken "
        "from the header. The header's basePeriod: 1h is FMZ's fill "
        "granularity, not the strategy's period.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        length = int(params["length"])
        oversold = float(params["overSold"])
        overbought = float(params["overBought"])
        # vrsi = rsi(price, length)          // price = close
        vrsi = ta.pine_rsi(close, length)
        dataframe["pine_vrsi"] = vrsi
        # if (crossover(vrsi, overSold)) / if (crossunder(vrsi, overBought))
        dataframe["pine_long_condition"] = ta.pine_crossover(vrsi, oversold)
        dataframe["pine_short_condition"] = ta.pine_crossunder(vrsi, overbought)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "vrsi": dataframe["pine_vrsi"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (not na(vrsi))
        if np.isfinite(ctx["vrsi"][i]):
            # if (crossover(vrsi, overSold))
            #     strategy.entry("RsiLE", strategy.long, comment="RsiLE")
            if ctx["long_condition"][i]:
                broker.entry("RsiLE", "long")
            # if (crossunder(vrsi, overBought))
            #     strategy.entry("RsiSE", strategy.short, comment="RsiSE")
            if ctx["short_condition"][i]:
                broker.entry("RsiSE", "short")
