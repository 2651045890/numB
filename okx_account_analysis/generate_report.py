"""
生成友好的账户分析报告
"""
import json
from datetime import datetime

def format_number(num_str):
    """格式化数字显示"""
    try:
        num = float(num_str)
        if num >= 1000000:
            return f"{num/1000000:.2f}M"
        elif num >= 1000:
            return f"{num/1000:.2f}K"
        else:
            return f"{num:.2f}"
    except:
        return num_str

def generate_report(json_file="account_analysis_result.json"):
    """生成友好的报告"""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    report = []
    report.append("="*70)
    report.append("OKX 账户分析报告")
    report.append("="*70)
    report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"账户类型: {data['账户类型']}")
    report.append("")
    
    # 账户配置
    if "账户配置" in data and "错误" not in data["账户配置"]:
        config = data["账户配置"]
        report.append("【账户配置信息】")
        report.append(f"  账户等级: {config.get('acctLv', 'N/A')} ({config.get('level', 'N/A')})")
        report.append(f"  KYC等级: {config.get('kycLv', 'N/A')}")
        report.append(f"  持仓模式: {config.get('posMode', 'N/A')} (net_mode=单向, long_short_mode=双向)")
        report.append(f"  结算币种: {', '.join(config.get('settleCcyList', []))}")
        report.append(f"  希腊值类型: {config.get('greeksType', 'N/A')} (PA=币本位, BS=美元本位)")
        report.append(f"  自动借币: {'是' if config.get('autoLoan') else '否'}")
        report.append(f"  现货借币: {'是' if config.get('enableSpotBorrow') else '否'}")
        report.append(f"  API权限: {config.get('perm', 'N/A')}")
        report.append(f"  账户标签: {config.get('label', 'N/A')}")
        report.append("")
    
    # 账户余额详情
    if "账户余额" in data and "错误" not in data["账户余额"]:
        balance = data["账户余额"]
        details = balance.get("details", [])
        total_eq = balance.get("totalEq", "0")
        
        report.append("【账户余额详情】")
        report.append(f"  总权益: {format_number(total_eq)} USD")
        report.append("")
        report.append("  币种明细:")
        
        # 按USD价值排序
        sorted_details = sorted(
            [d for d in details if d.get("eqUsd")],
            key=lambda x: float(x.get("eqUsd", 0)),
            reverse=True
        )
        
        for detail in sorted_details:
            ccy = detail.get("ccy", "N/A")
            avail = detail.get("availBal", "0")
            frozen = detail.get("frozenBal", "0")
            eq = detail.get("eq", "0")
            eq_usd = detail.get("eqUsd", "0")
            
            report.append(f"    {ccy}:")
            report.append(f"      数量: {eq}")
            report.append(f"      可用: {avail}")
            report.append(f"      冻结: {frozen}")
            report.append(f"      USD价值: ${format_number(eq_usd)}")
            report.append("")
    
    # 持仓信息
    if "持仓信息" in data and data["持仓信息"]:
        positions = data["持仓信息"]
        if positions and "错误" not in positions[0]:
            report.append("【持仓信息】")
            if len(positions) == 0:
                report.append("  当前无持仓")
            else:
                for pos in positions:
                    inst_id = pos.get("instId", "N/A")
                    pos_size = pos.get("pos", "0")
                    avg_px = pos.get("avgPx", "0")
                    upl = pos.get("upl", "0")
                    report.append(f"  {inst_id}:")
                    report.append(f"    持仓数量: {pos_size}")
                    report.append(f"    平均价格: {avg_px}")
                    report.append(f"    未实现盈亏: {upl}")
            report.append("")
    
    # 挂单信息
    if "挂单信息" in data and data["挂单信息"]:
        orders = data["挂单信息"]
        if orders and "错误" not in orders[0]:
            report.append("【挂单信息】")
            report.append(f"  当前挂单数: {len(orders)}")
            if len(orders) > 0:
                report.append("  最近挂单:")
                for order in orders[:10]:  # 显示前10个
                    inst_id = order.get("instId", "N/A")
                    side = order.get("side", "N/A")
                    px = order.get("px", "0")
                    sz = order.get("sz", "0")
                    state = order.get("state", "N/A")
                    report.append(f"    {inst_id} | {side} | {sz} @ {px} | {state}")
            report.append("")
    
    # 资产估值
    if "资产估值" in data and "错误" not in data["资产估值"]:
        valuation = data["资产估值"]
        details = valuation.get("details", {})
        total_bal = valuation.get("totalBal", "0")
        
        report.append("【资产估值】")
        report.append(f"  总资产: ${format_number(total_bal)}")
        if details:
            report.append("  分类明细:")
            report.append(f"    交易账户: ${format_number(details.get('trading', '0'))}")
            report.append(f"    资金账户: ${format_number(details.get('funding', '0'))}")
            report.append(f"    经典账户: ${format_number(details.get('classic', '0'))}")
            report.append(f"    赚币账户: ${format_number(details.get('earn', '0'))}")
        report.append("")
    
    report.append("="*70)
    
    return "\n".join(report)

if __name__ == "__main__":
    try:
        report = generate_report()
        print(report)
        
        # 保存到文件
        with open("account_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print("\n报告已保存到: account_report.txt")
    except FileNotFoundError:
        print("错误: 找不到 account_analysis_result.json 文件")
        print("请先运行 account_analyzer.py 生成分析结果")
    except Exception as e:
        print(f"错误: {str(e)}")
