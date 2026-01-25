"""
检查实际数据提取逻辑
"""
import json

# 读取sample JSON
with open('d:/work/110agenticAI/code/ai-deal-associate/backend/data/structured_json/sample_asset_bundle.json') as f:
    source_json = json.load(f)

print("="*70)
print("检查实际数据结构")
print("="*70)

# 模拟build_model中的数据提取逻辑
tenancy_data = []
if "assets" in source_json:
    for asset in source_json["assets"]:
        if "leases" in asset:
            for lease in asset["leases"]:
                t_name = "Unknown"
                if isinstance(lease.get("tenant"), dict):
                    t_name = lease["tenant"].get("name", "Unknown")
                elif isinstance(lease.get("tenant"), str):
                    t_name = lease.get("tenant")
                
                area_val = float(lease.get("area_m2") or 0)
                current_rent_val = float(lease.get("annual_rent") or (area_val * float(lease.get("rent_psm_pa") or 0)))
                
                lease_obj = {
                    "name": t_name,
                    "area": area_val,
                    "lease_start": lease.get("lease_start"),
                    "lease_end": lease.get("lease_end"),
                    "current_rent": current_rent_val
                }
                tenancy_data.append(lease_obj)
                print(f"\n租户: {t_name}")
                print(f"  面积: {area_val:,.0f} m²")
                print(f"  租约开始: {lease.get('lease_start')}")
                print(f"  租约结束: {lease.get('lease_end')}")
                print(f"  年租金: €{current_rent_val:,.2f}")

print("\n" + "="*70)
total_rent = sum(t['current_rent'] for t in tenancy_data)
print(f"Total Passing Rent: €{total_rent:,.2f}")

# 测试effective_noi计算
import sys
sys.path.insert(0, 'd:/work/110agenticAI/code/ai-deal-associate/backend')
from deal_agent.nodes.model import calculate_effective_noi

effective_noi, explanation = calculate_effective_noi(tenancy_data)
print(f"Effective NOI: €{effective_noi:,.2f}")
print(f"Explanation: {explanation}")
print("="*70)
