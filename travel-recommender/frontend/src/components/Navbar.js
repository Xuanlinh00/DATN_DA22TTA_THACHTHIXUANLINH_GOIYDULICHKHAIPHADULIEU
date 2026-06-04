import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
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
        <span className="material-symbols-outlined text-[#c24482] text-2xl cursor-pointer scale-105 active:scale-95 transition-transform">
          account_circle
        </span>
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
