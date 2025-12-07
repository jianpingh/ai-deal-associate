import os
from typing import List, Dict, Any
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from deal_agent.utils.config import Config

@tool
def search_documents(query: str, deal_id: str) -> str:
    """
    Search for relevant documents in the vector database based on a query and deal ID.
    Useful for finding specific information within the deal documents (CIM, financials, etc.).
    
    Args:
        query: The search query string.
        deal_id: The unique identifier for the deal to filter results.
    """
    # MOCK DATA FOR TESTING
    return f"[MOCK] Found relevant documents for deal {deal_id} matching '{query}':\n1. CIM.pdf (Page 12): Revenue grew by 20% YoY.\n2. Financials.xlsx: EBITDA margin is 15%."

    # try:
    #     # Check for API keys
    #     if not Config.PINECONE_API_KEY:
    #         return "Error: PINECONE_API_KEY is not set in environment variables."
    #     
    #     # Initialize Pinecone
    #     pc = Pinecone(api_key=Config.PINECONE_API_KEY)
    #     
    #     # Get index name from env or default
    #     index_name = os.getenv("PINECONE_INDEX_NAME", "ai-deal-associate")
    #     
    #     index = pc.Index(index_name)
    #
    #     # Initialize Embeddings
    #     embeddings = OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY)
    #     vector = embeddings.embed_query(query)
    #
    #     # Search Pinecone
    #     # We filter by deal_id to ensure we only get results for the current deal
    #     results = index.query(
    #         vector=vector,
    #         top_k=5,
    #         include_metadata=True,
    #         filter={"deal_id": deal_id}
    #     )
    #     
    #     # Format results
    #     formatted_results = []
    #     for match in results.matches:
    #         content = match.metadata.get("text", "")
    #         source = match.metadata.get("source", "Unknown")
    #         page = match.metadata.get("page", "N/A")
    #         formatted_results.append(f"Source: {source} (Page {page})\nContent: {content}")
    #         
    #     return "\n\n".join(formatted_results) if formatted_results else "No relevant documents found."
    #
    # except Exception as e:
    #     # Log the error in a real app
    #     return f"Error searching documents: {str(e)}"
