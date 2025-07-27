import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
}

class AuthService {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }

  async login(username: string, password: string): Promise<AuthResponse> {
    const response = await axios.post(`${API_BASE_URL}/auth/login`, {
      username,
      password,
    });
    return response.data;
  }

  async register(username: string, password: string): Promise<AuthResponse> {
    const response = await axios.post(`${API_BASE_URL}/auth/register`, {
      username,
      password,
    });
    return response.data;
  }
}

export const authService = new AuthService();