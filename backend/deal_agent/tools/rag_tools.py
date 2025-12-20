import os
from typing import List, Dict, Any
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from deal_agent.tools.vector_store import get_pinecone_index

@tool
def search_documents(query: str, deal_id: str = None) -> str:
    """
    Search for relevant documents in the vector database based on a query.
    Searches both the current deal's assets and market comparables.
    
    Args:
        query: The search query string.
        deal_id: Optional deal ID to filter results. If not provided, searches broadly.
    """
    try:
        index = get_pinecone_index()
        if not index:
            return "Error: Vector database not configured."

        # Initialize Embeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vector = embeddings.embed_query(query)

        results_text = []

        # 1. Search 'deal' namespace (Current Deal Assets)
        # Filter by deal_id if provided
        filter_dict = {"deal_id": deal_id} if deal_id else {}
        
        try:
            deal_results = index.query(
                vector=vector,
                top_k=5,
                include_metadata=True,
                namespace="deal",
                filter=filter_dict
            )
            
            for match in deal_results.matches:
                # Remove threshold to ensure we get results even for broad queries
                # if match.score > 0.5: 
                source = match.metadata.get("source", "Unknown")
                text = match.metadata.get("text", "")
                results_text.append(f"[Source: {source} (Deal Asset)]\n{text}")
        except Exception as e:
            print(f"Error searching deal namespace: {e}")

        # 2. Search 'market_comps' namespace (Market Comparables)
        # We might want to search comps even without deal_id, or use deal_id if they are associated
        # For "deals learned", we definitely want to check here.
        try:
            comp_results = index.query(
                vector=vector,
                top_k=5,
                include_metadata=True,
                namespace="market_comps",
                filter=filter_dict # Filter by deal_id if we only want comps relevant to this deal context
            )
            
            for match in comp_results.matches:
                # Remove threshold to ensure we get results even for broad queries
                # if match.score > 0.5:
                source = match.metadata.get("source", "Unknown")
                text = match.metadata.get("text", "")
                results_text.append(f"[Source: {source} (Market Comp)]\n{text}")
        except Exception as e:
            print(f"Error searching market_comps namespace: {e}")

        if not results_text:
            return "No relevant documents found in the knowledge base."

        return "\n\n".join(results_text)

    except Exception as e:
        return f"Error performing search: {e}"
    #         source = match.metadata.get("source", "Unknown")
    #         page = match.metadata.get("page", "N/A")
    #         formatted_results.append(f"Source: {source} (Page {page})\nContent: {content}")
    #         
    #     return "\n\n".join(formatted_results) if formatted_results else "No relevant documents found."
    #
    # except Exception as e:
    #     # Log the error in a real app
    #     return f"Error searching documents: {str(e)}"
