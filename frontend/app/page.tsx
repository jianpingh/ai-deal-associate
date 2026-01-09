"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { client } from "@/lib/client";
import { Send, Bot, User, Loader2, PlusCircle, Terminal, ChevronDown, ChevronRight, ArrowUp } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

interface Message {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string;
  name?: string;
  type?: string;
}

const preprocessLaTeX = (content: string) => {
  // Replace \[ ... \] with $$ ... $$
  const blockRep = content.replace(/\\\[/g, '$$').replace(/\\\]/g, '$$');
  // Replace \( ... \) with $ ... $
  const inlineRep = blockRep.replace(/\\\(/g, '$').replace(/\\\)/g, '$');
  return inlineRep;
};

const SystemLogGroup = ({ items }: { items: Message[] }) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="flex justify-start gap-4 opacity-90 group">
      <div className="w-8 h-8 flex-shrink-0" /> {/* Spacer */}
      <div className="max-w-[80%] rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden transition-all duration-200">
        {/* Header - Clickable for toggle */}
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between px-4 py-2.5 bg-gray-50 border-b border-gray-100 hover:bg-gray-100 transition-colors"
        >
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
            <Terminal className="w-3.5 h-3.5" />
            System Activity
          </div>
          {isOpen ? <ChevronDown className="w-3.5 h-3.5 text-gray-400" /> : <ChevronRight className="w-3.5 h-3.5 text-gray-400" />}
        </button>

        {/* Content - Collapsible */}
        {isOpen && (
          <div className="px-5 py-3 bg-white">
            <div className="relative">
              {/* Continuous vertical line */}
              <div className="absolute left-[7px] top-2 bottom-2 w-[2px] bg-gray-100" />
              
              <div className="space-y-2">
                {items.flatMap((msg) => 
                    msg.content.split('\n')
                        .filter(line => line.trim() && line.trim() !== "System Processing:")
                        .map((line, lineIdx) => ({
                            id: `${msg.id}-${lineIdx}`,
                            content: line
                        }))
                ).map((lineItem, idx) => (
                    <div key={lineItem.id} className="relative flex items-start gap-3">
                        {/* Icon/Dot wrapper */}
                        <div className="flex-shrink-0 w-4 h-5 flex items-center justify-center z-10 -mt-0.5">
                            <div className="w-1.5 h-1.5 rounded-full bg-gray-200" />
                        </div>
                        <div className="prose prose-sm max-w-none text-gray-600 text-xs leading-snug">
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm, remarkMath]}
                                rehypePlugins={[rehypeKatex]}
                                components={{
                                    a: ({ node, ...props }: any) => (
                                        <a {...props} className="text-blue-600 hover:underline font-medium" target="_blank" rel="noopener noreferrer" />
                                    ),
                                    strong: ({ node, ...props }: any) => (
                                        <span {...props} className="font-semibold text-gray-800" />
                                    ),
                                    p: ({ node, ...props }: any) => (
                                        <p {...props} className="m-0" />
                                    )
                                }}
                            >
                                {preprocessLaTeX(lineItem.content)}
                            </ReactMarkdown>
                        </div>
                    </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper to group consecutive system logs
const groupMessages = (msgs: Message[]) => {
  const grouped: (Message | { type: 'system_log_group', id: string, messages: Message[] })[] = [];
  let currentLogGroup: Message[] = [];

  msgs.forEach((msg) => {
    // Filter out empty assistant messages or tool messages (same as original logic)
    if (msg.role === "assistant" && !msg.content) return;
    if (msg.role === "tool" || msg.type === "tool") return;

    if (msg.name === "system_log") {
      currentLogGroup.push(msg);
    } else {
      if (currentLogGroup.length > 0) {
        grouped.push({ 
            type: 'system_log_group', 
            id: `group-${currentLogGroup[0].id}`, 
            messages: [...currentLogGroup] 
        });
        currentLogGroup = [];
      }
      grouped.push(msg);
    }
  });

  if (currentLogGroup.length > 0) {
    grouped.push({ 
        type: 'system_log_group', 
        id: `group-${currentLogGroup[0].id}`, 
        messages: [...currentLogGroup] 
    });
  }

  return grouped;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState<string>("");
  const [threadId, setThreadId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startNewChat = async () => {
    setThreadId(null);
    setMessages([]);
    setSystemStatus("");
    setInput("");
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setSystemStatus("");

    try {
      let currentThreadId = threadId;
      if (!currentThreadId) {
        const thread = await client.threads.create();
        currentThreadId = thread.thread_id;
        setThreadId(currentThreadId);
      }

      const stream = client.runs.stream(
        currentThreadId,
        "agent",
        {
          input: { messages: [{ role: "user", content: userMessage.content }] },
          streamMode: "values",
        }
      );

      let assistantMessageId = (Date.now() + 1).toString();
      let assistantContent = "";

      // Add a placeholder for the assistant message
      setMessages((prev) => [
        ...prev,
        { id: assistantMessageId, role: "assistant", content: "" },
      ]);

      for await (const chunk of stream) {
        if (chunk.event === "values" && chunk.data.messages) {
          const msgs = chunk.data.messages;
          // Process all new messages
          // We need to handle the case where multiple messages come in one chunk
          // Since we are in "values" mode, we get the full history.
          // We need to find the messages that correspond to this run.
          
          // Simple approach: Look at the last few messages
          // If we find a system_log that we haven't added, add it.
          // If we find an agent message, update the placeholder.

          // Better approach for this specific UI requirement:
          // Just update the messages state to reflect the latest state from the server,
          // but we need to map the server messages to our UI format.
          
          // Let's stick to the current pattern but handle system_log as a separate message type in the UI
          
          // Filter messages to only include those after the last user message
          let lastUserIndex = -1;
          for (let i = msgs.length - 1; i >= 0; i--) {
            if (msgs[i].role === "user" || msgs[i].type === "human") {
                lastUserIndex = i;
                break;
            }
          }
          
          const relevantMessages = lastUserIndex !== -1 ? msgs.slice(lastUserIndex + 1) : [];

          if (relevantMessages.length > 0) {
            setMessages((prev) => {
              // 1. Find where the current turn started (the user message we just added)
              const userMsgIndex = prev.findIndex(m => m.id === userMessage.id);
              if (userMsgIndex === -1) return prev;

              // 2. Keep history up to and including the user message
              // This effectively removes the "placeholder" and replaces it with actual server messages
              const history = prev.slice(0, userMsgIndex + 1);

              // 3. Map server messages to frontend format
              const newFrontendMessages = relevantMessages.map((msg: any, index: number) => ({
                id: `${userMessage.id}_response_${index}`, // Stable ID based on sequence
                role: msg.role || "assistant", // Use role from server if available
                content: typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content),
                name: msg.name || "agent",
                type: msg.type // Capture message type (e.g. 'tool')
              }));

              return [...history, ...newFrontendMessages];
            });
          }
        }
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen font-sans text-gray-900 bg-white">
      {/* Sidebar */}
      <div className="flex flex-col w-64 bg-[#1a3c54] border-r border-[#153043]">
        <div className="px-6 py-5 border-b border-[#234e6b]">
          <div className="flex flex-col gap-0.5">
            <h1 className="relative w-36 h-9 flex-shrink-0 -ml-1">
               <Image 
                 src="/logo-ca8d5c4c.svg" 
                 alt="GoCanopy Logo" 
                 fill
                 className="object-contain object-left" 
               />
            </h1>
            <span className="text-[10px] font-semibold text-blue-100 tracking-[0.15em] uppercase pl-0.5 opacity-90">AI Deal Associate</span>
          </div>
        </div>
        <div className="p-4">
          <button
            onClick={startNewChat}
            className="flex items-center w-full gap-2 px-4 py-2 text-white transition-colors bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            <PlusCircle className="w-4 h-4" />
            New Chat
          </button>
        </div>
        <div className="flex-1 p-4 overflow-y-auto">
          <div className="mb-2 text-xs font-semibold tracking-wider text-gray-500 uppercase">
            History
          </div>
          {/* Placeholder for history items */}
          <div className="text-sm italic text-gray-400">
            No previous chats
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="relative flex-1 bg-white">
        <div className="h-full p-4 pb-40 overflow-y-auto md:p-8 md:pb-40 bg-white">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.length === 0 ? (
              <div className="mt-20 text-center text-gray-500">
                <Bot className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <h2 className="mb-2 text-2xl font-bold text-gray-900">
                  How can I help you today?
                </h2>
                <p>
                  I can help you analyze deals, parse documents, and run scenarios.
                </p>
              </div>
            ) : (
              groupMessages(messages).map((item) => {
                // Handle System Log Groups
                if ('messages' in item) {
                    return <SystemLogGroup key={item.id} items={item.messages} />;
                }

                // Handle Normal Messages
                const msg = item as Message;

                return (
                  <div
                    key={msg.id}
                    className={`flex gap-4 ${
                      msg.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {msg.role === "assistant" && (
                      <div className="flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-full border border-[#1a3c54] bg-[#1a3c54]">
                        <Bot className="w-5 h-5 text-white" />
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] rounded-2xl px-6 py-4 ${
                        msg.role === "user"
                          ? "bg-gray-100 text-gray-900"
                          : "bg-white text-gray-900 border border-gray-200 shadow-sm"
                      }`}
                    >
                      <div className={`prose max-w-none ${msg.role === "user" ? "" : ""}`}>
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm, remarkMath]}
                            rehypePlugins={[rehypeKatex]}
                            components={{
                                a: ({ node, ...props }: any) => (
                                    <a 
                                        {...props} 
                                        className="text-blue-600 underline hover:text-blue-800" 
                                    />
                                ),
                                table: ({ node, ...props }: any) => (
                                  <div className="overflow-x-auto my-0">
                                    <table {...props} className="min-w-full divide-y divide-gray-200" />
                                  </div>
                                ),
                                thead: ({ node, ...props }: any) => (
                                  <thead {...props} className="bg-gray-50" />
                                ),
                                th: ({ node, ...props }: any) => (
                                  <th {...props} className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500" />
                                ),
                                tbody: ({ node, ...props }: any) => (
                                  <tbody {...props} className="bg-white divide-y divide-gray-200" />
                                ),
                                tr: ({ node, ...props }: any) => (
                                  <tr {...props} className="hover:bg-gray-50" />
                                ),
                                td: ({ node, ...props }: any) => (
                                  <td {...props} className="px-4 py-3 text-sm whitespace-nowrap text-gray-700" />
                                ),
                                pre: ({ node, ...props }: any) => (
                                    <div className="w-full my-4 overflow-hidden rounded-lg bg-gray-50 border border-gray-200">
                                        <div className="flex items-center justify-between px-4 py-2 bg-gray-100 border-b border-gray-200">
                                            <div className="flex space-x-2">
                                                <div className="w-3 h-3 bg-red-400 rounded-full" />
                                                <div className="w-3 h-3 bg-yellow-400 rounded-full" />
                                                <div className="w-3 h-3 bg-green-400 rounded-full" />
                                            </div>
                                            <span className="text-xs text-gray-500 font-medium">Code</span>
                                        </div>
                                        <pre {...props} className="p-4 overflow-x-auto font-mono text-sm text-gray-800" />
                                    </div>
                                )
                            }}
                        >
                            {preprocessLaTeX(msg.content)}
                        </ReactMarkdown>
                      </div>
                    </div>
                    {msg.role === "user" && (
                      <div className="flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-full border border-[#9ca3af] bg-[#9ca3af]">
                        <User className="w-5 h-5 text-white" />
                      </div>
                    )}
                  </div>
                );
              })
            )}
            {isLoading && (
              <div className="flex justify-start gap-4">
                 <div className="flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-full border border-[#1a3c54] bg-[#1a3c54]">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                <div className="flex flex-col px-6 py-4 bg-white border border-gray-200 rounded-2xl shadow-sm">
                  <div className="flex items-center">
                    <Loader2 className="w-5 h-5 mr-2 text-[#1a3c54] animate-spin" />
                    <span className="text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 left-0 right-6 p-4 bg-white">
          <div className="relative max-w-3xl mx-auto">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Ask me anything..."
              className="w-full bg-white text-gray-900 rounded-2xl pl-4 pr-12 py-4 focus:outline-none focus:ring-0 focus:shadow-none border border-gray-200 resize-none h-[96px] max-h-48 overflow-y-auto"
              rows={3}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="absolute p-1.5 text-white transition-colors bg-[#1a3c54] border-2 border-[#1a3c54] rounded-full right-3 bottom-5 hover:bg-[#153043] disabled:cursor-not-allowed"
            >
              <ArrowUp className="w-5 h-5 stroke-2" />
            </button>
          </div>
          <div className="mt-2 text-xs text-center text-gray-500">
            GoCanopy – AI-Powered Real Estate platform for investment analysis.
          </div>
        </div>
      </div>
    </div>
  );
}
