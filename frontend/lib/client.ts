import { Client } from "@langchain/langgraph-sdk";

export const client = new Client({
  apiUrl: process.env.NEXT_PUBLIC_LANGGRAPH_API_URL || "http://localhost:8000",
});
