"""Deep semantic map of FMZ JavaScript strategy 智能间隔倍投策略出售版.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '智能间隔倍投策略出售版.md'
SOURCE_FEATURES = []
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = '/*backtest\nstart: 2023-04-01 00:00:00\nend: 2023-05-01 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT","balance":10000}]\nargs: [["TransactionVal",300,411371]]\n*/\n\n\n/*\n0.具体请看该教程https://www.fmz.com/bbs-topic/4145\n1.添加交易所\n2.部署托管者\n3.创建与修改参数\n4.创建和管理实盘\n\n5.技术支持 VX:18826683356   okex实盘交易免费\n\n5.1 币安实盘交易权限费用如下\n6.TRC(20)主网 收USDT地址: TFZn8YGYRVuE5CPLsSieaKgPbwJrG3E8e7\n7 通过币安支付 手机号18826683356 （免手续费）建议使用该方式支付\n8.币安需要支付 100USDT/3月\n  币安需要支付 500USDT/永久\n\n9.不对策略利润作任何保证，可以参考回测参数设置运行\n10.非开通权限，时间宝贵，请勿联系\n*/\n\n/*\n参数解析\n\n设置杠杆：设置该合约使用资金的倍数，杠杆越大开仓需要的保证金越小\n止损值：亏损额达账号总资金的一定百分比，清仓强平\n初始开单价值USDT：首单开仓的价值，如果设置为300，当前交易产品为BTC_USDT,报价为30000，那么开仓量为300/30000=0.01个\n加倍数值：如果已经有持仓订单，会加仓拉平持仓成本，设置为1，那么加仓量与持仓量一致。该参数需要设置为正整数\nATR周期波幅天数：指标ATR的参数\n长期均线：指标MA的参数\n短期均线：指标MA的参数\n均线反转平仓：打勾，长期均线>短期均线 会全平所有多单；长期均线<短期均线 会全平所有空单\n最大开单次数：符合条件可以加仓补单的次数，结束一轮循环会重新计数\nATR系数:用来修改ATR值，调整波动间隔\n*/\n//2023.05.15 用户反馈获利无法覆盖手续费，检查发现每个用户的手续费有差异化。为解决该问题，引用手续费率参数\n//双向持仓\n\nfunction main() {\n    Log("策略保密,复制可以直接加载币安期货交易所回测与OKEX期货交易所免费实盘"); \n    Log("策略保密,复制可以直接加载币安期货交易所实盘，需要支付费用开通权限");   \n    $.main1()\n}'

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
