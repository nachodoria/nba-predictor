"use client";

import { useEffect, useRef, useState } from "react";
import { Textarea, Button } from "@heroui/react";
import { ArrowRight, Zap } from "lucide-react";
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
  const router = useRouter();

  const handleSend = () => {
    if (!value.trim()) return;

    if (onSend) {
      onSend(value.trim());
      setValue("");
    } else {
      router.push(`/chat?msg=${encodeURIComponent(value.trim())}`);
    }
  };
  // Make the Textarea grow depending on text size
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    if (baseHeight === null) {
      const initial = el.scrollHeight;
      setBaseHeight(initial);
      el.style.height = initial + "px";
      return;
    }
    if (value === "") {
      el.style.height = baseHeight + "px";
      return;
    }
    if (el.scrollHeight > baseHeight) {
      el.style.height = Math.min(el.scrollHeight, 160) + "px";
    } else {
      el.style.height = baseHeight + "px";
    }
  }, [value, baseHeight]);


  return (
    <div
      className={`
        flex items-center w-full rounded-[24px] p-2 pl-4 bg-zinc-900/80 border border-white/10 backdrop-blur-sm transition-all duration-300
        ${focused ? "border-neon-blue/50 shadow-[0_0_15px_rgba(0,240,255,0.1)]" : "hover:border-white/20"}
      `}
      onClick={() => textareaRef.current?.focus()}
    >
      <Textarea
        ref={textareaRef}
        value={value}
        onValueChange={setValue}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
          }
        }}
        minRows={1}
        placeholder="Ask a prediction... (e.g., 'Who wins Lakers vs Celtics tonight?')"
        className="w-full text-white bg-transparent resize-none overflow-hidden"
        classNames={{
          inputWrapper:
            "bg-transparent shadow-none outline-none border-none p-0 h-auto min-h-0 flex items-center",
          innerWrapper: "bg-transparent h-auto flex items-center",
          input:
            "text-white placeholder:text-zinc-500 bg-transparent outline-none p-0 m-0 leading-[2.4] h-auto",
        }}

      />


      <Button
        isIconOnly
        radius="full"
        className={`
          min-w-10 w-10 h-10 ml-2 transition-all duration-300 flex items-center
          ${value.trim()
            ? "bg-gradient-to-r from-neon-blue to-neon-purple text-white shadow-lg shadow-neon-blue/20"
            : "bg-zinc-800 text-zinc-500"}
        `}
        onPress={handleSend}
        disabled={!value.trim() || isLoading}
      >
        <ArrowRight size={20} />
      </Button>
    </div>
  );
};
