/**
 * Business API Client
 * 
 * Provides typed API methods for business endpoints (deals, assets, templates, etc.)
 * Uses unified response format: { code, msg, data }
 * 
 * Note: LangGraph endpoints use a separate client (client.ts) with raw responses.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ============================================================
// Types
// ============================================================

/** Unified API response format */
interface ApiResponse<T = unknown> {
  code: number;
  msg: string;
  data: T;
}

/** Paged data wrapper */
interface PagedData<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}

/** Deal entity */
interface Deal {
  id: number;
  name: string;
  client_name?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

/** Asset entity */
interface Asset {
  id: number;
  deal_id: number;
  name: string;
  asset_type: string;
  address?: string;
  city?: string;
  state?: string;
  valuation?: number;
  created_at: string;
}

// ============================================================
// Error Codes
// ============================================================

export const ErrorCode = {
  SUCCESS: 0,
  PARAM_ERROR: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  SERVER_ERROR: 500,
  DB_ERROR: 501,
  EXTERNAL_API_ERROR: 502,
  SERVICE_UNAVAILABLE: 503,
} as const;

// ============================================================
// Custom Error Class
// ============================================================

export class ApiError extends Error {
  code: number;
  data?: unknown;

  constructor(code: number, message: string, data?: unknown) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.data = data;
  }
}

// ============================================================
// Request Helper
// ============================================================

/**
 * Make an API request with unified response handling
 * 
 * @param endpoint - API endpoint path
 * @param options - Fetch options
 * @returns Parsed response data
 * @throws ApiError if response code is not SUCCESS
 */
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  // Parse response as JSON
  const result: ApiResponse<T> = await response.json();

  // Check for business logic errors
  if (result.code !== ErrorCode.SUCCESS) {
    throw new ApiError(result.code, result.msg, result.data);
  }

  return result.data;
}

/**
 * Make a form data request (for file uploads)
 */
async function requestFormData<T>(
  endpoint: string,
  formData: FormData
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    body: formData,
  });

  const result: ApiResponse<T> = await response.json();

  if (result.code !== ErrorCode.SUCCESS) {
    throw new ApiError(result.code, result.msg, result.data);
  }

  return result.data;
}

// ============================================================
// API Methods
// ============================================================

export const api = {
  // Health check
  health: () => request<{ status: string }>("/health"),

  // Deal endpoints
  deals: {
    /** Get list of deals with pagination */
    list: (params?: { offset?: number; limit?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.offset) searchParams.set("offset", String(params.offset));
      if (params?.limit) searchParams.set("limit", String(params.limit));
      const query = searchParams.toString();
      return request<Deal[]>(`/deals/${query ? `?${query}` : ""}`);
    },

    /** Get a specific deal by ID */
    get: (id: number) => request<Deal>(`/deals/${id}`),

    /** Create a new deal */
    create: (data: Partial<Deal>) =>
      request<Deal>("/deals/", {
        method: "POST",
        body: JSON.stringify(data),
      }),

    /** Update an existing deal */
    update: (id: number, data: Partial<Deal>) =>
      request<Deal>(`/deals/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),

    /** Delete a deal */
    delete: (id: number) =>
      request<boolean>(`/deals/${id}`, { method: "DELETE" }),

    /** Get all assets for a deal */
    getAssets: (dealId: number) => request<Asset[]>(`/deals/${dealId}/assets/`),
  },

  // Asset endpoints
  assets: {
    /** Create a new asset */
    create: (data: Partial<Asset>) =>
      request<Asset>("/assets/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },

  // Template endpoints (for future use)
  templates: {
    /** Upload an Excel template */
    upload: (file: File, name?: string) => {
      const formData = new FormData();
      formData.append("file", file);
      if (name) formData.append("name", name);
      return requestFormData<{
        template_id: number;
        input_fields: Record<string, string>;
        output_fields: Record<string, string>;
      }>("/api/templates/upload", formData);
    },

    /** Generate a financial model from template */
    generate: (templateId: number, inputs: Record<string, unknown>) =>
      request<{ results: Record<string, unknown>; download_url: string }>(
        `/api/templates/${templateId}/generate`,
        {
          method: "POST",
          body: JSON.stringify(inputs),
        }
      ),
  },
};

// Export types for use in components
export type { Deal, Asset, ApiResponse, PagedData };
