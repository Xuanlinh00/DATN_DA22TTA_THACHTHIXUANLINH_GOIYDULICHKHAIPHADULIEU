import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authApi } from '../services/api';
import Footer from '../components/Footer';
import './ForgotPasswordPage.css';

function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [successData, setSuccessData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const validateEmail = (val) =>
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val.trim());

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setError('Vui long nhap email.');
      return;
    }
    if (!validateEmail(email)) {
      setError('Email khong dung dinh dang.');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccessData(null);

    try {
      const res = await authApi.forgotPassword(email.trim().toLowerCase());
      setIsLoading(false);
      if (res.data.success) {
        setSuccessData({
          message:        res.data.message,
          emailConfigured: res.data.email_configured,
          devResetLink:   res.data.dev_reset_link || null,
        });
      } else {
        setError(res.data.message || 'Gui yeu cau that bai. Vui long thu lai.');
      }
    } catch (err) {
      setIsLoading(false);
      const msg = err.response?.data?.detail || 'Ket noi may chu that bai.';
      setError(msg);
    }
  };

  // Lay raw token tu dev reset link: http://localhost:3000/reset-password/{token}
  const handleDevNavigate = () => {
    if (!successData?.devResetLink) return;
    const parts = successData.devResetLink.split('/reset-password/');
    const rawToken = parts[1] || '';
    navigate(`/reset-password/${rawToken}`);
  };

  return (
    <div className="forgot-password-page flex items-center justify-center min-h-screen px-4 pb-12 pt-32">
      {/* Decorative orbs */}
      <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-primary/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-[140px] pointer-events-none" />

      <div className="glass-forgot-card w-full max-w-md p-8 md:p-10 rounded-3xl border border-white/30 shadow-2xl relative z-10">

        <div className="text-center mb-8">
          <span className="text-4xl mb-3 inline-block">🔒</span>
          <h1 className="font-display-lg text-3xl font-bold text-primary">Quen Mat Khau</h1>
          <p className="text-secondary text-xs mt-1">
            Nhap email va chung toi se gui lien ket de khoi phuc mat khau.
          </p>
        </div>

        {/* Error */}
        {error && (
          <div className="error-alert p-4 mb-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-600 text-xs font-semibold flex items-start gap-2 animate-shake">
            <span className="material-symbols-outlined text-sm mt-0.5">error</span>
            <span>{error}</span>
          </div>
        )}

        {/* ── SUCCESS STATE ── */}
        {successData ? (
          <div className="text-center py-2 animate-fade-in">

            {successData.emailConfigured ? (
              /* Email da gui that */
              <>
                <div className="mb-4 inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-500">
                  <span className="material-symbols-outlined text-3xl">mark_email_read</span>
                </div>
                <h3 className="font-bold text-emerald-600 text-sm mb-2">Email da duoc gui!</h3>
                <p className="text-secondary text-xs mb-6 px-2">
                  {successData.message} Vui long kiem tra hop thu den (va thu rac) de hoan tat viec dat lai mat khau.
                </p>
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-left text-[10px] text-blue-700 mb-5">
                  <p className="font-bold mb-1">Khong thay email?</p>
                  <ol className="list-decimal pl-4 space-y-0.5 leading-relaxed">
                    <li>Kiem tra thu muc <strong>Thu rac / Spam</strong></li>
                    <li>Link het han sau <strong>10 phut</strong> – yeu cau lai neu can</li>
                    <li>Kiem tra lai dia chi email da nhap</li>
                  </ol>
                </div>
                <Link
                  to="/login"
                  className="inline-flex items-center justify-center px-6 py-2.5 rounded-full text-xs font-bold uppercase tracking-widest text-white transition-all shadow-md hover:-translate-y-0.5"
                  style={{ background: 'var(--grad-primary, linear-gradient(135deg, #c24482, #f4a4c6))' }}
                >
                  Quay lai dang nhap
                </Link>
              </>
            ) : (
              /* Email chua cau hinh - hien thi dev link */
              <>
                <div className="mb-4 inline-flex items-center justify-center w-16 h-16 rounded-full bg-amber-50 border border-amber-200 text-amber-500">
                  <span className="material-symbols-outlined text-3xl">warning</span>
                </div>
                <h3 className="font-bold text-amber-600 text-sm mb-2">Email chua duoc cau hinh</h3>
                <p className="text-secondary text-xs mb-4 px-2">
                  Email that chua duoc gui vi chua cau hinh EMAIL_USER/EMAIL_PASS trong .env.
                  Ban co the dung link duoi day de dat lai mat khau ngay:
                </p>

                {successData.devResetLink && (
                  <div className="mb-4">
                    <button
                      onClick={handleDevNavigate}
                      className="w-full py-3 px-4 rounded-full font-bold text-xs uppercase tracking-widest text-white shadow-lg transition-all hover:-translate-y-0.5 flex items-center justify-center gap-1.5"
                      style={{ background: 'var(--grad-primary, linear-gradient(135deg, #c24482, #f4a4c6))' }}
                    >
                      <span className="material-symbols-outlined text-sm">lock_reset</span>
                      Dat lai mat khau ngay
                    </button>

                    <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-xl text-left">
                      <p className="text-[10px] text-amber-700 font-bold uppercase tracking-widest mb-1">
                        Link dat lai (dev only):
                      </p>
                      <p className="text-[10px] text-amber-800 break-all font-mono leading-relaxed">
                        {successData.devResetLink}
                      </p>
                      <button
                        onClick={() => navigator.clipboard?.writeText(successData.devResetLink)}
                        className="mt-2 text-[10px] text-amber-600 hover:text-amber-800 flex items-center gap-1 font-semibold transition-colors"
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 12 }}>content_copy</span>
                        Sao chep link
                      </button>
                    </div>
                  </div>
                )}

                <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-left text-[10px] text-blue-700">
                  <p className="font-bold mb-1">Cau hinh email that:</p>
                  <ol className="list-decimal pl-4 space-y-1 leading-relaxed">
                    <li>Mo <strong>.env</strong> trong thu muc goc du an</li>
                    <li>Dieu chinh: <code className="bg-blue-100 px-1 rounded">EMAIL_USER</code> va <code className="bg-blue-100 px-1 rounded">EMAIL_PASS</code></li>
                    <li>Gmail: tao <strong>App Password</strong> tai myaccount.google.com</li>
                    <li>Khoi dong lai backend</li>
                  </ol>
                </div>
              </>
            )}
          </div>
        ) : (
          /* ── FORM STATE ── */
          <form onSubmit={handleSubmit} className="space-y-5 text-left">
            <div className="flex flex-col gap-2">
              <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
                Dia chi Email
              </label>
              <div className="relative">
                <input
                  type="email"
                  id="forgot-email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Vi du: ban@gmail.com"
                  disabled={isLoading}
                  className="w-full bg-white/50 border border-pink-100/80 rounded-2xl py-3 pl-11 pr-4 text-sm text-on-surface focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-pink-300 transition-all font-body-md"
                />
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                  mail
                </span>
              </div>
            </div>

            <button
              type="submit"
              id="forgot-submit"
              disabled={isLoading}
              className="w-full py-4 mt-4 rounded-full font-bold text-xs uppercase tracking-widest text-white shadow-lg transition-all duration-300 hover:-translate-y-0.5 disabled:opacity-60 flex items-center justify-center gap-1.5"
              style={{ background: 'var(--grad-primary, linear-gradient(135deg, #c24482, #f4a4c6))' }}
            >
              {isLoading ? (
                <span className="spinner-border animate-spin border-2 border-t-transparent border-white w-4 h-4 rounded-full" />
              ) : (
                <>
                  <span className="material-symbols-outlined text-sm">send</span>
                  Gui yeu cau dat lai
                </>
              )}
            </button>
          </form>
        )}

        {!successData && (
          <div className="text-center mt-8 pt-6 border-t border-pink-100/50">
            <Link to="/login" className="text-primary font-bold text-xs hover:underline flex items-center justify-center gap-1">
              <span className="material-symbols-outlined text-xs">arrow_back</span>
              Quay lai dang nhap
            </Link>
          </div>
        )}
      </div>
      <Footer />
    </div>
  );
}

export default ForgotPasswordPage;
