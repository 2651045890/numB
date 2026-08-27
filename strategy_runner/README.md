# Strategy Runner 目录与产物说明

`strategy_runner/` 是一个独立的 Freqtrade 策略批量回测器。它从
`../freqtrade-strategies/user_data/strategies/` 扫描策略，调用 Conda 环境
`freqtrade313` 中安装的 Freqtrade 2026.7，对每个策略分别回测，然后生成
可追溯的明细、排名和摘要。

它不会修改 Freqtrade 框架或策略源文件。每次执行 `inventory` 或 `run`
前都会检查外层 Git 中受跟踪的 `freqtrade/` 是否有未提交修改；如果有，
程序会拒绝继续，以保证回测基础一致。

## 整体数据流

```text
../freqtrade-strategies/user_data/strategies/   策略源码（只读）
data/okx/                  历史 K 线（输入）
configs/*.json            现货/期货回测配置
settings.json             时间范围与排名规则
          \                 |                 /
                    orchestrator.py
                           |
                           v
runs/<run-id>/             日志、原始结果、明细和排名
```

## 顶层文件和目录

| 路径 | 作用 | 何时生成/变化 |
|---|---|---|
| `orchestrator.py` | 主入口；扫描策略、分类现货/期货、并发调用 Freqtrade、保存失败原因、汇总和排名。 | 手工维护，运行不会改它 |
| `settings.json` | 指定 Freqtrade 可执行文件、默认时间段、最低交易数和排名权重。 | 手工维护 |
| `configs/` | 存放传给 Freqtrade 的现货和永续合约配置。 | 手工维护 |
| `inventory.json` | 当前扫描到的策略快照：策略名、源文件、周期、模式、是否做空和 lookahead 标记。 | `inventory` 命令覆盖生成 |
| `data/` | 本地历史 K 线；编排器当前固定读取 `data/okx/`。 | 由数据下载/同步流程产生，本程序不下载 |
| `user_data/` | 通过 `--userdir` 传给 Freqtrade 的标准工作目录。 | 部分子目录可被 Freqtrade 命令写入 |
| `runs/` | 核心输出；每次 `run` 或 `merge` 生成独立的 `<run-id>/`。 | 运行时生成，Git 忽略 |
| `outputs/` | 预留给 XLSX 等二次加工报告。当前 `orchestrator.py` **不会**自动写入。 | 由后续脚本/人工生成，Git 忽略 |
| `test_orchestrator.py` | 验证策略发现/分类以及排名剔除逻辑。 | 测试代码 |
| `.gitignore` | 忽略行情、回测结果、报告、缓存和本地环境文件。 | 手工维护 |
| `__pycache__/` | Python 的 `.pyc` 字节码缓存；可删除且会自动重建，不是回测结果。 | Python 自动生成，Git 忽略 |

### `configs/`

- `configs/spot.json`：OKX 现货回测，交易对为 `DOGE/USDT`。
- `configs/futures.json`：OKX USDT 本位永续合约回测，交易对为
  `DOGE/USDT:USDT`，使用逐仓模式。

两者都使用 1000 USDT 模拟资金、最多 3 个同时持仓，不启用 Telegram 和
API Server。交易所密钥为空，用途是本地回测，不是实盘配置。

### `data/`

```text
data/
├── okx/
│   ├── DOGE_USDT-5m.feather       # OKX 现货 5 分钟 K 线
│   ├── DOGE_USDT-15m.feather      # 其他现货周期同理
│   └── futures/                   # OKX 期货/永续合约数据
└── binance/                            # Binance 数据，当前编排器不读取
```

`.feather` 是 Freqtrade 可读取的历史行情文件，文件名中的 `5m`、`1h`、
`1d` 表示 K 线周期。缺少策略需要的模式或周期时，失败原因会记入
`results.*` 和 `backtest.log`。

### `user_data/`

| 子目录 | Freqtrade 中的用途 | 本编排器当前的使用情况 |
|---|---|---|
| `strategies/` | 用户策略 | 不从这里读；实际读取 `../freqtrade-strategies/user_data/strategies/` |
| `data/` | Freqtrade 默认行情目录 | 不使用；`--datadir` 明确指向顶层 `data/okx/` |
| `backtest_results/` | Freqtrade 默认回测输出 | `--backtest-directory` 将结果改写到 `runs/<run-id>/...` |
| `logs/` | 常规 Freqtrade 日志 | 每个子进程的输出实际写入对应 `backtest.log` |
| `hyperopts/` | 自定义 Hyperopt 损失函数 | `run` 不使用 |
| `hyperopt_results/` | Hyperopt 优化结果 | `run` 不使用 |
| `freqaimodels/` | FreqAI 自定义模型 | `run` 不使用 |
| `notebooks/` | 研究和分析 Notebook | `run` 不使用 |
| `plot/` | 图表文件 | `run` 不使用 |

这些空目录主要是为了保持 Freqtrade 标准结构，不代表每次运行后都会有产物。

## 运行方式与产物

### 1. `inventory`：生成策略清单

```bash
conda activate freqtrade313
cd /Users/htq/Desktop/数字货币/numB
python strategy_runner/orchestrator.py inventory
```

默认覆盖生成 `strategy_runner/inventory.json`。它只用 Python AST 解析策略，
不导入策略，也不执行回测。字段含义：

- `name`：策略类名；`file`：相对策略源目录的路径。
- `timeframe`：策略 K 线周期；无法静态读取时默认为 `5m`。
- `mode`：`spot` 或 `futures`。`can_short = true` 或文件在 `futures/`
  路径下时归为期货，否则归为现货。
- `can_short`：是否声明允许做空。
- `lookahead_flag`：是否位于 `lookahead_bias/` 路径下。

### 2. `run`：执行回测

```bash
# 只跑现货
python strategy_runner/orchestrator.py run --mode spot --jobs 2

# 现货和期货都跑
python strategy_runner/orchestrator.py run --mode all --jobs 2

# 只验证一个策略
conda run -n freqtrade313 python strategy_runner/orchestrator.py run \
  --strategy Bandtastic --run-id smoke_bandtastic
```

不指定 `--run-id` 时使用当地时间生成 `YYYYMMDD_HHMMSS`。同名目录已存在时
会报错，不会覆盖旧结果。完整目录结构：

```text
runs/<run-id>/
├── inventory.json
├── results.json
├── results.csv
├── ranked_results.json
├── ranked_results.csv
├── summary.md
├── spot/
│   └── <策略名>/<时间范围>/
│       ├── backtest.log
│       ├── backtest-result-<timestamp>.zip
│       ├── backtest-result-<timestamp>.meta.json
│       └── .last_result.json
└── futures/
    └── <策略名>/<时间范围>/...
```

| 产物 | 作用 |
|---|---|
| `inventory.json` | 本次筛选后实际要跑的策略，用于确认覆盖范围。 |
| `results.json` | 最完整的汇总：当次设置快照，以及每个策略/时间段的状态、错误、耗时、路径和指标。每完成一项就重写，中途停止也能保留已完成项。 |
| `results.csv` | 上述明细的表格版，带 UTF-8 BOM，方便 Excel 打开和过滤。 |
| `ranked_results.json` | 在明细上增加 `eligible`、剔除原因、各指标得分、综合分和名次。 |
| `ranked_results.csv` | 排名表格版，适合筛选成功/失败、对比指标和制作报告。 |
| `summary.md` | 人类可读摘要：现货和期货最多前 10 名，以及成功、失败、被剔除数量。 |
| `spot/` / `futures/` | 对应模式的 Freqtrade 原始产物，按“策略名/时间范围”隔离；无该模式任务时不生成。 |
| `backtest.log` | 单个策略和时间段的 Freqtrade 完整输出；排查失败首先看它。 |
| `backtest-result-*.zip` | Freqtrade 原始回测包，包含统计和交易明细；编排器从中提取指标。 |
| `backtest-result-*.meta.json` | Freqtrade 为原始回测结果生成的元数据。 |
| `.last_result.json` | Freqtrade 指向该目录最新回测结果的索引。 |

回测失败仍会保留 `backtest.log`，并在 `results.json/csv` 写入
`status=failed` 和截取后的 `error`。至少一条成功时 `run` 返回退出码 0；
全部失败时返回 2。

### 3. `summarize`：重建排名

```bash
python strategy_runner/orchestrator.py summarize strategy_runner/runs/<run-id>
```

它读取已有 `results.json`，重新计算并覆盖 `ranked_results.json`、
`ranked_results.csv` 和 `summary.md`。它不重跑 Freqtrade，也不改原始
`spot/` 或 `futures/` 产物。

### 4. `merge`：合并多次任务

```bash
python strategy_runner/orchestrator.py merge \
  --run-id combined_run \
  strategy_runner/runs/run_a strategy_runner/runs/run_b
```

它按 `(模式, 策略名, 时间范围)` 去重，优先保留成功的重试记录，在新目录中
生成 `results.*`、`ranked_results.*` 和 `summary.md`。

`merge` **不复制**源任务的 `spot/`、`futures/`、日志和 zip，也不生成
`inventory.json`。合并记录的 `run_directory` 仍指向原任务的详细产物。

## 排名原则

排名先按 `mode + timerange` 分组，现货与期货、不同时段不直接混合比较。
策略进入排名必须同时满足：

- 回测成功；
- 交易数不少于 `minimum_trades`，当前为 30；
- 没有被路径标记为 `lookahead_bias`。

默认权重：总收益 30%、Sharpe 25%、Sortino 15%、Calmar 15%、最大回撤 15%。
指标先在同组合格策略中转为相对百分位，再加权；回撤越小得分越高。
`composite_score` 是组内相对得分，不是收益率，不应跨任务直接比较。当组内
只有一个合格策略时，它会得 100 分，这不代表绝对表现优秀。

## 常用参数

- `--mode spot|futures|all`：限制策略模式。
- `--timerange YYYYMMDD-YYYYMMDD`：覆盖默认时间段；可重复传入。
- `--strategy <策略类名>`：只跑指定策略；可重复传入。
- `--path-prefix <相对路径前缀>`：只跑某个策略子目录或文件前缀。
- `--limit N`：只取筛选后前 N 个策略，适合冒烟测试。
- `--jobs N`：同时运行 N 个 Freqtrade 子进程，越大越占 CPU 和内存。
- `--run-id <名称>`：指定 `runs/` 下的任务目录名。

## 快速查找问题

1. 先在 `summary.md` 看总体成功率和排名。
2. 在 `ranked_results.csv` 筛选 `eligible=false`，看 `eligibility_reason`。
3. 在 `results.csv` 筛选 `status=failed`，先看 `error`。
4. 根据 `run_directory` 进入具体目录，查看 `backtest.log` 完整错误。
5. 如果提示缺行情，核对 `data/okx/` 中是否有该模式、交易对和周期。

`lookahead_bias/` 下的策略仍会执行并保留结果，但会在排名中标记为不合格。
缺少数据、不兼容新版 Freqtrade 或其他原因失败的策略也会保留失败记录。
