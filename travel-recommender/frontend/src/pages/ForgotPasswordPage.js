import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authApi } from '../services/api';
import './ForgotPasswordPage.css';

function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const validateEmail = (emailVal) => {
    return String(emailVal)
      .toLowerCase()
      .match(
        /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setError('Vui lòng điền địa chỉ email của bạn.');
      return;
    }

    if (!validateEmail(email.trim())) {
      setError('Email không đúng định dạng.');
      return;
    }

    setSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const res = await authApi.forgotPassword(email.trim().toLowerCase());
      setSubmitting(false);
      if (res.data.success) {
        setSuccess(res.data.message || 'Liên kết đặt lại mật khẩu đã được gửi đến email của bạn.');
      } else {
        setError(res.data.message || 'Gửi yêu cầu thất bại. Vui lòng thử lại.');
      }
    } catch (err) {
      setSubmitting(false);
      console.error('Forgot password error:', err);
      const msg = err.response?.data?.detail || 'Kết nối máy chủ thất bại';
      setError(msg);
    }
  };

  return (
    <div className="forgot-password-page flex items-center justify-center min-h-screen px-4 pb-12 pt-32">
      {/* Decorative Orbs */}
      <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-primary/5 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-[140px] pointer-events-none"></div>

      <div className="glass-forgot-card w-full max-w-md p-8 md:p-10 rounded-3xl border border-white/30 shadow-2xl relative z-10">
        <div className="text-center mb-8">
          <span className="text-4xl mb-3 inline-block">🔒</span>
          <h1 className="font-display-lg text-3xl font-bold text-primary">Quên Mật Khẩu</h1>
          <p className="text-secondary text-xs mt-1">
            Nhập email của bạn và chúng tôi sẽ gửi liên kết để khôi phục mật khẩu.
          </p>
        </div>

        {error && (
          <div className="error-alert p-4 mb-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-600 text-xs font-semibold text-left flex items-start gap-2 animate-shake">
            <span className="material-symbols-outlined text-sm mt-0.5">error</span>
            <span>{error}</span>
          </div>
        )}

        {success ? (
          <div className="text-center py-6 animate-fade-in">
            <div className="mb-4 inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-500">
              <span className="material-symbols-outlined text-3xl">mark_email_read</span>
            </div>
            <h3 className="font-bold text-emerald-600 text-sm mb-2">Thành công!</h3>
            <p className="text-secondary text-xs mb-8 px-2">
              {success} Vui lòng kiểm tra hộp thư đến (và thư rác) để hoàn tất việc đặt lại mật khẩu.
            </p>
            <Link
              to="/login"
              className="inline-flex items-center justify-center px-6 py-2.5 rounded-full text-xs font-bold uppercase tracking-widest text-white transition-all shadow-md hover:-translate-y-0.5"
              style={{
                background: 'var(--grad-primary, linear-gradient(135deg, #c24482, #f4a4c6))'
              }}
            >
              Quay lại đăng nhập
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5 text-left">
            <div className="flex flex-col gap-2">
              <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
                Địa chỉ Email
              </label>
              <div className="relative">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Ví dụ: ban@gmail.com"
                  disabled={submitting}
                  className="w-full bg-white/50 border border-pink-100/80 rounded-2xl py-3 pl-11 pr-4 text-sm text-on-surface focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-pink-300 transition-all font-body-md"
                />
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                  mail
                </span>
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
                  <span className="material-symbols-outlined text-sm">send</span>
                  Gửi yêu cầu đặt lại
                </>
              )}
            </button>
          </form>
        )}

        {!success && (
          <div className="text-center mt-8 pt-6 border-t border-pink-100/50">
            <p className="text-secondary text-xs">
              <Link to="/login" className="text-primary font-bold hover:underline flex items-center justify-center gap-1">
                <span className="material-symbols-outlined text-xs">arrow_back</span>
                Quay lại đăng nhập
              </Link>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ForgotPasswordPage;
