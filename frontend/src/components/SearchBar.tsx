"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Globe, Minus, Plus } from "lucide-react";

interface SearchBarProps {
    onSearch: (query: string, numSites: number) => void;
    isLoading: boolean;
}

export default function SearchBar({ onSearch, isLoading }: SearchBarProps) {
    const [query, setQuery] = useState("");
    const [numSites, setNumSites] = useState(5);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (query.trim() && !isLoading) {
            onSearch(query.trim(), numSites);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-3xl mx-auto"
        >
            <form onSubmit={handleSubmit} className="space-y-4">
                {/* Search Input */}
                <div className="search-input-wrapper">
                    <div className="search-icon">
                        <Search size={20} />
                    </div>
                    <input
                        id="search-input"
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search for any product... e.g. RTX 5070, iPhone 16 Pro"
                        className="search-input"
                        disabled={isLoading}
                        autoFocus
                    />
                    <button
                        id="search-button"
                        type="submit"
                        disabled={isLoading || !query.trim()}
                        className="search-button"
                    >
                        {isLoading ? (
                            <div className="spinner" />
                        ) : (
                            <>
                                <Search size={16} />
                                <span>Search</span>
                            </>
                        )}
                    </button>
                </div>

                {/* Number of Sites Selector */}
                <div className="sites-selector">
                    <Globe size={16} className="sites-icon" />
                    <span className="sites-label">Websites to scan:</span>
                    <div className="sites-counter">
                        <button
                            type="button"
                            onClick={() => setNumSites(Math.max(1, numSites - 1))}
                            disabled={numSites <= 1 || isLoading}
                            className="counter-btn"
                            id="decrease-sites"
                        >
                            <Minus size={14} />
                        </button>
                        <span className="counter-value" id="num-sites-value">
                            {numSites}
                        </span>
                        <button
                            type="button"
                            onClick={() => setNumSites(Math.min(10, numSites + 1))}
                            disabled={numSites >= 10 || isLoading}
                            className="counter-btn"
                            id="increase-sites"
                        >
                            <Plus size={14} />
                        </button>
                    </div>
                </div>
            </form>
        </motion.div>
    );
}
