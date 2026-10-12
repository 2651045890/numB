"""Port of sources/SM_4c0e8b14a7232e29.pine (batch_001/ADXRSI动量指标策略ADXRSI-Momentum-Indicators-Strategy.md).

Pine v4 (`//@version=4`, bare builtins: `change`, `rma`, `tr`, `abs`, `max`,
`min`, `sma`, `stdev`, `crossover`, `crossunder`, `fixnan`, `na`).
`strategy("DAX Shooter 5M Strategy", overlay=true)` declares only title/overlay,
so every other property is Pine's default: `default_qty_type=strategy.fixed`,
`default_qty_value=1`, commission 0%, `pyramiding=0`,
`process_orders_on_close=false`, `initial_capital=1000000`.

Three indicator blocks, all hand-written in the source (nothing is a library
call there):

    dirmov(len) =>
        up        = change(high)
        down      = -change(low)
        plusDM    = na(up)   ? na : up   > down and up   > 0 ? up   : 0
        minusDM   = na(down) ? na : down > up   and down > 0 ? down : 0
        truerange = rma(tr, len)
        plus      = fixnan(100 * rma(plusDM,  len) / truerange)
        minus     = fixnan(100 * rma(minusDM, len) / truerange)
        [plus, minus]

    adx(dilen, adxlen) =>
        [plus, minus] = dirmov(dilen)
        sum = plus + minus
        100 * rma(abs(plus - minus) / (sum == 0 ? 1 : sum), adxlen)

    # RSI
    up   = rma(max(change(close), 0), 7)
    down = rma(-min(change(close), 0), 7)
    rsi  = down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down)

    # Bollinger Bands
    basis = sma(close, 50) ; dev = 2.0 * stdev(close, 50)
    upper = basis + dev ; lower = basis - dev

    if crossover(rsi, 30) and adx(dilen, adxlen) > 32 and low < lower
        strategy.entry("COMPRA", strategy.long,  limit=upper, oca_name="DaxShooter")
    else
        strategy.cancel(id="COMPRA")

    if crossunder(rsi, 70) and adx(dilen, adxlen) > 32 and high > upper
        strategy.entry("VENDI", strategy.short, limit=lower, oca_name="DaxShooter")
    else
        strategy.cancel(id="VENDI")

Both legs are LIMIT entries (`limit=` names an absolute price), so the engine
rests them and fills when a later bar's low (long) / high (short) reaches the
level, at `min(limit, open)` / `max(limit, open)`. PINE_SEMANTICS.md section 2
item 11: a resting entry cannot be projected onto Freqtrade's interface, so the
framework's leg of this port enters at the next open of the placement bar
instead.

FIDELITY:

* `tr` is the BARE v4 builtin, i.e. Pine's `handle_na=false` form, which is na
  on the FIRST bar (there is no `close[1]`). PINE_SEMANTICS.md section 3.7
  records that `pine_ta.pine_tr` returns `high - low` on that first bar instead,
  which would start the `rma` window one bar early and shift the whole DI/ADX
  series (converging). Because `tr`'s na is part of the source's own
  initialisation, the port builds true range explicitly and lets `close[1]`'s
  na propagate, rather than using `pine_tr`. `pine_atr` is deliberately NOT
  used (it is the `handle_na=true` series). This is a port-local correction of a
  recorded shared-layer deviation; it is idempotent if that layer is ever fixed.
* `plusDM` / `minusDM` keep the source's na: the outer `na(up) ? na : ...`
  ternary wins over the inner `up > down and up > 0 ? up : 0`, so the first bar
  (where `change` is na) enters the rma as na and does NOT consume a smoothing
  step. Writing only the inner ternary would silently start the window a bar
  early, so the na is restored explicitly.
* `fixnan` is not in `pine_ta`; it is written out as a forward fill, which is
  its documented behaviour (replace na with the last non-na value).
* MEASURED CHOICE: `100 * di / truerange` divides by a possibly-zero
  `truerange` (a fully flat series). Pine's behaviour there is not published;
  pandas' +/-inf is mapped onto na before `fixnan`, which feeds `fixnan` exactly
  like a warmup na. `truerange` is never 0 on BTC data.
* `sum == 0 ? 1 : sum` is written as `total.where(total != 0, 1.0)`; when
  `plus`/`minus` are na the comparison is false and the na sum propagates, which
  is what Pine does.
* The source writes the RSI recursion out by hand, so the port does too rather
  than calling `pine_ta.pine_rsi`. The two are algebraically identical:
  `rma(max(change,0), n)` / `rma(-min(change,0), n)` are `pine_rsi`'s
  `average_gain` / `average_loss`, and the `down == 0 ? 100 : up == 0 ? 0 : ...`
  nesting is reproduced with the OUTER test applied last so that `down == 0`
  still wins when both are zero.
* `th` (`input(title="threshold", type=input.integer, defval=20)`) is DECLARED
  BUT NEVER USED: both conditions compare `adx(...)` against the LITERAL 32.
  The literal is kept; `th` is carried in `source_defaults` for visibility.
* The two `strategy.exit("exit", ..., loss = 90)` calls are COMMENTED OUT in the
  source and place nothing; they are not restored, so
  `source_reproduce_stops` is False and a position is only closed by the
  opposite entry reversing it.
* `alertcondition` is not order flow and is not reproduced. `plot` / `fill` are
  display-only.
* Both entry calls sit in an `if`/`else` whose else branch is
  `strategy.cancel(id=...)`; the ids "COMPRA" / "VENDI" and the call order are
  reproduced verbatim.
* `low < lower` / `high > upper` read the CURRENT bar's own low/high, which is
  not future data: Pine evaluates the script at that bar's close.
* The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
  `timeframe` is "1h"; the strategy title says "5M" but the header's period is
  the authority for the port. Its `basePeriod: 15m` is the FMZ backtester's own
  granularity for filling those 1h bars.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _fixnan(series: pd.Series) -> pd.Series:
    """Pine `fixnan`: replace na with the last non-na value."""
    return series.ffill()


class SMAdxRsiMomentumIndicators_4c0e8b(PinePortBase, IStrategy):
    source_id = "SM_4c0e8b14a7232e29"
    source_file = "ADXRSI动量指标策略ADXRSI-Momentum-Indicators-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "adxlen": 14,
        "dilen": 14,
        "th": 20,
        "len": 7,
        "bandainf": 30,
        "bandasup": 70,
        "length": 50,
        "mult": 2.0,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`tr` is the bare v4 builtin (handle_na=false), which is na on the first "
        "bar. PINE_SEMANTICS.md section 3.7 records that pine_ta.pine_tr returns "
        "high-low there instead, starting the rma window one bar early and "
        "shifting the whole DI/ADX series. Since tr's na is part of the source's "
        "own initialisation, true range is built explicitly here and close[1]'s "
        "na is allowed to propagate; pine_atr (the handle_na=true series) is "
        "deliberately not used. The correction is idempotent if the shared layer "
        "is ever fixed.",
        "plusDM / minusDM keep the source's na: the outer `na(up) ? na : ...` "
        "ternary wins over the inner one, so the first bar enters the rma as na "
        "and does not consume a smoothing step. The na is restored explicitly "
        "rather than being coalesced to 0.",
        "`fixnan` is not in pine_ta; written out as a forward fill, which is its "
        "documented behaviour.",
        "MEASURED CHOICE: 100*di/truerange divides by a possibly-zero truerange. "
        "Pine's behaviour there is not published; pandas' +/-inf is mapped onto "
        "na before fixnan, which feeds fixnan exactly like a warmup na. "
        "truerange is never 0 on BTC data.",
        "`sum == 0 ? 1 : sum` is total.where(total != 0, 1.0); when plus/minus "
        "are na the comparison is false and the na sum propagates, as in Pine.",
        "The source hand-writes its RSI, so the port does too instead of calling "
        "pine_rsi; the two are algebraically identical, with the `down == 0` "
        "test applied AFTER the `up == 0` test so the outer ternary still wins "
        "when both are zero.",
        "`th` (input title='threshold', defval=20) is DECLARED BUT NEVER USED: "
        "both conditions compare adx(...) against the LITERAL 32. The literal is "
        "kept; th is carried in source_defaults for visibility.",
        "The two `strategy.exit('exit', ..., loss = 90)` calls are COMMENTED OUT "
        "in the source and place nothing, so source_reproduce_stops is False and "
        "a position is only closed by the opposite entry reversing it.",
        "Both entry legs are LIMIT entries with an absolute price; nothing is "
        "scaled by mintick.",
        "Resting limit entries cannot be projected onto Freqtrade's interface "
        "(PINE_SEMANTICS.md section 2 item 11): the engine fills them on a later "
        "bar that reaches the level, while signal projection can only enter at "
        "the next open of the bar the order was placed on.",
        "alertcondition is not order flow and is not reproduced; plot / fill are "
        "display-only.",
        "The strategy title says '5M' but the /*backtest header declares "
        "`period: 1h`, which is what the port's timeframe takes.",
        "strategy() declares only title/overlay, so qty is Pine's default "
        "fixed/1, commission 0%, pyramiding 0 and initial_capital 1000000.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        high, low, close = dataframe["high"], dataframe["low"], dataframe["close"]
        dilen = int(params["dilen"])
        adxlen = int(params["adxlen"])

        # up = change(high) ; down = -change(low)
        up = ta.pine_change(high, 1)
        down = -ta.pine_change(low, 1)
        # plusDM = na(up) ? na : up > down and up > 0 ? up : 0
        # minusDM = na(down) ? na : down > up and down > 0 ? down : 0
        # The outer `na(...) ? na :` test wins, so the na is restored after the
        # inner ternary (which would otherwise coalesce it to 0).
        plus_dm = up.where((up > down) & (up > 0.0), 0.0).where(up.notna())
        minus_dm = down.where((down > up) & (down > 0.0), 0.0).where(down.notna())

        # truerange = rma(tr, len), with `tr` the bare v4 builtin: na on bar 0.
        previous_close = close.shift(1)
        true_range = pd.concat(
            [
                (high - low).abs(),
                (high - previous_close).abs(),
                (low - previous_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        true_range = true_range.where(previous_close.notna())
        truerange = ta.pine_rma(true_range, dilen)

        # plus  = fixnan(100 * rma(plusDM,  len) / truerange)
        # minus = fixnan(100 * rma(minusDM, len) / truerange)
        plus_raw = (100.0 * ta.pine_rma(plus_dm, dilen)) / truerange
        minus_raw = (100.0 * ta.pine_rma(minus_dm, dilen)) / truerange
        plus = _fixnan(plus_raw.replace([np.inf, -np.inf], np.nan))
        minus = _fixnan(minus_raw.replace([np.inf, -np.inf], np.nan))

        # sum = plus + minus ; adx = 100 * rma(abs(plus - minus) / (sum == 0 ? 1 : sum), adxlen)
        total = plus + minus
        divisor = total.where(total != 0.0, 1.0)
        adx = 100.0 * ta.pine_rma((plus - minus).abs() / divisor, adxlen)

        # RSI, hand-written in the source:
        #   up   = rma(max(change(src), 0), len)
        #   down = rma(-min(change(src), 0), len)
        #   rsi  = down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down)
        rsi_len = int(params["len"])
        change = ta.pine_change(close, 1)
        rsi_up = ta.pine_rma(change.clip(lower=0.0), rsi_len)
        rsi_down = ta.pine_rma((-change).clip(lower=0.0), rsi_len)
        with np.errstate(divide="ignore", invalid="ignore"):
            rsi = 100.0 - 100.0 / (1.0 + rsi_up / rsi_down)
        rsi = rsi.where(rsi_up != 0.0, 0.0)      # inner ternary: up == 0 -> 0
        rsi = rsi.where(rsi_down != 0.0, 100.0)  # outer ternary wins: down == 0 -> 100
        rsi = rsi.where(rsi_up.notna() & rsi_down.notna())

        # basis = sma(source, length) ; dev = mult * stdev(source, length)
        bb_len = int(params["length"])
        basis = ta.pine_sma(close, bb_len)
        dev = float(params["mult"]) * ta.pine_stdev(close, bb_len)
        upper = basis + dev
        lower = basis - dev

        # if crossover(rsi, bandainf) and adx(dilen, adxlen) > 32 and low < lower
        long_condition = (
            ta.pine_crossover(rsi, float(params["bandainf"]))
            & (adx > 32.0)
            & (low < lower)
        )
        # if crossunder(rsi, bandasup) and adx(dilen, adxlen) > 32 and high > upper
        short_condition = (
            ta.pine_crossunder(rsi, float(params["bandasup"]))
            & (adx > 32.0)
            & (high > upper)
        )

        dataframe["pine_plus_di"] = plus
        dataframe["pine_minus_di"] = minus
        dataframe["pine_adx"] = adx
        dataframe["pine_rsi"] = rsi
        dataframe["pine_bb_upper"] = upper
        dataframe["pine_bb_lower"] = lower
        dataframe["pine_long_condition"] = long_condition.fillna(False)
        dataframe["pine_short_condition"] = short_condition.fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "upper": dataframe["pine_bb_upper"].to_numpy(dtype=float),
            "lower": dataframe["pine_bb_lower"].to_numpy(dtype=float),
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if crossover(rsi, bandainf) and adx(dilen, adxlen) > 32 and low < lower
        #     strategy.entry("COMPRA", strategy.long, limit=upper, oca_name="DaxShooter")
        # else
        #     strategy.cancel(id="COMPRA")
        if ctx["long_condition"][i]:
            broker.entry("COMPRA", "long", limit=float(ctx["upper"][i]))
        else:
            broker.cancel("COMPRA")

        # if crossunder(rsi, bandasup) and adx(dilen, adxlen) > 32 and high > upper
        #     strategy.entry("VENDI", strategy.short, limit=lower, oca_name="DaxShooter")
        # else
        #     strategy.cancel(id="VENDI")
        if ctx["short_condition"][i]:
            broker.entry("VENDI", "short", limit=float(ctx["lower"][i]))
        else:
            broker.cancel("VENDI")
