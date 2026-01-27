"use client";

import { motion } from "framer-motion";
import { Sparkles, AlertTriangle, Lightbulb } from "lucide-react";
import type { RecommendationData } from "@/types/search";

interface RecommendationPanelProps {
    recommendation: RecommendationData;
}

export default function RecommendationPanel({
    recommendation,
}: RecommendationPanelProps) {
    const data = recommendation.data;

    if (!data || !data.summary) {
        return null;
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="recommendation-panel"
        >
            <div className="recommendation-header">
                <Sparkles size={24} className="text-primary" />
                <h2>AI Shopping Insights</h2>
            </div>

            <div className="recommendation-summary">
                <p>{data.summary}</p>
            </div>

            <div className="recommendation-grid">
                {/* Insights */}
                {data.insights && data.insights.length > 0 && (
                    <div className="recommendation-card recommendation-card--blue">
                        <div className="card-header">
                            <Lightbulb size={18} />
                            <h3>Key Insights</h3>
                        </div>
                        <ul>
                            {data.insights.map((insight, idx) => (
                                <li key={idx}>{insight}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Warnings */}
                {data.warnings && data.warnings.length > 0 && (
                    <div className="recommendation-card recommendation-card--red">
                        <div className="card-header">
                            <AlertTriangle size={18} />
                            <h3>Warnings</h3>
                        </div>
                        <ul>
                            {data.warnings.map((warning, idx) => (
                                <li key={idx}>{warning}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {/* Verdict */}
            {data.verdict && (
                <div className="recommendation-verdict">
                    <span className="verdict-label">Final Verdict:</span>
                    <p>{data.verdict}</p>
                </div>
            )}
        </motion.div>
    );
}
