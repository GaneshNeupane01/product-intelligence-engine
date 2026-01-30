"use client";

import { motion } from "framer-motion";
import {
    Search,
    Globe,
    FileText,
    Ruler,
    GitCompareArrows,
    Sparkles,
    CheckCircle,
    XCircle,
} from "lucide-react";
import type { PipelineStep } from "@/types/search";

interface PipelineVisualizerProps {
    currentStep: PipelineStep;
}

const steps = [
    { key: "searching", label: "Searching the Web", icon: Search },
    { key: "crawling", label: "Crawling Websites", icon: Globe },
    { key: "parsing", label: "Extracting Data", icon: FileText },
    { key: "normalizing", label: "Normalizing Specs", icon: Ruler },
    { key: "comparing", label: "Comparing Prices", icon: GitCompareArrows },
    { key: "recommending", label: "AI Insights", icon: Sparkles },
    { key: "completed", label: "Done", icon: CheckCircle },
];

const stepOrder = [
    "submitting",
    "searching",
    "crawling",
    "parsing",
    "normalizing",
    "comparing",
    "recommending",
    "completed",
];

function getStepState(
    stepKey: string,
    currentStep: PipelineStep
): "pending" | "active" | "done" {
    if (currentStep === "failed") return "pending";
    const currentIdx = stepOrder.indexOf(currentStep);
    const stepIdx = stepOrder.indexOf(stepKey);
    if (stepIdx < currentIdx) return "done";
    if (stepIdx === currentIdx) return "active";
    return "pending";
}

export default function PipelineVisualizer({
    currentStep,
}: PipelineVisualizerProps) {
    if (currentStep === "idle") return null;

    return (
        <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.4 }}
            className="pipeline-container"
        >
            {currentStep === "failed" && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="pipeline-error"
                >
                    <XCircle size={20} />
                    <span>Search failed. Please try again.</span>
                </motion.div>
            )}

            <div className="pipeline-steps">
                {steps.map((step, idx) => {
                    const state = getStepState(step.key, currentStep);
                    const Icon = step.icon;

                    return (
                        <motion.div
                            key={step.key}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            className={`pipeline-step pipeline-step--${state}`}
                        >
                            <div className="pipeline-step-icon">
                                {state === "active" ? (
                                    <div className="spinner-sm" />
                                ) : state === "done" ? (
                                    <CheckCircle size={18} />
                                ) : (
                                    <Icon size={18} />
                                )}
                            </div>
                            <span className="pipeline-step-label">{step.label}</span>
                        </motion.div>
                    );
                })}
            </div>
        </motion.div>
    );
}
