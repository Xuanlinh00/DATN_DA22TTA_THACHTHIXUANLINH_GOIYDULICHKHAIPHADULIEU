import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FaGlobeAmericas, FaCompass, FaMapMarkedAlt } from 'react-icons/fa';
import './Navbar.css';

function Navbar() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <FaGlobeAmericas className="logo-icon" />
          <span>Travel Recommender</span>
        </Link>

        <ul className="navbar-menu">
          <li>
            <Link 
              to="/" 
              className={`navbar-link ${isActive('/') ? 'active' : ''}`}
            >
              <FaCompass className="nav-icon" />
              <span>Khám Phá</span>
            </Link>
          </li>
          <li>
            <Link 
              to="/destinations" 
              className={`navbar-link ${isActive('/destinations') ? 'active' : ''}`}
            >
              <FaMapMarkedAlt className="nav-icon" />
              <span>Điểm Đến</span>
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
