import React, { useState, useEffect } from 'react';
import { filtersApi } from '../services/api';
import { translateCategory, translateCountry } from '../utils/translator';
import './FilterPanel.css';

function FilterPanel({ onFilterChange, inline = false }) {
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
  };

  const toggleOption = (key, value) => {
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

  const applyFilters = () => {
    onFilterChange(filters);
    setIsOpen(false);
  };

  const activeFilterCount = Object.values(filters).filter(v => v !== '').length;

  return (
    <>
      {/* Floating Filter Toggle Trigger (Visible on mobile/tablet when panel is closed) */}
      {(!inline || !isOpen) && (
        <button 
          className={`fixed top-[100px] right-6 z-40 glass-panel p-4 rounded-full shadow-lg text-primary scale-100 transition-all duration-500 hover:scale-110 active:scale-95 flex items-center justify-center ${
            inline ? 'lg:hidden' : ''
          } ${isOpen ? 'opacity-0 scale-0 pointer-events-none' : 'opacity-100 scale-100'}`}
          onClick={() => setIsOpen(true)}
        >
          <span className="material-symbols-outlined text-2xl">tune</span>
        </button>
      )}

      {/* Filter Panel Container */}
      <aside 
        className={inline ? "fixed top-[100px] right-6 z-40 transition-all duration-500 ease-in-out lg:static lg:z-0 lg:w-full lg:opacity-100 lg:pointer-events-auto" : "fixed top-[100px] right-6 z-40 transition-all duration-500 ease-in-out"}
        style={inline && typeof window !== 'undefined' && window.innerWidth >= 1024 ? {
          transition: 'none'
        } : {
          transform: isOpen ? 'translateX(0)' : 'translateX(400px)',
          opacity: isOpen ? 1 : 0,
          pointerEvents: isOpen ? 'all' : 'none',
          transition: 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)'
        }}
      >
        <div className={`filter-panel-card glass-panel rounded-2xl p-6 flex flex-col gap-6 max-h-[calc(100vh-140px)] overflow-y-auto ${
          inline ? 'w-full lg:max-h-none lg:p-7' : 'w-80'
        }`}>
          {/* Header */}
          <div className="filter-panel-header flex justify-between items-center pb-2">
            <div>
              <h2 className="font-display text-xl font-bold text-primary">Bộ Lọc Chuyến Đi</h2>
              <p className="font-body-md text-[10px] text-secondary opacity-70 mt-0.5">Refine your escape</p>
            </div>
            <button 
              className={`material-symbols-outlined text-primary p-2 hover:bg-primary-container/20 rounded-full transition-colors flex items-center justify-center ${
                inline ? 'lg:hidden' : ''
              }`}
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
                      className={`filter-chip rounded-full px-3 py-1.5 font-label-caps text-[10px] cursor-pointer transition-all duration-200 ${
                        isSelected 
                          ? 'filter-chip--active text-white shadow-sm font-semibold' 
                          : 'filter-chip--idle text-secondary'
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
                      className={`filter-chip rounded-full px-3 py-1.5 font-label-caps text-[10px] cursor-pointer transition-all duration-200 ${
                        isSelected 
                          ? 'filter-chip--active text-white shadow-sm font-semibold' 
                          : 'filter-chip--idle text-secondary'
                      }`}
                      onClick={() => toggleOption('category', category)}
                    >
                      {translateCategory(category)}
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
                className="filter-select w-full p-2.5 rounded-xl focus:outline-none text-on-surface text-xs"
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
                className="filter-select w-full p-2.5 rounded-xl focus:outline-none text-on-surface text-xs"
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
                className="filter-apply-btn w-full py-3.5 text-white rounded-full font-label-caps text-[11px] font-bold uppercase tracking-wider shadow-md transition-transform active:scale-95 flex items-center justify-center gap-1"
                onClick={applyFilters}
              >
                <span className="material-symbols-outlined text-sm">done</span>
                Áp Dụng Bộ Lọc
              </button>
              {activeFilterCount > 0 && (
                <button 
                  className="filter-clear-btn w-full py-3.5 text-primary rounded-full font-label-caps text-[11px] font-bold uppercase tracking-wider transition-all flex items-center justify-center gap-1"
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

      {/* Overlay backdrop when open (mobile only) */}
      {isOpen && (
        <div 
          className={`fixed inset-0 bg-black/10 backdrop-blur-[2px] z-30 transition-all duration-300 ${
            inline ? 'lg:hidden' : ''
          }`}
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}

export default FilterPanel;
