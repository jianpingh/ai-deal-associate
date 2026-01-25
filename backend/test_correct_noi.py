"""
测试使用正确的 NOI (€409,491 - 只有有效租约) 计算财务指标
"""
import sys
sys.path.insert(0, 'd:/work/110agenticAI/code/ai-deal-associate/backend')

from deal_agent.nodes.model import calculate_metrics_excel_compatible, xirr
from datetime import datetime

# Excel期望值
EXCEL_EQUITY_INVESTED = 2_519_945  # €2,519,945
EXCEL_IRR = 0.1230  # 12.30%
EXCEL_MULTIPLE = 2.03

# 输入参数 (与Excel模板一致)
inputs = {
    "entry_yield": 0.065,     # 6.5%
    "exit_yield": 0.065,      # 6.5%
    "rent_growth": 0.02,      # 2%
    "ltv": 0.60,              # 60%
    "interest_rate": 0.0575,  # 5.75%
    "purchasers_costs": 0.065,  # 6.5%
    "hold_period": 5,         # 5 years
    "opex_ratio": 0.0,        # 现在设为0，因为我们直接使用NOI
}

# 关键: 使用正确的NOI (只有有效租约 - Tenant 2的租金)
# 这就是Excel GRI Sheet计算出来的值
correct_annual_noi = 409_491  # €409,491 (only Tenant 2's rent)

print("="*70)
print("测试: 使用正确的 NOI (€409,491 - 只有有效租约)")
print("="*70)

# 使用正确的NOI计算
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

# 验证关键中间值
print("\n✅ 中间值验证:")
print(f"   Purchase Price = NOI/Entry Cap = {correct_annual_noi}/{inputs['entry_yield']} = €{correct_annual_noi/inputs['entry_yield']:,.2f}")
print(f"   TIC = €{result['debug']['tic']:,.2f}")
print(f"   Senior Debt = TIC × LTV = €{result['debug']['tic']:,.2f} × {inputs['ltv']} = €{result['debug']['loan_amount']:,.2f}")
print(f"   Equity = TIC - Senior Debt = €{result['debug']['tic']:,.2f} - €{result['debug']['loan_amount']:,.2f} = €{result['debug']['equity_invested']:,.2f}")

# 检查是否匹配
print("\n" + "="*70)
if abs(result['debug']['equity_invested'] - EXCEL_EQUITY_INVESTED) < 10:
    print("🎉 Equity Invested 匹配!")
else:
    print("❌ Equity Invested 不匹配")

if result['irr'] and abs(result['irr'] - EXCEL_IRR) < 0.005:
    print("🎉 Levered IRR 匹配 (误差<0.5%)")
else:
    print("❌ Levered IRR 不匹配")

if abs(result['equity_multiple'] - EXCEL_MULTIPLE) < 0.05:
    print("🎉 Levered Multiple 匹配 (误差<0.05)")
else:
    print("❌ Levered Multiple 不匹配")
print("="*70)
