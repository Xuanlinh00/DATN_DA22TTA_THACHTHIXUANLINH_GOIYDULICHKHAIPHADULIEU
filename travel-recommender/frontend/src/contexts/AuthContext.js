import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi, getOrCreateUserId } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize Auth state from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem('nomadai_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        localStorage.removeItem('nomadai_user');
      }
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (username, password) => {
    try {
      const response = await authApi.login(username, password);
      if (response.data.success) {
        const userData = response.data.user;
        setUser(userData);
        localStorage.setItem('nomadai_user', JSON.stringify(userData));
        localStorage.setItem('nomadai_user_id', userData.username); // Link CF/Ratings to username
        return { success: true, message: response.data.message };
      }
      return { success: false, message: response.data.message || 'Đăng nhập thất bại' };
    } catch (error) {
      console.error('Login error:', error);
      const msg = error.response?.data?.detail || 'Kết nối máy chủ thất bại';
      return { success: false, message: msg };
    }
  }, []);

  const register = useCallback(async (username, password, fullName, email) => {
    try {
      const response = await authApi.register(username, password, fullName, email);
      if (response.data.success) {
        return { success: true, message: response.data.message };
      }
      return { success: false, message: response.data.message || 'Đăng ký thất bại' };
    } catch (error) {
      console.error('Register error:', error);
      const msg = error.response?.data?.detail || 'Kết nối máy chủ thất bại';
      return { success: false, message: msg };
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('nomadai_user');
    
    // Clear and restore a fresh anonymous ID for guest use
    localStorage.removeItem('nomadai_user_id');
    getOrCreateUserId(); 
  }, []);

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      register,
      logout,
      isAuthenticated: !!user
    }}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
