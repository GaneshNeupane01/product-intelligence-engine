/* ---------------------------------------------------------------
   API client for the Django backend
   --------------------------------------------------------------- */

import { SearchQuery, SearchRequest } from "@/types/search";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function handleResponse<T>(res: Response): Promise<T> {
    if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error || body.detail || `API error: ${res.status}`);
    }
    return res.json() as Promise<T>;
}

export async function searchProducts(
    data: SearchRequest
): Promise<SearchQuery> {
    const res = await fetch(`${API_BASE}/api/search/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    return handleResponse<SearchQuery>(res);
}

export async function getSearchDetail(id: string): Promise<SearchQuery> {
    const res = await fetch(`${API_BASE}/api/search/${id}/`);
    return handleResponse<SearchQuery>(res);
}

export async function getSearchHistory(): Promise<SearchQuery[]> {
    const res = await fetch(`${API_BASE}/api/search/history/`);
    return handleResponse<SearchQuery[]>(res);
}
