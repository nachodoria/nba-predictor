"use client";

import { useEffect } from "react";
import { RotatingQueries } from "../components/RotatingQueries";
import { QueryInput } from "../components/QueryInput";
import { Kbd } from "@heroui/react";

export default function Home() {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const isMac = navigator.platform.toUpperCase().includes("MAC");
      const commandPressed = isMac ? e.metaKey : e.ctrlKey;

      if (commandPressed && e.shiftKey && e.key.toLowerCase() === "g") {
        e.preventDefault();
        window.open(
          "https://github.com/nachodoria/nba-predictor",
          "_blank",
          "noopener,noreferrer"
        );
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  return (
    <main className="relative min-h-screen min-w-full bg-[#0a0a0a] flex flex-col m-0">

      {/* KBD TOP RIGHT */}
      <div className="absolute top-8 right-8">
        <Kbd
          keys={["command", "shift"]}
          className="bg-zinc-800 text-white/90 shadow-lg rounded-xl px-3 py-2 text-sm no-underline"
        >
          G
        </Kbd>

      </div>

      {/* CENTERED CONTENT */}
      <div className="
        flex flex-col 
        items-center justify-center 
        flex-grow-2
        w-full 
        px-4 md:px-0
        text-start
      ">

        {/* ROTATING HEADLINE */}
        <div className="max-w-3xl w-full">
          <RotatingQueries />
        </div>

        {/* INPUT */}
        <div className="w-full max-w-3xl mt-10 ">
          <QueryInput />
        </div>

        {/* SUBTEXT */}
        <p className="text-zinc-500 text-sm mt-6">
          Get AI-powered sports analysis, predictions, and insights
        </p>
      </div>

    </main>
  );
}
