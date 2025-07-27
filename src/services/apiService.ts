import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface ChatRequest {
  prompt: string;
  temperature?: number;
  max_tokens?: number;
  tools?: string[];
}

export interface ToolCall {
  tool: string;
  params: Record<string, any>;
  result: any;
  success: boolean;
  execution_time: number;
  error?: string;
}

export interface ChatResponse {
  id: string;
  thought: string;
  tool_calls: ToolCall[];
  final_answer: string;
  model_info: Record<string, any>;
  processing_time: number;
  tokens_used: number;
  timestamp: string;
}

export interface ToolInfo {
  name: string;
  description: string;
  parameters: Record<string, any>;
  category: string;
  enabled: boolean;
}

export interface SystemStatus {
  status: string;
  version: string;
  uptime: number;
  model_loaded: boolean;
  tools_available: number;
  active_users: number;
  requests_today: number;
}

class ApiService {
  async getStatus(): Promise<SystemStatus> {
    const response = await axios.get(`${API_BASE_URL}/`);
    return response.data;
  }

  async getTools(): Promise<ToolInfo[]> {
    const response = await axios.get(`${API_BASE_URL}/tools`);
    return response.data;
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await axios.post(`${API_BASE_URL}/ask`, request);
    return response.data;
  }

  async getHistory(limit = 50, offset = 0) {
    const response = await axios.get(`${API_BASE_URL}/history`, {
      params: { limit, offset },
    });
    return response.data;
  }

  async toggleTool(toolName: string): Promise<{ tool: string; enabled: boolean }> {
    const response = await axios.post(`${API_BASE_URL}/tools/${toolName}/toggle`);
    return response.data;
  }
}

export const apiService = new ApiService();