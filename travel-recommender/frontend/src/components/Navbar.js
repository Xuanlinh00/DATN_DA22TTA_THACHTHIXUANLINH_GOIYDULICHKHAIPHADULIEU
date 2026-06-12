import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  const isActive = (path) => location.pathname === path;

  return (
    <nav className={`navbar-custom ${scrolled ? 'scrolled' : ''}`}>
      {/* Brand Logo */}
      <Link to="/" className="navbar-logo-custom">
        Trợ lý du lịch
      </Link>

      {/* Desktop Menu links (hidden on mobile via CSS class desktop-only) */}
      <div className="navbar-links-custom desktop-only">
        <Link 
          className={`navbar-link-custom ${isActive('/') ? 'active' : ''}`} 
          to="/"
        >
          Khám Phá
        </Link>
        <Link 
          className={`navbar-link-custom ${isActive('/destinations') ? 'active' : ''}`} 
          to="/destinations"
        >
          Điểm Đến
        </Link>
        <Link 
          className={`navbar-link-custom ${isActive('/recommend') ? 'active' : ''}`} 
          to="/recommend"
        >
          ✨ Gợi Ý
        </Link>
        <Link 
          className={`navbar-link-custom ${isActive('/admin') ? 'active' : ''}`} 
          to="/admin"
        >
          ⚙️ Quản Trị
        </Link>
      </div>

      {/* Action / Mobile Toggle button */}
      <div className="flex items-center gap-4">
        {isAuthenticated ? (
          <div className="flex items-center gap-3">
            <span className="hidden lg:inline-block text-xs font-semibold text-secondary">
              Chào {user.fullName} ✨
            </span>
            <button 
              onClick={logout}
              className="text-[10px] uppercase font-bold tracking-wider text-primary border border-pink-200 bg-white/40 hover:bg-white px-3.5 py-2 rounded-full transition-all flex items-center gap-1 cursor-pointer"
            >
              <span className="material-symbols-outlined text-xs">logout</span>
              Thoát
            </button>
          </div>
        ) : (
          <Link 
            to="/login"
            className="text-[10px] uppercase font-bold tracking-wider text-white shadow-md px-4 py-2.5 rounded-full transition-all flex items-center gap-1"
            style={{ background: 'var(--grad-primary, linear-gradient(135deg,#c24482,#f4a4c6))' }}
          >
            <span className="material-symbols-outlined text-xs">login</span>
            Đăng Nhập
          </Link>
        )}
        
        <button 
          className="mobile-only material-symbols-outlined text-[#c24482] text-2xl flex items-center justify-center p-1"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? 'close' : 'menu'}
        </button>
      </div>

      {/* Mobile Menu Dropdown (shows up on mobile only) */}
      {menuOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 p-6 navbar-mobile-menu flex flex-col gap-4 shadow-xl mobile-only z-50">
          <Link 
            className={`font-body-lg text-body-md py-2 px-4 rounded-xl transition-all ${
              isActive('/') 
                ? 'navbar-mobile-active font-bold' 
                : 'text-on-surface-variant hover:bg-secondary-container/20'
            }`} 
            to="/"
          >
            Khám Phá
          </Link>
          <Link 
            className={`font-body-lg text-body-md py-2 px-4 rounded-xl transition-all ${
              isActive('/destinations') 
                ? 'navbar-mobile-active font-bold' 
                : 'text-on-surface-variant hover:bg-secondary-container/20'
            }`} 
            to="/destinations"
          >
            Điểm Đến
          </Link>
          <Link 
            className={`font-body-lg text-body-md py-2 px-4 rounded-xl transition-all ${
              isActive('/recommend') 
                ? 'navbar-mobile-active font-bold' 
                : 'text-on-surface-variant hover:bg-secondary-container/20'
            }`} 
            to="/recommend"
          >
            ✨ Gợi Ý
          </Link>
          <Link 
            className={`font-body-lg text-body-md py-2 px-4 rounded-xl transition-all ${
              isActive('/admin') 
                ? 'navbar-mobile-active font-bold' 
                : 'text-on-surface-variant hover:bg-secondary-container/20'
            }`} 
            to="/admin"
          >
            ⚙️ Quản Trị
          </Link>
        </div>
      )}
    </nav>
  );
}

export default Navbar;
