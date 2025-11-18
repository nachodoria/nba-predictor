"use client";

import { useRef, useState, useEffect } from "react";
import { Textarea, Button } from "@heroui/react";
import { ArrowRight } from "lucide-react";

export const QueryInput = () => {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const [focused, setFocused] = useState(false);
  const [value, setValue] = useState("");

  // Auto-resize effect
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;

    el.style.height = "auto"; // reset
    el.style.height = Math.min(el.scrollHeight, 160) + "px"; 
    // 160px ≈ 2.2x height — optimal
  }, [value]);

  return (
    <>
      <style>{`
        .focus-anim {
          transition: border-color 0.25s ease, box-shadow 0.25s ease;
        }
        .focus-anim-focused {
          border-color: var(--color-zinc-500) !important;
        }
      `}</style>

      <div
        className={`
          flex items-start w-full rounded-xl p-5 
          border border-zinc-800 focus-anim
          hover:border-zinc-700
          ${focused ? "focus-anim-focused" : ""}
        `}
        onClick={() => textareaRef.current?.focus()}
      >
        {/* TEXTAREA THAT LOOKS LIKE AN INPUT */}
        <Textarea
          ref={textareaRef}
          value={value}
          onValueChange={setValue}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          minRows={1}
          maxRows={6}
          placeholder="Start typing..."
          className="w-full text-white resize-none"
          classNames={{
            inputWrapper: "bg-transparent shadow-none outline-none ring-0 border-none p-0",
            input: "text-white placeholder:text-zinc-400 bg-transparent outline-none",
            innerWrapper: "bg-transparent",
          }}
        />

        {/* SEND BUTTON */}
        <Button
          isIconOnly
          radius="full"
          className="bg-transparent text-white transition ml-3 mt-1 hover:bg-zinc-800 hover:scale-110"
        >
          <ArrowRight size={22} />
        </Button>
      </div>
    </>
  );
};
