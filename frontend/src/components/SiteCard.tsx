"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    ExternalLink,
    ChevronDown,
    ChevronUp,
    FileText,
    Hash,
} from "lucide-react";
import type { SearchResult as SearchResultType } from "@/types/search";

interface SiteCardProps {
    result: SearchResultType;
    index: number;
    autoExpand?: boolean;
}

export default function SiteCard({ result, index, autoExpand = false }: SiteCardProps) {
    const [isExpanded, setIsExpanded] = useState(autoExpand);
    const markdown = result.raw_markdown;
    const contentPreview = markdown?.content
        ? markdown.content.slice(0, 300) + (markdown.content.length > 300 ? "…" : "")
        : "No content extracted.";

    const domain = (() => {
        try {
            return new URL(result.url).hostname.replace("www.", "");
        } catch {
            return result.url;
        }
    })();

    return (
        <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: index * 0.08 }}
            className="site-card"
            id={`site-card-${index}`}
        >
            {/* Card Header */}
            <div className="site-card-header">
                <div className="site-card-rank">#{result.position}</div>
                <div className="site-card-info">
                    <h3 className="site-card-title">
                        {result.title || "Untitled Page"}
                    </h3>
                    <div className="site-card-meta">
                        <span className="site-card-domain">{domain}</span>
                        {markdown && (
                            <span className="site-card-size">
                                <FileText size={12} />
                                {(markdown.content_length / 1024).toFixed(1)} KB
                            </span>
                        )}
                    </div>
                </div>
                <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="site-card-link"
                    title="Open source"
                >
                    <ExternalLink size={16} />
                </a>
            </div>

            {/* Preview */}
            <div className="site-card-preview">
                <p>{contentPreview}</p>
            </div>

            {/* Expand/Collapse */}
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="site-card-toggle"
                id={`toggle-markdown-${index}`}
            >
                {isExpanded ? (
                    <>
                        <ChevronUp size={14} />
                        <span>Hide Markdown</span>
                    </>
                ) : (
                    <>
                        <ChevronDown size={14} />
                        <span>View Full Markdown</span>
                    </>
                )}
            </button>

            {/* Expanded Content */}
            <AnimatePresence>
                {isExpanded && (markdown?.content || result.parsed_product) && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="site-card-markdown"
                    >
                        <div className="markdown-header" style={{ display: "flex", gap: "16px", marginBottom: "8px" }}>
                            <div className="tab-buttons" style={{ display: "flex", gap: "8px", flex: 1 }}>
                                {markdown && (
                                    <span style={{ fontSize: "12px", color: "rgba(255,255,255,0.7)" }}>
                                        <Hash size={12} style={{ display: "inline", marginRight: "4px" }} />
                                        MD ({markdown.content_length.toLocaleString()} chars)
                                    </span>
                                )}
                                {result.parsed_product && (
                                    <span style={{ fontSize: "12px", color: "#10b981", marginLeft: "10px" }}>
                                        ✓ Parsed JSON Object
                                    </span>
                                )}
                            </div>
                        </div>
                        <div style={{ display: "flex", gap: "16px" }}>
                            {result.parsed_product && (
                                <div style={{ flex: 1, minWidth: 0 }}>
                                    <div style={{ fontSize: "11px", color: "#10b981", marginBottom: "4px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Extracted Product Data</div>
                                    <pre className="markdown-content json-view" style={{ borderColor: "rgba(16, 185, 129, 0.3)" }}>
                                        {JSON.stringify(result.parsed_product.data, null, 2)}
                                    </pre>
                                </div>
                            )}
                            {markdown && (
                                <div style={{ flex: result.parsed_product ? 1 : 'none', minWidth: 0, width: result.parsed_product ? 'auto' : '100%' }}>
                                    <div style={{ fontSize: "11px", color: "rgba(255,255,255,0.4)", marginBottom: "4px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Raw Scraped Content</div>
                                    <pre className="markdown-content">{markdown.content}</pre>
                                </div>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}
