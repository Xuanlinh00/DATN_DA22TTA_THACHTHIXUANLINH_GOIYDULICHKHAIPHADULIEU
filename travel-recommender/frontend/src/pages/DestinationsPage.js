import React, { useState, useEffect } from 'react';
import { FaSearch } from 'react-icons/fa';
import { recommendationsApi, destinationsApi } from '../services/api';
import DestinationCard from '../components/DestinationCard';
import FilterPanel from '../components/FilterPanel';
import './DestinationsPage.css';

function DestinationsPage() {
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({});

  useEffect(() => {
    loadDestinations();
  }, []);

  const loadDestinations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await destinationsApi.getAll({ limit: 50 });
      
      if (response.data.success) {
        setDestinations(response.data.destinations);
      }
    } catch (err) {
      setError('Không thể tải dữ liệu. Vui lòng thử lại sau.');
      console.error('Error loading destinations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = async (newFilters) => {
    setFilters(newFilters);
    
    // Check if any filter is active
    const hasActiveFilters = Object.values(newFilters).some(v => v !== '');
    
    if (!hasActiveFilters) {
      loadDestinations();
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await recommendationsApi.getFiltered({
        season: newFilters.season || undefined,
        budget: newFilters.budget || undefined,
        category: newFilters.category || undefined,
        country: newFilters.country || undefined,
        limit: 50
      });
      
      if (response.data.success) {
        setDestinations(response.data.recommendations);
      }
    } catch (err) {
      setError('Không thể lọc dữ liệu. Vui lòng thử lại sau.');
      console.error('Error filtering destinations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      loadDestinations();
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await destinationsApi.search(searchQuery);
      
      if (response.data.success) {
        setDestinations(response.data.results);
      }
    } catch (err) {
      setError('Không thể tìm kiếm. Vui lòng thử lại sau.');
      console.error('Error searching destinations:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="destinations-page">
      <div className="page-header">
        <div className="header-content">
          <h1>Khám Phá Điểm Đến</h1>
          <p>Tìm kiếm và lọc hơn 3000 điểm đến trên toàn thế giới</p>
        </div>
      </div>

      <div className="page-container">
        <div className="controls-bar">
          <form className="search-form" onSubmit={handleSearch}>
            <input
              type="text"
              placeholder="Tìm kiếm điểm đến..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            <button type="submit" className="search-btn">
              <FaSearch />
            </button>
          </form>

          <FilterPanel onFilterChange={handleFilterChange} />
        </div>

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Đang tải...</p>
          </div>
        )}

        {error && (
          <div className="error">
            <p>{error}</p>
            <button onClick={loadDestinations}>Thử Lại</button>
          </div>
        )}

        {!loading && !error && destinations.length > 0 && (
          <>
            <div className="results-info">
              <p>Tìm thấy <strong>{destinations.length}</strong> điểm đến</p>
            </div>
            <div className="destinations-grid">
              {destinations.map((dest, index) => (
                <DestinationCard key={index} destination={dest} />
              ))}
            </div>
          </>
        )}

        {!loading && !error && destinations.length === 0 && (
          <div className="no-results">
            <p>Không tìm thấy điểm đến phù hợp</p>
            <button onClick={loadDestinations}>Xem Tất Cả</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default DestinationsPage;
