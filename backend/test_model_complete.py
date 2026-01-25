"""
测试完整的 model.py 计算流程
验证:
1. Python 计算函数
2. Excel 直接读取函数
"""
import sys
import os
sys.path.insert(0, 'd:/work/110agenticAI/code/ai-deal-associate/backend')

from deal_agent.nodes.model import (
    calculate_metrics_excel_compatible, 
    read_excel_cash_flows_and_calculate,
    xirr
)
from datetime import datetime

TEMPLATE_PATH = r"d:\work\110agenticAI\code\ai-deal-associate\backend\data\templates\MS Canopy Template -v5.xlsx"

# Excel期望值
EXCEL_EQUITY_INVESTED = 2_519_945
EXCEL_IRR = 0.1230
EXCEL_MULTIPLE = 2.03

print("="*70)
print("测试 model.py 完整计算流程")
print("="*70)

# 测试1: Python 计算 (使用实际的输入参数)
print("\n📊 测试1: Python 计算 (calculate_metrics_excel_compatible)")
print("-"*50)

inputs = {
    "entry_yield": 0.065,
    "exit_yield": 0.0475,
    "rent_growth": 0.02,
    "ltv": 0.60,
    "interest_rate": 0.0575,
    "purchasers_costs": 0.065,
    "hold_period": 7,
    "opex_ratio": 0.0,
}

# 使用正确的NOI (从Excel GRI分析得到)
correct_noi = 409_491

python_result = calculate_metrics_excel_compatible(inputs, passing_rent_total=correct_noi)

print(f"Equity Invested: €{python_result['debug']['equity_invested']:,.2f}")
print(f"Levered IRR: {python_result['irr']*100:.2f}%" if python_result['irr'] else "Levered IRR: N/A")
print(f"Levered Multiple: {python_result['equity_multiple']:.2f}x")

# 测试2: Excel 直接读取
print("\n📊 测试2: Excel 直接读取 (read_excel_cash_flows_and_calculate)")
print("-"*50)

if os.path.exists(TEMPLATE_PATH):
    excel_result = read_excel_cash_flows_and_calculate(TEMPLATE_PATH)
    
    if excel_result:
        print(f"Equity Invested: €{excel_result['equity_invested']:,.2f}")
        print(f"Levered IRR: {excel_result['irr']*100:.2f}%" if excel_result['irr'] else "Levered IRR: N/A")
        print(f"Levered Multiple: {excel_result['equity_multiple']:.2f}x")
        print(f"Cash Flows Count: {excel_result['cash_flows_count']}")
        
        # 验证与Excel期望值
        print("\n📋 与Excel期望值对比:")
        print(f"  Equity: €{excel_result['equity_invested']:,.0f} vs €{EXCEL_EQUITY_INVESTED:,} (差异: €{abs(excel_result['equity_invested']-EXCEL_EQUITY_INVESTED):,.0f})")
        
        if excel_result['irr']:
            irr_diff = abs(excel_result['irr'] - EXCEL_IRR) * 100
            print(f"  IRR: {excel_result['irr']*100:.2f}% vs {EXCEL_IRR*100:.2f}% (差异: {irr_diff:.2f}%)")
        
        mult_diff = abs(excel_result['equity_multiple'] - EXCEL_MULTIPLE)
        print(f"  Multiple: {excel_result['equity_multiple']:.2f}x vs {EXCEL_MULTIPLE:.2f}x (差异: {mult_diff:.2f})")
        
        # 判断是否匹配
        print("\n✅ 匹配检查:")
        if excel_result['irr'] and abs(excel_result['irr'] - EXCEL_IRR) < 0.005:
            print("  🎉 IRR 匹配 (误差<0.5%)")
        else:
            print("  ❌ IRR 不匹配")
            
        if abs(excel_result['equity_multiple'] - EXCEL_MULTIPLE) < 0.05:
            print("  🎉 Multiple 匹配 (误差<0.05)")
        else:
            print("  ❌ Multiple 不匹配")
    else:
        print("❌ Excel读取失败")
else:
    print(f"❌ Excel文件不存在: {TEMPLATE_PATH}")

print("\n" + "="*70)
