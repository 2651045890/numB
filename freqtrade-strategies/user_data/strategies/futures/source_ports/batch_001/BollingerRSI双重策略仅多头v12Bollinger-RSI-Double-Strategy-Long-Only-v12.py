"""Port of sources/SM_95ae2d4e1396d74a.pine (batch_001/BollingerRSI双重策略仅多头v12Bollinger-RSI-Double-Strategy-Long-Only-v12.md).

Pine v3 long-only ChartArt RSI + Bollinger Bands "double" strategy. Both
indicators must turn at the same time; the entry is a resting stop-buy at the
lower band and it is cancelled again on any bar the long condition is false:

    RSIlength  = input(6,   title="RSI Period Length")
    RSIoverSold = 50        // literal
    RSIoverBought = 50      // literal
    price = close
    vrsi  = rsi(price, RSIlength)

    BBlength = input(200, minval=1, title="Bollinger Period Length")
    BBmult   = 2            // literal; the input version is commented out
    BBbasis  = sma(price, BBlength)
    BBdev    = BBmult * stdev(price, BBlength)
    BBupper  = BBbasis + BBdev
    BBlower  = BBbasis - BBdev

    long       = crossover(vrsi, RSIoverSold) and crossover(price, BBlower)
    close_long = crossunder(vrsi, RSIoverBought) and crossunder(price, BBupper)

    if (not na(vrsi))
        if long
            strategy.entry("RSI_BB", strategy.long, stop=BBlower, comment="RSI_BB")
        else
            strategy.cancel(id="RSI_BB")
        if close_long
            strategy.close("RSI_BB")

`strategy()` declares only `title`, `shorttitle` and `overlay`, so Pine's
documented defaults apply: `default_qty_type = fixed`, `default_qty_value = 1`,
`commission_value = 0`, `pyramiding = 0`, initial capital 1000000 and
`process_orders_on_close = false`. The `/*backtest` header declares
`period: 1m` on Futures_Binance BTC_USDT, so `timeframe` is "1m"; its
`basePeriod: 1m` matches.

FIDELITY:

* `BBmult = 2` is a literal in the source -- the `input(2.0, ...)` that would
  make it tunable is commented out on the same line -- so it stays a literal
  and is not exposed as a parameter.
* `RSIoverSold` / `RSIoverBought` are 50 and are literals, not inputs; they are
  kept as literals.
* `rsi`, `sma` and `stdev` are reproduced with the shared Pine models:
  `pine_ta.pine_rsi` (rma of gains/losses, 100 when there are no losses in the
  window), `pine_ta.pine_sma` and `pine_ta.pine_stdev` (population standard
  deviation, ddof=0, which is what `stdev` computes). Substituting a library
  RSI or a sample-stdev would change the bands, so they are not substituted.
* `crossover` / `crossunder` are Pine's event forms, false whenever either
  operand is na, which `pine_ta.pine_crossover` / `pine_crossunder` reproduce
  by filling na with False.
* The entry is a RESTING STOP order (`stop=BBlower`), which the framework
  cannot express: PINE_SEMANTICS §二-11. The long condition requires
  `crossover(price, BBlower)`, so the stop price sits below the signal bar's
  close and the order usually fills at the next bar's open -- which is also
  what the projected `enter_long` makes the framework do. The two can still
  part on a bar that gaps down through the band. Framework boundary, not a
  port defect.
* `strategy.cancel(id="RSI_BB")` runs on every bar the long condition is false
  (inside the `not na(vrsi)` guard), so the stop order normally rests for
  exactly one bar. It is reproduced with `broker.cancel`, which cancels the
  pending order and never touches the position.
* The guard is `not na(vrsi)`, not a fully warmed-up state: with RSIlength 6,
  `vrsi` is na until the rma seeds, and the port skips the whole block on those
  bars, exactly as the source does. Note that `long` and `close_long` both
  depend on `vrsi`, and `crossover`/`crossunder` are false while it is na, so
  the guard changes nothing else here -- it is reproduced because it is in the
  source.
* The source places a market `strategy.close("RSI_BB")` (Pine's `strategy.close`
  has no price leg) and does NOT cancel the same-id entry order with it. The
  port matches that: no cancellation is added to `close`.
* `buyEntry`, `sellEntry`, `plot(...)`, `fill(...)`, the `TrendColor`
  expression and the `barcolor` / `bgcolor` calls are display-only and are not
  reproduced. `TrendColor` also reads `price[1]`, but since it never reaches an
  order it is not computed.
* The md's "策略原理" describes level conditions ("RSI below 50", "price below
  the lower band") while the source uses the crossover/crossunder EVENTS. The
  source wins; the port is event-driven. Recorded, not corrected.
* `switch1` / `switch2` are display toggles for the bar/background colour. They
  are carried in `source_defaults` because they are inputs, and they reach no
  decision.
* Contract-step rounding, leverage, margin, liquidation and funding are not
  modelled (PINE_SEMANTICS §1.6, §二-4).
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerRsiDoubleLong_95ae2d(PinePortBase, IStrategy):
    source_id = "SM_95ae2d4e1396d74a"
    source_file = (
        "BollingerRSI双重策略仅多头v12Bollinger-RSI-Double-Strategy-Long-Only-v12.md"
    )
    timeframe = "1m"
    can_short = False
    source_defaults: dict = {
        "RSIlength": 6,
        "BBlength": 200,
        "switch1": True,
        "switch2": True,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "BBmult is the literal 2 in the source (its input() is commented out on "
        "the same line), so it is not exposed as a parameter.",
        "RSIoverSold and RSIoverBought are the literals 50, not inputs.",
        "rsi / sma / stdev use the shared Pine models -- pine_rsi (rma of gains "
        "and losses, 100 when the window has no losses), pine_sma and "
        "pine_stdev (population stdev, ddof=0). They are not swapped for "
        "library equivalents.",
        "crossover / crossunder are Pine's event forms and are false whenever "
        "either operand is na.",
        "The entry is a resting stop order (PINE_SEMANTICS §二-11), which the "
        "framework cannot express: the projected enter_long fills at the next "
        "open while the engine fills at max(stop, open) of a later bar. They "
        "usually coincide because the stop sits below the signal bar's close. "
        "Framework boundary, not a port defect.",
        "strategy.cancel(id=\"RSI_BB\") runs on every bar the long condition is "
        "false, so the stop order normally rests for exactly one bar; "
        "broker.cancel reproduces it and never touches the position.",
        "The `not na(vrsi)` guard is reproduced as written, even though "
        "crossover/crossunder are already false while vrsi is na.",
        "strategy.close(\"RSI_BB\") is a market close with no price leg and does "
        "not cancel the same-id entry order in the source; no cancellation was "
        "added to it.",
        "buyEntry / sellEntry / plot / fill / TrendColor / barcolor / bgcolor "
        "are display-only and are not reproduced; TrendColor's price[1] read "
        "reaches no order.",
        "The md's principle section describes level conditions (RSI below 50, "
        "price below the lower band) while the source is event-driven "
        "(crossover / crossunder). The source wins; recorded, not corrected.",
        "switch1 / switch2 are display toggles; they are carried as inputs and "
        "reach no decision.",
        "strategy() declares only title/shorttitle/overlay, so Pine's defaults "
        "apply: qty_type fixed, qty_value 1, commission 0, pyramiding 0, "
        "initial capital 1000000, process_orders_on_close false.",
        "Contract-step rounding, leverage, margin, liquidation and funding are "
        "not modelled (PINE_SEMANTICS §1.6, §二-4).",
    ]

    def pine_indicators(self, dataframe, params):
        price = dataframe["close"]
        rsi_length = int(params["RSIlength"])
        bb_length = int(params["BBlength"])
        rsi_over_sold = 50.0   # literal in the source
        rsi_over_bought = 50.0  # literal in the source
        bb_mult = 2.0          # literal in the source

        vrsi = ta.pine_rsi(price, rsi_length)
        bb_basis = ta.pine_sma(price, bb_length)
        bb_dev = bb_mult * ta.pine_stdev(price, bb_length)
        bb_upper = bb_basis + bb_dev
        bb_lower = bb_basis - bb_dev

        dataframe["pine_rsi"] = vrsi
        dataframe["pine_bb_basis"] = bb_basis
        dataframe["pine_bb_upper"] = bb_upper
        dataframe["pine_bb_lower"] = bb_lower
        dataframe["pine_long"] = (
            ta.pine_crossover(vrsi, rsi_over_sold)
            & ta.pine_crossover(price, bb_lower)
        ).fillna(False).astype(bool)
        dataframe["pine_close_long"] = (
            ta.pine_crossunder(vrsi, rsi_over_bought)
            & ta.pine_crossunder(price, bb_upper)
        ).fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "vrsi": dataframe["pine_rsi"].to_numpy(),
            "bb_lower": dataframe["pine_bb_lower"].to_numpy(),
            "long": dataframe["pine_long"].to_numpy(),
            "close_long": dataframe["pine_close_long"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (not na(vrsi))
        if not np.isnan(ctx["vrsi"][i]):
            # if long
            #     strategy.entry("RSI_BB", strategy.long, stop=BBlower, ...)
            if ctx["long"][i]:
                broker.entry("RSI_BB", "long", stop=float(ctx["bb_lower"][i]))
            else:
                # strategy.cancel(id="RSI_BB")
                broker.cancel("RSI_BB")
            # if close_long
            #     strategy.close("RSI_BB")
            if ctx["close_long"][i]:
                broker.close("RSI_BB")
