"use client";

import { useState, useEffect, useRef } from "react";
import { client } from "@/lib/client";
import { Send, User, Bot, Loader2, AlertCircle, Sparkles, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState("");
  const [status, setStatus] = useState<string>("idle");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, status]);

  // Initialize thread
  useEffect(() => {
    const init = async () => {
      try {
        // Let the server generate the thread ID (UUID)
        const thread = await client.threads.create();
        setThreadId(thread.thread_id);
        console.log("Thread created:", thread.thread_id);
      } catch (e) {
        console.error("Error creating thread:", e);
      }
    };
    init();
  }, []);

  const sendMessage = async (e?: React.FormEvent, customInput?: string) => {
    e?.preventDefault();
    const textToSend = customInput || input;
    if (!textToSend.trim() || isLoading) return;

    setInput("");
    setIsLoading(true);
    
    // Optimistic update
    const newMessages: Message[] = [...messages, { role: "user", content: textToSend }];
    setMessages(newMessages);

    try {
      // Check current state to decide if we are resuming or starting new
      const currentState = await client.threads.getState(threadId);
      let stream;

      if (currentState.next && currentState.next.length > 0) {
        // Resuming from interrupted state
        console.log("Resuming from interrupted state:", currentState.next);
        
        // 1. Update state with user input
        await client.threads.updateState(threadId, {
          values: {
            messages: [{ role: "user", content: textToSend }],
          },
          asNode: currentState.next[0],
        });
        
        // 2. Resume execution (input: null)
        stream = client.runs.stream(
          threadId,
          "agent", 
          {
            input: null,
            streamMode: "values",
          }
        );
      } else {
        // Normal new run
        stream = client.runs.stream(
          threadId,
          "agent", 
          {
            input: { messages: [{ role: "user", content: textToSend }] },
            streamMode: "values",
          }
        );
      }

      setStatus("running");

      for await (const event of stream) {
        if (event.event === "values") {
          const stateMessages = (event.data as any).messages;
          if (stateMessages && Array.isArray(stateMessages)) {
            const uiMsgs: Message[] = stateMessages.map((m: any) => ({
              role: (m.type === "human" || m.role === "user") ? "user" : "assistant",
              content: typeof m.content === 'string' ? m.content : JSON.stringify(m.content),
            }));
            setMessages(uiMsgs);
          }
        }
      }

      // 2. Check final state AFTER stream finishes
      // Add a small delay to ensure backend state is updated
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const state = await client.threads.getState(threadId);
      console.log("Final state:", state);
      
      // Check if we are interrupted (next steps available)
      if (state.next && state.next.length > 0) {
        setStatus("interrupted");
      } else {
        setStatus("idle");
      }

    } catch (error) {
      console.error("Error:", error);
      setStatus("error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50 font-sans text-slate-900">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto w-full px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-xl shadow-lg shadow-blue-600/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-800 tracking-tight">AI Deal Associate</h1>
              <p className="text-xs text-slate-500 font-medium">Real Estate Investment Committee Agent</p>
            </div>
          </div>
          <div className="hidden md:block text-xs font-mono text-slate-400 bg-slate-100 px-3 py-1 rounded-full">
            {threadId ? `ID: ${threadId.slice(0, 8)}...` : 'Initializing...'}
          </div>
        </div>
      </header>

      {/* Main Chat Area */}
      <main className="flex-1 overflow-y-auto scroll-smooth">
        <div className="max-w-4xl mx-auto w-full p-6 pb-32 space-y-8">
          
          {/* Empty State */}
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <div className="bg-white p-6 rounded-3xl shadow-xl shadow-slate-200/50 ring-1 ring-slate-100">
                <Bot className="w-16 h-16 text-blue-600" strokeWidth={1.5} />
              </div>
              <div className="space-y-2 max-w-md">
                <h2 className="text-2xl font-bold text-slate-800">Ready to underwrite?</h2>
                <p className="text-slate-500 leading-relaxed">
                  I can help you analyze deals, run comps, and build investment memos. 
                  Upload documents or start a conversation.
                </p>
              </div>
              
              <div className="grid gap-3 w-full max-w-sm">
                <button 
                  onClick={() => sendMessage(undefined, "Start underwriting this deal")}
                  className="flex items-center justify-between p-4 bg-white hover:bg-blue-50 border border-slate-200 hover:border-blue-200 rounded-xl transition-all group text-left"
                >
                  <span className="text-sm font-medium text-slate-700 group-hover:text-blue-700">Start underwriting this deal</span>
                  <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-blue-500" />
                </button>
                <button 
                  onClick={() => sendMessage(undefined, "What information do you need?")}
                  className="flex items-center justify-between p-4 bg-white hover:bg-blue-50 border border-slate-200 hover:border-blue-200 rounded-xl transition-all group text-left"
                >
                  <span className="text-sm font-medium text-slate-700 group-hover:text-blue-700">What information do you need?</span>
                  <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-blue-500" />
                </button>
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={cn(
                "flex w-full animate-in fade-in slide-in-from-bottom-2 duration-300",
                msg.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              <div
                className={cn(
                  "flex gap-4 max-w-[85%] md:max-w-[75%]",
                  msg.role === "user" ? "flex-row-reverse" : "flex-row"
                )}
              >
                {/* Avatar */}
                <div
                  className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-sm border",
                    msg.role === "user" 
                      ? "bg-white border-slate-100 text-slate-600" 
                      : "bg-blue-600 border-blue-600 text-white"
                  )}
                >
                  {msg.role === "user" ? <User size={20} /> : <Bot size={20} />}
                </div>

                {/* Message Bubble */}
                <div className="flex flex-col gap-1 min-w-0">
                  <div className={cn("text-xs font-medium ml-1", msg.role === "user" ? "text-right text-slate-400" : "text-slate-400")}>
                    {msg.role === "user" ? "You" : "AI Associate"}
                  </div>
                  <div
                    className={cn(
                      "p-5 rounded-2xl shadow-sm leading-relaxed overflow-hidden",
                      msg.role === "user"
                        ? "bg-slate-800 text-white rounded-tr-none"
                        : "bg-white text-slate-800 border border-slate-100 rounded-tl-none"
                    )}
                  >
                    {msg.role === "user" ? (
                      <div className="whitespace-pre-wrap break-words">{msg.content}</div>
                    ) : (
                      <div className="prose prose-sm max-w-none prose-slate prose-p:leading-relaxed prose-pre:bg-slate-100 prose-pre:text-slate-800">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Status Indicators */}
          {status === "interrupted" && (
            <div className="flex justify-center animate-in fade-in zoom-in duration-300">
              <div className="bg-amber-50 text-amber-800 px-6 py-3 rounded-full text-sm font-medium flex items-center gap-3 border border-amber-200 shadow-sm">
                <AlertCircle size={18} className="text-amber-600" />
                <span>Waiting for your review... Reply &apos;ok&apos; to proceed.</span>
              </div>
            </div>
          )}

          {isLoading && (
            <div className="flex justify-start w-full animate-in fade-in duration-300">
               <div className="flex gap-4 max-w-[75%]">
                  <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center shrink-0 shadow-sm">
                    <Bot size={20} className="text-white" />
                  </div>
                  <div className="bg-white p-5 rounded-2xl rounded-tl-none border border-slate-100 shadow-sm flex items-center gap-3">
                    <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                    <span className="text-slate-500 text-sm font-medium">Thinking...</span>
                  </div>
               </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input Area */}
      <footer className="bg-white/80 backdrop-blur-md border-t border-slate-200 fixed bottom-0 w-full z-10">
        <div className="max-w-4xl mx-auto w-full p-4 md:p-6">
          <form onSubmit={(e) => sendMessage(e)} className="relative flex items-center gap-3 bg-white p-2 rounded-2xl border border-slate-200 shadow-lg shadow-slate-200/50 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-4 py-3 bg-transparent border-none focus:outline-none text-slate-800 placeholder:text-slate-400"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shadow-blue-600/20 hover:shadow-lg hover:shadow-blue-600/30 active:scale-95"
            >
              <Send size={20} />
            </button>
          </form>
          <div className="text-center mt-2">
             <p className="text-[10px] text-slate-400">AI can make mistakes. Please review generated results.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
