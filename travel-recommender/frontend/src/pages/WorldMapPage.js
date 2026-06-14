import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-routing-machine';
import 'leaflet-routing-machine/dist/leaflet-routing-machine.css';
import { destinationsApi, recommendationsApi } from '../services/api';
import { getDestinationImage, getFallbackImage } from '../services/imageService';
import { translateDestinationName, translateCountry, translateCategory, translateSeason } from '../utils/translator';

// Fix default marker icon issue in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom pulsing pink marker icon for Ethereal Wanderer theme
const customIcon = L.divIcon({
  className: 'custom-leaflet-marker',
  html: `
    <div style="position: relative; width: 16px; height: 16px;">
      <div style="position: absolute; width: 28px; height: 28px; left: -6px; top: -6px; border-radius: 50%; background: #f4a4c6; opacity: 0.6; filter: blur(2px);" class="marker-pulse animate-ping"></div>
      <div style="position: relative; z-index: 20; width: 14px; height: 14px; background: #c24482; border: 2px solid white; border-radius: 50%; box-shadow: 0 4px 10px rgba(194,68,130,0.15);"></div>
    </div>
  `,
  iconSize: [16, 16],
  iconAnchor: [8, 8],
  popupAnchor: [0, -8]
});

// Helper component to center/zoom map when markers change
function MapController({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, zoom);
    }
  }, [center, zoom, map]);
  return null;
}

// Helper component to display the route
function RoutingMachine({ start, end }) {
  const map = useMap();

  useEffect(() => {
    if (!start || !end) return;

    const routingControl = L.Routing.control({
      waypoints: [
        L.latLng(start[0], start[1]),
        L.latLng(end[0], end[1])
      ],
      routeWhileDragging: false,
      showAlternatives: false,
      fitSelectedRoutes: true,
      lineOptions: {
        styles: [{ color: '#c24482', weight: 5, opacity: 0.8 }]
      },
      addWaypoints: false, // Prevents adding waypoints by dragging the line
      createMarker: (i, waypoint, n) => {
        // Create standard markers for start (A) and end (B)
        const markerIcon = L.icon({
          iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
          shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
          iconAnchor: [12, 41]
        });
        return L.marker(waypoint.latLng, {
          draggable: false,
          icon: markerIcon
        });
      }
    }).addTo(map);

    return () => {
      try {
        if (map && routingControl) {
          map.removeControl(routingControl);
        }
      } catch (e) {
        console.warn("Could not remove routing control", e);
      }
    };
  }, [map, start, end]);

  return null;
}

function WorldMapPage() {
  const navigate = useNavigate();
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filter states
  const [season, setSeason] = useState('');
  const [budget, setBudget] = useState('');
  const [category, setCategory] = useState('');
  
  // Map positioning state
  const [mapCenter, setMapCenter] = useState([20, 0]);
  const [mapZoom, setMapZoom] = useState(2);

  // Selected destination state for Quick Info Card
  const [selectedDest, setSelectedDest] = useState(null);

  // Routing states
  const [userLocation, setUserLocation] = useState(null);
  const [routingStart, setRoutingStart] = useState(null);
  const [routingEnd, setRoutingEnd] = useState(null);
  const [isRouting, setIsRouting] = useState(false);

  useEffect(() => {
    loadMapDestinations();
  }, []);

  const loadMapDestinations = async (currentFilters = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      const hasActiveFilters = Object.values(currentFilters).some(v => v !== '');
      let response;
      
      if (hasActiveFilters) {
        response = await recommendationsApi.getFiltered({
          season: currentFilters.season || undefined,
          budget: currentFilters.budget || undefined,
          category: currentFilters.category || undefined,
          limit: 150
        });
      } else {
        response = await destinationsApi.getAll({ limit: 150 });
      }
      
      if (response.data.success) {
        const list = hasActiveFilters ? response.data.recommendations : response.data.destinations;
        const validCoords = list.filter(
          d => d.destination_latitude !== null && d.destination_longitude !== null &&
               d.destination_latitude !== undefined && d.destination_longitude !== undefined &&
               !isNaN(d.destination_latitude) && !isNaN(d.destination_longitude)
        );
        setDestinations(validCoords);
        
        // Auto select first coordinates as default for quick-info card
        if (validCoords.length > 0) {
          setSelectedDest(validCoords[0]);
          if (hasActiveFilters) {
            setMapCenter([validCoords[0].destination_latitude, validCoords[0].destination_longitude]);
            setMapZoom(4);
          }
        }
      }
    } catch (err) {
      setError('Không thể tải dữ liệu bản đồ. Vui lòng thử lại sau.');
      console.error('Error loading map data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (type, value) => {
    const nextFilters = {
      season: type === 'season' ? value : season,
      budget: type === 'budget' ? value : budget,
      category: type === 'category' ? value : category
    };
    
    if (type === 'season') setSeason(value);
    if (type === 'budget') setBudget(value);
    if (type === 'category') setCategory(value);
    
    loadMapDestinations(nextFilters);
  };

  const resetFilters = () => {
    setSeason('');
    setBudget('');
    setCategory('');
    setMapCenter([20, 0]);
    setMapZoom(2);
    loadMapDestinations({});
  };

  const handleMarkerClick = (dest) => {
    setSelectedDest(dest);
    setMapCenter([dest.destination_latitude, dest.destination_longitude]);
    setMapZoom(5);
    // Auto-update route end point if currently routing
    if (isRouting && routingStart) {
      setRoutingEnd([dest.destination_latitude, dest.destination_longitude]);
    }
  };

  const handleDirections = () => {
    if (!selectedDest) return;
    
    const endCoords = [selectedDest.destination_latitude, selectedDest.destination_longitude];
    
    if (userLocation) {
      setRoutingStart(userLocation);
      setRoutingEnd(endCoords);
      setIsRouting(true);
    } else {
      // Request geolocation
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const loc = [position.coords.latitude, position.coords.longitude];
            setUserLocation(loc);
            setRoutingStart(loc);
            setRoutingEnd(endCoords);
            setIsRouting(true);
          },
          (error) => {
            alert("Không thể lấy vị trí của bạn để tính toán đường đi. Vui lòng cấp quyền truy cập vị trí trên trình duyệt.");
            console.error("Geolocation error:", error);
          },
          { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
      } else {
        alert("Trình duyệt của bạn không hỗ trợ định vị (Geolocation).");
      }
    }
  };

  const clearRoute = () => {
    setIsRouting(false);
    setRoutingStart(null);
    setRoutingEnd(null);
  };

  const infoImage = selectedDest 
    ? selectedDest.image || getDestinationImage(selectedDest['Destination Name'], selectedDest.Type, selectedDest.Country)
    : 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&q=80&w=1000';

  return (
    <div className="relative w-screen h-screen overflow-hidden text-left" style={{ backgroundColor: '#fff7fa' }}>
      
      {/* Fullscreen Map Canvas */}
      <main className="absolute inset-0 z-0 flex items-center justify-center">
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          style={{ height: '100%', width: '100%' }}
          zoomControl={false}
        >
          <MapController center={mapCenter} zoom={mapZoom} />
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          />

          {isRouting && routingStart && routingEnd && (
            <RoutingMachine start={routingStart} end={routingEnd} />
          )}

          {destinations.map((dest, idx) => (
            <Marker
              key={idx}
              position={[dest.destination_latitude, dest.destination_longitude]}
              icon={customIcon}
              eventHandlers={{
                click: () => handleMarkerClick(dest),
              }}
            >
              <Popup>
                <div className="p-1 max-w-[180px] text-left text-on-surface">
                  <h3 className="font-bold text-primary text-sm leading-tight mb-1" style={{ fontFamily: 'var(--font-display)' }}>
                    {dest['Destination Name']}
                  </h3>
                  <p className="text-secondary text-[10px] font-semibold mb-2">
                    📍 {translateCountry(dest.Country)}
                  </p>
                  <button
                    onClick={() => navigate(`/destinations/${encodeURIComponent(dest['Destination Name'])}`)}
                    className="w-full text-center bg-primary hover:bg-primary/95 text-white text-[10px] py-1.5 px-2 rounded-full font-bold transition duration-150 uppercase"
                  >
                    Xem Chi Tiết
                  </button>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </main>

      {/* Sidebar Filter Panel (Left side) */}
      <aside className="hidden lg:flex flex-col p-6 gap-4 bg-white/80 dark:bg-surface-container-low/80 backdrop-blur-2xl rounded-2xl h-[560px] w-80 fixed left-gutter top-[120px] border border-white/30 shadow-[40px_0_80px_rgba(136,19,55,0.05)] z-40 text-left">
        <header className="mb-4">
          <h2 className="font-display-lg text-xl font-bold text-primary">Bộ Lọc Bản Đồ</h2>
          <p className="font-label-caps text-[10px] text-secondary tracking-widest mt-1 uppercase">TÌM KIẾM ĐIỂM ĐẾN</p>
        </header>

        <div className="flex flex-col gap-4 flex-1">
          {/* Season Selector */}
          <div className="flex flex-col gap-1.5">
            <span className="font-label-caps text-[10px] font-bold text-secondary uppercase tracking-widest">Mùa du lịch</span>
            <select
              value={season}
              onChange={(e) => handleFilterChange('season', e.target.value)}
              className="w-full p-2 bg-white/60 border border-pink-200 rounded-xl focus:ring-2 focus:ring-pink-400 focus:outline-none text-xs text-on-surface"
            >
              <option value="">-- Chọn mùa --</option>
              <option value="Spring">Mùa Xuân</option>
              <option value="Summer">Mùa Hè</option>
              <option value="Autumn">Mùa Thu</option>
              <option value="Winter">Mùa Đông</option>
            </select>
          </div>

          {/* Budget Selector */}
          <div className="flex flex-col gap-1.5">
            <span className="font-label-caps text-[10px] font-bold text-secondary uppercase tracking-widest">Ngân sách</span>
            <select
              value={budget}
              onChange={(e) => handleFilterChange('budget', e.target.value)}
              className="w-full p-2 bg-white/60 border border-pink-200 rounded-xl focus:ring-2 focus:ring-pink-400 focus:outline-none text-xs text-on-surface"
            >
              <option value="">-- Chọn ngân sách --</option>
              <option value="Budget">Tiết kiệm</option>
              <option value="Moderate">Bình dân</option>
              <option value="Expensive">Cao cấp</option>
              <option value="Luxury">Sang trọng</option>
            </select>
          </div>

          {/* Category Selector */}
          <div className="flex flex-col gap-1.5">
            <span className="font-label-caps text-[10px] font-bold text-secondary uppercase tracking-widest">Loại hình du lịch</span>
            <select
              value={category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="w-full p-2 bg-white/60 border border-pink-200 rounded-xl focus:ring-2 focus:ring-pink-400 focus:outline-none text-xs text-on-surface"
            >
              <option value="">-- Chọn loại hình --</option>
              <option value="Beach">Du lịch Biển</option>
              <option value="Mountain">Du lịch Núi</option>
              <option value="Cultural">Du lịch Văn hóa</option>
              <option value="Nature">Khám phá Thiên nhiên</option>
              <option value="Adventure">Du lịch Mạo hiểm</option>
              <option value="Urban">Du lịch Đô thị</option>
            </select>
          </div>

          <button
            onClick={resetFilters}
            className="w-full mt-4 py-3 bg-white border border-pink-200 text-primary font-label-caps text-[10px] font-bold tracking-wider rounded-full hover:bg-pink-50 transition-all uppercase"
          >
            Xóa bộ lọc
          </button>
        </div>

        <div className="border-t border-pink-100 pt-3 text-[10px] text-secondary font-semibold">
          {loading ? (
            'Đang tải...'
          ) : error ? (
            <span className="text-red-500">{error}</span>
          ) : (
            `Tìm thấy ${destinations.length} điểm đến.`
          )}
        </div>
      </aside>

      {/* Quick Info Card (Asymmetric Layout at the Bottom) */}
      {selectedDest && (
        <div className="fixed bottom-6 left-6 right-6 lg:left-[360px] lg:right-6 z-40 transition-all duration-700 transform translate-y-0 opacity-100">
          <div className="bg-white/80 backdrop-blur-3xl rounded-2xl p-6 glass border border-white/40 shadow-[0_40px_80px_rgba(136,19,55,0.08)] flex flex-col md:flex-row gap-6 max-w-4xl mx-auto text-left">
            <div className="w-full md:w-1/3 aspect-[4/3] rounded-xl overflow-hidden shrink-0 shadow-inner">
              <img 
                alt={selectedDest['Destination Name']} 
                className="w-full h-full object-cover" 
                src={infoImage}
              />
            </div>
            
            <div className="flex flex-col justify-center flex-1">
              <span className="font-label-caps text-[10px] font-bold text-primary tracking-widest mb-1.5 uppercase">
                {translateCategory(selectedDest.Type) || 'ĐỀ XUẤT HÀNH TRÌNH'}
              </span>
              
              <h3 className="font-display-lg text-2xl font-bold text-primary mb-2" style={{ fontFamily: 'var(--font-display)' }}>
                {selectedDest['Destination Name']}, {translateCountry(selectedDest.Country)}
              </h3>
              
              <p className="font-body-lg text-xs md:text-sm text-on-surface-variant max-w-xl mb-4 leading-relaxed line-clamp-2">
                {selectedDest.Description && String(selectedDest.Description).toLowerCase() !== 'nan' && selectedDest.Description.trim() !== ''
                  ? selectedDest.Description
                  : `Khám phá ${selectedDest['Destination Name']} - điểm đến ${translateCategory(selectedDest.Type).toLowerCase()} tuyệt vời tại ${translateCountry(selectedDest.Country)}. Nơi đây nổi tiếng với phong cảnh đẹp, khí hậu lý tưởng vào ${translateSeason(selectedDest['Best Season']).toLowerCase()} và nhiều trải nghiệm du lịch hấp dẫn đang chờ đón bạn.`
                }
              </p>
              
              <div className="flex flex-wrap gap-3">
                <button 
                  onClick={() => navigate(`/destinations/${encodeURIComponent(selectedDest['Destination Name'])}`)}
                  className="bg-primary text-white rounded-full px-5 py-2.5 font-label-caps text-[10px] font-bold hover:opacity-90 transition-all shadow-md uppercase tracking-wider"
                >
                  Xem Chi Tiết
                </button>
                <button 
                  onClick={handleDirections}
                  className="bg-blue-600 text-white rounded-full px-5 py-2.5 font-label-caps text-[10px] font-bold hover:bg-blue-700 transition-all shadow-md uppercase tracking-wider flex items-center gap-1.5"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.242-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Chỉ Đường
                </button>
                {isRouting && (
                  <button 
                    onClick={clearRoute}
                    className="border border-red-500 text-red-500 rounded-full px-5 py-2.5 font-label-caps text-[10px] font-bold hover:bg-red-50 transition-all uppercase tracking-wider"
                  >
                    Hủy Chỉ Đường
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="absolute inset-0 bg-white/60 backdrop-blur-sm z-50 flex flex-col items-center justify-center">
          <div className="spinner border-t-primary w-10 h-10 border-4 border-pink-200 rounded-full animate-spin"></div>
          <p className="text-primary font-semibold mt-3">Đang tải bản đồ thế giới...</p>
        </div>
      )}
    </div>
  );
}

export default WorldMapPage;
