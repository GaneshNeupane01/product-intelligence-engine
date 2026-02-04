/* ---------------------------------------------------------------
   Types matching the Django REST API responses (Phases 1-5)
   --------------------------------------------------------------- */

export interface RawMarkdown {
    id: string;
    content: string;
    content_length: number;
    extracted_at: string;
}

export interface NormalizedProduct {
    id: string;
    normalized_specs: Record<string, string>;
    normalized_price: {
        amount: number | null;
        currency: string;
        original_amount: number | null;
        usd_equivalent: number | null;
    };
    normalized_at: string;
}

export interface ParsedProduct {
    id: string;
    data: Record<string, any>;
    error_message: string | null;
    parsed_at: string;
    normalized: NormalizedProduct | null;
}

export interface SearchResult {
    id: string;
    url: string;
    title: string;
    description: string;
    position: number;
    raw_markdown: RawMarkdown | null;
    parsed_product: ParsedProduct | null;
    created_at: string;
}

export interface ComparisonResult {
    id: string;
    data: {
        product_name?: string;
        total_sellers?: number;
        price_comparison?: {
            cheapest?: { seller: string; price: number; currency: string };
            most_expensive?: { seller: string; price: number; currency: string } | null;
            average_price?: number;
            price_range?: string;
        };
        rating_comparison?: {
            highest_rated?: { seller: string; score: number; count: number };
            average_rating?: number;
        };
        availability_summary?: {
            in_stock_count?: number;
            out_of_stock_sellers?: string[];
        };
        shipping_comparison?: {
            fastest?: { seller: string; timeframe: string };
            free_shipping_sellers?: string[];
        };
        value_analysis?: {
            best_value?: { seller: string; reason: string };
            best_overall?: { seller: string; reason: string };
        };
        seller_details?: Array<{
            seller: string;
            domain: string;
            price: number;
            currency: string;
            usd_equivalent: number | null;
            rating: number | null;
            in_stock: boolean;
            shipping: string;
        }>;
        [key: string]: any;
    };
    compared_at: string;
}

export interface RecommendationData {
    id: string;
    data: {
        summary?: string;
        best_pick?: { seller: string; reason: string };
        budget_pick?: { seller: string; reason: string };
        insights?: string[];
        warnings?: string[];
        verdict?: string;
        confidence_score?: number;
        [key: string]: any;
    };
    recommended_at: string;
}

export interface SearchQuery {
    id: string;
    query: string;
    num_sites: number;
    provider: string;
    status:
    | "pending"
    | "searching"
    | "crawling"
    | "parsing"
    | "normalizing"
    | "comparing"
    | "recommending"
    | "completed"
    | "failed";
    error_message: string | null;
    results: SearchResult[];
    comparison: ComparisonResult | null;
    recommendation: RecommendationData | null;
    created_at: string;
    completed_at: string | null;
}

export interface SearchRequest {
    query: string;
    num_sites: number;
}

/* Pipeline step for loading visualization */
export type PipelineStep =
    | "idle"
    | "submitting"
    | "searching"
    | "crawling"
    | "parsing"
    | "normalizing"
    | "comparing"
    | "recommending"
    | "completed"
    | "failed";
