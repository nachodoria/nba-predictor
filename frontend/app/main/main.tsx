"use client";

import { RotatingQueries } from "../components/RotatingQueries";
import { QueryInput } from "../components/QueryInput";

export default function Home() {
  return (
    <main className="flex min-h-screen w-full items-center justify-center p-4">
      <div className="flex flex-col items-start gap-12 w-full max-w-3xl">

        <RotatingQueries />
        <QueryInput /> 

      </div>
    </main>
  );
}
