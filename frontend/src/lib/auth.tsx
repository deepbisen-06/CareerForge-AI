import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';
import { AuthResponse } from '../types';

interface AuthUser {
  email: string;
  full_name?: string;
  user_id: number;
  role?: string;
}

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  login: (email: string, pass: string) => Promise<void>;
  loginAsDemo: () => Promise<void>;
  loginAsAdmin: () => Promise<void>;
  register: (email: string, pass: string, name?: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('careerbridge_token') || localStorage.getItem('token'));
  const [user, setUser] = useState<AuthUser | null>(() => {
    const saved = localStorage.getItem('careerbridge_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    if (token) {
      api.auth.me()
        .then((userData) => {
          if (userData && userData.email) {
            setUser({
              email: userData.email,
              full_name: userData.full_name,
              user_id: userData.id,
              role: userData.role || 'student'
            });
          }
        })
        .catch(() => {
          logout();
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const handleAuthSuccess = (data: AuthResponse) => {
    const userObj: AuthUser = {
      email: data.email,
      full_name: data.full_name,
      user_id: data.user_id,
      role: data.role || (data.email.includes('admin') ? 'admin' : 'student')
    };
    setToken(data.access_token);
    setUser(userObj);
    localStorage.setItem('careerbridge_token', data.access_token);
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('careerbridge_user', JSON.stringify(userObj));
  };

  const login = async (email: string, pass: string) => {
    const data = await api.auth.login({ email, password: pass });
    handleAuthSuccess(data);
  };

  const loginAsDemo = async () => {
    const data = await api.auth.login({ email: 'demo@careerbridge.ai', password: 'Demo@123' });
    handleAuthSuccess(data);
  };

  const loginAsAdmin = async () => {
    const data = await api.auth.login({ email: 'admin@careerbridge.ai', password: 'Admin@123' });
    handleAuthSuccess(data);
  };

  const register = async (email: string, pass: string, name?: string) => {
    const data = await api.auth.register({ email, password: pass, full_name: name });
    handleAuthSuccess(data);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('careerbridge_token');
    localStorage.removeItem('token');
    localStorage.removeItem('careerbridge_user');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, loginAsDemo, loginAsAdmin, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
