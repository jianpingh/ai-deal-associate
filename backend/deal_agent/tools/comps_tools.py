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


def fetch_market_comparables(location: str = None, asset_type: str = "Logistics") -> list:
    """
    Simulates an API call to a market data provider (e.g., CoStar, RCA, Internal DB).
    Returns a list of comparable properties.
    """
    # Mock database
    # In a real scenario, this would query a vector DB or external API
    mock_db = [
        {"name": "Comp A", "size": "52k m2", "yield": "4.5%", "rent": "82", "dist": "20km"},
        {"name": "Comp B", "size": "60k m2", "yield": "4.7%", "rent": "85", "dist": "35km"},
        {"name": "Comp C", "size": "45k m2", "yield": "4.4%", "rent": "87", "dist": "50km"},
        {"name": "Comp D", "size": "75k m2", "yield": "4.8%", "rent": "80", "dist": "15km"}, # The XXL box
        {"name": "Comp E", "size": "40k m2", "yield": "4.3%", "rent": "90", "dist": "60km"},
    ]
    
    # Simulate filtering (if we had real logic)
    # For now, return the top 3 as the "proposed" set, or all for "search"
    return mock_db

