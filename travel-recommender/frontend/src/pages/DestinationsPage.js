import React, { useState, useEffect, useRef } from 'react';
import { recommendationsApi, destinationsApi } from '../services/api';
import { translateSearchQuery } from '../utils/translator';
import DestinationCard from '../components/DestinationCard';
import FilterPanel from '../components/FilterPanel';
import './DestinationsPage.css';

function DestinationsPage() {
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLabel, setSearchLabel] = useState(''); // từ khóa đang hiển thị
  const debounceRef = useRef(null);

  useEffect(() => {
    loadDestinations();
  }, []);

  // Debounced live search
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!searchQuery.trim()) {
      if (searchQuery === '') {
        setSearchLabel('');
        loadDestinations();
      }
      return;
    }
    debounceRef.current = setTimeout(() => {
      performSearch(searchQuery);
    }, 400);
    return () => clearTimeout(debounceRef.current);
    // eslint-disable-next-line
  }, [searchQuery]);

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

  const performSearch = async (query) => {
    try {
      setLoading(true);
      setError(null);

      // Dịch từ khóa tiếng Việt → tiếng Anh (có thể ra nhiều terms)
      const terms = translateSearchQuery(query); // ['biển'] → ['biển', 'beach']

      // Gửi song song tất cả terms, lấy results không trùng
      const allResults = await Promise.all(
        terms.map(term => destinationsApi.search(term).catch(() => null))
      );

      // Merge & dedupe theo Destination Name, ưu tiên thứ tự term đầu tiên (relevance cao nhất)
      const seen = new Set();
      const merged = [];
      for (const res of allResults) {
        if (!res?.data?.success) continue;
        for (const dest of res.data.results) {
          const key = dest['Destination Name'];
          if (!seen.has(key)) {
            seen.add(key);
            merged.push(dest);
          }
        }
      }

      setDestinations(merged);
      setSearchLabel(query);
    } catch (err) {
      setError('Không thể tìm kiếm. Vui lòng thử lại sau.');
      console.error('Error searching destinations:', err);
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
    await performSearch(searchQuery);
  };

  const handleClear = () => {
    setSearchQuery('');
    loadDestinations();
  };


  return (
    <main className="pt-[180px] pb-20 px-container-padding max-w-7xl mx-auto text-left" style={{ backgroundColor: '#fff7fa' }}>
      
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
          <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-secondary text-xl pointer-events-none">search</span>
          <input
            type="text"
            placeholder="Tìm kiếm điểm đến, quốc gia..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white/60 border border-pink-200 focus:border-primary-container focus:ring-2 focus:ring-pink-300 rounded-full py-3.5 pl-12 pr-12 text-sm transition-all focus:outline-none text-on-surface font-body-md"
          />
          {searchQuery ? (
            <button
              type="button"
              onClick={handleClear}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-secondary hover:text-primary flex items-center justify-center transition-colors"
              title="Xóa tìm kiếm"
            >
              <span className="material-symbols-outlined text-xl">close</span>
            </button>
          ) : null}
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
          <div className="mb-6 text-xs text-secondary font-semibold flex items-center gap-2">
            {searchLabel ? (
              <>
                Kết quả tìm kiếm "<strong className="text-primary">{searchLabel}</strong>":&nbsp;
                <strong className="text-primary">{destinations.length}</strong> điểm đến
              </>
            ) : (
              <>Tìm thấy <strong className="text-primary">{destinations.length}</strong> điểm đến phù hợp</>
            )}
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
