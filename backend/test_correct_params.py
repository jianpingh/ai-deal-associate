"""
用正确的参数测试计算（7年持有期，4.75% Exit Cap）
"""
import sys
sys.path.insert(0, 'd:/work/110agenticAI/code/ai-deal-associate/backend')

from deal_agent.nodes.model import calculate_metrics_excel_compatible, xirr
from datetime import datetime

# Excel期望值
EXCEL_EQUITY_INVESTED = 2_519_945  # €2,519,945
EXCEL_IRR = 0.1230  # 12.30%
EXCEL_MULTIPLE = 2.03

# 输入参数 (更正: 7年持有期, 4.75% Exit Cap)
inputs = {
    "entry_yield": 0.065,     # 6.5%
    "exit_yield": 0.0475,     # 4.75% (不是6.5%!)
    "rent_growth": 0.02,      # 2%
    "ltv": 0.60,              # 60%
    "interest_rate": 0.0575,  # 5.75%
    "purchasers_costs": 0.065,  # 6.5%
    "hold_period": 7,         # 7年 (不是5年!)
    "opex_ratio": 0.0,        # 设为0，因为我们直接使用NOI
}

correct_annual_noi = 409_491  # €409,491 

print("="*70)
print("测试: 使用正确参数 (7年持有期, 4.75% Exit Cap)")
print("="*70)

result = calculate_metrics_excel_compatible(inputs, passing_rent_total=correct_annual_noi)

print("\n📊 计算结果:")
print(f"   Equity Invested: €{result['debug']['equity_invested']:,.2f}")
print(f"   Levered IRR: {result['irr']*100:.2f}%" if result['irr'] else "   Levered IRR: N/A")
print(f"   Levered Multiple: {result['equity_multiple']:.2f}x")
print(f"   Net Gain/Loss: €{result['net_gain_loss']:,.2f}")

print("\n📋 Excel期望值:")
print(f"   Equity Invested: €{EXCEL_EQUITY_INVESTED:,}")
print(f"   Levered IRR: {EXCEL_IRR*100:.2f}%")
print(f"   Levered Multiple: {EXCEL_MULTIPLE:.2f}x")

print("\n📈 差异分析:")
equity_diff = result['debug']['equity_invested'] - EXCEL_EQUITY_INVESTED
irr_diff = (result['irr'] - EXCEL_IRR) * 100 if result['irr'] else None
multiple_diff = result['equity_multiple'] - EXCEL_MULTIPLE

print(f"   Equity差异: €{equity_diff:,.2f} ({equity_diff/EXCEL_EQUITY_INVESTED*100:.2f}%)")
if irr_diff is not None:
    print(f"   IRR差异: {irr_diff:.4f}个百分点")
print(f"   Multiple差异: {multiple_diff:.4f}x")

print("\n🔍 调试信息:")
for key, value in result['debug'].items():
    if isinstance(value, float):
        print(f"   {key}: €{value:,.2f}")
    else:
        print(f"   {key}: {value}")

# 验证退出价值计算
print("\n✅ 退出价值验证:")
exit_noi = correct_annual_noi * ((1 + 0.02) ** 7)  # 7年2%增长
print(f"   Exit NOI (7年后): €{exit_noi:,.2f}")
exit_value = exit_noi / 0.0475
print(f"   Gross Exit Value: €{exit_value:,.2f}")

# 检查是否匹配
print("\n" + "="*70)
if abs(result['debug']['equity_invested'] - EXCEL_EQUITY_INVESTED) < 10:
    print("🎉 Equity Invested 匹配!")
else:
    print("❌ Equity Invested 不匹配")

if result['irr'] and abs(result['irr'] - EXCEL_IRR) < 0.01:
    print("🎉 Levered IRR 匹配 (误差<1%)")
else:
    print("❌ Levered IRR 不匹配")

if abs(result['equity_multiple'] - EXCEL_MULTIPLE) < 0.10:
    print("🎉 Levered Multiple 匹配 (误差<0.10)")
else:
    print("❌ Levered Multiple 不匹配")
print("="*70)
