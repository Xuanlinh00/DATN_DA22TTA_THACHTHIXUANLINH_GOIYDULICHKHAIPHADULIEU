import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { recommendationsApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import DestinationCard from '../components/DestinationCard';
import Footer from '../components/Footer';
import { translateCountry, translateCategory, stripDisplayName } from '../utils/translator';
import { resolveCategoryKey } from '../services/imageService';
import './HomePage.css';


/* ── Season helpers ──────────────────────────────────────────── */
const SEASON_LABELS = { Spring: 'Xuân', Summer: 'Hạ', Autumn: 'Thu', Winter: 'Đông' };
const SEASON_EMOJIS = { Spring: '🌸', Summer: '☀️', Autumn: '🍂', Winter: '❄️' };

const LANGUAGE_KEY = 'Nau_home_language';

const LANGUAGES = [
  { code: 'vi', label: 'VI' },
  { code: 'en', label: 'EN' },
  { code: 'zh', label: '中文' },
];

const HOME_COPY = {
  vi: {
    language: 'Ngôn ngữ',
    eyebrow: 'Trợ lý gợi ý du lịch thông minh',
    titleA: 'Gợi ý điểm đến',
    titleB: 'du lịch quốc tế.',
    subtitle: 'Hệ thống sử dụng các thuật toán khai phá dữ liệu để giúp bạn nhanh chóng tìm kiếm và lựa chọn địa điểm du lịch tối ưu nhất.',
    primaryCta: 'Gợi ý cá nhân hóa',
    aiLabel: 'Gợi ý AI',
    analyzing: 'Đang phân tích dữ liệu...',
    topSeason: 'Hàng đầu mùa',
    destinationFallback: 'Điểm đến',
    personalizedBadge: 'Gợi ý dành riêng cho bạn',
    seasonalBadge: 'Gợi ý theo mùa',
    hello: 'Xin chào',
    seasonPrefix: 'Mùa',
    personalizedDesc: 'Dựa trên sở thích và lịch sử của bạn, chúng tôi đã tuyển chọn những điểm đến phù hợp nhất.',
    seasonalDesc: 'Những điểm đến lý tưởng nhất cho thời điểm hiện tại.',
    loading: 'Đang phân tích các cụm dữ liệu...',
    error: 'Không thể tải gợi ý. Vui lòng thử lại.',
    retry: 'Thử lại',
    viewAll: 'Xem tất cả điểm đến',
    destinations: 'Điểm đến',
    countries: 'Quốc gia',
    rules: 'Luật Apriori',
    ctaTitle: 'Bắt đầu hành trình của bạn',
    ctaDesc: 'Chỉ mất 30 giây trả lời 3 câu hỏi, AI sẽ tìm ra những điểm đến phù hợp nhất với bạn.',
    ctaPrimary: 'Nhận gợi ý ngay',
    ctaSecondary: 'Khám phá bản đồ',
    footerPrivacy: 'Bảo mật',
    footerTerms: 'Điều khoản',
    footerSupport: 'Hỗ trợ',
    footerDestinations: 'Điểm đến',
    seasonLabels: { Spring: 'Xuân', Summer: 'Hè', Autumn: 'Thu', Winter: 'Đông' },
  },
  en: {
    language: 'Language',
    eyebrow: 'Smart travel recommendation assistant',
    titleA: 'Discover travel',
    titleB: 'recommendations worldwide.',
    subtitle: 'The system uses data mining algorithms to help you quickly find and choose the most suitable travel destinations.',
    primaryCta: 'Personalized recommendation',
    aiLabel: 'AI Insight',
    analyzing: 'Analyzing data...',
    topSeason: 'Top pick for',
    destinationFallback: 'Destination',
    personalizedBadge: 'Personalized for you',
    seasonalBadge: 'Seasonal recommendations',
    hello: 'Hello',
    seasonPrefix: '',
    personalizedDesc: 'Based on your preferences and history, we selected the destinations that best match you.',
    seasonalDesc: 'Ideal destinations for the current season and travel timing.',
    loading: 'Analyzing destination clusters...',
    error: 'Unable to load recommendations. Please try again.',
    retry: 'Retry',
    viewAll: 'View all destinations',
    destinations: 'Destinations',
    countries: 'Countries',
    rules: 'Apriori rules',
    ctaTitle: 'Start your journey',
    ctaDesc: 'Answer 3 quick questions in 30 seconds and AI will find the destinations that fit you best.',
    ctaPrimary: 'Get recommendations',
    ctaSecondary: 'Explore map',
    footerPrivacy: 'Privacy',
    footerTerms: 'Terms',
    footerSupport: 'Support',
    footerDestinations: 'Destinations',
    seasonLabels: { Spring: 'Spring', Summer: 'Summer', Autumn: 'Autumn', Winter: 'Winter' },
  },
  zh: {
    language: '语言',
    eyebrow: '智能旅行推荐助手',
    titleA: '发现全球',
    titleB: '旅行推荐。',
    subtitle: '系统使用数据挖掘算法，帮助你快速找到并选择最适合的旅行目的地。',
    primaryCta: '个性化推荐',
    aiLabel: 'AI 推荐',
    analyzing: '正在分析数据...',
    topSeason: '本季优选',
    destinationFallback: '目的地',
    personalizedBadge: '为你个性化推荐',
    seasonalBadge: '季节推荐',
    hello: '你好',
    seasonPrefix: '',
    personalizedDesc: '系统会根据你的偏好 and 历史记录，筛选最适合你的目的地。',
    seasonalDesc: '根据当前季节，为你推荐更合适的旅行目的地。',
    loading: '正在分析目的地数据...',
    error: '无法加载推荐，请重试。',
    retry: '重试',
    viewAll: '查看全部目的地',
    destinations: '目的地',
    countries: '国家',
    rules: 'Apriori 规则',
    ctaTitle: '开始你的旅程',
    ctaDesc: '只需 30 秒回答 3 个问题，AI 会为你找到最匹配 Destination...',
    ctaPrimary: '立即获取推荐',
    ctaSecondary: '探索地图',
    footerPrivacy: '隐私',
    footerTerms: '条款',
    footerSupport: '支持',
    footerDestinations: '目的地',
    seasonLabels: { Spring: '春季', Summer: '夏季', Autumn: '秋季', Winter: '冬季' },
  },
};

function detectSeason() {
  const m = new Date().getMonth() + 1;
  if (m >= 1 && m <= 3) return 'Spring';
  if (m >= 4 && m <= 6) return 'Summer';
  if (m >= 7 && m <= 9) return 'Autumn';
  return 'Winter'; // 10, 11, 12
}

const HERO_IMAGES = [
  { src: '/beach_hero.png', alt: 'Tropical Beach' },
  { src: '/mountain_hero.png', alt: 'Swiss Alps' },
  { src: '/culture_hero.png', alt: 'Kyoto Temple' },
];

function HomePage() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentSeason] = useState(detectSeason);
  const [language, setLanguage] = useState(() => localStorage.getItem(LANGUAGE_KEY) || 'vi');
  // Top destination for floating card
  const [topDest, setTopDest] = useState(null);
  // Whether showing personalized or seasonal recs
  const [isPersonalized, setIsPersonalized] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const t = HOME_COPY[language] || HOME_COPY.vi;
  const seasonLabel = t.seasonLabels[currentSeason] || SEASON_LABELS[currentSeason] || currentSeason;

  useEffect(() => {
    localStorage.setItem(LANGUAGE_KEY, language);
  }, [language]);

  // Slideshow auto-play effect
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentImageIndex((prev) => (prev + 1) % HERO_IMAGES.length);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  /* Load recommendations */
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
              limit: 8,
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
          const seaRes = await recommendationsApi.getSeasonal(currentSeason, 8);
          if (seaRes.data.success) {
            const recs = seaRes.data.recommendations;
            setDestinations(recs);
            if (recs.length > 0) setTopDest(recs[0]);
          }
        }

      } catch (err) {
        setError(t.error);
      } finally {
        setLoading(false);
      }
    })();
  }, [isAuthenticated, user, currentSeason, t.error]);

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
    <div className="home-page overflow-x-hidden font-body-md" lang={language} style={{ backgroundColor: '#fff7fa' }}>
      


      {/* ══════════════════ HERO SECTION (Split Screen with offset) ══════════════════ */}
      <section className="relative min-h-[60vh] pt-20 pb-6 px-container-padding flex flex-col md:flex-row items-center gap-asymmetric-gap-lg overflow-hidden">
        {/* Background Decorative Orbs */}
        <div className="absolute -bottom-20 -left-20 w-96 h-96 bg-primary/5 rounded-full blur-[100px] pointer-events-none"></div>
        <div className="absolute top-20 right-0 w-64 h-64 bg-secondary/10 rounded-full blur-[80px] pointer-events-none"></div>

        {/* Text Content (Left Half) */}
        <div className="w-full md:w-1/2 z-10 space-y-6 text-left glass-hero-text p-8 md:p-10 rounded-3xl border border-white/20 backdrop-blur-md bg-white/25">
          <div className="home-language-switcher" aria-label={t.language}>
            <span>{t.language}</span>
            <div>
              {LANGUAGES.map((lang) => (
                <button
                  key={lang.code}
                  type="button"
                  className={language === lang.code ? 'active' : ''}
                  onClick={() => setLanguage(lang.code)}
                >
                  {lang.label}
                </button>
              ))}
            </div>
          </div>
          <div className="hero-eyebrow">
            {t.eyebrow}
          </div>
          <h1 className="font-display-lg text-display-lg leading-[1.1] font-bold text-on-surface">
            <span className="text-gradient">{t.titleA}</span><br />
            <span>{t.titleB}</span>
          </h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant max-w-lg leading-relaxed">
            {t.subtitle}
          </p>
          <div className="flex flex-wrap gap-4 pt-4">
            <button 
              className="btn-premium-secondary"
              onClick={() => navigate('/recommend')}
            >
              {t.primaryCta} ✨
            </button>
          </div>
        </div>

        {/* Visual Content (Right Half - Teardrop Beach & Floating Cards) */}
        <div className="w-full md:w-1/2 relative">
                  <div className="relative w-full aspect-square max-w-[280px] sm:max-w-[380px] xl:max-w-[440px] 2xl:max-w-[500px] ml-auto md:mr-10">
            {/* Main Image - Teardrop/Blob Shape (Slideshow) */}
            <div className="w-full h-full overflow-hidden blob-shape shadow-2xl relative border border-white/40 bg-white/10">
              {HERO_IMAGES.map((img, index) => (
                <img 
                  key={index}
                  alt={img.alt} 
                  className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ${
                    index === currentImageIndex ? 'opacity-100 z-10' : 'opacity-0 z-0'
                  }`} 
                  src={img.src}
                />
              ))}
              {/* Slideshow pagination indicators */}
              <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-2.5 z-20 bg-black/25 backdrop-blur-md px-3.5 py-2 rounded-full border border-white/15">
                {HERO_IMAGES.map((_, index) => (
                  <button
                    key={index}
                    type="button"
                    aria-label={`Slide ${index + 1}`}
                    className={`w-2 h-2 rounded-full transition-all duration-300 ${
                      index === currentImageIndex ? 'bg-white scale-125' : 'bg-white/50 hover:bg-white/80'
                    }`}
                    onClick={() => setCurrentImageIndex(index)}
                  />
                ))}
              </div>
            </div>
            {/* Floating Card 1: AI Insight */}
            <div className="absolute -top-10 -left-10 glass p-6 rounded-xl floating shadow-xl w-48 z-20 border border-white/40">
              <div className="flex items-center gap-3 mb-2">
                <span className="material-symbols-outlined text-primary text-lg">auto_awesome</span>
                <span className="text-xs font-bold font-label-caps text-primary">{t.aiLabel}</span>
              </div>
              <p className="text-[10px] leading-tight text-on-surface-variant">
                {topDest
                  ? `${t.topSeason} ${seasonLabel}: ${translateCategory(resolveCategoryKey(topDest.Type, topDest['Destination Name'])) || t.destinationFallback}`
                  : t.analyzing}
              </p>
            </div>
            {/* Floating Card 2: Top destination tag (real data) */}
            <div className="absolute bottom-10 -right-5 glass p-4 rounded-full floating shadow-xl z-20 flex items-center gap-3 border border-white/40">
              <div className="w-10 h-10 rounded-full bg-secondary-container flex items-center justify-center text-primary">
                <span className="material-symbols-outlined text-sm">flight</span>
              </div>
              <div>
                <div className="text-[10px] font-bold">
                  {topDest ? stripDisplayName(topDest['Destination Name']) : '...'}
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
      <section className="pt-4 pb-20 px-6 md:px-12 max-w-[1400px] mx-auto" style={{ background: 'transparent' }}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            {isPersonalized ? (
              <span className="inline-block px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-widest mb-4"
                style={{ background: 'color-mix(in srgb, var(--text-accent,#c24482) 10%, white)', color: 'var(--text-accent,#c24482)' }}>
                🤖 {t.personalizedBadge}
              </span>
            ) : (
              <span className="inline-block px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-widest mb-4"
                style={{ background: 'color-mix(in srgb, var(--text-accent,#c24482) 10%, white)', color: 'var(--text-accent,#c24482)' }}>
                ⭐ {t.seasonalBadge}
              </span>
            )}
            <h2 className="font-display-lg text-headline-lg text-primary">
              {isPersonalized
                ? `👋 ${t.hello}, ${user?.fullName || user?.username}!`
                : `${SEASON_EMOJIS[currentSeason]} ${t.seasonPrefix ? `${t.seasonPrefix} ` : ''}${seasonLabel}`}
            </h2>
            <p className="text-secondary mt-3 max-w-lg mx-auto text-sm">
              {isPersonalized
                ? t.personalizedDesc
                : t.seasonalDesc}
            </p>
          </div>

          {loading && (
            <div className="loading">
              <div className="spinner" />
              <p className="text-secondary">{t.loading}</p>
            </div>
          )}

          {error && (
            <div className="error">
              <p>{error}</p>
              <button className="bg-primary text-white py-2 px-6 rounded-full font-bold" onClick={() => window.location.reload()}>{t.retry}</button>
            </div>
          )}

          {!loading && !error && (
            <div className="masonry-grid">
              {destinations.map((dest, i) => (
                <div key={i} className="masonry-item">
                  <DestinationCard destination={dest} rank={i + 1} imageVariant={i} />
                </div>
              ))}
            </div>
          )}

          <div className="text-center mt-12">
            <button
              className="flex items-center gap-3 px-10 py-4 rounded-full shadow-lg mx-auto font-bold text-xs uppercase tracking-widest transition-all duration-300 hover:-translate-y-1"
              style={{ background: 'var(--grad-primary,linear-gradient(135deg,#c24482,#f4a4c6))', color: 'white' }}
              onClick={() => navigate('/destinations')}
            >
              {t.viewAll}
              <span className="material-symbols-outlined text-base">arrow_forward</span>
            </button>
          </div>
        </div>
      </section>


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
              {t.ctaTitle}
            </h2>
            <p className="text-secondary text-sm mb-8 max-w-md mx-auto leading-relaxed">
              {t.ctaDesc}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                className="px-8 py-4 rounded-full font-bold text-xs uppercase tracking-widest text-white shadow-lg transition-all duration-300 hover:-translate-y-1"
                style={{ background: 'var(--grad-primary, linear-gradient(135deg,#c24482,#f4a4c6))' }}
                onClick={() => navigate('/recommend')}
              >
                ✨ {t.ctaPrimary}
              </button>
              <button
                className="px-8 py-4 rounded-full font-bold text-xs uppercase tracking-widest border-2 transition-all duration-300 hover:-translate-y-1"
                style={{ borderColor: 'var(--text-accent,#c24482)', color: 'var(--text-accent,#c24482)', background: 'transparent' }}
                onClick={() => navigate('/destinations')}
              >
                🗺️ {t.ctaSecondary}
              </button>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}



export default HomePage;
