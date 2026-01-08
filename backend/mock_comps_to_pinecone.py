import json
import os
import random
import time
from uuid import uuid4
from dotenv import load_dotenv
import sys

# Add the current directory to sys.path to ensure we can import deal_agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_openai import OpenAIEmbeddings
from deal_agent.tools.vector_store import get_pinecone_index

# Load environment variables
load_dotenv()

# --- Configuration ---
PINECONE_NAMESPACE = "market_comps"
NUM_COMPS_TO_GENERATE = 30
# Construct path relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_FILE = os.path.join(BASE_DIR, "data", "structured_json", "sample_asset_bundle.json")

# --- Mock Data Generators ---
CITIES = ["Daventry", "Northampton", "Rugby", "Coventry", "Milton Keynes", "Birmingham", "Lutterworth", "Leicester", "Derby", "Nottingham"]
ASSET_TYPES = ["Logistics", "Industrial", "Warehouse", "Distribution Centre"]
TENANT_INDUSTRIES = ["3PL", "E-commerce", "Automotive", "Retail", "Manufacturing", "FMCG", "Pharmaceuticals"]

def generate_mock_comp(base_comp=None):
    """Generates a single mock comparable asset."""
    city = random.choice(CITIES)
    # Size between 10k and 200k sq m
    size_base = random.randint(10, 200) * 1000 
    
    # Randomize yield around 4.0% - 6.0% (0.04 - 0.06)
    yield_val = round(random.uniform(0.04, 0.075), 4)
    
    # Randomize rent around 7.0 - 12.0 GBP/sq ft -> converted to sqm approx 75 - 130
    rent_val = round(random.uniform(75, 130), 2)
    
    acquisition_year = random.randint(2018, 2024)
    acquisition_month = random.randint(1, 12)
    acquisition_day = random.randint(1, 28)
    
    comp = {
        "id": str(uuid4()),
        "name": f"{city} {random.choice(['Distribution Park', 'Logistics Hub', 'Gateway', 'Park', 'Centre'])} {random.randint(1, 20)}",
        "distance_km": random.randint(1, 50),
        "asset_type": random.choice(ASSET_TYPES),
        "size_m2": size_base,
        "yield": yield_val,
        "rent_psm_pa": rent_val,
        "acquisition_date": f"{acquisition_year}-{acquisition_month:02d}-{acquisition_day:02d}",
        "city": city,
        "country": "United Kingdom",
        "source": f"internal://{city}_Market_Report_{acquisition_year}.pdf",
        "description": f"Modern {random.choice(ASSET_TYPES).lower()} facility located in {city}. "
                       f"Acquired in {acquisition_year}. "
                       f"Key tenant in {random.choice(TENANT_INDUSTRIES)} sector. "
                       f"Good access to major transport links. Clear eaves height of {random.randint(10, 18)}m."
    }
    return comp

def main():
    print("--- 1. Loading Sample Data ---")
    print(f"Reading from: {SAMPLE_FILE}")
    try:
        with open(SAMPLE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Use the first comp as a template if available
            base_template = data.get("comps", [{}])[0]
    except FileNotFoundError:
        print(f"Warning: {SAMPLE_FILE} not found. Using pure random generation.")
        base_template = {}
    except Exception as e:
        print(f"Error reading file: {e}")
        base_template = {}

    print(f"--- 2. Generating {NUM_COMPS_TO_GENERATE} Mock Comps ---")
    mock_comps = [generate_mock_comp(base_template) for _ in range(NUM_COMPS_TO_GENERATE)]
    
    # Optional: Save generated JSON for inspection
    output_json = os.path.join(BASE_DIR, "mock_comps_generated.json")
    with open(output_json, "w", encoding='utf-8') as f:
        json.dump(mock_comps, f, indent=2)
    print(f"Saved generated comps to '{output_json}'")

    print("--- 3. Connecting to Pinecone ---")
    try:
        index = get_pinecone_index()
        if not index:
            print("Error: Could not connect to Pinecone. Check api key.")
            return
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    print("--- 4. Generating Embeddings & Upserting ---")
    # Initialize embeddings
    try:
        embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
    except Exception as e:
        print(f"Failed to initialize OpenAIEmbeddings: {e}")
        return
    
    batch_size = 10
    total_upserted = 0

    for i in range(0, len(mock_comps), batch_size):
        batch = mock_comps[i : i + batch_size]
        
        vectors_to_upsert = []
        texts_to_embed = []
        
        for comp in batch:
            # Create a rich text description for embedding
            text_representation = (
                f"Market Comparable: {comp['name']}. "
                f"Location: {comp['city']}, {comp['country']}. "
                f"Type: {comp['asset_type']}. "
                f"Size: {comp['size_m2']} sqm. "
                f"Rent: {comp['rent_psm_pa']} per sqm. "
                f"Yield: {comp['yield']*100}%. "
                f"Description: {comp['description']}"
            )
            texts_to_embed.append(text_representation)
            comp['text_representation'] = text_representation # Keep track
        
        # Batch embed
        try:
            print(f"Generating embeddings for batch {i//batch_size + 1}...")
            embeddings_list = embeddings_model.embed_documents(texts_to_embed)
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            continue

        for j, comp in enumerate(batch):
            vector = {
                "id": comp["id"],
                "values": embeddings_list[j],
                "metadata": {
                    "text": texts_to_embed[j], # Store text for RAG retrieval
                    "name": comp["name"],
                    "city": comp["city"],
                    "size_m2": comp["size_m2"],
                    "rent_psm_pa": comp["rent_psm_pa"],
                    "yield": comp["yield"],
                    "source": comp["source"],
                    "acquisition_date": comp["acquisition_date"],
                    "type": "market_comp"
                }
            }
            vectors_to_upsert.append(vector)
        
        # Upsert
        try:
            print(f"Upserting batch {i//batch_size + 1} to Pinecone namespace '{PINECONE_NAMESPACE}'...")
            index.upsert(vectors=vectors_to_upsert, namespace=PINECONE_NAMESPACE)
            total_upserted += len(vectors_to_upsert)
            print(f"Upserted batch {i//batch_size + 1}: {len(vectors_to_upsert)} vectors.")
        except Exception as e:
            print(f"Error upserting to Pinecone: {e}")

    print(f"--- Done! {total_upserted} comps added to Pinecone. ---")

if __name__ == "__main__":
    main()
