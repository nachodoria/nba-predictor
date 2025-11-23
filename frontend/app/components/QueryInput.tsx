"use client";

import { useRef, useState, useEffect } from "react";
import { Textarea, Button } from "@heroui/react";
import { ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";

interface QueryInputProps {
  onSend?: (message: string) => void;
  isLoading?: boolean;
}

export const QueryInput = ({ onSend, isLoading }: QueryInputProps) => {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const [focused, setFocused] = useState(false);
  const [value, setValue] = useState("");
  const [baseHeight, setBaseHeight] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSend = async () => {
    if (!value.trim() || loading) return;

    const message = value.trim();
    setValue(""); // Clear input immediately
    
    if (onSend) {
      // If onSend prop provided, use it (for chat page)
      onSend(message);
    } else {
      // Otherwise navigate to chat page (for home page)
      setLoading(true);
      try {
        const response = await fetch('http://localhost:5000/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: message })
        });
        
        const data = await response.json();
        
        if (data.success) {
          router.push(`/chat?query=${encodeURIComponent(message)}&response=${encodeURIComponent(data.response)}`);
        } else {
          alert('Error: ' + data.error);
        }
      } catch (error) {
        alert('Failed to connect to the prediction service. Make sure the backend is running on port 5000.');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    
    if (baseHeight === null) {
      setBaseHeight(el.scrollHeight);
    }
    
    if (value === "") {
      el.style.height = `${baseHeight}px`;
    }
    
    if (el.scrollHeight > (baseHeight || 0)) {
      el.style.height = `${el.scrollHeight}px`;
    } else {
      el.style.height = `${baseHeight}px`;
    }
  }, [value, baseHeight]);

  return (
    <div
      className={`
        flex items-start w-full rounded-xl p-5 
        border border-zinc-800 transition-colors
        hover:border-zinc-700
        ${focused ? "border-zinc-600" : ""}
      `}
      onClick={() => textareaRef.current?.focus()}
    >
      <Textarea
        ref={textareaRef}
        value={value}
        onValueChange={setValue}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        onKeyDown={handleKeyDown}
        disabled={loading || isLoading}
        minRows={1}
        maxRows={6}
        placeholder="Ask about NBA predictions..."
        className="w-full text-white resize-none"
        classNames={{
          inputWrapper: "bg-transparent shadow-none outline-none ring-0 border-none p-0",
          input: "text-white placeholder:text-zinc-400 bg-transparent outline-none",
          innerWrapper: "bg-transparent",
        }}
      />

      <Button
        isIconOnly
        radius="full"
        isLoading={loading || isLoading}
        disabled={!value.trim() || loading || isLoading}
        onPress={handleSend}
        className="bg-transparent text-white transition ml-3 mt-1 hover:bg-zinc-800 hover:scale-110 disabled:opacity-50"
      >
        <ArrowRight size={22} />
      </Button>
    </div>
  );
};