"""
正常的交易过程BCT
"""

Freqtrade 专区:
https://www.wuzao.com/freqtrade/tutorial/installation

这个网页的教程可以:
https://www.learndatasci.com/tutorials/algo-trading-crypto-bot-python-strategy-backtesting/?ref=defiplot.com

中文
https://www.wuzao.com/document/freqtrade/hyperopt/

# 切换下标准版分支

# 切换到stable分支
git checkout stable

# 切换到develop分支
git checkout develop

# 配置代理，设置全局，即可下载。
"ccxt_config": { 
"httpsProxy": "http://127.0.0.1:7890",
"wsProxy": "http://127.0.0.1:7890"
},
"ccxt_async_config": {
    "httpsProxy": "http://127.0.0.1:7890",
    "wsProxy": "http://127.0.0.1:7890"
},

最受欢迎的开源python量化框架--（1）freqtrade使用教程
https://zhuanlan.zhihu.com/p/693171716

# 创建一个user_data文件
freqtrade create-userdir --userdir user_data

# 初始化文件夹
freqtrade new-config --config user_data/config.json

strategies/sample_strategy.py 是一个策略文件，用于编写交易策略。

freqtrade download-data --config user_data/config.json --pairs ETH/USDT:USDT --exchange binance --days 15 -t 15m

freqtrade download-data --config user_data/config.json --exchange binance --pairs BTC/USDT --timeframes 1h --days 1 

freqtrade new-strategy --strategy minimal_Strategy001 --template  minimal

freqtrade new-strategy --strategy advanced_Strategy001 --template  advanced

下载数据:
freqtrade download-data [选项]


freqtrade download-data --pairs ETH/USDT:USDT --exchange binance --days 15 -t 15m

freqtrade download-data --pairs BTC/USDT:USDT --exchange binance --days 15 -t 15m

- 数据下载命令:
freqtrade download-data [选项]

存储到:
user_data/data

freqtrade backtesting --config user_data/config.json --strategy BbandRsi


"""
- 启动和环境信息
2025-09-12 14:01:16,559 - freqtrade - INFO - freqtrade 2025.8
👉 启动了 Freqtrade，版本是 2025.8（稳定版，不是 dev 版）。

2025-09-12 14:01:17,026 - numexpr.utils - INFO - NumExpr defaulting to 8 threads.
👉 NumExpr 库自动选择了 8 个线程来加速数值计算。

- 配置加载
2025-09-12 14:01:18,074 - freqtrade.configuration.load_config - INFO - Using config: user_data/config.json ...
👉 使用的配置文件是 user_data/config.json。


2025-09-12 14:01:18,077 - freqtrade.loggers - INFO - Enabling colorized output.
2025-09-12 14:01:18,077 - freqtrade.loggers - INFO - Logfile configured
2025-09-12 14:01:18,077 - freqtrade.loggers - INFO - Verbosity set to 0
👉 启用了彩色日志输出，日志文件已配置，详细程度为默认。

2025-09-12 14:01:18,077 - freqtrade.configuration.configuration - INFO - Using exchange binance
👉 交易所选择的是 Binance。

2025-09-12 14:01:18,078 - freqtrade.configuration.configuration - INFO - Using user-data directory: /Users/htq/Desktop/真正的金融/币圈/freqtrade/user_data ...
👉 用户数据目录路径。

2025-09-12 14:01:18,079 - freqtrade.configuration.configuration - INFO - Using data directory: /Users/htq/Desktop/真正的金融/币圈/freqtrade/user_data/data/binance ...
👉 下载的数据会存储在 user_data/data/binance/ 下。

2025-09-12 14:01:18,079 - freqtrade.configuration.configuration - INFO - Using pairs ['ETH/USDT:USDT']
👉 你指定的交易对是 ETH/USDT:USDT，这里的写法说明是 U 本位合约 (swap)，不是现货。

2025-09-12 14:01:18,079 - freqtrade.configuration.configuration - INFO - timeframes --timeframes: ['15m']
👉 下载的 K 线周期为 15 分钟。

2025-09-12 14:01:18,079 - freqtrade.configuration.configuration - INFO - Detected --days: 15
👉 需要下载 15 天的数据。

- 检查交易所
2025-09-12 14:01:18,080 - freqtrade.exchange.check_exchange - INFO - Checking exchange...
2025-09-12 14:01:18,090 - freqtrade.exchange.check_exchange - INFO - Exchange "binance" is officially supported by the Freqtrade development team.
👉 确认 Binance 是官方支持的交易所。

配置验证
2025-09-12 14:01:18,091 - freqtrade.configuration.config_validation - INFO - Validating configuration ...
👉 验证配置文件是否合法。

2025-09-12 14:01:18,135 - freqtrade.exchange.exchange - INFO - Instance is running with dry_run enabled
👉 当前处于 dry_run 模式，不会真的下单。

2025-09-12 14:01:18,136 - freqtrade.exchange.exchange - INFO - Using CCXT 4.5.3
👉 使用的交易所接口库是 CCXT 4.5.3。

2025-09-12 14:01:18,136 - freqtrade.exchange.exchange - INFO - Applying additional ccxt config: {'options': {'defaultType': 'swap'}}
2025-09-12 14:01:18,145 - freqtrade.exchange.exchange - INFO - Applying additional ccxt config: {'options': {'defaultType': 'swap'}}
👉 这里明确指定了 defaultType=swap，所以 Freqtrade 会去访问 Binance 合约接口 (fapi)。

- 交易所连接
2025-09-12 14:01:18,155 - freqtrade.exchange.exchange - INFO - Using Exchange "Binance"
2025-09-12 14:01:18,155 - freqtrade.resolvers.exchange_resolver - INFO - Using resolved exchange 'Binance'...
👉 确认使用的是 Binance 交易所对象。

2025-09-12 14:01:18,156 - freqtrade.exchange.exchange - INFO - Markets were not loaded. Loading them now..
👉 市场数据（交易对列表）还没加载，现在开始加载。

- 请求错误和重试
2025-09-12 14:01:29,025 - freqtrade.exchange.common - WARNING - _load_async_markets() returned exception: "Error in reload_markets due to RequestTimeout. Message: binance GET https://fapi.binance.com/fapi/v1/exchangeInfo". Retrying still for 3 times.
👉 第一次加载市场信息时，访问 Binance 合约 API (fapi.binance.com/fapi/v1/exchangeInfo) 超时，准备重试 3 次。

2025-09-12 14:01:40,025 - freqtrade.exchange.common - WARNING - _load_async_markets() returned exception: "Error in reload_markets due to RequestTimeout. Message: binance GET https://api.binance.com/api/v3/exchangeInfo". Retrying still for 2 times.
👉 第二次重试时，换成了 Binance 现货 API (api.binance.com/api/v3/exchangeInfo)，也超时了，还剩 2 次机会。




"""


# 启动
全局模式: 日本、日本
freqtrade trade --config user_data/config.json --strategy SampleStrategy

# 关闭端口
ps aux | grep freqtrade 
kill -9 95391  93982

# 判断有哪些数字货币市场
freqtrade list-markets --config user_data/config.json > markets_list.txt 

# 其他重要的前置条件和准备工作

## 1. 检查交易所连接
freqtrade list-exchanges

## 2. 查看可用的交易对
freqtrade list-pairs --config user_data/config.json
freqtrade list-pairs --config user_data/config.json > pairs_list.txt 

## 3. 检查可用的时间框架
freqtrade list-timeframes --config user_data/config.json
freqtrade list-timeframes --config user_data/config.json > timeframes_list.txt 

## 4. 查看可用的策略
freqtrade list-strategies

## 5. 测试配置文件
freqtrade show-config --config user_data/config.json

## 6. 测试交易对列表配置
freqtrade test-pairlist --config user_data/config.json


## 7. 下载历史数据（回测前必需）
freqtrade download-data --config user_data/config.json --timeframe 5m --days 30

## 8. 查看已下载的数据
freqtrade list-data --config user_data/config.json
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃             Pair ┃   Timeframe ┃          Type ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│    BTC/USDT:USDT │         15m │       futures │
│    BTC/USDT:USDT │          8h │  funding_rate │
│    BTC/USDT:USDT │          8h │          mark │
│    ETH/USDT:USDT │         15m │       futures │
│    ETH/USDT:USDT │          8h │  funding_rate │
│    ETH/USDT:USDT │          8h │          mark │
└──────────────────┴─────────────┴───────────────┘

## 9. 验证策略（可选）
freqtrade backtesting --config user_data/config.json --strategy SampleStrategy --timerange 20240101-20240201

## 📊 市场数据字段说明

| 字段名称 | 中文含义 | 详细说明 | 示例 |
|---------|---------|---------|------|
| **Id** | 市场内部编号 | Binance 给每个交易对分配的唯一数字标识符 | `1234567` |
| **Symbol** | 交易对符号 | 标准化的交易对表示格式 | • 现货：`BTCUSDT`<br>• 合约：`BTC/USDT:USDT` |
| **Base** | 基础资产 | 交易对中的基础货币（前缀） | `BTC`、`ETH`、`ADA` |
| **Quote** | 计价资产 | 交易对中的计价货币（后缀） | `USDT`、`BTC`、`ETH` |
| **Active** | 交易状态 | 当前是否可以进行交易 | • `True` = 可交易<br>• `False` = 已暂停 |
| **Spot** | 现货标识 | 是否为现货交易市场 | • `True` = 现货市场<br>• `False` = 其他类型 |
| **Margin** | 杠杆支持 | 是否支持保证金交易 | • `True` = 支持杠杆<br>• `False` = 仅现货 |
| **Future** | 合约标识 | 是否为永续合约市场 | • `True` = USDT-M 永续<br>• `False` = 非合约 |
| **Leverage** | 最大杠杆 | 该交易对支持的最高杠杆倍数 | `75.0` = 最高75倍杠杆 |
| **Min Stake** | 最小订单 | 最小下单金额（以计价货币计算） | `10.0` = 最少10 USDT |

> **💡 提示**：下单时需确保 `价格 × 数量 ≥ Min Stake` 的要求


