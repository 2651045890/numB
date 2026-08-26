"""
OKX 账户分析工具 - 主入口
提供统一的调用接口
"""
import json
import sys
from account_analyzer import AccountAnalyzer
from generate_report import generate_report
from config import USE_SIMULATED


def analyze_account(simulated=None, save_json=True, print_summary=True, generate_txt_report=True):
    """
    分析OKX账户信息 - 统一入口函数
    
    Args:
        simulated: bool, 是否使用模拟盘，None则使用config.py中的设置
        save_json: bool, 是否保存JSON格式的详细结果
        print_summary: bool, 是否打印摘要信息
        generate_txt_report: bool, 是否生成文本报告
    
    Returns:
        dict: 分析结果字典
    """
    # 确定是否使用模拟盘
    use_sim = simulated if simulated is not None else USE_SIMULATED
    
    print("="*70)
    print("OKX 账户分析工具")
    print("="*70)
    print(f"账户类型: {'模拟盘' if use_sim else '实盘'}\n")
    
    try:
        # 创建分析器
        analyzer = AccountAnalyzer(simulated=use_sim)
        
        # 执行完整分析
        result = analyzer.analyze_all()
        
        # 打印摘要
        if print_summary:
            analyzer.print_summary(result)
        
        # 保存JSON结果
        if save_json:
            output_file = "account_analysis_result.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n详细结果已保存到: {output_file}")
        
        # 生成文本报告
        if generate_txt_report:
            try:
                report = generate_report("account_analysis_result.json" if save_json else None)
                report_file = "account_report.txt"
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(report)
                print(f"文本报告已保存到: {report_file}")
            except Exception as e:
                print(f"生成文本报告时出错: {str(e)}")
        
        print("\n" + "="*70)
        print("分析完成！")
        print("="*70)
        
        return result
        
    except Exception as e:
        print(f"\n❌ 分析失败: {str(e)}")
        print("\n请检查:")
        print("1. API密钥是否正确")
        print("2. API密钥是否有读取权限")
        print("3. 网络连接是否正常")
        print("4. 是否使用了正确的账户类型（模拟盘/实盘）")
        return None


def get_account_balance(ccy=None, simulated=None):
    """
    快速获取账户余额
    
    Args:
        ccy: str, 币种，如 'USDT'，不传则返回所有币种
        simulated: bool, 是否使用模拟盘
    
    Returns:
        dict: 余额信息
    """
    use_sim = simulated if simulated is not None else USE_SIMULATED
    analyzer = AccountAnalyzer(simulated=use_sim)
    return analyzer.get_account_balance(ccy=ccy)


def get_account_config(simulated=None):
    """
    快速获取账户配置
    
    Args:
        simulated: bool, 是否使用模拟盘
    
    Returns:
        dict: 账户配置信息
    """
    use_sim = simulated if simulated is not None else USE_SIMULATED
    analyzer = AccountAnalyzer(simulated=use_sim)
    return analyzer.get_account_config()


def get_positions(inst_type=None, inst_id=None, simulated=None):
    """
    快速获取持仓信息
    
    Args:
        inst_type: str, 产品类型，如 'SPOT', 'SWAP', 'FUTURES'
        inst_id: str, 交易对ID，如 'BTC-USDT'
        simulated: bool, 是否使用模拟盘
    
    Returns:
        list: 持仓信息列表
    """
    use_sim = simulated if simulated is not None else USE_SIMULATED
    analyzer = AccountAnalyzer(simulated=use_sim)
    return analyzer.get_positions(inst_type=inst_type, inst_id=inst_id)


def get_orders(inst_type=None, inst_id=None, state=None, simulated=None):
    """
    快速获取挂单信息
    
    Args:
        inst_type: str, 产品类型
        inst_id: str, 交易对ID
        state: str, 订单状态
        simulated: bool, 是否使用模拟盘
    
    Returns:
        list: 订单信息列表
    """
    use_sim = simulated if simulated is not None else USE_SIMULATED
    analyzer = AccountAnalyzer(simulated=use_sim)
    return analyzer.get_orders(inst_type=inst_type, inst_id=inst_id, state=state)


def quick_test(simulated=None):
    """
    快速测试API连接
    
    Args:
        simulated: bool, 是否使用模拟盘
    
    Returns:
        bool: 测试是否通过
    """
    use_sim = simulated if simulated is not None else USE_SIMULATED
    
    print("="*70)
    print("OKX 账户分析工具 - 快速测试")
    print("="*70)
    print(f"\n使用{'模拟盘' if use_sim else '实盘'}账户\n")
    
    try:
        analyzer = AccountAnalyzer(simulated=use_sim)
        
        # 测试1: 获取账户配置
        print("测试1: 获取账户配置...")
        config = analyzer.get_account_config()
        print("✓ 成功获取账户配置")
        print(f"  账户等级: {config.get('acctLv', 'N/A')}")
        print(f"  持仓模式: {config.get('posMode', 'N/A')}")
        
        # 测试2: 获取账户余额
        print("\n测试2: 获取账户余额...")
        balance = analyzer.get_account_balance()
        print("✓ 成功获取账户余额")
        if balance.get("details"):
            print(f"  币种数量: {len(balance.get('details', []))}")
        
        # 测试3: 获取持仓信息
        print("\n测试3: 获取持仓信息...")
        positions = analyzer.get_positions()
        print(f"✓ 成功获取持仓信息，共 {len(positions)} 个持仓")
        
        print("\n" + "="*70)
        print("所有测试通过！工具运行正常。")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        print("\n请检查:")
        print("1. API密钥是否正确")
        print("2. API密钥是否有读取权限")
        print("3. 网络连接是否正常（如需要代理，请检查代理设置）")
        print("4. 是否使用了正确的账户类型（模拟盘/实盘）")
        return False


def main():
    """
    命令行主函数
    支持命令行参数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='OKX 账户分析工具')
    parser.add_argument('--mode', choices=['analyze', 'test', 'balance', 'config', 'positions', 'orders'],
                        default='analyze', help='运行模式')
    parser.add_argument('--simulated', action='store_true', help='使用模拟盘')
    parser.add_argument('--real', action='store_true', help='使用实盘')
    parser.add_argument('--ccy', type=str, help='币种（用于balance模式）')
    parser.add_argument('--inst-type', type=str, help='产品类型（用于positions/orders模式）')
    parser.add_argument('--inst-id', type=str, help='交易对ID（用于positions/orders模式）')
    parser.add_argument('--no-json', action='store_true', help='不保存JSON文件')
    parser.add_argument('--no-report', action='store_true', help='不生成文本报告')
    parser.add_argument('--quiet', action='store_true', help='不打印摘要')
    
    args = parser.parse_args()
    
    # 确定是否使用模拟盘
    if args.real:
        simulated = False
    elif args.simulated:
        simulated = True
    else:
        simulated = None  # 使用config.py中的默认值
    
    # 根据模式执行相应操作
    if args.mode == 'analyze':
        analyze_account(
            simulated=simulated,
            save_json=not args.no_json,
            print_summary=not args.quiet,
            generate_txt_report=not args.no_report
        )
    elif args.mode == 'test':
        quick_test(simulated=simulated)
    elif args.mode == 'balance':
        balance = get_account_balance(ccy=args.ccy, simulated=simulated)
        print(json.dumps(balance, ensure_ascii=False, indent=2))
    elif args.mode == 'config':
        config = get_account_config(simulated=simulated)
        print(json.dumps(config, ensure_ascii=False, indent=2))
    elif args.mode == 'positions':
        positions = get_positions(
            inst_type=args.inst_type,
            inst_id=args.inst_id,
            simulated=simulated
        )
        print(json.dumps(positions, ensure_ascii=False, indent=2))
    elif args.mode == 'orders':
        orders = get_orders(
            inst_type=args.inst_type,
            inst_id=args.inst_id,
            simulated=simulated
        )
        print(json.dumps(orders, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # 如果直接运行，执行完整分析
    if len(sys.argv) == 1:
        # 无参数时，执行完整分析
        analyze_account()
    else:
        # 有参数时，使用命令行模式
        main()
