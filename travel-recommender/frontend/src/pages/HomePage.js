import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { recommendationsApi, dataApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import DestinationCard from '../components/DestinationCard';
import { translateDestinationName, translateCountry, translateCategory } from '../utils/translator';
import './HomePage.css';


/* ── Season helpers ──────────────────────────────────────────── */
const SEASON_LABELS = { Spring: 'Xuân', Summer: 'Hạ', Autumn: 'Thu', Winter: 'Đông' };
const SEASON_EMOJIS = { Spring: '🌸', Summer: '☀️', Autumn: '🍂', Winter: '❄️' };

function detectSeason() {
  const m = new Date().getMonth() + 1;
  if (m >= 1 && m <= 3) return 'Spring';
  if (m >= 4 && m <= 6) return 'Summer';
  if (m >= 7 && m <= 9) return 'Autumn';
  return 'Winter'; // 10, 11, 12
}

function HomePage() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentSeason] = useState(detectSeason);
  // Live stats from real data
  const [stats, setStats] = useState(null);
  // Top destination for floating card
  const [topDest, setTopDest] = useState(null);
  // Whether showing personalized or seasonal recs
  const [isPersonalized, setIsPersonalized] = useState(false);

  /* Load recommendations + live stats */
  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        setIsPersonalized(false);

        // Try personalized (CF) first if user is logged in
        let recsLoaded = false;
        if (isAuthenticated && user?.username) {
          try {
            const cfRes = await recommendationsApi.getFiltered({
              user_id: user.username,
              season: currentSeason,
              limit: 6,
            });
            if (cfRes.data.success && cfRes.data.recommendations?.length > 0) {
              const recs = cfRes.data.recommendations;
              setDestinations(recs);
              if (recs.length > 0) setTopDest(recs[0]);
              setIsPersonalized(true);
              recsLoaded = true;
            }
          } catch (_) {
            // fall through to seasonal
          }
        }

        // Fallback: seasonal recommendations
        if (!recsLoaded) {
          const seaRes = await recommendationsApi.getSeasonal(currentSeason, 6);
          if (seaRes.data.success) {
            const recs = seaRes.data.recommendations;
            setDestinations(recs);
            if (recs.length > 0) setTopDest(recs[0]);
          }
        }

        // Load stats in parallel
        const statsRes = await dataApi.getStats();
        if (statsRes.data.success) setStats(statsRes.data.data);

      } catch (err) {
        setError('Không thể tải gợi ý. Vui lòng thử lại.');
      } finally {
        setLoading(false);
      }
    })();
  }, [isAuthenticated, user, currentSeason]);

  /* Parallax effect for floating elements in hero */
  useEffect(() => {
    const handleMouseMove = (e) => {
      const amount = 20;
      const x = (e.clientX / window.innerWidth - 0.5) * amount;
      const y = (e.clientY / window.innerHeight - 0.5) * amount;
      
      document.querySelectorAll('.floating').forEach((el, index) => {
        const speed = 0.15 + (index * 0.1);
        el.style.transform = `translate(${x * speed}px, ${y * speed}px)`;
      });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div className="home-page overflow-x-hidden font-body-md" style={{ backgroundColor: '#fff7fa' }}>
      


      {/* ══════════════════ HERO SECTION (Split Screen with offset) ══════════════════ */}
      <section className="relative min-h-screen pt-40 pb-20 px-container-padding flex flex-col md:flex-row items-center gap-asymmetric-gap-lg overflow-hidden">
        {/* Background Decorative Orbs */}
        <div className="absolute -bottom-20 -left-20 w-96 h-96 bg-primary/5 rounded-full blur-[100px] pointer-events-none"></div>
        <div className="absolute top-20 right-0 w-64 h-64 bg-secondary/10 rounded-full blur-[80px] pointer-events-none"></div>

        {/* Text Content (Left Half) */}
        <div className="w-full md:w-1/2 z-10 space-y-6 text-left glass-hero-text p-8 md:p-10 rounded-3xl border border-white/20 backdrop-blur-md bg-white/25">
          <div className="hero-eyebrow">
            Trợ lý gợi ý du lịch thông minh
          </div>
          <h1 className="font-display-lg text-display-lg leading-[1.1] font-bold text-on-surface">
            <span className="text-gradient">Gợi ý điểm đến</span><br />
            <span>du lịch quốc tế.</span>
          </h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant max-w-lg leading-relaxed">
            Hệ thống sử dụng các thuật toán khai phá dữ liệu để giúp bạn nhanh chóng tìm kiếm và lựa chọn địa điểm du lịch tối ưu nhất.
          </p>
          <div className="flex flex-wrap gap-4 pt-4">
            <button 
              className="btn-premium-secondary"
              onClick={() => navigate('/recommend')}
            >
              GỢI Ý CÁ NHÂN HÓA ✨
            </button>
          </div>
        </div>

        {/* Visual Content (Right Half - Teardrop Beach & Floating Cards) */}
        <div className="w-full md:w-1/2 relative">
          <div className="relative w-full aspect-square max-w-[320px] sm:max-w-[420px] xl:max-w-[460px] 2xl:max-w-[540px] ml-auto md:mr-24">
            {/* Main Image - Teardrop/Blob Shape */}
            <div className="w-full h-full overflow-hidden blob-shape shadow-2xl relative border border-white/40">
              <img 
                alt="Tropical Beach" 
                className="w-full h-full object-cover" 
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuChl1Mjof0tQQxGArnAuLriyebHPeUhk6VXhZEiJGpZeBnbJqT3N4TT6a7AUv-X_q_bQl1yX6Cv581KnPEaAtm8lTi9mmEdIV1Q3ycvKtk3bmJmv1pLcA59YZAOgNCENR0pmBzJBE6MYEhrizOR59b-Z9kgLyQz5RtFV6u3nqqe00PfDoISaGDL7jrtBhZp3yRiIZGUVrFGYblBYvWDiBjP6avMUTIyeUbW0QtEIJTEvl5DygIwH8GYF2LNz-cCwnruWE2sMop4HKA"
              />
            </div>
            {/* Floating Card 1: AI Insight */}
            <div className="absolute -top-10 -left-10 glass p-6 rounded-xl floating shadow-xl w-48 z-20 border border-white/40">
              <div className="flex items-center gap-3 mb-2">
                <span className="material-symbols-outlined text-primary text-lg">auto_awesome</span>
                <span className="text-xs font-bold font-label-caps text-primary">GỢI Ý AI</span>
              </div>
              <p className="text-[10px] leading-tight text-on-surface-variant">
                {topDest
                  ? `Hàng đầu mùa ${SEASON_LABELS[currentSeason]}: ${translateCategory(topDest.Type) || 'Điểm đến'}`
                  : 'Đang phân tích dữ liệu...'}
              </p>
            </div>
            {/* Floating Card 2: Top destination tag (real data) */}
            <div className="absolute bottom-10 -right-5 glass p-4 rounded-full floating shadow-xl z-20 flex items-center gap-3 border border-white/40">
              <div className="w-10 h-10 rounded-full bg-secondary-container flex items-center justify-center text-primary">
                <span className="material-symbols-outlined text-sm">flight</span>
              </div>
              <div>
                <div className="text-[10px] font-bold">
                  {topDest ? topDest['Destination Name'] : '...'}
                </div>
                <div className="text-[8px] text-on-surface-variant font-semibold">
                  {topDest ? translateCountry(topDest['Country']) : ''}
                </div>
              </div>
            </div>
            {/* Floating Card 3: User Avatar bubble */}
            <div className="absolute top-1/2 -left-20 glass p-3 rounded-2xl floating shadow-lg z-20 border border-white/40">
              <div className="flex -space-x-2">
                <img alt="User" className="w-8 h-8 rounded-full border-2 border-white" src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&fit=crop" />
                <img alt="User" className="w-8 h-8 rounded-full border-2 border-white" src="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=80&fit=crop" />
                <div className="w-8 h-8 rounded-full bg-primary-fixed flex items-center justify-center text-[10px] font-bold border-2 border-white text-primary">+12</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════ RECOMMENDATIONS (Personalized or Seasonal) ══════════════════ */}
      <section className="py-20 px-6 md:px-12 max-w-6xl mx-auto" style={{ background: 'transparent' }}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            {isPersonalized ? (
              <span className="inline-block px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-widest mb-4"
                style={{ background: 'color-mix(in srgb, var(--text-accent,#c24482) 10%, white)', color: 'var(--text-accent,#c24482)' }}>
                🤖 Gợi ý dành riêng cho bạn
              </span>
            ) : (
              <span className="inline-block px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-widest mb-4"
                style={{ background: 'color-mix(in srgb, var(--text-accent,#c24482) 10%, white)', color: 'var(--text-accent,#c24482)' }}>
                ⭐ Gợi ý theo mùa
              </span>
            )}
            <h2 className="font-display-lg text-headline-lg text-primary">
              {isPersonalized
                ? `👋 Xin chào, ${user?.fullName || user?.username}!`
                : `${SEASON_EMOJIS[currentSeason]} Mùa ${SEASON_LABELS[currentSeason]}`}
            </h2>
            <p className="text-secondary mt-3 max-w-lg mx-auto text-sm">
              {isPersonalized
                ? 'Dựa trên sở thích và lịch sử của bạn, chúng tôi đã tuyển chọn những điểm đến hoàn hảo nhất'
                : 'Những thiên đường nghỉ dưỡng và điểm đến lý tưởng nhất cho thời điểm hiện tại'}
            </p>
          </div>

          {loading && (
            <div className="loading">
              <div className="spinner" />
              <p className="text-secondary">Đang phân tích các cụm dữ liệu…</p>
            </div>
          )}

          {error && (
            <div className="error">
              <p>{error}</p>
              <button className="bg-primary text-white py-2 px-6 rounded-full font-bold" onClick={() => window.location.reload()}>Thử Lại</button>
            </div>
          )}

          {!loading && !error && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {destinations.map((dest, i) => (
                <DestinationCard key={i} destination={dest} rank={i + 1} />
              ))}
            </div>
          )}

          <div className="text-center mt-12">
            <button
              className="flex items-center gap-3 px-10 py-4 rounded-full shadow-lg mx-auto font-bold text-xs uppercase tracking-widest transition-all duration-300 hover:-translate-y-1"
              style={{ background: 'var(--grad-primary,linear-gradient(135deg,#c24482,#f4a4c6))', color: 'white' }}
              onClick={() => navigate('/destinations')}
            >
              Xem Tất Cả Điểm Đến
              <span className="material-symbols-outlined text-base">arrow_forward</span>
            </button>
          </div>
        </div>
      </section>


      {/* ══════════════════ LIVE STATS COUNTER ══════════════════ */}
      {stats && (
        <section className="py-16 px-6 md:px-12"
          style={{ background: 'linear-gradient(135deg, color-mix(in srgb, var(--text-accent,#c24482) 5%, transparent), color-mix(in srgb, var(--text-accent,#c24482) 3%, transparent))' }}>
          <div className="max-w-4xl mx-auto grid grid-cols-3 gap-6 text-center">
            <div className="glass-panel py-8 px-4 rounded-2xl flex flex-col items-center gap-2">
              <span className="material-symbols-outlined text-3xl text-primary">location_on</span>
              <p className="font-display-lg text-3xl font-bold text-primary">
                {stats.total_destinations?.toLocaleString()}
              </p>
              <p className="font-label-caps text-[10px] text-secondary uppercase tracking-widest">Điểm Đến</p>
            </div>
            <div className="glass-panel py-8 px-4 rounded-2xl flex flex-col items-center gap-2">
              <span className="material-symbols-outlined text-3xl text-primary">public</span>
              <p className="font-display-lg text-3xl font-bold text-primary">
                {stats.total_countries?.toLocaleString()}
              </p>
              <p className="font-label-caps text-[10px] text-secondary uppercase tracking-widest">Quốc Gia</p>
            </div>
            <div className="glass-panel py-8 px-4 rounded-2xl flex flex-col items-center gap-2">
              <span className="material-symbols-outlined text-3xl text-primary">schema</span>
              <p className="font-display-lg text-3xl font-bold text-primary">
                {stats.total_rules?.toLocaleString()}
              </p>
              <p className="font-label-caps text-[10px] text-secondary uppercase tracking-widest">Luật Apriori</p>
            </div>
          </div>
        </section>
      )}



      {/* ══════════════════ CTA BANNER ══════════════════ */}
      <section className="py-20 px-6 md:px-12">
        <div className="max-w-4xl mx-auto glass-panel rounded-3xl p-12 text-center relative overflow-hidden">
          {/* Decorative blobs */}
          <div className="absolute -top-10 -right-10 w-40 h-40 rounded-full blur-[60px] pointer-events-none opacity-30"
            style={{ background: 'var(--text-accent, #c24482)' }} />
          <div className="absolute -bottom-10 -left-10 w-32 h-32 rounded-full blur-[50px] pointer-events-none opacity-20"
            style={{ background: 'var(--text-accent, #c24482)' }} />
          <div className="relative z-10">
            <div className="text-5xl mb-4">✈️</div>
            <h2 className="font-display-lg text-headline-lg text-primary mb-4">
              Bắt Đầu Hành Trình Của Bạn
            </h2>
            <p className="text-secondary text-sm mb-8 max-w-md mx-auto leading-relaxed">
              Chỉ mất 30 giây trả lời 3 câu hỏi — AI sẽ tìm ra những điểm đến phù hợp nhất với bạn.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                className="px-8 py-4 rounded-full font-bold text-xs uppercase tracking-widest text-white shadow-lg transition-all duration-300 hover:-translate-y-1"
                style={{ background: 'var(--grad-primary, linear-gradient(135deg,#c24482,#f4a4c6))' }}
                onClick={() => navigate('/recommend')}
              >
                ✨ Nhận Gợi Ý Ngay
              </button>
              <button
                className="px-8 py-4 rounded-full font-bold text-xs uppercase tracking-widest border-2 transition-all duration-300 hover:-translate-y-1"
                style={{ borderColor: 'var(--text-accent,#c24482)', color: 'var(--text-accent,#c24482)', background: 'transparent' }}
                onClick={() => navigate('/destinations')}
              >
                🗺️ Khám Phá Bản Đồ
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="bg-surface-container-lowest py-asymmetric-gap-lg flex flex-col items-center gap-asymmetric-gap-sm w-full px-container-padding bg-gradient-to-t from-tertiary-fixed/20 to-transparent">
        <div className="font-display-lg text-headline-md text-primary font-bold">Trợ lý du lịch</div>
        <div className="flex flex-wrap justify-center gap-10">
          <span className="text-on-surface-variant hover:text-primary transition-opacity font-label-caps text-label-caps cursor-pointer" onClick={() => navigate('/')}>Bảo mật</span>
          <span className="text-on-surface-variant hover:text-primary transition-opacity font-label-caps text-label-caps cursor-pointer" onClick={() => navigate('/')}>Điều khoản</span>
          <span className="text-on-surface-variant hover:text-primary transition-opacity font-label-caps text-label-caps cursor-pointer" onClick={() => navigate('/')}>Hỗ trợ</span>
          <span className="text-primary underline font-label-caps text-label-caps cursor-pointer" onClick={() => navigate('/destinations')}>Điểm đến</span>
        </div>
        <p className="text-secondary font-body-md text-body-md mt-6 opacity-60">GVHD: ThS. Phạm Thị Trúc Mai | Sinh viên thực hiện: Thạch Thị Xuân Linh_DA22TTA_110122013</p>
      </footer>
    </div>
  );
}



export default HomePage;
