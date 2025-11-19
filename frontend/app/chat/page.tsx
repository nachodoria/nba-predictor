"use client";

import { useSearchParams } from "next/navigation";
import { QueryInput } from "../components/QueryInput";

export default function ChatPage() {
  const params = useSearchParams();
  const userMessage = params.get("msg");

  return (
    <main className="flex flex-col min-h-screen bg-[#131313]">

      {/* SCROLLABLE CHAT AREA */}
      <div className="flex-grow overflow-y-auto p-6">
        <div className="w-[60vw] mx-auto flex flex-col">

          {/* User bubble */}
          {userMessage && (
            <div className="self-end bg-zinc-700 text-white px-4 py-3 rounded-lg max-w-md mb-8">
              {userMessage}
            </div>
          )}

          {/* Placeholder AI response */}
          <div className="text-white max-w-xl mb-4">
            Let's analyze the stats for tonight and predict the performance of the team...
          </div>

          <div className="w-[250px] h-[150px] bg-zinc-300 rounded-lg mb-6" />

          <p className="text-white max-w-xl mb-20 leading-relaxed">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi in magna
            lobortis, vestibulum ligula vel, pretium mi. Donec venenatis vel lorem
            eu cursus. Donec aliquam enim sagittis pretium semper.
          </p>

        </div>
      </div>

      {/* FIXED INPUT BAR AT BOTTOM */}
      <div className="sticky bottom-0 w-full pb-10 pt-2">
        <div className="w-[60vw] mx-auto">
          <QueryInput />
        </div>
      </div>

    </main>
  );
}
