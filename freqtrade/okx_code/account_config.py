import time
import base64
import hmac
import hashlib
import requests
from datetime import datetime, timezone

"""
1. 用于获取账户信息
"""

API_KEY = "358f2c93-b394-4551-a163-f802c37a5d4c"
SECRET_KEY = "FF6C67C33EEDB5691B781A85F4421D00"
PASSPHRASE ="Hu265104$"

BASE_URL = "https://www.okx.com"

def iso_timestamp():
    # OKX 要求 ISO8601 毫秒+Z
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')

def sign(timestamp: str, method: str, request_path: str, body: str = "") -> str:
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(mac).decode()

def get_account_config(simulated: bool = False):
    method = "GET"
    path = "/api/v5/account/config"
    ts = iso_timestamp()
    signature = sign(ts, method, path, "")

    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": ts,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
    }
    if simulated:
        headers["x-simulated-trading"] = "1"

    url = BASE_URL + path
    resp = requests.get(url, headers=headers, timeout=10)
    # 常见返回结构：{"code":"0","msg":"","data":[{...}]}
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
    j = resp.json()
    if j.get("code") != "0":
        raise RuntimeError(f"API error: {j}")
    return j["data"][0] if j.get("data") else j

if __name__ == "__main__":
    cfg = get_account_config(simulated=True)
    # 典型字段举例：acctLv, posMode, mgnMode, greeksType, autoBorrow
    print(cfg)


# posMode: "net_mode"：单向持仓模式（不是双向多空分离的 long_short_mode）。
# 
# 结算币默认 USDC；若策略或风控要用 USDT 结算，需要在账户/产品侧确认是否可切或在下单时指定相应合约/市场。

# greeksType: "PA"：期权希腊值显示为 PA（币本位）；另一种是 BS（美元本位）。
# 期权分析如果习惯美元计价的 Greeks，改 greeksType 为 BS 会更直观。
# 自动借币与自动还币均关闭，做杠杆或资金效率策略时要留意资金可用性和借贷成本。

