# numB

OKX 策略回测与实盘。命令都在 numB 根目录下运行。

## 环境

```bash
conda activate freqtrade313
```

`environment.yml` 用于重建这个环境。

代理按这个顺序取，先命中先用：`run --proxy` > 环境变量 `STRATEGY_RUNNER_PROXY` >
`strategy_runner/settings.json` 的 `proxy`（空串＝直连）。`--proxy` 只影响这一次运行，
并记进该次运行的 `results.json`（`settings.proxy`）。回测也必须联网——freqtrade 每次启动
都要向交易所 `load_markets()`，出口不通时任何 stage 都会报 `Could not load markets`。

## 目录

| 目录 | 作用 |
|---|---|
| `freqtrade-strategies/user_data/strategies/` | 策略代码（`futures/` 合约、`spot/` 现货） |
| `strategy_runner/` | 回测调度：扫策略、下数据、批量回测、排名 |
| `live_runner/` | 实盘启动，默认 dry-run，加 `--live` 才真下单 |
| `strategy_workspace/` | 行情数据与回测结果 |
| `freqtrade/` | Freqtrade 源码副本；实际跑的是 conda 里的 2026.7 |

## 回测

```bash
# 只下载数据，不回测
python strategy_runner/orchestrator.py run --stage data --mode futures --jobs 2

# 只回测，不下载（用本地已有数据）
python strategy_runner/orchestrator.py run --stage backtest --mode futures --jobs 2

nohup python -u strategy_runner/orchestrator.py run --stage backtest --mode futures --jobs 2 > ./sweep_$(date +%m%d_%H%M).log 2>&1 & echo PID=$!


# 先下载再回测
python strategy_runner/orchestrator.py run --stage all --mode futures --jobs 2


## 一个策略，多个币种 --run-id目录名
python strategy_runner/orchestrator.py run --stage backtest --mode futures \
  --strategy FSupertrendStrategy \
  --jobs 1 --pair-jobs 4 \
  --run-id FSupertrendStrategy_all


python strategy_runner/orchestrator.py run --stage backtest --mode futures \
  --strategy SM123PatternQuant_0a0a82 \
  --jobs 1 --pair-jobs 4 \
  --run-id SM123PatternQuant_0a0a82_all
  




--jobs 1 同时运行策略数
--pair-jobs 4 同时运行币数

```

`--strategy`、`--pair` 都可重复，`--path-prefix` 按目录筛，`--mode spot` 切现货。

```bash
python strategy_runner/orchestrator.py run --stage backtest --mode futures \
  --strategy FSupertrendStrategy --pair SOL/USDT:USDT --pair ADA/USDT:USDT \
  --pair-jobs 1 --run-id sol_ada
```

## 每个币种一份日志

终端显示每个币种的开始、完成和成功/失败进度；`backtest.log` 在运行期间实时写入，可用 `tail -f <日志路径>` 查看。`--jobs` 控制策略并发，`--pair-jobs` 控制每个策略内的币种并发，设为 `1` 即串行。

**每个策略 × 每个币种跑一个独立的 freqtrade 进程**，因为 freqtrade 一个进程只写一份日志，
没法按币种拆。每个进程只回测一个币种（配置里白名单就写死那一个），各自留下完整日志。

结果在 `strategy_workspace/outputs/runs/<运行目录>/`：

- `results.json` — 逐策略 + 逐币种的原始结果；每个策略行和币种行都带
  `strict_filter`（`候选`/`剔除`）、`strict_filter_reason`（卡在哪几条门槛）和
  `strict_filter_thresholds`（本次实际用的阈值）
- `backtest_results.xlsx` — 两张表：`币种排名`（主表）、`策略汇总`
- `<模式>/<策略>/<币种>/backtest.log` — 例如 `futures/FSupertrendStrategy/BTC_USDT_USDT/backtest.log`
- `configs/` — 该次运行每币种用的 freqtrade 配置
- `_user_data/` — freqtrade 自己的 `--userdir` 暂存区（空目录骨架等），不属于某次运行，
  下划线开头以示区别。**跑完可以整个删掉**，不影响已有结果。

重建已有运行的排名（不重跑回测）：`python strategy_runner/orchestrator.py summarize <运行目录>`
——改完 `strict_filter` 阈值后也用它重算筛选结果，不用重跑回测。

`timeframe`（例如 `1h`）是每根 K 线的粒度，Freqtrade 计算指标时必须明确一个粒度；
它不限制历史覆盖范围。`timerange=auto` 表示每个币种使用该 K 线周期下本地已有的全部历史，
不同币种可以按各自实际存在的数据起止时间回测。

每个币种的 `backtest.log` 最后一行会额外写入中文交易统计：总交易次数、盈利次数、
亏损次数和持平次数。相同数据在 `results.json` 中对应 `total_trades`、`wins`、
`losses` 和 `draws`。

合并多次运行：`python strategy_runner/orchestrator.py merge --run-id <新目录> <运行目录> <运行目录>`

## 并发与耗时

回测很吃内存，进程数 = `--jobs` × `--pair-jobs`（默认 1 × 4）。超过 8 会告警。

`--backtest-timeout` 是**每个币种**的预算，不是每个策略的：一个卡住的策略最多会耗
`超时 × ⌈币种数 ÷ --pair-jobs⌉`。单个币种失败不会拖垮整个策略，日志和结果行都留着。

## 两条别改的配置

`strategy_runner/configs/*.json` 里：

- `stake_amount` 保持固定值 `100`，别改回 `"unlimited"`。浮动仓位会让收益率被资金曲线的路径污染——同样的信号，只因为交易顺序不同就得出不同结果。
- 币种之间必须分成独立进程跑（默认就是这样）。全部币种塞进一个进程会 OOM 被 SIGKILL。

`strategy_runner/settings.json` 里的两个交易数门槛：`minimum_trades: 30` 管策略表，
`minimum_trades_per_pair: 10` 管币种表。币种表按 `(模式, K线周期, 时间范围)` 分组打分——
不按周期分组的话，1m 策略的币种（几百笔）和 1d 策略的币种（几笔）会混进同一个百分位分布，
排出来的是交易频率而不是优势。某个分组一个都够不上 10 笔时会整体放宽到 1 笔并标
`已放宽交易数门槛`。

## 严格筛选（核心池）

`settings.json` 的 `strict_filter` 块是绝对门槛，和上面那套百分位打分是两件事：打分回答
「比同组其他行好」，筛选回答「按实盘会看的数字，它本身够不够格」。每个策略行和币种行都会
被盖上 `strict_filter`（`候选`/`剔除`）与 `strict_filter_reason`，xlsx 两张表里对应
`严格筛选结果`、`严格筛选未通过原因` 两列。`严格筛选未通过原因` 为空才是候选。

阈值一律是小数不是百分数（`0.10` 就是 10%），下限严格大于、上限严格小于，只有
`min_total_trades` 是 `>=`。指标缺失按不通过处理（和 pandas 里 `NaN > x` 为 False 一致）。
只能改数值不能加键——写了 `DEFAULT_STRICT_FILTER` 里没有的键会直接报错。

**两个门槛的口径随钱包变**：`min_cagr` 和 `max_max_drawdown_account` 是相对账户的百分比，
账户越大越显得无所谓。当前 `initial_capital` 是 1,000,000 而 `stake_amount` 固定 100，
这两个数被放大约 1000 倍——实测某次 447 行币种里 `cagr` 最大只有 0.34%，`min_cagr: 0.10`
永远不可能通过；`max_max_drawdown_account: 0.10` 则形同虚设（220 个成功行里 218 个通过，
最差的一行是 19.9%）。这两个值要按你实际打算投入的钱包口径重新标定，或者干脆改用不随
钱包变的 `sharpe`/`sortino`/`calmar`/盈亏比/美元金额来判断。
