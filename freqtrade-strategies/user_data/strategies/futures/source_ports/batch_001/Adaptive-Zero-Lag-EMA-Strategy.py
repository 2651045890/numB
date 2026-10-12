"""Port of sources/SM_a79516ae251cc593.pine (batch_001/Adaptive-Zero-Lag-EMA-Strategy.md).

Pine v3. Ehlers-style adaptive zero-lag EMA: a Cosine-IFM block estimates the
dominant cycle, the K-th period is an EMA of the source, and a 31-step scan over
a "Gain" term picks the error-correlation (EC) series that best tracks the
source. Trade rule:

    buy  = crossover(EC, EMA) and 100*LeastError/src > Threshold
    sell = crossunder(EC, EMA) and 100*LeastError/src > Threshold
    if buy
        strategy.entry("Enter Long", strategy.long)
    else if sell
        strategy.entry("Enter Short", strategy.short)

Those two `strategy.entry` calls are the whole trade behaviour: there is NO
`strategy.exit` / `strategy.close` / `strategy.cancel` anywhere in the source
(see the FIDELITY note on `fixedSL` / `fixedTP` / `risk`). So `can_short` is
True and `source_reproduce_stops` is False -- a position is closed only by the
opposite entry reversing it and a position open on the last bar stays open.

The whole script is a per-bar state machine (every `:=` reads `[1]` of itself),
so the indicators are computed with one explicit forward pass that reproduces
Pine's na handling rather than vectorised.

`/*backtest` header: period 2h on Futures_Binance BTC_USDT; `basePeriod: 15m`
is the FMZ backtester's fill granularity, not the strategy's period.

FIDELITY:

* `Gain := i/10` is PINE v3 INTEGER DIVISION, and that is preserved verbatim.
  Both operands are int, and Pine's arithmetic type rule makes int / int an int
  truncated toward zero (the v3 Operators page: "If both operands are integers,
  then the result will also have the type integer"; `23/7 == 3`). Over the loop
  `for i = -15 to 15` the gain therefore only ever takes the three values
  -1.0, 0.0, +1.0 -- six iterations each for the first and last, nineteen for
  0.0 -- and NOT the 31 values -1.5, -1.4, ... +1.5 a decimal reading suggests.
  The port runs all 31 iterations in Pine's order with Pine's strict `<`, so
  the first-minimum tie-break is the source's; only `Gain` itself is truncated.
  This is a load-bearing reading (EC, and therefore every crossover, depends on
  it) and is flagged as such rather than "tidied up" to `i/10.0`.
* `calc_on_every_tick=true` is NOT reproduced: the engine runs the script once
  per bar close (PINE_SEMANTICS section 2.5 -- no intra-bar `varip`-style
  recomputation). Recorded, not approximated.
* `slippage = 5` (Pine: ticks) is NOT reproduced; neither the engine nor the
  Freqtrade port carries a slippage term.
* `commission_type=strategy.commission.cash_per_contract` with
  `commission_value=0.000005` is a CASH amount per contract, which the port's
  percent-of-turnover commission model cannot express. At the source's own
  sizing (`fixed`, 1 contract) that is 0.000005 USD per leg, i.e. nil; the port
  declares 0% and records the unmapped argument rather than inventing a
  percentage.
* `pyramiding=1` (NOT Pine's default 0) and `initial_capital=1000` are declared
  by the source and are carried. They interact with PINE_SEMANTICS 1.5/1.6: a
  `fixed` 1-contract order on BTC/USDT:USDT is tens of thousands of USD of
  notional against a 1000-unit wallet, so the framework will refuse the entries
  on wallet/min-stake grounds even though the source's own backtest did not —
  a framework boundary, never reproduced by shrinking the declared capital.
* `nz()` is load-bearing and is reproduced: `nz(s2[1])`, `nz(s3[1])`,
  `nz(len[1])`, `nz(EMA[1])`, `nz(EC[1])` all fall back to 0 before their first
  real value.
* Comparisons against na are False in Pine, so `if (s2 != 0)` / `if (s3 != 0)`
  do NOT fire while those series are na: `v2` and `delta` keep their per-bar
  reset value 0.0 instead of becoming na. The port checks the na case
  explicitly for the same reason.
* Warmup is preserved exactly: `v1 = src - src[7]` needs 7 prior bars, `s2`/`s3`
  need one more, and the `for i = 0 to 100` accumulation of `delta[i]` cannot
  complete until ~108 bars have elapsed. Until then `inst` copies the na carried
  by `if (inst == 0.0) inst := inst[1]`, so `len`, `Period`, `alpha`, `EMA` and
  `EC` are na and no signal can fire. Nothing is shortened or pre-seeded.
* `Period := round(len)` overwrites the `Period` input on every bar when
  `adaptive` is true (the default); `Period` is only the literal 20 when
  `adaptive` is false. Both branches are implemented.
* There is no `ta.ema` in this source -- `EMA` is the source's own recursion
  seeded through `nz(EMA[1])`, so PINE_SEMANTICS 3.1 (ta.ema's seed) does not
  apply to it.
* md vs source: the md's step 7 states "It sets a stop loss and a trailing take
  profit for each position", but the SOURCE declares no stop or take-profit
  anywhere. `fixedSL`, `fixedTP` and `risk` are `input()`s that are never read
  again after their declaration, and there is no `strategy.exit`. The md is
  describing an exit mechanism this source does not have (it matches the
  sibling v2 script, which does call `strategy.exit(..., loss=fixedSL,
  trail_offset=15, trail_points=fixedTP)`). Reproducing the md would mean
  inventing two order calls; per 铁律 2 the source wins, so the port is
  entry-only and `source_reproduce_stops` is False.
* md vs source, minor: the md's argument table lists 8 inputs, matching the
  source. `v_input_1_close` is the `src` source-selector input; its declared
  default is the bare identifier `close`, which the port fixes to `close`
  rather than exposing it as a parameter (a non-numeric source cannot be
  overridden through `source_defaults`).
* md vs source, minor: the script is `//@version=3` while both md and source
  use the v3 bare forms (`crossover`, `crossunder`, `atan`, `sqrt`, `round`);
  no v4/v5 namespace migration is involved. `PI = 3.14159265359` is the source's
  own truncated constant and is kept, not replaced by `math.pi`.
* `plot()` calls, `overlay=true`, `title`, `shorttitle` and `currency` are
  display-only and are not reproduced.
* Leverage, margin, liquidation and funding are not modelled by the engine, and
  the venue's contract-step rounding is applied by the framework but not by the
  engine (PINE_SEMANTICS 1.6); the chain verifier measures that separately.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMAdaptiveZeroLagEmaStrategy_a79516(PinePortBase, IStrategy):
    source_id = "SM_a79516ae251cc593"
    source_file = "Adaptive-Zero-Lag-EMA-Strategy.md"
    timeframe = "2h"
    can_short = True
    source_defaults: dict = {
        "Period": 20,
        "adaptive": True,
        "GainLimit": 15,
        "Threshold": 0.03,
        "fixedSL": 50,
        "fixedTP": 10,
        "risk": 0.01,
    }
    # `strategy()` declares neither default_qty_type nor default_qty_value, so
    # Pine's documented defaults apply: strategy.fixed / 1.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    # commission_type=strategy.commission.cash_per_contract, value 0.000005 --
    # a cash-per-contract fee the percent model cannot express; see FIDELITY.
    source_commission_percent = 0.0
    source_pyramiding = 1
    source_initial_capital = 1_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`Gain := i/10` is Pine v3 integer division: int/int is an int truncated "
        "toward zero, so over `for i = -15 to 15` Gain only takes -1.0, 0.0 and "
        "+1.0 -- not the 31 values -1.5..+1.5 a decimal reading suggests. The "
        "port reproduces the truncation and still runs all 31 iterations in "
        "Pine's order with Pine's strict `<` tie-break. This is load-bearing for "
        "EC and therefore for every crossover.",
        "`calc_on_every_tick=true` is not reproduced: the engine evaluates once "
        "per bar close (PINE_SEMANTICS 2.5). `slippage=5` ticks is not "
        "reproduced either; neither the engine nor the port carries slippage.",
        "commission_type=strategy.commission.cash_per_contract with "
        "commission_value=0.000005 is a cash-per-contract fee (0.000005 USD per "
        "leg at the source's own 1-contract sizing) that the percent-of-turnover "
        "model cannot express; the port declares 0% and records it.",
        "No exit call of any kind exists in the source: `source_reproduce_stops` "
        "is False, a position is closed only by the opposite entry reversing it, "
        "and a position open at the window end stays open.",
        "MODELLED READING: the md says each position gets a stop loss and a "
        "trailing take profit, but fixedSL/fixedTP/risk are input()s that are "
        "never read again and there is no strategy.exit in the source. The port "
        "reproduces the source (entry-only), not the md's description.",
        "`nz()` is load-bearing and is reproduced for s2/s3/len/EMA/EC; "
        "comparisons against na are False, so `if (s2 != 0)` / `if (s3 != 0)` do "
        "not fire while those series are na and v2/delta keep their per-bar "
        "reset value 0.0.",
        "Warmup preserved: src[7] needs 7 prior bars, s2/s3 one more, and the "
        "`for i = 0 to 100` accumulation of delta[i] needs ~108 bars; until then "
        "inst carries na, so Period/alpha/EMA/EC are na and no signal can fire.",
        "`Period := round(len)` overwrites the Period input every bar when "
        "adaptive=true (the default); the literal 20 is only used when "
        "adaptive=false. Both branches are implemented.",
        "EMA here is the source's own `alpha*src + (1-alpha)*nz(EMA[1])` "
        "recursion seeded from 0, not ta.ema, so PINE_SEMANTICS 3.1's seeding "
        "question does not apply.",
        "Source declares fixed / 1 contract and initial_capital=1000: a "
        "1-contract BTC order is far beyond a 1000-unit wallet, so the framework "
        "may veto entries that the source's own backtest took (PINE_SEMANTICS "
        "1.5/1.6). Declared capital is kept at the source's value.",
        "PI is the source's own truncated 3.14159265359, not math.pi; the `src` "
        "input is fixed to its declared default `close` and is not a parameter.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"].to_numpy(dtype=float)
        n = len(close)
        adaptive = bool(params["adaptive"])
        gain_limit = int(params["GainLimit"])
        threshold = float(params["Threshold"])
        period_input = float(params["Period"])
        # PI = 3.14159265359 (source literal); the loop tests v4 > 2*PI.
        two_pi = 2.0 * 3.14159265359

        delta = np.zeros(n)
        ema = np.full(n, np.nan)
        ec = np.full(n, np.nan)
        least_error = np.full(n, np.nan)

        # Per-bar `:=` state; every `[1]` reference reads the previous bar's
        # FINAL value, so one scalar of carry per variable is enough.
        prev_v1 = prev_s2 = prev_s3 = np.nan
        prev_inst = prev_len = np.nan
        prev_ema = prev_ec = np.nan

        for t in range(n):
            src = close[t]
            if adaptive:
                # v1 := src - src[7]
                v1 = src - close[t - 7] if t >= 7 else np.nan
                total = prev_v1 + v1
                diff = prev_v1 - v1
                # s2 := 0.2*(v1[1] + v1)^2 + 0.8*nz(s2[1])
                s2 = 0.2 * total * total + 0.8 * (0.0 if np.isnan(prev_s2) else prev_s2)
                # s3 := 0.2*(v1[1] - v1)^2 + 0.8*nz(s3[1])
                s3 = 0.2 * diff * diff + 0.8 * (0.0 if np.isnan(prev_s3) else prev_s3)
                # if (s2 != 0) v2 := sqrt(s3/s2)  -- na never compares true
                v2 = 0.0
                if not np.isnan(s2) and s2 != 0.0:
                    v2 = float(np.sqrt(s3 / s2))
                # if (s3 != 0) delta := 2*atan(v2)  -- na never compares true
                delta_t = 0.0
                if not np.isnan(s3) and s3 != 0.0:
                    delta_t = float(2.0 * np.arctan(v2))
                delta[t] = delta_t
                # for i = 0 to 100: v4 := v4 + delta[i]; if v4 > 2*PI and inst == 0: inst := i-1
                v4 = 0.0
                inst = 0.0
                for i in range(0, 101):
                    j = t - i
                    v4 = v4 + (delta[j] if j >= 0 else np.nan)
                    if v4 > two_pi and inst == 0.0:
                        inst = float(i - 1)
                # if (inst == 0) inst := inst[1]
                if inst == 0.0:
                    inst = prev_inst
                # len := 0.25*inst + 0.75*nz(len[1])
                length = 0.25 * inst + 0.75 * (0.0 if np.isnan(prev_len) else prev_len)
                # Period := round(len)
                period = ta.pine_round(length)
                prev_v1, prev_s2, prev_s3 = v1, s2, s3
                prev_inst, prev_len = inst, length
            else:
                period = period_input

            # alpha = 2/(Period + 1); EMA := alpha*src + (1-alpha)*nz(EMA[1])
            alpha = 2.0 / (period + 1.0)
            ema_t = alpha * src + (1.0 - alpha) * (0.0 if np.isnan(prev_ema) else prev_ema)
            ec_prev = 0.0 if np.isnan(prev_ec) else prev_ec

            # for i = -GainLimit to GainLimit: Gain := i/10 (INTEGER division);
            # EC := alpha*(EMA + Gain*(src - nz(EC[1]))) + (1-alpha)*nz(EC[1]);
            # Error := src - EC; if |Error| < LeastError: LeastError := |Error|,
            # BestGain := Gain
            best_gain = 0.0
            least = 1_000_000.0
            for i in range(-gain_limit, gain_limit + 1):
                gain = float(int(i / 10))  # Pine v3 int/int -> int (trunc toward 0)
                candidate = alpha * (ema_t + gain * (src - ec_prev)) + (1.0 - alpha) * ec_prev
                error = abs(src - candidate)
                if error < least:
                    least = error
                    best_gain = gain
            # EC := alpha*(EMA + BestGain*(src - nz(EC[1]))) + (1-alpha)*nz(EC[1])
            ec_t = alpha * (ema_t + best_gain * (src - ec_prev)) + (1.0 - alpha) * ec_prev

            ema[t], ec[t], least_error[t] = ema_t, ec_t, least
            prev_ema, prev_ec = ema_t, ec_t

        # buy = crossover(EC, EMA) and 100*LeastError/src > Threshold
        # sell = crossunder(EC, EMA) and 100*LeastError/src > Threshold
        # `crossover`/`crossunder` need x[1], so bar 0 can never fire, and an na
        # on either side makes the comparison false.
        buy = np.zeros(n, dtype=bool)
        sell = np.zeros(n, dtype=bool)
        for t in range(1, n):
            if np.isnan(ec[t]) or np.isnan(ec[t - 1]) or np.isnan(ema[t]) or np.isnan(ema[t - 1]):
                continue
            strength = 100.0 * least_error[t] / close[t]
            if not strength > threshold:
                continue
            buy[t] = bool(ec[t] > ema[t] and ec[t - 1] <= ema[t - 1])
            sell[t] = bool(ec[t] < ema[t] and ec[t - 1] >= ema[t - 1])

        dataframe["pine_ec"] = ec
        dataframe["pine_ema"] = ema
        dataframe["pine_least_error"] = least_error
        dataframe["pine_buy"] = buy
        dataframe["pine_sell"] = sell
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy": dataframe["pine_buy"].to_numpy(),
            "sell": dataframe["pine_sell"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if buy
        #     strategy.entry("Enter Long", strategy.long)
        # else if sell
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["buy"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["sell"][i]:
            broker.entry("Enter Short", "short")
