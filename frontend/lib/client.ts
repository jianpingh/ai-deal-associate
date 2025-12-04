import { Client } from "@langchain/langgraph-sdk";

// Ensure this matches your backend port (default 8083 for langgraph dev)
export const client = new Client({
  apiUrl: process.env.NEXT_PUBLIC_LANGGRAPH_API_URL || "http://localhost:8083",
});
