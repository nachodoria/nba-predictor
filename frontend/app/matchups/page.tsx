"use client";

import { useEffect, useState } from "react";
import { Header } from "../components/Header";

interface Game {
    game_id: string;
    date: string;
    time: string;
    home_team: string;
    home_team_id: number;
    visitor_team: string;
    visitor_team_id: number;
}

export default function MatchupsPage() {
    const [games, setGames] = useState<Game[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchGames = async () => {
            try {
                const response = await fetch("http://localhost:5000/api/upcoming-games");
                const data = await response.json();
                if (data.success) {
                    setGames(data.games);
                }
            } catch (error) {
                console.error("Error fetching games:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchGames();
    }, []);

    return (
        <main className="min-h-screen bg-black text-white">
            <Header />

            <div className="max-w-7xl mx-auto p-6">
                <div className="mb-8">
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
                        Tonight's Matchups
                    </h2>
                    <p className="text-zinc-400 mt-2">
                        Live schedule and predictions for upcoming games
                    </p>
                </div>

                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="h-48 bg-zinc-900/50 rounded-xl animate-pulse border border-white/5" />
                        ))}
                    </div>
                ) : games.length === 0 ? (
                    <div className="text-center py-20 bg-zinc-900/30 rounded-xl border border-white/5">
                        <p className="text-zinc-400">No games scheduled for today.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {games.map((game) => (
                            <div
                                key={game.game_id}
                                className="bg-zinc-900/50 border border-white/10 rounded-xl p-6 hover:border-neon-blue/50 transition-all duration-300 group"
                            >
                                <div className="flex items-center justify-between mb-6">
                                    {/* Visitor Team */}
                                    <div className="flex flex-col items-center gap-3 flex-1">
                                        <div className="w-20 h-20 relative p-2 bg-white/5 rounded-full group-hover:bg-white/10 transition-colors">
                                            <img
                                                src={`https://cdn.nba.com/logos/nba/${game.visitor_team_id}/global/L/logo.svg`}
                                                alt={game.visitor_team}
                                                className="w-full h-full object-contain"
                                            />
                                        </div>
                                        <span className="text-sm font-medium text-center text-zinc-300">
                                            {game.visitor_team}
                                        </span>
                                    </div>

                                    {/* VS */}
                                    <div className="flex flex-col items-center px-4">
                                        <span className="text-2xl font-bold text-white/20 group-hover:text-neon-blue transition-colors">VS</span>
                                    </div>

                                    {/* Home Team */}
                                    <div className="flex flex-col items-center gap-3 flex-1">
                                        <div className="w-20 h-20 relative p-2 bg-white/5 rounded-full group-hover:bg-white/10 transition-colors">
                                            <img
                                                src={`https://cdn.nba.com/logos/nba/${game.home_team_id}/global/L/logo.svg`}
                                                alt={game.home_team}
                                                className="w-full h-full object-contain"
                                            />
                                        </div>
                                        <span className="text-sm font-medium text-center text-zinc-300">
                                            {game.home_team}
                                        </span>
                                    </div>
                                </div>

                                <div className="pt-4 border-t border-white/5 flex justify-center">
                                    <span className="text-sm font-mono text-neon-blue bg-zinc-900/80 px-4 py-1.5 rounded-full border border-neon-blue/20">
                                        {game.time}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </main>
    );
}
