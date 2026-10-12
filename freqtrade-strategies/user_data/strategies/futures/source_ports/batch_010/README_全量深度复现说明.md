# batch_010 全量复现包

- 原始策略：500 个
- Python 策略文件：500 个（不含共享 runtime）
- 手工逐条审计深度版：20 个
- 逐策略源码解析 + 独立语义映射版：480 个
- PENDING：0 个

## 重要说明

这个包的原则是“不伪造等价性”。20 个手工审计策略包含显式指标、订单与状态实现；其余策略也不是空白模板，每个文件都保存其自己的输入、赋值、函数、控制条件、strategy.* 订单调用和 fidelity notes。对于 `request.security`、`var/varip`、数组、策略账户状态、FMZ 盘口/API 等无法仅靠 OHLCV 静态向量化保证等价的部分，代码会交给 bar-by-bar replay/平台 adapter，而不会捏造一个看似能跑但语义错误的信号。

`REPRODUCTION_STATUS.csv` 可逐文件审计处理方式、语言、订单调用数量与 fidelity gap。
