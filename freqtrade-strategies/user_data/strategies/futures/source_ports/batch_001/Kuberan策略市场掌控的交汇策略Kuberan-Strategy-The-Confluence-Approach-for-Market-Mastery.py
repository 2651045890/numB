"""Port of sources/SM_11e4c6d9c951f408.pine (batch_001/Kuberan策略市场掌控的交汇策略Kuberan-Strategy-The-Confluence-Approach-for-Market-Mastery.md).

Pine v5 source (unsigned; it uses `matrategy`-free v5 syntax: `input.int`,
`input.bool`, `ta.pivothigh`, bare `crossover`). `strategy('Kuberan*',
overlay=true, max_lines_count=500)` declares only `title`/`overlay`, so every
other property is Pine's documented default: `default_qty_type=strategy.fixed`,
`default_qty_value=1`, commission 0%, `pyramiding=0`,
`process_orders_on_close=false`, `initial_capital=1000000`.

The source contains exactly TWO order-producing calls, at its very end:

    source = close
    length = input.int(20, minval=1)
    mult   = input.float(2.0, minval=0.001, maxval=50)
    basis  = ta.sma(source, length)
    dev    = mult * ta.stdev(source, length)
    upper  = basis + dev
    lower  = basis - dev

    if (ta.crossover(source, lower))
        strategy.entry("BBandLE", strategy.long,  stop=lower, oca_name="BollingerBands")
    else
        strategy.cancel(id="BBandLE")

    if (ta.crossunder(source, upper))
        strategy.entry("BBandSE", strategy.short, stop=upper, oca_name="BollingerBands")
    else
        strategy.cancel(id="BBandSE")

Both are STOP entries (`stop=` names an absolute price, not a tick count), so
the port passes the band value straight through as `broker.entry(..., stop=...)`
and the engine rests them, filling on a later bar that touches the level
(PINE_SEMANTICS.md section 2 item 11: a resting entry cannot be projected onto
Freqtrade's interface, so the framework's leg of this port enters at the next
open instead).

EVERYTHING ABOVE THE BOLLINGER BLOCK IS DISPLAY-ONLY. Lines 27-134 build a
pivot/zigzag support-resistance structure (`ph`/`pl`, `hl`, `zz`, `res`, `sup`,
`trend`) and draw it with `plotshape` / `line.new` / `barcolor`; lines 140-203
build a second "UT Bot"-style ATR trailing-stop pair (`xATRTrailingStop1/2`,
`pos1/pos2`, `buy1/sell1/buy2/sell2`) whose every consumer is a `plotshape`,
`barcolor` or `alertcondition` call. The only `strategy.*` call among them,
line 205 `// strategy.entry('long', strategy.long, when=buy2)`, is COMMENTED
OUT. None of those values reaches an order, so reproducing them would not move
a single fill; they are recorded here rather than recomputed, which is the same
treatment the display-only `plot`/`hline` calls get in the other ports of this
batch.

FIDELITY:

* The two `strategy.entry` calls use `stop=` with an ABSOLUTE PRICE (`lower` /
  `upper`), not a tick distance, so nothing is scaled by `mintick`; they are
  reproduced as entry orders with `stop=`.
* Both entry calls sit in an `if`/`else`, and the `else` branch is
  `strategy.cancel(id=...)`: the order is cancelled on every bar whose crossing
  condition is false, and re-placed on every bar where it is true. The
  if/else order and the two ids ("BBandLE" for the long, "BBandSE" for the
  short) are reproduced verbatim.
* `ta.stdev` is Pine's population standard deviation (ddof=0);
  `pine_ta.pine_stdev` implements exactly that.
* `crossover(source, lower)` is `source > lower and source[1] <= lower[1]` and
  `crossunder(source, upper)` is the mirror; na on either side is false. Both
  come from `pine_ta`, so the first `length` bars (where `lower`/`upper` are na)
  cannot fire.
* The `input.color` declarations (`supcol`, `rescol`, `bcolup`, `bcoldn`,
  `upCss`, `dnCss`) are display-only styling and are not carried in
  `source_defaults`; every other `input()` default IS carried, including the
  ones whose only consumers are the display-only blocks, so that the source's
  full parameter surface stays visible. `calcMethod` is kept as the Pine string
  'Atr'.
* `h` (`Signals from Heikin Ashi Candles`) switches `src` between `close` and a
  `request.security(ticker.heikinashi(...), ...)` call. `request.security` is
  not modelled by the engine (PINE_SEMANTICS.md section 2 item 1), but `src`
  feeds only the display-only ATR trailing-stop block, so no order is affected
  and no blocker arises. Left at its default (false) in `source_defaults`.
* `showsupres` / `changebarcol` / `backpaint` / `showExt` / `srlinewidth` /
  `lengthTL` / `multTL` likewise drive only drawing code.
* SOURCE BUG, NOT CORRECTED: line 262 reads `lowerTL := pl ? pl : lowerTL +
  slope_plTL`, using the `pl` pivot of the PIVOT/zigzag block above rather than
  the `plTL` defined two lines earlier. It is a display-only line so nothing
  trades on it; it is recorded and left as written.
* SOURCE-vs-md: the md's argument table renders `C2` (source
  `input(1, 'ATR Period for buy2')`) as `true`, `multTL` (source
  `input.float(1., 'Slope')`) as `true`, and `calcMethod` (source default
  'Atr') as the index `0`. All three are the FMZ table's own rendering of the
  numeric/bool/string defaults (1 -> true, 1.0 -> true, option 0 -> 'Atr'); the
  SOURCE values 1, 1.0 and 'Atr' are used, which is what rule 2 requires.
* `max_lines_count=500` and the `line.*` calls are drawing parameters with no
  trading effect and are not reproduced.
* The `/*backtest` header declares `period: 5m` on Futures_Binance BTC_USDT, so
  `timeframe` is "5m". Its `basePeriod: 1m` is the FMZ backtester's own
  granularity for filling those 5m bars, not the strategy's period.
* There is no `strategy.exit` / `strategy.close` in the source, so
  `source_reproduce_stops` is False: a position is only ever closed by the
  opposite entry reversing it, or by the window ending.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMKuberan_11e4c6(PinePortBase, IStrategy):
    source_id = "SM_11e4c6d9c951f408"
    source_file = (
        "Kuberan策略市场掌控的交汇策略Kuberan-Strategy-The-Confluence-Approach-for-Market-Mastery.md"
    )
    timeframe = "5m"
    can_short = True
    source_defaults: dict = {
        "lb": 5,
        "rb": 5,
        "showsupres": False,
        "srlinewidth": 3,
        "changebarcol": True,
        "A1": 5,
        "C1": 400,
        "A2": 6,
        "C2": 1,
        "h": False,
        "length": 20,
        "mult": 2.0,
        "lengthTL": 14,
        "multTL": 1.0,
        "calcMethod": "Atr",
        "backpaint": True,
        "showExt": True,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Only two strategy.* calls exist, both at the end of the source: a long "
        "STOP entry on ta.crossover(close, lower) with stop=lower, and a short "
        "STOP entry on ta.crossunder(close, upper) with stop=upper. Each sits in "
        "an if/else whose else branch is strategy.cancel(id=...). Both are "
        "reproduced verbatim, in source order, with the source's ids 'BBandLE' "
        "and 'BBandSE'.",
        "Both entry legs use ABSOLUTE-PRICE stops (the Bollinger band values), "
        "not tick distances, so nothing is scaled by mintick.",
        "Resting stop entries cannot be projected onto Freqtrade's interface "
        "(PINE_SEMANTICS.md section 2 item 11): the engine fills them on a later "
        "bar that touches the level, while signal projection can only enter at "
        "the next open of the bar the order was placed on. This is the framework "
        "boundary, not a port choice.",
        "The pivot/zigzag support-resistance block (ph, pl, hl, zz, res, sup, "
        "trend, the res/sup lines) is DISPLAY-ONLY: its every consumer is "
        "plotshape / line.new / barcolor. Not recomputed.",
        "The ATR trailing-stop block (xATRTrailingStop1/2, pos1/pos2, buy1, "
        "sell1, buy2, sell2) is DISPLAY-ONLY: its only consumers are plotshape, "
        "barcolor and alertcondition, and the one strategy.entry that referenced "
        "buy2 is COMMENTED OUT in the source (line 205). Not recomputed.",
        "input.color declarations (supcol, rescol, bcolup, bcoldn, upCss, "
        "dnCss) are display-only styling and are not carried in "
        "source_defaults; every numeric/bool/string input default IS carried.",
        "`h` switches src to request.security(ticker.heikinashi(...)). That is "
        "PINE_SEMANTICS.md section 2 item 1 (multi-timeframe not modelled), but "
        "src feeds only the display-only ATR block, so no order is affected. "
        "Left at its default false.",
        "SOURCE BUG, not corrected: `lowerTL := pl ? pl : lowerTL + slope_plTL` "
        "uses the `pl` of the zigzag block instead of the `plTL` defined just "
        "above it. Display-only, so nothing trades on it.",
        "SOURCE-vs-md: the md argument table renders the source defaults C2=1 as "
        "`true`, multTL=1.0 as `true`, and calcMethod='Atr' as the option index "
        "`0`. The SOURCE values (1, 1.0, 'Atr') are used; the md rendering is "
        "recorded, not followed.",
        "strategy() declares only title/overlay, so qty is Pine's default "
        "fixed/1, commission 0%, pyramiding 0 and initial_capital 1000000.",
        "No strategy.exit / strategy.close exists, so source_reproduce_stops is "
        "False: a position is only closed by the opposite entry reversing it.",
        "The /*backtest header's basePeriod: 1m is the FMZ backtester's own "
        "granularity for filling the 5m bars, not the strategy's period.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        source = dataframe["close"]
        # ta.sma(source, length) / mult * ta.stdev(source, length)
        basis = ta.pine_sma(source, int(params["length"]))
        dev = float(params["mult"]) * ta.pine_stdev(source, int(params["length"]))
        upper = basis + dev
        lower = basis - dev

        dataframe["pine_bb_basis"] = basis
        dataframe["pine_bb_upper"] = upper
        dataframe["pine_bb_lower"] = lower
        # if ta.crossover(source, lower)  -> the LONG arm
        dataframe["pine_long_condition"] = ta.pine_crossover(source, lower)
        # if ta.crossunder(source, upper) -> the SHORT arm
        dataframe["pine_short_condition"] = ta.pine_crossunder(source, upper)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "upper": dataframe["pine_bb_upper"].to_numpy(dtype=float),
            "lower": dataframe["pine_bb_lower"].to_numpy(dtype=float),
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (ta.crossover(source, lower))
        #     strategy.entry("BBandLE", strategy.long, stop=lower, oca_name="BollingerBands")
        # else
        #     strategy.cancel(id="BBandLE")
        if ctx["long_condition"][i]:
            broker.entry("BBandLE", "long", stop=float(ctx["lower"][i]))
        else:
            broker.cancel("BBandLE")

        # if (ta.crossunder(source, upper))
        #     strategy.entry("BBandSE", strategy.short, stop=upper, oca_name="BollingerBands")
        # else
        #     strategy.cancel(id="BBandSE")
        if ctx["short_condition"][i]:
            broker.entry("BBandSE", "short", stop=float(ctx["upper"][i]))
        else:
            broker.cancel("BBandSE")
