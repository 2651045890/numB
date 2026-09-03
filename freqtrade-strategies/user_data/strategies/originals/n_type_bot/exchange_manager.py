"""
交易所接口模块 - 封装ccxt操作OKX永续合约
"""
import time
import logging
import base64
import hashlib
import hmac
import json
import requests
import ccxt.pro as ccxtpro
import ccxt

logger = logging.getLogger(__name__)


class ExchangeManager:
    """交易所管理器，封装所有交易所API调用"""

    def __init__(self, config):
        self.config = config
        ex_conf = config['EXCHANGE']

        exchange_class = getattr(ccxt, ex_conf['name'])
        self.exchange = exchange_class({
            'apiKey': ex_conf['api_key'],
            'secret': ex_conf['api_secret'],
            'password': ex_conf['password'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',          # 永续合约
            },
        })

        self.markets = {}
        self._load_markets()
        self._time_offset = self._sync_time()

    def _load_markets(self):
        """手动预填充市场数据 + 绕过ccxt的fetch_currencies"""
        # 预填充交易品种
        prefilled = {
            'BTC/USDT:USDT': {
                'id': 'BTC-USDT-SWAP', 'symbol': 'BTC/USDT:USDT',
                'base': 'BTC', 'quote': 'USDT', 'settle': 'USDT',
                'type': 'swap', 'swap': True, 'contract': True, 'linear': True,
                'contractSize': 0.01,
                'precision': {'amount': 0.0001, 'price': 0.1},
                'limits': {'amount': {'min': 0.0001}, 'price': {'min': 0.1}},
            },
            'ETH/USDT:USDT': {
                'id': 'ETH-USDT-SWAP', 'symbol': 'ETH/USDT:USDT',
                'base': 'ETH', 'quote': 'USDT', 'settle': 'USDT',
                'type': 'swap', 'swap': True, 'contract': True, 'linear': True,
                'contractSize': 0.01,
                'precision': {'amount': 0.0001, 'price': 0.01},
                'limits': {'amount': {'min': 0.0001}, 'price': {'min': 0.01}},
            },
            'SOL/USDT:USDT': {
                'id': 'SOL-USDT-SWAP', 'symbol': 'SOL/USDT:USDT',
                'base': 'SOL', 'quote': 'USDT', 'settle': 'USDT',
                'type': 'swap', 'swap': True, 'contract': True, 'linear': True,
                'contractSize': 0.01,
                'precision': {'amount': 0.001, 'price': 0.001},
                'limits': {'amount': {'min': 0.001}, 'price': {'min': 0.001}},
            },
            'LINK/USDT:USDT': {
                'id': 'LINK-USDT-SWAP', 'symbol': 'LINK/USDT:USDT',
                'base': 'LINK', 'quote': 'USDT', 'settle': 'USDT',
                'type': 'swap', 'swap': True, 'contract': True, 'linear': True,
                'contractSize': 0.01,
                'precision': {'amount': 0.1, 'price': 0.0001},
                'limits': {'amount': {'min': 0.1}, 'price': {'min': 0.0001}},
            },
            'AVAX/USDT:USDT': {
                'id': 'AVAX-USDT-SWAP', 'symbol': 'AVAX/USDT:USDT',
                'base': 'AVAX', 'quote': 'USDT', 'settle': 'USDT',
                'type': 'swap', 'swap': True, 'contract': True, 'linear': True,
                'contractSize': 0.01,
                'precision': {'amount': 0.001, 'price': 0.001},
                'limits': {'amount': {'min': 0.001}, 'price': {'min': 0.001}},
            },
        }

        # 填充markets（含原始符号和带后缀符号两种格式）
        self.markets = {}
        self.markets_by_id = {}
        for sym, info in prefilled.items():
            self.markets[sym] = info
            self.markets_by_id[info['id']] = info
            orig = sym.split(':')[0]
            self.markets[orig] = info

        # 同步到ccxt交易所对象，避免内部load_markets再次调用
        self.exchange.markets = self.markets
        self.exchange.markets_by_id = self.markets_by_id
        self.exchange.currencies = {}
        self.exchange.markets_loading = False

        logger.info(f"预填充 {len(prefilled)} 个永续合约市场")
        return

    def fetch_ohlcv(self, symbol, timeframe='15m', limit=200):
        """获取K线数据（使用requests直接请求，避免ccxt DNS问题）"""
        # 解析instId
        instId = self._get_inst_id(symbol)
        if not instId:
            logger.error(f"[{symbol}] 无法解析instId")
            return None

        bar_map = {'1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                   '1H': '1H', '4H': '4H', '1D': '1D',
                   '1h': '1H', '4h': '4H', '1d': '1D'}
        bar = bar_map.get(timeframe, timeframe)

        # 限制最多300条
        limit = min(limit, 300)
        url = f'https://www.okx.com/api/v5/market/candles?instId={instId}&bar={bar}&limit={limit}'

        for attempt in range(self.config['SYSTEM']['max_retries']):
            try:
                resp = requests.get(url, timeout=15)
                data = resp.json()
                if data.get('code') == '0':
                    candles = data['data']
                    # 转换为ccxt标准格式 (timestamp, open, high, low, close, volume)
                    result = []
                    for c in candles:
                        result.append([
                            int(c[0]),
                            float(c[1]), float(c[2]), float(c[3]),
                            float(c[4]), float(c[5]),
                        ])
                    result.reverse()  # OKX返回从新到旧，转换为从旧到新
                    return result
                else:
                    logger.warning(f"[{symbol}] OKX API错误: {data}")
                    time.sleep(1)
            except Exception as e:
                logger.warning(f"[{symbol}] 获取K线失败(第{attempt+1}次): {e}")
                time.sleep(self.config['SYSTEM']['retry_delay'])
        return None

    def _get_inst_id(self, symbol):
        """将symbol转换为OKX的instId格式"""
        mapping = {
            'BTC/USDT': 'BTC-USDT-SWAP', 'BTC/USDT:USDT': 'BTC-USDT-SWAP',
            'ETH/USDT': 'ETH-USDT-SWAP', 'ETH/USDT:USDT': 'ETH-USDT-SWAP',
            'SOL/USDT': 'SOL-USDT-SWAP', 'SOL/USDT:USDT': 'SOL-USDT-SWAP',
            'LINK/USDT': 'LINK-USDT-SWAP', 'LINK/USDT:USDT': 'LINK-USDT-SWAP',
            'AVAX/USDT': 'AVAX-USDT-SWAP', 'AVAX/USDT:USDT': 'AVAX-USDT-SWAP',
        }
        return mapping.get(symbol)

    def _sync_time(self):
        """同步OKX服务器时间"""
        try:
            resp = requests.get('https://www.okx.com/api/v5/public/time', timeout=10)
            data = resp.json()
            if data.get('code') == '0':
                server_ts = int(data['data'][0]['ts'])
                local_ts = int(time.time() * 1000)
                offset = server_ts - local_ts
                logger.info(f"时间同步完成: offset={offset}ms")
                return offset
        except Exception as e:
            logger.warning(f"时间同步失败: {e}")
        return 0

    def _okx_sign(self, method, path, query='', body=''):
        """OKX API签名"""
        from datetime import datetime, timezone
        ex_conf = self.config['EXCHANGE']
        # OKX要求ISO 8601格式时间戳
        ts = datetime.fromtimestamp(
            time.time() + self._time_offset / 1000,
            tz=timezone.utc
        ).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        # GET请求: body=""，query拼在path里
        # POST请求: body=JSON字符串
        sign_path = path + ('?' + query if query else '')
        msg = ts + method.upper() + sign_path + body
        mac = hmac.new(
            ex_conf['api_secret'].encode('utf-8'),
            msg.encode('utf-8'),
            hashlib.sha256
        )
        sign = base64.b64encode(mac.digest()).decode('utf-8')
        return {
            'OK-ACCESS-KEY': ex_conf['api_key'],
            'OK-ACCESS-SIGN': sign,
            'OK-ACCESS-TIMESTAMP': ts,
            'OK-ACCESS-PASSPHRASE': ex_conf['password'],
        }

    def _okx_get(self, path, params=None):
        """带签名的GET请求"""
        qs = ''
        if params:
            qs = '&'.join(f'{k}={v}' for k, v in sorted(params.items()))
        url = f'https://www.okx.com{path}'
        if qs:
            url += '?' + qs
        headers = self._okx_sign('GET', path, qs, '')
        headers['Content-Type'] = 'application/json'
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            return resp.json()
        except Exception as e:
            logger.error(f"OKX GET {path} 失败: {e}")
            return None

    def fetch_balance(self):
        """获取账户余额"""
        data = self._okx_get('/api/v5/account/balance')
        if data and data.get('code') == '0':
            bal_data = data['data'][0]
            details = bal_data.get('details', [])
            balance = {}
            for d in details:
                currency = d.get('ccy', '')
                balance[currency] = {
                    'free': float(d.get('availBal', 0)),
                    'used': float(d.get('frozenBal', 0)),
                    'total': float(d.get('eq', 0)),
                }
            return balance
        logger.error(f"获取余额失败: {data}")
        return None

    def fetch_positions(self, symbols=None):
        """获取持仓信息"""
        try:
            data = self._okx_get('/api/v5/account/positions')
            if data and data.get('code') == '0':
                return data.get('data', [])
            return []
        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            return []

    def fetch_position(self, symbol):
        """获取单个品种持仓"""
        try:
            inst_id = self._get_inst_id(symbol) or symbol
            data = self._okx_get('/api/v5/account/positions', {'instId': inst_id})
            if data and data.get('code') == '0':
                positions = data.get('data', [])
                return positions[0] if positions else None
            return None
        except Exception as e:
            logger.error(f"[{symbol}] 获取持仓失败: {e}")
            return None

    def _okx_post(self, path, params):
        """带签名的POST请求"""
        body = json.dumps(params)
        headers = self._okx_sign('POST', path, '', body)
        headers['Content-Type'] = 'application/json'
        try:
            resp = requests.post(
                f'https://www.okx.com{path}',
                data=body, headers=headers, timeout=15
            )
            return resp.json()
        except Exception as e:
            logger.error(f"OKX POST {path} 失败: {e}")
            return None

    def create_market_order(self, symbol, side, amount, reduce_only=False):
        """
        创建市价单
        :param symbol:   交易对
        :param side:     'buy' 或 'sell'
        :param amount:   合约数量（张数）
        :param reduce_only: 是否仅减仓
        """
        inst_id = self._get_inst_id(symbol) or symbol
        params = {
            'instId': inst_id,
            'tdMode': 'cross',
            'side': side,
            'ordType': 'market',
            'sz': str(amount),
        }
        if reduce_only:
            params['reduceOnly'] = 'true'

        result = self._okx_post('/api/v5/trade/order', params)
        if result and result.get('code') == '0':
            order_id = result['data'][0]['ordId']
            logger.info(f"[{symbol}] 市价{side} {amount}张 - 订单ID: {order_id}")
            return result['data'][0]
        else:
            logger.error(f"[{symbol}] 市价单失败: {result}")
            return None

    def set_leverage(self, symbol, leverage):
        """设置杠杆倍数"""
        inst_id = self._get_inst_id(symbol) or symbol
        params = {
            'instId': inst_id,
            'lever': str(leverage),
            'mgnMode': 'cross',
        }
        result = self._okx_post('/api/v5/account/set-leverage', params)
        if result and result.get('code') == '0':
            logger.info(f"[{symbol}] 杠杆设为 {leverage}x")
            return True
        logger.warning(f"[{symbol}] 设置杠杆失败: {result}")
        return False

    def fetch_ticker(self, symbol):
        """获取最新行情"""
        inst_id = self._get_inst_id(symbol) or symbol
        try:
            resp = requests.get(
                f'https://www.okx.com/api/v5/market/ticker?instId={inst_id}',
                timeout=15
            )
            data = resp.json()
            if data.get('code') == '0':
                return data['data'][0]
            return None
        except Exception as e:
            logger.error(f"[{symbol}] 获取行情失败: {e}")
            return None

    def fetch_funding_rate(self, symbol):
        """获取资金费率"""
        try:
            return self.exchange.fetch_funding_rate(symbol)
        except Exception as e:
            return None

    def get_precision(self, symbol):
        """获取精度信息"""
        market = self.markets.get(symbol)
        if market:
            return {
                'amount': market['precision']['amount'],
                'price': market['precision']['price'],
            }
        return {'amount': 0.001, 'price': 0.01}

    def get_min_amount(self, symbol):
        """获取最小交易量"""
        market = self.markets.get(symbol)
        if market:
            return market['limits']['amount']['min']
        return 0.001

    def get_contract_size(self, symbol):
        """获取合约面值（如OKX是张/合约面值）"""
        market = self.markets.get(symbol)
        if market:
            return market.get('contractSize', 1) or 1
        return 1

    def get_tick_size(self, symbol):
        """获取最小价格变动"""
        market = self.markets.get(symbol)
        if market:
            return market['precision']['price']
        return 0.01

    def close(self):
        """关闭交易所连接"""
        try:
            self.exchange.close()
        except:
            pass