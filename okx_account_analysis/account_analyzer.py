"""
OKX 账户分析工具
获取并分析账户的各种信息
"""
import json
from typing import Dict, Any, List
from okx_client import OKXClient
from config import USE_SIMULATED


class AccountAnalyzer:
    """账户分析器"""
    
    def __init__(self, simulated: bool = None):
        self.simulated = simulated if simulated is not None else USE_SIMULATED
        self.client = OKXClient(simulated=self.simulated)
    
    def get_account_config(self) -> Dict[str, Any]:
        """获取账户配置信息"""
        data = self.client.get("/api/v5/account/config")
        return data[0] if data else {}
    
    def get_account_balance(self, ccy: str = None) -> Dict[str, Any]:
        """获取账户余额
        
        Args:
            ccy: 币种，如 'USDT'，不传则返回所有币种
        """
        params = {}
        if ccy:
            params["ccy"] = ccy
        data = self.client.get("/api/v5/account/balance", params=params)
        return data[0] if data else {}
    
    def get_positions(self, inst_type: str = None, inst_id: str = None) -> List[Dict[str, Any]]:
        """获取持仓信息
        
        Args:
            inst_type: 产品类型，如 'SPOT', 'SWAP', 'FUTURES', 'OPTION'
            inst_id: 交易对ID，如 'BTC-USDT'
        """
        params = {}
        if inst_type:
            params["instType"] = inst_type
        if inst_id:
            params["instId"] = inst_id
        return self.client.get("/api/v5/account/positions", params=params)
    
    def get_orders(self, inst_type: str = None, inst_id: str = None, state: str = None) -> List[Dict[str, Any]]:
        """获取订单信息
        
        Args:
            inst_type: 产品类型
            inst_id: 交易对ID
            state: 订单状态，如 'filled', 'canceled', 'live'
        """
        params = {}
        if inst_type:
            params["instType"] = inst_type
        if inst_id:
            params["instId"] = inst_id
        if state:
            params["state"] = state
        return self.client.get("/api/v5/trade/orders-pending", params=params)
    
    def get_trade_fees(self, inst_type: str = None, inst_id: str = None) -> Dict[str, Any]:
        """获取交易手续费率"""
        params = {}
        if inst_type:
            params["instType"] = inst_type
        if inst_id:
            params["instId"] = inst_id
        data = self.client.get("/api/v5/account/trade-fee", params=params)
        return data[0] if data else {}
    
    def get_asset_valuation(self, ccy: str = "USD") -> Dict[str, Any]:
        """获取资产估值（按法币计价）"""
        params = {"ccy": ccy}
        data = self.client.get("/api/v5/asset/asset-valuation", params=params)
        return data[0] if data else {}
    
    def get_interest_accrued(self, inst_type: str = None, ccy: str = None) -> List[Dict[str, Any]]:
        """获取计息记录"""
        params = {}
        if inst_type:
            params["instType"] = inst_type
        if ccy:
            params["ccy"] = ccy
        return self.client.get("/api/v5/account/interest-accrued", params=params)
    
    def get_max_withdrawal(self, ccy: str) -> Dict[str, Any]:
        """获取最大可提币数量"""
        params = {"ccy": ccy}
        data = self.client.get("/api/v5/account/max-withdrawal", params=params)
        return data[0] if data else {}
    
    def analyze_all(self) -> Dict[str, Any]:
        """综合分析所有账户信息"""
        print("正在获取账户信息...")
        result = {
            "账户类型": "模拟盘" if self.simulated else "实盘",
            "账户配置": {},
            "账户余额": {},
            "持仓信息": [],
            "挂单信息": [],
            "手续费率": {},
            "资产估值": {},
        }
        
        try:
            # 账户配置
            print("  - 获取账户配置...")
            result["账户配置"] = self.get_account_config()
        except Exception as e:
            result["账户配置"] = {"错误": str(e)}
        
        try:
            # 账户余额
            print("  - 获取账户余额...")
            balance_data = self.get_account_balance()
            result["账户余额"] = balance_data
        except Exception as e:
            result["账户余额"] = {"错误": str(e)}
        
        try:
            # 持仓信息
            print("  - 获取持仓信息...")
            result["持仓信息"] = self.get_positions()
        except Exception as e:
            result["持仓信息"] = [{"错误": str(e)}]
        
        try:
            # 挂单信息
            print("  - 获取挂单信息...")
            result["挂单信息"] = self.get_orders()
        except Exception as e:
            result["挂单信息"] = [{"错误": str(e)}]
        
        try:
            # 手续费率
            print("  - 获取手续费率...")
            result["手续费率"] = self.get_trade_fees()
        except Exception as e:
            result["手续费率"] = {"错误": str(e)}
        
        try:
            # 资产估值
            print("  - 获取资产估值...")
            result["资产估值"] = self.get_asset_valuation()
        except Exception as e:
            result["资产估值"] = {"错误": str(e)}
        
        return result
    
    def print_summary(self, analysis_result: Dict[str, Any]):
        """打印账户摘要信息"""
        print("\n" + "="*60)
        print("OKX 账户分析报告")
        print("="*60)
        
        print(f"\n账户类型: {analysis_result['账户类型']}")
        
        # 账户配置摘要
        if "账户配置" in analysis_result and "错误" not in analysis_result["账户配置"]:
            config = analysis_result["账户配置"]
            print("\n【账户配置】")
            print(f"  账户等级: {config.get('acctLv', 'N/A')}")
            print(f"  持仓模式: {config.get('posMode', 'N/A')}")
            print(f"  保证金模式: {config.get('mgnMode', 'N/A')}")
            print(f"  希腊值类型: {config.get('greeksType', 'N/A')}")
            print(f"  自动借币: {config.get('autoLoan', 'N/A')}")
        
        # 账户余额摘要
        if "账户余额" in analysis_result and "错误" not in analysis_result["账户余额"]:
            balance = analysis_result["账户余额"]
            details = balance.get("details", [])
            if details:
                print("\n【账户余额】")
                for detail in details:
                    ccy = detail.get("ccy", "N/A")
                    avail = detail.get("availBal", "0")
                    frozen = detail.get("frozenBal", "0")
                    equity = detail.get("eq", "0")
                    print(f"  {ccy}:")
                    print(f"    可用余额: {avail}")
                    print(f"    冻结余额: {frozen}")
                    print(f"    权益: {equity}")
        
        # 持仓摘要
        if "持仓信息" in analysis_result and analysis_result["持仓信息"]:
            positions = analysis_result["持仓信息"]
            if positions and "错误" not in positions[0]:
                print("\n【持仓信息】")
                for pos in positions:
                    inst_id = pos.get("instId", "N/A")
                    pos_size = pos.get("pos", "0")
                    avg_px = pos.get("avgPx", "0")
                    upl = pos.get("upl", "0")
                    print(f"  {inst_id}:")
                    print(f"    持仓数量: {pos_size}")
                    print(f"    平均价格: {avg_px}")
                    print(f"    未实现盈亏: {upl}")
        
        # 挂单摘要
        if "挂单信息" in analysis_result and analysis_result["挂单信息"]:
            orders = analysis_result["挂单信息"]
            if orders and "错误" not in orders[0]:
                print(f"\n【挂单信息】共 {len(orders)} 个挂单")
                for order in orders[:5]:  # 只显示前5个
                    inst_id = order.get("instId", "N/A")
                    side = order.get("side", "N/A")
                    px = order.get("px", "0")
                    sz = order.get("sz", "0")
                    print(f"  {inst_id} {side} {sz} @ {px}")
        
        # 资产估值
        if "资产估值" in analysis_result and "错误" not in analysis_result["资产估值"]:
            valuation = analysis_result["资产估值"]
            total_equity = valuation.get("details", {}).get("totalEq", "0")
            print(f"\n【资产估值】")
            print(f"  总权益: {total_equity} USD")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    # 创建分析器（默认使用配置中的模拟盘设置）
    analyzer = AccountAnalyzer()
    
    # 执行完整分析
    result = analyzer.analyze_all()
    
    # 打印摘要
    analyzer.print_summary(result)
    
    # 保存详细结果到JSON文件
    output_file = "account_analysis_result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n详细结果已保存到: {output_file}")
