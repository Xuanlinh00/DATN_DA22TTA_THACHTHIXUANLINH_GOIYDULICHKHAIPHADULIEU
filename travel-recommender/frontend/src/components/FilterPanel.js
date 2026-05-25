import React, { useState, useEffect } from 'react';
import { FaFilter, FaTimes } from 'react-icons/fa';
import { filtersApi } from '../services/api';
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
      <button className="filter-toggle-btn" onClick={() => setIsOpen(!isOpen)}>
        <FaFilter />
        <span>Bộ Lọc</span>
        {activeFilterCount > 0 && (
          <span className="filter-badge">{activeFilterCount}</span>
        )}
      </button>

      <div className={`filter-panel ${isOpen ? 'open' : ''}`}>
        <div className="filter-header">
          <h3>
            <FaFilter /> Bộ Lọc
          </h3>
          <button className="close-btn" onClick={() => setIsOpen(false)}>
            <FaTimes />
          </button>
        </div>

        <div className="filter-content">
          <div className="filter-group">
            <label>Mùa</label>
            <select 
              value={filters.season} 
              onChange={(e) => handleFilterChange('season', e.target.value)}
            >
              <option value="">Tất cả</option>
              {options.seasons.map(season => (
                <option key={season} value={season}>{season}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Ngân Sách</label>
            <select 
              value={filters.budget} 
              onChange={(e) => handleFilterChange('budget', e.target.value)}
            >
              <option value="">Tất cả</option>
              {options.budgets.map(budget => (
                <option key={budget} value={budget}>{budget}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Loại Hình</label>
            <select 
              value={filters.category} 
              onChange={(e) => handleFilterChange('category', e.target.value)}
            >
              <option value="">Tất cả</option>
              {options.categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Quốc Gia</label>
            <select 
              value={filters.country} 
              onChange={(e) => handleFilterChange('country', e.target.value)}
            >
              <option value="">Tất cả</option>
              {options.countries.map(country => (
                <option key={country} value={country}>{country}</option>
              ))}
            </select>
          </div>

          {activeFilterCount > 0 && (
            <button className="clear-filters-btn" onClick={clearFilters}>
              <FaTimes /> Xóa Bộ Lọc
            </button>
          )}
        </div>
      </div>

      {isOpen && <div className="filter-overlay" onClick={() => setIsOpen(false)} />}
    </>
  );
}

export default FilterPanel;
