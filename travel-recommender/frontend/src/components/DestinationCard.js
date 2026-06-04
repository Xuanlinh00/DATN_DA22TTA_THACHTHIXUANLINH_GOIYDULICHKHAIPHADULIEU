import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDestinationImage } from '../services/imageService';
import './DestinationCard.css';

// ── Helpers ──────────────────────────────────────────────────────────────────

function StarRating({ value }) {
  if (!value && value !== 0) return <span className="text-xs text-secondary opacity-50">N/A</span>;
  const num = Number(value);
  const filled = Math.round(num);
  return (
    <div className="flex items-center gap-0.5" title={`${num.toFixed(1)} / 5`}>
      {Array.from({ length: 5 }, (_, i) => (
        <span
          key={i}
          className="material-symbols-outlined text-[14px]"
          style={{ 
            fontVariationSettings: "'FILL' " + (i < filled ? 1 : 0),
            color: i < filled ? '#f59e0b' : '#dac0c9'
          }}
        >
          star
        </span>
      ))}
      <span className="text-xs font-bold text-on-surface ml-1">{num.toFixed(1)}</span>
    </div>
  );
}

// ── Main Component ───────────────────────────────────────────────────────────

function DestinationCard({ destination, rank, selected = false, onMapPin }) {
  const navigate = useNavigate();
  const [imgError, setImgError] = useState(false);

  // ── Field extraction ─────────────────────────────────────────────────────
  const name = destination['Destination Name'] ?? 'N/A';
  const country = destination['Country'] ?? 'N/A';
  const type = destination['Type'] ?? '';
  const season = destination['Best Season'] ?? '';
  const avgCost = destination['Avg Cost (USD/day)'];
  const avgRating = destination['Avg Rating'] ?? destination['Rating'];
  const rawDesc = destination['Description'] ?? '';
  const countryFlag = destination['country_flag'] ?? '';

  const description = rawDesc && String(rawDesc).toLowerCase() !== 'nan'
    ? String(rawDesc)
    : '';

  const imageUrl = !imgError && (destination.image || getDestinationImage(name, type))
    ? destination.image || getDestinationImage(name, type)
    : 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800';

  const handleCardClick = () => {
    navigate(`/destinations/${encodeURIComponent(name)}`);
  };

  const handleMapPin = (e) => {
    e.stopPropagation();
    if (onMapPin) onMapPin(destination);
  };

  return (
    <article
      className={`glass-panel p-5 rounded-xl hover:shadow-[0_40px_80px_rgba(136,19,55,0.08)] transition-all duration-700 cursor-pointer group flex flex-col justify-between ${
        selected ? 'ring-2 ring-primary ring-offset-2' : ''
      }`}
      onClick={handleCardClick}
    >
      <div>
        {/* Image Frame */}
        <div className="overflow-hidden rounded-lg mb-4 relative aspect-[4/3] w-full">
          <img
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000"
            src={imageUrl}
            alt={name}
            loading="lazy"
            onError={() => setImgError(true)}
          />
          {rank && (
            <span className="absolute top-3 right-3 bg-primary-container text-white w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs shadow-md">
              #{rank}
            </span>
          )}
          <div className="absolute top-3 left-3 flex flex-wrap gap-1.5">
            {type && (
              <span className="bg-secondary-container/80 backdrop-blur-md text-on-secondary-container px-3 py-1 rounded-full font-label-caps text-[9px] uppercase tracking-wider">
                {type}
              </span>
            )}
            {season && (
              <span className="bg-tertiary-fixed/80 backdrop-blur-md text-on-tertiary-fixed-variant px-3 py-1 rounded-full font-label-caps text-[9px] uppercase tracking-wider">
                {season}
              </span>
            )}
          </div>
        </div>

        {/* Content Body */}
        <div className="px-1 text-left">
          <h3 className="font-display-lg text-headline-md text-primary mb-1 truncate font-bold">
            {name}
          </h3>
          <div className="flex items-center gap-1 text-secondary opacity-80 mb-3">
            <span className="material-symbols-outlined text-[16px] text-primary">location_on</span>
            <span className="font-label-caps text-[10px] tracking-wider uppercase font-semibold">
              {country} {countryFlag}
            </span>
          </div>

          {description && (
            <p className="font-body-md text-on-surface-variant text-xs line-clamp-2 mb-4 leading-relaxed">
              {description}
            </p>
          )}
        </div>
      </div>

      {/* Metadata & Actions footer */}
      <div>
        <div className="flex justify-between items-center px-1 py-3 border-t border-pink-100/50 mt-2">
          <StarRating value={avgRating} />
          
          {avgCost != null && (
            <div className="flex items-center text-xs font-bold text-on-surface">
              <span className="material-symbols-outlined text-xs text-primary mr-0.5">payments</span>
              <span>${Number(avgCost).toLocaleString()}</span>
              <span className="text-[9px] text-secondary font-medium ml-0.5">/ngày</span>
            </div>
          )}
        </div>

        <div className="flex gap-2 mt-2">
          <button
            className="flex-1 py-3 bg-primary text-white rounded-full font-label-caps text-[10px] tracking-wider uppercase hover:opacity-90 active:scale-95 transition-all text-center"
            onClick={handleCardClick}
          >
            Chi tiết
          </button>
          {onMapPin && (
            <button
              className="flex-1 py-3 glass text-primary rounded-full font-label-caps text-[10px] tracking-wider uppercase hover:bg-white/40 active:scale-95 transition-all flex items-center justify-center gap-1"
              onClick={handleMapPin}
            >
              <span className="material-symbols-outlined text-xs">map</span>
              Bản đồ
            </button>
          )}
        </div>
      </div>
    </article>
  );
}

export default DestinationCard;