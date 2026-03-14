const API_BASE_URL = '/api'

export class ApiClient {
    private baseURL: string

    constructor(baseURL: string = API_BASE_URL) {
        this.baseURL = baseURL
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {},
        skipContentType = false
    ): Promise<T> {
        const url = `${this.baseURL}${endpoint}`
        const headers = skipContentType
            ? { ...options.headers as Record<string, string> }
            : { 'Content-Type': 'application/json', ...options.headers as Record<string, string> }
        const config: RequestInit = {
            ...options,
            headers,
        }

        try {
            const response = await fetch(url, config)

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            return await response.json()
        } catch (error) {
            console.error('API request failed:', error)
            throw error
        }
    }

    async get<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, { method: 'GET' })
    }

    async post<T>(endpoint: string, data?: unknown): Promise<T> {
        if (data instanceof FormData) {
            return this.request<T>(endpoint, {
                method: 'POST',
                body: data,
            }, true)
        }
        return this.request<T>(endpoint, {
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined,
        })
    }

    async put<T>(endpoint: string, data?: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined,
        })
    }

    async delete<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, { method: 'DELETE' })
    }
}

export const apiClient = new ApiClient() 