"use client";

import { useState } from "react";
import { ChatBubble } from "../components/chat/ChatBubble";
import { ChatInput } from "../components/chat/ChatInput";
import { CompsTable } from "../components/deal/CompsTable";
import { ModelView } from "../components/deal/ModelView";

export default function Home() {
  const [messages, setMessages] = useState<{ message: string; isUser: boolean }[]>([]);

  const handleSend = (msg: string) => {
    setMessages((prev) => [...prev, { message: msg, isUser: true }]);
    // Simulate AI response
    setTimeout(() => {
      setMessages((prev) => [...prev, { message: "I am processing your request...", isUser: false }]);
    }, 1000);
  };

  return (
    <main className="flex min-h-screen flex-col p-4 gap-4">
      <h1 className="text-2xl font-bold">AI Deal Associate</h1>
      
      <div className="flex flex-1 gap-4">
        <div className="flex-1 flex flex-col border rounded p-4">
          <div className="flex-1 overflow-y-auto mb-4 flex flex-col gap-2">
            {messages.map((m, i) => (
              <ChatBubble key={i} message={m.message} isUser={m.isUser} />
            ))}
          </div>
          <ChatInput onSend={handleSend} />
        </div>
        
        <div className="flex-1 flex flex-col gap-4">
          <CompsTable />
          <ModelView />
        </div>
      </div>
    </main>
  );
}
