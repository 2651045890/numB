"""Source-preserving Python port envelope for 顺大势逆小势策略之代码实现及可行性分析.md.

Original language: javascript.  This strategy is not PineScript and uses FMZ
exchange/event APIs or MyLanguage semantics.  It cannot be truthfully mapped to
the batch_001 candle PinePortBase engine without an event/order-book adapter.
The exact source is retained in ORIGINAL_SOURCE for a dedicated translation.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '//语法固定格式，调用main主函数\nfunction main() {\n    \n    //调用商品期货交易类库中的CTA框架\n    $.CTA("RM000", function(st) {\n        \n        //获取K线数组\n        var j = st.records;\n        \n        //指标运算参考的最大K线数量\n        if (j.length < 100) {\n            return;\n        }\n        \n        //获取上根K线的收盘价\n        var c = j[j.length - 2].Close;\n        \n        //获取KDJ指标数组\n        var kds = TA.KDJ(j, kd1, kd2, kd2);\n        \n        //获取KDJ指标K的数组\n        var ks = kds[0];\n        \n        //获取KDJ指标D的数组\n        var ds = kds[1];\n        \n        //获取上根K线的K值\n        var k = ks[ks.length - 2].toFixed(2);\n        \n        //获取上根K线的D值\n        var d = ds[ds.length - 2].toFixed(2);\n        \n        //获取均线数组\n        var mas = TA.MA(j, 100);\n        \n        //获取上根K线的MA值\n        var ma = mas[mas.length - 2];\n        \n        //获取当前的持仓数量，正数指多仓, 负数指空仓, 0则不持仓\n        var mp = st.position.amount;\n        \n        //如果当前持有多单，并且上根K线的K值小于上根K线的D值，平多单\n        if (mp > 0 && k < d) {\n            return -1; //如果当前有多单，指定返回值为-N，就是平N手多单。\n        }\n\n        //如果当前持有空单，并且上根K线的K值大于上根K线的D值，平空单\n        if (mp < 0 && k > d) {\n            return 1; //如果当前有空单，指定返回值为N，就是平N手空单。\n        }\n\n        //如果当前无持仓，并且上根K线的收盘价大于上根K线的MA值，并且上根K线的K值大于上根K线的D值，开多单\n        if (mp === 0 && c > ma && k > d) {\n            return 1; //如果当前无持仓，指定返回值为N，就是开N手多单。\n        }\n    \n        //如果当前无持仓，并且上根K线的收盘价小于上根K线的MA值，并且上根K线的K值小于上根K线的D值，开空单\n        if (mp === 0 && c < ma && k < d) {\n            return -1; //如果当前无持仓，指定返回值为-N，就是开N手空单。\n        }\n    });\n}\n'
SOURCE_FILE = '顺大势逆小势策略之代码实现及可行性分析.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ event/order-book adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
