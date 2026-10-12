"""Port of sources/SM_869eed0bd52d0059.pine
(batch_001/EMA黄金交叉短线交易策略EMA-Golden-Cross-Short-term-Trading-Strategy.md).

Pine v5, `strategy(title="EMA SCALPEUR", overlay=true, initial_capital = 1000)`.
Four EMA inputs, two of which are crossed for the entry and the other two for
the exit:

    EMA_L = input.int(9,   "EMA_L")     EMA_L2 = input.int(26,  "EMA_L2")
    EMA_S = input.int(100, "EMA_S")     EMA_S2 = input.int(55,  "EMA_S2")

    shortest = ta.ema(close, 9)  / short  = ta.ema(close, 26)
    longer   = ta.ema(close, 100)/ longest= ta.ema(close, 55)   # plots only
    EMA1 = ta.ema(close, EMA_L)   EMA2 = ta.ema(close, EMA_L2)
    EMA3 = ta.ema(close, EMA_S)   EMA4 = ta.ema(close, EMA_S2)

    buy     = ta.crossover(EMA1, EMA2)
    buyexit = ta.crossunder(EMA3, EMA4)

    strategy.entry("long", strategy.short, when = buy, comment = "ENTER-SHORT")
    strategy.close("long", when = buyexit, comment = "EXIT-SHORT")

The direction is deliberately `strategy.short` while the entry ID is "long" and
the comments say "ENTER-SHORT"/"EXIT-SHORT" -- the source is short only, which
is why `can_short` is True. `strategy()` declares only `title`, `overlay` and
`initial_capital`, so the remaining properties are Pine's documented defaults:
`default_qty_type=fixed`, `default_qty_value=1`, `commission_value=0`,
`pyramiding=0`, `process_orders_on_close=false`.

FIDELITY:

* The markdown describes a LONG strategy ("go long when the 9 EMA crosses above
  the 26 EMA"), which contradicts the source's `strategy.short`. The source is
  the authority: the port is short only and `can_short` is True.
* The markdown's "Strategy Arguments" table lists the four inputs as
  9 / 26 / 100 / 55, which are the source's own `defval`s and are carried in
  `source_defaults` under the source's variable names. `minval` / `maxval` /
  `step` only constrain the UI.
* `shortest` / `short` / `longer` / `longest` (hardcoded 9 / 26 / 100 / 55) are
  plotted and never read by an order call; the trading EMAs come from the
  inputs, whose defaults happen to be the same four numbers. The hardcoded
  series are kept as columns and not re-used for the signals.
* The commented-out `//sell`, `//sellexit`, `//strategy.entry("short", ...)`
  and `//strategy.close("short", ...)` lines place nothing and are NOT restored.
* THE SOURCE'S SIZING CANNOT BE FUNDED BY THE FRAMEWORK. `initial_capital =
  1000` with Pine's default `fixed` / 1 contract is a one-unit BTC position
  (about 43 000 USDT over the source's December 2023 window) against a 1 000
  USDT account. The engine charges no affordability check and books the trades;
  Freqtrade's `custom_stake_amount` refuses a stake above the wallet and logs
  `SOURCE_STAKE_VETO`, so the framework opens nothing and the comparison reads
  as `one_sided_trades`. That is the PINE_SEMANTICS 1.6 / 1.5.1 class of
  exposure -- a function of the source's declared capital, not a porting error
  -- and the source's capital is reproduced rather than rescaled.
* `pine_ema` seeds with the first observation (PINE_SEMANTICS 3.1), a
  public-layer choice; the source's `ta.ema` seeding is unpublished, and a
  100-period EMA is the longest leg here, so early bars can differ from the
  original platform (PINE_SEMANTICS 3.1 records exactly this risk).
* `plot()` of the four EMAs, of `close` and the `//@version` / licence comment
  lines are display-only.
* Leverage, margin, funding and the venue's contract-step rounding are not
  modelled (PINE_SEMANTICS 1.6, 2.4).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaScalpeur_869eed(PinePortBase, IStrategy):
    source_id = "SM_869eed0bd52d0059"
    source_file = "EMA黄金交叉短线交易策略EMA-Golden-Cross-Short-term-Trading-Strategy.md"
    # /*backtest ... period: 1m ... */ on Futures_Binance BTC_USDT.
    timeframe = "1m"
    # strategy.entry(id="long", direction=strategy.short): a real short entry.
    can_short = True
    source_defaults: dict = {"EMA_L": 9, "EMA_L2": 26, "EMA_S": 100, "EMA_S2": 55}
    # strategy(title=..., overlay=true, initial_capital=1000): no sizing and no
    # commission, so Pine's defaults apply -- fixed 1 contract, 0% commission,
    # pyramiding 0, process_orders_on_close false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    # The only exit is strategy.close (a market close); no stop / limit / trail
    # level is ever placed.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source enters SHORT (strategy.short) under the entry id 'long', so "
        "can_short is True; the markdown's description of a long strategy is a "
        "md-vs-source difference and the source wins.",
        "The entry id is 'long' even though the position is short; it is never "
        "renamed, and strategy.close('long') names the same id.",
        "initial_capital=1000 with Pine's default fixed qty of 1 contract is a "
        "one-unit BTC position (~43000 USDT) the framework's wallet cannot "
        "fund: custom_stake_amount vetoes it (SOURCE_STAKE_VETO, "
        "PINE_SEMANTICS 1.5.1 / 1.6) while the engine, which has no "
        "affordability check, trades. The comparison is expected to read as "
        "one_sided_trades; the source's capital is reproduced, not rescaled.",
        "The hardcoded 9/26/100/55 EMAs (shortest/short/longer/longest) are "
        "plots only; the signals use the EMA_L / EMA_L2 / EMA_S / EMA_S2 "
        "inputs, whose defaults are the same four numbers.",
        "The commented-out entry/exit pairs (sell, sellexit, the 'short' id "
        "variants) place nothing and are not restored.",
        "pine_ema seeds with the first observation (PINE_SEMANTICS 3.1), a "
        "public-layer choice; the source's ta.ema seeding is unpublished and "
        "the 100-period leg makes early-bar differences in the original "
        "platform plausible.",
        "plot() calls and the licence/version comments are display-only.",
        "Leverage, margin, funding and the venue's contract-step rounding are "
        "not modelled (PINE_SEMANTICS 1.6, 2.4).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # Displays only in the source; kept for traceability, never read by an
        # order call.
        dataframe["pine_display_shortest"] = ta.pine_ema(close, 9)
        dataframe["pine_display_short"] = ta.pine_ema(close, 26)
        dataframe["pine_display_longer"] = ta.pine_ema(close, 100)
        dataframe["pine_display_longest"] = ta.pine_ema(close, 55)
        # EMA1 = ta.ema(close, EMA_L) ... EMA4 = ta.ema(close, EMA_S2)
        ema1 = ta.pine_ema(close, int(params["EMA_L"]))
        ema2 = ta.pine_ema(close, int(params["EMA_L2"]))
        ema3 = ta.pine_ema(close, int(params["EMA_S"]))
        ema4 = ta.pine_ema(close, int(params["EMA_S2"]))
        # buy = ta.crossover(EMA1, EMA2); buyexit = ta.crossunder(EMA3, EMA4)
        dataframe["pine_buy"] = ta.pine_crossover(ema1, ema2)
        dataframe["pine_buyexit"] = ta.pine_crossunder(ema3, ema4)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy": dataframe["pine_buy"].to_numpy(),
            "buyexit": dataframe["pine_buyexit"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("long", strategy.short, when = buy, comment = "ENTER-SHORT")
        broker.entry("long", "short", when=bool(ctx["buy"][i]))
        # strategy.close("long", when = buyexit, comment = "EXIT-SHORT")
        broker.close("long", when=bool(ctx["buyexit"][i]))
