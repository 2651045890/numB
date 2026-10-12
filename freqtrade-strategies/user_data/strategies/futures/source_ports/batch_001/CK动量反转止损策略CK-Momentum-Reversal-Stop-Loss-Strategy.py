"""Port of sources/SM_05bd5a36c6e5932c.pine (batch_001/CK动量反转止损策略CK-Momentum-Reversal-Stop-Loss-Strategy.md).

Pine v4 "Chande Kroll Stop". Two ATR-offset channels whose common direction
flips a state, and the two flips feed a pair of market entries:

    hiP=9, hix=1, hiQ=7, loP=9, lox=1, loQ=5, Xr=false, tl=true, sbg=true
    first_high_stop = highest(high, hiP) - hix * atr(hiP)
    first_low_stop  = lowest(high,  loP) + lox * atr(loP)      // NOTE: `high`
    stop_short = highest(first_high_stop, hiQ)
    stop_long  = lowest(first_low_stop,   loQ)
    cklow = stop_short
    ckhigh = stop_long

    Xdn = cklow < cklow[1] and ckhigh < ckhigh[1]
    Xup = cklow > cklow[1] and ckhigh > ckhigh[1]

    Xp = 0.0
    Xp := Xdn ? -1 : Xup ? 1 : Xp[1]
    Xdf = Xr ? (Xup and Xp[1] == -1) : (Xdn and Xp[1] ==  1)
    Xuf = Xr ? (Xdn and Xp[1] ==  1) : (Xup and Xp[1] == -1)

    testTF = time >= timestamp(FY,FM,FD,00,00) and time <= timestamp(TY,TM,TDy,23,59)
    if testTF
        strategy.entry("Long ", strategy.long,  comment=" Long ", when=Xuf)
        strategy.entry("Short", strategy.short, comment=" Short", when=Xdf)

`strategy()` declares `initial_capital=100000`, `calc_on_every_tick=true`,
`default_qty_type=strategy.percent_of_equity` and `default_qty_value=10`. Commission
is not declared, so Pine's documented 0% applies; pine's documented default
`pyramiding` is used for the port (see the note below), and
`process_orders_on_close` is not declared either. The `/*backtest` header
declares `period: 1h`, so `timeframe` is "1h".

`Xup` and `Xdn` are mutually exclusive (one needs both channels rising, the other
both falling), and the state `Xp` only changes on one of them, so `Xuf` and `Xdf`
can never both be true and no same-direction entry can stack. Both orders are
market orders, so the engine fills them at the next bar's open. The source has no
strategy.exit / strategy.close / close_all -- the "stop" of the title is the
channel, which is only plotted -- so a position is only ever changed by an
opposite entry, which the engine nets and reverses in one fill
(PINE_SEMANTICS.md 1.1). Hence `can_short` is True and
`source_reproduce_stops` is False.

FIDELITY:

* `Xp` is a Pine series variable with history (`Xp = 0.0` then `:=` reading
  `Xp[1]`), so it is an explicit recursion. It is na until the first bar on
  which Xdn or Xup holds -- `Xp[1]` has no history on bar 0 and every later bar
  inherits that na until a flip seeds it. Comparisons against that na
  (`Xp[1] == 1`, `Xp[1] == -1`) are false in Pine, so the port seeds the
  recursion with nan and compares with `==`.
* `atr(length)` is v4's builtin: `rma(max(high-low, |high-close[1]|,
  |low-close[1]|), length)`. `pine_ta.pine_atr` supplies it, including the
  first-bar `handle_na` seeding that PINE_SEMANTICS.md 3.7 records as a shared
  boundary: `ta.rma` seeds one bar earlier than TradingView's `handle_na=false`
  `ta.tr` would, which shifts the whole ATR series by that one bar.
* `lowest(high, loP)` takes `high` as its SOURCE, not `low` -- almost certainly a
  slip in the original (the symmetric line above uses `highest(high, hiP)`), but
  it is what the source computes and it changes both channel levels, so it is
  reproduced verbatim rather than "corrected".
* `hix = input(1, step=0.1)` and `lox = input(1, step=0.1)` are INT inputs whose
  default is 1 (`step` only constrains the dialog); the multipliers are 1.
  The source's own Strategy-Arguments table in the md prints them as `true`,
  which is the table's rendering of the integer 1, not a boolean -- the code is
  followed.
* `testTF` gates BOTH entries on the bar's time. It is kept as a real gate, with
  the timestamps built in UTC (PINE_SEMANTICS.md 3.4: no exchange timezone is
  known offline; this data is UTC). With the declared 2021-09-01 .. 2032-01-01
  window the gate is open for the entire locally available history, so it does
  not change the modelled trades -- but it is implemented rather than dropped.
* MD vs SOURCE (recorded, not reconciled): the md's prose describes the reversal
  as "上通道线开始下降,下通道线开始上升" (upper falls while lower rises), while the
  code requires BOTH channels to fall for Xdn and BOTH to rise for Xup. The md
  also presents this as a stop-loss strategy; the source never places a stop
  order -- the channels feed the state machine that gates the two entries.
* `calc_on_every_tick=true` is declared but NOT modelled: the shared engine (and
  Freqtrade's backtester) evaluate the script once per bar close, so an order the
  original platform could have placed and filled intrabar here waits for the
  close. Same class of gap as PINE_SEMANTICS.md 二.2 / 二.5.
* `pyramiding` is not declared by the source. The port uses 0, the value the
  repository records as Pine's documented default; it is recorded here explicitly
  because Pine v4's `pyramiding` default has been read both ways, and on THIS
  source the choice cannot matter: Xuf and Xdf are mutually exclusive and gated
  by the flip state, so no second same-direction entry is ever placed.
* `alert()` / `alertcondition()` / `plotshape` / `plotchar` / `bgcolor` are
  display or alerting only and place no order (PINE_SEMANTICS.md 二.7). The two
  string `input("My Long  Msg")` / `input("My Short Msg")` calls live inside
  `alert()` and are carried in `source_defaults` as the source states them,
  never read.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6, 二.4).
"""
from freqtrade.strategy import IStrategy

import numpy as np
import pandas as pd

import pine_ta as ta
from pine_port_base import PinePortBase


def pine_ck_state(xdn: pd.Series, xup: pd.Series) -> pd.Series:
    """`Xp := Xdn ? -1 : Xup ? 1 : Xp[1]`, seeded with na.

    A Pine series variable: carried forward until one of the two channel
    conditions fires. `Xp[1]` on the first bar is na, and that na propagates
    through the carry branch until the first flip, which is what makes
    `Xp[1] == 1` / `Xp[1] == -1` false on all the bars before it.
    """
    down = xdn.to_numpy(dtype=bool)
    up = xup.to_numpy(dtype=bool)
    out = np.full(len(down), np.nan)
    state = np.nan
    for i in range(len(down)):
        if down[i]:
            state = -1.0
        elif up[i]:
            state = 1.0
        out[i] = state
    return pd.Series(out, index=xdn.index, dtype=float)


class SMChandeKrollStop_05bd5a(PinePortBase, IStrategy):
    source_id = "SM_05bd5a36c6e5932c"
    source_file = "CK动量反转止损策略CK-Momentum-Reversal-Stop-Loss-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "hiP": 9,
        "hix": 1,
        "hiQ": 7,
        "loP": 9,
        "lox": 1,
        "loQ": 5,
        "Xr": False,
        "tl": True,
        "sbg": True,
        "FY": 2021,
        "FM": 9,
        "FD": 1,
        "TY": 2032,
        "TM": 1,
        "TDy": 1,
        "longMsg": "My Long  Msg",
        "shortMsg": "My Short Msg",
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 10.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`Xp` is a Pine series variable with history (`Xp = 0.0` then `:=` "
        "reading `Xp[1]`); reproduced as an explicit recursion seeded with na, "
        "so `Xp[1] == 1` / `== -1` are false on every bar before the first flip "
        "-- Pine's na comparison semantics.",
        "`lowest(high, loP)` uses `high` as its source, not `low` (asymmetric "
        "with the `highest(high, hiP)` line above it). Reproduced verbatim; it "
        "moves both channel levels, so 'correcting' it would change the source's "
        "behaviour.",
        "`atr(length)` is v4's builtin, modelled by pine_ta.pine_atr. Its "
        "first-bar handle_na seeding is the shared boundary recorded in "
        "PINE_SEMANTICS.md 3.7, which shifts the ATR series by one bar at the "
        "start.",
        "`hix` / `lox` are integer inputs of 1 (step=0.1 constrains the dialog "
        "only). The md's Strategy-Arguments table renders them as `true`, which "
        "is that table's display of the integer 1; the code is followed.",
        "`testTF` is implemented as a real time gate on both entries, built in "
        "UTC (PINE_SEMANTICS.md 3.4). With the declared 2021-09-01 .. 2032-01-01 "
        "window it is open across the whole locally available history, so it "
        "does not change the modelled trades.",
        "MD vs SOURCE: the prose says the reversal is the upper channel falling "
        "while the lower rises; the code requires BOTH channels to move the same "
        "way (Xdn both down, Xup both up). The prose also calls this a stop-loss "
        "strategy; no stop order is ever placed -- the channels gate the two "
        "market entries. Recorded, not reconciled.",
        "`calc_on_every_tick=true` is declared by the source but not modelled: "
        "the shared engine and Freqtrade both evaluate once per bar close, so an "
        "order the original platform could place and fill intrabar waits for the "
        "close here (same class as PINE_SEMANTICS.md 二.2 / 二.5).",
        "`pyramiding` is not declared; the port uses 0, the repository's "
        "recorded Pine default. The choice cannot change this source's trades: "
        "Xuf and Xdf are mutually exclusive and gated by the flip state, so a "
        "same-direction entry can never be placed twice.",
        "The two `input(\"My Long Msg\")` / `input(\"My Short Msg\")` strings sit "
        "inside `alert()` and are never read; carried in source_defaults as "
        "declared. alert/alertcondition/plot* place no orders "
        "(PINE_SEMANTICS.md 二.7).",
        "Commission is not declared (0% per Pine's documented default), and "
        "initial capital IS declared (100000). Leverage, margin, liquidation, "
        "funding and contract-step rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        high, low = dataframe["high"], dataframe["low"]
        hi_p, lo_p = int(params["hiP"]), int(params["loP"])
        first_high_stop = (
            ta.pine_highest(high, hi_p) - float(params["hix"]) * ta.pine_atr(dataframe, hi_p)
        )
        first_low_stop = (
            ta.pine_lowest(high, lo_p) + float(params["lox"]) * ta.pine_atr(dataframe, lo_p)
        )
        stop_short = ta.pine_highest(first_high_stop, int(params["hiQ"]))
        stop_long = ta.pine_lowest(first_low_stop, int(params["loQ"]))
        cklow, ckhigh = stop_short, stop_long
        xdn = (cklow < cklow.shift(1)) & (ckhigh < ckhigh.shift(1))
        xup = (cklow > cklow.shift(1)) & (ckhigh > ckhigh.shift(1))
        xp = pine_ck_state(xdn, xup)
        xp_prev = xp.shift(1)
        reverse = bool(params["Xr"])
        # Xr=false: Xdf = Xdn and Xp[1] == 1 ; Xuf = Xup and Xp[1] == -1
        # Xr=true : Xdf = Xup and Xp[1] == -1 ; Xuf = Xdn and Xp[1] == 1
        if reverse:
            xdf = xup & (xp_prev == -1.0)
            xuf = xdn & (xp_prev == 1.0)
        else:
            xdf = xdn & (xp_prev == 1.0)
            xuf = xup & (xp_prev == -1.0)
        dataframe["pine_first_high_stop"] = first_high_stop
        dataframe["pine_first_low_stop"] = first_low_stop
        dataframe["pine_stop_short"] = stop_short
        dataframe["pine_stop_long"] = stop_long
        dataframe["pine_xdn"] = xdn
        dataframe["pine_xup"] = xup
        dataframe["pine_xp"] = xp
        dataframe["pine_xdf"] = xdf
        dataframe["pine_xuf"] = xuf
        index = dataframe.index
        # timestamp(FY,FM,FD,00,00) .. timestamp(TY,TM,TDy,23,59), built in UTC.
        # A tz-naive frame (some offline callers) gets naive bounds so the
        # comparison stays legal instead of raising.
        tz = getattr(index, "tz", None)
        start = pd.Timestamp(
            int(params["FY"]), int(params["FM"]), int(params["FD"]),
            tz="UTC" if tz is not None else None,
        )
        end = pd.Timestamp(
            int(params["TY"]), int(params["TM"]), int(params["TDy"]),
            hour=23, minute=59, tz="UTC" if tz is not None else None,
        )
        dataframe["pine_test_tf"] = (index >= start) & (index <= end)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "xuf": dataframe["pine_xuf"].to_numpy(),
            "xdf": dataframe["pine_xdf"].to_numpy(),
            "test_tf": dataframe["pine_test_tf"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        if not ctx["test_tf"][i]:
            return
        # strategy.entry("Long ", strategy.long,  comment=" Long ", when=Xuf)
        # strategy.entry("Short", strategy.short, comment=" Short", when=Xdf)
        # (one source line, "Long " first; the ids keep the source's spelling)
        broker.entry("Long ", "long", when=bool(ctx["xuf"][i]))
        broker.entry("Short", "short", when=bool(ctx["xdf"][i]))
