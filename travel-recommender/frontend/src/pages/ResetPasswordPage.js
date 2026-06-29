import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { authApi } from '../services/api';
import './ResetPasswordPage.css';

function ResetPasswordPage() {
  const navigate = useNavigate();
  const { token } = useParams(); // Token lay tu URL path: /reset-password/:token

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');

  // Kiem tra token co trong URL khong
  useEffect(() => {
    if (!token) {
      setError('Lien ket dat lai mat khau khong hop le hoac thieu token.');
    }
  }, [token]);

  // ── Password strength ──────────────────────────────────────────
  const getStrength = (pwd) => {
    if (!pwd) return { level: 0, label: '', color: '' };
    let score = 0;
    if (pwd.length >= 6)  score++;
    if (pwd.length >= 10) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^A-Za-z0-9]/.test(pwd)) score++;
    if (score <= 1) return { level: 1, label: 'Yeu', color: '#ef4444' };
    if (score <= 2) return { level: 2, label: 'Trung binh', color: '#f59e0b' };
    if (score <= 3) return { level: 3, label: 'Kha', color: '#3b82f6' };
    return { level: 4, label: 'Manh', color: '#22c55e' };
  };
  const strength = getStrength(password);

  // Realtime validation
  const validLength  = password.length >= 6;
  const validMatch   = confirmPassword !== '' && password === confirmPassword;
  const mismatch     = confirmPassword !== '' && password !== confirmPassword;

  // ── Submit ─────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!token) {
      setError('Token khong hop le.');
      return;
    }
    if (!password || !confirmPassword) {
      setError('Vui long nhap day du mat khau.');
      return;
    }
    if (password.length < 6) {
      setError('Mat khau phai co it nhat 6 ky tu.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Mat khau khong khop.');
      return;
    }

    setIsLoading(true);
    try {
      const res = await authApi.resetPassword(token, password);
      setIsLoading(false);
      if (res.data.success) {
        setIsSuccess(true);
        // Tu dong chuyen ve login sau 2 giay
        setTimeout(() => navigate('/login'), 2000);
      } else {
        setError(res.data.message || 'Dat lai mat khau that bai.');
      }
    } catch (err) {
      setIsLoading(false);
      const msg = err.response?.data?.detail || 'Dat lai mat khau that bai. Ma xac nhan co the da het han.';
      setError(msg);
    }
  };

  return (
    <div className="reset-password-page flex items-center justify-center min-h-screen px-4 pb-12 pt-32">
      {/* Decorative blobs */}
      <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-primary/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-[140px] pointer-events-none" />

      <div className="glass-reset-card w-full max-w-md p-8 md:p-10 rounded-3xl border border-white/30 shadow-2xl relative z-10">

        {/* ── SUCCESS STATE ── */}
        {isSuccess ? (
          <div className="text-center py-6 animate-fade-in">
            <div className="mb-4 inline-flex items-center justify-center w-20 h-20 rounded-full bg-emerald-50 border-2 border-emerald-200 text-emerald-500">
              <span className="material-symbols-outlined" style={{ fontSize: 40 }}>check_circle</span>
            </div>
            <h2 className="font-bold text-emerald-600 text-xl mb-2">Thanh cong!</h2>
            <p className="text-secondary text-sm mb-6 px-2">
              Mat khau cua ban da duoc dat lai thanh cong.<br />
              Dang chuyen ve trang dang nhap...
            </p>
            <div className="flex justify-center">
              <span className="inline-flex gap-1">
                {[0,1,2].map(i => (
                  <span
                    key={i}
                    className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }}
                  />
                ))}
              </span>
            </div>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="text-center mb-8">
              <span className="text-4xl mb-3 inline-block">🔄</span>
              <h1 className="font-display-lg text-3xl font-bold text-primary">Dat Lai Mat Khau</h1>
              <p className="text-secondary text-xs mt-1">Nhap mat khau moi de hoan tat.</p>
            </div>

            {/* Error */}
            {error && (
              <div className="error-alert p-4 mb-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-600 text-xs font-semibold flex items-start gap-2 animate-shake">
                <span className="material-symbols-outlined text-sm mt-0.5">error</span>
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5 text-left">

              {/* Mat khau moi */}
              <div className="flex flex-col gap-2">
                <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
                  Mat khau moi
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="new-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="It nhat 6 ky tu"
                    disabled={isLoading || !token}
                    className="w-full bg-white/50 border border-pink-100/80 rounded-2xl py-3 pl-11 pr-11 text-sm text-on-surface focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-pink-300 transition-all font-body-md"
                  />
                  <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                    lock
                  </span>
                  <button
                    type="button"
                    tabIndex={-1}
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-secondary hover:text-primary transition-colors"
                  >
                    <span className="material-symbols-outlined text-sm">
                      {showPassword ? 'visibility_off' : 'visibility'}
                    </span>
                  </button>
                </div>

                {/* Strength bar */}
                {password && (
                  <div className="flex items-center gap-2 mt-1 px-1">
                    <div className="flex gap-1 flex-1">
                      {[1,2,3,4].map(i => (
                        <div
                          key={i}
                          className="h-1.5 flex-1 rounded-full transition-all duration-300"
                          style={{ backgroundColor: i <= strength.level ? strength.color : '#e5e7eb' }}
                        />
                      ))}
                    </div>
                    <span className="text-[10px] font-bold" style={{ color: strength.color }}>
                      {strength.label}
                    </span>
                  </div>
                )}

                {/* Validation hints */}
                <div className="flex items-center gap-1.5 pl-1 mt-0.5">
                  <span
                    className="material-symbols-outlined"
                    style={{ fontSize: 13, color: validLength ? '#22c55e' : '#d1d5db' }}
                  >
                    {validLength ? 'check_circle' : 'radio_button_unchecked'}
                  </span>
                  <span className={`text-[10px] ${validLength ? 'text-emerald-600' : 'text-gray-400'}`}>
                    It nhat 6 ky tu
                  </span>
                </div>
              </div>

              {/* Xac nhan mat khau */}
              <div className="flex flex-col gap-2">
                <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
                  Xac nhan mat khau
                </label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    id="confirm-password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Nhap lai mat khau moi"
                    disabled={isLoading || !token}
                    className={`w-full bg-white/50 border rounded-2xl py-3 pl-11 pr-11 text-sm text-on-surface focus:outline-none focus:ring-2 transition-all font-body-md ${
                      mismatch
                        ? 'border-rose-300 focus:ring-rose-200'
                        : 'border-pink-100/80 focus:border-primary-container focus:ring-pink-300'
                    }`}
                  />
                  <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                    lock_reset
                  </span>
                  <button
                    type="button"
                    tabIndex={-1}
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-secondary hover:text-primary transition-colors"
                  >
                    <span className="material-symbols-outlined text-sm">
                      {showConfirmPassword ? 'visibility_off' : 'visibility'}
                    </span>
                  </button>
                </div>

                {/* Match indicator */}
                {confirmPassword && (
                  <div className="flex items-center gap-1.5 pl-1">
                    <span
                      className="material-symbols-outlined"
                      style={{ fontSize: 13, color: validMatch ? '#22c55e' : '#ef4444' }}
                    >
                      {validMatch ? 'check_circle' : 'cancel'}
                    </span>
                    <span className={`text-[10px] font-medium ${validMatch ? 'text-emerald-600' : 'text-rose-500'}`}>
                      {validMatch ? 'Mat khau khop' : 'Mat khau chua khop'}
                    </span>
                  </div>
                )}
              </div>

              <button
                type="submit"
                id="reset-password-submit"
                disabled={isLoading || !token}
                className="w-full py-4 mt-4 rounded-full font-bold text-xs uppercase tracking-widest text-white shadow-lg transition-all duration-300 hover:-translate-y-0.5 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-1.5"
                style={{ background: 'var(--grad-primary, linear-gradient(135deg, #c24482, #f4a4c6))' }}
              >
                {isLoading ? (
                  <span className="spinner-border animate-spin border-2 border-t-transparent border-white w-4 h-4 rounded-full" />
                ) : (
                  <>
                    <span className="material-symbols-outlined text-sm">lock_open</span>
                    Dong y & Doi mat khau
                  </>
                )}
              </button>
            </form>

            <div className="text-center mt-8 pt-6 border-t border-pink-100/50">
              <Link to="/login" className="text-primary font-bold text-xs hover:underline flex items-center justify-center gap-1">
                <span className="material-symbols-outlined text-xs">arrow_back</span>
                Quay lai dang nhap
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default ResetPasswordPage;
