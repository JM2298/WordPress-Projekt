export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:18000/api";

type RequestOptions = {
  method?: "GET" | "POST";
  body?: unknown;
  token?: string;
};

export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

export function formatApiError(error: unknown) {
  if (error instanceof ApiError) {
    return JSON.stringify(
      {
        message: error.message,
        status: error.status,
        payload: error.payload,
      },
      null,
      2,
    );
  }

  if (error instanceof Error) {
    return JSON.stringify(
      {
        message: error.message,
      },
      null,
      2,
    );
  }

  return JSON.stringify(
    {
      message: "Unknown error",
      payload: error,
    },
    null,
    2,
  );
}

export function persistAuth(payload: {
  access: string;
  refresh: string;
  user?: unknown;
}) {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem("accessToken", payload.access);
  window.localStorage.setItem("refreshToken", payload.refresh);
  if (payload.user) {
    window.localStorage.setItem("currentUser", JSON.stringify(payload.user));
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers: {
      Accept: "application/json",
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
    cache: "no-store",
  });

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message =
      typeof payload === "object" && payload !== null && "detail" in payload
        ? String((payload as { detail: unknown }).detail)
        : `Request failed with status ${response.status}`;
    throw new ApiError(message, response.status, payload);
  }

  return payload as T;
}

export type RegisterPayload = {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
};

export type CategoryPayload = {
  name: string;
  image?: {
    src: string;
  };
};

export type ProductPayload = {
  name: string;
  type: string;
  regular_price: string;
  description?: string;
  short_description?: string;
  categories?: Array<{ id: number }>;
  images?: Array<{ id?: number; src?: string }>;
};
