"use client";

import { motion } from "framer-motion";
import type { SearchQuery } from "@/types/search";
import SiteCard from "./SiteCard";
import { Clock, Globe, Layers } from "lucide-react";

interface ResultsPanelProps {
    searchData: SearchQuery;
}

export default function ResultsPanel({ searchData }: ResultsPanelProps) {
    const totalChars = searchData.results.reduce(
        (sum, r) => sum + (r.raw_markdown?.content_length || 0),
        0
    );

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="results-panel"
        >
            {/* Summary Bar */}
            <div className="results-summary">
                <h2 className="results-title">
                    Results for{" "}
                    <span className="results-query">&ldquo;{searchData.query}&rdquo;</span>
                </h2>
                <div className="results-stats">
                    <div className="stat-badge">
                        <Globe size={14} />
                        <span>{searchData.results.length} sites</span>
                    </div>
                    <div className="stat-badge">
                        <Layers size={14} />
                        <span>{(totalChars / 1024).toFixed(1)} KB extracted</span>
                    </div>
                    {searchData.completed_at && (
                        <div className="stat-badge">
                            <Clock size={14} />
                            <span>
                                {new Date(searchData.completed_at).toLocaleTimeString()}
                            </span>
                        </div>
                    )}
                </div>
            </div>

            {/* Site Cards */}
            <div className="results-grid">
                {searchData.results.map((result, idx) => (
                    <SiteCard key={result.id} result={result} index={idx} />
                ))}
            </div>

            {searchData.results.length === 0 && (
                <div className="results-empty">
                    <p>No results found. Try a different search query.</p>
                </div>
            )}
        </motion.div>
    );
}
