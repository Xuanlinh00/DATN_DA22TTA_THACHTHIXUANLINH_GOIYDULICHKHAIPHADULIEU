import React, { useState, useEffect } from 'react';
import { filtersApi } from '../services/api';
import { translateCountry } from '../utils/translator';
import './FilterPanel.css';

function FilterPanel({ onFilterChange }) {
  const [filters, setFilters] = useState({
    season: '',
    budget: '',
    category: '',
    country: ''
  });

  const [options, setOptions] = useState({
    seasons: [],
    budgets: [],
    categories: [],
    countries: []
  });

  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadFilterOptions();
  }, []);

  const loadFilterOptions = async () => {
    try {
      const response = await filtersApi.getOptions();
      if (response.data.success) {
        setOptions(response.data.options);
      }
    } catch (error) {
      console.error('Error loading filter options:', error);
    }
  };

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const toggleOption = (key, value) => {
    // If already selected, clear it. Otherwise set it.
    const newValue = filters[key] === value ? '' : value;
    handleFilterChange(key, newValue);
  };

  const clearFilters = () => {
    const emptyFilters = {
      season: '',
      budget: '',
      category: '',
      country: ''
    };
    setFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  const activeFilterCount = Object.values(filters).filter(v => v !== '').length;

  return (
    <>
      {/* Floating Filter Toggle Trigger (Visible when panel is closed) */}
      <button 
        className={`fixed top-[100px] right-6 z-40 glass-panel p-4 rounded-full shadow-lg text-primary scale-100 transition-all duration-500 hover:scale-110 active:scale-95 flex items-center justify-center ${
          isOpen ? 'opacity-0 scale-0 pointer-events-none' : 'opacity-100 scale-100'
        }`}
        onClick={() => setIsOpen(true)}
      >
        <span className="material-symbols-outlined text-2xl">tune</span>
      </button>

      {/* Floating Filter Panel (Slides in from right) */}
      <aside 
        className="fixed top-[100px] right-6 z-40 transition-all duration-500 ease-in-out"
        style={{
          transform: isOpen ? 'translateX(0)' : 'translateX(400px)',
          opacity: isOpen ? 1 : 0,
          pointerEvents: isOpen ? 'all' : 'none',
          transition: 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)'
        }}
      >
        <div className="glass-panel rounded-2xl w-80 p-6 flex flex-col gap-6 shadow-[40px_0_80px_rgba(136,19,55,0.05)] max-h-[calc(100vh-140px)] overflow-y-auto">
          {/* Header */}
          <div className="flex justify-between items-center pb-2 border-b border-pink-100/50">
            <div>
              <h2 className="font-display-lg text-xl font-bold text-primary">Bộ Lọc Chuyến Đi</h2>
              <p className="font-label-caps text-[10px] text-secondary opacity-70 mt-0.5">Tinh chỉnh hành trình của bạn</p>
            </div>
            <button 
              className="material-symbols-outlined text-primary p-2 hover:bg-primary-container/20 rounded-full transition-colors flex items-center justify-center"
              onClick={() => setIsOpen(false)}
            >
              close
            </button>
          </div>

          {/* Filter Body */}
          <div className="space-y-6">
            {/* Season Filter Chips */}
            <div className="flex flex-col gap-2 text-left">
              <span className="font-label-caps text-[10px] text-primary font-bold uppercase tracking-widest">Mùa Lý Tưởng</span>
              <div className="flex flex-wrap gap-2">
                {options.seasons.map(season => {
                  const isSelected = filters.season === season;
                  return (
                    <span 
                      key={season}
                      className={`rounded-full px-3 py-1.5 font-label-caps text-[10px] cursor-pointer transition-all duration-200 ${
                        isSelected 
                          ? 'bg-primary-container text-white shadow-sm font-semibold' 
                          : 'text-secondary bg-secondary-container/20 hover:bg-secondary-container/50'
                      }`}
                      onClick={() => toggleOption('season', season)}
                    >
                      {season === 'Spring' ? '🌸 Xuân' : season === 'Summer' ? '☀️ Hè' : season === 'Autumn' ? '🍂 Thu' : '❄️ Đông'}
                    </span>
                  );
                })}
              </div>
            </div>

            {/* Category/Type Filter Chips */}
            <div className="flex flex-col gap-2 text-left">
              <span className="font-label-caps text-[10px] text-primary font-bold uppercase tracking-widest">Phong Cách Du Lịch</span>
              <div className="flex flex-wrap gap-2">
                {options.categories.map(category => {
                  const isSelected = filters.category === category;
                  return (
                    <span 
                      key={category}
                      className={`rounded-full px-3 py-1.5 font-label-caps text-[10px] cursor-pointer transition-all duration-200 ${
                        isSelected 
                          ? 'bg-primary-container text-white shadow-sm font-semibold' 
                          : 'text-secondary bg-secondary-container/20 hover:bg-secondary-container/50'
                      }`}
                      onClick={() => toggleOption('category', category)}
                    >
                      {category}
                    </span>
                  );
                })}
              </div>
            </div>

            {/* Budget Dropdown */}
            <div className="flex flex-col gap-2 text-left">
              <span className="font-label-caps text-[10px] text-primary font-bold uppercase tracking-widest">Ngân Sách</span>
              <select
                value={filters.budget}
                onChange={(e) => handleFilterChange('budget', e.target.value)}
                className="w-full p-2.5 bg-white/60 border border-pink-200 rounded-xl focus:ring-2 focus:ring-pink-400 focus:outline-none text-on-surface text-xs"
              >
                <option value="">Tất cả</option>
                {options.budgets.map(budget => (
                  <option key={budget} value={budget}>
                    {budget === 'Budget' ? 'Tiết kiệm' : budget === 'Moderate' ? 'Bình dân' : budget === 'Expensive' ? 'Cao cấp' : 'Sang trọng'}
                  </option>
                ))}
              </select>
            </div>

            {/* Country Dropdown */}
            <div className="flex flex-col gap-2 text-left">
              <span className="font-label-caps text-[10px] text-primary font-bold uppercase tracking-widest">Quốc Gia</span>
              <select
                value={filters.country}
                onChange={(e) => handleFilterChange('country', e.target.value)}
                className="w-full p-2.5 bg-white/60 border border-pink-200 rounded-xl focus:ring-2 focus:ring-pink-400 focus:outline-none text-on-surface text-xs"
              >
                <option value="">Tất cả</option>
                {options.countries.map(country => (
                  <option key={country} value={country}>{translateCountry(country)}</option>
                ))}
              </select>
            </div>

            {/* Apply & Reset Buttons */}
            <div className="flex flex-col gap-2 mt-4">
              <button 
                className="w-full py-3.5 bg-primary-container hover:bg-primary-container/95 text-white rounded-full font-label-caps text-[11px] font-bold uppercase tracking-wider shadow-lg transition-transform active:scale-95 flex items-center justify-center gap-1"
                onClick={() => setIsOpen(false)}
              >
                <span className="material-symbols-outlined text-sm">done</span>
                Áp Dụng Bộ Lọc
              </button>
              {activeFilterCount > 0 && (
                <button 
                  className="w-full py-3.5 bg-white border border-pink-200 text-primary rounded-full font-label-caps text-[11px] font-bold uppercase tracking-wider transition-all hover:bg-pink-50 flex items-center justify-center gap-1"
                  onClick={clearFilters}
                >
                  <span className="material-symbols-outlined text-sm">close</span>
                  Xóa Bộ Lọc ({activeFilterCount})
                </button>
              )}
            </div>
          </div>
        </div>
      </aside>

      {/* Overlay backdrop when open */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/10 backdrop-blur-[2px] z-30 transition-all duration-300"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}

export default FilterPanel;
