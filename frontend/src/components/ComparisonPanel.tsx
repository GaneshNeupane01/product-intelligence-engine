"use client";

import { motion } from "framer-motion";
import {
    TrendingDown,
    TrendingUp,
    Star,
    Truck,
    Package,
    Award,
    DollarSign,
} from "lucide-react";
import type { ComparisonResult } from "@/types/search";

interface ComparisonPanelProps {
    comparison: ComparisonResult;
}

export default function ComparisonPanel({ comparison }: ComparisonPanelProps) {
    const data = comparison.data;

    if (!data || !data.seller_details?.length) {
        return null;
    }

    const cheapest = data.price_comparison?.cheapest;
    const bestValue = data.value_analysis?.best_value;
    const highestRated = data.rating_comparison?.highest_rated;
    const fastest = data.shipping_comparison?.fastest;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="comparison-panel"
        >
            <h2 className="comparison-title">
                <Award size={20} />
                Price Comparison — {data.product_name || "Product"}
            </h2>
            <p className="comparison-subtitle">
                {data.total_sellers || 0} sellers compared
            </p>

            {/* Highlight Cards */}
            <div className="comparison-highlights">
                {cheapest && (
                    <div className="highlight-card highlight-card--green">
                        <div className="highlight-icon">
                            <TrendingDown size={20} />
                        </div>
                        <div className="highlight-content">
                            <span className="highlight-label">Cheapest</span>
                            <span className="highlight-value">
                                {cheapest.currency} {cheapest.price?.toLocaleString()}
                            </span>
                            <span className="highlight-seller">{cheapest.seller}</span>
                        </div>
                    </div>
                )}

                {bestValue && (
                    <div className="highlight-card highlight-card--blue">
                        <div className="highlight-icon">
                            <DollarSign size={20} />
                        </div>
                        <div className="highlight-content">
                            <span className="highlight-label">Best Value</span>
                            <span className="highlight-value">{bestValue.seller}</span>
                            <span className="highlight-reason">{bestValue.reason}</span>
                        </div>
                    </div>
                )}

                {highestRated && (
                    <div className="highlight-card highlight-card--amber">
                        <div className="highlight-icon">
                            <Star size={20} />
                        </div>
                        <div className="highlight-content">
                            <span className="highlight-label">Highest Rated</span>
                            <span className="highlight-value">
                                {highestRated.score}/5 ({highestRated.count} reviews)
                            </span>
                            <span className="highlight-seller">{highestRated.seller}</span>
                        </div>
                    </div>
                )}

                {fastest && (
                    <div className="highlight-card highlight-card--purple">
                        <div className="highlight-icon">
                            <Truck size={20} />
                        </div>
                        <div className="highlight-content">
                            <span className="highlight-label">Fastest Shipping</span>
                            <span className="highlight-value">{fastest.timeframe}</span>
                            <span className="highlight-seller">{fastest.seller}</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Seller Table */}
            {data.seller_details && data.seller_details.length > 0 && (
                <div className="comparison-table-wrapper">
                    <table className="comparison-table">
                        <thead>
                            <tr>
                                <th>Seller</th>
                                <th>Price</th>
                                <th>Rating</th>
                                <th>Stock</th>
                                <th>Shipping</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.seller_details.map((seller, idx) => (
                                <tr key={idx}>
                                    <td>
                                        <div className="seller-cell">
                                            <span className="seller-name">{seller.seller}</span>
                                            <span className="seller-domain">{seller.domain}</span>
                                        </div>
                                    </td>
                                    <td className="price-cell">
                                        {seller.currency} {seller.price?.toLocaleString() || "—"}
                                    </td>
                                    <td>
                                        {seller.rating ? (
                                            <span className="rating-badge">
                                                <Star size={12} /> {seller.rating}
                                            </span>
                                        ) : (
                                            <span className="no-data">—</span>
                                        )}
                                    </td>
                                    <td>
                                        <span
                                            className={`stock-badge ${seller.in_stock
                                                    ? "stock-badge--in"
                                                    : "stock-badge--out"
                                                }`}
                                        >
                                            <Package size={12} />
                                            {seller.in_stock ? "In Stock" : "Out"}
                                        </span>
                                    </td>
                                    <td>{seller.shipping || "—"}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </motion.div>
    );
}
