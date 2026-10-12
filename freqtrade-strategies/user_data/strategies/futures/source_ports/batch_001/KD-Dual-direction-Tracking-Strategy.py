"""Port of sources/SM_4288a547905d0a4a.pine (batch_001/KD-Dual-direction-Tracking-Strategy.md).

Pine v4. A KD (stochastic) two-way inventory tracker (author: Tonyder):

    max = input(20)   min = input(-10)   period = input(9)
    rsv := stoch(close, high, low, period)
    if bar_index <= period
        k := rsv ; dir2 := 0 ; sum2 := 0
    else
        k := k[1]*2/3 + rsv/3 ; dir2 := dir2[1] ; sum2 := sum2[1]

    rule 1  dir2 ==  1 and k[1] >= 50 and k < 50 and 0 <= sum2 < 0.66  -> sum2 += 0.33
    rule 2  dir2 == -1 and k[1] <= 50 and k > 50 and -0.66 < sum2 <= 0 -> sum2 -= 0.33
            k >= 80                                                        -> dir2 :=  1
            k <= 20                                                        -> dir2 := -1
    rule 3  dir2 == -1 and dir2[1] ==  1                               -> sum2 += 0.33
    rule 4  dir2 ==  1 and dir2[1] == -1                               -> sum2 -= 0.33
    rule 5  dir2 ==  1 and k[1] >= 50 and k < 50 and sum2 <= 0          -> sum2 :=  0.33
    rule 6  dir2 == -1 and k[1] >= 50 and k < 50 and sum2 >= 0          -> sum2 := -0.33

    share2 = sum2 > 0 ? round(sum2 * max) : sum2 < 0 ? round(abs(sum2) * min) : 0
    share  = strategy.position_size
    if share2 > share
        strategy.order(id='buy',  long=true)
    else if share2 < share
        strategy.order(id='sell', long=false)

`k`, `dir2` and `sum2` are declared WITHOUT `var` and then assigned with `:=` on
every bar, including on both arms of the if/else, so each bar's value is a
function of the previous bar's value: Pine's series history carries them. `k` is
the usual KD smoothing recursion and is computed as a series in
`pine_indicators`; `dir2` / `sum2` are the result of the rule chain above and
are carried per bar in `pine_script`. The rules are applied in the source's own
order, because several of them read and write the same two variables inside one
bar (rule 1/2 run BEFORE `dir2` can be flipped by the k >= 80 / k <= 20 blocks,
and rules 3/4 read the PREVIOUS bar's final `dir2`).

`strategy()` IS COMMENTED OUT (source line 13), so Pine's documented defaults
are in force -- `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, `pyramiding = 0`, `process_orders_on_close = false`. The
commented line asks for `pyramiding = 1000`, `process_orders_on_close = true`,
`precision = 6` and `max_bars_back = 720`; those are recorded in
`source_fidelity_notes`, not applied. The `pyramiding` fork is the load-bearing
one for this source, and it is treated at length there and in the module's
blockers -- the strategy is a position ladder, so the port's inability to hold
more than one contract in a direction is the single largest difference between
this port and the original platform.

Sizing: every `strategy.order` in the source omits `qty=`, so each one is the
default order size -- one contract under the defaults in force. The comparison
`share2 > share` is therefore not a quantity: the source walks its inventory
toward `share2` one contract at a time, one order per bar.
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMKdDualDirectionTracking_4288a5(PinePortBase, IStrategy):
    source_id = "SM_4288a547905d0a4a"
    source_file = "KD-Dual-direction-Tracking-Strategy.md"
    timeframe = "1d"
    # strategy.order(id="sell", long=false) opens a short in the source.
    can_short = True
    source_defaults: dict = {
        # max = input(defval=20, title="庫存上限(share)", type=input.integer)
        # (shadows Pine's built-in `max`; the source's own name is kept so the
        # input table matches)
        "max": 20,
        # min = input(defval=-10, title="庫存下限(share)", type=input.integer)
        # A POSITIVE ceiling is NOT assumed: the source multiplies by this
        # negative default to produce the short inventory target.
        "min": -10,
        # period = input(defval=9, title="KD 週期(KD period)", type=input.integer, minval=2)
        "period": 9,
    }
    # The ONLY strategy() declaration in the file (line 13) is commented out, so
    # it declares nothing: Pine's documented defaults apply. The commented line
    # asks for pyramiding=1000, process_orders_on_close=true, precision=6 and
    # max_bars_back=720; none of that is in force (see source_fidelity_notes).
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop / limit / trail leg exists -- the only exits are the cost of the
    # next strategy.order.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "NOT a converter-appended order block, despite its tier_reason. The "
        "file declares no indicator() and no study(), its only strategy() line "
        "(line 13) is COMMENTED OUT, and the two order calls are the author's "
        "own strategy.order('buy'/'sell') at the end of an eight-rule state "
        "machine -- nothing a converter template appends. The tier_reason's "
        "'declares indicator()/study(), tool appended strategy.entry pair; NO "
        "exits' is false on the first three counts. The source is followed.",
        "The file's only strategy() declaration is COMMENTED OUT (line 13), so "
        "Pine's documented defaults are in force: default_qty_type fixed / 1 "
        "contract, initial_capital 1000000, commission 0%, pyramiding 0, "
        "process_orders_on_close false. RECORDED BUT NOT APPLIED: the commented "
        "line asks for pyramiding = 1000, process_orders_on_close = true, "
        "precision = 6 and max_bars_back = 720.",
        "THE PYRAMIDING FORK IS THE WHOLE STRATEGY HERE. `share2` is a TARGET "
        "INVENTORY in contracts, built from max=20 (long) and min=-10 (short), "
        "and the source walks `strategy.position_size` toward it one "
        "1-contract strategy.order per bar. The md says the same thing in its "
        "own words ('the pyramiding carries high risk'). Under the commented "
        "pyramiding = 1000 the ladder stacks; under the default in force the "
        "ladder is capped, and the public layer's model of strategy.order "
        "decides which reading this port gets. See the blocker in "
        "source_fidelity_notes on strategy.order for the consequence, which is "
        "large and is recorded rather than papered over.",
        "strategy.order vs strategy.entry (PUBLIC-LAYER MODEL, UNVERIFIED, "
        "affects this port more than any other): pine_engine.PineBroker.order "
        "delegates to entry, so every strategy.order here is placed as an "
        "entry: (a) it passes the creation-time pyramiding gate, which Pine is "
        "believed NOT to apply to strategy.order, and (b) it reverses rather "
        "than nets, since `_entry_delta` sizes an opposing entry as "
        "`qty + |position|` (PINE_SEMANTICS.md 1.1). Consequence of (a) with "
        "source_pyramiding = 0: the port can hold ONE contract per direction, "
        "so `share2 = 7 > share = 1` produces no second order, and the source's "
        "inventory ladder (up to +20 / -10 contracts) becomes a single "
        "contract. Consequence of (b): a sell while long 1 leaves the port "
        "short 1 where Pine's order would leave it flat, so the direction "
        "after the first exit differs. Both follow from modelling the two Pine "
        "call types as one, which is what the public layer does; this port uses "
        "that model rather than working around it, and records it. The same "
        "open question is already recorded on the sibling port "
        "HMA日线交叉交易策略 (which also places strategy.order).",
        "MEASURED, and this is the size of the blocker: on a 3000-bar daily "
        "smoke frame the port placed 2964 orders, 2912 of which were BLOCKED by "
        "the creation-time pyramiding gate, for 52 fills, 51 round trips and a "
        "maximum |position| of 1.0 contract. The source's own arithmetic was "
        "asking for targets of 6.6 / 13.2 / 19.8 and more contracts at those "
        "same bars. So the port trades the SIGNAL sequence faithfully -- the "
        "k / dir2 / sum2 state machine is reproduced exactly, and it is what "
        "decides the direction of every order -- but not the SIZE ladder: Pine "
        "accumulates inventory, this port is flat-or-one-contract.",
        "Related, and also measured: `max = 20` is NOT a hard cap on the "
        "target. Only rule 1's guard carries `sum2 < 1`; rules 3 and 5 add or "
        "set 0.33 with no ceiling, and rule 3 can fire on a bar whose sum2 is "
        "already 0.99. Observed sum2 values include 1.32, i.e. "
        "share2 = round(1.32 * 20) = 26 contracts -- above the declared "
        "inventory ceiling. The source calls `max` a 庫存上限; its code does not "
        "enforce one, and the port does not add one.",
        "Nothing in the source is an exit call: no strategy.exit, no "
        "strategy.close, no strategy.close_all, and no commented-out one "
        "either. The md's prose ('Exits occur when strong turns weak or vice "
        "versa' / 平仓条件为强势转弱做多平仓) describes the EFFECT of rules 3/4, "
        "which only re-price `sum2` (the target); the position itself is only "
        "ever reduced by the next strategy.order, one contract at a time, once "
        "share2 < share. src note: source_reproduce_stops is False because "
        "there is no stop/limit/trail leg to mirror.",
        "`share2 = 0` IS A LIVE VALUE, NOT 'NO TARGET'. share2 is declared "
        "`share2=0` without `var` and the if/else only overwrites it when "
        "sum2 > 0 or sum2 < 0, so a bar with sum2 exactly 0 leaves the target "
        "at 0 contracts -- which orders a SELL while long and a BUY while "
        "short. It is reachable: the seeding bars (bar_index <= period) set "
        "sum2 := 0, and 0.33 + (-0.33) cancels exactly in floating point. "
        "Reproduced by defaulting share2 to 0.0 rather than skipping the "
        "comparison.",
        "`max` and `min` are Pine input names that shadow Pine's own built-ins; "
        "they are kept VERBATIM as the source_defaults keys so the input table "
        "matches the source (check_source_defaults normalises names), and are "
        "read through context keys max_share / min_share so Python's builtins "
        "are not shadowed in this module.",
        "`min` is NEGATIVE (-10) and the source multiplies by it, so "
        "round(abs(sum2) * min) yields a NEGATIVE inventory target. It is not "
        "treated as a magnitude: a positive reading of `min` would produce a "
        "second long ladder instead of a short one.",
        "round() is Pine's math.round -- half away from zero -- which is what "
        "pine_ta.pine_round implements, not Python's banker's rounding. With "
        "the declared defaults the products land on 0.33/0.66/0.99 * 20 = "
        "6.6 / 13.2 / 19.8 (long) and -3.3 / -6.6 / -9.9 (short), none of them "
        "a tie; the helper is used anyway so an overridden `max`/`min` that "
        "does produce a .5 is not rounded the wrong way.",
        "The order of the eight conditional blocks is load-bearing and is "
        "reproduced literally. Rules 1 and 2 run BEFORE the k >= 80 / k <= 20 "
        "blocks can flip dir2, and rules 3/4 compare the CURRENT dir2 against "
        "`dir2[1]`, the PREVIOUS bar's final value. Rules 5 and 6 then "
        "OVERRIDE sum2 outright (+0.33 / -0.33) instead of adjusting it, on the "
        "same guard rules 1/2 use for a k-downcross; because rule 2 leaves any "
        "sum2 it touched strictly negative (decrement by 0.33 from a value "
        "<= 0), rule 6's `sum2 >= 0` guard only holds on a downcross bar that "
        "rule 2 did not apply to. Reordering any of the eight changes `sum2` "
        "and therefore the inventory target.",
        "The author's own comments do not match the code: rule 3 is commented "
        "'strong become to weak, buy when k < 20' yet it fires on a "
        "strong-to-weak flip and ADDS to sum2, rule 4 is commented 'buy' yet it "
        "SUBTRACTS, and rule 6 is commented 'weak but share is bigger than 0' "
        "while its guard is k[1] >= 50 and k < 50. Only the code is reproduced; "
        "the comments are not behaviour.",
        "`k` is a recursion on a NON-`var` series: `k := rsv` while "
        "bar_index <= period and `k := k[1]*2/3 + rsv/3` afterwards, so `k` is a "
        "real series even though the declaration above it is reset every bar. "
        "`k[1]` in the rules is that series' previous value. Same for `dir2` "
        "and `sum2`, which the if/else assigns unconditionally on both arms -- "
        "the `dir2=0` / `sum2=0.0` declarations above them never take effect "
        "after the seeding bars. The port keeps `k` as an array and `dir2` / "
        "`sum2` as carried per-bar state.",
        "stoch(close, high, low, period) is 100 * (close - lowest(low, period)) "
        "/ (highest(high, period) - lowest(low, period)); pine_ta.pine_highest "
        "/ pine_lowest use min_periods=length, so rsv is na for the first "
        "period-1 bars, matching Pine's na handling (PINE_SEMANTICS.md 3.2). "
        "The port transcribes the formula rather than calling a KD helper.",
        "rsv on a zero denominator (a window whose highest equals its lowest) "
        "is na in Pine; the port maps the resulting inf/-inf to nan so the "
        "comparisons stay false, the same modelling choice as the sibling "
        "BBB策略BBB port. Because k is a recursion, one na bar would make every "
        "later k na in Pine too; numpy's nan propagation reproduces that "
        "exactly (all rule guards then read false and dir2/sum2 freeze).",
        "2/3 and /3 are FLOAT divisions on a float series (k is declared 0.0), "
        "so the weights are 0.666... and 0.333...; the port writes 2.0/3.0 and "
        "/ 3.0 rather than relying on Python's integer division.",
        "The seeding window is `bar_index <= period`, i.e. bar_index 0..period "
        "INCLUSIVE -- period+1 bars, one more than the window stoch needs. "
        "Transcribed as `i <= period`, and no order can come out of those bars "
        "in any case (dir2 = 0 and sum2 = 0 give share2 = 0 = a flat target).",
        "plot(share) / plot(dir2) / plot(k80) / plot(k50) / plot(k20) / plot(k) "
        "are display-only, so `k80` / `k50` / `k20` (and the `up`, `bottom`, "
        "`first`, `k_value` declarations that feed nothing else) are not "
        "reproduced. The commented algebra above them is a derivation note, not "
        "code.",
        "MD/SOURCE MATCH: the md's embedded source listing is line-for-line "
        "identical to the source file (checked by diffing the two, ignoring "
        "blank lines), and its argument table (20 / -10 / 9) agrees with the "
        "source. Unlike its three siblings in this group there is no "
        "rendered-default mismatch to record here; the only md-vs-code gap is "
        "the md's prose wording about 'exits' noted above.",
        "The /*backtest header declares `period: 1d` on Futures_Binance "
        "BTC_USDT, hence timeframe = '1d'; its basePeriod: 1h is the FMZ "
        "backtester's own intrabar fill granularity, not the strategy period. "
        "The header's start/end window is the recorded run's window, not a "
        "source property, and is not applied (PINE_SEMANTICS.md section 二 8). "
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6 measures the step "
        "rounding separately).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]
        period = int(params["period"])

        high_max = ta.pine_highest(high, period)
        low_min = ta.pine_lowest(low, period)
        # rsv := stoch(close, high, low, period)
        with np.errstate(divide="ignore", invalid="ignore"):
            rsv = 100.0 * (close - low_min) / (high_max - low_min)
        # Pine yields na where the window is flat, never an infinity.
        rsv = rsv.replace([np.inf, -np.inf], np.nan).to_numpy(dtype=float)

        # if bar_index <= period: k := rsv
        # else:                   k := k[1]*2/3 + rsv/3
        # A non-`var` series that is nonetheless recursive: Pine's series
        # history carries k[1] across bars. na propagates, as it does in Pine.
        k = np.full(rsv.shape[0], np.nan, dtype=float)
        for i in range(rsv.shape[0]):
            if i <= period:
                k[i] = rsv[i]
            else:
                k[i] = k[i - 1] * 2.0 / 3.0 + rsv[i] / 3.0

        dataframe["pine_rsv"] = rsv
        dataframe["pine_k"] = k
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "k": dataframe["pine_k"].to_numpy(dtype=float),
            "period": int(params["period"]),
            # `max` / `min` are the source's own input names (they shadow Pine
            # built-ins there too); they are read here under names that do not
            # shadow Python's.
            "max_share": float(params["max"]),
            "min_share": float(params["min"]),
            # `dir2 = 0` / `sum2 = 0.0` are re-declared every bar in the source,
            # but both if/else arms assign them, so they carry across bars.
            "state": {"dir2": 0, "sum2": 0.0},
        }

    def pine_script(self, broker, i, ctx):
        st = ctx["state"]
        k = ctx["k"]
        period = ctx["period"]
        k_now = float(k[i])
        # k[1]
        k_prev = float(k[i - 1]) if i > 0 else float("nan")
        # dir2[1] / sum2[1]: the PREVIOUS bar's final values, captured before
        # this bar's rules can change them.
        dir2_prev = int(st["dir2"])
        sum2_prev = float(st["sum2"])

        # if bar_index <= period ... else k := k[1]*2/3 + rsv/3 (done above)
        if i <= period:
            dir2 = 0
            sum2 = 0.0
        else:
            dir2 = dir2_prev
            sum2 = sum2_prev

        # rule 1, strong target, buy when k < 50.
        if (dir2 == 1 and k_prev >= 50 and k_now < 50
                and sum2 < 1 and sum2 >= 0 and sum2 < 0.66):
            sum2 = sum2 + 0.33
        # rule 2, weak target, sell when k > 50.
        if (dir2 == -1 and k_prev <= 50 and k_now > 50
                and sum2 > -1 and sum2 <= 0 and sum2 > -0.66):
            sum2 = sum2 - 0.33

        # become to strong
        if k_now >= 80:
            dir2 = 1
        # become to weak
        if k_now <= 20:
            dir2 = -1

        # rule 3, strong become to weak
        if dir2 == -1 and dir2_prev == 1:
            sum2 = sum2 + 0.33
        # rule 4, weak become to strong
        if dir2 == 1 and dir2_prev == -1:
            sum2 = sum2 - 0.33

        # rule 5, strong but share is smaller than 0
        if dir2 == 1 and k_prev >= 50 and k_now < 50 and sum2 <= 0:
            sum2 = 0.33
        # rule 6, weak but share is bigger than 0
        if dir2 == -1 and k_prev >= 50 and k_now < 50 and sum2 >= 0:
            sum2 = -0.33

        st["dir2"] = dir2
        st["sum2"] = sum2

        # share2 = 0  (re-declared every bar: a sum2 of exactly 0 leaves the
        # target at 0 contracts, which is an order, not an absence of one)
        share2 = 0.0
        if sum2 > 0:
            # share2 := round(sum2 * max)
            share2 = float(ta.pine_round(sum2 * ctx["max_share"]))
        elif sum2 < 0:
            # share2 := round(abs(sum2) * min)   -- min is NEGATIVE
            share2 = float(ta.pine_round(abs(sum2) * ctx["min_share"]))

        # share = strategy.position_size
        share = broker.position_size
        if share2 > share:
            # strategy.order(id='buy', long=true)
            broker.order("buy", "long")
        elif share2 < share:
            # strategy.order(id="sell", long=false)
            broker.order("sell", "short")
