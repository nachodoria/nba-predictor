export const Header = () => {
    return (
        <header className="w-full py-4 px-6 border-b border-white/5 bg-[#0A0A0A]/80 backdrop-blur-md sticky top-0 z-50">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="w-1 h-6 bg-gradient-to-b from-neon-blue to-neon-purple rounded-full" />
                    <h1 className="text-lg font-semibold tracking-tight text-white">
                        NBA <span className="font-light text-white/60">Predictor</span>
                    </h1>
                </div>
                {/* Placeholder for future nav or user profile */}
                <div className="w-8 h-8 rounded-full bg-white/5" />
            </div>
        </header>
    );
};
