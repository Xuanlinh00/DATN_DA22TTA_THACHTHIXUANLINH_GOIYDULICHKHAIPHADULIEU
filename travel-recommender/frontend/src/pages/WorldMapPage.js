import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { destinationsApi, recommendationsApi, filtersApi } from '../services/api';
import { getDestinationImage, getFallbackImage, resolveCategoryKey } from '../services/imageService';
import {
  translateCountry, translateCategory, translateSeason,
  stripDisplayName, fixDescription
} from '../utils/translator';

/* ─── Fix default Leaflet marker icons broken by Webpack ──────────────────── */
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl:       'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl:     'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

/* ─── Custom pulsing pink marker ──────────────────────────────────────────── */
const customIcon = L.divIcon({
  className: '',
  html: `
    <div style="position:relative;width:20px;height:20px;">
      <div style="position:absolute;width:32px;height:32px;left:-6px;top:-6px;border-radius:50%;
                  background:rgba(194,68,130,0.25);animation:ping 1.5s cubic-bezier(0,0,0.2,1) infinite;"></div>
      <div style="position:relative;z-index:10;width:18px;height:18px;background:#c24482;
                  border:2.5px solid #fff;border-radius:50%;
                  box-shadow:0 2px 8px rgba(194,68,130,0.45);"></div>
    </div>`,
  iconSize:    [20, 20],
  iconAnchor:  [10, 10],
  popupAnchor: [0, -12],
});

const selectedIcon = L.divIcon({
  className: '',
  html: `
    <div style="position:relative;width:24px;height:24px;">
      <div style="position:absolute;width:40px;height:40px;left:-8px;top:-8px;border-radius:50%;
                  background:rgba(194,68,130,0.35);animation:ping 1s cubic-bezier(0,0,0.2,1) infinite;"></div>
      <div style="position:relative;z-index:10;width:22px;height:22px;background:#c24482;
                  border:3px solid #fff;border-radius:50%;
                  box-shadow:0 4px 14px rgba(194,68,130,0.6);"></div>
    </div>`,
  iconSize:    [24, 24],
  iconAnchor:  [12, 12],
  popupAnchor: [0, -14],
});

/* ─── MapFlyTo: smoothly pan/zoom when selected destination changes ────────── */
function MapFlyTo({ dest }) {
  const map = useMap();
  useEffect(() => {
    if (!dest) return;
    const lat = parseFloat(dest.destination_latitude);
    const lon = parseFloat(dest.destination_longitude);
    if (!isNaN(lat) && !isNaN(lon)) {
      map.flyTo([lat, lon], 6, { duration: 1.2 });
    }
  }, [dest, map]);
  return null;
}

/* ─── Translate helpers ───────────────────────────────────────────────────── */
const SEASON_LABEL = {
  Spring: '🌸 Mùa Xuân', Summer: '☀️ Mùa Hè',
  Autumn: '🍂 Mùa Thu',  Winter: '❄️ Mùa Đông',
};
const BUDGET_LABEL = {
  Budget: '💚 Tiết kiệm', Moderate: '💛 Bình dân',
  Expensive: '🧡 Cao cấp', Luxury: '💎 Sang trọng',
};
const EMPTY_OPTS = { seasons: [], budgets: [], categories: [], countries: [] };
const INIT_FILTERS = { season: '', budget: '', category: '', country: '' };

/* ════════════════════════════════════════════════════════════════════════════ */
export default function WorldMapPage() {
  const navigate  = useNavigate();
  const mapRef    = useRef(null);             // direct Leaflet map instance

  /* state */
  const [destinations, setDestinations] = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState(null);
  const [filters,      setFilters]      = useState(INIT_FILTERS);
  const [options,      setOptions]      = useState(EMPTY_OPTS);
  const [selectedDest, setSelectedDest] = useState(null);
  const [flyToDest,    setFlyToDest]    = useState(null);   // triggers MapFlyTo

  /* ── load filter options once ─────────────────────────────────────────── */
  useEffect(() => {
    filtersApi.getOptions()
      .then(r => { if (r.data.success) setOptions(r.data.options); })
      .catch(err => console.error('Filter options error:', err));
  }, []);

  /* ── load destinations whenever filters change ────────────────────────── */
  const loadDestinations = useCallback(async (activeFilters) => {
    setLoading(true);
    setError(null);
    try {
      const hasFilter = Object.values(activeFilters).some(v => v !== '');

      let list = [];
      if (hasFilter) {
        const payload = {
          season:         activeFilters.season   || undefined,
          budget:         activeFilters.budget   || undefined,
          category:       activeFilters.category || undefined,
          country:        activeFilters.country  || undefined,
          limit:          150,
          strict_country: Boolean(activeFilters.country),
        };
        const res = await recommendationsApi.getFiltered(payload);
        if (res.data.success) list = res.data.recommendations || [];
      } else {
        const res = await destinationsApi.getAll({ limit: 150 });
        if (res.data.success) list = res.data.destinations || [];
      }

      /* keep only items with valid coordinates */
      const valid = list.filter(d => {
        const lat = parseFloat(d.destination_latitude);
        const lon = parseFloat(d.destination_longitude);
        return !isNaN(lat) && !isNaN(lon);
      });

      setDestinations(valid);

      /* keep the info card hidden until the user clicks a marker */
      setSelectedDest(null);
      if (valid.length > 0) {
        setFlyToDest(valid[0]);
      } else {
        setFlyToDest(null);
      }
    } catch (err) {
      console.error('Map load error:', err);
      setError('Không thể tải dữ liệu. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  }, []);

  /* initial load */
  useEffect(() => { loadDestinations(INIT_FILTERS); }, [loadDestinations]);

  /* ── filter change handler ────────────────────────────────────────────── */
  const handleFilterChange = (key, value) => {
    const next = { ...filters, [key]: value };
    setFilters(next);
    loadDestinations(next);
  };

  const resetFilters = () => {
    setFilters(INIT_FILTERS);
    loadDestinations(INIT_FILTERS);
  };

  /* ── marker click ─────────────────────────────────────────────────────── */
  const handleMarkerClick = (dest) => {
    setSelectedDest(dest);
    setFlyToDest(dest);
  };

  /* ── open Google Maps directions in new tab ───────────────────────────── */
  const openGoogleMapsDirections = () => {
    if (!selectedDest) return;
    const lat = parseFloat(selectedDest.destination_latitude);
    const lon = parseFloat(selectedDest.destination_longitude);
    const name = encodeURIComponent(selectedDest['Destination Name']);
    window.open(
      `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}&destination_place_id=${name}`,
      '_blank'
    );
  };

  /* ── active-filter count for badge ────────────────────────────────────── */
  const activeCount = Object.values(filters).filter(v => v !== '').length;

  /* ════════════════════════════════════════════════════════════════════════ */
  return (
    <div className="relative w-screen overflow-hidden text-left" style={{ height: '100dvh', backgroundColor: '#f8f0f5' }}>

      {/* ── Fullscreen Map ─────────────────────────────────────────────── */}
      <MapContainer
        center={[20, 10]}
        zoom={2}
        style={{ position: 'absolute', inset: 0, height: '100%', width: '100%', zIndex: 0 }}
        zoomControl={false}
        whenCreated={m => { mapRef.current = m; }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />

        {/* smooth fly-to when selection changes */}
        <MapFlyTo dest={flyToDest} />

        {/* destination markers */}
        {destinations.map(dest => {
          const isSelected = selectedDest && selectedDest['Destination Name'] === dest['Destination Name'];
          return (
            <Marker
              key={dest['Destination Name']}
              position={[parseFloat(dest.destination_latitude), parseFloat(dest.destination_longitude)]}
              icon={isSelected ? selectedIcon : customIcon}
              zIndexOffset={isSelected ? 1000 : 0}
              eventHandlers={{ click: () => handleMarkerClick(dest) }}
            >
              <Popup minWidth={160} maxWidth={200}>
                <div style={{ fontFamily: 'Inter, sans-serif', padding: '4px 2px' }}>
                  <p style={{ fontWeight: 700, fontSize: 12, color: '#c24482', margin: '0 0 4px' }}>
                    {stripDisplayName(dest['Destination Name'])}
                  </p>
                  <p style={{ fontSize: 10, color: '#765469', margin: '0 0 8px' }}>
                    📍 {translateCountry(dest.Country)}
                  </p>
                  <button
                    onClick={() => navigate(`/destinations/${encodeURIComponent(dest['Destination Name'])}`)}
                    style={{
                      width: '100%', background: '#c24482', color: '#fff',
                      border: 'none', borderRadius: 20, padding: '5px 10px',
                      fontSize: 9, fontWeight: 700, cursor: 'pointer', letterSpacing: '0.05em',
                      textTransform: 'uppercase'
                    }}
                  >
                    Xem Chi Tiết
                  </button>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* ── Filter Sidebar ─────────────────────────────────────────────── */}
      <aside style={{
        position: 'fixed', top: 82, left: 20, zIndex: 40,
        width: 272,
        background: 'rgba(255,255,255,0.95)',
        backdropFilter: 'blur(20px)',
        borderRadius: 18,
        border: '1px solid var(--glass-border, rgba(194,68,130,0.14))',
        boxShadow: 'var(--shadow-md, 0 8px 40px rgba(136,19,55,0.1))',
        overflow: 'hidden',
      }}>

        {/* ── sidebar header ── */}
        <div style={{
          background: 'var(--grad-primary, linear-gradient(135deg, #c24482 0%, #e8679b 100%))',
          padding: '14px 18px 12px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 18 }}>🔍</span>
            <div>
              <h2 style={{
                fontFamily: 'Inter,sans-serif', fontWeight: 700, fontSize: 14,
                color: '#fff', margin: 0, lineHeight: 1.3,
              }}>
                Lọc Điểm Đến
              </h2>
              <p style={{
                fontFamily: 'Inter,sans-serif', fontSize: 10, color: 'rgba(255,255,255,0.8)',
                margin: 0, marginTop: 2,
              }}>
                Chọn tiêu chí để tìm điểm phù hợp
              </p>
            </div>
          </div>

          {/* active chips row */}
          {activeCount > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 10 }}>
              {filters.season && (
                <ActiveChip
                  label={SEASON_LABEL[filters.season] || filters.season}
                  onRemove={() => handleFilterChange('season', '')}
                />
              )}
              {filters.budget && (
                <ActiveChip
                  label={BUDGET_LABEL[filters.budget] || filters.budget}
                  onRemove={() => handleFilterChange('budget', '')}
                />
              )}
              {filters.category && (
                <ActiveChip
                  label={translateCategory(filters.category) || filters.category}
                  onRemove={() => handleFilterChange('category', '')}
                />
              )}
              {filters.country && (
                <ActiveChip
                  label={'🌐 ' + (translateCountry(filters.country) || filters.country)}
                  onRemove={() => handleFilterChange('country', '')}
                />
              )}
            </div>
          )}
        </div>

        {/* ── filter body ── */}
        <div style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>

          <FilterSelect
            icon="🌤️"
            label="Mùa du lịch"
            hint="Chọn thời điểm bạn muốn đi"
            value={filters.season}
            onChange={v => handleFilterChange('season', v)}
            placeholder="Tất cả các mùa"
            options={options.seasons.map(s => ({ value: s, label: SEASON_LABEL[s] || s }))}
          />

          <FilterSelect
            icon="💰"
            label="Ngân sách"
            hint="Mức chi tiêu trung bình mỗi ngày"
            value={filters.budget}
            onChange={v => handleFilterChange('budget', v)}
            placeholder="Tất cả mức giá"
            options={options.budgets.map(b => ({ value: b, label: BUDGET_LABEL[b] || b }))}
          />

          <FilterSelect
            icon="🏷️"
            label="Loại hình du lịch"
            hint="Biển, thiên nhiên, văn hóa, mạo hiểm..."
            value={filters.category}
            onChange={v => handleFilterChange('category', v)}
            placeholder="Tất cả loại hình"
            options={options.categories.map(c => ({ value: c, label: translateCategory(c) || c }))}
          />

          <FilterSelect
            icon="🌍"
            label="Quốc gia"
            hint="Thu hẹp về một quốc gia cụ thể"
            value={filters.country}
            onChange={v => handleFilterChange('country', v)}
            placeholder="Tất cả quốc gia"
            options={options.countries.map(c => ({ value: c, label: translateCountry(c) || c }))}
          />

          {/* reset button — only when filters active */}
          {activeCount > 0 && (
            <button
              onClick={resetFilters}
              style={{
                marginTop: 2,
                width: '100%', background: 'transparent',
                border: '1.5px dashed color-mix(in srgb, var(--theme-primary, #c24482) 40%, transparent)',
                color: 'var(--theme-primary, #c24482)', borderRadius: 10, padding: '8px 0',
                fontFamily: 'Inter,sans-serif', fontSize: 10, fontWeight: 600,
                cursor: 'pointer', letterSpacing: '0.04em',
                transition: 'all .15s',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = 'var(--theme-primary-bg, #fbe4f2)';
                e.currentTarget.style.borderStyle = 'solid';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.borderStyle = 'dashed';
              }}
            >
              ✕ Xóa tất cả bộ lọc
            </button>
          )}
        </div>

        {/* ── result footer ── */}
        <div style={{
          padding: '10px 16px 14px',
          borderTop: '1px solid var(--glass-border, rgba(194,68,130,0.1))',
        }}>
          {loading ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
              <div style={{
                width: 14, height: 14, border: '2px solid #f4a4c6',
                borderTopColor: '#c24482', borderRadius: '50%',
                animation: 'spin .7s linear infinite', flexShrink: 0,
              }} />
              <span style={{ fontFamily: 'Inter,sans-serif', fontSize: 11, color: '#87717a' }}>
                Đang tìm kiếm...
              </span>
            </div>
          ) : error ? (
            <p style={{ fontFamily: 'Inter,sans-serif', fontSize: 11, color: '#ba1a1a', margin: 0 }}>
              ⚠️ {error}
            </p>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                {/* coloured dot */}
                <div style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: destinations.length > 0 ? '#c24482' : '#87717a',
                  flexShrink: 0,
                }} />
                <span style={{
                  fontFamily: 'Inter,sans-serif', fontSize: 11,
                  color: destinations.length > 0 ? '#1f1a1e' : '#87717a',
                  fontWeight: destinations.length > 0 ? 600 : 400,
                }}>
                  {destinations.length > 0
                    ? `${destinations.length} điểm đến trên bản đồ`
                    : 'Không tìm thấy điểm đến'}
                </span>
              </div>
              {destinations.length === 0 && activeCount > 0 && (
                <button
                  onClick={resetFilters}
                  style={{
                    fontFamily: 'Inter,sans-serif', fontSize: 9, color: '#c24482',
                    background: 'none', border: 'none', cursor: 'pointer',
                    fontWeight: 700, textDecoration: 'underline', padding: 0,
                  }}
                >
                  Xóa lọc
                </button>
              )}
            </div>
          )}

          {/* usage hint when no filters active */}
          {!loading && !error && activeCount === 0 && (
            <p style={{
              fontFamily: 'Inter,sans-serif', fontSize: 10, color: '#87717a',
              margin: '6px 0 0', lineHeight: 1.5,
            }}>
              💡 Dùng bộ lọc bên trên để thu hẹp điểm đến theo sở thích của bạn.
            </p>
          )}
        </div>
      </aside>




      {/* ── Destination Info Card (bottom) ─────────────────────────────── */}
      {selectedDest && !loading && (
        <DestinationCard
          dest={selectedDest}
          onNavigate={() => navigate(`/destinations/${encodeURIComponent(selectedDest['Destination Name'])}`)}
          onDirections={openGoogleMapsDirections}
          onClose={() => setSelectedDest(null)}
        />
      )}

      {/* ── Loading overlay ────────────────────────────────────────────── */}
      {loading && (
        <div style={{
          position: 'absolute', inset: 0, background: 'rgba(255,255,255,0.7)',
          backdropFilter: 'blur(6px)', zIndex: 50,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 14
        }}>
          <div style={{
            width: 40, height: 40, border: '3px solid #f4a4c6',
            borderTopColor: '#c24482', borderRadius: '50%',
            animation: 'spin .8s linear infinite'
          }} />
          <p style={{ fontFamily: 'Inter,sans-serif', color: '#c24482', fontWeight: 600, fontSize: 14 }}>
            Đang tải bản đồ...
          </p>
        </div>
      )}

      {/* ── Inline keyframes for marker ping & spinner ─────────────────── */}
      <style>{`
        @keyframes ping {
          75%, 100% { transform: scale(2); opacity: 0; }
        }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}

/* ─── Sub-components ──────────────────────────────────────────────────────── */

/* ─── FilterSelect: labelled dropdown with icon + hint ───────────────────── */
function FilterSelect({ icon, label, hint, value, onChange, options, placeholder = 'Tất cả' }) {
  const isActive = value !== '';
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* label row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
        {icon && <span style={{ fontSize: 12 }}>{icon}</span>}
        <span style={{
          fontFamily: 'Inter,sans-serif', fontSize: 11, fontWeight: 600,
          color: isActive ? 'var(--theme-primary, #c24482)' : 'var(--text-secondary, #544249)',
        }}>
          {label}
        </span>
        {isActive && (
          <span style={{
            marginLeft: 'auto', fontSize: 8, fontWeight: 700,
            color: 'var(--theme-primary, #c24482)',
            background: 'color-mix(in srgb, var(--theme-primary, #c24482) 10%, transparent)',
            borderRadius: 99, padding: '1px 6px',
          }}>đang lọc</span>
        )}
      </div>

      {/* hint */}
      {hint && (
        <p style={{
          fontFamily: 'Inter,sans-serif', fontSize: 9.5, color: 'var(--text-muted, #87717a)',
          margin: 0, lineHeight: 1.4,
        }}>
          {hint}
        </p>
      )}

      {/* select */}
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        style={{
          width: '100%', padding: '7px 10px',
          background: isActive
            ? 'color-mix(in srgb, var(--theme-primary, #c24482) 8%, var(--glass-bg, rgba(255,255,255,0.8)))'
            : 'var(--glass-bg, rgba(255,255,255,0.8))',
          border: isActive
            ? '1.5px solid color-mix(in srgb, var(--theme-primary, #c24482) 50%, transparent)'
            : '1px solid var(--glass-border, rgba(194,68,130,0.18))',
          borderRadius: 10, fontSize: 11.5,
          color: isActive ? 'var(--theme-primary, #c24482)' : 'var(--text-primary, #1f1a1e)',
          fontFamily: 'Inter,sans-serif', outline: 'none', cursor: 'pointer',
          fontWeight: isActive ? 600 : 400,
          transition: 'all .15s',
        }}
      >
        <option value="">{placeholder}</option>
        {options.map(o => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  );
}

/* ─── ActiveChip: removable tag shown in filter header ───────────────────── */
function ActiveChip({ label, onRemove }) {
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      background: 'rgba(255,255,255,0.25)', color: '#fff',
      borderRadius: 99, padding: '3px 8px 3px 7px',
      fontSize: 9.5, fontWeight: 600, fontFamily: 'Inter,sans-serif',
      border: '1px solid rgba(255,255,255,0.35)',
    }}>
      {label}
      <button
        onClick={onRemove}
        style={{
          background: 'rgba(255,255,255,0.3)', border: 'none',
          borderRadius: '50%', width: 13, height: 13,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer', color: '#fff', fontSize: 9, fontWeight: 700,
          padding: 0, lineHeight: 1, flexShrink: 0,
        }}
        title={`Bỏ lọc ${label}`}
      >
        ×
      </button>
    </span>
  );
}

function DestinationCard({ dest, onNavigate, onDirections, onClose }) {
  const imgSrc = getDestinationImage(dest['Destination Name'], dest.Type, dest.Country);
  const desc = dest.Description && String(dest.Description).toLowerCase() !== 'nan' && dest.Description.trim()
    ? fixDescription(dest.Description, dest['Destination Name'])
    : `Khám phá ${stripDisplayName(dest['Destination Name'])} — điểm đến ${(translateCategory(resolveCategoryKey(dest.Type, dest['Destination Name'])) || '').toLowerCase()} tại ${translateCountry(dest.Country)}. Lý tưởng vào ${translateSeason(dest['Best Season']).toLowerCase()}.`;

  return (
    <div style={{
      position: 'fixed', bottom: 20, left: 300, right: 20, zIndex: 40,
      maxWidth: 860, margin: '0 auto',
    }}>
      <div style={{
        background: 'rgba(255,255,255,0.88)', backdropFilter: 'blur(24px)',
        borderRadius: 20, border: '1px solid rgba(255,255,255,0.5)',
        boxShadow: '0 20px 60px rgba(136,19,55,0.1)',
        display: 'flex', gap: 0, overflow: 'hidden',
      }}>
        {/* image */}
        <div style={{ width: 180, minWidth: 180, flexShrink: 0 }}>
          <img
            src={imgSrc}
            alt={dest['Destination Name']}
            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
            onError={e => { e.target.src = getFallbackImage(dest['Destination Name'], dest.Type); }}
          />
        </div>

        {/* content */}
        <div style={{ flex: 1, padding: '18px 20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            {/* tag */}
            <span style={{
              fontFamily: 'Inter,sans-serif', fontSize: 8, fontWeight: 700,
              color: '#c24482', textTransform: 'uppercase', letterSpacing: '0.1em',
              background: 'rgba(194,68,130,0.08)', borderRadius: 99, padding: '2px 8px',
              display: 'inline-block', marginBottom: 8,
            }}>
              {translateCategory(resolveCategoryKey(dest.Type, dest['Destination Name'])) || 'Điểm Đến'}
            </span>

            {/* name */}
            <h3 style={{
              fontFamily: 'Inter,sans-serif', fontWeight: 700, fontSize: 18,
              color: '#1f1a1e', margin: '0 0 6px', lineHeight: 1.25,
            }}>
              {stripDisplayName(dest['Destination Name'])}
              <span style={{ color: '#87717a', fontWeight: 400, fontSize: 14 }}>
                {', '}{translateCountry(dest.Country)}
              </span>
            </h3>

            {/* meta row */}
            <div style={{ display: 'flex', gap: 12, marginBottom: 8, flexWrap: 'wrap' }}>
              {dest['Best Season'] && (
                <span style={{ fontSize: 10, color: '#765469', fontFamily: 'Inter,sans-serif' }}>
                  {SEASON_LABEL[dest['Best Season']] || dest['Best Season']}
                </span>
              )}
              {dest['Avg Rating'] && (
                <span style={{ fontSize: 10, color: '#765469', fontFamily: 'Inter,sans-serif' }}>
                  ⭐ {Number(dest['Avg Rating']).toFixed(1)}
                </span>
              )}
              {dest['Avg Cost (USD/day)'] && (
                <span style={{ fontSize: 10, color: '#765469', fontFamily: 'Inter,sans-serif' }}>
                  💵 ~${Math.round(dest['Avg Cost (USD/day)'])}/ngày
                </span>
              )}
            </div>

            {/* description */}
            <p style={{
              fontFamily: 'Inter,sans-serif', fontSize: 12, color: '#544249',
              lineHeight: 1.55, margin: 0,
              display: '-webkit-box', WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical', overflow: 'hidden',
            }}>
              {desc}
            </p>
          </div>

          {/* action buttons */}
          <div style={{ display: 'flex', gap: 8, marginTop: 14, flexWrap: 'wrap' }}>
            <button
              onClick={onNavigate}
              style={{
                background: '#c24482', color: '#fff', border: 'none',
                borderRadius: 99, padding: '8px 18px',
                fontFamily: 'Inter,sans-serif', fontSize: 10, fontWeight: 700,
                cursor: 'pointer', textTransform: 'uppercase', letterSpacing: '0.07em',
                boxShadow: '0 4px 14px rgba(194,68,130,0.3)',
              }}
            >
              Xem Chi Tiết
            </button>
            <button
              onClick={onDirections}
              style={{
                background: '#2563eb', color: '#fff', border: 'none',
                borderRadius: 99, padding: '8px 18px',
                fontFamily: 'Inter,sans-serif', fontSize: 10, fontWeight: 700,
                cursor: 'pointer', textTransform: 'uppercase', letterSpacing: '0.07em',
                display: 'flex', alignItems: 'center', gap: 5,
              }}
            >
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M17.657 16.657L13.414 20.9a2 2 0 01-2.827 0l-4.243-4.243a8 8 0 1111.314 0z"/>
                <path d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              Chỉ Đường
            </button>
          </div>
        </div>

        {/* close button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute', top: 10, right: 12,
            background: 'rgba(194,68,130,0.1)', border: 'none',
            borderRadius: '50%', width: 26, height: 26,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer', color: '#c24482', fontSize: 14, fontWeight: 700,
            lineHeight: 1,
          }}
        >
          ×
        </button>
      </div>
    </div>
  );
}
