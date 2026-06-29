import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Footer from '../components/Footer';
import './LoginPage.css';

function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [notFound, setNotFound] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('Vui lòng điền đầy đủ tên đăng nhập và mật khẩu.');
      return;
    }

    setSubmitting(true);
    setError('');
    setNotFound(false);

    const res = await login(username, password);
    setSubmitting(false);

    if (res.success) {
      navigate('/');
    } else {
      setError(res.message);
      // Nếu lỗi do tài khoản không tồn tại → gợi ý đăng ký
      if (res.message && res.message.toLowerCase().includes('không chính xác')) {
        setNotFound(true);
      }
    }
  };

  return (
    <div className="login-page flex items-center justify-center min-h-screen px-4 pb-12 pt-32">
      {/* Decorative Orbs */}
      <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-primary/5 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-[140px] pointer-events-none"></div>

      <div className="glass-login-card w-full max-w-md p-8 md:p-10 rounded-3xl border border-white/30 shadow-2xl relative z-10">
        <div className="text-center mb-8">
          <span className="text-4xl mb-3 inline-block">✈️</span>
          <h1 className="font-display-lg text-3xl font-bold text-primary">Đăng Nhập</h1>
          <p className="text-secondary text-xs mt-1">
            Chào mừng trở lại! Hãy đăng nhập để cá nhân hóa hành trình của bạn.
          </p>
        </div>

        {error && (
          <div className="error-alert p-4 mb-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-600 text-xs font-semibold text-left flex flex-col gap-2 animate-shake">
            <div className="flex items-start gap-2">
              <span className="material-symbols-outlined text-sm mt-0.5">error</span>
              <span>{error}</span>
            </div>
            {notFound && (
              <div className="pl-6 text-[11px] font-normal text-rose-500">
                Chưa có tài khoản?{' '}
                <Link to="/register" className="font-bold underline text-primary hover:opacity-80">
                  Đăng ký ngay miễn phí
                </Link>
              </div>
            )}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5 text-left">
          <div className="flex flex-col gap-2">
            <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
              Tên đăng nhập
            </label>
            <div className="relative">
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Tên đăng nhập của bạn"
                disabled={submitting}
                className="w-full bg-white/50 border border-pink-100/80 rounded-2xl py-3 pl-11 pr-4 text-sm text-on-surface focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-pink-300 transition-all font-body-md"
              />
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                person
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
              Mật khẩu
            </label>
            <div className="relative">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Mật khẩu bảo mật"
                disabled={submitting}
                className="w-full bg-white/50 border border-pink-100/80 rounded-2xl py-3 pl-11 pr-4 text-sm text-on-surface focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-pink-300 transition-all font-body-md"
              />
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                lock
              </span>
            </div>
            <div className="text-right pr-1">
              <Link to="/forgot-password" className="text-[11px] font-semibold text-primary hover:underline">
                Quên mật khẩu?
              </Link>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-4 mt-4 rounded-full font-bold text-xs uppercase tracking-widest text-white shadow-lg transition-all duration-300 hover:-translate-y-0.5 active:scale-98 flex items-center justify-center gap-1.5"
            style={{
              background: 'var(--grad-primary, linear-gradient(135deg, #c24482, #f4a4c6))'
            }}
          >
            {submitting ? (
              <span className="spinner-border animate-spin border-2 border-t-transparent border-white w-4 h-4 rounded-full"></span>
            ) : (
              <>
                <span className="material-symbols-outlined text-sm">login</span>
                Đăng Nhập
              </>
            )}
          </button>
        </form>

        <div className="text-center mt-8 pt-6 border-t border-pink-100/50">
          <p className="text-secondary text-xs">
            Bạn chưa có tài khoản?{' '}
            <Link to="/register" className="text-primary font-bold hover:underline">
              Đăng ký ngay
            </Link>
          </p>
        </div>
      </div>
      <Footer />
    </div>
  );
}

export default LoginPage;
