"""Port of sources/SM_b24b6beccc86992b.pine (batch_001/Keltner通道突破回抽策略Keltner-Channel-Pullback-Strategy.md).

Pine v2. A Keltner channel built from an SMA and an ATR is used as a bounce
band; price poking in from outside the lower border goes long and poking in
from above the upper border goes short, each entry protected by a fixed
tick-distance stop:

    price  = close
    EMA    = sma(price, keltnerLength)            // named EMA, is an SMA
    ATR    = atr(keltnerATRLength)
    top    = EMA + ATR * keltnerDeviation
    bottom = EMA - ATR * keltnerDeviation

    if (enterOnBorderTouchFromInside and crossunder(price, bottom))
        strategy.entry("BUY", strategy.long, qty=tradeSize)
    else if (crossover(price, bottom))
        strategy.entry("BUY", strategy.long, qty=tradeSize)

    if (crossover(price, EMA) and closeOnEMATouch)
        strategy.close("BUY")

    if (0 != SL)
        strategy.exit("EXIT BUY",  "BUY",  qty=tradeSize, loss=SL)
        strategy.exit("EXIT SELL", "SELL", qty=tradeSize, loss=SL)

    if (enterOnBorderTouchFromInside and crossover(price, bottom))
        strategy.entry("SELL", strategy.long, qty=tradeSize)   // long, id SELL
    else if (crossunder(price, top))
        strategy.entry("SELL", strategy.short, qty=tradeSize)

    if (crossunder(price, EMA) and closeOnEMATouch)
        strategy.close("SELL")

The port keeps the source's statement ORDER exactly: the BUY block, then the
BUY-market close, then the two `strategy.exit` legs, then the SELL block, then
the SELL-market close. Reordering them would change which order the engine sees
first on a bar that arms several at once (PINE_SEMANTICS.md section 1.13).

`strategy()` declares only `title` / `shorttitle` / `overlay`, so every
property is Pine's documented default: `strategy.fixed` / 1 contract, initial
capital 1000000, commission 0%, pyramiding 0, `process_orders_on_close=false`.
The entry passes `qty=tradeSize` explicitly, and `tradeSize` defaults to 1 --
the same quantity the Pine default would supply.

`loss=SL` is in TICKS, not price: the engine multiplies it by the instrument's
mintick (0.1 for BTC/USDT:USDT, so SL=50 is a 5.0 price-unit stop), matching
`_order_stop_limit`. `strategy.exit(..., qty=tradeSize)` also passes a quantity,
which the engine's `exit()` does not take -- it closes the whole entry via
`from_entry`; with pyramiding 0 an entry holds exactly `tradeSize` contracts, so
the two agree (recorded below rather than silently dropped).

MEASURED (BTC/USDT:USDT 1h, `python strategy_migration/verify_chain.py --port
SM_b24b6beccc86992b`): engine 115 trades against the framework's 92, giving
`mismatch`; of the 115, EXACTLY 23 stops fill at a bar's OPEN because the price
gapped past the 5.0 tick stop, and 115 - 92 = 23. On each of those bars the
shared `PinePortBase.custom_stoploss` sees the engine's level already beyond the
candle's bound (`level <= low` for a short, `level >= high` for a long) and,
reading that as "a stop that would move against the position", publishes
nothing. The framework's stop is therefore left at its initial value, the trade
is not stopped, and it merges with the next engine trade: the §1.13 "并账" shape,
which is why the paired comparison reports 88 `open_date` / 89 `close_date`
mismatches and a `max_price_gap` of 38882.9 that is a ±1 alignment artefact, not
89 price errors. The guard lives in the shared layer, which this port must not
change (铁律 9); the divergence is the framework's inability to book a stop at a
gap-through-open, not an error in this port.

FIDELITY:

* `EMA = sma(price, keltnerLength)` is an SMA despite the name and is
  reproduced as `pine_sma`, NOT as an EMA. The variable name is the author's.
* `0 != SL` is reproduced verbatim (SL is an int input, and the comparison is a
  numeric one -- PINE_SEMANTICS.md 1.16 concerns `type=bool` inputs, which this
  is not). With SL's default of 50 the exit block IS live, so
  `source_reproduce_stops` is True.
* `closeOnEMATouch` and `enterOnBorderTouchFromInside` are `input(type=bool)`
  and appear only in boolean (`and`) contexts, so no `!= 0` inversion risk
  (PINE_SEMANTICS.md 1.16). Both default false, which means the `else`/`elif`
  branches are the live ones; the `if` branches are reproduced anyway because
  the source contains them and they are reachable through `source_parameters`.
* `buyEntry` / `sellEntry` are computed by the source and then never read.
  They are computed here too and kept as columns, and never read by the script.
* The `else` inside the SELL block belongs to `if (enterOnBorderTouchFromInside
  and crossover(price, bottom))`, whose inner condition is a CROSSOVER of the
  bottom band -- not to a condition on `top`. It is an unusual pairing (a
  "touch from inside" that fires long, not short) and is reproduced as written.
* `atr()` is `rma(tr, length)`; `pine_ta.pine_atr` seeds the rma on the first
  bar with high-low (`ta.tr` with `handle_na=true`), whereas Pine's `ta.tr`
  default leaves the first bar na (PINE_SEMANTICS.md 3.7). The seeding point of
  the whole ATR series is therefore one bar early relative to that reading,
  which shifts the warm-up only; the SMA(200) warms up far later anyway.
* `sma` is na until its 200-bar window is full and na propagates, so no signal
  can exist before bar 200; `crossover`/`crossunder` are false while either
  side is na.
* The md's argument table renders `v_input_7` (source `input(defval=1, minval=1,
  title="Trade size")`) as `true`. That is the FMZ table's own rendering of the
  numeric default 1; the source's `1` is reproduced.
* The md's prose describes a "pullback" strategy in which price returns to a
  border after having left it; the code has no such state. Only the
  `enterOnBorderTouchFromInside` input changes the branch taken, and both of
  its branches fire on the same crossover. Recorded, code followed.
* `plot` / `fill` are display-only and place no condition.
* The `/*backtest` header declares `period: 1h`; its `basePeriod: 15m` is the
  FMZ backtester's own granularity for filling those 1h bars.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMKeltnerChannelPullback_b24b6b(PinePortBase, IStrategy):
    source_id = "SM_b24b6beccc86992b"
    source_file = "Keltner通道突破回抽策略Keltner-Channel-Pullback-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "keltnerLength": 200,
        "keltnerATRLength": 200,
        "keltnerDeviation": 8,
        "closeOnEMATouch": False,
        "enterOnBorderTouchFromInside": False,
        "SL": 50,
        "tradeSize": 1,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = True
    # `loss=SL` is in ticks (Pine reads mintick off the symbol); BTC/USDT:USDT
    # futures quote in 0.1, so SL=50 is a 5.0 price-unit stop.
    source_mintick = 0.1
    source_fidelity_notes = [
        "`EMA = sma(price, keltnerLength)` is a SIMPLE moving average despite "
        "its name; reproduced with pine_sma, not pine_ema.",
        "`strategy.exit(..., qty=tradeSize)` passes a quantity the engine's "
        "exit() does not accept -- an exit closes the whole entry via "
        "from_entry. With pyramiding 0 (Pine's default, and the source declares "
        "none) the entry holds exactly tradeSize contracts, so the two agree; "
        "recorded rather than silently dropped.",
        "Entry statement order is preserved: BUY block, close('BUY'), the two "
        "strategy.exit legs, SELL block, close('SELL'). The engine fills "
        "same-bar pending orders in creation order (PINE_SEMANTICS.md 1.13), so "
        "reordering would change behaviour.",
        "The SELL block's `else` belongs to `if (enterOnBorderTouchFromInside "
        "and crossover(price, bottom))` -- a crossover of the BOTTOM band, not "
        "a condition on `top`, even though the branch places a short. "
        "Reproduced as written.",
        "`buyEntry = crossover(price, bottom)` and `sellEntry = "
        "crossunder(price, top)` are dead code -- computed by the source and "
        "never read. Computed here too, kept as columns, never read.",
        "`closeOnEMATouch` and `enterOnBorderTouchFromInside` are "
        "`input(type=bool)` used only in boolean contexts, so the `!= 0` "
        "inversion trap of PINE_SEMANTICS.md 1.16 does not apply. Both default "
        "false, so with the shipped defaults the `else if` branches are the "
        "live ones; the `if` branches are still reproduced because the source "
        "contains them and source_parameters can reach them.",
        "`0 != SL` is a numeric test on an int input, reproduced verbatim. It "
        "is live at SL's default of 50, hence source_reproduce_stops=True.",
        "loss=SL is a TICK distance: the engine applies it as "
        "avg_price -/+ SL * mintick, with mintick 0.1 (BTC/USDT:USDT). The "
        "source does not state a mintick; it is read off the symbol by Pine.",
        "atr() = rma(tr, length); pine_ta.pine_atr seeds the rma with a "
        "first-bar high-low while Pine's ta.tr leaves the first bar na "
        "(PINE_SEMANTICS.md 3.7). One bar of warm-up, then convergent; the "
        "SMA(200) needs 200 bars regardless.",
        "sma is na until its window is full and na propagates, so no order can "
        "be placed before bar 200 and crossover/crossunder are false while "
        "either operand is na.",
        "md-vs-source: the md argument table renders v_input_7 (source "
        "`input(defval=1, minval=1, title=\"Trade size\")`) as `true`. That is "
        "the FMZ table rendering the numeric default 1; the source's 1 is used.",
        "md-vs-source: the md prose describes a stateful 'pullback' rule "
        "(price returns to a border it previously left). The code holds no "
        "such state -- the only branch selector is the boolean "
        "enterOnBorderTouchFromInside. Code followed, prose recorded.",
        "MEASURED on BTC/USDT:USDT 1h: engine 115 trades vs the framework's "
        "92. Exactly 23 of the 115 stops fill at a bar OPEN past the 5.0 tick "
        "stop, and 115-92=23. On those bars the shared custom_stoploss guard "
        "(level already beyond the candle's bound -> 'not tightening') "
        "publishes no level, so the framework is never stopped and merges the "
        "trade with the next engine one (PINE_SEMANTICS.md 1.13). The reported "
        "open_date/close_date mismatches (88/89) and max_price_gap (38882.9) "
        "are that ±1 merge, not 89 price errors. Shared layer, not modified "
        "(铁律 9).",
        "plot/fill are display-only and place no condition.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately.",
    ]

    def pine_indicators(self, dataframe, params):
        price = dataframe["close"]
        # EMA = sma(price, keltnerLength): an SMA under an EMA's name.
        keltner_ma = ta.pine_sma(price, int(params["keltnerLength"]))
        keltner_atr = ta.pine_atr(dataframe, int(params["keltnerATRLength"]))
        deviation = float(params["keltnerDeviation"])
        top = keltner_ma + keltner_atr * deviation
        bottom = keltner_ma - keltner_atr * deviation
        dataframe["pine_keltner_ma"] = keltner_ma
        dataframe["pine_keltner_atr"] = keltner_atr
        dataframe["pine_keltner_top"] = top
        dataframe["pine_keltner_bottom"] = bottom
        # buyEntry / sellEntry: dead in the source, computed for the record.
        dataframe["pine_buy_entry"] = ta.pine_crossover(price, bottom)
        dataframe["pine_sell_entry"] = ta.pine_crossunder(price, top)
        # The crossings the script actually reads.
        dataframe["pine_cross_bottom_up"] = ta.pine_crossover(price, bottom)
        dataframe["pine_cross_bottom_down"] = ta.pine_crossunder(price, bottom)
        dataframe["pine_cross_top_up"] = ta.pine_crossover(price, top)
        dataframe["pine_cross_top_down"] = ta.pine_crossunder(price, top)
        dataframe["pine_cross_ma_up"] = ta.pine_crossover(price, keltner_ma)
        dataframe["pine_cross_ma_down"] = ta.pine_crossunder(price, keltner_ma)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "cross_bottom_up": dataframe["pine_cross_bottom_up"].to_numpy(),
            "cross_bottom_down": dataframe["pine_cross_bottom_down"].to_numpy(),
            "cross_top_up": dataframe["pine_cross_top_up"].to_numpy(),
            "cross_top_down": dataframe["pine_cross_top_down"].to_numpy(),
            "cross_ma_up": dataframe["pine_cross_ma_up"].to_numpy(),
            "cross_ma_down": dataframe["pine_cross_ma_down"].to_numpy(),
            "close_on_ema_touch": bool(params["closeOnEMATouch"]),
            "inside_touch": bool(params["enterOnBorderTouchFromInside"]),
            "trade_size": float(params["tradeSize"]),
            "sl": int(params["SL"]),
        }

    def pine_script(self, broker, i, ctx):
        size = ctx["trade_size"]
        # if ( enterOnBorderTouchFromInside and crossunder(price, bottom) )
        #     strategy.entry("BUY", strategy.long, qty=tradeSize, comment="BUY")
        # else
        #     if( crossover(price, bottom) )
        #         strategy.entry("BUY", strategy.long, qty=tradeSize, comment="BUY")
        if ctx["inside_touch"] and ctx["cross_bottom_down"][i]:
            broker.entry("BUY", "long", qty=size)
        elif ctx["cross_bottom_up"][i]:
            broker.entry("BUY", "long", qty=size)

        # if( crossover(price,EMA) and closeOnEMATouch )
        #     strategy.close("BUY")
        if ctx["cross_ma_up"][i] and ctx["close_on_ema_touch"]:
            broker.close("BUY")

        # if( 0 != SL )
        #     strategy.exit("EXIT BUY", "BUY", qty=tradeSize, loss=SL)
        #     strategy.exit("EXIT SELL", "SELL", qty=tradeSize, loss=SL)
        if 0 != ctx["sl"]:
            broker.exit("EXIT BUY", "BUY", loss=ctx["sl"])
            broker.exit("EXIT SELL", "SELL", loss=ctx["sl"])

        # if( enterOnBorderTouchFromInside and crossover(price, bottom) )
        #     strategy.entry("SELL", strategy.long, qty=tradeSize, comment="SELL")
        # else
        #     if ( crossunder(price, top) )
        #         strategy.entry("SELL", strategy.short, qty=tradeSize, comment="SELL")
        if ctx["inside_touch"] and ctx["cross_bottom_up"][i]:
            broker.entry("SELL", "long", qty=size)
        elif ctx["cross_top_down"][i]:
            broker.entry("SELL", "short", qty=size)

        # if( crossunder(price, EMA) and closeOnEMATouch )
        #     strategy.close("SELL")
        if ctx["cross_ma_down"][i] and ctx["close_on_ema_touch"]:
            broker.close("SELL")
