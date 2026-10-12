"""Port of sources/SM_30fc81c0d5b5e82c.pine (batch_001/JBravo量化趋势策略JBravo-Quantitative-Trend-Strategy.md).

Pine v4 by bradvaughn. `strategy("JBravo Swing", overlay = false)` declares no
sizing, no commission and no pyramiding, so all three stay at Pine's documented
defaults (fixed / 1 contract, 0%, pyramiding 0 -- see the attributes below).

The source computes a large set of moving averages and conditions, but only ONE
pair of them reaches a `strategy.*` call. The traded logic is the VWAP against
the 20 EMA:

    vwap1     = vwap(hlc3)
    ema20     = ema(close, 20)
    vwaplong  = vwap1 > ema20
    vwapshort = vwap1 < ema20

    strategy.entry("GoGo Long",  strategy.long,  1, when = vwaplong  and vwapInput)
    strategy.entry("GoGo Short", strategy.short, 1, when = vwapshort and vwapInput)
    strategy.close("GoGo Long",  when = vwapshort and vwapInput)
    strategy.close("GoGo Short", when = vwaplong  and vwapInput)

`vwapInput` is an input.bool defaulting to true, so the four calls are live.
The quantity `1` is written explicitly as the third positional argument of both
entries, so the source's own `default_qty_value` never sizes anything here.

Everything else in the source -- `sma9`, `sma180`, `buyLow`/`sellLow`/`sellma`,
the `sma9_uptrend` / `sma180_uptrend` / `ema20_uptrend` flags, the `var
buy_in_progress` state machine, `Buy` / `Sell` / `StrongBuy` / `StrongSell` --
feeds only `plot`, `plotshape` and `alertcondition`. No `strategy.*` call reads
any of it, so none of it can change an order and none of it is reproduced (see
FIDELITY). Note in particular that `Buy` and `Sell` are NOT the traded signal
despite their names; the traded signal is the VWAP/EMA cross.

FIDELITY:

* `vwap(hlc3)` is called with no anchor argument. Pine documents the
  anchor-less form as a SESSION VWAP that restarts at the start of each session,
  so the port uses the same session-VWAP helper convention as the other ports in
  this repository (restart on the first bar of each UTC calendar day). On this
  source's 1d timeframe each bar IS a session, so the modelled `vwap1` is that
  bar's own `hlc3`. This is a modelling choice on an underspecified Pine
  builtin, recorded rather than certified.
* `vwap(hlc3)` is fed `hlc3` explicitly (Pine's own default source for `vwap` is
  also hlc3); the source's argument is kept verbatim.
* The source writes `ema20_uptrend = ema(close, 20) > sma(close[2], 20)` -- the
  right-hand side is an SMA of the two-bars-ago close, not an EMA. That
  asymmetry is in the source, is reproduced as an aside, and is preserved rather
  than "corrected" to EMA-vs-EMA (iron rule 2). It reaches no order in any case.
* `strategy.entry(..., 1, ...)` passes the quantity positionally; the engine
  receives it as an explicit qty so `default_qty_type` is inert for these orders.
* No stop / limit / trail exit exists, so `source_reproduce_stops` is False; a
  position is only ever closed by the opposite `strategy.close` or reversed by
  the opposite entry, and one still open at the window's end stays open.
* `alertcondition` is not trading-related and is ignored
  (PINE_SEMANTICS.md section 2 item 7).
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are unmodelled (PINE_SEMANTICS.md section 2); the chain verifier measures the
  rounding separately.
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMJbravoSwing_30fc81(PinePortBase, IStrategy):
    source_id = "SM_30fc81c0d5b5e82c"
    source_file = "JBravo量化趋势策略JBravo-Quantitative-Trend-Strategy.md"
    timeframe = "1d"
    can_short = True
    # Every input() in the source, with its defval. The first four are
    # display/colour switches read by plot() only; vwapInput is the one that
    # gates the orders.
    source_defaults: dict = {
        "smaInput1": True,
        "smaInput2": True,
        "smaInput4": True,
        "colored_180": False,
        "vwapInput": True,
    }
    # strategy("JBravo Swing", overlay=false) states no sizing, commission or
    # pyramiding, so Pine's documented defaults apply: fixed / 1, 0%, 0, and the
    # default 1000000 initial capital. process_orders_on_close stays false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Only the VWAP-vs-EMA20 cross is traded. `Buy` / `Sell` / `StrongBuy` / "
        "`StrongSell` and the `var buy_in_progress` state machine that feeds "
        "them reach only plotshape/alertcondition -- no strategy.* call reads "
        "them -- so they are not reproduced (they cannot affect an order).",
        "`vwap(hlc3)` is the anchor-less form, modelled as a session VWAP that "
        "restarts on the first bar of each UTC day (the convention used "
        "elsewhere in this repository). On the 1d timeframe each bar is its own "
        "session, so vwap1 reduces to that bar's hlc3. Recorded as a modelling "
        "choice on an underspecified builtin, not a certified equivalence.",
        "Source asymmetry preserved and not 'corrected': `ema20_uptrend` "
        "compares `ema(close, 20)` against `sma(close[2], 20)`. It reaches no "
        "order.",
        "`strategy.entry(..., 1, ...)` passes qty positionally; the port hands "
        "the engine an explicit 1, so the declared default_qty_value is inert.",
        "No stop/limit/trail exit exists: source_reproduce_stops is False and a "
        "position open at the end of the window stays open.",
        "smaInput1/smaInput2/smaInput4/colored_180 are plot() switches only and "
        "change no order; they are carried in source_defaults regardless.",
        "alertcondition() is not trading-related and is ignored "
        "(PINE_SEMANTICS.md section 2 item 7). Leverage/margin/liquidation/"
        "funding and the venue's contract-step rounding are unmodelled.",
    ]

    @staticmethod
    def _session_ids(dataframe: pd.DataFrame) -> pd.Series:
        """Pine `timeframe.change('1D')` grouping key: the UTC calendar day."""
        index = dataframe.index
        if isinstance(index, pd.DatetimeIndex):
            local = index.tz_convert("UTC") if index.tz is not None else index
            return pd.Series(local.normalize(), index=index)
        # No time index: `timeframe.change` cannot be evaluated, and grouping
        # everything into one session is the only behaviour that matches Pine on
        # a symbol with no session definition.
        return pd.Series(0, index=index)

    @classmethod
    def _session_vwap(cls, source: pd.Series, volume: pd.Series,
                      dataframe: pd.DataFrame) -> pd.Series:
        """Running VWAP of `source` that restarts on the first bar of a session."""
        session = cls._session_ids(dataframe)
        cum_pv = (source * volume).groupby(session).cumsum()
        cum_volume = volume.groupby(session).cumsum()
        with np.errstate(divide="ignore", invalid="ignore"):
            vwap = cum_pv / cum_volume
        # Pine returns na when the accumulated volume is zero.
        return vwap.where(cum_volume != 0.0)

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        volume = dataframe["volume"]
        hlc3 = (dataframe["high"] + dataframe["low"] + close) / 3.0

        # Plot-only moving averages, kept so the port reads like the source.
        sma9 = ta.pine_sma(close, 9)
        ema20 = ta.pine_ema(close, 20)
        sma180 = ta.pine_sma(close, 180)

        vwap1 = self._session_vwap(hlc3, volume, dataframe)
        vwaplong = (vwap1 > ema20).fillna(False)
        vwapshort = (vwap1 < ema20).fillna(False)

        dataframe["pine_vwap"] = vwap1
        dataframe["pine_ema20"] = ema20
        dataframe["pine_sma9"] = sma9
        dataframe["pine_sma180"] = sma180
        dataframe["pine_vwaplong"] = vwaplong
        dataframe["pine_vwapshort"] = vwapshort
        return dataframe

    def pine_context(self, dataframe, params):
        vwap_input = bool(params["vwapInput"])
        return {
            # `when = vwaplong and vwapInput` -- both sides of every order.
            "vwaplong": dataframe["pine_vwaplong"].to_numpy() & vwap_input,
            "vwapshort": dataframe["pine_vwapshort"].to_numpy() & vwap_input,
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("GoGo Long", strategy.long, 1, when=vwaplong and vwapInput)
        if ctx["vwaplong"][i]:
            broker.entry("GoGo Long", "long", 1)
        # strategy.entry("GoGo Short", strategy.short, 1, when=vwapshort and vwapInput)
        if ctx["vwapshort"][i]:
            broker.entry("GoGo Short", "short", 1)
        # strategy.close("GoGo Long", when = vwapshort and vwapInput)
        if ctx["vwapshort"][i]:
            broker.close("GoGo Long")
        # strategy.close("GoGo Short", when = vwaplong and vwapInput)
        if ctx["vwaplong"][i]:
            broker.close("GoGo Short")
