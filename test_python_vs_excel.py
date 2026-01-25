"""
验证新的 Python Excel-Compatible 计算与 Excel 结果是否一致
"""
import sys
sys.path.insert(0, 'backend')

from deal_agent.nodes.model import get_model_inputs, calculate_metrics_excel_compatible
from deal_agent.tools.excel_engine import calculate_excel_and_read_results
import os

# 使用与Excel模板相同的输入参数
assumptions = {
    "erv": 85.44,  # Market Rent EUR/SQM
    "leasable_area": 222221,  # SQM
    "entry_yield": 6.5,  # %
    "exit_yield": 4.75,  # %
    "rent_growth": 2.0,  # %
    "ltv": 60,  # %
    "interest_rate": 4.5,  # %
    "purchasers_costs": 5.0,  # %
    "hold_period": 7,
    "project_name": "Comparison Test"
}

# Total Passing Rent 与Excel模板一致
passing_rent = 1631706.50  # €1,631,706.50

print("=" * 70)
print("Python Excel-Compatible 计算 vs Excel COM 计算 对比")
print("=" * 70)

# 输入参数
inputs = get_model_inputs(assumptions)
print("\n【输入参数】")
print(f"  Total Passing Rent: €{passing_rent:,.2f}")
print(f"  Entry Cap Rate: {inputs['entry_yield']*100:.2f}%")
print(f"  Exit Cap Rate: {inputs['exit_yield']*100:.2f}%")
print(f"  LTV: {inputs['ltv']*100:.0f}%")
print(f"  Interest Rate: {inputs['interest_rate']*100:.2f}%")
print(f"  Hold Period: {inputs['hold_period']} years")
print(f"  Purchasers Costs: {inputs['purchasers_costs']*100:.2f}%")

# 1. Python Excel-Compatible 计算
print("\n【Python Excel-Compatible 计算】")
python_metrics = calculate_metrics_excel_compatible(inputs, passing_rent_total=passing_rent)

py_equity = python_metrics['debug'].get('equity_invested', 0)
py_irr = python_metrics['irr']
py_em = python_metrics['equity_multiple']
py_gain = python_metrics.get('net_gain_loss', 0)
py_tic = python_metrics['debug'].get('tic', 0)
py_loan = python_metrics['debug'].get('loan_amount', 0)

print(f"  Total Investment Cost (TIC): €{py_tic:,.2f}")
print(f"  Senior Debt: €{py_loan:,.2f}")
print(f"  Equity Invested: €{py_equity:,.2f}")
print(f"  Levered IRR: {py_irr*100:.2f}%" if py_irr else "  Levered IRR: N/A")
print(f"  Levered Multiple: {py_em:.2f}x" if py_em else "  Levered Multiple: N/A")
print(f"  Net Gain/(Loss): €{py_gain:,.2f}" if py_gain else "  Net Gain/(Loss): N/A")

# 显示现金流序列 (部分)
print(f"\n  Cash Flows (sample): {python_metrics['debug'].get('cash_flows', [])}")
print(f"  Dates (sample): {python_metrics['debug'].get('dates', [])}")

# 2. Excel COM 计算
print("\n【Excel COM 计算 (真实Excel模板)】")
template_path = os.path.abspath('backend/data/templates/MS Canopy Template -v5.xlsx')

if os.path.exists(template_path):
    excel_results = calculate_excel_and_read_results(template_path)
    
    if excel_results['success']:
        ex_equity = excel_results['equity_invested']
        ex_irr = excel_results['levered_irr']
        ex_em = excel_results['levered_multiple']
        ex_gain = excel_results['net_gain_loss']
        
        print(f"  Equity Invested: €{ex_equity:,.2f}" if ex_equity else "  Equity Invested: N/A")
        print(f"  Levered IRR: {ex_irr*100:.2f}%" if ex_irr else "  Levered IRR: N/A")
        print(f"  Levered Multiple: {ex_em:.2f}x" if ex_em else "  Levered Multiple: N/A")
        print(f"  Net Gain/(Loss): €{ex_gain:,.2f}" if ex_gain else "  Net Gain/(Loss): N/A")
        
        # 3. 差异分析
        print("\n" + "=" * 70)
        print("【差异分析】")
        print("=" * 70)
        
        if ex_equity and py_equity:
            diff_equity = py_equity - ex_equity
            diff_equity_pct = (diff_equity / ex_equity) * 100
            match_equity = "✓" if abs(diff_equity_pct) < 1 else "✗"
            print(f"  Equity Invested: Python €{py_equity:,.0f} vs Excel €{ex_equity:,.0f}")
            print(f"    差异: €{diff_equity:,.0f} ({diff_equity_pct:+.2f}%) {match_equity}")
        
        if ex_irr and py_irr:
            diff_irr = (py_irr - ex_irr) * 100  # 转为百分点
            match_irr = "✓" if abs(diff_irr) < 0.5 else "✗"
            print(f"  Levered IRR: Python {py_irr*100:.2f}% vs Excel {ex_irr*100:.2f}%")
            print(f"    差异: {diff_irr:+.2f} 百分点 {match_irr}")
        
        if ex_em and py_em:
            diff_em = py_em - ex_em
            match_em = "✓" if abs(diff_em) < 0.05 else "✗"
            print(f"  Levered Multiple: Python {py_em:.2f}x vs Excel {ex_em:.2f}x")
            print(f"    差异: {diff_em:+.2f}x {match_em}")
        
        if ex_gain and py_gain:
            diff_gain = py_gain - ex_gain
            diff_gain_pct = (diff_gain / ex_gain) * 100 if ex_gain != 0 else 0
            match_gain = "✓" if abs(diff_gain_pct) < 1 else "✗"
            print(f"  Net Gain/(Loss): Python €{py_gain:,.0f} vs Excel €{ex_gain:,.0f}")
            print(f"    差异: €{diff_gain:,.0f} ({diff_gain_pct:+.2f}%) {match_gain}")
        
        # 总体评估
        print("\n" + "=" * 70)
        all_match = all([
            abs((py_equity - ex_equity) / ex_equity) < 0.01 if ex_equity else True,
            abs(py_irr - ex_irr) < 0.005 if ex_irr and py_irr else True,
            abs(py_em - ex_em) < 0.05 if ex_em else True,
            abs((py_gain - ex_gain) / ex_gain) < 0.01 if ex_gain else True,
        ])
        
        if all_match:
            print("✅ 结论: Python 计算与 Excel 模板计算结果一致!")
        else:
            print("⚠️ 结论: 存在差异，需要进一步调整计算逻辑")
        print("=" * 70)
    else:
        print(f"  Error: {excel_results['error']}")
else:
    print("  Template file not found!")
