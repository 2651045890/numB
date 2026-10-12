"""Port of sources/SM_051df50ead92da5a.pine
(batch_001/CCI强势突破策略CCI-Strong-Breakthrough-Strategy.md).

Pine v5, long only. A mean-reversion entry on a CCI washout, with two market
exits -- a CCI target and a percentage stop measured from the average entry
price:

    src = input(close), length = 20, lossp = 8, scart = 0.25
    upperline = 150, lowline = -150

    ma  = ta.sma(src, length)
    cci = (src - ma) / (0.015 * ta.dev(src, length))

    window() => time >= timestamp(2016,1,1,0,0) and time <= timestamp(2112,1,1,23,59)

    scart_level = open * (1 + scart/100)
    entryl = cci[1] < lowline[1] and cci > cci[1] and close > scart_level and window()
    exit1  = cci > upperline

    strategy.entry('Long', strategy.long, when=entryl)
    strategy.close('Long', when=exit1, comment='target')

    losspel = strategy.position_avg_price * (1 - lossp/100)
    fixed_stop_long = close < losspel
    strategy.close('Long', when=fixed_stop_long, comment='Stop Loss')

`ta.dev` is not in pine_ta, so it is implemented here from its Pine definition:
`ta.dev(source, length) = ta.sma(math.abs(source - ta.sma(source, length)), length)`.
It is NOT substituted by `ta.stdev`, which is a different statistic (Pine's
`ta.dev` is the mean absolute deviation; `ta.stdev` is the population standard
deviation) and would change every CCI value.

Both exits are `strategy.close`, i.e. market orders -- the source has no stop,
limit or trail leg -- so `source_reproduce_stops` is False, even though the
second exit is named "Stop Loss".

`strategy()` declares only `title` and `overlay=false`, so every other property
is Pine's documented default: `fixed` sizing of 1 contract, 0% commission,
`pyramiding = 0`, initial capital 1000000.

The /*backtest header declares `period: 1d` on Futures_Binance BTC_USDT, hence
`timeframe = "1d"` (its `basePeriod: 1h` is the FMZ backtester's intrabar fill
granularity, not the strategy's period).

FIDELITY -- translation choices and source/original mismatches:

1. MD vs SOURCE, entry trigger. The md's prose says the entry fires when "CCI
   下穿低线并开始上涨" (CCI crosses BELOW the low line and starts rising). The
   source's `cci[1] < lowline[1]` requires only that the PREVIOUS bar sat below
   the line; it is a level test, not a crossunder. The port follows the source.
2. MD vs SOURCE, exit trigger. The md calls exit 1 "CCI上穿上线" (CCI crosses the
   upper line); the source's `exit1 = cci > upperline` is a plain level test.
   The port follows the source.
3. `lowline[1]` is a `[1]` reference to an `input.int` constant, so it equals
   `lowline` on every bar. The port uses the constant directly and keeps the
   comparison as `cci[1] < lowline`. Behaviour is identical; the subscript is
   noted rather than reproduced because it has no effect.
4. `window()` is evaluated from the date inputs but cannot filter anything in
   practice: the window opens 2016-01-01 and closes 2112-01-01, so every bar of
   any real history is inside it. It is reproduced as a real comparison rather
   than dropped, so an override of the date inputs still behaves as the source
   would. The timestamps are built in UTC; the boundary is 85 years away from
   the local history, so the exchange-timezone question (Pine_SEMANTICS.md 3.4)
   cannot change any bar's membership here.
5. The md's argument table renders the month/day inputs as `true` (FMZ's bool
   column showing the integer 1) and lists `v_input_1_close` with default `0`
   for a source selector whose options are close/high/low/open/hl2/hlc3/hlcc4/
   ohlc4. The source's own defaults are used here: `src = close`, and the
   integer 1 for the four month/day fields.
6. `strategy.position_avg_price` is na while flat, and a comparison against na
   is falsy in Pine. The port therefore computes `close < position_avg_price *
   (1 - lossp/100)` directly against the broker's own `position_avg_price`
   (which is nan when flat), with no added guard -- the same shape the source
   has, so no extra branch can suppress a stop the source would have taken.
7. Order of the three calls is preserved verbatim: entry, then the CCI-target
   close, then the stop-loss close. Both closes are market exits and both use
   the id 'Long'.
8. `ta.dev`'s NaNs propagate through `ta.sma`'s window (Pine_SEMANTICS.md 3.2),
   so `cci` is na until 2*length-1 bars have elapsed (sma warm-up at `length`,
   then the absolute deviation's own sma warm-up). No entries can fire before
   then, because a comparison with na is falsy.
9. hline()/fill()/plot() are display-only and are not reproduced.
10. Leverage, margin, liquidation, funding and the venue's contract-step
    rounding are not modelled; the chain verifier measures the step rounding
    separately instead of treating it as a signal difference.
"""
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMCciStrongBreakthrough_051df5(PinePortBase, IStrategy):
    source_id = "SM_051df50ead92da5a"
    source_file = "CCI强势突破策略CCI-Strong-Breakthrough-Strategy.md"
    timeframe = "1d"
    # Long only. There is no `strategy.entry(..., strategy.short)` anywhere in
    # the source -- the title says so outright ("long only").
    can_short = False
    source_defaults: dict = {
        # input(close) -- Pine's `input.source`, whose default is the close series.
        "src": "close",
        # input.int(20, title='Period', minval=1)
        "length": 20,
        # input.float(8, title='Stop Loss percentage', minval=0.5, step=0.5)
        "lossp": 8.0,
        # input.float(0.25, title='Close of the signal bar higher than Open %', minval=0)
        "scart": 0.25,
        # input.int(150, title='Upper Band', minval=0, step=10)
        "upperline": 150,
        # input.int(-150, title='Low Band', maxval=0, step=10)
        "lowline": -150,
        # input.int(1, "From Month"), input.int(1, "From Day"),
        # input.int(2016, "From Year"), input.int(1, "Thru Month"),
        # input.int(1, "Thru Day"), input.int(2112, "Thru Year")
        "fromMonth": 1,
        "fromDay": 1,
        "fromYear": 2016,
        "thruMonth": 1,
        "thruDay": 1,
        "thruYear": 2112,
    }
    # strategy(title='CCI High Performance long only', overlay=false): title and
    # overlay only, so Pine's documented defaults apply -- fixed / 1 contract,
    # 0% commission, pyramiding 0, initial capital 1000000.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop / limit / trail leg exists: both exits are market strategy.close
    # calls, including the one commented 'Stop Loss' and driven by a percentage.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "MD/SOURCE MISMATCH (entry): the md says the entry needs CCI to CROSS "
        "BELOW the low line; the source only requires the previous bar to be "
        "below it (`cci[1] < lowline[1]`). The source is followed.",
        "MD/SOURCE MISMATCH (exit 1): the md says CCI crosses the upper line; "
        "the source is a plain level test (`cci > upperline`). The source is "
        "followed.",
        "ta.dev is not in pine_ta and is implemented here from its Pine "
        "definition sma(abs(src - sma(src, length)), length). It is NOT "
        "ta.stdev -- that is a different statistic and would change every CCI.",
        "`lowline[1]` is a history reference to an input constant; it equals "
        "lowline on every bar, so the port compares against the constant.",
        "window() is reproduced from the six date inputs, but its bounds "
        "(2016-01-01 .. 2112-01-01) contain any real history, so it filters "
        "nothing. Kept so an override of those inputs still behaves as the "
        "source would. Timestamps are built in UTC; the 85-year margin makes "
        "the exchange-timezone question moot here.",
        "The md's argument table shows `true` for the month/day inputs (FMZ's "
        "bool column rendering the integer 1) and `0` for the src selector; the "
        "source's real defaults (1s, and close) are declared here.",
        "strategy.position_avg_price is na while flat and a comparison with na "
        "is falsy in Pine, so the port compares against the broker's own "
        "position_avg_price (nan when flat) with no extra guard.",
        "Call order preserved: entry, then the CCI-target close, then the "
        "stop-loss close. Both closes are market exits on the id 'Long'.",
        "ta.dev's na propagates through ta.sma's window, so cci is na until "
        "2*length-1 bars have elapsed; no entry can fire before that.",
        "hline/fill/plot are display-only and are not reproduced.",
    ]

    def pine_indicators(self, dataframe, params):
        src = ta.pine_source(dataframe, str(params["src"]))
        length = int(params["length"])
        # ma = ta.sma(src, length)
        ma = ta.pine_sma(src, length)
        # cci = (src - ma) / (0.015 * ta.dev(src, length))
        # ta.dev(source, length) = sma(abs(source - sma(source, length)), length)
        dev = ta.pine_sma((src - ma).abs(), length)
        cci = (src - ma) / (0.015 * dev)
        dataframe["pine_cci"] = cci
        dataframe["pine_cci_prev"] = cci.shift(1)

        # window() => time >= start and time <= finish ? true : false
        index = dataframe.index
        tz = getattr(index, "tz", None)
        start = pd.Timestamp(
            f"{int(params['fromYear']):04d}-{int(params['fromMonth']):02d}-"
            f"{int(params['fromDay']):02d} 00:00:00",
            tz=tz,
        )
        finish = pd.Timestamp(
            f"{int(params['thruYear']):04d}-{int(params['thruMonth']):02d}-"
            f"{int(params['thruDay']):02d} 23:59:00",
            tz=tz,
        )
        in_window = (index >= start) & (index <= finish)

        # scart_level = open * (1 + scart/100)
        scart_level = dataframe["open"] * (1.0 + float(params["scart"]) / 100.0)
        # entryl = cci[1] < lowline[1] and cci > cci[1] and close > scart_level and window()
        dataframe["pine_enter"] = (
            (dataframe["pine_cci_prev"] < float(params["lowline"]))
            & (cci > dataframe["pine_cci_prev"])
            & (dataframe["close"] > scart_level)
            & in_window
        )
        # exit1 = cci > upperline
        dataframe["pine_exit_target"] = cci > float(params["upperline"])
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "enter": dataframe["pine_enter"].to_numpy(dtype=bool),
            "exit_target": dataframe["pine_exit_target"].to_numpy(dtype=bool),
            "lossp": float(params["lossp"]),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry('Long', strategy.long, when=entryl)
        if ctx["enter"][i]:
            broker.entry("Long", "long")

        # strategy.close('Long', when=exit1, comment='target')
        if ctx["exit_target"][i]:
            broker.close("Long", comment="target")

        # losspel = strategy.position_avg_price * (1 - lossp / 100)
        # fixed_stop_long = close < losspel
        # strategy.close('Long', when=fixed_stop_long, comment='Stop Loss')
        # The source has no na guard: position_avg_price is na while flat and
        # `close < na` is falsy in Pine, which is what `nan` does in Python too.
        losspel = broker.position_avg_price * (1.0 - ctx["lossp"] / 100.0)
        if bool(ctx["close"][i] < losspel):
            broker.close("Long", comment="Stop Loss")
