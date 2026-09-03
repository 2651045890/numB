# numB

本项目只保留与策略回测和择优直接相关的三部分：

- `freqtrade/`：保持不变的 Freqtrade 源码副本；实际回测调用 Conda 环境中的 Freqtrade 2026.7。
- `freqtrade-strategies/user_data/`：待回测的策略代码。
- `strategy_runner/`：策略发现、批量回测、指标比较和最优策略排名。
- `live_runner/`：你人工确认后，用来一键启动多个独立实盘实例。

`environment.yml` 用于重建 `freqtrade313` Conda 运行环境。

详细使用方法见 `strategy_runner/README.md`。
