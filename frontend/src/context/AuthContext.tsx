'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import jwtDecode from 'jwt-decode';
import api from '@/lib/api';
import { toast } from 'sonner';  // Import sonner for notifications

interface User {
  id: number;
  username: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded: { user_id: number } = jwtDecode(token);
        api.get('me').then((res) => {
          setUser(res.data);
        }).catch(() => {
          localStorage.removeItem('token');
          toast.error('Session expired. Please log in again.');
        });
      } catch {
        localStorage.removeItem('token');
        toast.error('Invalid session token.');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const res = await api.post('login', { username, password });
      localStorage.setItem('token', res.data.token);
      const userRes = await api.get('me');
      setUser(userRes.data);
      toast.success('Logged in successfully');  // Use sonner toast for feedback
    } catch {
      toast.error('Invalid credentials');  // Use sonner toast for error
      throw new Error('Login failed');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    toast.info('Logged out successfully');  // Use sonner toast for info
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};