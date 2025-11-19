"use client";

import { useRef, useState, useEffect } from "react";
import { Textarea, Button } from "@heroui/react";
import { ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";

export const QueryInput = () => {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const [focused, setFocused] = useState(false);
  const [value, setValue] = useState("");

  const router = useRouter();

  const sendMessage = () => {
    if (!value.trim()) return;
    router.push(`/chat?msg=${encodeURIComponent(value.trim())}`);
  };

  // Auto-expand height
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;

    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px"; 
  }, [value]);

  return (
    <>


      <div
        className={`
          flex items-start w-full rounded-3xl p-5 bg-zinc-800
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
              sendMessage();
            }
          }}
          minRows={1}
          placeholder="Start typing..."
          className="w-full text-white bg-transparent resize-none"
          classNames={{
            inputWrapper: "bg-transparent shadow-none outline-none ring-0 border-none p-0",
            input: "text-white placeholder:text-zinc-400 bg-transparent outline-none",
            innerWrapper: "bg-transparent",
          }}
        />

        <Button
          isIconOnly
          radius="full"
          className="bg-transparent text-white hover:brightness-125 transition ml-3 mt-1"
          onPress={sendMessage}
        >
          <ArrowRight size={22} />
        </Button>
      </div>
    </>
  );
};
