def calculate_blended_rent(comps_data: list) -> float:
    """
    Calculates the weighted average (blended) market rent based on size.
    Expects comps_data to have 'rent' and 'size' fields.
    """
    total_rent_mass = 0
    total_size = 0
    
    for comp in comps_data:
        try:
            # Parse rent (e.g., "82", "€82")
            rent_str = str(comp.get("rent", "0")).replace("€", "").strip()
            rent = float(rent_str)
            
            # Parse size (e.g., "52k m2", "60,000 sqft")
            # Simple heuristic: remove non-numeric chars except '.' and 'k' multiplier
            size_raw = str(comp.get("size", "0")).lower()
            multiplier = 1000 if 'k' in size_raw else 1
            
            # Remove common units and separators
            clean_size = size_raw.replace("k", "").replace("m2", "").replace("sqft", "").replace(",", "").strip()
            size = float(clean_size) * multiplier
            
            if size > 0:
                total_rent_mass += rent * size
                total_size += size
        except (ValueError, TypeError):
            continue
            
    if total_size == 0:
        return 0.0
        
    return round(total_rent_mass / total_size, 2)
