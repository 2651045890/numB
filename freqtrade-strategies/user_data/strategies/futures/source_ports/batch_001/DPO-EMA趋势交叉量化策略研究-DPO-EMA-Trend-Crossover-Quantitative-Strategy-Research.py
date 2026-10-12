"""Port of sources/SM_f308360ca29746e7.pine (batch_001/DPO-EMA趋势交叉量化策略研究-DPO-EMA-Trend-Crossover-Quantitative-Strategy-Research.md).

Pine v5. The Detrended Price Oscillator against its own 4-period EMA:

    sma         = ta.sma(close, 24)
    shifted_sma = sma[24 / 2 + 1]          # 13 bars back
    dpo         = close - shifted_sma
    dpo_ema     = ta.ema(dpo, 4)
    ta.crossover(dpo, dpo_ema)  -> strategy.entry("Buy", strategy.long)
    ta.crossunder(dpo, dpo_ema) -> strategy.close("Buy")

`length = 24` and `ema_length = 4` are literals in the source, not inputs, so
they stay literals here (the source's own title calls them "DPO 4,24").

`strategy("DPO 4,24 Strategy", shorttitle=..., overlay=true)` declares neither
order sizing nor costs, so Pine's documented defaults apply and are recorded in
the class attributes below: `fixed` / 1 unit, commission 0%,
`pyramiding = 0`, `initial_capital = 1000000`,
`process_orders_on_close = false` (see the inline note on `pine_script`).

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1d` is the FMZ backtester's own bar grid
and not a second period the strategy reads.

There is no short entry anywhere in the source, so `can_short` is False.

FIDELITY:

* `sma[length / 2 + 1]` is a HISTORY reference -- 13 bars back -- not a forward
  shift. The md's prose says "Shift the SMA forward by (length/2+1) periods",
  which is the opposite direction. The source is authoritative and the port
  follows the source (`pine_sma(close, 24).shift(13)`); the prose is recorded
  here and the source's logic is NOT changed to match it.
* In Pine v5 `/` between two integer literals is not required to be integer
  division for this expression to be well defined: `24 / 2 + 1` is 13 either
  way, so the shift is 13 and no v5-vs-v4 division reading changes the port.
* Pine's `ta.ema` seeding rule is not publicly specified; this layer seeds the
  recursion with the first non-na observation (PINE_SEMANTICS.md §3.1). The
  dpo series is na for the first 36 bars (24-bar SMA window plus a 13-bar
  history reference), so the EMA's seed bar follows from that.
* `ta.sma` returns na until its window is full and na inside the window
  propagates; `pine_ta.pine_sma` implements exactly that (§3.2).
* `plotshape` / `shorttitle` / `overlay` are display-only and are not
  reproduced.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled by this layer (§1.6, §二.4); the chain verifier measures the
  rounding separately rather than treating it as a signal difference.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDPOEmaTrendCrossStrategy_f30836(PinePortBase, IStrategy):
    source_id = "SM_f308360ca29746e7"
    source_file = (
        "DPO-EMA趋势交叉量化策略研究-DPO-EMA-Trend-Crossover-Quantitative-Strategy-Research.md"
    )
    timeframe = "1d"
    can_short = False
    # `length` / `ema_length` are literals in the source, so there is no input()
    # to copy. Everything else about the source's sizing comes from Pine's
    # documented `strategy()` defaults, since only title/shorttitle/overlay are
    # declared.
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`sma[length / 2 + 1]` is a 13-bar HISTORY reference, not a forward "
        "shift. The md says \"Shift the SMA forward by (length/2+1) periods\"; "
        "the source is authoritative and the port follows the source. The md "
        "prose discrepancy is recorded, not applied.",
        "`length = 24` and `ema_length = 4` are literals in the source, not "
        "input() calls, so they stay literals.",
        "`strategy()` declares only title/shorttitle/overlay: Pine defaults "
        "fixed / 1 unit, commission 0%, pyramiding 0, initial capital 1000000, "
        "process_orders_on_close=false.",
        "ta.ema seeding is a modelled choice (first non-na seed), see "
        "PINE_SEMANTICS.md §3.1.",
        "ta.sma na propagation and the na-until-window-full rule follow the "
        "source's functions, see §3.2.",
        "plotshape / shorttitle / overlay are display-only, not reproduced.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled (§二.4, §1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # length = 24; ema_length = 4 (literals in the source)
        sma = ta.pine_sma(close, 24)
        # shifted_sma = sma[length / 2 + 1] -> sma[13]
        shifted_sma = sma.shift(24 // 2 + 1)
        dpo = close - shifted_sma
        dpo_ema = ta.pine_ema(dpo, 4)
        dataframe["pine_dpo"] = dpo
        dataframe["pine_dpo_ema"] = dpo_ema
        dataframe["pine_buy_signal"] = ta.pine_crossover(dpo, dpo_ema)
        dataframe["pine_sell_signal"] = ta.pine_crossunder(dpo, dpo_ema)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # The script is evaluated at bar close and its market orders fill on the
        # NEXT bar's open, which is what run_pine does with the ledger the
        # signals are projected from (process_orders_on_close is false).
        if ctx["buy_signal"][i]:
            # if (buy_signal)
            #     strategy.entry("Buy", strategy.long)
            broker.entry("Buy", "long")
        if ctx["sell_signal"][i]:
            # if (sell_signal)
            #     strategy.close("Buy")
            broker.close("Buy")
