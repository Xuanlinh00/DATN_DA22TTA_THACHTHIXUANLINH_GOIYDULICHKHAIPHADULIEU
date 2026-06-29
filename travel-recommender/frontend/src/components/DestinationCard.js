import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDestinationImage, getFallbackImage, getExactDestinationImage, resolveCategoryKey } from '../services/imageService';
import { translateCountry, translateCategory, translateSeason, stripDisplayName } from '../utils/translator';
import './DestinationCard.css';

// ── Helpers ──────────────────────────────────────────────────────────────────

// ── Main Component ───────────────────────────────────────────────────────────

function DestinationCard({ destination, rank, selected = false, onMapPin, imageVariant = 0 }) {
  const navigate = useNavigate();
  const [imgError, setImgError] = useState(false);

  // Giữ country gốc (tiếng Anh) để tìm ảnh trên Unsplash chính xác hơn
  const rawCountry = destination['Country'] ?? '';

  // ── Field extraction ─────────────────────────────────────────────────────
  const name = destination['Destination Name'] ?? 'N/A';
  const displayName = stripDisplayName(name);
  const country = translateCountry(destination['Country'] ?? 'N/A');
  // ── Resolve correct category from name keywords (CSV Type field is unreliable) ──
  const rawType = destination['Type'] ?? '';
  const resolvedKey = resolveCategoryKey(rawType, name);
  const type = translateCategory(resolvedKey);
  const season = translateSeason(destination['Best Season'] ?? '');
  const avgCost = destination['Avg Cost (USD/day)'];
  const avgRating = destination['Avg Rating'] ?? destination['Rating'];
  const rawDesc = destination['Description'] ?? '';
  const countryFlag = destination['country_flag'] ?? '';

  const description = rawDesc && String(rawDesc).toLowerCase() !== 'nan'
    ? String(rawDesc)
    : '';

  // Ưu tiên: 1) exact curated image → 2) IMAGES_BY_TYPE (name-keyword resolution) → 3) fallback
  const exactImg = getExactDestinationImage(name, imageVariant);
  const imageUrl = imgError
    ? getFallbackImage(name, rawType, imageVariant)
    : (exactImg || getDestinationImage(name, rawType, rawCountry, imageVariant));

  const handleCardClick = () => {
    navigate(`/destinations/${encodeURIComponent(name)}`);
  };

  const handleMapPin = (e) => {
    e.stopPropagation();
    if (onMapPin) onMapPin(destination);
  };

  const getDynamicAspectRatio = (name) => {
    const sum = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const mod = sum % 3;
    if (mod === 0) return 'aspect-[3/4]'; // Tall portrait
    if (mod === 1) return 'aspect-[1/1]'; // Square
    return 'aspect-[4/3]'; // Landscape
  };

  return (
    <article
      className={`glass-panel p-4 pb-5 rounded-2xl shadow-[0_4px_20px_rgba(194,68,130,0.02)] hover:shadow-[0_12px_32px_rgba(194,68,130,0.06)] transition-all duration-500 cursor-pointer group flex flex-col justify-between bg-white border border-pink-100/30 hover:-translate-y-1 ${
        selected ? 'ring-2 ring-primary ring-offset-2' : ''
      }`}
      onClick={handleCardClick}
    >
      <div>
        {/* Image Frame with Staggered Aspect Ratio */}
        <div className={`overflow-hidden rounded-xl mb-4 relative w-full ${getDynamicAspectRatio(name)}`}>
          <img
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-[1.2s] ease-out"
            src={imageUrl}
            alt={name}
            loading="lazy"
            onError={() => setImgError(true)}
          />
          {rank && (
            <span className="absolute top-3 right-3 bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center font-bold text-[10px] shadow-md z-10">
              #{rank}
            </span>
          )}
          
          {/* Overlay Tag Badges */}
          <div className="absolute top-3 left-3 flex flex-wrap gap-1.5 z-10">
            {type && (
              <span className="bg-secondary/80 backdrop-blur-md text-white px-2.5 py-0.5 rounded-full font-label-caps text-[8px] uppercase tracking-wider">
                {type}
              </span>
            )}
            {season && (
              <span className="bg-primary/85 backdrop-blur-md text-white px-2.5 py-0.5 rounded-full font-label-caps text-[8px] uppercase tracking-wider">
                {season}
              </span>
            )}
          </div>

          {/* Floating Map Pin Button */}
          {onMapPin && (
            <button
              type="button"
              className="absolute bottom-3 right-3 w-8 h-8 rounded-full bg-white/90 backdrop-blur-md text-primary flex items-center justify-center shadow-md hover:bg-primary hover:text-white transition-all active:scale-90 z-20"
              onClick={handleMapPin}
              title="Xem trên bản đồ"
            >
              <span className="material-symbols-outlined text-[16px]">map</span>
            </button>
          )}
        </div>

        {/* Content Body */}
        <div className="px-1 text-left">
          <h3 className="font-display text-lg text-primary mb-1 font-bold group-hover:text-primary/80 transition-colors">
            {displayName}
          </h3>
          
          <div className="flex items-center gap-1 text-secondary/70 mb-2">
            <span className="material-symbols-outlined text-[14px]">location_on</span>
            <span className="font-label-caps text-[9px] tracking-wider uppercase font-semibold">
              {country} {countryFlag}
            </span>
          </div>

          {/* Inline rating & budget details */}
          <div className="flex items-center gap-2 text-[11px] text-secondary/80 mb-3">
            {avgRating && (
              <span className="flex items-center gap-0.5">
                <span className="material-symbols-outlined text-[12px] text-amber-500" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
                <span className="font-bold text-on-surface">{Number(avgRating).toFixed(1)}</span>
              </span>
            )}
            {avgRating && avgCost && <span className="opacity-40">•</span>}
            {avgCost != null && (
              <span>
                <span className="font-semibold text-primary">${Number(avgCost).toLocaleString()}</span>/ngày
              </span>
            )}
          </div>

          {description && (
            <p className="font-body-md text-on-surface-variant text-[11px] line-clamp-2 leading-relaxed opacity-90">
              {description}
            </p>
          )}
        </div>
      </div>
    </article>
  );
}

export default DestinationCard;
