"use client";

import { useState, useEffect, useRef } from "react";
import { client } from "@/lib/client";
import { Send, Bot, User, Loader2, PlusCircle } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
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
        },
        {
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
          const lastMessage = chunk.data.messages[chunk.data.messages.length - 1];
          if (lastMessage.type === "ai" || lastMessage.role === "assistant") {
             assistantContent = lastMessage.content;
             setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? { ...msg, content: assistantContent }
                  : msg
              )
            );
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
    <div className="flex h-screen font-sans text-gray-100 bg-gray-900">
      {/* Sidebar */}
      <div className="flex flex-col w-64 bg-gray-800 border-r border-gray-700">
        <div className="p-4 border-b border-gray-700">
          <h1 className="flex items-center gap-2 text-xl font-bold text-white">
            <Bot className="w-6 h-6 text-blue-400" />
            AI Deal Associate
          </h1>
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
      <div className="flex flex-col flex-1">
        <div className="flex-1 p-4 overflow-y-auto md:p-8">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.length === 0 ? (
              <div className="mt-20 text-center text-gray-400">
                <Bot className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                <h2 className="mb-2 text-2xl font-bold text-white">
                  How can I help you today?
                </h2>
                <p>
                  I can help you analyze deals, parse documents, and run scenarios.
                </p>
              </div>
            ) : (
              messages.map((msg) => {
                if (msg.role === "assistant" && !msg.content) return null;
                return (
                  <div
                    key={msg.id}
                    className={`flex gap-4 ${
                      msg.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {msg.role === "assistant" && (
                      <div className="flex items-center justify-center flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full">
                        <Bot className="w-5 h-5 text-white" />
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] rounded-2xl px-6 py-4 ${
                        msg.role === "user"
                          ? "bg-blue-600 text-white"
                          : "bg-gray-800 text-gray-100 border border-gray-700"
                      }`}
                    >
                      <div className="prose prose-invert max-w-none">
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>
                    </div>
                    {msg.role === "user" && (
                      <div className="flex items-center justify-center flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full">
                        <User className="w-5 h-5 text-white" />
                      </div>
                    )}
                  </div>
                );
              })
            )}
            {isLoading && (
              <div className="flex justify-start gap-4">
                 <div className="flex items-center justify-center flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                <div className="flex items-center px-6 py-4 bg-gray-800 border border-gray-700 rounded-2xl">
                  <Loader2 className="w-5 h-5 mr-2 text-blue-400 animate-spin" />
                  <span className="text-gray-400">Thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-700 bg-gray-800/50 backdrop-blur-sm">
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
              placeholder="Type your message..."
              className="w-full bg-gray-900 text-white rounded-xl pl-4 pr-12 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 resize-none h-[52px] max-h-32 overflow-y-auto"
              rows={1}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="absolute p-2 text-white transition-colors bg-blue-600 rounded-lg right-2 top-2 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="mt-2 text-xs text-center text-gray-500">
            AI Deal Associate can make mistakes. Consider checking important information.
          </div>
        </div>
      </div>
    </div>
  );
}
