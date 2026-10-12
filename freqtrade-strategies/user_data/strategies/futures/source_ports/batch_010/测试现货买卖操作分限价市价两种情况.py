"""Deep semantic map of FMZ JavaScript strategy 测试现货买卖操作分限价市价两种情况.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '测试现货买卖操作分限价市价两种情况.md'
SOURCE_FEATURES = ['var ', 'exchange.', 'Sleep(', 'GetTicker', 'GetAccount']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.', 'Uses ticker/depth data; OHLCV-only backtests cannot reproduce microstructure fills exactly.']
ORIGINAL_JAVASCRIPT = '/*backtest\nstart: 2020-01-01 00:00:00\nend: 2020-04-01 00:00:00\nperiod: 1d\nexchanges: [{"eid":"Huobi","currency":"BTC_USD","balance":1000000,"stocks":0}]\n*/\n\nvar id, order, buyAmount, lastPrice;\n\nfunction main() {\n    Log(exchange.GetAccount());\n\n    lastPrice = parseInt(exchange.GetTicker().Last);\n    id = exchange.Buy(lastPrice + 50, 5); // 限价买入5个BTC，买入价是当前最新价格+50          \n    Log(order = exchange.GetOrder(id));\n    buyAmount = parseFloat(order.DealAmount);\n    Log(exchange.GetAccount());\n\n    Sleep(1000);\n    last_price = parseInt(exchange.GetTicker().Last);\n    id = exchange.Sell(lastPrice - 50, buyAmount); // 限价卖出5个BTC，卖出价是当前最新价格-50    \n    Log(order = exchange.GetOrder(id));\n    Log(exchange.GetAccount());\n\n    Sleep(1000);\n    id = exchange.Buy(-1, 5); // 市价买入BTC，成交量是5个usdt    \n    Sleep(1000);    \n    Log(order = exchange.GetOrder(id));\n    buyAmount = parseFloat(order.DealAmount);    \n    Log(exchange.GetAccount());\n\n    Sleep(1000);    \n    id = exchange.Sell(-1, buyAmount); // 市价卖出BTC，成交量是刚才买入的BTC   \n    Sleep(1000);    \n    Log(order = exchange.GetOrder(id));\n    Log(exchange.GetAccount());\n\n}'

class FMZDeepPort:
    source_file = SOURCE_FILE
    source_features = SOURCE_FEATURES
    fidelity_notes = SOURCE_FIDELITY_NOTES
    javascript = ORIGINAL_JAVASCRIPT
    def run(self, adapter):
        runner = getattr(adapter, 'run_fmz_javascript', None)
        if runner is None:
            raise RuntimeError('This strategy needs an FMZ-compatible event/API adapter; refusing to invent OHLCV-only behavior.')
        return runner(self.javascript)
