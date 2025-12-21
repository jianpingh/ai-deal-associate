import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
if not api_key:
    print("PINECONE_API_KEY not found")
    exit()

pc = Pinecone(api_key=api_key)
index_name = "deal-associate-index"

print(f"Listing indexes: {pc.list_indexes().names()}")

if index_name not in pc.list_indexes().names():
    print(f"Index {index_name} does not exist.")
    exit()

index = pc.Index(index_name)
stats = index.describe_index_stats()
print("\nIndex Stats:")
print(stats)

print("\nChecking 'deal' namespace:")
# Fetch a dummy vector to see if we can query? No, just stats is enough to see count.
# If count > 0, let's try to fetch one item if possible, or just query dummy.

from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector = embeddings.embed_query("logistics")

print("\nQuerying 'deal' namespace with 'DC1 Ingram Micro':")
vector_specific = embeddings.embed_query("DC1 Ingram Micro")
res_deal = index.query(vector=vector_specific, top_k=3, namespace="deal", include_metadata=True)
print(f"Matches: {len(res_deal.matches)}")
for m in res_deal.matches:
    print(f" - Score: {m.score}")
    print(f"   Text: {m.metadata.get('text')[:200]}...") # Print first 200 chars

print("\nQuerying 'market_comps' namespace with 'logistics':")
res_comps = index.query(vector=vector, top_k=3, namespace="market_comps", include_metadata=True)
print(f"Matches: {len(res_comps.matches)}")
for m in res_comps.matches:
    print(f" - Score: {m.score}")
    print(f"   Text: {m.metadata.get('text')[:200]}...")

