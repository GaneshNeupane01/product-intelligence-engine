"use client";

import { motion } from "framer-motion";
import { Clock, CheckCircle2, ChevronRight, Activity } from "lucide-react";
import type { SearchQuery } from "@/types/search";

interface SearchTimelineProps {
    searchData: SearchQuery;
}

export default function SearchTimeline({ searchData }: SearchTimelineProps) {
    // Extract timestamps
    const started = new Date(searchData.created_at);

    // We can assume the process finishes around completed_at
    const completed = searchData.completed_at ? new Date(searchData.completed_at) : null;

    // Extract intermediate timestamps where available
    const parsedAt = searchData.results[0]?.parsed_product?.parsed_at
        ? new Date(searchData.results[0].parsed_product.parsed_at)
        : null;

    const comparedAt = searchData.comparison?.compared_at
        ? new Date(searchData.comparison.compared_at)
        : null;

    const recommendedAt = searchData.recommendation?.recommended_at
        ? new Date(searchData.recommendation.recommended_at)
        : null;

    const timelineEvents = [
        { label: "Search Received", time: started, active: true },
        { label: "Crawling & Extraction", time: parsedAt, active: !!parsedAt },
        { label: "Normalization & Comparison", time: comparedAt, active: !!comparedAt },
        { label: "AI Insights Generated", time: recommendedAt, active: !!recommendedAt },
        { label: "Pipeline Complete", time: completed, active: !!completed },
    ];

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-[#111118] border border-[#2a2a3a] rounded-xl p-6 shadow-[0_4px_20px_rgba(0,0,0,0.2)] h-full"
        >
            <div className="flex items-center gap-2 mb-6 text-[var(--text-primary)] border-b border-[#2a2a3a] pb-3">
                <Activity size={18} className="text-[#a78bfa]" />
                <h3 className="font-bold text-sm tracking-widest uppercase">Execution Timeline</h3>
            </div>

            <div className="relative border-l border-[#2a2a3a]/70 ml-3 space-y-6">
                {timelineEvents.map((event, idx) => (
                    <div key={idx} className="relative pl-6">
                        <div
                            className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full border-2 border-[#111118] transition-colors ${event.active ? "bg-[#22c55e]" : "bg-[#2a2a3a]"
                                }`}
                        />
                        <div className="flex flex-col">
                            <span className={`text-sm font-semibold mb-1 ${event.active ? "text-[var(--text-primary)]" : "text-[var(--text-muted)]"
                                }`}>
                                {event.label}
                            </span>
                            {event.time ? (
                                <span className="text-xs text-[var(--text-secondary)] flex items-center gap-1 font-mono">
                                    <Clock size={12} />
                                    {event.time.toLocaleTimeString(undefined, {
                                        hour: '2-digit',
                                        minute: '2-digit',
                                        second: '2-digit',
                                        fractionalSecondDigits: 1
                                    })}
                                </span>
                            ) : (
                                <span className="text-xs text-[var(--text-muted)]">Pending...</span>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {completed && (
                <div className="mt-8 pt-4 border-t border-[#2a2a3a] flex items-center justify-between text-xs text-[var(--text-secondary)]">
                    <span>Total Latency</span>
                    <span className="font-mono text-[#a78bfa]">
                        {((completed.getTime() - started.getTime()) / 1000).toFixed(2)}s
                    </span>
                </div>
            )}
        </motion.div>
    );
}
