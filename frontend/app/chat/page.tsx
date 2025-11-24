"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { Suspense, useState, useEffect, useRef } from "react";
import { QueryInput } from "../components/QueryInput";
import { Spinner } from "@heroui/react";

function ChatContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const initialQuery = searchParams.get("query");
  const initialResponse = searchParams.get("response");

  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (initialQuery && initialResponse) {
      setMessages([
        { role: "user", content: initialQuery },
        { role: "assistant", content: initialResponse }
      ]);
    }
  }, [initialQuery, initialResponse]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    // Add user message
    setMessages(prev => [...prev, { role: "user", content: message }]);
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: message })
      });

      const data = await res.json();

      if (data.success) {
        // Add assistant response
        setMessages(prev => [...prev, {
          role: "assistant",
          content: data.response
        }]);
      } else {
        setMessages(prev => [...prev, {
          role: "assistant",
          content: "❌ Sorry, I encountered an error: " + data.error
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "❌ Failed to connect to the prediction service. Make sure the backend is running on port 5000."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-900 text-white flex flex-col bg-zinc-900 ">
      {/* Header */}
      <div className="border-b border-zinc-800 p-4 bg-zinc-900">
        <div className="max-w-4xl mx-auto flex items-center">
          <button
            onClick={() => router.push('/')}
            className="text-zinc-400 hover:text-white mr-4 transition"
          >
            ← Back
          </button>
          <div>
            <h1 className="text-xl font-bold">NBA Prediction Chat</h1>
            <p className="text-xs text-zinc-500">Powered by Gemini AI</p>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-zinc-500 mt-20">
              <p className="text-lg mb-2">👋 Start a conversation</p>
              <p className="text-sm">Ask me about NBA predictions, team stats, or matchups!</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}
              >
                <div
                  className={`rounded-2xl p-4 max-w-[85%] md:max-w-2xl ${msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-zinc-900 border border-zinc-800 text-white'
                    }`}
                >
                  <p className="text-xs opacity-70 mb-2 font-semibold">
                    {msg.role === 'user' ? '👤 You' : '🤖 AI Assistant'}
                  </p>
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex justify-start animate-in fade-in">
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-4">
                <div className="flex items-center gap-2">
                  <Spinner size="sm" color="primary" />
                  <p className="text-sm text-zinc-400">AI is thinking...</p>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Box at Bottom */}
      <div className="border-t border-zinc-800 p-4 bg-[#26282a]/10  ">
        <div className="max-w-4xl mx-auto">
          <QueryInput onSend={handleSendMessage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <Spinner size="lg" color="primary" />
      </div>
    }>
      <ChatContent />
    </Suspense>
  );
}