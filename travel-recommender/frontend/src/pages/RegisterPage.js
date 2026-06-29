import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Footer from '../components/Footer';
import './RegisterPage.css';

function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
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
    if (!username.trim() || !password.trim() || !fullName.trim() || !email.trim()) {
      setError('Vui lòng điền đầy đủ các thông tin bắt buộc.');
      return;
    }

    if (!validateEmail(email.trim())) {
      setError('Email không đúng định dạng.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Mật khẩu nhập lại không khớp.');
      return;
    }

    if (password.length < 4) {
      setError('Mật khẩu phải chứa ít nhất 4 ký tự.');
      return;
    }

    setSubmitting(true);
    setError('');
    setSuccess('');

    const res = await register(username.trim(), password, fullName.trim(), email.trim().toLowerCase());
    setSubmitting(false);

    if (res.success) {
      setSuccess('Đăng ký tài khoản thành công! Đang chuyển hướng...');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } else {
      setError(res.message);
    }
  };

  return (
    <div className="register-page flex items-center justify-center min-h-screen px-4 pb-12 pt-32">
      {/* Decorative Orbs */}
      <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-primary/5 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-[140px] pointer-events-none"></div>

      <div className="glass-register-card w-full max-w-md p-8 md:p-10 rounded-3xl border border-white/30 shadow-2xl relative z-10">
        <div className="text-center mb-8">
          <span className="text-4xl mb-3 inline-block">✨</span>
          <h1 className="font-display-lg text-3xl font-bold text-primary">Đăng Ký</h1>
          <p className="text-secondary text-xs mt-1">
            Tạo tài khoản mới để lưu lịch sử và nhận gợi ý cá nhân hóa tốt hơn.
          </p>
        </div>

        {error && (
          <div className="error-alert p-4 mb-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-600 text-xs font-semibold text-left flex items-start gap-2 animate-shake">
            <span className="material-symbols-outlined text-sm mt-0.5">error</span>
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="success-alert p-4 mb-6 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-600 text-xs font-semibold text-left flex items-start gap-2">
            <span className="material-symbols-outlined text-sm mt-0.5">check_circle</span>
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-left">
          <div className="flex flex-col gap-2">
            <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
              Tên đầy đủ *
            </label>
            <div className="relative">
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Ví dụ: Thạch Thị Xuân Linh"
                disabled={submitting}
                className="w-full bg-white/50 border border-pink-100/80 rounded-2xl py-3 pl-11 pr-4 text-sm text-on-surface focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-pink-300 transition-all font-body-md"
              />
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                badge
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
              Email *
            </label>
            <div className="relative">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Ví dụ: email@domain.com"
                disabled={submitting}
                className="w-full bg-white/50 border border-pink-100/80 rounded-2xl py-3 pl-11 pr-4 text-sm text-on-surface focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-pink-300 transition-all font-body-md"
              />
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                mail
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
              Tên đăng nhập *
            </label>
            <div className="relative">
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Tên đăng nhập viết liền"
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
              Mật khẩu *
            </label>
            <div className="relative">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Tối thiểu 4 ký tự"
                disabled={submitting}
                className="w-full bg-white/50 border border-pink-100/80 rounded-2xl py-3 pl-11 pr-4 text-sm text-on-surface focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-pink-300 transition-all font-body-md"
              />
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                lock
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-[10px] font-bold text-primary uppercase tracking-widest pl-1">
              Nhập lại mật khẩu *
            </label>
            <div className="relative">
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Xác nhận mật khẩu"
                disabled={submitting}
                className="w-full bg-white/50 border border-pink-100/80 rounded-2xl py-3 pl-11 pr-4 text-sm text-on-surface focus:outline-none focus:border-primary-container focus:ring-2 focus:ring-pink-300 transition-all font-body-md"
              />
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-sm">
                lock_reset
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
                <span className="material-symbols-outlined text-sm">how_to_reg</span>
                Đăng Ký Tài Khoản
              </>
            )}
          </button>
        </form>

        <div className="text-center mt-8 pt-6 border-t border-pink-100/50">
          <p className="text-secondary text-xs">
            Bạn đã có tài khoản?{' '}
            <Link to="/login" className="text-primary font-bold hover:underline">
              Đăng nhập tại đây
            </Link>
          </p>
        </div>
      </div>
      <Footer />
    </div>
  );
}

export default RegisterPage;
