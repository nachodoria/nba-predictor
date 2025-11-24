"use client";

import React from "react";

export const LoadingScreen = () => {
    return (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-zinc-900 backdrop-blur-sm">
            <div className="relative flex flex-col items-center">
                {/* Outer rotating ring */}
                <div className="w-24 h-24 rounded-full border-4 border-zinc-800 border-t-[var(--neon-blue)] animate-spin mb-8"></div>

                <h2 className="text-2xl font-bold text-white mb-2 animate-pulse">
                    Analyzing Your Request...
                </h2>
                <p className="text-zinc-400 text-sm">
                    Consulting with the agent! Please wait...
                </p>
            </div>
        </div>
    );
};
