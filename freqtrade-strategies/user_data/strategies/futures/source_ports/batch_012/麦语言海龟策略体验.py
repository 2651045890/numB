"""Source-preserving Python port envelope for 麦语言海龟策略体验.md.

Original language: pascal.  This strategy is not PineScript and uses FMZ
exchange/event APIs or MyLanguage semantics.  It cannot be truthfully mapped to
the batch_001 candle PinePortBase engine without an event/order-book adapter.
The exact source is retained in ORIGINAL_SOURCE for a dedicated translation.
"""
ORIGINAL_LANGUAGE = 'pascal'
ORIGINAL_SOURCE = '(*backtest\nstart: 2020-10-26 00:00:00\nend: 2021-10-25 23:59:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"BTC_USDT"}]\n*)\n\n//该示范主要用海龟交易法则，演示“头寸计算，最大仓位控制等资金管理”的编写方法\n//编写示范中，只对示范重点内容语句进行了注释，其他语句请自行翻译，或者咨询客服\n//该模型仅仅用来示范演示使用，依此入市，风险自负。\nATRPERIOD:=20; // ATR波动周期\nSHORTPERIOD:=20; // 入市短周期\nLONGPERIOD:= 55; // 入市长周期\nVARIABLE:ISLASTFAILURE:=1; // 上次是否止损离场, 全局变量过滤信号\nTR:=MAX(MAX((HIGH-LOW),ABS(REF(CLOSE,1)-HIGH)),ABS(REF(CLOSE,1)-LOW));//真实波幅\nATR:MA(TR,ATRPERIOD); //求20个周期内真实波幅的简单移动平均, 在附图显示\nZOOM:=IFELSE(ISCONTRACT(\'@Futures_(?!CTP).*\'), CLOSE, 1); // 兼容数字货币期货币为保证金\nLOT:=((MONEYTOT*RATIO*ZOOM)/(UNIT*ATR))*ZOOM;//根据权益的1%计算下单手数\nTC..IFELSE(ISCONTRACT(\'@Futures.*\'), INTPART(LOT), LOT); // 兼容期货与现货ISCONTRACT以@开头表示匹配交易所名子, 支持正则\nMTC..4*TC; //总的持仓头寸\nHH^^HV(H,SHORTPERIOD); // 附加到主图显示\nLL^^LV(L,SHORTPERIOD);\nHHH^^HV(H,LONGPERIOD);\nLLL^^LV(L,LONGPERIOD);\nISEMPTY:=ISLASTBK=0&&ISLASTSK=0;\nCROSSUP(C,HH)&&ISEMPTY&&ISLASTFAILURE,BK(TC);//最新价超过短周期的最高值，首次买入开仓，手数为TC手\nCROSSDOWN(C,LL)&&ISEMPTY&&ISLASTFAILURE,SK(TC); //最新价跌破短周期的最低值，首次卖出开仓，手数为TC手\nCROSSUP(C,HHH)&&ISEMPTY,BK(TC);//最新价超过长周期的最高值，首次买入开仓，手数为TC手\nCROSSDOWN(C,LLL)&&ISEMPTY,SK(TC); //最新价跌破长周期的最低值，首次卖出开仓，手数为TC手\nC>=BKPRICE+0.5*ATR&&BKVOL<MTC&&ISLASTBK,BK(TC);//价格在上次开仓的基础上上涨0.5倍ATR，在手数不超过4倍TC的时候，买入加仓TC手\nC<=SKPRICE-0.5*ATR&&SKVOL<MTC&&ISLASTSK,SK(TC);//价格在上次开仓的基础上下跌0.5倍ATR，在手数不超过4倍TC的时候，卖出加仓TC手\nNEEDSTOP:=(C<=(BKPRICE-2*ATR)&&BKVOL>0) OR (C>=(SKPRICE+2*ATR)&&SKVOL>0);\nNEEDLEAVE:=(CROSSUP(H,HV(H,10))&&SKVOL>0) OR (CROSSDOWN(L,LV(L,10))&&BKVOL>0);\nNEEDSTOP OR NEEDLEAVE,CLOSEOUT;\nISLASTFAILURE..IF(NEEDSTOP OR NEEDLEAVE, NEEDSTOP, ISLASTFAILURE);\nINFO(NEEDSTOP, \'止损离场\');\nINFO(NEEDLEAVE, \'成功离场\');\nTRADE_AGAIN(10);\nMULTSIG(1, 1, 10);\n'
SOURCE_FILE = '麦语言海龟策略体验.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ event/order-book adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
