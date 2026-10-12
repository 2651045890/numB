"""Port of sources/SM_dbe2ef2667c14d7a.pine (batch_001/K线形态策略Candlestick-Patterns-Strategy.md).

Pine v2 candlestick-pattern strategy. Nineteen classic patterns are each
encoded as one boolean expression over open/high/low/close with history
offsets up to `[4]`; eleven of them are bullish and eight bearish. Each
pattern is gated by its own `input(type=bool)` and the gated value is
`condition ? OnX : na`, so a disabled pattern contributes nothing:

    bullish_engulfing = high>high[1] and low<low[1] and open<open[1] and
                        close>close[1] and close>open and close[1]<close[2] and
                        close>open[1] ? OnEngulfing : na
    ... (18 more, see pine_indicators)

    SignalUp   = bullish_engulfing or bullish_harami or piercing_line or
                 morning_star or bullish_belt_hold or three_white_soldiers or
                 three_stars_in_the_south or stick_sandwich or bullish_ml or
                 bullish_kicking or ladder_bottom
    SignalDown = bearish_engulfing or bearish_harami or dark_cloud_cover or
                 evening_star or bearish_belt_hold or three_black_crows or
                 bearish_ml or bearish_kicking

    strategy.entry("long",  true,  when = SignalUp   and session_open)
    strategy.entry("short", false, when = SignalDown and session_open)
    strategy.close("long",  when = not session_open)
    strategy.close("short", when = not session_open)
    strategy.exit("Risk Exit long",  from_entry="long",  profit=tp, trail_points=trail, loss=sl)
    strategy.exit("Risk Exit short", from_entry="short", profit=tp, trail_points=trail, loss=sl)

Every `input()` default is carried in `source_defaults` verbatim: the eleven
pattern switches default true, and the risk inputs default to 70 (stop), 1000
(take profit) and 30 (trailing activation) -- the source converts each to na
below 1, which is what `_na_below_one` reproduces.

`strategy()` declares only `title`, `shorttitle` and `overlay`, so Pine's
documented defaults apply: `default_qty_type = fixed`, `default_qty_value = 1`,
`commission_value = 0`, `pyramiding = 0`, initial capital 1000000 and
`process_orders_on_close = false`. The `/*backtest` header declares
`period: 2h` on Futures_Binance BTC_USDT, so `timeframe` is "2h"; its
`basePeriod: 15m` is the FMZ backtester's own intrabar granularity, not the
strategy's period.

FIDELITY:

* `session_open` is the literal `true` on the line after the session lookup,
  and the `t = time(timeframe.period, sess)` value is never read. The port
  therefore holds `session_open` as a constant true, which makes both
  `strategy.close(...)` calls (`when = not session_open`) permanent no-ops.
  They are still issued, in source order, with `when=False`.
* `sess` ("0000-0000") is an input but reaches no decision, so it is carried in
  `source_defaults` for completeness and is otherwise unused.
* Each pattern is `cond ? OnX : na`; the `or` chain over a mixture of true,
  false and na is reproduced as `any(gated condition)`, which is what the
  chain yields when na is read as false in a boolean context -- the reading
  both Pine v2 and the `when=` parameter use. Under the alternative reading
  (`na or x` staying na) the result would be na rather than false, and `when`
  is false for na either way, so no order changes.
* `sl` / `tp` are tick distances handed to `strategy.exit(profit=..., loss=...)`
  as the source writes them, in ticks; the engine converts them against
  `source_mintick`. The source never states a mintick -- TradingView reads it
  off the symbol -- so the shared default for BTC/USDT:USDT (0.1) is used, and
  the resulting levels are entry +/- 7.0 (loss 70 ticks) and entry + 100.0
  (profit 1000 ticks).
* `trail_points = 30` is passed through as the source writes it. The source
  gives no `trail_offset`, and the engine only evaluates a trailing leg when
  both are present (`pine_engine._exit_fill`), so the trail is inert here: the
  resting exit is the stop/profit pair. Pine's own behaviour for
  `trail_points` without `trail_offset` is not stated in the source and is not
  guessed at -- it is recorded, not "corrected".
* The trailing leg is also not reproducible through the framework for the
  reason in PINE_SEMANTICS §二-9(a): a trail that arms and triggers inside one
  bar has no publishable level. That does not bite here, because the leg is
  inert in the engine as well.
* The exits are re-placed on every bar, which is Pine's usual shape and what the
  engine models as same-id replacement (PINE_SEMANTICS §3.6). With no
  `trail_offset` there is no ratchet state to lose.
* `plotshape` and the pattern text labels are display-only and are not
  reproduced.
* Contract-step rounding, leverage, margin, liquidation and funding are not
  modelled (PINE_SEMANTICS §1.6, §二-4).
"""
import pandas as pd

from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


def _na_below_one(value):
    """Pine `x >= 1 ? x : na` -- a disabled risk leg is na, not zero."""
    value = float(value)
    return value if value >= 1 else None


class SMCandlestickPatterns_dbe2ef(PinePortBase, IStrategy):
    source_id = "SM_dbe2ef2667c14d7a"
    source_file = "K线形态策略Candlestick-Patterns-Strategy.md"
    timeframe = "2h"
    can_short = True
    source_defaults: dict = {
        "OnEngulfing": True,
        "OnHarami": True,
        "OnPiercingLine": True,
        "OnMorningStar": True,
        "OnBeltHold": True,
        "OnThreeWhiteSoldiers": True,
        "OnThreeStarsInTheSouth": True,
        "OnStickSandwich": True,
        "OnMeetingLine": True,
        "OnKicking": True,
        "OnLadderBottom": True,
        "inpsl": 70,
        "inptp": 1000,
        "inptrail": 30,
        "sess": "0000-0000",
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "`session_open` is a literal `true`; the `time()` lookup above it is "
        "never read, so `strategy.close(...) when = not session_open` can never "
        "fire. Both closes are issued with when=False, in source order.",
        "The `sess` input reaches no decision and is carried only for "
        "completeness.",
        "Each pattern is `cond ? OnX : na`; the or-chain is reproduced as "
        "any(gated condition), i.e. na read as false -- the reading shared by "
        "Pine v2 booleans and the `when=` parameter. No order differs under the "
        "alternative reading.",
        "`profit` / `loss` are tick distances as written in the source; the "
        "engine converts them with source_mintick. The source states no mintick "
        "(TradingView reads it from the symbol), so the BTC/USDT:USDT default "
        "0.1 is used: loss 70 ticks = 7.0, profit 1000 ticks = 100.0.",
        "`trail_points = 30` is passed through but the source supplies no "
        "`trail_offset`, and the engine only evaluates a trailing leg when both "
        "are given -- so the trail is inert and the resting exit is the "
        "stop/profit pair. Pine's behaviour for trail_points without "
        "trail_offset is not stated and is not guessed at.",
        "The exits are re-placed every bar (Pine's same-id replacement, "
        "PINE_SEMANTICS §3.6). With no trail_offset there is no ratchet state "
        "to lose.",
        "strategy() declares only title/shorttitle/overlay, so Pine's defaults "
        "apply: qty_type fixed, qty_value 1, commission 0, pyramiding 0, "
        "initial capital 1000000, process_orders_on_close false.",
        "The header's `basePeriod: 15m` asks the platform for 15m intrabar "
        "fills; the engine resolves every order against the 2h bar alone.",
        "plotshape/text labels are display-only and are not reproduced.",
        "Contract-step rounding, leverage, margin, liquidation, funding and "
        "intrabar path (PINE_SEMANTICS §1.6, §二-2, §二-4) are not modelled.",
    ]

    # ---- patterns ---------------------------------------------------------
    @staticmethod
    def _patterns(df: pd.DataFrame) -> dict[str, pd.Series]:
        """The nineteen pattern expressions, exactly as the source writes them.

        Pine's `[n]` is `shift(n)`; a comparison against an na operand is false,
        which is what a pandas comparison against NaN yields as well.
        """
        o, h, l, c = (df["open"], df["high"], df["low"], df["close"])
        o1, h1, l1, c1 = o.shift(1), h.shift(1), l.shift(1), c.shift(1)
        o2, h2, l2, c2 = o.shift(2), h.shift(2), l.shift(2), c.shift(2)
        o3, c3 = o.shift(3), c.shift(3)
        o4, l4 = o.shift(4), l.shift(4)
        l3, c4 = l.shift(3), c.shift(4)
        out = {}
        out["bullish_engulfing"] = (
            (h > h1) & (l < l1) & (o < o1) & (c > c1) & (c > o) & (c1 < c2) & (c > o1)
        )
        out["bearish_engulfing"] = (
            (h > h1) & (l < l1) & (o > o1) & (c < c1) & (c < o) & (c1 > c2) & (c < o1)
        )
        out["bullish_harami"] = (
            (o1 > c1) & (c1 < c2) & (o > c1) & (o < o1) & (c > c1) & (c < o1)
            & (h < h1) & (l > l1) & (c >= o)
        )
        out["bearish_harami"] = (
            (o1 < c1) & (c1 > c2) & (o < c1) & (o > o1) & (c < c1) & (c > o1)
            & (h < h1) & (l > l1) & (c <= o)
        )
        # avg(open[1], close[1]) is Pine's two-argument avg.
        out["piercing_line"] = (
            (c2 > c1) & (o < l1) & (c > (o1 + c1) / 2.0) & (c < o1)
        )
        out["dark_cloud_cover"] = (
            (c2 < c1) & (o > h1) & (c < (o1 + c1) / 2.0) & (c > o1)
        )
        out["morning_star"] = (
            (c3 > c2) & (c2 < o2) & (o1 < c2) & (c1 < c2) & (o > o1) & (o > c1)
            & (c > c2) & ((o2 - c2) > (c - o))
        )
        out["evening_star"] = (
            (c3 < c2) & (c2 > o2) & (o1 > c2) & (c1 > c2) & (o < o1) & (o < c1)
            & (c < c2) & ((c2 - o2) > (o - c))
        )
        out["bullish_belt_hold"] = (
            (c1 < o1) & (l1 > o) & (c1 > o) & (o == l) & (c > (c + o) / 2.0)
        )
        out["bearish_belt_hold"] = (
            (c1 > o1) & (h1 < o) & (c1 < o) & (o == h) & (c < (c + o) / 2.0)
        )
        out["three_white_soldiers"] = (
            (c3 < o3) & (o2 < c3) & (c2 > (c2 + o2) / 2.0) & (o1 > o2) & (o1 < c2)
            & (c1 > (c1 + o1) / 2.0) & (o > o1) & (o < c1) & (c > (c + o) / 2.0)
            & (h1 > h2) & (h > h1)
        )
        out["three_black_crows"] = (
            (c3 > o3) & (o2 > c3) & (c2 < (c2 + o2) / 2.0) & (o1 < o2) & (o1 > c2)
            & (c1 < (c1 + o1) / 2.0) & (o < o1) & (o > c1) & (c < (c + o) / 2.0)
            & (l1 < l2) & (l < l1)
        )
        out["three_stars_in_the_south"] = (
            (o3 > c3) & (o2 > c2) & (o2 == h2) & (o1 > c1) & (o1 < o2) & (o1 > c2)
            & (l1 > l2) & (o1 == h1) & (o > c) & (o < o1) & (o > c1) & (o == h)
            & (c == l) & (c >= l1)
        )
        out["stick_sandwich"] = (
            (o2 > c2) & (o1 > c2) & (o1 < c1) & (o > c1) & (o > c) & (c == c2)
        )
        out["bullish_ml"] = (
            (o2 > c2) & (o1 > c1) & (c1 == c) & (o < c) & (o1 >= h)
        )
        out["bearish_ml"] = (
            (o2 < c2) & (o1 < c1) & (c1 == c) & (o > c) & (o1 <= l)
        )
        out["bullish_kicking"] = (
            (o1 > c1) & (o1 == h1) & (c1 == l1) & (o > o1) & (o == l) & (c == h)
            & ((c - o) > (o1 - c1))
        )
        out["bearish_kicking"] = (
            (o1 < c1) & (o1 == l1) & (c1 == h1) & (o < o1) & (o == h) & (c == l)
            & ((o - c) > (c1 - o1))
        )
        out["ladder_bottom"] = (
            (o4 > c4) & (o3 > c3) & (o3 < o4) & (o2 > c2) & (o2 < o3) & (o1 > c1)
            & (o1 < o2) & (o < c) & (o > o1) & (l4 > l3) & (l3 > l2) & (l2 > l1)
        )
        return out

    def pine_indicators(self, dataframe, params):
        patterns = self._patterns(dataframe)
        # `cond ? OnX : na` -- the switch turns the pattern on or off entirely.
        gated = {
            name: patterns[name] & bool(params[switch])
            for name, switch in (
                ("bullish_engulfing", "OnEngulfing"),
                ("bearish_engulfing", "OnEngulfing"),
                ("bullish_harami", "OnHarami"),
                ("bearish_harami", "OnHarami"),
                ("piercing_line", "OnPiercingLine"),
                ("dark_cloud_cover", "OnPiercingLine"),
                ("morning_star", "OnMorningStar"),
                ("evening_star", "OnMorningStar"),
                ("bullish_belt_hold", "OnBeltHold"),
                ("bearish_belt_hold", "OnBeltHold"),
                ("three_white_soldiers", "OnThreeWhiteSoldiers"),
                ("three_black_crows", "OnThreeWhiteSoldiers"),
                ("three_stars_in_the_south", "OnThreeStarsInTheSouth"),
                ("stick_sandwich", "OnStickSandwich"),
                ("bullish_ml", "OnMeetingLine"),
                ("bearish_ml", "OnMeetingLine"),
                ("bullish_kicking", "OnKicking"),
                ("bearish_kicking", "OnKicking"),
                ("ladder_bottom", "OnLadderBottom"),
            )
        }
        for name, series in gated.items():
            dataframe[f"pine_{name}"] = series.fillna(False).astype(bool)

        signal_up = gated["bullish_engulfing"]
        for name in ("bullish_harami", "piercing_line", "morning_star",
                     "bullish_belt_hold", "three_white_soldiers",
                     "three_stars_in_the_south", "stick_sandwich", "bullish_ml",
                     "bullish_kicking", "ladder_bottom"):
            signal_up = signal_up | gated[name]
        signal_down = gated["bearish_engulfing"]
        for name in ("bearish_harami", "dark_cloud_cover", "evening_star",
                     "bearish_belt_hold", "three_black_crows", "bearish_ml",
                     "bearish_kicking"):
            signal_down = signal_down | gated[name]
        dataframe["pine_signal_up"] = signal_up.fillna(False).astype(bool)
        dataframe["pine_signal_down"] = signal_down.fillna(False).astype(bool)

        # sl = inpsl >= 1 ? inpsl : na  (and the same for tp / trail)
        for column, name in (("pine_sl", "inpsl"), ("pine_tp", "inptp"),
                             ("pine_trail", "inptrail")):
            value = float(params[name])
            dataframe[column] = value if value >= 1 else float("nan")
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "signal_up": dataframe["pine_signal_up"].to_numpy(),
            "signal_down": dataframe["pine_signal_down"].to_numpy(),
            "sl": dataframe["pine_sl"].to_numpy(),
            "tp": dataframe["pine_tp"].to_numpy(),
            "trail": dataframe["pine_trail"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # session_open = true, so `not session_open` is constantly false.
        session_open = True

        # strategy.entry("long", true, when = SignalUp and session_open)
        if ctx["signal_up"][i] and session_open:
            broker.entry("long", "long")
        # strategy.entry("short", false, when = SignalDown and session_open)
        if ctx["signal_down"][i] and session_open:
            broker.entry("short", "short")
        # strategy.close("long", when = not session_open)   -- never fires
        broker.close("long", when=not session_open)
        # strategy.close("short", when = not session_open)  -- never fires
        broker.close("short", when=not session_open)
        # strategy.exit("Risk Exit long", from_entry="long", profit=tp,
        #               trail_points=trail, loss=sl)
        broker.exit(
            "Risk Exit long",
            from_entry="long",
            profit=_na_below_one(ctx["tp"][i]),
            trail_points=_na_below_one(ctx["trail"][i]),
            loss=_na_below_one(ctx["sl"][i]),
        )
        # strategy.exit("Risk Exit short", from_entry="short", profit=tp,
        #               trail_points=trail, loss=sl)
        broker.exit(
            "Risk Exit short",
            from_entry="short",
            profit=_na_below_one(ctx["tp"][i]),
            trail_points=_na_below_one(ctx["trail"][i]),
            loss=_na_below_one(ctx["sl"][i]),
        )
