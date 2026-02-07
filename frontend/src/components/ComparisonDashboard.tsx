"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { LayoutGrid, ListTree, Code2 } from "lucide-react";
import type { SearchQuery } from "@/types/search";

import RecommendationPanel from "./RecommendationPanel";
import ComparisonPanel from "./ComparisonPanel";
import SpecDiffTable from "./SpecDiffTable";
import SiteCard from "./SiteCard";

interface ComparisonDashboardProps {
    searchData: SearchQuery;
}

type TabType = "overview" | "specs" | "dev";

export default function ComparisonDashboard({ searchData }: ComparisonDashboardProps) {
    const [activeTab, setActiveTab] = useState<TabType>("overview");

    return (
        <div className="w-full max-w-5xl mx-auto mt-8 mb-24">
            {/* Main Tabs */}
            <div className="flex items-center justify-center gap-4 mb-8">
                <button
                    onClick={() => setActiveTab("overview")}
                    className={`flex items-center gap-2 px-6 py-2.5 rounded-full transition-all text-sm font-medium ${activeTab === "overview"
                            ? "bg-[var(--accent-primary)] text-white shadow-[0_0_20px_var(--accent-glow)]"
                            : "bg-[#1a1a24] text-[#a0a0b5] border border-[#2a2a3a] hover:text-white"
                        }`}
                >
                    <LayoutGrid size={16} /> Overview
                </button>
                <button
                    onClick={() => setActiveTab("specs")}
                    className={`flex items-center gap-2 px-6 py-2.5 rounded-full transition-all text-sm font-medium ${activeTab === "specs"
                            ? "bg-[var(--accent-primary)] text-white shadow-[0_0_20px_var(--accent-glow)]"
                            : "bg-[#1a1a24] text-[#a0a0b5] border border-[#2a2a3a] hover:text-white"
                        }`}
                >
                    <ListTree size={16} /> Deep Dive Specs
                </button>
                <button
                    onClick={() => setActiveTab("dev")}
                    className={`flex items-center gap-2 px-6 py-2.5 rounded-full transition-all text-sm font-medium ${activeTab === "dev"
                            ? "bg-[#6b7280] text-white shadow-[0_0_20px_rgba(107,114,128,0.3)]"
                            : "bg-[#1a1a24] text-[#a0a0b5] border border-[#2a2a3a] hover:text-white"
                        }`}
                >
                    <Code2 size={16} /> Developer Mode
                </button>
            </div>

            {/* Tab Content */}
            <AnimatePresence mode="wait">
                {activeTab === "overview" && (
                    <motion.div
                        key="overview"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.3 }}
                    >
                        {searchData.recommendation && (
                            <RecommendationPanel recommendation={searchData.recommendation} />
                        )}
                        {searchData.comparison && (
                            <ComparisonPanel comparison={searchData.comparison} />
                        )}

                        <div className="mt-8 text-center text-[var(--text-muted)] text-sm">
                            Scroll down for individual site details, or use the tabs above.
                        </div>
                    </motion.div>
                )}

                {activeTab === "specs" && (
                    <motion.div
                        key="specs"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.3 }}
                    >
                        <h3 className="text-xl font-bold mb-4 text-[var(--text-primary)]">
                            Normalized Specification Diff
                        </h3>
                        <p className="text-sm text-[var(--text-secondary)] mb-6">
                            Side-by-side spec comparison extracted automatically. Discrepancies between sellers are automatically highlighted.
                        </p>
                        <SpecDiffTable results={searchData.results} />
                    </motion.div>
                )}

                {activeTab === "dev" && (
                    <motion.div
                        key="dev"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.3 }}
                    >
                        <div className="mb-6 p-4 bg-[#111118] border border-[#f59e0b]/30 rounded-lg flex items-center justify-between">
                            <div>
                                <h3 className="text-[#f59e0b] font-bold text-sm tracking-widest uppercase">Developer Mode</h3>
                                <p className="text-[#a0a0b5] text-sm mt-1">
                                    Expand the site cards below to view the Raw Scraped Markdown next to the Parsed Structured JSON.
                                </p>
                            </div>
                        </div>

                        <div className="results-grid">
                            {searchData.results.map((result, idx) => (
                                <SiteCard key={result.id} result={result} index={idx} autoExpand={true} />
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Standard Site Cards (on Overview Tab only) */}
            {activeTab === "overview" && (
                <motion.div
                    className="results-grid mt-12"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                >
                    <h3 className="text-lg font-bold mb-4 text-[var(--text-primary)] px-2 border-b border-[#2a2a3a] pb-2">
                        Top {searchData.results.length} Indexed Sites
                    </h3>
                    {searchData.results.map((result, idx) => (
                        <SiteCard key={result.id} result={result} index={idx} />
                    ))}
                </motion.div>
            )}
        </div>
    );
}
