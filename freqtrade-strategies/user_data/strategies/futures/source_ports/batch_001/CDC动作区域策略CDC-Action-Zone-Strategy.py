"""Port of sources/SM_2d2bd192e4423ebe.pine (batch_001/CDC动作区域策略CDC-Action-Zone-Strategy.md).

Pine v4. `strategy("CDC Action Zone [TS Trader]", overlay=true)` declares no
sizing, no commission and no pyramiding, so every one of those stays at Pine's
documented default (see the declared attributes below).

The indicator is two chained exponential smoothings of a selectable source:

    src   = ohlc4                     (input.source, defval=ohlc4)
    AP    = ema(src, 2)
    Fast  = ema(AP, prd1)             prd1 = 12
    Slow  = ema(AP, prd2)             prd2 = 26
    Bullish = Fast > Slow
    Bearish = Fast < Slow
    Green = Bullish and AP > Fast
    Red   = Bearish and AP < Fast

and the two signals are the FIRST bar of a colour run, not every bar of it:

    Buy  = Green and Green[1] == 0
    Sell = Red   and Red[1]   == 0

`Green[1] == 0` is a v4 bool-in-numeric-context test -- it is true when the
PREVIOUS bar was not Green (Pine's `bool` is 1/0 there). Note this is the `== 0`
form, not the `!= 0` form of PINE_SEMANTICS.md 1.16: Python and numpy agree with
Pine on `== 0` for both a bool and an int, so a direct translation is correct
here. On bar 0 the history reference is `na`, and Pine treats `na == 0` as false,
which `Series.shift(1)` reproduces as NaN (and NaN == 0 is False).

Both entries and both closes are guarded by `window()`, which the source defines
as the literal `true`; the From/To date inputs are computed into `start` and
`finish` and then never used, so they place no restriction on the orders.

    strategy.entry("Buy",  strategy.long,  when = window() and Buy)
    strategy.entry("Sell", strategy.short, when = window() and Sell)
    strategy.close("Buy",  when = window() and Sell)
    strategy.close("Sell", when = window() and Buy)

`Buy` and `Sell` are mutually exclusive (`Green` and `Red` cannot both hold), so
a reversal is always a close followed by an entry on the SAME bar for the
opposite side, and the engine settles both on the next bar's open in source
order. `Short` and `Cover` are computed in the source but never called; they are
not reproduced.

FIDELITY:

* `prd1` / `prd2` are the source's own `input()` lengths; the `ema` is Pine's,
  whose seeding rule TradingView does not publish -- `pine_ta.pine_ema` seeds
  with the first non-na observation and na does not advance the recursion
  (PINE_SEMANTICS.md 3.1). The port keeps whatever that shared choice is; it is
  not re-decided here.
* The port does not re-time orders: signals are evaluated at the bar close and
  the engine fills on the next bar's open, matching Pine.
* There is no stop / limit / trail exit anywhere in the source, so
  `source_reproduce_stops` is False: a position is only ever closed by the
  opposite-side `strategy.close`, and one still open at the end of the window
  stays open.
* `Short` / `Cover` and the `plot` / `barcolor` / `fill` calls are display-only
  and are not reproduced.
* `lowest`/`highest` and leverage/margin/liquidation/funding are not modelled by
  the shared engine (PINE_SEMANTICS.md section 2); the venue's contract-step
  rounding is measured separately by the chain verifier rather than reproduced.
* The md's own `v_input_*` table renders `From Month` and `From Day` as `true`;
  the SOURCE declares `defval = 1` for both. The source is authoritative and the
  port carries 1. Neither value can affect an order, because `window()` returns
  `true` unconditionally.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMCdcActionZone_2d2bd1(PinePortBase, IStrategy):
    source_id = "SM_2d2bd192e4423ebe"
    source_file = "CDC动作区域策略CDC-Action-Zone-Strategy.md"
    timeframe = "1d"
    can_short = True
    # Every input() in the source, with its defval. `src` is an input.source
    # (defval=ohlc4) and is carried as the source name the pine_ta helper
    # resolves; the From/To window inputs are inert (`window()` is `true`).
    source_defaults: dict = {
        "src": "ohlc4",
        "prd1": 12,
        "prd2": 26,
        "FromYear": 2019,
        "FromMonth": 1,
        "FromDay": 1,
        "ToYear": 9999,
        "ToMonth": 12,
        "ToDay": 31,
    }
    # strategy("CDC Action Zone [TS Trader]", overlay=true) states none of these,
    # so Pine's documented defaults apply: fixed / 1 contract, commission 0%,
    # pyramiding 0, process_orders_on_close=false, initial capital 1000000.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`Green[1] == 0` is Pine v4's bool-as-number test for 'the previous bar "
        "was not Green'. It is the `== 0` form, which Python/numpy evaluate "
        "identically for bool and for int, so it is translated directly; the "
        "`!= 0` trap of PINE_SEMANTICS.md 1.16 does not apply to it. On bar 0 "
        "the reference is na and Pine reads `na == 0` as false, which the port "
        "reproduces with `shift(1)` (NaN == 0 is False).",
        "`window()` is defined as `true`; the From/To inputs feed `start` and "
        "`finish`, which no order reads. They are carried in source_defaults "
        "for completeness but place no restriction on any order.",
        "`Short = Red and Red[1] == 0` and `Cover = Red[1] and Red == 0` are "
        "computed in the source and never passed to any strategy.* call; they "
        "are not reproduced (they are dead code with respect to orders).",
        "No stop/limit/trail exit exists in the source: `source_reproduce_stops` "
        "is False and a position open at the window's end stays open.",
        "`ema` seeding follows the shared PINE_SEMANTICS.md 3.1 modelling choice "
        "(first non-na observation seeds the recursion); it is not re-decided "
        "per port.",
        "plot / barcolor / fill are display-only. Leverage, margin, liquidation "
        "and funding are unmodelled (PINE_SEMANTICS.md section 2).",
        "md/source divergence recorded, not acted on: the md's v_input table "
        "renders `From Month` and `From Day` as `true`, where the source "
        "declares `defval = 1` for both. The md's pinescript block is otherwise "
        "byte-identical to the extracted source. Neither value can affect an "
        "order (`window()` is `true`).",
    ]

    def pine_indicators(self, dataframe, params):
        src = ta.pine_source(dataframe, params["src"])
        ap = ta.pine_ema(src, 2)
        fast = ta.pine_ema(ap, int(params["prd1"]))
        slow = ta.pine_ema(ap, int(params["prd2"]))

        bullish = fast > slow
        bearish = fast < slow
        green = bullish & (ap > fast)
        red = bearish & (ap < fast)

        # Buy = Green and Green[1] == 0 / Sell = Red and Red[1] == 0. `astype`
        # to float first so the history reference is a plain value, with NaN
        # standing in for Pine's `na` (and `NaN == 0` being False, as Pine's
        # `na == 0` is).
        buy = green & (green.astype(float).shift(1) == 0.0)
        sell = red & (red.astype(float).shift(1) == 0.0)

        dataframe["pine_ap"] = ap
        dataframe["pine_fast"] = fast
        dataframe["pine_slow"] = slow
        dataframe["pine_green"] = green
        dataframe["pine_red"] = red
        dataframe["pine_buy"] = buy.fillna(False)
        dataframe["pine_sell"] = sell.fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy": dataframe["pine_buy"].to_numpy(),
            "sell": dataframe["pine_sell"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Buy", strategy.long, when=window() and Buy)
        if ctx["buy"][i]:
            broker.entry("Buy", "long")
        # strategy.entry("Sell", strategy.short, when=window() and Sell)
        if ctx["sell"][i]:
            broker.entry("Sell", "short")
        # strategy.close("Buy", when=window() and Sell)
        if ctx["sell"][i]:
            broker.close("Buy")
        # strategy.close("Sell", when=window() and Buy)
        if ctx["buy"][i]:
            broker.close("Sell")
