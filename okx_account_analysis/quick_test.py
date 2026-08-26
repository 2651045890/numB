"""
快速测试脚本 - 验证API连接和基本功能
"""
from account_analyzer import AccountAnalyzer
from config import USE_SIMULATED

def main():
    print("="*60)
    print("OKX 账户分析工具 - 快速测试")
    print("="*60)
    print(f"\n使用{'模拟盘' if USE_SIMULATED else '实盘'}账户\n")
    
    try:
        analyzer = AccountAnalyzer()
        
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
        
        print("\n" + "="*60)
        print("所有测试通过！工具运行正常。")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        print("\n请检查:")
        print("1. API密钥是否正确")
        print("2. API密钥是否有读取权限")
        print("3. 网络连接是否正常（如需要代理，请检查代理设置）")
        print("4. 是否使用了正确的账户类型（模拟盘/实盘）")

if __name__ == "__main__":
    main()
