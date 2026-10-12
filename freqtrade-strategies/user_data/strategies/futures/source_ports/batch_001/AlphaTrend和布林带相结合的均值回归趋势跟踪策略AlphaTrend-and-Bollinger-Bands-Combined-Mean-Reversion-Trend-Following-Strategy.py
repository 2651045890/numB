"""Port of sources/SM_33c8278404801cb5.pine (batch_001/AlphaTrend和布林带相结合的均值回归趋势跟踪策略AlphaTrend-and-Bollinger-Bands-Combined-Mean-Reversion-Trend-Following-Strategy.md).

Pine v5. KivancOzbilgic's AlphaTrend ratchet -- gated by MFI, with an RSI
variant behind an input -- combined with a Bollinger Band breakout:

    coeff = input.float(1, 'Multiplier', step=0.1)      // 1.0
    AP    = input(14, 'Common Period')
    ATR   = ta.sma(ta.tr, 20)                           // 20 is a LITERAL, not AP
    src   = input(close)
    novolumedata = input(false)
    upT   = low  - ATR * coeff
    downT = high + ATR * coeff
    AlphaTrend = 0.0
    AlphaTrend := (novolumedata ? ta.rsi(src, AP) >= 50 : ta.mfi(hlc3, AP) >= 50)
                  ? (upT   < nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : upT)
                  : (downT > nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : downT)

    BBPeriod = input.int(20);   BBMultiplier = input.float(2.0)
    basis = ta.sma(close, BBPeriod)
    dev   = ta.stdev(close, BBPeriod)
    upper = basis + BBMultiplier * dev
    lower = basis - BBMultiplier * dev

    longCondition  = ta.crossover(close,  upper) and ta.crossover(AlphaTrend, AlphaTrend[1])
    shortCondition = ta.crossunder(close, lower) and ta.crossunder(AlphaTrend, AlphaTrend[1])
    longExit_AT_6  = ta.crossover(close, AlphaTrend)
    shortExit_AT_6 = ta.crossunder(close, AlphaTrend)
    exit1 = input.bool(true, title="Enable Exit Condition for Strategy 1")   // never read
    exit1_condition = close < AlphaTrend ? 1.0 : na

    strategy.entry("Buy",  strategy.long,  when = longCondition)
    strategy.entry("Sell", strategy.short, when = shortCondition)
    strategy.exit("Buy",  "longExit_AT_6",  stop = exit1_condition, when = shortExit_AT_6)
    strategy.exit("Sell", "shortExit_AT_6", stop = exit1_condition, when = longExit_AT_6)

THE TWO EXITS ARE INERT, AND THAT IS THE SOURCE'S OWN SHAPE -- not a modelling
shortcut. Each `strategy.exit` takes an order id that happens to equal an entry
id ("Buy" / "Sell") but a `from_entry` of "longExit_AT_6" / "shortExit_AT_6";
those two names are CONDITION variables in the source and are never used as an
entry id anywhere in the file. Pine books an exit against the entry it names, so
neither call ever has an entry to close, and the port transcribes both calls
verbatim -- `when=`, `stop=` and argument order included. A position in this
strategy is therefore closed only by the opposite entry reversing it.

`AlphaTrend` is a ratchet: each bar holds the previous value or steps to that
bar's band, so it is walked bar by bar, and `nz(AlphaTrend[1])` collapses the
first bar's na to 0 exactly as the source does.

`strategy()` declares only overlay, format, precision, title, shorttitle and
`pyramiding=0`; every other property is Pine's documented default: initial
capital 1000000 USD, `default_qty_type = fixed` / 1 contract, commission 0%.

The `/*backtest` header declares `period: 1d` on `Futures_Binance` BTC_USDT, so
`timeframe` is "1d". `basePeriod: 1h` is the FMZ backtester's own fill
granularity, not the strategy's period.

FIDELITY -- every claim below is read off the source or measured on a run; the
measurements are stated where they exist and marked where they do not.

* `ta.mfi` is not in the shared layer, so `_pine_mfi` is written out from the
  standard rolling-sum definition (see its docstring). It is the same body the
  other batch_001 AlphaTrend ports use, so one reading of `ta.mfi` serves the
  family. The length is the `AP` input here, which is DIFFERENT from
  `AlphaTrend-use-mfi` (that source hardcodes 14); the source passes `AP`.
* `ta.sma(ta.tr, 20)`: the ATR period is the literal 20 and is NOT `AP`. `AP`
  drives only the RSI/MFI gate. MEASURED on BTC/USDT:USDT 1d
  2024-01-01..2025-01-01 (367 bars): the port's ATR is na on bars 0..18 and first
  valid at index 19, and the resulting AlphaTrend line is likewise na on bars
  0..18 and first valid at index 19.
* Bare `ta.tr` in v5 is `handle_na = false`, i.e. na on the first bar; the
  shared `pine_ta.pine_tr` yields `high - low` there instead because its pandas
  `max(axis=1)` skips na. With `ta.sma` propagating na, the source's ATR-SMA is
  na on bars 0..19 and first valid at index 20 -- one bar later than this port's.
  That advances the whole upT/downT/AlphaTrend chain by one bar in the warmup
  region. This is the documented public-layer boundary PINE_SEMANTICS.md 3.7,
  recorded rather than patched locally.
* Pine treats an na ternary condition as false, so a warmup bar -- where the
  gate, ATR or `AlphaTrend[1]` is na -- falls through to the `downT` leg and
  `AlphaTrend` itself becomes na rather than 0. Plain numpy comparisons against
  NaN are also false, which reproduces it.
* `exit1 = input.bool(true, ...)` is declared and NEVER read: the source body
  mentions `exit1` exactly once, on its own declaration line. It is an `input`,
  so it is carried in `source_defaults` for provenance and has no other effect.
* `exit1_condition = close < AlphaTrend ? 1.0 : na` IS computed every bar and IS
  passed as the `stop=` leg of both exits. It is kept, but it can never arm: the
  stops are bound to entry ids that do not exist, so the engine leaves both
  orders resting. `source_reproduce_stops` is False for the same reason.
* SHARED-LAYER RISK, MEASURED: the two `strategy.exit` calls reuse the entry ids
  "Buy" / "Sell" as their order id, and `PineBroker._place` drops every pending
  order sharing an id with a new `exit`. On a bar where a `Buy` entry is placed
  and the `Buy` exit is placed in the same script pass, the entry is removed
  from the pending list and never fills. Whether Pine keys entry and exit orders
  in one id namespace is not published; the engine models one namespace, and the
  port does not work around it. MEASURED: the collision never fires on the data
  available here. On BTC/USDT:USDT 1d 2024-01-01..2025-01-01 (367 bars) there are
  4 `longCondition` bars and 2 `shortCondition` bars, and 0 bars where
  `longCondition` and `shortExit_AT_6` are both true and 0 where `shortCondition`
  and `longExit_AT_6` are both true; over the ENTIRE local 1d history (2453 bars,
  2020-01-01..2026-09-18; 21 `longCondition` bars, 11 `shortCondition` bars) both
  counts are still 0. This does NOT mean the two are mutually exclusive -- they
  are not, `shortExit_AT_6` bears no logical relation to `longCondition` -- only
  that the co-occurrence the risk needs does not happen to occur in the data
  available here. The risk is therefore recorded unexercised, not dismissed.
* `alertcondition` and the three `plot` calls are display-only and place no
  order.
* MD-vs-CODE DISAGREEMENT 1: the md's prose says "策略的出场条件是:当价格跌破
  AlphaTrend指标时平仓" / "The exit condition of the strategy is: when the price
  falls below the AlphaTrend indicator, close the position". The CODE has no
  such exit: `exit1_condition` (close < AlphaTrend) is only ever handed to a
  `strategy.exit` whose `from_entry` names a nonexistent entry, so nothing is
  ever closed by it. The prose is contradicted by the code; the code wins.
* MD-vs-CODE DISAGREEMENT 2: the md's Strategy Arguments table gives
  `v_input_float_1` a default of `true` for `Multiplier`, while the source reads
  `input.float(1, 'Multiplier', step=0.1)`. The code's value 1.0 is used. The
  other six rows of that table (14, close/0, false, 20, 2, true) do match the
  six `input()` calls.
* The md's code block is line-for-line identical to sources/SM_33c8278404801cb5.pine;
  no other difference was found.
* No `security()` call, no `barstate.isrealtime` branch, no repainting, no
  future-data reference.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  of order quantities are not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_mfi(source: pd.Series, volume: pd.Series, length: int) -> pd.Series:
    """Pine `ta.mfi(source, length)` from the standard rolling-sum definition.

    Both terms are windowed with a plain rolling SUM, not RMA:

        upper = sum(volume * (ta.change(source) <= 0 ? 0 : source), length)
        lower = sum(volume * (ta.change(source) >= 0 ? 0 : source), length)
        mfi   = 100 - 100 / (1 + upper / lower)

    The MFI's standard definition is a ratio of summed money flows, and the
    published Pine reimplementations use a rolling sum. TradingView's own
    built-in source is not available to compare against, so this is the reading
    the whole batch_001 AlphaTrend family shares, not a verified copy.

    A bar whose `ta.change(source)` is na (the first bar) fails both
    comparisons, so Pine's ternary takes its false branch and that bar's
    turnover is counted on BOTH sides -- matched here by numpy's False for a
    NaN comparison. A window whose `lower` sums to zero is left to IEEE
    division rather than special-cased: `upper > 0` then gives `inf` and
    `mfi = 100`, and a window in which every change is exactly zero gives
    `0/0 = nan` and therefore `mfi = nan`. Which of those the platform returns,
    and whether it substitutes 50 instead, is UNPUBLISHED here; the gate
    `mfi >= 50` is True for 100 and False for nan, so the choice matters and is
    recorded rather than guessed. MEASURED on BTC/USDT:USDT 1d: over the ENTIRE
    local history (2453 bars, 2020-01-01..2026-09-18; 2440 windows with both
    terms defined) `lower` sums to exactly 0 on 0 windows, and over the default
    verification window 2024-01-01..2025-01-01 (367 bars; 354 defined windows)
    likewise 0. So no degenerate window is exercised by the data available here
    -- which is a statement about the data, not about the platform's rule.
    """
    change = ta.pine_change(source)
    values = source.to_numpy(dtype=float)
    volume_values = volume.to_numpy(dtype=float)
    upper_term = np.where((change <= 0).to_numpy(), 0.0, values) * volume_values
    lower_term = np.where((change >= 0).to_numpy(), 0.0, values) * volume_values
    index = source.index
    upper = pd.Series(upper_term, index=index).rolling(length, min_periods=length).sum()
    lower = pd.Series(lower_term, index=index).rolling(length, min_periods=length).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        return 100.0 - 100.0 / (1.0 + upper / lower)


class SMAlphaTrendBollinger_33c827(PinePortBase, IStrategy):
    source_id = "SM_33c8278404801cb5"
    source_file = (
        "AlphaTrend和布林带相结合的均值回归趋势跟踪策略AlphaTrend-and-Bollinger-Bands-"
        "Combined-Mean-Reversion-Trend-Following-Strategy.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "coeff": 1.0,
        "AP": 14,
        "src": "close",
        "novolumedata": False,
        "BBPeriod": 20,
        "BBMultiplier": 2.0,
        "exit1": True,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop can ever arm: both strategy.exit calls name a from_entry that is
    # not an entry id, so the engine leaves them resting.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Both strategy.exit calls pass a from_entry ('longExit_AT_6' / "
        "'shortExit_AT_6') that is a CONDITION variable in the source, never an "
        "entry id ('Buy' / 'Sell'), so neither call ever closes anything. Both "
        "are transcribed verbatim and stay inert; a position ends only by the "
        "opposite entry reversing it.",
        "MD-vs-CODE 1: the md prose says the strategy exits when price falls "
        "below AlphaTrend. The code has no such exit -- exit1_condition is only "
        "ever the stop= leg of the two inert exits. Code wins.",
        "MD-vs-CODE 2: the md's argument table lists Multiplier's default as "
        "`true`; the source reads input.float(1, 'Multiplier'). 1.0 is used.",
        "exit1 = input.bool(true, ...) is declared and never read (the source "
        "mentions it only on that line); kept in source_defaults for provenance.",
        "ATR = ta.sma(ta.tr, 20): 20 is a literal, NOT the AP input; AP drives "
        "only the RSI/MFI gate.",
        "Bare ta.tr in v5 is handle_na=false (na on bar 0); pine_ta.pine_tr "
        "returns high - low there instead, so this port's ATR is first valid one "
        "bar earlier than the source's and the whole upT/downT/AlphaTrend chain "
        "shifts by one bar in the warmup region. PINE_SEMANTICS 3.7 boundary: "
        "recorded, not patched locally.",
        "ta.mfi is not in the shared layer; _pine_mfi follows the rolling-sum "
        "definition shared with the other batch_001 AlphaTrend ports. "
        "TradingView's built-in source is not available to compare against.",
        "A ta.mfi window whose `lower` sums to zero is left to IEEE division "
        "(upper > 0 -> 100, all-zero window -> nan) rather than special-cased to "
        "50; the platform's convention is unpublished and the gate mfi >= 50 "
        "differs between those values. Measured on BTC/USDT:USDT 1d: 0 degenerate "
        "windows over the whole local history (2440 defined windows) and 0 over "
        "the verification window (354 defined windows) -- a fact about the data, "
        "not a resolution of the platform's rule.",
        "Pine treats an na ternary condition as false, so warmup bars fall "
        "through to the downT leg and AlphaTrend is na, not 0; nz(AlphaTrend[1]) "
        "collapses the first bar's na to 0.",
        "SHARED-LAYER RISK: the exits reuse the entry ids 'Buy' / 'Sell' as "
        "their order id, and PineBroker._place drops every pending order sharing "
        "an id with a new exit. A same-bar Buy entry plus Buy exit therefore "
        "loses the entry. Pine's id namespace for entry vs exit orders is not "
        "published; the port does not work around the engine's model. Measured: "
        "the co-occurrence never happens in the available data -- 0 such bars in "
        "the verification window and 0 over the whole local 1d history (21 "
        "longCondition and 11 shortCondition bars). The conditions are NOT "
        "mutually exclusive, so this is an unexercised risk, not a dismissed one.",
        "Measured on BTC/USDT:USDT 1d 2024-01-01..2025-01-01: the shared ATR is "
        "na on bars 0..18 and first valid at index 19, and AlphaTrend follows it "
        "(also na on 0..18). The source's own ATR-SMA would start one bar later "
        "(see the ta.tr note above).",
        "alertcondition and the three plot calls are display-only; no order.",
        "/*backtest declares period: 1d on Futures_Binance BTC_USDT; "
        "basePeriod: 1h is the FMZ backtester's fill granularity.",
        "No security() call, no barstate.isrealtime branch, no repainting and no "
        "future-data reference.",
        "CHAIN: verify_chain --port SM_33c8278404801cb5 returns 'match' on "
        "BTC/USDT:USDT 1d 2024-01-01..2025-01-01 (2 engine trades vs 2 framework "
        "trades, every mismatch count 0, max_pnl_gap 4.3e-12). A pass says the "
        "two implementations of THIS port agree; it does not say the engine "
        "reads Pine correctly (see PINE_SEMANTICS 5).",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding of order quantities are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        coefficient = float(params["coeff"])
        gate_period = int(params["AP"])
        novolumedata = bool(params["novolumedata"])
        bb_period = int(params["BBPeriod"])
        bb_multiplier = float(params["BBMultiplier"])

        # ATR = ta.sma(ta.tr, 20) -- ta.tr with handle_na = false, and the
        # period 20 is a literal in the source, not the AP input.
        true_range = ta.pine_tr(dataframe, handle_na=False)
        atr = ta.pine_sma(true_range, 20)

        # Gate: novolumedata ? ta.rsi(src, AP) >= 50 : ta.mfi(hlc3, AP) >= 50.
        # `src = input(close)` is read ONLY by the RSI arm of this ternary.
        hl3 = ta.pine_source(dataframe, "hlc3")
        mfi = _pine_mfi(hl3, dataframe["volume"], gate_period)
        if novolumedata:
            source = ta.pine_source(dataframe, str(params["src"]))
            gate = ta.pine_rsi(source, gate_period) >= 50
        else:
            gate = mfi >= 50
        gate_values = gate.to_numpy(dtype=bool)

        low = dataframe["low"].to_numpy(dtype=float)
        high = dataframe["high"].to_numpy(dtype=float)
        atr_values = atr.to_numpy(dtype=float)
        up_t = low - atr_values * coefficient
        down_t = high + atr_values * coefficient

        size = len(dataframe)
        alpha_trend = np.full(size, np.nan)
        for i in range(size):
            # nz(AlphaTrend[1]): na collapses to 0 on the first bar.
            previous = alpha_trend[i - 1] if i >= 1 else np.nan
            reference = previous if np.isfinite(previous) else 0.0
            if gate_values[i]:
                # upT < nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : upT
                alpha_trend[i] = reference if up_t[i] < reference else up_t[i]
            else:
                # downT > nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : downT
                alpha_trend[i] = reference if down_t[i] > reference else down_t[i]
        alpha = pd.Series(alpha_trend, index=dataframe.index)

        # Bollinger Bands: basis / ta.stdev (ddof=0, as Pine computes it).
        close = dataframe["close"]
        basis = ta.pine_sma(close, bb_period)
        dev = ta.pine_stdev(close, bb_period)
        upper = basis + bb_multiplier * dev
        lower = basis - bb_multiplier * dev

        dataframe["pine_alphatrend"] = alpha
        dataframe["pine_basis"] = basis
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        dataframe["pine_long_condition"] = (
            ta.pine_crossover(close, upper) & ta.pine_crossover(alpha, alpha.shift(1))
        ).to_numpy()
        dataframe["pine_short_condition"] = (
            ta.pine_crossunder(close, lower) & ta.pine_crossunder(alpha, alpha.shift(1))
        ).to_numpy()
        dataframe["pine_long_exit_at_6"] = ta.pine_crossover(close, alpha).to_numpy()
        dataframe["pine_short_exit_at_6"] = ta.pine_crossunder(close, alpha).to_numpy()
        # exit1_condition = close < AlphaTrend ? 1.0 : na
        dataframe["pine_exit1_condition"] = np.where(
            (close < alpha).to_numpy(), 1.0, np.nan
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "long_exit_at_6": dataframe["pine_long_exit_at_6"].to_numpy(),
            "short_exit_at_6": dataframe["pine_short_exit_at_6"].to_numpy(),
            "exit1_condition": dataframe["pine_exit1_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Buy", strategy.long, when=longCondition)
        broker.entry("Buy", "long", when=bool(ctx["long_condition"][i]))
        # strategy.entry("Sell", strategy.short, when=shortCondition)
        broker.entry("Sell", "short", when=bool(ctx["short_condition"][i]))
        # strategy.exit("Buy", "longExit_AT_6", stop = exit1_condition,
        #               when = shortExit_AT_6)
        broker.exit(
            "Buy", "longExit_AT_6",
            when=bool(ctx["short_exit_at_6"][i]),
            stop=float(ctx["exit1_condition"][i]),
        )
        # strategy.exit("Sell", "shortExit_AT_6", stop = exit1_condition,
        #               when = longExit_AT_6)
        broker.exit(
            "Sell", "shortExit_AT_6",
            when=bool(ctx["long_exit_at_6"][i]),
            stop=float(ctx["exit1_condition"][i]),
        )
