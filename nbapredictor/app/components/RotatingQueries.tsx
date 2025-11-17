"use client";

import { useState, useEffect } from "react";

// ----------------------------
// Types
// ----------------------------
export type TeamName = "Warriors" | "Lakers" | "Suns" | "Bucks" | "Mavs";

type Prompt = {
  player: string;
  team: TeamName;
};

const prompts: Prompt[] = [
  { player: "Steph", team: "Warriors" },
  { player: "LeBron", team: "Lakers" },
  { player: "Kevin", team: "Suns" },
  { player: "Giannis", team: "Bucks" },
  { player: "Luka", team: "Mavs" },
];

// Team colors
const teamColors: Record<TeamName, { primary: string; secondary: string }> = {
  Warriors: { primary: "#1D428A", secondary: "#FFC72C" },
  Lakers: { primary: "#552583", secondary: "#FDB927" },
  Suns: { primary: "#1D1160", secondary: "#E56020" },
  Bucks: { primary: "#00471B", secondary: "#EEE1C6" },
  Mavs: { primary: "#00538C", secondary: "#B8C4CA" },
};

export const RotatingQueries = () => {
  const [index, setIndex] = useState(0);
  const [playerText, setPlayerText] = useState("");
  const [teamText, setTeamText] = useState("");
  const [phase, setPhase] = useState<"typing" | "waiting" | "deleting">(
    "typing"
  );

  // Smooth pacing
  const typingSpeed = 120;
  const deletingSpeed = 90;
  const pauseTime = 1400;

  const current = prompts[index];
  const colors = teamColors[current.team];

  useEffect(() => {
    const playerDone = playerText.length === current.player.length;
    const teamDone = teamText.length === current.team.length;

    if (phase === "typing") {
      if (!playerDone || !teamDone) {
        const t = setTimeout(() => {
          if (!playerDone)
            setPlayerText(current.player.slice(0, playerText.length + 1));
          if (!teamDone)
            setTeamText(current.team.slice(0, teamText.length + 1));
        }, typingSpeed);
        return () => clearTimeout(t);
      }
      setTimeout(() => setPhase("waiting"), pauseTime);
    }

    if (phase === "waiting") {
      const t = setTimeout(() => setPhase("deleting"), pauseTime);
      return () => clearTimeout(t);
    }

    if (phase === "deleting") {
      const emptyPlayer = playerText.length === 0;
      const emptyTeam = teamText.length === 0;

      if (!emptyPlayer || !emptyTeam) {
        const t = setTimeout(() => {
          if (!emptyPlayer)
            setPlayerText(playerText.slice(0, playerText.length - 1));
          if (!emptyTeam)
            setTeamText(teamText.slice(0, teamText.length - 1));
        }, deletingSpeed);
        return () => clearTimeout(t);
      }

      // Move to next rotation
      setIndex((prev) => (prev + 1) % prompts.length);
      setPhase("typing");
    }
  }, [playerText, teamText, phase, index, current]);

  return (
    <>
      {/* Cursor animation */}
      <style>{`
        @keyframes blink {
          0% { opacity: 1; }
          50% { opacity: 0; }
          100% { opacity: 1; }
        }
        .cursor {
          display: inline-block;
          width: 0.6ch;
          animation: blink 1s infinite;
        }
      `}</style>

      <h1 className="text-xl md:text-5xl lg:text-4xl font-semibold leading-tight text-white max-w-150">
        How will{" "}
        <span style={{ color: colors.primary }}>
          {playerText}
          <span className="cursor">|</span>
        </span>{" "}
        and the{" "}
        <span style={{ color: colors.secondary }}>
          {teamText}
          <span className="cursor">|</span>
        </span>{" "}
        do tonight?
      </h1>
    </>
  );
};
