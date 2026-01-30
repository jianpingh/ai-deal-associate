import { Client } from "@langchain/langgraph-sdk";
import { NextRequest, NextResponse } from "next/server";

// LangGraph client - API Key 安全存储在服务端
const client = new Client({
  apiUrl: process.env.LANGGRAPH_API_URL!,
  apiKey: process.env.LANGGRAPH_API_KEY!,
});

// 默认 assistant ID
const ASSISTANT_ID = process.env.LANGGRAPH_ASSISTANT_ID || "agent";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, ...params } = body;

    switch (action) {
      case "createThread": {
        const thread = await client.threads.create();
        return NextResponse.json(thread);
      }

      case "getThreadState": {
        const { threadId } = params;
        const state = await client.threads.getState(threadId);
        return NextResponse.json(state);
      }

      case "createRun": {
        const { threadId, input, config } = params;
        const run = await client.runs.create(threadId, ASSISTANT_ID, {
          input,
          config,
        });
        return NextResponse.json(run);
      }

      case "streamRun": {
        const { threadId, input, config, streamMode } = params;
        const stream = client.runs.stream(threadId, ASSISTANT_ID, {
          input,
          config,
          streamMode: streamMode || ["values", "messages", "updates"],
        });

        // 返回流式响应
        const encoder = new TextEncoder();
        const readableStream = new ReadableStream({
          async start(controller) {
            try {
              for await (const chunk of stream) {
                const data = JSON.stringify(chunk) + "\n";
                controller.enqueue(encoder.encode(data));
              }
              controller.close();
            } catch (error) {
              controller.error(error);
            }
          },
        });

        return new Response(readableStream, {
          headers: {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            Connection: "keep-alive",
          },
        });
      }

      case "waitForRun": {
        const { threadId, input, config } = params;
        const result = await client.runs.wait(threadId, ASSISTANT_ID, {
          input,
          config,
        });
        return NextResponse.json(result);
      }

      case "updateThreadState": {
        const { threadId, values, asNode } = params;
        await client.threads.updateState(threadId, { values, asNode });
        return NextResponse.json({ success: true });
      }

      case "getAssistants": {
        const assistants = await client.assistants.search();
        return NextResponse.json(assistants);
      }

      default:
        return NextResponse.json(
          { error: "Unknown action" },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error("API Error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Internal server error" },
      { status: 500 }
    );
  }
}

// 健康检查
export async function GET() {
  return NextResponse.json({ status: "ok" });
}
