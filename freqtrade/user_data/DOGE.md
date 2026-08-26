- 针对DOGE的交易
2013年12月6日 上市

# 1. 下载不同时间段的数据。

# 2. 跑一个脚本，

# 3. 回测一下数据将终端的全部内容得到，然后问大模型哪一个策略比较好

# 狗狗币最早日期
freqtrade download-data --timeframe 15m --pairs DOGE/USDT --timerange 20200730-20250924 --exchange binance

freqtrade backtesting --strategy Bandtastic --timeframe 15m --timerange 20200730-20250924 --logfile backtest_20200730-20250924_15m_Bandtastic.log

freqtrade backtesting --strategy Bandtastic --timeframe 15m --timerange 20200730-20250924 > backtest_output.txt  --logfile Bandtastic.log

# 运行日志 15m
freqtrade download-data --timeframe 15m --pairs DOGE/USDT:USDT --timerange 20250601-20250912 

# 运行策略
freqtrade backtesting --strategy Bandtastic --timeframe 15m --timerange 20250601-20250912 --logfile backtest.log


# 运行策略
freqtrade backtesting --strategy Bandtastic --timeframe 15m --timerange 20220601-20250922

# 回测得到backtest.log
freqtrade backtesting --strategy Bandtastic --timeframe 15m --timerange 20250601-20250912 --logfile backtest.log

# 整理所有日志，给大模型



策略Strategy001.py -> 里面使用的 timeframe 5m
// 获取下数据
freqtrade download-data --pairs DOGE/USDT --timeframe 5m

- 确保代理是否可用
curl -x http://127.0.0.1:7890 https://api.binance.com/api/v3/ping

-  查看交易对，USDT现货的情况 spot是看货
freqtrade list-pairs --exchange binance --quote USDT --trading-mode spot

freqtrade download-data --timeframe 15m --pairs DOGE/USDT:USDT --timerange 20250601-20250912 

freqtrade download-data --timeframe 15m --pairs DOGE/USDT --timerange 20240601-20240924 --exchange binance

freqtrade download-data --timeframe 15m --pairs DOGE/USDT --timerange 20220601-20250922 --exchange binance

- 获取数据
freqtrade download-data --pairs DOGE/USDT --timeframe 15m --timerange 20250601-20250912

freqtrade download-data --timeframe 15m --timerange 20250601-20250912 --pairs DOGE/USDT

freqtrade backtesting --strategy Bandtastic --timeframe 15m --timerange 20220601-20250922
下载数据，要控制     "trading_mode": "spot", 这个参数

- 清除缓存
freqtrade backtesting --strategy Bandtastic --timeframe 15m --timerange 20250601-20250912 --cache none

- 日志输出
freqtrade backtesting --strategy Bandtastic --timeframe 15m --timerange 20250601-20250912 --logfile backtest.log

- 查看可用数据
freqtrade list-data

回测策略
freqtrade backtesting --strategy Bandtastic --timeframe 15m

- 模拟账户:
freqtrade trade --strategy Bandtastic --dry-run

- 真实账户
freqtrade trade --strategy Bandtastic

//写一个策略
freqtrade backtesting --strategy Strategy001
在backtest_results出现了:

--export none: 不导出任何数据。

--export trades: 仅导出交易记录（包括每笔交易的买入、卖出信息等）。

--export signals: 导出信号数据（例如，买入和卖出信号的触发点等）。


回测分析：
freqtrade backtesting-analysis

再次显示，和 回测策略出现的是一样的
freqtrade backtesting-show

查看回测结果：
启动模拟交易
freqtrade trade --strategy Strategy001 --dry-run

// 解压，将数据转换一下
python json_to_csv_converter.py "user_data/backtest_results/backtest-result-2025-09-18_10-34-46/backtest-result-2025-09-18_10-34-46.json" 


//今天需要搞下币安的账号。

