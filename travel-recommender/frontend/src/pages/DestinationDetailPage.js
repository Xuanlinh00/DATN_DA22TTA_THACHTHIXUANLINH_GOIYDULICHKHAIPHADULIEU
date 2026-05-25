import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FaStar, FaMapMarkerAlt, FaDollarSign, FaArrowLeft, FaCalendarAlt } from 'react-icons/fa';
import { destinationsApi } from '../services/api';
import DestinationCard from '../components/DestinationCard';
import './DestinationDetailPage.css';

function DestinationDetailPage() {
  const { name } = useParams();
  const navigate = useNavigate();
  const [destination, setDestination] = useState(null);
  const [similarDestinations, setSimilarDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDestinationDetails();
  }, [name]);

  const loadDestinationDetails = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load destination details
      const response = await destinationsApi.getByName(name);
      if (response.data.success) {
        setDestination(response.data.destination);
      }

      // Load similar destinations
      try {
        const similarResponse = await destinationsApi.getSimilar(name);
        if (similarResponse.data.success) {
          setSimilarDestinations(similarResponse.data.similar.slice(0, 4));
        }
      } catch (err) {
        console.log('No similar destinations found');
      }

    } catch (err) {
      setError('Không tìm thấy điểm đến này.');
      console.error('Error loading destination:', err);
    } finally {
      setLoading(false);
    }
  };

  const getBudgetIcon = (category) => {
    const count = category === 'Budget' ? 1 : category === 'Moderate' ? 2 : category === 'Expensive' ? 3 : 4;
    return Array(count).fill('$').join('');
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Đang tải...</p>
      </div>
    );
  }

  if (error || !destination) {
    return (
      <div className="error">
        <p>{error || 'Không tìm thấy điểm đến'}</p>
        <button onClick={() => navigate('/destinations')}>
          Quay Lại Danh Sách
        </button>
      </div>
    );
  }

  const imageUrl = destination.image || `https://source.unsplash.com/1200x600/?${encodeURIComponent(destination['Destination Name'])},travel`;

  return (
    <div className="destination-detail-page">
      <button className="back-btn" onClick={() => navigate(-1)}>
        <FaArrowLeft /> Quay Lại
      </button>

      <div className="detail-hero">
        <img 
          src={imageUrl} 
          alt={destination['Destination Name']}
          onError={(e) => {
            e.target.src = 'https://source.unsplash.com/1200x600/?travel,destination';
          }}
        />
        <div className="hero-overlay">
          <div className="hero-content">
            <h1>{destination['Destination Name']}</h1>
            <div className="hero-meta">
              <span className="location">
                <FaMapMarkerAlt /> {destination.Country}
              </span>
              <span className="rating">
                <FaStar /> {destination['Avg Rating']?.toFixed(1) || 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="detail-container">
        <div className="detail-main">
          <div className="info-section">
            <h2>Thông Tin Chi Tiết</h2>
            <div className="info-grid">
              <div className="info-item">
                <div className="info-label">Loại Hình</div>
                <div className="info-value">{destination.Type}</div>
              </div>
              <div className="info-item">
                <div className="info-label">Mùa Tốt Nhất</div>
                <div className="info-value">
                  <FaCalendarAlt /> {destination['Best Season']}
                </div>
              </div>
              <div className="info-item">
                <div className="info-label">Ngân Sách</div>
                <div className="info-value">
                  <FaDollarSign /> {getBudgetIcon(destination.Cost_Category)}
                </div>
              </div>
              <div className="info-item">
                <div className="info-label">Chi Phí Trung Bình</div>
                <div className="info-value">${destination['Avg Cost (USD/day)']} / ngày</div>
              </div>
            </div>
          </div>

          {destination.Broader_Type && (
            <div className="info-section">
              <h2>Phân Loại</h2>
              <p className="category-tag">{destination.Broader_Type}</p>
            </div>
          )}

          {destination['UNESCO Site'] === 'Yes' && (
            <div className="unesco-badge">
              🏛️ Di Sản UNESCO
            </div>
          )}
        </div>

        {similarDestinations.length > 0 && (
          <div className="similar-section">
            <h2>Điểm Đến Tương Tự</h2>
            <div className="similar-grid">
              {similarDestinations.map((dest, index) => (
                <DestinationCard key={index} destination={dest} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default DestinationDetailPage;
