"use client";

import { Button, Input } from "@heroui/react";
import { ArrowRight } from "lucide-react";
import Main from "./main/main";

export default function Home() {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-[#141315] gap-4">
      <Main />
    </div>
  );
}
