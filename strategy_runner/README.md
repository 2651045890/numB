# Strategy Runner

该目录从 `freqtrade/` 外部调用安装在 `../.venv` 中的 Freqtrade 2026.7。
框架以 wheel 形式安装，策略直接从 `freqtrade-strategies/user_data` 读取，
因此回测不会修改 Freqtrade 框架或策略源文件。

## 结构

- `orchestrator.py`：发现策略、分类现货/期货、逐个回测并记录失败原因
- `configs/spot.json`：OKX 现货 DOGE/USDT 回测配置
- `configs/futures.json`：Binance 永续 DOGE/USDT:USDT 回测配置
- `settings.json`：时间范围、最低交易数和排名权重
- `data/`：外部回测数据（Git 忽略）
- `runs/`：每次回测的 JSON、CSV 和日志（Git 忽略）
- `outputs/`：最终 XLSX 报告（Git 忽略）

## 使用

```bash
python3 strategy_runner/orchestrator.py inventory
.venv/bin/python strategy_runner/orchestrator.py run --mode spot --jobs 2
.venv/bin/python strategy_runner/orchestrator.py run --mode all --jobs 2
```

单个策略验证：

```bash
.venv/bin/python strategy_runner/orchestrator.py run --strategy Bandtastic --run-id smoke_bandtastic
```

`lookahead_bias/` 下的策略会运行但会在排名中标记为不合格；没有足够交易数、
缺少数据或与新版 Freqtrade 不兼容的策略会保留失败原因，不会从汇总中消失。

## 排名原则

默认综合分权重为：总收益 30%、Sharpe 25%、Sortino 15%、Calmar 15%、
最大回撤反向得分 15%。交易数少于 30 或已标记 lookahead bias 的策略不进入最佳候选。
