"""Source-preserving Python port envelope for 统计K线回测是否存在趋势.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = 'function adjustFloat(v) {\n\n    return Math.floor(v*1000)/1000;\n}\nfunction main(){\n    var arr=[0,0,0,0,0,0];//总共考察六根K线，用前五个的结果去预测第六个，可以自由选择\n    var appear=0;         //模式的出现次数\n    var fit=0;            //第六根K线的结果符合预期\n    var diff=0;           //预定模式出现后，第六根的收盘价和开盘价之差。\n    while(true){\n    var records=exchange.GetRecords();\n    i=records.length-1;\n    if(i>1&&(records[i].Close-records[i].Open>0)){\n        arr.push(1);\n        arr.shift();      //把最近一个K线的插入数组末尾，删去元素一以保持长度不变。上涨插入1，否则插入0\n    }\n    if(i>1&&!(records[i].Close-records[i].Open>0)){\n        arr.push(0);\n        arr.shift();\n    }\n    if(i>5){\n        var count=0;\n        for(k=0;k<5;k++){\n            if(arr[k]<1){\n                count++;   //前5根K线上涨的个数\n            }\n        }\n        if(count<2){       //设定需要多少个上涨K线，在这里要求四个或五个。\n            appear++;      //所需模式出现一次\n            diff+=(records[i].Close-records[i].Open);//统计第六根，也是最近一根的差价和\n            if(arr[5]<1){  //这里所期望的结果是上涨，也可以写成其它的\n                fit++;     //期待结果出现一次\n                Log("出现模式次数",appear,"符合预计次数",fit,"所占比例",adjustFloat(fit/appear),"差价之和",adjustFloat(diff));\n                LogProfit(adjustFloat(fit/appear));   //把比例输出为收益曲线\n            }\n        }\n    }\n    Sleep(300000);       //间隔时间，应与所选K线周期相同？这里是5分钟\n    }\n}'
SOURCE_FILE = '统计K线回测是否存在趋势.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
