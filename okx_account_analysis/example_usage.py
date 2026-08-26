"""
使用示例 - 展示如何使用主入口函数
"""
from main import (
    analyze_account,
    get_account_balance,
    get_account_config,
    get_positions,
    get_orders,
    quick_test
)

# ============================================
# 示例1: 完整分析账户（最常用）
# ============================================
def example_full_analysis():
    """完整分析账户信息"""
    print("示例1: 完整分析账户")
    print("-" * 50)
    
    result = analyze_account(
        simulated=True,           # 使用模拟盘
        save_json=True,           # 保存JSON文件
        print_summary=True,       # 打印摘要
        generate_txt_report=True  # 生成文本报告
    )
    
    return result


# ============================================
# 示例2: 快速获取余额
# ============================================
def example_get_balance():
    """快速获取账户余额"""
    print("\n示例2: 获取账户余额")
    print("-" * 50)
    
    # 获取所有币种余额
    all_balance = get_account_balance(simulated=True)
    print("所有币种余额:", all_balance.get("details", []))
    
    # 获取USDT余额
    usdt_balance = get_account_balance(ccy="USDT", simulated=True)
    print("USDT余额:", usdt_balance)


# ============================================
# 示例3: 获取账户配置
# ============================================
def example_get_config():
    """获取账户配置"""
    print("\n示例3: 获取账户配置")
    print("-" * 50)
    
    config = get_account_config(simulated=True)
    print(f"账户等级: {config.get('acctLv')}")
    print(f"持仓模式: {config.get('posMode')}")
    print(f"API权限: {config.get('perm')}")


# ============================================
# 示例4: 获取持仓信息
# ============================================
def example_get_positions():
    """获取持仓信息"""
    print("\n示例4: 获取持仓信息")
    print("-" * 50)
    
    # 获取所有持仓
    all_positions = get_positions(simulated=True)
    print(f"总持仓数: {len(all_positions)}")
    
    # 获取现货持仓
    spot_positions = get_positions(inst_type="SPOT", simulated=True)
    print(f"现货持仓数: {len(spot_positions)}")


# ============================================
# 示例5: 获取挂单信息
# ============================================
def example_get_orders():
    """获取挂单信息"""
    print("\n示例5: 获取挂单信息")
    print("-" * 50)
    
    orders = get_orders(simulated=True)
    print(f"当前挂单数: {len(orders)}")
    
    for order in orders[:5]:  # 显示前5个
        print(f"  {order.get('instId')} - {order.get('side')} - {order.get('sz')}")


# ============================================
# 示例6: 快速测试
# ============================================
def example_quick_test():
    """快速测试API连接"""
    print("\n示例6: 快速测试")
    print("-" * 50)
    
    success = quick_test(simulated=True)
    if success:
        print("✓ API连接正常")
    else:
        print("✗ API连接失败")


# ============================================
# 主函数
# ============================================
if __name__ == "__main__":
    print("=" * 70)
    print("OKX 账户分析工具 - 使用示例")
    print("=" * 70)
    
    try:
        # 运行所有示例
        example_quick_test()
        example_get_config()
        example_get_balance()
        example_get_positions()
        example_get_orders()
        
        # 完整分析（会生成文件，所以放在最后）
        # example_full_analysis()
        
        print("\n" + "=" * 70)
        print("所有示例运行完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
