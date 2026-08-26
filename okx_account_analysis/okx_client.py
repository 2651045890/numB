"""
OKX API 客户端封装
提供签名、请求等基础功能
"""
import time
import base64
import hmac
import hashlib
import requests
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from config import API_KEY, SECRET_KEY, PASSPHRASE, BASE_URL, USE_PROXY, PROXY_CONFIG


class OKXClient:
    """OKX API 客户端"""
    
    def __init__(self, simulated: bool = False):
        self.simulated = simulated
        self.base_url = BASE_URL
        self.proxies = PROXY_CONFIG if USE_PROXY else None
    
    def iso_timestamp(self) -> str:
        """生成ISO8601格式的时间戳（毫秒精度）"""
        return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    
    def sign(self, timestamp: str, method: str, request_path: str, body: str = "") -> str:
        """生成API签名"""
        message = f"{timestamp}{method}{request_path}{body}"
        mac = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
        return base64.b64encode(mac).decode()
    
    def _get_headers(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """生成请求头"""
        timestamp = self.iso_timestamp()
        signature = self.sign(timestamp, method, path, body)
        
        headers = {
            "OK-ACCESS-KEY": API_KEY,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": PASSPHRASE,
            "Content-Type": "application/json",
        }
        
        if self.simulated:
            headers["x-simulated-trading"] = "1"
        
        return headers
    
    def request(self, method: str, path: str, params: Optional[Dict] = None, body: Optional[Dict] = None) -> Dict[str, Any]:
        """发送API请求"""
        import json
        
        # 处理查询参数
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            path = f"{path}?{query_string}"
        
        # 处理请求体
        body_str = ""
        if body:
            body_str = json.dumps(body, separators=(',', ':'))
        
        headers = self._get_headers(method, path, body_str)
        url = self.base_url + path
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, proxies=self.proxies, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, data=body_str, proxies=self.proxies, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") != "0":
                raise RuntimeError(f"API错误: {result.get('msg', '未知错误')} - {result}")
            
            return result.get("data", [])
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"请求失败: {str(e)}")
    
    def get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET请求"""
        return self.request("GET", path, params=params)
    
    def post(self, path: str, body: Optional[Dict] = None) -> Dict[str, Any]:
        """POST请求"""
        return self.request("POST", path, body=body)
