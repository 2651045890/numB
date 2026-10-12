"""Source-preserving Python port envelope for 设定比特币价格并微信推送-100取整突破推送.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '/*backtest\nstart: 2020-10-13 00:00:00\nend: 2020-10-14 01:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"OKEX","currency":"BTC_USDT"}]\n*/\nvar a=[1,2,3,4,5,6,7,8,9,10]\nvar ticker= _C(exchange.GetTicker)\n\nfunction lock(){                                //锁定现价在哪个整数区间\n    P=parseInt(ticker.Last/100)*100\n    HP=P+100\n    lock_tickLast=ticker.Last\n//    Log(P,HP,ticker.Last)\n} \n\nfunction stack(){\n    for(var k=0;k<a.length;k++)\n        a[k]=a[k+1]\n}    \n\nfunction onTick(){\n    ticker = _C(exchange.GetTicker) \n    var get=parseInt(ticker.Last/100)*100\n    if(get>P){\n        a[9]=get \n        if(a[8]!=a[9]){\n            str=a.toString()\n            if(a[9]-a[8]>100)\n                Log("向上跳空突破成功",get,ticker.Last,"{",str,"}",\'@\')\n            else                        \n                Log("向上突破成功",get,ticker.Last,"{",str,"}",\'@\' )\n            lock()\n            stack()\n        }\n    } \n    else if(get<P){\n        a[9]=get+100\n        if(a[9]!=a[8]){\n            str=a.toString()\n            if(a[8]-a[9]>100)\n                Log("向下跳空突破成功",a[9],ticker.Last,"{",str,"}",\'@\')\n            else\n                Log("向下突破成功",a[9],ticker.Last,"{",str,"}",\'@\' )\n            lock()\n            stack()\n        }\n    }\n}\n\nfunction main(){\n\n    lock()\n    a[8]=P\n//    var ticker=0\n    Log("程序运行开始推送",ticker.Last,\'@\')\n    \n    while(true){ \n\n            onTick()  \n\n        Sleep(Interval*1000)                      \n            \n    }    \n}\n\n'
SOURCE_FILE = '设定比特币价格并微信推送-100取整突破推送.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
