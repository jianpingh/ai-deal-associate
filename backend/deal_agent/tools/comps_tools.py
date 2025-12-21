from deal_agent.tools.vector_store import get_pinecone_index
from langchain_openai import OpenAIEmbeddings

def calculate_blended_rent(comps_data: list) -> float:
    """
    Calculates the weighted average (blended) market rent based on size.
    Expects comps_data to have 'rent' and 'size' fields.
    """
    total_rent_mass = 0
    total_size = 0
    
    for comp in comps_data:
        try:
            # Parse rent (e.g., "82", "€82", 82.5)
            rent_val = comp.get("rent", 0)
            if isinstance(rent_val, str):
                rent_str = rent_val.replace("€", "").replace("£", "").strip()
                rent = float(rent_str)
            else:
                rent = float(rent_val)
            
            # Parse size (e.g., "52k m2", "60,000 sqft", 52000)
            size_val = comp.get("size", 0)
            if isinstance(size_val, str):
                size_raw = size_val.lower()
                multiplier = 1000 if 'k' in size_raw else 1
                # Handle both m2 and m²
                clean_size = size_raw.replace("k", "").replace("m²", "").replace("m2", "").replace("sqft", "").replace(",", "").strip()
                size = float(clean_size) * multiplier
            else:
                size = float(size_val)
            
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
    Fetches comparable properties from the Pinecone vector database.
    Returns a list of comparable properties.
    """
    try:
        index = get_pinecone_index()
        if not index:
            print("Pinecone index not found, returning empty list.")
            return []

        # Initialize Embeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Construct a query vector
        query_text = f"{asset_type} market comparables"
        if location:
            query_text += f" in {location}"
            
        vector = embeddings.embed_query(query_text)

        # Query 'market_comps' namespace
        results = index.query(
            vector=vector,
            top_k=10, # Fetch more to filter
            include_metadata=True,
            namespace="market_comps"
        )
        
        comps_list = []
        for match in results.matches:
            meta = match.metadata
            # Map metadata to expected format
            # Expected: name, size, yield, rent, dist
            
            # Handle size
            size_val = meta.get("size_m2", 0)
            size_str = f"{int(size_val/1000)}k m²" if size_val else "N/A"
            
            # Handle yield
            yield_val = meta.get("yield", 0)
            yield_str = f"{yield_val*100:.1f}%" if yield_val else "N/A"
            
            # Handle rent
            rent_val = meta.get("rent_psm_pa", 0)

            # Handle distance
            dist_val = meta.get("distance_km", 0)
            dist_str = f"{dist_val} km" if dist_val else "Unknown"
            
            comp = {
                "name": meta.get("name", "Unknown Asset"),
                "size": size_str,
                "yield": yield_str,
                "rent": rent_val,
                "dist": dist_str,
                "raw_metadata": meta # Keep raw data just in case
            }
            comps_list.append(comp)
            
        return comps_list

    except Exception as e:
        print(f"Error fetching comps from Pinecone: {e}")
        return []

