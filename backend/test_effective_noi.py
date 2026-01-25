"""
测试有效NOI计算逻辑
"""
import sys
sys.path.insert(0, 'd:/work/110agenticAI/code/ai-deal-associate/backend')

from deal_agent.nodes.model import calculate_effective_noi, calculate_metrics_excel_compatible
from datetime import datetime

# 模拟租户数据 (与Excel模板中的数据一致)
tenancy_data = [
    {
        "name": "Ingram Micro",
        "area": 50000,
        "lease_start": "2015-01-01",
        "lease_end": "2020-05-31",  # 已过期
        "current_rent": 1222215.50
    },
    {
        "name": "CNH Industrial", 
        "area": 30000,
        "lease_start": "2018-06-01",
        "lease_end": "2021-10-22",  # 已过期，但是最近过期的
        "current_rent": 409491.00
    }
]

print("="*70)
print("测试有效NOI计算逻辑")
print("="*70)

# 计算有效NOI
effective_noi, explanation = calculate_effective_noi(tenancy_data)

print(f"\n📊 租户数据:")
total_rent = 0
for t in tenancy_data:
    print(f"  - {t['name']}: €{t['current_rent']:,.2f}, 租约结束 {t['lease_end']}")
    total_rent += t['current_rent']

print(f"\n📋 Total Passing Rent: €{total_rent:,.2f}")
print(f"📋 Effective NOI: €{effective_noi:,.2f}")
print(f"📋 解释: {explanation}")

# Excel期望值
EXCEL_EQUITY = 2_519_945
EXCEL_IRR = 0.1230
EXCEL_MULTIPLE = 2.03

# 使用有效NOI计算
inputs = {
    "entry_yield": 0.065,
    "exit_yield": 0.0475,
    "rent_growth": 0.02,
    "ltv": 0.60,
    "interest_rate": 0.045,  # 4.5% (与Excel一致)
    "purchasers_costs": 0.05,  # 5% Transfer Tax (与Excel一致)
    "hold_period": 7,
    "opex_ratio": 0.0,
}

print("\n📊 使用有效NOI计算财务指标:")
result = calculate_metrics_excel_compatible(inputs, passing_rent_total=effective_noi)

print(f"  Equity Invested: €{result['debug']['equity_invested']:,.2f}")
print(f"  Levered IRR: {result['irr']*100:.2f}%" if result['irr'] else "  Levered IRR: N/A")
print(f"  Levered Multiple: {result['equity_multiple']:.2f}x")

print(f"\n📋 Excel期望值:")
print(f"  Equity Invested: €{EXCEL_EQUITY:,}")
print(f"  Levered IRR: {EXCEL_IRR*100:.2f}%")
print(f"  Levered Multiple: {EXCEL_MULTIPLE:.2f}x")

print("\n📈 差异分析:")
equity_diff = result['debug']['equity_invested'] - EXCEL_EQUITY
irr_diff = (result['irr'] - EXCEL_IRR) * 100 if result['irr'] else None
multiple_diff = result['equity_multiple'] - EXCEL_MULTIPLE

print(f"  Equity差异: €{equity_diff:,.2f}")
if irr_diff is not None:
    print(f"  IRR差异: {irr_diff:.2f}个百分点")
print(f"  Multiple差异: {multiple_diff:.2f}x")

# 匹配检查
print("\n" + "="*70)
if abs(result['debug']['equity_invested'] - EXCEL_EQUITY) < 10:
    print("✅ Equity Invested 匹配!")
else:
    print("❌ Equity Invested 不匹配")

if result['irr'] and abs(result['irr'] - EXCEL_IRR) < 0.02:
    print("✅ Levered IRR 近似匹配 (误差<2%)")
else:
    print("❌ Levered IRR 不匹配")

if abs(result['equity_multiple'] - EXCEL_MULTIPLE) < 0.15:
    print("✅ Levered Multiple 近似匹配 (误差<0.15)")
else:
    print("❌ Levered Multiple 不匹配")
print("="*70)
