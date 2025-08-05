const API_BASE_URL = 'http://localhost:8000';

export interface ChatResponse {
  response: string;
  session_id: string;
  pdf_generated: boolean;
  pdf_id?: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export const chatAPI = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  async downloadPdf(pdfId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/download/${pdfId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to download PDF: ${response.status}`);
    }

    return response.blob();
  },

  async healthCheck(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  }
};