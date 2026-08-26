import time, hmac, base64, json, requests
from datetime import datetime, timezone

API_KEY = "358f2c93-b394-4551-a163-f802c37a5d4c"
API_SECRET = "FF6C67C33EEDB5691B781A85F4421D00"
PASSPHRASE ="Hu265104$"
BASE_URL = "https://www.okx.com"


def iso_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

def sign(ts, method, request_path, body=""):
    prehash = f"{ts}{method}{request_path}{body}"
    return base64.b64encode(hmac.new(API_SECRET.encode(), prehash.encode(), digestmod="sha256").digest()).decode()

def set_position_mode(pos_mode="long_short_mode"):
    path   = "/api/v5/account/set-position-mode"
    body   = json.dumps({"posMode": pos_mode}, separators=(",", ":"))
    ts     = iso_timestamp()
    sig    = sign(ts, "POST", path, body)
    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": sig,
        "OK-ACCESS-TIMESTAMP": ts,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
    }
    r = requests.post(BASE_URL + path, headers=headers, data=body, timeout=10)
    print(r.status_code, r.text)

def get_account_config():
    path = "/api/v5/account/config"
    ts   = iso_timestamp()
    sig  = sign(ts, "GET", path, "")
    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": sig,
        "OK-ACCESS-TIMESTAMP": ts,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
    }
    r = requests.get(BASE_URL + path, headers=headers, timeout=10)
    print(r.status_code, r.text)

# 先切换为双向模式，再查询确认
# set_position_mode("long_short_mode")
get_account_config()

"""
net_mode（买卖/单向）：同一合约只能单边持仓，数量正负代表多/空。

long_short_mode（开平仓/双向）：同一合约可同时持有多仓与空仓。 

'posMode': 'net_mode

现货永远是单向
现货叫做平仓，没有空仓，只是一种货币换成另一种货币

合约：看涨、看跌、三倍杠杆。

强行平仓，就是爆仓了。 亏到本金。


"""
