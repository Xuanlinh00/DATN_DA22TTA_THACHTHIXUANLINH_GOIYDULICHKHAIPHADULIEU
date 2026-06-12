import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { authApi } from '../services/api';
import './ResetPasswordPage.css';

function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const emailParam = searchParams.get('email') || '';
  const tokenParam = searchParams.get('token') || '';

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!emailParam || !tokenParam) {
      setError('Liên kết đặt lại mật khẩu không hợp lệ hoặc thiếu thông tin cần thiết.');
    }
  }, [emailParam, tokenParam]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!emailParam || !tokenParam) {
      setError('Không thể tiếp tục vì liên kết thiếu thông tin xác thực.');
      return;
    }

    if (!password.trim() || !confirmPassword.trim()) {
      setError('Vui lòng điền đầy đủ mật khẩu mới.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Mật khẩu xác nhận không khớp.');
      return;
    }

    if (password.length < 4) {
      setError('Mật khẩu phải chứa ít nhất 4 ký tự.');
      return;
    }

    setSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const res = await authApi.resetPassword(emailParam, tokenParam, password);
      setSubmitting(false);
      if (res.data.success) {
        setSuccess(res.data.message || 'Mật khẩu của bạn đã được đặt lại thành công!');
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } else {
        setError(res.data.message || 'Đặt lại mật khẩu thất bại.');
      }
    } catch (err) {
      setSubmitting(false);
      console.error('Reset password error:', err);
      const msg = err.response?.data?.detail || 'Đặt lại mật khẩu thất bại. Mã xác nhận có thể đã hết hạn.';
      setError(msg);
    }
  };

  return (
    <div className="reset-password-page flex items-center justify-center min-h-screen px-4 pb-12 pt-32">
      {/* Decorative Orbs */}
      <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-primary/5 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-[140px] pointer-events-none"></div>

      <div className="glass-reset-card w-full max-w-md p-8 md:p-10 rounded-3xl border border-white/30 shadow-2xl relative z-10">
        <div className="text-center mb-8">
          <span className="text-4xl mb-3 inline-block">🔄</span>
          <h1 className="font-display-lg text-3xl font-bold text-primary">Đặt Lại Mật Khẩu</h1>
          <p className="text-secondary text-xs mt-1">
            Vui lòng nhập mật khẩu mới của bạn bên dưới.
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
              <span className="material-symbols-outlined text-3xl">check_circle</span>
            </div>
            <h3 className="font-bold text-emerald-600 text-sm mb-2">Thành công!</h3>
            <p className="text-secondary text-xs mb-8 px-2">
              {success} Bạn sẽ được chuyển hướng về trang đăng nhập sau vài giây...
            </p>
            <Link
              to="/login"
              className="inline-flex items-center justify-center px-6 py-2.5 rounded-full text-xs font-bold uppercase tracking-widest text-white transition-all shadow-md hover:-translate-y-0.5"
              style={{
                background: 'var(--grad-primary, linear-gradient(135deg, #c24482, #f4a4c6))'
              }}
            >
              Đăng nhập ngay
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5 text-left">
            {/* Info Badge */}
            <div className="p-3 mb-4 rounded-xl bg-pink-50/50 border border-pink-100 text-[#c24482] text-[11px] font-medium flex items-center gap-2">
              <span className="material-symbols-outlined text-sm">account_circle</span>
              <span>Đang thiết lập cho: <strong>{emailParam || 'Không xác định'}</strong></span>
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
                Mật khẩu mới *
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Tối thiểu 4 ký tự"
                  disabled={submitting || !emailParam || !tokenParam}
                  className="w-full bg-white/50 border border-pink-100/80 rounded-2xl py-3 pl-11 pr-4 text-sm text-on-surface focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-pink-300 transition-all font-body-md"
                />
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                  lock
                </span>
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
                Xác nhận mật khẩu *
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Nhập lại mật khẩu mới"
                  disabled={submitting || !emailParam || !tokenParam}
                  className="w-full bg-white/50 border border-pink-100/80 rounded-2xl py-3 pl-11 pr-4 text-sm text-on-surface focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-pink-300 transition-all font-body-md"
                />
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                  lock_reset
                </span>
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting || !emailParam || !tokenParam}
              className="w-full py-4 mt-4 rounded-full font-bold text-xs uppercase tracking-widest text-white shadow-lg transition-all duration-300 hover:-translate-y-0.5 active:scale-98 flex items-center justify-center gap-1.5"
              style={{
                background: 'var(--grad-primary, linear-gradient(135deg, #c24482, #f4a4c6))'
              }}
            >
              {submitting ? (
                <span className="spinner-border animate-spin border-2 border-t-transparent border-white w-4 h-4 rounded-full"></span>
              ) : (
                <>
                  <span className="material-symbols-outlined text-sm">lock_open</span>
                  Đồng ý & Đổi mật khẩu
                </>
              )}
            </button>
          </form>
        )}

        <div className="text-center mt-8 pt-6 border-t border-pink-100/50">
          <p className="text-secondary text-xs">
            <Link to="/login" className="text-primary font-bold hover:underline">
              Quay lại trang Đăng nhập
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default ResetPasswordPage;
