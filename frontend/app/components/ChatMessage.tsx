import { cn } from "@heroui/react";

interface ChatMessageProps {
    message: string;
    isUser: boolean;
}

export const ChatMessage = ({ message, isUser }: ChatMessageProps) => {
    return (
        <div
            className={cn(
                "max-w-2xl px-6 py-4 rounded-2xl mb-6 leading-relaxed text-[15px] tracking-wide shadow-sm",
                isUser
                    ? "self-end bg-gradient-to-br from-zinc-800 to-zinc-900 text-white border border-white/10 rounded-tr-sm"
                    : "self-start glass-panel text-zinc-100 rounded-tl-sm"
            )}
        >
            {message}
        </div>
    );
};
