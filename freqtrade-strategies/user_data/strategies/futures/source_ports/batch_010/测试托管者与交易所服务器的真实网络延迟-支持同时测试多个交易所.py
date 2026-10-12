"""Deep preservation port of original Python strategy 测试托管者与交易所服务器的真实网络延迟-支持同时测试多个交易所.md."""
ORIGINAL_SOURCE = '# Contact : ck@xueqiubot.com / WeChat@stay37\n\nimport time\nimport numpy as np\n\n\ndef test():\n    #延迟数据接收器\n    delay_list = []\n    for i in range(len(exchanges)):\n        delay_list.append([])\n    while True:\n        #延迟数据获取\n        for i in range(len(exchanges)):\n            send_t = time.time()\n            ticker = exchanges[i].GetTicker()\n            delay_list[i].append(round((time.time() - send_t) * 1000 , 2))\n        #数据输出 \n        delay_table = {"type":\'table\',"title":\'延迟数据\',"cols": [\'账号序号\',\'最近一次延迟\',\'平均延迟\',\'已测试次数\'],"rows":[]}\n        for i in range(len(delay_list)):\n            delay_table[\'rows\'].append([i + 1, str(delay_list[i][-1])+\' ms\', str(round(np.mean(delay_list[i]) , 2)) + \' ms\', len(delay_list[i])])\n        LogStatus("输出的延迟为：发送一次get_ticker请求到获取到数据的真实时间" + "\\n" + "`" + json.dumps(delay_table) + "`")\n        time.sleep(0.05)\n\n                \ndef main():\n    for i in range(len(exchanges)):\n        exchanges[i].SetContractType(\'swap\')\n    test()'
SOURCE_FILE = '测试托管者与交易所服务器的真实网络延迟-支持同时测试多个交易所.md'
SOURCE_FEATURES = ['for ', 'while ', 'exchanges[', 'GetTicker']
SOURCE_FIDELITY_NOTES = ['Original source is Python; retained as the canonical implementation with only packaging/syntax-safety changes when needed.']

def get_original_source():
    return ORIGINAL_SOURCE
