import { apiClient } from './client'

export interface Citation {
    chunk_id: string
    content: string
    page_number: number
    relevance_score?: number
}

export interface ChatRequest {
    query: string
    document_id?: string
    conversation_id?: string | null
}

export interface ChatResponse {
    response: string
    citations: Citation[]
    response_time: number
    conversation_id: string | null
}

export interface ChatHistoryItem {
    id: string
    user_query: string
    ai_response: string
    created_at: string
    response_time?: number
    document_id?: string
    conversation_id?: string | null
    citations?: Citation[]
}

export interface ChatHistoryResponse {
    chats: ChatHistoryItem[]
    total: number
}

export interface ConversationSummary {
    id: string
    title: string | null
    created_at: string
    updated_at: string
    message_count: number
}

export interface ConversationListResponse {
    conversations: ConversationSummary[]
    total: number
}

export interface ConversationDetail {
    id: string
    title: string | null
    created_at: string
    updated_at: string
    chats: ChatHistoryItem[]
}

export const chatApi = {
    async sendMessage(request: ChatRequest): Promise<ChatResponse> {
        return await apiClient.post<ChatResponse>('/chat/', request)
    },

    async getHistory(skip: number = 0, limit: number = 50, document_id?: string): Promise<ChatHistoryResponse> {
        const params = new URLSearchParams()
        if (skip > 0) params.append('skip', skip.toString())
        if (limit !== 50) params.append('limit', limit.toString())
        if (document_id) params.append('document_id', document_id)

        const queryString = params.toString()
        const endpoint = `/chat/history${queryString ? `?${queryString}` : ''}`

        return await apiClient.get<ChatHistoryResponse>(endpoint)
    },
}

export const conversationsApi = {
    async list(skip: number = 0, limit: number = 30): Promise<ConversationListResponse> {
        const params = new URLSearchParams()
        if (skip > 0) params.append('skip', skip.toString())
        if (limit !== 30) params.append('limit', limit.toString())
        const queryString = params.toString()
        return await apiClient.get<ConversationListResponse>(
            `/conversations/${queryString ? `?${queryString}` : ''}`
        )
    },

    async get(id: string): Promise<ConversationDetail> {
        return await apiClient.get<ConversationDetail>(`/conversations/${id}`)
    },

    async delete(id: string): Promise<void> {
        await apiClient.delete(`/conversations/${id}`)
    },
}
