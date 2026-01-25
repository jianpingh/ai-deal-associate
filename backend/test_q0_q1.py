"""
详细对比Q0和Q1现金流
"""
import sys
sys.path.insert(0, 'd:/work/110agenticAI/code/ai-deal-associate/backend')

from deal_agent.nodes.model import calculate_metrics_excel_compatible

# Excel值 (从之前分析)
EXCEL_Q0 = -2_938_885
EXCEL_Q1 = 44_887

# 输入参数 (使用与Excel一致的默认值)
inputs = {
    "entry_yield": 0.065,
    "exit_yield": 0.0475,
    "rent_growth": 0.02,
    "ltv": 0.60,
    "interest_rate": 0.045,  # 4.5%
    "purchasers_costs": 0.05,  # 5% Transfer Tax (不是6.5%)
    "hold_period": 7,
    "opex_ratio": 0.0,
}

noi = 409_491

print("="*70)
print("Q0和Q1现金流详细分析")
print("="*70)

result = calculate_metrics_excel_compatible(inputs, passing_rent_total=noi)
debug = result['debug']

print(f"\n📊 关键中间值:")
print(f"  Annual NOI: €{debug['annual_noi']:,.2f}")
print(f"  Purchase Price: €{debug['purchase_price']:,.2f}")
print(f"  TIC: €{debug['tic']:,.2f}")
print(f"  Total Acquisition Cost: €{debug['total_acquisition_cost']:,.2f}")
print(f"  Senior Debt: €{debug['loan_amount']:,.2f}")
print(f"  Equity Invested: €{debug['equity_invested']:,.2f}")
print(f"  Quarterly EBITDA: €{debug['quarterly_ebitda']:,.2f}")
print(f"  Quarterly Interest: €{debug['quarterly_interest']:,.2f}")

print(f"\n📋 Q0 计算:")
print(f"  Python Q0: €{debug['q0_cf']:,.2f}")
print(f"  Excel Q0: €{EXCEL_Q0:,}")
print(f"  差异: €{debug['q0_cf'] - EXCEL_Q0:,.2f}")

# 分析Q0组成
total_acq = debug['total_acquisition_cost']
senior_debt = debug['loan_amount']
q0_expected = -total_acq + senior_debt
print(f"\n  分析: -Total Acq + Senior Debt = -€{total_acq:,.2f} + €{senior_debt:,.2f} = €{q0_expected:,.2f}")

# Q1分析
quarterly_ebitda = debug['quarterly_ebitda']
quarterly_interest = debug['quarterly_interest']
pre_tax = quarterly_ebitda - quarterly_interest
tax = pre_tax * 0.25
q1_calc = pre_tax - tax

print(f"\n📋 Q1 计算:")
print(f"  EBITDA: €{quarterly_ebitda:,.2f}")
print(f"  Interest: €{quarterly_interest:,.2f}")
print(f"  Pre-tax CF: €{pre_tax:,.2f}")
print(f"  Tax (25%): €{tax:,.2f}")
print(f"  Python Q1: €{q1_calc:,.2f}")
print(f"  Excel Q1: €{EXCEL_Q1:,}")
print(f"  差异: €{q1_calc - EXCEL_Q1:,.2f}")

print(f"\n📊 现金流汇总:")
print(f"  {debug['cash_flows_summary']}")
