# Freqtrade 策略

此 Git 仓库收录了可供 [Freqtrade](https://github.com/freqtrade/freqtrade) 使用的免费买卖策略。

所有策略原则上都支持 Freqtrade 2022.4 及以上版本。

## 免责声明

这些策略仅供学习使用。请勿投入你无法承受损失的资金。使用本软件的风险由你
自行承担，作者及所有关联方均不对你的交易结果负责。

请始终先进行策略回测，再以模拟运行（Dry-run）模式启动交易机器人。在理解其
工作原理和预期盈亏之前，请勿投入真实资金。

强烈建议使用者具备编程和 Python 基础，并阅读源代码以理解机器人的运行机制。

## 目录

- [免费交易策略](#免费交易策略)
- [分享策略并参与贡献](#分享你的策略并参与贡献)
- [常见问题](#常见问题)
  - [Freqtrade 是什么？](#freqtrade-是什么)
  - [这些策略包含什么？](#这些策略包含什么)
  - [如何安装策略？](#如何安装策略)
  - [如何测试策略？](#如何测试策略)
  - [如何创建或优化策略？](https://www.freqtrade.io/en/latest/strategy-customization/)

## 免费交易策略

本仓库中的策略可以免费使用，但均按原样提供，不附带任何保证。大多数策略应当
作为你编写自有策略的起点，而非可直接投入使用的成品。你可以按需使用或修改。

部分策略可能只适用于特定市场环境，另一些则较为通用。针对实际使用的交易所和
交易对进一步优化，通常会获得更好的结果。

请注意，结果会在很大程度上取决于回测使用的交易对、K 线周期和时间范围。因此，
请按照自己的实际场景运行回测，并自行评估每个策略。

上述结果仅用于大致展示预期交易次数；实际表现会因多种因素而有所不同。

## 分享你的策略并参与贡献

欢迎通过 [Issue](https://github.com/freqtrade/freqtrade-strategies/issues/new) 或
[Pull Request](https://github.com/freqtrade/freqtrade-strategies/pulls) 提交策略、意见、
优化方案和代码改动，共同完善本仓库。

## 常见问题

### Freqtrade 是什么？

[Freqtrade](https://github.com/freqtrade/freqtrade) 是一个使用 Python 编写的免费开源
加密货币交易机器人。它旨在支持各大主流交易所，并可通过 Telegram 控制；内置
回测、绘图、资金管理工具，以及基于机器学习的策略优化功能。

### 这些策略包含什么？

每个策略包含：

- [x] **最低投资回报率（Minimal ROI）**：针对策略优化的最低投资回报率。
- [x] **止损（Stoploss）**：优化后的止损设置。
- [x] **买入信号**：由 Hyperopt 得出，或基于现有交易策略设计。
- [x] **卖出信号**：由 Hyperopt 得出，或基于现有交易策略设计。
- [x] **指标**：运行策略所需的指标。

建议使用你关注的交易所和交易对回测多个策略，并针对实际交易市场进行微调。

### 如何安装策略？

首先需要一个[可正常运行的 Freqtrade](https://freqtrade.io)。

确认机器人版本正确后，按以下步骤操作：

1. 选择所需策略。本仓库的全部策略均位于
   [user_data/strategies](https://github.com/freqtrade/freqtrade-strategies/tree/main/user_data/strategies)。
2. 复制策略文件。
3. 将文件粘贴到你的 `user_data/strategies` 文件夹中。
4. 使用参数 `--strategy <策略类名>` 运行机器人，例如：
   `freqtrade trade --strategy Strategy001`。

更多信息请参阅[回测文档](https://www.freqtrade.io/en/latest/backtesting/)和
[策略定制文档](https://www.freqtrade.io/en/latest/strategy-customization/)。

### 如何测试策略？

假设你选择了策略 `strategy001.py`：

#### 简单回测

```bash
freqtrade backtesting --strategy Strategy001
```

#### 更新测试数据

```bash
freqtrade download-data --days 100
```

*注意：* 通常建议使用固定时间段的静态回测数据，以便比较不同结果。

更多信息请查阅[官方回测文档](https://www.freqtrade.io/en/latest/backtesting/)。
