import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

interface User {
  id: string;
  username: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token validity
      authService.setToken(token);
      // In a real app, you'd verify the token with the server
      setUser({ id: 'user', username: 'demo' });
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    const response = await authService.login(username, password);
    localStorage.setItem('token', response.access_token);
    authService.setToken(response.access_token);
    setUser({ id: response.user_id, username });
  };

  const register = async (username: string, password: string) => {
    const response = await authService.register(username, password);
    localStorage.setItem('token', response.access_token);
    authService.setToken(response.access_token);
    setUser({ id: response.user_id, username });
  };

  const logout = () => {
    localStorage.removeItem('token');
    authService.setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};