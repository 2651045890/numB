"""Port of sources/SM_be835004bf9b7084.pine (batch_001/Bollinger-Bands-RSI-OBV策略Bollinger-Bands-RSI-OBV-Strategy.md).

Pine v4 (`//@version=4`; the md attributes it to atakhadivi). Bollinger Bands
for direction, RSI for strength and OBV for a short-term turn:

    obv    = cum(sign(change(close)) * volume)
    basis  = sma(close, 20)
    dev    = 2.0 * stdev(close, 20)          // Pine stdev = population (ddof=0)
    upper  = basis + dev
    lower  = basis - dev

    buyEntry  = close > basis and rsi(close, 14) > 50 and obv[1] < obv
    buyExit   = close < lower
    sellEntry = close < basis and rsi(close, 14) < 50 and obv[1] > obv
    sellExit  = close > upper

    strategy.entry("BBandLE", strategy.long,  stop=lower, oca_name="BollingerBands", comment="BBandLE", when=buyEntry)
    strategy.exit(id='BBandLE', when=buyExit)
    strategy.entry("BBandSE", strategy.short, stop=upper, oca_name="BollingerBands", comment="BBandSE", when=sellEntry)
    strategy.exit(id='BBandSE', when=sellExit)

Both entries are STOP orders (`stop=` is an entry parameter, not an exit), and
both are placed marketable -- the long's buy-stop at the LOWER band sits below
the market, the short's sell-stop at the UPPER band sits above it -- so on the
original platform they fill at once, and the engine's `_price_order_fill`
resolves them to the next bar's open (`max(lower, open)` / `min(upper, open)`)
whenever that bar does not gap through the level.

THE TWO `strategy.exit` CALLS CARRY NO PRICE LEG AT ALL -- no stop, limit,
profit, loss or trail -- and that is what they are, not an omission here. Pine
does not turn such a call into a market exit: the exit order needs at least one
of `profit` / `limit` / `loss` / `stop` or a `trail_offset` pair, and the
compiler diagnostic for it says exactly that, adding that such lines "didn't do
anything in your code anyway" and that a market close is `strategy.close`.
FMZ's own Pine documentation says the same and points to `strategy.close` /
`strategy.close_all` for a market close. So the source's exits place nothing:
`buyExit` / `sellExit` are computed and handed to a call that discards them,
and a position is in fact closed only when the OPPOSITE entry reverses it.
The engine models that (a level-less exit order never fills -- measured below).
See FIDELITY for the one thing that does NOT follow from this.

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. The
`/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the platform's own granularity
for filling those 1h bars (bar magnifier), which pine_engine does not model.

FIDELITY:

* The source's two level-less `strategy.exit` calls are transcribed verbatim
  (`broker.exit(id, when=...)`) and, as in the source, place nothing: the
  engine's exit fill path requires a price leg, so all 1 138 of them rest
  un-filled for the whole window. Positions therefore end only by reversal.
  MEASURED (BTC/USDT:USDT 1h 2024): engine 743 round trips, 1 left open, and
  every one of those exits is an opposite entry filling, not an exit order.
* THE SHARED PROJECTION LAYER DISAGREES WITH THE ENGINE ABOUT THIS SHAPE, and
  that is a shared-layer defect rather than a port choice. `run_pine` projects
  an exit order with no price legs as a next-open MARKET exit signal (the same
  branch that handles `strategy.close`), so the framework is told to close
  where the engine holds: measured on the same run, the port projects
  `exit_long` 941 and `exit_short` 870 times while the engine's own exit orders
  fill 0 times. The engine's reading is the one Pine documents; the projection
  is not modified here (PINE_SEMANTICS.md section 一 does not cover this shape
  and the shared layer is out of scope for a port), so a chain-verification
  divergence on this port is expected and is attributable there. Reported, not
  worked around -- substituting `broker.close` would invent an exit the source
  does not have.
* `oca_name="BollingerBands"` is passed through, but pine_engine implements no
  OCA cancellation (it only records the group). The two entry conditions are
  mutually exclusive on one bar, so the arms cannot both rest; recorded.
* Both entries are resting STOP orders placed marketable, which Freqtrade's
  strategy interface cannot express: the projected entry is a next-open market
  order. Identical to the engine while the next bar opens beyond the level,
  different when it gaps through it (engine fills at the stop, framework at the
  open). Same limitation as SMPivotPointReversal_db6f0c (PINE_SEMANTICS.md
  section 二.11), inherited rather than introduced.
* `obv` follows Pine's documented `cum(sign(change(close)) * volume)`. The
  first bar's `change` is na; pine_ta treats na as a zero contribution to the
  cumulative sum instead of adding volume, which shifts the level by one bar of
  volume and only matters through the `obv[1] < obv` / `obv[1] > obv`
  comparisons, where an na operand is false (Pine's boolean context).
* `stdev` is Pine's population standard deviation (ddof=0) and `rsi` is the
  Wilder-smoothed ta.rsi, both taken straight from pine_ta rather than
  re-derived. sma/stdev/rsi are na until their windows fill, and na propagates,
  so no signal is emitted before the 20-bar (and 15-bar RSI) warm-up.
* The md's prose describes the exits as closing the previous long / short
  position ("当股价跌破布林带下轨时候,平掉之前的多单头寸"). The code hands those
  conditions to a call that places no order. Code followed, disagreement
  recorded -- this is the same source-vs-md split the docstring above records
  from the Pine side.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the framework trades a rounded quantity where the engine
  trades a float one, which the chain verifier measures separately.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBollingerBandsRsiObv_be8350(PinePortBase, IStrategy):
    source_id = "SM_be835004bf9b7084"
    source_file = "Bollinger-Bands-RSI-OBV策略Bollinger-Bands-RSI-OBV-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults = {
        # input(20, minval=1) -- Bollinger length; the RSI length 14 is a literal
        "length": 20,
        # input(2.0, minval=0.001, maxval=50)
        "mult": 2.0,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Both `strategy.exit` calls carry no price leg (no stop/limit/profit/"
        "loss/trail), which in Pine places no order at all: the compiler "
        "diagnostic for this shape says an exit needs one of profit/limit/loss/"
        "stop or a trail pair and that a market close is `strategy.close`. "
        "Transcribed verbatim, so the exits are inert in the engine too (1 138 "
        "exit orders placed, 0 filled) and positions end only by reversal.",
        "The shared projection layer (`run_pine`) projects a level-less exit "
        "order as a next-open market exit signal, so the FRAMEWORK exits where "
        "the engine holds: measured on BTC/USDT:USDT 1h 2024, exit_long=941 and "
        "exit_short=870 projected against 0 engine exit fills. That is an "
        "inconsistency inside the shared layer, reported and NOT worked around "
        "(substituting `broker.close` would invent an exit the source lacks); "
        "any chain-verification divergence on this port is attributable there.",
        "Both entries are resting STOP orders placed marketable (long stop at "
        "the lower band, short stop at the upper band). Freqtrade has no "
        "resting-entry expression, so the projected entry is a next-open market "
        "order -- identical while the next bar opens beyond the level, different "
        "when it gaps through it. Same limitation as SMPivotPointReversal_db6f0c "
        "(PINE_SEMANTICS.md section 二.11).",
        "`oca_name=\"BollingerBands\"` is passed through, but pine_engine "
        "implements no OCA cancellation (it only records the group); the two "
        "entry conditions are mutually exclusive on one bar, so the arms cannot "
        "both rest.",
        "`obv` is Pine's `cum(sign(change(close)) * volume)`; the first bar's "
        "`change` is na and pine_ta counts that bar as a zero contribution "
        "rather than adding volume, which shifts the level by one bar of volume "
        "and only matters through the `obv[1] < obv` / `obv[1] > obv` tests "
        "(na comparisons are false).",
        "`strategy()` declares only title/overlay, so Pine's defaults apply: "
        "strategy.fixed / 1 contract, initial capital 1000000, 0% commission, "
        "pyramiding 0, process_orders_on_close=false. No exit call exists in "
        "effect, so source_reproduce_stops is False.",
        "The md's prose says buyExit/sellExit close the previous long/short; "
        "the code hands those conditions to a call that places no order. Code "
        "followed, disagreement recorded.",
        "The `/*backtest` header's `basePeriod: 15m` is the platform's "
        "granularity for filling 1h bars (bar magnifier), not modelled here.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounded quantity can differ from the engine's "
        "float one, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        length = int(params["length"])
        mult = float(params["mult"])
        # obv = cum(sign(change(src)) * volume)
        obv = ta.pine_cum(ta.pine_sign(ta.pine_change(close)) * dataframe["volume"])
        basis = ta.pine_sma(close, length)
        dev = mult * ta.pine_stdev(close, length)
        upper = basis + dev
        lower = basis - dev
        rsi = ta.pine_rsi(close, 14)
        dataframe["pine_obv"] = obv
        dataframe["pine_basis"] = basis
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        dataframe["pine_rsi"] = rsi
        # Pine's `and` on an na operand is false, which is what the pandas
        # comparisons already give for the warm-up bars.
        dataframe["pine_buy_entry"] = (
            (close > basis) & (rsi > 50) & (obv.shift(1) < obv)
        )
        dataframe["pine_buy_exit"] = close < lower
        dataframe["pine_sell_entry"] = (
            (close < basis) & (rsi < 50) & (obv.shift(1) > obv)
        )
        dataframe["pine_sell_exit"] = close > upper
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_entry": dataframe["pine_buy_entry"].to_numpy(),
            "buy_exit": dataframe["pine_buy_exit"].to_numpy(),
            "sell_entry": dataframe["pine_sell_entry"].to_numpy(),
            "sell_exit": dataframe["pine_sell_exit"].to_numpy(),
            "upper": dataframe["pine_upper"].to_numpy(dtype=float),
            "lower": dataframe["pine_lower"].to_numpy(dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("BBandLE", strategy.long, stop=lower,
        #                 oca_name="BollingerBands", comment="BBandLE", when=buyEntry)
        broker.entry("BBandLE", "long", stop=float(ctx["lower"][i]),
                     oca_name="BollingerBands", when=bool(ctx["buy_entry"][i]))
        # strategy.exit(id='BBandLE', when=buyExit)  -- no price leg: places nothing
        broker.exit("BBandLE", when=bool(ctx["buy_exit"][i]))
        # strategy.entry("BBandSE", strategy.short, stop=upper,
        #                 oca_name="BollingerBands", comment="BBandSE", when=sellEntry)
        broker.entry("BBandSE", "short", stop=float(ctx["upper"][i]),
                     oca_name="BollingerBands", when=bool(ctx["sell_entry"][i]))
        # strategy.exit(id='BBandSE', when=sellExit)  -- no price leg: places nothing
        broker.exit("BBandSE", when=bool(ctx["sell_exit"][i]))
