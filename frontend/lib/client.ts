/**
 * LangGraph API Client
 * Calls through FastAPI backend proxy to avoid exposing API Key in frontend
 */

// Backend API URL (development environment)
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ThreadState {
  values: Record<string, unknown>;
  next: string[];
  config?: Record<string, unknown>;
}

interface RunResult {
  thread_id: string;
  run_id: string;
  status: string;
  [key: string]: unknown;
}

interface Thread {
  thread_id: string;
  [key: string]: unknown;
}

// Client API - mimics @langchain/langgraph-sdk interface
export const client = {
  threads: {
    async create(): Promise<Thread> {
      const response = await fetch(`${API_BASE}/api/langgraph/threads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!response.ok) throw new Error("Failed to create thread");
      return response.json();
    },

    async getState(threadId: string): Promise<ThreadState> {
      const response = await fetch(
        `${API_BASE}/api/langgraph/threads/${threadId}/state`
      );
      if (!response.ok) throw new Error("Failed to get thread state");
      return response.json();
    },

    async updateState(
      threadId: string,
      state: { values: Record<string, unknown>; asNode?: string }
    ): Promise<unknown> {
      const response = await fetch(
        `${API_BASE}/api/langgraph/threads/${threadId}/state`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(state),
        }
      );
      if (!response.ok) throw new Error("Failed to update thread state");
      return response.json();
    },
  },

  runs: {
    async create(
      threadId: string,
      assistantId: string,
      options: { input?: Record<string, unknown>; config?: Record<string, unknown> }
    ): Promise<RunResult> {
      const response = await fetch(
        `${API_BASE}/api/langgraph/threads/${threadId}/runs`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            assistant_id: assistantId,
            input: options.input,
            config: options.config,
          }),
        }
      );
      if (!response.ok) throw new Error("Failed to create run");
      return response.json();
    },

    async wait(
      threadId: string,
      assistantId: string,
      options: { input?: Record<string, unknown>; config?: Record<string, unknown> }
    ): Promise<RunResult> {
      const response = await fetch(
        `${API_BASE}/api/langgraph/threads/${threadId}/runs/wait`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            assistant_id: assistantId,
            input: options.input,
            config: options.config,
          }),
        }
      );
      if (!response.ok) throw new Error("Failed to wait for run");
      return response.json();
    },

    stream(
      threadId: string,
      assistantId: string,
      options: {
        input?: Record<string, unknown>;
        config?: Record<string, unknown>;
        streamMode?: string[];
      }
    ) {
      // Returns an async iterable object
      return {
        async *[Symbol.asyncIterator]() {
          const response = await fetch(
            `${API_BASE}/api/langgraph/threads/${threadId}/runs/stream`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                assistant_id: assistantId,
                input: options.input,
                config: options.config,
                stream_mode: options.streamMode || ["values", "messages", "updates"],
              }),
            }
          );

          if (!response.ok) throw new Error("Failed to stream run");
          if (!response.body) throw new Error("No response body");

          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let buffer = "";

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            
            // Parse SSE format - need to parse both event and data
            const lines = buffer.split("\n");
            buffer = lines.pop() || "";

            let currentEvent = "";
            for (const line of lines) {
              if (line.startsWith("event: ")) {
                currentEvent = line.slice(7).trim();
              } else if (line.startsWith("data: ")) {
                const data = line.slice(6);
                if (data && data !== "[DONE]") {
                  try {
                    const parsedData = JSON.parse(data);
                    // Return object with event and data, consistent with LangGraph SDK format
                    yield {
                      event: currentEvent || "values",
                      data: parsedData,
                    };
                  } catch {
                    // Skip invalid JSON
                  }
                }
                currentEvent = ""; // Reset after yielding
              }
            }
          }
        },
      };
    },
  },

  assistants: {
    async search(): Promise<unknown[]> {
      const response = await fetch(`${API_BASE}/api/langgraph/assistants`);
      if (!response.ok) throw new Error("Failed to get assistants");
      return response.json();
    },
  },
};