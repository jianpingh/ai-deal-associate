"""
端到端测试 - 模拟实际的build_model流程
"""
import sys
sys.path.insert(0, 'd:/work/110agenticAI/code/ai-deal-associate/backend')

from deal_agent.nodes.model import calculate_effective_noi, calculate_metrics_excel_compatible, get_model_inputs

# 模拟实际租户数据 (来自PDF/JSON)
tenancy_data = [
    {
        "name": "Ingram Micro",
        "area": 172221,
        "lease_start": "2015-01-01",
        "lease_end": "2020-05-31",
        "current_rent": 1222215.50
    },
    {
        "name": "CNH Industrial", 
        "area": 50000,
        "lease_start": "2018-06-01",
        "lease_end": "2021-10-22",
        "current_rent": 409491.00
    }
]

# 模拟assumptions
assumptions = {
    "entry_yield": 0.065,
    "exit_yield": 0.0475,
    "rent_growth": 0.02,
    "ltv": 0.60,
    "interest_rate": 0.045,
    "purchasers_costs": 0.05,
    "hold_period": 7,
}

print("="*70)
print("端到端测试 - 模拟build_model流程")
print("="*70)

# Step 1: 获取模型输入
inputs = get_model_inputs(assumptions)
print(f"\n📋 Model Inputs:")
print(f"  Entry Cap: {inputs['entry_yield']*100:.2f}%")
print(f"  Exit Cap: {inputs['exit_yield']*100:.2f}%")
print(f"  LTV: {inputs['ltv']*100:.0f}%")
print(f"  Interest Rate: {inputs['interest_rate']*100:.2f}%")
print(f"  Purchasers Costs: {inputs['purchasers_costs']*100:.2f}%")
print(f"  Hold Period: {inputs['hold_period']} years")

# Step 2: 计算租金
total_passing_rent = sum([float(t.get("current_rent", 0)) for t in tenancy_data])
print(f"\n📋 Rent Data:")
print(f"  Total Passing Rent: €{total_passing_rent:,.2f}")

# Step 3: 计算有效NOI (关键!)
effective_noi, noi_explanation = calculate_effective_noi(tenancy_data)
print(f"  Effective NOI: €{effective_noi:,.2f}")
print(f"  Explanation: {noi_explanation}")

# Step 4: 计算指标
print(f"\n📊 计算指标 (使用Effective NOI):")
metrics = calculate_metrics_excel_compatible(inputs, passing_rent_total=effective_noi)

equity_invested = metrics['debug']['equity_invested']
irr = metrics['irr']
multiple = metrics['equity_multiple']

print(f"  Equity Invested: €{equity_invested:,.2f}")
print(f"  Levered IRR: {irr*100:.2f}%" if irr else "  Levered IRR: N/A")
print(f"  Levered Multiple: {multiple:.2f}x")

# 对比使用Total Passing Rent的错误结果
print(f"\n📊 对比 (如果错误使用Total Passing Rent):")
wrong_metrics = calculate_metrics_excel_compatible(inputs, passing_rent_total=total_passing_rent)
print(f"  Equity Invested: €{wrong_metrics['debug']['equity_invested']:,.2f}")
print(f"  Levered IRR: {wrong_metrics['irr']*100:.2f}%" if wrong_metrics['irr'] else "  Levered IRR: N/A")
print(f"  Levered Multiple: {wrong_metrics['equity_multiple']:.2f}x")

# Excel期望值
print(f"\n📋 Excel期望值:")
print(f"  Equity Invested: €2,519,945")
print(f"  Levered IRR: 12.30%")
print(f"  Levered Multiple: 2.03x")

print("\n" + "="*70)
if abs(equity_invested - 2519945) < 10 and irr and abs(irr - 0.1230) < 0.01:
    print("✅ 测试通过! Python计算与Excel完全一致")
else:
    print("❌ 测试失败! 需要检查代码")
print("="*70)
