"use client";

import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { QueryInput } from "../components/QueryInput";
import { ChatMessage } from "../components/ChatMessage";

interface Message {
  id: string;
  text: string;
  isUser: boolean;
}

export default function ChatPage() {
  const params = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    const initialMsg = params.get("msg");
    if (initialMsg) {
      const userMsg: Message = {
        id: Date.now().toString(),
        text: initialMsg,
        isUser: true,
      };
      setMessages([userMsg]);
      setIsTyping(true);

      // Simulate AI response
      setTimeout(() => {
        const aiMsg: Message = {
          id: (Date.now() + 1).toString(),
          text: "Let's analyze the stats for tonight and predict the performance of the team...",
          isUser: false,
        };
        setMessages((prev) => [...prev, aiMsg]);
        setIsTyping(false);
      }, 1500);
    }
  }, [params]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSendMessage = (text: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      text,
      isUser: true,
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    setTimeout(() => {
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm analyzing the latest data for you. This might take a moment...",
        isUser: false,
      };
      setMessages((prev) => [...prev, aiMsg]);
      setIsTyping(false);
    }, 2000);
  };

  return (
    <main className="flex flex-col h-screen bg-[#0A0A0A] text-white overflow-hidden">

      {/* SCROLLABLE CHAT AREA */}
      <div className="flex-grow overflow-y-auto p-4 md:p-8 scrollbar-hide">
        <div className="max-w-3xl mx-auto flex flex-col pt-4">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg.text} isUser={msg.isUser} />
          ))}

          {isTyping && (
            <ChatMessage
              message="AI is thinking..."
              isUser={false}
            />
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* FIXED INPUT BAR AT BOTTOM */}
      <div className="w-full pb-8 pt-4 px-4 bg-gradient-to-t from-[#0A0A0A] via-[#0A0A0A] to-transparent">
        <div className="max-w-3xl mx-auto">
          <QueryInput onSend={handleSendMessage} isLoading={isTyping} />
        </div>
      </div>
    </main>
  );
}
