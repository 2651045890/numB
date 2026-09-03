# Live Runner

`live_runner/` 是你人工确认策略后的一键实盘启动层，当前只允许
OKX USDT 本位永续合约（futures）。

推荐流程：

1. 先用 `strategy_runner/` 批量回测并排名。
2. 你人工挑出要实盘的一个或多个策略。
3. 用 `live_runner/launcher.py` 按策略和币种启动多个独立实例。

默认是 `dry-run`，只有显式传 `--live` 才会真正下单。

## 最常用命令

```bash
python live_runner/launcher.py --strategy FSampleStrategy --pairs BTC/USDT:USDT
```

这会使用默认的 `safe_dryrun` 预设，先跑模拟盘。

## 参数

- `--profile`：选择预设，默认 `safe_dryrun`。
- `--strategy`：策略类名，可重复传入。
- `--pairs`：交易对，可重复传入。
- `--live`：显式切到真仓。
- `--leverage`：统一合约杠杆，默认 1 倍，例如 `--leverage 3`。
- `--plan-only`：只生成计划和配置，不启动。
- `--mode`：固定为 `futures`。
- `--run-id`：指定本次输出目录名。

## 示例

```bash
python live_runner/launcher.py \
  --strategy FSampleStrategy \
  --strategy FSupertrendStrategy \
  --pairs BTC/USDT:USDT \
  --pairs ETH/USDT:USDT \
  --plan-only
```

这会生成一份计划，但不真正开跑。
