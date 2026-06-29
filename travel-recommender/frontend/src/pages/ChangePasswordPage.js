import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './ChangePasswordPage.css';

function ChangePasswordPage() {
  const navigate = useNavigate();
  const { user, isAuthenticated, changePassword } = useAuth();

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Redirect if not logged in
  if (!isAuthenticated) {
    return (
      <div className="change-pw-page flex items-center justify-center min-h-screen px-4">
        <div className="glass-change-pw-card w-full max-w-md p-8 rounded-3xl text-center">
          <span className="text-5xl mb-4 block">🔒</span>
          <h2 className="font-display-lg text-2xl font-bold text-primary mb-3">Yêu cầu đăng nhập</h2>
          <p className="text-secondary text-sm mb-6">Bạn cần đăng nhập để đổi mật khẩu.</p>
          <Link
            to="/login"
            className="inline-block py-3 px-8 rounded-full font-bold text-xs uppercase tracking-widest text-white shadow-lg transition-all hover:-translate-y-0.5"
            style={{ background: 'var(--grad-primary, linear-gradient(135deg, #c24482, #f4a4c6))' }}
          >
            Đăng Nhập
          </Link>
        </div>
      </div>
    );
  }

  // Password strength indicator
  const getStrength = (pwd) => {
    if (!pwd) return { level: 0, label: '', color: '' };
    let score = 0;
    if (pwd.length >= 6) score++;
    if (pwd.length >= 10) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^A-Za-z0-9]/.test(pwd)) score++;
    if (score <= 1) return { level: 1, label: 'Yếu', color: '#ef4444' };
    if (score <= 2) return { level: 2, label: 'Trung bình', color: '#f59e0b' };
    if (score <= 3) return { level: 3, label: 'Khá', color: '#3b82f6' };
    return { level: 4, label: 'Mạnh', color: '#22c55e' };
  };

  const strength = getStrength(newPassword);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!currentPassword || !newPassword || !confirmPassword) {
      setError('Vui lòng điền đầy đủ tất cả các trường.');
      return;
    }
    if (newPassword.length < 6) {
      setError('Mật khẩu mới phải có ít nhất 6 ký tự.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Xác nhận mật khẩu không khớp.');
      return;
    }
    if (newPassword === currentPassword) {
      setError('Mật khẩu mới phải khác mật khẩu hiện tại.');
      return;
    }

    setSubmitting(true);
    const res = await changePassword(user.username, currentPassword, newPassword);
    setSubmitting(false);

    if (res.success) {
      setSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } else {
      setError(res.message);
    }
  };

  return (
    <div className="change-pw-page flex items-center justify-center min-h-screen px-4 pb-12 pt-32">
      {/* Decorative blobs */}
      <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-primary/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-[140px] pointer-events-none" />

      <div className="glass-change-pw-card w-full max-w-md p-8 md:p-10 rounded-3xl border border-white/30 shadow-2xl relative z-10">
        {/* Header */}
        <div className="text-center mb-8">
          <span className="text-4xl mb-3 inline-block">🔐</span>
          <h1 className="font-display-lg text-3xl font-bold text-primary">Đổi Mật Khẩu</h1>
          <p className="text-secondary text-xs mt-1">
            Tài khoản: <span className="font-bold text-primary">{user.fullName}</span>
          </p>
        </div>

        {/* Success state */}
        {success && (
          <div className="success-banner p-4 mb-6 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm font-semibold text-center animate-fadein">
            <span className="text-2xl block mb-1">✅</span>
            Đổi mật khẩu thành công! Hãy dùng mật khẩu mới cho lần đăng nhập tiếp theo.
            <div className="mt-3">
              <button
                onClick={() => navigate('/')}
                className="text-xs underline text-emerald-600 hover:text-emerald-800"
              >
                Về trang chủ
              </button>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="error-alert p-4 mb-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-600 text-xs font-semibold flex items-start gap-2 animate-shake">
            <span className="material-symbols-outlined text-sm mt-0.5">error</span>
            <span>{error}</span>
          </div>
        )}

        {!success && (
          <form onSubmit={handleSubmit} className="space-y-5 text-left">
            {/* Current password */}
            <div className="flex flex-col gap-2">
              <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
                Mật khẩu hiện tại
              </label>
              <div className="relative">
                <input
                  type={showCurrent ? 'text' : 'password'}
                  id="current-password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="Nhập mật khẩu hiện tại"
                  disabled={submitting}
                  className="w-full bg-white/50 border border-pink-100/80 rounded-2xl py-3 pl-11 pr-11 text-sm text-on-surface focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-pink-300 transition-all font-body-md"
                />
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                  lock
                </span>
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowCurrent(!showCurrent)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-secondary hover:text-primary transition-colors"
                >
                  <span className="material-symbols-outlined text-sm">
                    {showCurrent ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
            </div>

            {/* New password */}
            <div className="flex flex-col gap-2">
              <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
                Mật khẩu mới
              </label>
              <div className="relative">
                <input
                  type={showNew ? 'text' : 'password'}
                  id="new-password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Ít nhất 6 ký tự"
                  disabled={submitting}
                  className="w-full bg-white/50 border border-pink-100/80 rounded-2xl py-3 pl-11 pr-11 text-sm text-on-surface focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-pink-300 transition-all font-body-md"
                />
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                  lock_open
                </span>
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowNew(!showNew)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-secondary hover:text-primary transition-colors"
                >
                  <span className="material-symbols-outlined text-sm">
                    {showNew ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>

              {/* Strength bar */}
              {newPassword && (
                <div className="flex items-center gap-2 mt-1 px-1">
                  <div className="flex gap-1 flex-1">
                    {[1, 2, 3, 4].map((i) => (
                      <div
                        key={i}
                        className="h-1.5 flex-1 rounded-full transition-all duration-300"
                        style={{
                          backgroundColor: i <= strength.level ? strength.color : '#e5e7eb',
                        }}
                      />
                    ))}
                  </div>
                  <span className="text-[10px] font-bold" style={{ color: strength.color }}>
                    {strength.label}
                  </span>
                </div>
              )}
            </div>

            {/* Confirm password */}
            <div className="flex flex-col gap-2">
              <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
                Xác nhận mật khẩu mới
              </label>
              <div className="relative">
                <input
                  type={showConfirm ? 'text' : 'password'}
                  id="confirm-password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Nhập lại mật khẩu mới"
                  disabled={submitting}
                  className={`w-full bg-white/50 border rounded-2xl py-3 pl-11 pr-11 text-sm text-on-surface focus:outline-none focus:ring-2 transition-all font-body-md ${
                    confirmPassword && confirmPassword !== newPassword
                      ? 'border-rose-300 focus:ring-rose-200'
                      : 'border-pink-100/80 focus:border-primary-container focus:ring-pink-300'
                  }`}
                />
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                  check_circle
                </span>
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowConfirm(!showConfirm)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-secondary hover:text-primary transition-colors"
                >
                  <span className="material-symbols-outlined text-sm">
                    {showConfirm ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
              {confirmPassword && confirmPassword !== newPassword && (
                <p className="text-[10px] text-rose-500 pl-1">Mật khẩu xác nhận chưa khớp</p>
              )}
              {confirmPassword && confirmPassword === newPassword && newPassword && (
                <p className="text-[10px] text-emerald-500 pl-1 flex items-center gap-1">
                  <span className="material-symbols-outlined" style={{ fontSize: 12 }}>check</span>
                  Mật khẩu khớp
                </p>
              )}
            </div>

            <button
              type="submit"
              id="change-password-submit"
              disabled={submitting}
              className="w-full py-4 mt-4 rounded-full font-bold text-xs uppercase tracking-widest text-white shadow-lg transition-all duration-300 hover:-translate-y-0.5 active:scale-98 flex items-center justify-center gap-1.5"
              style={{
                background: 'var(--grad-primary, linear-gradient(135deg, #c24482, #f4a4c6))',
              }}
            >
              {submitting ? (
                <span className="spinner-border animate-spin border-2 border-t-transparent border-white w-4 h-4 rounded-full" />
              ) : (
                <>
                  <span className="material-symbols-outlined text-sm">key</span>
                  Đổi Mật Khẩu
                </>
              )}
            </button>
          </form>
        )}

        <div className="text-center mt-6 pt-5 border-t border-pink-100/50">
          <Link to="/" className="text-secondary text-xs hover:text-primary transition-colors">
            ← Quay về trang chủ
          </Link>
        </div>
      </div>
    </div>
  );
}

export default ChangePasswordPage;
