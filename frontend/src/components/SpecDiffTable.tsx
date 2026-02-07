"use client";

import { motion } from "framer-motion";
import type { SearchResult } from "@/types/search";

interface SpecDiffTableProps {
    results: SearchResult[];
}

export default function SpecDiffTable({ results }: SpecDiffTableProps) {
    // Extract sellers and their specs
    const validResults = results.filter(
        (r) => r.parsed_product?.normalized?.normalized_specs
    );

    if (validResults.length === 0) return null;

    const sellers = validResults.map((r) => {
        const domain = new URL(r.url).hostname.replace("www.", "");
        const sellerName = r.parsed_product?.data?.seller?.name || domain;
        return {
            id: r.id,
            name: sellerName,
            specs: r.parsed_product?.normalized?.normalized_specs || {},
        };
    });

    // Extract all unique spec keys
    const allSpecKeys = new Set<string>();
    sellers.forEach((s) => {
        Object.keys(s.specs).forEach((k) => allSpecKeys.add(k));
    });

    const specKeysArray = Array.from(allSpecKeys).sort();

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full overflow-x-auto rounded-xl border border-[#2a2a3a] mb-8 bg-[#13131d] shadow-[0_4px_20px_rgba(0,0,0,0.3)]"
        >
            <table className="w-full text-left border-collapse text-sm">
                <thead>
                    <tr className="bg-[#1a1a24] border-b border-[#2a2a3a]">
                        <th className="p-4 font-semibold text-[#a0a0b5] sticky left-0 bg-[#1a1a24] z-10 
                                       border-r border-[#2a2a3a] w-1/4 uppercase tracking-wider text-xs">
                            Specification
                        </th>
                        {sellers.map((s, idx) => (
                            <th key={s.id} className="p-4 font-semibold text-white whitespace-nowrap min-w-[150px]">
                                {s.name}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {specKeysArray.map((key, rowIdx) => {
                        // Check if values differ across sellers
                        const values = sellers.map((s) => s.specs[key]?.toString().toLowerCase() || "");
                        const firstVal = values.find((v) => v !== "");
                        const hasDifference = values.some(
                            (v) => v !== "" && firstVal !== undefined && v !== firstVal
                        );

                        return (
                            <motion.tr
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: rowIdx * 0.05 }}
                                key={key}
                                className="border-b border-[#2a2a3a]/50 hover:bg-[#1a1a28] transition-colors"
                            >
                                <td className="p-4 sticky left-0 bg-[#13131d] font-medium text-[#a78bfa] border-r border-[#2a2a3a] shadow-[4px_0_10px_-4px_rgba(0,0,0,0.3)] capitalize">
                                    {key.replace(/_/g, " ")}
                                </td>
                                {sellers.map((s) => {
                                    const val = s.specs[key] || "—";
                                    const isDiff = hasDifference && val !== "—";

                                    return (
                                        <td
                                            key={s.id}
                                            className={`p-4 text-[#f0f0f5] ${isDiff
                                                    ? "bg-[rgba(34,197,94,0.06)]/50 text-[#22c55e] font-semibold"
                                                    : ""
                                                }`}
                                        >
                                            {val}
                                        </td>
                                    );
                                })}
                            </motion.tr>
                        );
                    })}
                </tbody>
            </table>
        </motion.div>
    );
}
