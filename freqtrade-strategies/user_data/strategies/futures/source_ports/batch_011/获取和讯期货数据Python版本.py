"""Source-preserving Python port envelope for 获取和讯期货数据Python版本.md.

Original language: python. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'python'
ORIGINAL_SOURCE = '#coding: utf-8\nimport urllib2 as url\nimport json\nimport time\n\ndef hxRecords(instrument,timeFrame=1,size=1,includeLastBar=True,to_df=True):\n    ##从和讯获取期货实时数据\n    pInst=instrument.lower()\n    if pInst[-4]!=\'1\':\n        pInst=pInst[:-3]+\'1\'+pInst[-3:]\n    xchg=None\n    for i in instList:\n        if pInst[:-4] in i[\'inst\']:\n            xchg=i[\'xchg\']\n    if xchg is None:\n        print ("获取K线时发生错误: 找不到合约")\n        return None\n    tfs=[1,5,15,30,60,\'D\',\'W\']\n    tf=None\n    for i in range(len(tfs)):\n        if timeFrame==tfs[i]:\n            tf=i\n    if tf is None:\n        print("获取K线时发生错误: K线周期不正确")\n        return None\n    now=time.localtime()\n    timestr=str(now.tm_year+1)+str(12)+str(31)+\'000000\'\n    resp=\'http://webftcn.hermes.hexun.com/shf/kline?code=\' + xchg + pInst + \'&start=\' + timestr + \'&number=-\' + str(size) + \'&type=\' + str(tf)\n    try:\n        resp=url.urlopen(resp)\n        resp=resp.read()[1:-2]\n        resp=json.loads(resp)[\'Data\']\n    except:\n        print \'获取K线时发生错误: 不完整的JSON数据\'\n        return None\n    re=[]\n    pw=float(resp[4])\n    for i in resp[0]:\n        res=dict(Time=time.mktime(time.strptime(str(i[0]),\'%Y%m%d%H%M%S\'))*1000,Open=i[2]/pw,High=i[4]/pw\n                ,Low=i[5]/pw,Close=i[3]/pw,Volume=i[6])\n        re.append(res)\n    if to_df:\n        re=pd.DataFrame(re)\n        col=[]\n        for i in re.columns:\n            if i is \'Time\':\n                i=\'Date\'\n            col.append(i.lower())\n        re.columns=col\n        re[\'date\']=re[\'date\'].map(ts_dt64)\n    return re\n        \n\ninstList = [{\n    "xchg": "SHFE",\n    "inst": ["fu", "ru", "wr"]\n}, {\n    "xchg": "SHFE2",\n    "inst": ["ag", "au"]\n}, {\n    "xchg": "SHFE3",\n    "inst": ["al", "bu", "cu", "hc", "ni", "pb", "rb", "sn", "zn"]\n}, {\n    "xchg": "CZCE",\n    "inst": ["cf", "fg", "lr", "ma", "oi", "pm", "ri", "rm", "rs", "sf", "sm", "sr", "ta", "wh", "zc"]\n}, {\n    "xchg": "DCE",\n    "inst": ["a", "b", "bb", "c", "cs", "fb", "i", "j", "jd", "jm", "l", "m", "p", "pp", "v", "y"]\n}]\n\ndef main():\n    Log(exchange.GetAccount())\n'
SOURCE_FILE = '获取和讯期货数据Python版本.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
