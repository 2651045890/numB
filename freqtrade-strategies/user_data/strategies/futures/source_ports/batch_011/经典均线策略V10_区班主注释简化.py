"""Source-preserving Python port envelope for 经典均线策略V10_区班主注释简化.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '/*backtest\nstart: 2019-01-01 00:00:00\nend: 2019-10-10 00:00:00\nperiod: 1d\nexchanges: [{"eid":"OKEX","currency":"ETH_USDT","stocks":0}]\nargs: [["OpMode",1,10989],["MaxAmount",1,10989],["TradeFee",0.001,10989]]\n*/\n//注册币乎后https://m.bihu.com/signup?i=1ewtKO&s=4&c=4\n//搜索 物联网区块链 可以联系到作者区班主\nfunction main() {\n    var STATE_IDLE  = -1;\n    var state = STATE_IDLE; //表示状态\n    var entryPrice = 0;\n    var initAccount = _C(exchange.GetAccount);\n    Log(initAccount);\n    while (true) {\n        if (state === STATE_IDLE) {  //初始化状态为默认仓；默认为空仓，只买入\n            var n = $.Cross(FastPeriod, SlowPeriod);//模板函数返回EMA指标快线、慢线交叉结果\n            if (Math.abs(n) >= EnterPeriod) { //EnterPeriod入市观察区，等待上拉一定时，再入场\n                var account = _C(exchange.GetAccount);\n                var ticker = _C(exchange.GetTicker);\n                var obj;\n                //账户现金乘以比例，除以当前价格，保留小数前3位\n                if(n > 0){\n                   obj = $.Buy(_N(account.Balance * PositionRatio / ticker.Sell, 3));\n                   if (obj) { //如果购买成功，就标志开仓\n                      opAmount = obj.amount;\n                      entryPrice = obj.price;\n                      state = PD_LONG;\n                      account = _C(exchange.GetAccount);\n                      Log("开仓:购买量", opAmount);\n                      Log("目前持币数", account.Stocks, "交叉周期", n);\n                   }\n                }\n            }\n        } else { //state为非空闲状态；处理平仓检测\n            var n = $.Cross(ExitFastPeriod, ExitSlowPeriod);\n            //这个判断条件有点长，先看Math.abs(n) >= ExitPeriod，n的绝对值大于等于 离市观察期 这是触发条件1，并且\n            //(n > 0)两者中至少有个为真\n            //需要离市平仓\n            var needCover = Math.abs(n) >= ExitPeriod && (n<0);\n            if (needCover) { //离市平仓\n                var nowAccount = _C(exchange.GetAccount);\n                var obj = $.Sell(_N(nowAccount.Stocks, 3));\n                if(obj){\n                    state=STATE_IDLE;\n                    Log("平仓：卖出量",nowAccount.Stocks);\n                    nowAccount = _C(exchange.GetAccount);\n                    Log("目前资金",nowAccount.Balance, "交叉周期", n,"盈利",nowAccount.Balance - initAccount.Balance);\n                }\n                //打印收益\n                //LogProfit(nowAccount.Balance - initAccount.Balance, \'钱:\', nowAccount.Balance, \'币:\', nowAccount.Stocks, \'平仓详情:\', obj, "交叉周期", n);\n            }\n        }\n        Sleep(Interval*1000);\n    }\n}'
SOURCE_FILE = '经典均线策略V10_区班主注释简化.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
