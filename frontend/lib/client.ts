import { Client } from "@langchain/langgraph-sdk";

export const client = new Client({
  apiUrl: "https://ht-downright-spray-60-5e4f7a16f5985dd7b649b3edb608dabd.us.langgraph.app", // LangGraph API URL
  apiKey: "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", // LangSmith API Key
});