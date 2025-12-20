import os
import json
import hashlib
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

def get_pinecone_index():
    """Initialize and return Pinecone Index"""
    index_name = "deal-associate-index"
    
    if not PINECONE_API_KEY:
        print("Error: PINECONE_API_KEY not found in environment variables.")
        return None

    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Check if index exists, create if not
    existing_indexes = [i.name for i in pc.list_indexes()]
    if index_name not in existing_indexes:
        print(f"Creating Pinecone index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=1536, # text-embedding-3-small
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
    
    return pc.Index(index_name)

def generate_deterministic_id(content: str) -> str:
    """Generate deterministic ID to prevent duplicate data"""
    return hashlib.md5(content.encode()).hexdigest()

def ingest_deal_assets(texts: List[str], metadatas: List[Dict[str, Any]], namespace="default"):
    """
    Ingest text chunks and metadata into Pinecone.
    """
    index = get_pinecone_index()
    if not index:
        return "Pinecone not configured."

    # Use text-embedding-3-small
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    try:
        vectors = embeddings.embed_documents(texts)
    except Exception as e:
        return f"Error generating embeddings: {e}"

    to_upsert = []
    for text, meta, vector in zip(texts, metadatas, vectors):
        record_id = generate_deterministic_id(text)
        # Ensure text is stored in metadata for retrieval
        if "text" not in meta:
            meta["text"] = text
        to_upsert.append((record_id, vector, meta))

    # Batch upsert
    batch_size = 100
    for i in range(0, len(to_upsert), batch_size):
        batch = to_upsert[i:i+batch_size]
        index.upsert(vectors=batch, namespace=namespace)

    return f"Successfully ingested {len(texts)} items into Pinecone (Namespace: {namespace})."
