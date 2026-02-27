import { handleApiError } from './errors';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions extends Omit<RequestInit, 'headers'> {
  headers?: Record<string, string>;
  skipErrorHandling?: boolean;
}

async function request<T>(
  method: string,
  endpoint: string,
  data?: unknown,
  options: RequestOptions = {}
): Promise<T> {
  const { skipErrorHandling = false, ...fetchOptions } = options;

  const url = `${API_BASE}${endpoint}`;

  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  const config: RequestInit = {
    ...fetchOptions,
    method,
    headers: {
      ...defaultHeaders,
      ...fetchOptions.headers,
    },
  };

  // Add body for methods that support it
  if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
    config.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorText = await response.text();
      const error = new Error(
        `API Error (${response.status}): ${errorText || response.statusText}`
      );
      (error as any).status = response.status;
      throw error;
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  } catch (error) {
    if (!skipErrorHandling) {
      handleApiError(error, endpoint);
    }
    throw error;
  }
}

export async function fetchApi<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  return request<T>('GET', endpoint, undefined, options);
}

// API client with HTTP methods
export const api = {
  get: <T>(endpoint: string, options?: RequestOptions) => fetchApi<T>(endpoint, options),
  post: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
    request<T>('POST', endpoint, data, options),
  put: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
    request<T>('PUT', endpoint, data, options),
  patch: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
    request<T>('PATCH', endpoint, data, options),
  delete: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>('DELETE', endpoint, undefined, options),
};

export default fetchApi;
