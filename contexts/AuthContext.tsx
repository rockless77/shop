import React, {
    createContext,
    useContext,
    useState,
    useEffect,
  } from 'react';
  import type { ReactNode } from 'react';
  
  interface User {
    id: string;
    name: string;
    email: string;
  }
  
  interface AuthContextValue {
    user: User | null;
    login: (email: string, password: string) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
  }
  
  // Type assertion instead of generic argument
  const AuthContext = createContext({} as AuthContextValue);
  
  export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
  
    useEffect(() => {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
    }, []);
  
    const login = async (email: string, password: string) => {
      const mockUser = {
        id: '1',
        name: 'Test User',
        email,
      };
      setUser(mockUser);
      localStorage.setItem('user', JSON.stringify(mockUser));
    };
  
    const logout = () => {
      setUser(null);
      localStorage.removeItem('user');
    };
  
    const value: AuthContextValue = {
      user,
      login,
      logout,
      isAuthenticated: !!user,
    };
  
    return (
      <AuthContext.Provider value={value}>
        {children}
      </AuthContext.Provider>
    );
  };
  
  export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
      throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
  };
  