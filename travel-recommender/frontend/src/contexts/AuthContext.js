import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi, getOrCreateUserId } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize Auth state from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem('Nâu_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        localStorage.removeItem('Nâu_user');
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
        localStorage.setItem('Nâu_user', JSON.stringify(userData));
        localStorage.setItem('Nâu_user_id', userData.username); // Link CF/Ratings to username
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
    localStorage.removeItem('Nâu_user');
    
    // Clear and restore a fresh anonymous ID for guest use
    localStorage.removeItem('Nâu_user_id');
    getOrCreateUserId(); 
  }, []);

  const changePassword = useCallback(async (username, currentPassword, newPassword) => {
    try {
      const response = await authApi.changePassword(username, currentPassword, newPassword);
      if (response.data.success) {
        return { success: true, message: response.data.message };
      }
      return { success: false, message: response.data.message || 'Đổi mật khẩu thất bại' };
    } catch (error) {
      console.error('Change password error:', error);
      const msg = error.response?.data?.detail || 'Kết nối máy chủ thất bại';
      return { success: false, message: msg };
    }
  }, []);

  const updatePreferences = useCallback(async (preferences) => {
    if (!user?.username) {
      return { success: false, message: 'NgÆ°á»i dÃ¹ng chÆ°a Ä‘Äƒng nháº­p' };
    }

    try {
      const response = await authApi.updatePreferences(user.username, preferences);
      if (response.data.success) {
        const userData = response.data.user;
        setUser(userData);
        localStorage.setItem('Nâu_user', JSON.stringify(userData));
        return { success: true, message: response.data.message };
      }
      return { success: false, message: response.data.message || 'Cáº­p nháº­t sá»Ÿ thÃ­ch tháº¥t báº¡i' };
    } catch (error) {
      console.error('Update preferences error:', error);
      const msg = error.response?.data?.detail || 'Káº¿t ná»‘i mÃ¡y chá»§ tháº¥t báº¡i';
      return { success: false, message: msg };
    }
  }, [user]);

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      login,
      register,
      logout,
      changePassword,
      updatePreferences,
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
