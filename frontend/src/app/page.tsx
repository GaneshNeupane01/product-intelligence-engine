"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Cpu, Zap } from "lucide-react";

import SearchBar from "@/components/SearchBar";
import PipelineVisualizer from "@/components/PipelineVisualizer";
import ResultsPanel from "@/components/ResultsPanel";
import { searchProducts } from "@/lib/api";
import type { SearchQuery, PipelineStep } from "@/types/search";

export default function HomePage() {
  const [pipelineStep, setPipelineStep] = useState<PipelineStep>("idle");
  const [searchData, setSearchData] = useState<SearchQuery | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (query: string, numSites: number, persona: string) => {
    setError(null);
    setSearchData(null);
    setPipelineStep("submitting");

    // Simulate quick pipeline steps for UX
    setTimeout(() => setPipelineStep("searching"), 300);

    try {
      const data = await searchProducts({ query, num_sites: numSites, persona });

      if (data.status === "failed") {
        setPipelineStep("failed");
        setError(data.error_message || "Search failed");
        return;
      }

      // Animate through crawling → parsing → normalizing → comparing → recommending → completed
      setPipelineStep("crawling");
      await new Promise((r) => setTimeout(r, 400));
      setPipelineStep("parsing");
      await new Promise((r) => setTimeout(r, 400));
      setPipelineStep("normalizing");
      await new Promise((r) => setTimeout(r, 400));
      setPipelineStep("comparing");
      await new Promise((r) => setTimeout(r, 400));
      setPipelineStep("recommending");
      await new Promise((r) => setTimeout(r, 400));
      setPipelineStep("completed");

      setSearchData(data);
    } catch (err) {
      setPipelineStep("failed");
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="app-logo">
          <div className="app-logo-icon">
            <Cpu size={18} />
          </div>
          <span className="app-logo-text">Product Intelligence</span>
        </div>
        <div className="app-badge">
          <Zap size={12} style={{ display: "inline", marginRight: 4 }} />
          Phase 5 — Full AI Pipeline
        </div>
      </header>

      {/* Main content */}
      <main className="app-main">
        {/* Hero */}
        <section className="hero-section">
          <motion.h1
            className="hero-title"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            Search. Extract. Compare.
          </motion.h1>
          <motion.p
            className="hero-subtitle"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
          >
            Enter any product name and we&apos;ll crawl the web in real-time,
            extracting structured data from top websites.
          </motion.p>

          {/* Search Bar */}
          <SearchBar
            onSearch={handleSearch}
            isLoading={
              pipelineStep !== "idle" &&
              pipelineStep !== "completed" &&
              pipelineStep !== "failed"
            }
          />
        </section>

        {/* Pipeline Visualization */}
        <AnimatePresence>
          {pipelineStep !== "idle" && (
            <PipelineVisualizer currentStep={pipelineStep} />
          )}
        </AnimatePresence>

        {/* Error */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              style={{
                maxWidth: 600,
                margin: "16px auto",
                padding: "14px 20px",
                borderRadius: "var(--radius-md)",
                background: "rgba(239, 68, 68, 0.1)",
                border: "1px solid rgba(239, 68, 68, 0.3)",
                color: "var(--error)",
                fontSize: 14,
                textAlign: "center",
              }}
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results */}
        <AnimatePresence>
          {searchData && searchData.status === "completed" && (
            <ResultsPanel searchData={searchData} />
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
