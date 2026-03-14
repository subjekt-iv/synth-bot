import { apiClient } from './client'

export interface Document {
    id: string
    filename: string
    original_filename: string
    file_size: number
    num_pages: number
    num_chunks: number
    upload_date: string
}

export interface DocumentUploadResponse {
    document_id: string
    filename: string
    original_filename: string
    file_size: number
    num_pages: number
    num_chunks: number
    upload_date: string
    message: string
}

interface DocumentListResponse {
    documents: Document[]
    total: number
}

export const documentsApi = {
    async uploadDocument(file: File): Promise<DocumentUploadResponse> {
        const formData = new FormData()
        formData.append('file', file)

        return await apiClient.post<DocumentUploadResponse>('/documents/upload', formData)
    },

    async getDocuments(): Promise<Document[]> {
        const response = await apiClient.get<DocumentListResponse>('/documents')
        return response.documents
    },

    async deleteDocument(id: string): Promise<void> {
        await apiClient.delete(`/documents/${id}`)
    },
}
