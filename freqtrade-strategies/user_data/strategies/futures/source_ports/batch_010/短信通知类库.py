"""Deep semantic map of FMZ JavaScript strategy 短信通知类库.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '短信通知类库.md'
SOURCE_FEATURES = ['var ']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = '$.SMSNotify = function(content) {\n    if (IsVirtual()) {\n        throw "此模板只支持实盘";\n    }\n    if (SMSGate === 0) {\n        var retCode = HttpQuery("http://api.smsbao.com/sms?u="+SMSBaoUserName+"&p="+MD5(SMSBaoPWD)+"&m="+PhoneNum+"&c="+encodeURIComponent(content));\n        var retDict = {\n            \'30\': \'密码错误\',\n            \'40\': \'账号不存在\',\n            \'41\': \'余额不足\',\n            \'42\': \'帐号过期\',\n            \'43\': \'IP地址限制\',\n            \'50\': \'内容含有敏感词\',\n            \'51\': \'手机号码不正确\'\n        };\n        if (typeof(retCode) === \'string\' && typeof(retDict[retCode]) === \'string\') {\n            Log(\'短信通知返回:\', retDict[retCode]);\n        } else if (retCode === \'0\') {\n            Log(\'短信通知成功:\', content);\n        } else {\n            Log(\'短信通知失败:\', content, \'#ff0000\');\n        }\n    } else if (SMSGate == 1) {\n        var vars = {};\n        vars[VarName] = content;\n        var ret = HttpQuery(\'https://api.submail.cn/message/xsend.json\', \'appid=\'+AppId+\'&to=\'+PhoneNum+\'&project=\'+Project+\'&signature=\'+AppKey+\'&vars=\'+encodeURIComponent(JSON.stringify(vars)));\n        if (ret && ret.indexOf(\'"status"\') != -1) {\n            var obj = JSON.parse(ret);\n            Log("短信通知:", obj.status, typeof(obj.msg) != \'undefined\' ? obj.msg : \'\');\n        } else {\n            Log("短信通知失败");\n        }\n    }\n}\n\nfunction main() {\n    $.SMSNotify("abc 短信测试");\n}'

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
