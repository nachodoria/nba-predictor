import { QueryInput } from "./components/QueryInput";
import { RotatingQueries } from "./components/RotatingQueries";

export default function Home() {
  return (
    <main className="min-h-screen bg-black flex flex-col items-center justify-center p-8">
      <div className="w-full max-w-3xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            NBA Prediction AI
          </h1>
          <p className="text-zinc-400 text-lg mb-2">
            Powered by Gemini AI & Machine Learning
          </p>
          <p className="text-zinc-500 text-sm">
            Ask about game predictions, team stats, or matchup analysis
          </p>
        </div>
        
        {/* Rotating Queries */}
        <RotatingQueries />
        
        {/* Input Box */}
        <div className="mt-8">
          <QueryInput />
        </div>

        {/* Features */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
            <div className="text-2xl mb-2">🤖</div>
            <h3 className="font-semibold text-white mb-1">AI-Powered</h3>
            <p className="text-xs text-zinc-500">Gemini AI generates intelligent responses</p>
          </div>
          <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
            <div className="text-2xl mb-2">📊</div>
            <h3 className="font-semibold text-white mb-1">ML Predictions</h3>
            <p className="text-xs text-zinc-500">Random Forest model trained on NBA data</p>
          </div>
          <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
            <div className="text-2xl mb-2">🏀</div>
            <h3 className="font-semibold text-white mb-1">Real NBA Data</h3>
            <p className="text-xs text-zinc-500">Live statistics from official NBA API</p>
          </div>
        </div>
      </div>
    </main>
  );
}