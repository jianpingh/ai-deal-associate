"""
最终测试：验证Python计算与Excel完全一致
"""
import sys
sys.path.insert(0, 'd:/work/110agenticAI/code/ai-deal-associate/backend')

from deal_agent.nodes.model import calculate_metrics_excel_compatible, xirr
from datetime import datetime

# Excel期望值 (从实际读取)
EXCEL_EQUITY_INVESTED = 2_519_945
EXCEL_IRR = 0.1230  # 12.30%
EXCEL_MULTIPLE = 2.03
EXCEL_Q0 = -2_938_885
EXCEL_Q1 = 44_887
EXCEL_EXIT = 4_756_520

# 输入参数 (与Excel模板完全一致)
inputs = {
    "entry_yield": 0.065,     # 6.5% Entry Cap
    "exit_yield": 0.0475,     # 4.75% Exit Cap (来自Input Other B15)
    "rent_growth": 0.02,      # 2% (但Excel退出不使用!)
    "ltv": 0.60,              # 60%
    "interest_rate": 0.0575,  # 5.75%
    "purchasers_costs": 0.065,  # 6.5% Transfer Tax
    "hold_period": 7,         # 7年
    "opex_ratio": 0.0,        # 0 (NOI已经是净值)
}

correct_annual_noi = 409_491  # €409,491 (有效租约租金)

print("="*70)
print("最终测试: Python vs Excel 计算对比")
print("="*70)

result = calculate_metrics_excel_compatible(inputs, passing_rent_total=correct_annual_noi)

print("\n📊 Python计算结果:")
print(f"   Q0 (initial): €{result['debug']['q0_cf']:,.2f}")
print(f"   Q1 (operations): €{result['debug']['cash_flows_summary'].split('Q1-')[1].split('/')[0]}") 
print(f"   Equity Invested: €{result['debug']['equity_invested']:,.2f}")
print(f"   Levered IRR: {result['irr']*100:.2f}%" if result['irr'] else "   Levered IRR: N/A")
print(f"   Levered Multiple: {result['equity_multiple']:.2f}x")

print("\n📋 Excel期望值:")
print(f"   Q0 (initial): €{EXCEL_Q0:,}")
print(f"   Q1 (operations): €{EXCEL_Q1:,}")
print(f"   Equity Invested: €{EXCEL_EQUITY_INVESTED:,}")
print(f"   Levered IRR: {EXCEL_IRR*100:.2f}%")
print(f"   Levered Multiple: {EXCEL_MULTIPLE:.2f}x")

print("\n📈 差异分析:")
q0_diff = result['debug']['q0_cf'] - EXCEL_Q0
equity_diff = result['debug']['equity_invested'] - EXCEL_EQUITY_INVESTED
irr_diff = (result['irr'] - EXCEL_IRR) * 100 if result['irr'] else None
multiple_diff = result['equity_multiple'] - EXCEL_MULTIPLE

print(f"   Q0差异: €{q0_diff:,.2f} ({abs(q0_diff/EXCEL_Q0)*100:.2f}%)")
print(f"   Equity差异: €{equity_diff:,.2f} ({abs(equity_diff/EXCEL_EQUITY_INVESTED)*100:.4f}%)")
if irr_diff is not None:
    print(f"   IRR差异: {irr_diff:.4f}个百分点")
print(f"   Multiple差异: {multiple_diff:.4f}x")

print("\n🔍 调试信息:")
for key, value in result['debug'].items():
    if isinstance(value, float):
        print(f"   {key}: €{value:,.2f}")
    else:
        print(f"   {key}: {value}")

# 检查是否匹配
print("\n" + "="*70)
matches = 0
total = 4

if abs(result['debug']['equity_invested'] - EXCEL_EQUITY_INVESTED) < 10:
    print("✅ Equity Invested 匹配!")
    matches += 1
else:
    print("❌ Equity Invested 不匹配")

if abs(result['debug']['q0_cf'] - EXCEL_Q0) < 1000:
    print("✅ Q0现金流 近似匹配 (差异<€1,000)")
    matches += 1
else:
    print(f"❌ Q0现金流 不匹配 (差异€{abs(result['debug']['q0_cf'] - EXCEL_Q0):,.0f})")

if result['irr'] and abs(result['irr'] - EXCEL_IRR) < 0.005:
    print("✅ Levered IRR 匹配 (误差<0.5%)")
    matches += 1
else:
    print("❌ Levered IRR 不匹配")

if abs(result['equity_multiple'] - EXCEL_MULTIPLE) < 0.05:
    print("✅ Levered Multiple 匹配 (误差<0.05)")
    matches += 1
else:
    print("❌ Levered Multiple 不匹配")

print(f"\n匹配度: {matches}/{total}")
print("="*70)
