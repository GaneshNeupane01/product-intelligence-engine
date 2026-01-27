/* ---------------------------------------------------------------
   Types matching the Django REST API responses
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

export interface SearchQuery {
    id: string;
    query: string;
    num_sites: number;
    provider: string;
    status: "pending" | "searching" | "crawling" | "parsing" | "normalizing" | "completed" | "failed";
    error_message: string | null;
    results: SearchResult[];
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
    | "extracting"
    | "parsing"
    | "normalizing"
    | "completed"
    | "failed";
