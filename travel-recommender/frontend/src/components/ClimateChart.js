import React, { useState, useRef } from 'react';
import './ClimateChart.css';

// ─── Constants ──────────────────────────────────────────────────────────────
const MONTH_FULL_VI = [
  'Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4',
  'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8',
  'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12',
];

// ─── Sub-components ─────────────────────────────────────────────────────────

/** A single bar column for one month */
function MonthBar({ month, monthFull, tempBar, rainBar, tempVal, rainVal, isBest, onMouseEnter, onMouseLeave }) {
  return (
    <div
      className={`climate-month-col ${isBest ? 'best-month' : ''}`}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <div className="climate-bar-wrap">
        {/* Temperature bar */}
        {tempBar !== null && (
          <div
            className="climate-bar-temp"
            style={{ height: `${tempBar}%` }}
            title={`${tempVal}°C`}
          />
        )}
        {/* Rainfall bar */}
        {rainBar !== null && (
          <div
            className="climate-bar-rain"
            style={{ height: `${rainBar}%` }}
            title={`${rainVal}mm`}
          />
        )}
      </div>
      <span className="climate-month-label">{month}</span>
    </div>
  );
}

// ─── Main Component ──────────────────────────────────────────────────────────
/**
 * ClimateChart
 * 
 * Renders a dual-bar chart (temperature + rainfall) for 12 months.
 * Built from scratch with pure CSS bars — no external chart library needed.
 * 
 * Props:
 *   climateData {Object} — response.climate from GET /api/destinations/{name}/climate
 *   bestMonths  {Array}  — e.g. ["Apr", "May", "Oct"]
 *   year        {number} — e.g. 2025
 *   loading     {bool}
 *   error       {string|null}
 */
function ClimateChart({ climateData, bestMonths = [], year, loading, error }) {
  const [activeTab, setActiveTab] = useState('both'); // 'both' | 'temp' | 'rain'
  const [tooltip, setTooltip] = useState(null); // { month, temp, rain, x, y }
  const containerRef = useRef(null);

  // ── Loading state ──────────────────────────────────────────────
  if (loading) {
    return (
      <div className="climate-loading">
        <div className="climate-spinner" />
        <span>Đang tải dữ liệu khí hậu...</span>
      </div>
    );
  }

  // ── Error / no data state ──────────────────────────────────────
  if (error || !climateData) {
    return (
      <div className="climate-error">
        <span>🌫️</span>
        <span>{error || 'Không có dữ liệu khí hậu cho điểm đến này.'}</span>
      </div>
    );
  }

  const { months, temp_avg, temp_max, temp_min, rainfall } = climateData;

  // ── Compute bar heights (as % of chart height) ─────────────────
  const validTemps = temp_avg.filter(v => v !== null);
  const validRain  = rainfall.filter(v => v !== null);

  const tempMin = validTemps.length ? Math.min(...validTemps) : 0;
  const tempMax = validTemps.length ? Math.max(...validTemps) : 40;
  const rainMax = validRain.length  ? Math.max(...validRain)  : 200;

  // Normalize to 10%–100% height range so small bars are still visible
  const normTemp = (v) => {
    if (v === null || v === undefined) return null;
    const range = tempMax - tempMin || 1;
    return 10 + ((v - tempMin) / range) * 88;
  };
  const normRain = (v) => {
    if (v === null || v === undefined) return null;
    if (rainMax === 0) return 5;
    return 5 + (v / rainMax) * 93;
  };

  // Y-axis tick labels for temperature
  const tempTicks = [
    Math.round(tempMax + (tempMax - tempMin) * 0.1),
    Math.round((tempMax + tempMin) / 2),
    Math.round(tempMin - (tempMax - tempMin) * 0.1),
  ];

  // ── Tooltip handlers ───────────────────────────────────────────
  const handleMouseEnter = (idx, e) => {
    const rect = containerRef.current?.getBoundingClientRect() || {};
    const colRect = e.currentTarget.getBoundingClientRect();
    const x = colRect.left - rect.left + colRect.width / 2;
    setTooltip({
      month:  MONTH_FULL_VI[idx],
      temp:   temp_avg[idx],
      tmax:   temp_max?.[idx],
      tmin:   temp_min?.[idx],
      rain:   rainfall[idx],
      x,
    });
  };
  const handleMouseLeave = () => setTooltip(null);

  return (
    <div className="climate-chart-wrapper" ref={containerRef}>

      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="climate-header">
        <div className="climate-title-group">
          <div className="climate-icon">🌡️</div>
          <div>
            <p className="climate-label">Khí Hậu Lịch Sử</p>
            <h3 className="climate-title">Biểu Đồ Nhiệt Độ & Lượng Mưa</h3>
          </div>
        </div>
        {year && (
          <span className="climate-year-badge">Dữ liệu năm {year}</span>
        )}
      </div>

      {/* ── Tab switcher ───────────────────────────────────────── */}
      <div className="climate-tabs" role="tablist">
        <button
          id="tab-both"
          role="tab"
          aria-selected={activeTab === 'both'}
          className={`climate-tab ${activeTab === 'both' ? 'active' : ''}`}
          onClick={() => setActiveTab('both')}
        >
          🌤️ Cả hai
        </button>
        <button
          id="tab-temp"
          role="tab"
          aria-selected={activeTab === 'temp'}
          className={`climate-tab ${activeTab === 'temp' ? 'active' : ''}`}
          onClick={() => setActiveTab('temp')}
        >
          🌡️ Nhiệt độ
        </button>
        <button
          id="tab-rain"
          role="tab"
          aria-selected={activeTab === 'rain'}
          className={`climate-tab ${activeTab === 'rain' ? 'active' : ''}`}
          onClick={() => setActiveTab('rain')}
        >
          🌧️ Lượng mưa
        </button>
      </div>

      {/* ── Bar Chart Area ──────────────────────────────────────── */}
      <div className="climate-chart-area" style={{ position: 'relative' }}>
        {/* Y-axis labels */}
        <div className="climate-y-axis">
          {tempTicks.map((t, i) => (
            <span key={i} className="climate-y-label">{t}°</span>
          ))}
        </div>

        {/* Gridlines */}
        <div className="climate-gridlines">
          <div className="climate-gridline" />
          <div className="climate-gridline" />
          <div className="climate-gridline" />
          <div className="climate-gridline" />
        </div>

        {/* Month columns */}
        {months.map((month, idx) => {
          const isBest = bestMonths.includes(month);
          const showTemp = activeTab === 'both' || activeTab === 'temp';
          const showRain = activeTab === 'both' || activeTab === 'rain';
          return (
            <MonthBar
              key={month}
              month={month}
              monthFull={MONTH_FULL_VI[idx]}
              tempBar={showTemp ? normTemp(temp_avg[idx]) : null}
              rainBar={showRain ? normRain(rainfall[idx])  : null}
              tempVal={temp_avg[idx]}
              rainVal={rainfall[idx]}
              isBest={isBest}
              onMouseEnter={(e) => handleMouseEnter(idx, e)}
              onMouseLeave={handleMouseLeave}
            />
          );
        })}

        {/* Tooltip */}
        {tooltip && (
          <div
            className="climate-tooltip"
            style={{ left: tooltip.x, bottom: 'calc(100% - 148px)' }}
            role="tooltip"
          >
            <p className="climate-tooltip-month">{tooltip.month}</p>
            {tooltip.temp !== null && (
              <div className="climate-tooltip-row">
                <span className="climate-tooltip-dot" style={{ background: '#c24482' }} />
                <span>TB: <strong>{tooltip.temp}°C</strong>
                  {tooltip.tmax != null && ` ↑${tooltip.tmax}°C`}
                  {tooltip.tmin != null && ` ↓${tooltip.tmin}°C`}
                </span>
              </div>
            )}
            {tooltip.rain !== null && (
              <div className="climate-tooltip-row">
                <span className="climate-tooltip-dot" style={{ background: '#7bbfea' }} />
                <span>Mưa: <strong>{tooltip.rain} mm</strong></span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* ── Legend ─────────────────────────────────────────────── */}
      <div className="climate-legend">
        <div className="climate-legend-item">
          <span className="climate-legend-dot" style={{ background: 'linear-gradient(180deg,#c24482,rgba(194,68,130,0.3))' }} />
          Nhiệt độ TB (°C)
        </div>
        <div className="climate-legend-item">
          <span className="climate-legend-dot" style={{ background: 'linear-gradient(180deg,#7bbfea,rgba(100,180,240,0.25))' }} />
          Lượng mưa (mm)
        </div>
        {bestMonths.length > 0 && (
          <div className="climate-legend-item">
            <span style={{ color: '#c24482', fontSize: 12 }}>★</span>
            Tháng đẹp nhất
          </div>
        )}
      </div>

      {/* ── Best months pills ──────────────────────────────────── */}
      {bestMonths.length > 0 && (
        <div className="climate-best-months">
          <span className="climate-best-label">✈️ Nên đi vào:</span>
          {bestMonths.map(m => (
            <span key={m} className="climate-best-pill">{m}</span>
          ))}
        </div>
      )}

      {bestMonths.length === 0 && (
        <div className="climate-best-months">
          <span className="climate-best-label">📌 Nguồn:</span>
          <span className="climate-best-pill" style={{ background: 'rgba(123,191,234,0.1)', borderColor: 'rgba(123,191,234,0.2)', color: '#5a9cc4' }}>
            Dữ liệu Khí hậu Thực tế
          </span>
        </div>
      )}
    </div>
  );
}

export default ClimateChart;
