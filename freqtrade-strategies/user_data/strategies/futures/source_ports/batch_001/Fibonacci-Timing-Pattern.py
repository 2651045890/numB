"""Port of sources/SM_bf4b34187066cf16.pine (batch_001/Fibonacci-Timing-Pattern.md).

Pine v5. The file declares an INDICATOR -- `indicator("Fibonacci Timing
Pattern", overlay = true)` -- and a converter tool appended an order block to
it (PINE_SEMANTICS.md 1.17). Pine v5 does not compile `strategy.entry` inside
an `indicator()`, so the "original strategy" is the indicator PLUS the appended
block, and the trading behaviour it defines is entry-only:

    if FB_Buy
       strategy.entry("buy", strategy.long)
    else if  FB_Sell
        strategy.entry("sell", strategy.short)

The indicator itself is Sofien-Kaabar's FB timing pattern: a 13-term nested
comparison of the close against its own lags 3..12, checking that price has
stepped DOWN over the last several bars (FB_Buy) or UP (FB_Sell):

    FB_Buy  = close < close[3] and close < close[5]
              and close[1] < close[4] and close[1] < close[6]
              and close[2] < close[5] and close[2] < close[7]
              and close[3] < close[6] and close[3] < close[8]
              and close[4] < close[7] and close[4] < close[9]
              and close[5] < close[8] and close[5] < close[10]
              and close[6] < close[9] and close[6] < close[11]
              and close[7] < close[10] and close[7] < close[12]
              and close[8] > close[11]
    FB_Sell = the same with every operator flipped (all > except the last <)

The last term is inverted relative to the others: `close[8] > close[11]` for
the buy setup, `close[8] < close[11]` for the sell setup.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, and not even a commented-out one. A position is therefore
only ever left by the opposite entry, which the engine models as a reversal.
`pyramiding` keeps Pine's default of 0, so a repeated signal while already
positioned that way is ignored.

FIDELITY:

* The two `if FB_Buy == true and FB_Buy[1] == true` blocks are DEAD CODE and
  are reproduced as such. Their body is `FB_Buy == false` / `FB_Sell == false`
  -- a COMPARISON expression, not an assignment (`:=`), so it evaluates to a
  bool and discards it. Neither FB_Buy nor FB_Sell is modified by the block,
  and the block's own condition is not used to place an order either. The
  `FB_Buy[1]` / `FB_Sell[1]` history reads are modelled as one-bar lags and
  kept as ledger columns so the formula is on the record; nothing reads them.
* Every comparison is a shift against the close, so on the first 12 bars the
  lagged operands are na and Pine evaluates the comparison as false; the
  pandas comparison does the same, and the port fills the na with False before
  the scripts read it.
* `strategy.entry` is called with no `qty`, so the engine sizes it from
  `default_qty_type` / `default_qty_value`. The source declares `indicator()`,
  not `strategy()`, so Pine's documented defaults apply: fixed size 1, 0%
  commission, pyramiding 0, initial capital 1000000 USD.
* `plotshape(...)` is display-only and places no order; dropped.
* MD-vs-SOURCE: the md front matter names the author as "Zer3192", the file's
  own header reads "(c) Sofien-Kaabar". The md records the fmz uploader, the
  source the original indicator author. No effect on behaviour; recorded, not
  reconciled. The md's embedded source block is verbatim identical to the
  .pine source.
* The header's backtest window (2021-05-08 to 2022-05-07) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. The header's
  `basePeriod: 15m` is the host's intrabar granularity for filling 4h bars,
  not the strategy's period; the header's `period: 4h` is what `timeframe`
  uses.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled (PINE_SEMANTICS.md 1.6 measures that separately).
"""
import pandas as pd
from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


class SMFibonacciTimingPattern_bf4b34(PinePortBase, IStrategy):
    source_id = "SM_bf4b34187066cf16"
    source_file = "Fibonacci-Timing-Pattern.md"
    timeframe = "4h"
    can_short = True
    # No input() call exists anywhere in the source.
    source_defaults: dict = {}
    # indicator(...), not strategy(...): Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "Converter-appended source: the file declares an indicator "
        "(`indicator(\"Fibonacci Timing Pattern\", overlay = true)`) and the "
        "tool appended `if FB_Buy / strategy.entry(\"buy\", strategy.long) "
        "else if FB_Sell / strategy.entry(\"sell\", strategy.short)`. The port "
        "reproduces the indicator PLUS that appended block, i.e. entry-only "
        "behaviour (PINE_SEMANTICS.md 1.17).",
        "The appended block uses bare BOOLEAN conditions (`if FB_Buy`). No "
        "`? -1 : 0` integer is involved here, so the 1.17 truthiness trap does "
        "not apply; the port keeps the conditions as booleans, which is what "
        "Pine evaluates them as.",
        "The two `if FB_Buy == true and FB_Buy[1] == true` blocks are DEAD "
        "CODE: their body writes `FB_Buy == false` / `FB_Sell == false`, which "
        "is a COMPARISON (`==`), not an assignment (`:=`), so it stores "
        "nothing. Reproduced as a column for the record (`pine_fb_buy_lag1` / "
        "`pine_fb_sell_lag1`) and never read by the script.",
        "Every term is a comparison against the close shifted by 3..12 bars, "
        "so on the first 12 bars the lagged operand is na and Pine evaluates "
        "the comparison as false; the pandas comparison agrees and the port "
        "fills na with False.",
        "The final term is inverted relative to the rest: `close[8] > "
        "close[11]` for the buy setup and `close[8] < close[11]` for the sell "
        "setup. Transcribed literally.",
        "There is NO exit of any kind in the source. A position is only left "
        "by the opposite entry, which the engine models as a reverse fill, so "
        "`source_reproduce_stops` is False and a position open at the window's "
        "end stays open.",
        "The source declares indicator(...), so no strategy() properties exist "
        "and Pine's documented defaults are used: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD.",
        "MD-vs-SOURCE: the md front matter names the author as 'Zer3192', the "
        "source file's header reads '(c) Sofien-Kaabar' -- the md records the "
        "fmz uploader, the source the original author. No effect on behaviour; "
        "recorded, not reconciled.",
        "`plotshape(FB_Buy, ...)` / `plotshape(FB_Sell, ...)` are display-only "
        "and place no order; dropped.",
        "The header's backtest window is extraction metadata, not an "
        "input.time filter, so the port runs on whatever range the caller "
        "supplies; basePeriod: 15m is the host's intrabar fill granularity, "
        "not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        close = dataframe["close"]

        def lag(n):
            return close.shift(n)

        # FB_Buy: 16 downward steps across lags 3..12, then close[8] > close[11].
        fb_buy = (
            (close < lag(3)) & (close < lag(5))
            & (lag(1) < lag(4)) & (lag(1) < lag(6))
            & (lag(2) < lag(5)) & (lag(2) < lag(7))
            & (lag(3) < lag(6)) & (lag(3) < lag(8))
            & (lag(4) < lag(7)) & (lag(4) < lag(9))
            & (lag(5) < lag(8)) & (lag(5) < lag(10))
            & (lag(6) < lag(9)) & (lag(6) < lag(11))
            & (lag(7) < lag(10)) & (lag(7) < lag(12))
            & (lag(8) > lag(11))
        )
        # FB_Sell: the same shape with every operator flipped except the last.
        fb_sell = (
            (close > lag(3)) & (close > lag(5))
            & (lag(1) > lag(4)) & (lag(1) > lag(6))
            & (lag(2) > lag(5)) & (lag(2) > lag(7))
            & (lag(3) > lag(6)) & (lag(3) > lag(8))
            & (lag(4) > lag(7)) & (lag(4) > lag(9))
            & (lag(5) > lag(8)) & (lag(5) > lag(10))
            & (lag(6) > lag(9)) & (lag(6) > lag(11))
            & (lag(7) > lag(10)) & (lag(7) > lag(12))
            & (lag(8) < lag(11))
        )
        dataframe["pine_fb_buy"] = fb_buy.fillna(False)
        dataframe["pine_fb_sell"] = fb_sell.fillna(False)
        # Only read by the dead `if FB_Buy == true and FB_Buy[1] == true` block,
        # which stores nothing; kept as a ledger column, never read below.
        dataframe["pine_fb_buy_lag1"] = fb_buy.fillna(False).shift(1).fillna(False)
        dataframe["pine_fb_sell_lag1"] = fb_sell.fillna(False).shift(1).fillna(False)
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "fb_buy": dataframe["pine_fb_buy"].to_numpy(),
            "fb_sell": dataframe["pine_fb_sell"].to_numpy(),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if FB_Buy
        #    strategy.entry("buy", strategy.long)
        # else if  FB_Sell
        #     strategy.entry("sell", strategy.short)
        if ctx["fb_buy"][i]:
            broker.entry("buy", "long")
        elif ctx["fb_sell"][i]:
            broker.entry("sell", "short")
