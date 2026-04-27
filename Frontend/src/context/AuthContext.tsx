import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiUrl } from '../utils/api';

interface User {
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const CURRENT_USER_KEY = 'shiksha_flow_user';
const AUTH_TOKEN_KEY = 'shiksha_flow_token';
const LEGACY_CURRENT_USER_KEY = 'edubuilder_user';
const LEGACY_AUTH_TOKEN_KEY = 'edubuilder_token';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedUser = localStorage.getItem(CURRENT_USER_KEY) || localStorage.getItem(LEGACY_CURRENT_USER_KEY);
    const storedToken = localStorage.getItem(AUTH_TOKEN_KEY) || localStorage.getItem(LEGACY_AUTH_TOKEN_KEY);
    if (storedUser) {
      setUser(JSON.parse(storedUser));
      localStorage.setItem(CURRENT_USER_KEY, storedUser);
      localStorage.removeItem(LEGACY_CURRENT_USER_KEY);
    }
    if (storedToken) {
      setToken(storedToken);
      localStorage.setItem(AUTH_TOKEN_KEY, storedToken);
      localStorage.removeItem(LEGACY_AUTH_TOKEN_KEY);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await fetch(apiUrl('/auth/login'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data?.error || 'Invalid credentials');
    }

    setUser(data.user);
    setToken(data.token);
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(data.user));
    localStorage.setItem(AUTH_TOKEN_KEY, data.token);
  };

  const signup = async (name: string, email: string, password: string) => {
    const response = await fetch(apiUrl('/auth/signup'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data?.error || 'Failed to create account');
    }

    setUser(data.user);
    setToken(data.token);
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(data.user));
    localStorage.setItem(AUTH_TOKEN_KEY, data.token);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem(CURRENT_USER_KEY);
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(LEGACY_CURRENT_USER_KEY);
    localStorage.removeItem(LEGACY_AUTH_TOKEN_KEY);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, signup, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};
