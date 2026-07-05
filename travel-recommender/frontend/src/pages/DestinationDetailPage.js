import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { destinationsApi, getOrCreateUserId } from '../services/api';
import { getDatasetImage, getDestinationImage, getFallbackImage, getExactDestinationImage, resolveCategoryKey } from '../services/imageService';
import DestinationCard from '../components/DestinationCard';
import ClimateChart from '../components/ClimateChart';
import Footer from '../components/Footer';
import { translateCountry, translateCategory, translateSeason, translateDestinationName, stripDisplayName, fixDescription } from '../utils/translator';
import './DestinationDetailPage.css';

function DestinationDetailPage() {
  const { name } = useParams();
  const navigate = useNavigate();
  const [destination, setDestination] = useState(null);
  const [similarDestinations, setSimilarDestinations] = useState([]);
  const [weather, setWeather] = useState(null);
  const [climate, setClimate] = useState(null);
  const [climateLoading, setClimateLoading] = useState(false);
  const [climateError, setClimateError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // Star rating state
  const [myRating, setMyRating] = useState(null);      // user's current rating (1-5 or null)
  const [hoverRating, setHoverRating] = useState(0);   // star being hovered
  const [ratingSubmitting, setRatingSubmitting] = useState(false);
  const [ratingMessage, setRatingMessage] = useState(null);

  useEffect(() => {
    loadDestinationDetails();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [name]);

  const loadDestinationDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      setWeather(null);
      setClimate(null);
      setClimateError(null);

      // Load destination details
      const response = await destinationsApi.getByName(name);
      if (response.data.success) {
        setDestination(response.data.destination);
      }

      // Load similar destinations
      try {
        const similarResponse = await destinationsApi.getSimilar(name);
        if (similarResponse.data.success) {
          setSimilarDestinations(similarResponse.data.similar.slice(0, 4));
        }
      } catch (err) {
        console.log('No similar destinations found');
      }

      // Load weather info
      try {
        const weatherResponse = await destinationsApi.getWeather(name);
        if (weatherResponse.data.success) {
          setWeather(weatherResponse.data.weather);
        }
      } catch (err) {
        console.log('Weather data not available');
      }

      // Load historical climate data (Open-Meteo)
      setClimateLoading(true);
      try {
        const climateResponse = await destinationsApi.getClimate(name);
        if (climateResponse.data.success) {
          setClimate(climateResponse.data);
        }
      } catch (err) {
        console.log('Climate data not available:', err.message);
        setClimateError('Không thể tải dữ liệu khí hậu.');
      } finally {
        setClimateLoading(false);
      }

      // Load user's existing rating for this destination
      try {
        const userId = getOrCreateUserId();
        const ratingResp = await destinationsApi.getMyRating(name, userId);
        if (ratingResp.data.has_rated) {
          setMyRating(ratingResp.data.rating);
        }
      } catch (err) {
        // Not rated yet — silent fail is fine
      }

    } catch (err) {
      setError('Không tìm thấy điểm đến này.');
      console.error('Error loading destination:', err);
    } finally {
      setLoading(false);
    }
  };



  if (loading) {
    return (
      <div className="loading flex flex-col items-center justify-center py-40">
        <div className="spinner border-t-primary w-10 h-10 border-4 border-pink-200 rounded-full animate-spin"></div>
        <p className="text-secondary mt-3">Đang tải chi tiết...</p>
      </div>
    );
  }

  if (error || !destination) {
    return (
      <div className="error text-center py-20">
        <p className="text-red-500 font-medium mb-4">{error || 'Không tìm thấy điểm đến'}</p>
        <button onClick={() => navigate('/destinations')} className="bg-primary text-white px-6 py-2.5 rounded-full font-bold">
          Quay Lại Danh Sách
        </button>
      </div>
    );
  }

  // Ưu tiên: 1) exact curated image → 2) IMAGES_BY_TYPE (name-keyword resolution) → 3) fallback
  const imageUrl = getDatasetImage(destination)
    || getExactDestinationImage(destination['Destination Name'])
    || getDestinationImage(destination['Destination Name'], destination.Type, destination.Country);

  // Resolve correct category from name keywords (CSV Type field is unreliable)
  const resolvedCategory = resolveCategoryKey(destination.Type, destination['Destination Name']);

  const destName = stripDisplayName(destination['Destination Name']);
  const fullName = destination['Destination Name'] ?? 'N/A';
  const hasDesc = destination.Description && String(destination.Description).toLowerCase() !== 'nan' && destination.Description.trim() !== '';
  const rawDesc = hasDesc ? destination.Description : null;
  const descriptionText = rawDesc
    ? fixDescription(rawDesc, fullName)
    : `Khám phá ${destName} - điểm đến ${translateCategory(resolvedCategory).toLowerCase()} tuyệt vời tại ${translateCountry(destination.Country)}. Nơi đây nổi tiếng với phong cảnh đẹp, khí hậu lý tưởng vào ${translateSeason(destination['Best Season']).toLowerCase()} và nhiều trải nghiệm du lịch hấp dẫn đang chờ đón bạn.`;

  const hasCoords = destination.destination_latitude != null && destination.destination_longitude != null &&
                    !isNaN(destination.destination_latitude) && !isNaN(destination.destination_longitude);
  const mapUrl = hasCoords
    ? `https://maps.google.com/maps?q=${destination.destination_latitude},${destination.destination_longitude}&hl=vi&z=12&output=embed`
    : `https://maps.google.com/maps?q=${encodeURIComponent(destination['Destination Name'] + ' ' + destination.Country)}&hl=vi&z=12&output=embed`;


  return (
    <div className="min-h-screen text-left" style={{ backgroundColor: '#fff7fa' }}>
      <Helmet>
        <title>{destName} - NÂU</title>
        <meta name="description" content={descriptionText} />
        {/* Open Graph / Facebook */}
        <meta property="og:type" content="website" />
        <meta property="og:title" content={`${destName} | NÂU`} />
        <meta property="og:description" content={descriptionText} />
        <meta property="og:image" content={imageUrl} />
        <meta property="og:image:width" content="1200" />
        <meta property="og:image:height" content="630" />
        {/* Twitter Card */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={`${destName} | NÂU`} />
        <meta name="twitter:description" content={descriptionText} />
        <meta name="twitter:image" content={imageUrl} />
      </Helmet>
      
      {/* Back Button Pill */}
      <button 
        className="fixed top-24 left-10 z-50 glass-panel px-5 py-2.5 rounded-full shadow-lg text-primary hover:bg-white/40 active:scale-95 transition-all flex items-center gap-2 font-label-caps text-[10px] uppercase font-bold"
        onClick={() => navigate(-1)}
      >
        <span className="material-symbols-outlined text-xs">arrow_back</span>
        Quay Lại
      </button>

      {/* Main Content: Split Screen Layout */}
      <main className="flex flex-col md:flex-row min-h-screen pt-32 pb-10 px-4 md:px-0 max-w-7xl mx-auto md:pl-[8%]">
        
        {/* Left Half: Image & Climate Chart */}
        <section className="w-full md:w-1/2 flex flex-col gap-6">
          <div className="w-full h-[512px] md:h-[calc(100vh-160px)] relative overflow-hidden rounded-3xl shadow-2xl shrink-0">
            <img 
              alt={destName} 
              className="w-full h-full object-cover" 
              src={imageUrl}
              onError={(e) => {
                e.target.src = getFallbackImage(destination['Destination Name'], destination.Type);
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent"></div>
            
            <div className="absolute bottom-10 left-10 text-white z-10 text-left">
              <h1 className="font-display-lg text-display-lg tracking-tight leading-none text-white">
                {destName}
              </h1>
              <p className="font-label-caps text-label-caps uppercase tracking-widest mt-3 flex items-center gap-1">
                <span className="material-symbols-outlined text-sm">location_on</span>
                {translateCountry(destination.Country)} {destination.country_flag}
              </p>
            </div>
          </div>

          {/* ── Climate Chart Widget moved here (dưới hình) ─────────────────────────── */}
          {(climateLoading || climate || climateError) && (
            <div className="glass-panel p-6 rounded-2xl shadow-sm text-left">
              <ClimateChart
                climateData={climate?.climate}
                bestMonths={climate?.best_months || []}
                year={climate?.year}
                loading={climateLoading}
                error={climateError}
              />
            </div>
          )}
        </section>

        {/* Content Section (Right Half) */}
        <section className="w-full md:w-1/2 px-4 md:px-12 flex flex-col gap-8 pt-10 md:pt-0">
          
          {/* Description Glass Card */}
          <div className="glass-panel p-8 rounded-2xl shadow-[0_40px_80px_rgba(136,19,55,0.05)] transform md:-translate-x-12 relative z-20 text-left">
            <h2 className="font-display-lg text-headline-md text-primary mb-4">
              {destination['UNESCO Site'] === 'Yes'
                ? `Di Sản UNESCO · ${translateCategory(resolvedCategory) || 'Điểm Đến'}`
                : resolvedCategory
                  ? `Điểm Đến ${translateCategory(resolvedCategory)}`
                  : `Khám Phá ${destName}`}
            </h2>
            <p className="font-body-lg text-body-lg text-on-surface-variant leading-relaxed text-sm md:text-base">
              {descriptionText}
            </p>
          </div>

          {/* Stats & Metadata (Weather & Country Info Cards) */}
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Weather Card */}
            <div className="glass-panel flex-1 p-6 rounded-2xl flex items-center gap-4 shadow-sm border-r border-white/30 text-left">
              <div className="w-12 h-12 rounded-full bg-secondary-container flex items-center justify-center text-primary shrink-0">
                <span className="material-symbols-outlined text-2xl">light_mode</span>
              </div>
              <div>
                <p className="font-label-caps text-[9px] text-secondary font-bold uppercase tracking-wider">Khí Hậu Bản Địa</p>
                <h3 className="text-sm font-bold text-on-surface mt-0.5">
                  {weather ? `${weather.temp}°C | ${weather.description}` : `${translateSeason(destination['Best Season'])}`}
                </h3>
              </div>
            </div>

            {/* Country Metadata Card */}
            <div className="glass-panel flex-1 p-6 rounded-2xl flex items-center gap-4 shadow-sm border-r border-white/30 text-left">
              <div className="w-12 h-12 rounded-full bg-tertiary-fixed-dim/30 flex items-center justify-center text-primary shrink-0">
                <span className="material-symbols-outlined text-2xl">payments</span>
              </div>
              <div>
                <p className="font-label-caps text-[9px] text-secondary font-bold uppercase tracking-wider">Tiền Tệ & Thủ Đô</p>
                <h3 className="text-sm font-bold text-on-surface mt-0.5">
                  {destination.country_currency || 'N/A'} | {destination.country_capital || 'N/A'}
                </h3>
              </div>
            </div>
          </div>

          {/* Grid Metadata details */}
          <div className="glass-panel p-6 rounded-2xl grid grid-cols-2 gap-4 text-left">
            <div>
              <p className="text-[10px] font-bold text-secondary uppercase tracking-wider">Loại hình</p>
              <p className="text-sm font-semibold text-primary mt-1">{translateCategory(resolvedCategory)}</p>
            </div>
            <div>
              <p className="text-[10px] font-bold text-secondary uppercase tracking-wider">Chi phí tb</p>
              <p className="text-sm font-semibold text-primary mt-1">${destination['Avg Cost (USD/day)']}/ngày</p>
            </div>
            {destination['UNESCO Site'] === 'Yes' && (
              <div className="col-span-2 border-t border-pink-100/50 pt-3 flex items-center gap-1.5 text-xs text-primary font-bold">
                <span className="material-symbols-outlined text-sm">auto_awesome</span>
                <span>Di Sản Thế Giới UNESCO</span>
              </div>
            )}
          </div>

          <div className="glass-panel p-6 rounded-2xl shadow-sm text-left flex flex-col">
            <p className="font-label-caps text-[9px] text-secondary font-bold uppercase tracking-wider mb-1">
              Bản Đồ
            </p>
            <h3 className="text-sm font-bold text-on-surface mb-3">
              Vị trí {destName}
            </h3>
            <div className="w-full h-64 rounded-xl overflow-hidden shadow-inner">
              <iframe
                title="map"
                width="100%"
                height="100%"
                style={{ border: 0 }}
                loading="lazy"
                allowFullScreen
                src={mapUrl}
              ></iframe>
            </div>
          </div>

          {/* ── Star Rating Widget ───────────────────────────── */}
          <div className="glass-panel p-6 rounded-2xl shadow-sm text-left">
            <p className="font-label-caps text-[9px] text-secondary font-bold uppercase tracking-wider mb-1">
              Đánh Giá Của Bạn
            </p>
            <h3 className="text-sm font-bold text-on-surface mb-3">
              {myRating ? `Bạn đã đánh giá ${myRating} ⭐` : 'Hãy cho chúng tôi biết trải nghiệm của bạn!'}
            </h3>
            {/* 5 stars */}
            <div className="flex gap-1 mb-3">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  id={`star-${star}`}
                  disabled={ratingSubmitting}
                  className="text-3xl transition-all duration-150 hover:scale-125 active:scale-95 disabled:opacity-50 cursor-pointer"
                  style={{
                    color: star <= (hoverRating || myRating || 0) ? '#f59e0b' : '#d1d5db',
                    filter: star <= (hoverRating || myRating || 0) ? 'drop-shadow(0 0 4px rgba(245,158,11,0.5))' : 'none',
                  }}
                  onMouseEnter={() => setHoverRating(star)}
                  onMouseLeave={() => setHoverRating(0)}
                  onClick={async () => {
                    setRatingSubmitting(true);
                    setRatingMessage(null);
                    try {
                      const userId = getOrCreateUserId();
                      const resp = await destinationsApi.rateDestination(name, star, userId);
                      if (resp.data.success) {
                        setMyRating(star);
                        setRatingMessage({ type: 'success', text: `✅ ${resp.data.message}` });
                      }
                    } catch {
                      setRatingMessage({ type: 'error', text: '❌ Không thể lưu đánh giá, vui lòng thử lại.' });
                    } finally {
                      setRatingSubmitting(false);
                      setTimeout(() => setRatingMessage(null), 3500);
                    }
                  }}
                >
                  ★
                </button>
              ))}
            </div>
            {ratingMessage && (
              <p className={`text-xs font-semibold mt-1 ${
                ratingMessage.type === 'success' ? 'text-emerald-600' : 'text-rose-500'
              }`}>
                {ratingMessage.text}
              </p>
            )}
            <p className="text-[10px] text-secondary opacity-60 mt-1">
              Đánh giá của bạn giúp cải thiện thuật toán Collaborative Filtering.
            </p>
          </div>

          {/* Action CTA */}
          <div className="mt-4 flex justify-end">
            <button 
              onClick={() => navigate('/recommend')}
              className="bg-primary text-white px-8 py-4 rounded-full font-label-caps text-[11px] font-bold tracking-widest hover:opacity-90 transition-all shadow-lg shadow-primary/25 active:scale-95 uppercase"
            >
              GỢI Ý CÁ NHÂN HÓA ✨
            </button>
          </div>

        </section>
      </main>

      {/* Similar Destinations Section */}
      {similarDestinations.length > 0 && (
        <section className="py-20 px-6 max-w-7xl mx-auto md:pl-[8%] border-t border-pink-100 mt-20 text-left">
          <h2 className="font-display-lg text-headline-lg text-primary mb-10">Điểm Đến Tương Tự</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {similarDestinations.map((dest, index) => (
              <DestinationCard key={index} destination={dest} imageVariant={index} />
            ))}
          </div>
        </section>
      )}

      <Footer />

    </div>
  );
}

export default DestinationDetailPage;
