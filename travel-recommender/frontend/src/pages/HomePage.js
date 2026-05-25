import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaSearch, FaMapMarkedAlt } from 'react-icons/fa';
import { recommendationsApi } from '../services/api';
import DestinationCard from '../components/DestinationCard';
import './HomePage.css';

function HomePage() {
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentSeason, setCurrentSeason] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    detectSeasonAndLoad();
  }, []);

  const detectSeasonAndLoad = () => {
    const month = new Date().getMonth() + 1;
    let season = 'Spring';
    
    if (month >= 3 && month <= 5) season = 'Spring';
    else if (month >= 6 && month <= 8) season = 'Summer';
    else if (month >= 9 && month <= 11) season = 'Autumn';
    else season = 'Winter';

    setCurrentSeason(season);
    loadSeasonalRecommendations(season);
  };

  const loadSeasonalRecommendations = async (season) => {
    try {
      setLoading(true);
      setError(null);
      const response = await recommendationsApi.getSeasonal(season, 6);
      
      if (response.data.success) {
        setDestinations(response.data.recommendations);
      }
    } catch (err) {
      setError('Không thể tải dữ liệu. Vui lòng thử lại sau.');
      console.error('Error loading recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Khám Phá Thế Giới <br />
            <span className="gradient-text">Cùng AI</span>
          </h1>
          <p className="hero-subtitle">
            Hệ thống gợi ý du lịch thông minh dựa trên khai phá dữ liệu
          </p>
          <div className="hero-actions">
            <button 
              className="btn btn-primary"
              onClick={() => navigate('/destinations')}
            >
              <FaMapMarkedAlt /> Khám Phá Ngay
            </button>
          </div>
        </div>
      </section>

      {/* Seasonal Recommendations */}
      <section className="recommendations-section">
        <div className="section-container">
          <div className="section-header">
            <h2>
              Gợi Ý Cho Mùa {currentSeason === 'Spring' ? 'Xuân' : 
                              currentSeason === 'Summer' ? 'Hè' : 
                              currentSeason === 'Autumn' ? 'Thu' : 'Đông'}
            </h2>
            <p>Top 6 điểm đến phù hợp nhất với thời điểm hiện tại</p>
          </div>

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Đang tải gợi ý...</p>
            </div>
          )}

          {error && (
            <div className="error">
              <p>{error}</p>
              <button onClick={() => loadSeasonalRecommendations(currentSeason)}>
                Thử Lại
              </button>
            </div>
          )}

          {!loading && !error && destinations.length > 0 && (
            <div className="destinations-grid">
              {destinations.map((dest, index) => (
                <DestinationCard key={index} destination={dest} />
              ))}
            </div>
          )}

          {!loading && !error && destinations.length === 0 && (
            <div className="no-results">
              <p>Không tìm thấy điểm đến phù hợp</p>
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-container">
          <h2>Tính Năng Nổi Bật</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI Thông Minh</h3>
              <p>Gợi ý dựa trên khai phá dữ liệu và machine learning</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Bộ Lọc Mạnh Mẽ</h3>
              <p>Tìm kiếm theo mùa, ngân sách, loại hình du lịch</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🌍</div>
              <h3>3000+ Điểm Đến</h3>
              <p>Khám phá các địa điểm tuyệt vời trên toàn thế giới</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default HomePage;
