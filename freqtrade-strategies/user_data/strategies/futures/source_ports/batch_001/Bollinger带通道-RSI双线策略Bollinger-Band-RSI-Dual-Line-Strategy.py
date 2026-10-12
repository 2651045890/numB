"""Port of sources/SM_c7f9cc976c5437a3.pine (batch_001/Bollinger带通道-RSI双线策略Bollinger-Band-RSI-Dual-Line-Strategy.md).

Pine v2. ChartArt's RSI + Bollinger Bands "double" strategy v1.1, BOTH sides.
Both indicators must turn at the same time; each entry is a resting stop order
at the band it just crossed, and it is cancelled again on any bar its condition
is false:

    RSIlength = input(6, title="RSI Period Length")
    RSIoverSold   = 50      // literal
    RSIoverBought = 50      // literal
    price = close
    vrsi  = rsi(price, RSIlength)

    BBlength = input(200, minval=1, title="Bollinger Period Length")
    BBmult   = 2            // literal; the input version is commented out
    BBbasis  = sma(price, BBlength)
    BBdev    = BBmult * stdev(price, BBlength)
    BBupper  = BBbasis + BBdev
    BBlower  = BBbasis - BBdev

    if (not na(vrsi))
        if (crossover(vrsi, RSIoverSold) and crossover(source, BBlower))
            strategy.entry("RSI_BB_L", strategy.long,  stop=BBlower)
        else
            strategy.cancel(id="RSI_BB_L")
        if (crossunder(vrsi, RSIoverBought) and crossunder(source, BBupper))
            strategy.entry("RSI_BB_S", strategy.short, stop=BBupper)
        else
            strategy.cancel(id="RSI_BB_S")

`strategy()` declares only `title`, `shorttitle` and `overlay`, so Pine's
documented defaults apply: `default_qty_type = strategy.fixed`,
`default_qty_value = 1`, `commission_value = 0`, `pyramiding = 0`, initial
capital 1000000 and `process_orders_on_close = false`. The `/*backtest` header
declares `period: 1h` on Futures_Binance BTC_USDT, so `timeframe` is "1h"; its
`basePeriod: 15m` is the FMZ backtester's own granularity for filling those
bars, not the strategy's period.

This is the two-sided sibling of the already-ported long-only v12
(`SM_95ae2d4e1396d74a`): same indicator block and same BBmult/RSIoverSold
literals, but the short arm exists and `strategy.close` is absent -- here a
position leaves only by reversing.

FIDELITY:

* `BBmult = 2` is a literal in the source -- the `input(2.0, ...)` that would
  make it tunable is commented out on the same line -- so it stays a literal
  and is not exposed as a parameter.
* `RSIoverSold` / `RSIoverBought` are 50 and are literals, not inputs; they are
  kept as literals. Because both are 50, the two arms use the SAME RSI level,
  which is what the source says.
* `rsi`, `sma` and `stdev` use the shared Pine models: `pine_rsi` (rma of gains
  and losses, 100 when the window has no losses), `pine_sma` and `pine_stdev`
  (population standard deviation, ddof=0, which is what `stdev` computes).
  Substituting a library RSI or a sample-stdev would change the bands.
* `crossover` / `crossunder` are Pine's event forms, false whenever either
  operand is na.
* Both entries are RESTING STOP orders (`stop=BBlower` / `stop=BBupper`), which
  the framework cannot express: PINE_SEMANTICS §二-11. The engine ledger fills
  them inside the bar that first reaches the level; `run_pine` projects them as
  next-open market entries on the placement bar, and the `else` branch's
  `cancel` on the following bar bounds how long they can rest. Framework
  boundary, not a port defect.
* `strategy.cancel(id="RSI_BB_L")` / `("RSI_BB_S")` run on every bar their
  condition is false (inside the `not na(vrsi)` guard), so each stop order
  normally rests for exactly one bar. `broker.cancel` reproduces it and never
  touches the position.
* The guard is `not na(vrsi)`, not a fully warmed-up state: with RSIlength 6,
  `vrsi` is na until the rma seeds, and the port skips the whole block on those
  bars, exactly as the source does. `crossover` / `crossunder` already depend on
  `vrsi`, so the guard changes nothing else here -- it is reproduced because it
  is in the source.
* `buyEntry` / `sellEntry`, `plot(...)`, `fill(p1, p2)`, the `TrendColor`
  expression and the `barcolor` / `bgcolor` calls are display-only and are not
  reproduced. `TrendColor` also reads `price[1]`, but since it never reaches an
  order it is not computed.
* `switch1` / `switch2` are display toggles for the bar/background colour. They
  are carried in `source_defaults` because they are inputs, and they reach no
  decision.
* The md's principle section describes level conditions ("RSI高于overbought且价格
  突破上轨" / "RSI低于oversold且价格突破下轨") while the source uses the
  crossover/crossunder EVENTS, and it reads the short arm as "price breaks above
  the upper band" while `crossunder(source, BBupper)` means close crossing DOWN
  through the upper band. The source wins; recorded, not corrected.
* Contract-step rounding, leverage, margin, liquidation and funding are not
  modelled (PINE_SEMANTICS §1.6, §二-4).
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandRsiDualLine_c7f9cc(PinePortBase, IStrategy):
    source_id = "SM_c7f9cc976c5437a3"
    source_file = "Bollinger带通道-RSI双线策略Bollinger-Band-RSI-Dual-Line-Strategy.md"
    timeframe = "1h"
    can_short = True
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
        "RSIoverSold and RSIoverBought are both the literal 50, not inputs, so "
        "the long and short arms trigger off the same RSI level.",
        "rsi / sma / stdev use the shared Pine models -- pine_rsi (rma of gains "
        "and losses, 100 when the window has no losses), pine_sma and "
        "pine_stdev (population stdev, ddof=0). They are not swapped for "
        "library equivalents.",
        "crossover / crossunder are Pine's event forms and are false whenever "
        "either operand is na.",
        "Both entries are resting stop orders (PINE_SEMANTICS §二-11): the "
        "projected enter_long / enter_short fill at the next open while the "
        "engine fills at the band in a later bar that reaches it; the else "
        "branch's cancel on the following bar bounds how long each can rest. "
        "Framework boundary, not a port defect.",
        "strategy.cancel(id=...) runs on every bar its condition is false, so "
        "each stop order normally rests for exactly one bar; broker.cancel "
        "reproduces it and never touches the position.",
        "The `not na(vrsi)` guard is reproduced as written, even though "
        "crossover/crossunder are already false while vrsi is na.",
        "buyEntry / sellEntry / plot / fill / TrendColor / barcolor / bgcolor "
        "are display-only and are not reproduced; TrendColor's price[1] read "
        "reaches no order.",
        "switch1 / switch2 are display toggles; they are carried as inputs and "
        "reach no decision.",
        "The md describes level conditions and reads the short arm as 'price "
        "breaks above the upper band'; the source is event-driven "
        "(crossunder(source, BBupper) = close crossing DOWN through the upper "
        "band). The source wins; recorded, not corrected.",
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
        rsi_over_sold = 50.0    # literal in the source
        rsi_over_bought = 50.0  # literal in the source
        bb_mult = 2.0           # literal in the source

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
        dataframe["pine_short"] = (
            ta.pine_crossunder(vrsi, rsi_over_bought)
            & ta.pine_crossunder(price, bb_upper)
        ).fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "vrsi": dataframe["pine_rsi"].to_numpy(dtype=float),
            "bb_upper": dataframe["pine_bb_upper"].to_numpy(dtype=float),
            "bb_lower": dataframe["pine_bb_lower"].to_numpy(dtype=float),
            "long": dataframe["pine_long"].to_numpy(dtype=bool),
            "short": dataframe["pine_short"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (not na(vrsi))
        if not np.isnan(ctx["vrsi"][i]):
            # if (crossover(vrsi, RSIoverSold) and crossover(source, BBlower))
            #     strategy.entry("RSI_BB_L", strategy.long, stop=BBlower)
            if ctx["long"][i]:
                broker.entry("RSI_BB_L", "long", stop=float(ctx["bb_lower"][i]))
            else:
                # strategy.cancel(id="RSI_BB_L")
                broker.cancel("RSI_BB_L")
            # if (crossunder(vrsi, RSIoverBought) and crossunder(source, BBupper))
            #     strategy.entry("RSI_BB_S", strategy.short, stop=BBupper)
            if ctx["short"][i]:
                broker.entry("RSI_BB_S", "short", stop=float(ctx["bb_upper"][i]))
            else:
                # strategy.cancel(id="RSI_BB_S")
                broker.cancel("RSI_BB_S")
