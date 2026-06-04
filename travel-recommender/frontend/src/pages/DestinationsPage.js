import React, { useState, useEffect } from 'react';
import { recommendationsApi, destinationsApi } from '../services/api';
import DestinationCard from '../components/DestinationCard';
import FilterPanel from '../components/FilterPanel';
import './DestinationsPage.css';

function DestinationsPage() {
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

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
    <main className="pt-[180px] pb-20 px-container-padding max-w-7xl mx-auto md:pl-[12%] text-left" style={{ backgroundColor: '#fff7fa' }}>
      
      {/* Hero Header */}
      <header className="mb-16">
        <h1 className="font-display-lg text-display-lg text-primary mb-4 leading-tight">
          Chuyến Đi<br />
          <span className="italic font-light">Độc Bản</span>
        </h1>
        <p className="font-body-lg text-body-lg text-on-surface-variant max-w-xl opacity-80">
          Khám phá những thiên đường ẩn mình và những địa điểm nghỉ dưỡng được tuyển chọn dành riêng cho bạn.
        </p>
      </header>

      {/* Controls: Search and Filter Toggle */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-center mb-10 w-full">
        <form onSubmit={handleSearch} className="relative w-full max-w-md">
          <input
            type="text"
            placeholder="Tìm kiếm điểm đến thế giới..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white/60 border border-pink-200 focus:border-primary-container focus:ring-2 focus:ring-pink-300 rounded-full py-3.5 pl-6 pr-12 text-sm transition-all focus:outline-none text-on-surface font-body-md"
          />
          <button type="submit" className="absolute right-4 top-1/2 -translate-y-1/2 text-primary flex items-center justify-center">
            <span className="material-symbols-outlined text-xl">search</span>
          </button>
        </form>

        <FilterPanel onFilterChange={handleFilterChange} />
      </div>

      {loading && (
        <div className="loading flex flex-col items-center justify-center py-20">
          <div className="spinner border-t-primary w-10 h-10 border-4 border-pink-200 rounded-full animate-spin"></div>
          <p className="text-secondary mt-3">Đang phân tích các điểm đến…</p>
        </div>
      )}

      {error && (
        <div className="error text-center py-10">
          <p className="text-red-500 font-medium mb-4">{error}</p>
          <button onClick={loadDestinations} className="bg-primary text-white px-6 py-2.5 rounded-full font-bold">
            Thử Lại
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          <div className="mb-6 text-xs text-secondary font-semibold">
            Tìm thấy <strong className="text-primary">{destinations.length}</strong> điểm đến phù hợp
          </div>

          <div className="masonry-grid">
            {destinations.map((dest, index) => (
              <div key={index} className="masonry-item">
                <DestinationCard destination={dest} />
              </div>
            ))}
          </div>

          {destinations.length === 0 && (
            <div className="text-center py-20 glass-panel rounded-2xl p-10 max-w-md mx-auto">
              <span className="material-symbols-outlined text-5xl text-secondary mb-3">sentiment_dissatisfied</span>
              <p className="text-secondary font-medium mb-4">Không tìm thấy kết quả phù hợp</p>
              <button onClick={loadDestinations} className="bg-primary text-white px-6 py-2 rounded-full font-bold text-xs uppercase tracking-wider">
                Xem Tất Cả
              </button>
            </div>
          )}
        </>
      )}
    </main>
  );
}

export default DestinationsPage;
