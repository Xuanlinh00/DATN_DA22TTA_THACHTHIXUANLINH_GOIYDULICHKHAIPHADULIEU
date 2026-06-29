import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  useEffect(() => {
    const closeDropdown = () => setDropdownOpen(false);
    window.addEventListener('click', closeDropdown);
    return () => window.removeEventListener('click', closeDropdown);
  }, []);

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
        <img src="/img1.png" alt="Nâu Travel" className="nau-logo-img" />
      </Link>

      {/* Desktop Menu links (hidden on mobile via CSS class desktop-only) */}
      <div className="navbar-links-custom desktop-only">
        <Link
          className={`navbar-link-custom ${isActive('/') ? 'active' : ''}`}
          to="/"
        >
          Trang chủ 
        </Link>
        <Link
          className={`navbar-link-custom ${isActive('/destinations') ? 'active' : ''}`}
          to="/destinations"
        >
          Điểm Đến
        </Link>
        <Link
          className={`navbar-link-custom ${isActive('/map') ? 'active' : ''}`}
          to="/map"
        >
          Bản Đồ
        </Link>
        <Link
          className={`navbar-link-custom ${isActive('/recommend') ? 'active' : ''}`}
          to="/recommend"
        >
          Gợi Ý
        </Link>
      </div>

      {/* Action / Mobile Toggle button */}
      <div className="flex items-center gap-4">
        {/* Account Dropdown */}
        <div className="relative" onClick={(e) => e.stopPropagation()}>
          <button
            className="navbar-dropdown-btn"
            onClick={() => setDropdownOpen(!dropdownOpen)}
          >
            <span className="material-symbols-outlined text-xs" style={{ fontSize: 18 }}>account_circle</span>
            <span className="text-[12px] uppercase font-bold tracking-wider">
              {isAuthenticated ? user.fullName : "Tài khoản"}
            </span>
            <span className="material-symbols-outlined text-xs" style={{ fontSize: 18 }}>arrow_drop_down</span>
          </button>

          {dropdownOpen && (
            <div className="navbar-dropdown-menu">
              {isAuthenticated ? (
                <>
                  <Link to="/recommend" className="navbar-dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <span className="material-symbols-outlined text-xs" style={{ fontSize: 14 }}>auto_awesome</span>
                    Gợi Ý Của Tôi
                  </Link>
                  <Link to="/change-password" className="navbar-dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <span className="material-symbols-outlined text-xs" style={{ fontSize: 14 }}>key</span>
                    Đổi Mật Khẩu
                  </Link>
                  <Link to="/admin" className="navbar-dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <span className="material-symbols-outlined text-xs" style={{ fontSize: 14 }}>settings</span>
                    Thống Kê Hệ Thống
                  </Link>
                  <div className="navbar-dropdown-divider" />
                  <button
                    className="navbar-dropdown-item text-red-500"
                    onClick={() => {
                      setDropdownOpen(false);
                      logout();
                    }}
                  >
                    <span className="material-symbols-outlined text-xs" style={{ fontSize: 14, color: '#ef4444' }}>logout</span>
                    Đăng Xuất
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="navbar-dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <span className="material-symbols-outlined text-xs" style={{ fontSize: 14 }}>login</span>
                    Đăng Nhập
                  </Link>
                  <Link to="/register" className="navbar-dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <span className="material-symbols-outlined text-xs" style={{ fontSize: 14 }}>person_add</span>
                    Đăng Ký
                  </Link>
                  <Link to="/admin" className="navbar-dropdown-item" onClick={() => setDropdownOpen(false)}>
                    <span className="material-symbols-outlined text-xs" style={{ fontSize: 14 }}>settings</span>
                    Thống Kê Hệ Thống
                  </Link>
                </>
              )}
            </div>
          )}
        </div>

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
            className={`font-body-lg text-body-md py-2 px-4 rounded-xl transition-all ${isActive('/')
                ? 'navbar-mobile-active font-bold'
                : 'text-on-surface-variant hover:bg-secondary-container/20'
              }`}
            to="/"
          >
            Khám Phá
          </Link>
          <Link
            className={`font-body-lg text-body-md py-2 px-4 rounded-xl transition-all ${isActive('/destinations')
                ? 'navbar-mobile-active font-bold'
                : 'text-on-surface-variant hover:bg-secondary-container/20'
              }`}
            to="/destinations"
          >
            Điểm Đến
          </Link>
          <Link
            className={`font-body-lg text-body-md py-2 px-4 rounded-xl transition-all ${isActive('/map')
                ? 'navbar-mobile-active font-bold'
                : 'text-on-surface-variant hover:bg-secondary-container/20'
              }`}
            to="/map"
          >
            🗺️ Bản Đồ
          </Link>
          <Link
            className={`font-body-lg text-body-md py-2 px-4 rounded-xl transition-all ${isActive('/recommend')
                ? 'navbar-mobile-active font-bold'
                : 'text-on-surface-variant hover:bg-secondary-container/20'
              }`}
            to="/recommend"
          >
            ✨ Gợi Ý
          </Link>

          <div className="navbar-dropdown-divider" />

          {isAuthenticated ? (
            <>
              <span className="px-4 text-[12px] font-bold text-secondary uppercase tracking-wider">
                Tài khoản: {user.fullName}
              </span>
              <Link
                className={`font-body-lg text-body-md py-2 px-4 rounded-xl transition-all ${isActive('/admin')
                    ? 'navbar-mobile-active font-bold'
                    : 'text-on-surface-variant hover:bg-secondary-container/20'
                  }`}
                to="/admin"
              >
                Thống Kê Hệ Thống
              </Link>
              <Link
                className={`font-body-lg text-body-md py-2 px-4 rounded-xl transition-all ${isActive('/change-password')
                    ? 'navbar-mobile-active font-bold'
                    : 'text-on-surface-variant hover:bg-secondary-container/20'
                  }`}
                to="/change-password"
              >
                🔐 Đổi Mật Khẩu
              </Link>
              <button
                onClick={logout}
                className="font-body-lg text-body-md py-2 px-4 rounded-xl text-left text-red-500 hover:bg-red-50"
              >
                🚪 Đăng Xuất
              </button>
            </>
          ) : (
            <>
              <Link
                className={`font-body-lg text-body-md py-2 px-4 rounded-xl transition-all ${isActive('/login')
                    ? 'navbar-mobile-active font-bold'
                    : 'text-on-surface-variant hover:bg-secondary-container/20'
                  }`}
                to="/login"
              >
                🔑 Đăng Nhập
              </Link>
              <Link
                className={`font-body-lg text-body-md py-2 px-4 rounded-xl transition-all ${isActive('/register')
                    ? 'navbar-mobile-active font-bold'
                    : 'text-on-surface-variant hover:bg-secondary-container/20'
                  }`}
                to="/register"
              >
                👤 Đăng Ký
              </Link>
              <Link
                className={`font-body-lg text-body-md py-2 px-4 rounded-xl transition-all ${isActive('/admin')
                    ? 'navbar-mobile-active font-bold'
                    : 'text-on-surface-variant hover:bg-secondary-container/20'
                  }`}
                to="/admin"
              >
                Thống Kê Hệ Thống
              </Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}

export default Navbar;
