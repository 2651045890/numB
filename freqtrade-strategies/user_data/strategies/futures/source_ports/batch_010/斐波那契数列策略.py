"""Deep semantic map of FMZ JavaScript strategy 斐波那契数列策略.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '斐波那契数列策略.md'
SOURCE_FEATURES = ['var ', 'while ', 'exchange.', 'Sleep(']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = '/*\n本策略仅供学习使用，用于实盘后果自负 \n*/\n/*backtest\nstart: 2017-06-26 00:00:00\nend: 2022-02-16 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\nvar n = 1 //初始下单数\nvar MarginLevel = 50 //合约杠杆 \nvar profit = 1//期望收益 ，不能小于手续费 \nvar bet=1.1\n\n\n//取随机数 \nfunction sum(m, n) {\u3000\u3000\n    var num = Math.floor(Math.random() * (m - n) + n);\u3000\u3000\n    return num;\n}\n\nfunction main() {\n    exchange.SetContractType("swap")\n    exchange.SetMarginLevel(MarginLevel)\n    var position = []\n    while (true) {\n        position = exchange.GetPosition()\n        if (position.length == 0) {\n            //取随机数0、1作为方向\n            var redom = sum(2, 0)\n            Log(redom)\n            if (redom == 0) {\n                n=0.001\n                exchange.SetDirection("sell")\n                exchange.Sell(-1, n, "开空")\n            }\n            if (redom == 1) {\n                n=0.001\n                exchange.SetDirection("buy")\n                exchange.Buy(-1, n, "开多")\n            }\n\n        }\n        if (position.length > 0) {\n\n            if (position[0].Type == 0) {\n                //盈利大于期望 \n                if (position[0].Profit > profit) {\n                    exchange.SetDirection("closebuy")\n                    exchange.Sell(-1, position[0].Amount)\n                }\n                //负盈利大于保证金 则加仓\n\n                if (position[0].Profit < position[0].Margin * -1) {\n              function  fibonacci( n){\n\n        if (n == 1 || n == 2) {             //特殊情况，分开讨论\n            return 1;\n        }\n        if (n > 2) {\n            return fibonacci(n - 1) + fibonacci(n - 2);     //递归调用\n        }\n        return -1;              //如果输入错误的n，一律返回-1\n    }\n                    \n                    exchange.SetDirection("buy")\n                    exchange.Buy(-1, n)\n                }\n            }\n            if (position[0].Type == 1) {\n                if (position[0].Profit > profit) {\n                    exchange.SetDirection("closesell")\n                    exchange.Buy(-1, position[0].Amount)\n                }\n                if (position[0].Profit < position[0].Margin * -1) {\n                    \n                    function    fibonacci( n){\n\n        if (n == 1 || n == 2) {             //特殊情况，分开讨论\n            return 1;\n        }\n        if (n > 2) {\n            return fibonacci(n - 1) + fibonacci(n - 2);     //递归调用\n        }\n        return -1;              //如果输入错误的n，一律返回-1\n    }\n                    \n                    exchange.SetDirection("sell")\n                    exchange.Sell(-1, n)\n                    \n                }\n            }\n            Sleep(60000)\n        }\n    }\n\n}'

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
