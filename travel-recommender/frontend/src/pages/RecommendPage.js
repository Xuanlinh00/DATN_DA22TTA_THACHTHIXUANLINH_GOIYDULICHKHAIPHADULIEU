import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { recommendationsApi } from '../services/api';
import { getDestinationImage } from '../services/imageService';
import './RecommendPage.css';

// ── Data ─────────────────────────────────────────────────────────────────────

// Mùa theo lịch du lịch Việt Nam
const SEASONS = [
  { value: 'Spring', label: 'Xuân',      emoji: '🌸', desc: 'Tháng 1 – 3 · Tết, lễ hội, dịu mát' },
  { value: 'Summer', label: 'Hè',        emoji: '☀️', desc: 'Tháng 4 – 8 · Nắng đẹp, biển, nghỉ hè' },
  { value: 'Autumn', label: 'Thu',       emoji: '🍂', desc: 'Tháng 9 – 10 · Mát mẻ, lúa vàng, thanh bình' },
  { value: 'Winter', label: 'Đông',      emoji: '❄️', desc: 'Tháng 11 – 12 · Se lạnh, Giáng Sinh' },
];

const CATEGORIES = [
  { value: 'Beach',       label: 'Biển & Đảo',    emoji: '🏖️' },
  { value: 'Mountain',   label: 'Núi & Rừng',     emoji: '🏔️' },
  { value: 'Cultural',   label: 'Văn Hoá & Lịch Sử', emoji: '🏛️' },
  { value: 'City',       label: 'Thành Phố',       emoji: '🏙️' },
  { value: 'Adventure',  label: 'Phiêu Lưu',       emoji: '🪂' },
  { value: 'Wellness',   label: 'Nghỉ Dưỡng',      emoji: '🧘' },
  { value: 'Nature',     label: 'Thiên Nhiên',      emoji: '🌿' },
  { value: 'Theme Park', label: 'Vui Chơi',         emoji: '🎡' },
];

const BUDGETS = [
  { value: 'Budget',   label: 'Tiết Kiệm',   range: '< $50/ngày',   emoji: '💚' },
  { value: 'Moderate', label: 'Bình Dân',    range: '$50–$150/ngày', emoji: '💙' },
  { value: 'Expensive',label: 'Cao Cấp',     range: '$150–$300/ngày',emoji: '💜' },
  { value: 'Luxury',   label: 'Sang Trọng',  range: '> $300/ngày',   emoji: '🌟' },
];



const STEPS = [
  { label: 'Mùa', icon: '🗓️' },
  { label: 'Phong cách', icon: '🎒' },
  { label: 'Ngân sách', icon: '💰' },
  { label: 'Kết quả', icon: '✨' },
];

// ── Sub-components ────────────────────────────────────────────────────────────

function ProgressBar({ currentStep }) {
  return (
    <>
      <div className="wizard-progress">
        {STEPS.map((step, idx) => {
          const status = idx < currentStep ? 'completed' : idx === currentStep ? 'active' : 'pending';
          return (
            <React.Fragment key={idx}>
              <div className={`wizard-step-dot ${status}`} title={step.label}>
                {status === 'completed' ? '✓' : idx + 1}
              </div>
              {idx < STEPS.length - 1 && (
                <div className="wizard-step-line">
                  <div
                    className="wizard-step-line-fill"
                    style={{ width: idx < currentStep ? '100%' : '0%' }}
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
      <div className="wizard-step-labels">
        {STEPS.map((step, idx) => (
          <span key={idx} className={`wizard-step-label ${idx === currentStep ? 'active' : ''}`}>
            {step.icon} {step.label}
          </span>
        ))}
      </div>
    </>
  );
}

function OptionCard({ emoji, label, desc, selected, onClick }) {
  return (
    <div
      className={`wizard-option-card ${selected ? 'selected' : ''}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      {selected && <span className="wizard-option-check">✓</span>}
      <span className="wizard-option-emoji">{emoji}</span>
      <div className="wizard-option-label">{label}</div>
      {desc && <div style={{ fontSize: 10, color: '#87717a', marginTop: 2 }}>{desc}</div>}
    </div>
  );
}

// ── Tagline engine đa dạng ─────────────────────────────────────────────────
// Mỗi loại có nhiều câu → chọn theo hash của tên điểm đến để luôn nhất quán
// nhưng khác nhau giữa các card cùng loại.
function pickOne(arr, seed) {
  // Stable pick: tổng mã ASCII của seed % độ dài mảng
  const hash = (seed || '').split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
  return arr[hash % arr.length];
}

const TAGLINE_POOL = {
  beach: [
    (s, b, n, c) => `🌊 Nếu bạn mơ về làn sóng vỗ bờ — ${n} chính là thiên đường biển đẹp nhất ${c}!`,
    (s, b, n, c) => `🐚 Nếu bạn thích tắm nắng và hải sản tươi ngon — đây là chuyến đi không thể bỏ lỡ!`,
    (s, b, n, c) => `🏄 Nếu bạn muốn lướt sóng hay chỉ đơn giản thả hồn bên biển — ${n} đang chờ bạn!`,
    (s, b, n, c) => `🌅 Hoàng hôn trên biển ${c} được mô tả là "đẹp nhất cuộc đời" bởi hàng nghìn du khách.`,
    (s, b, n, c) => `🪸 Nếu bạn yêu màu xanh của đại dương — rạn san hô tại ${n} sẽ khiến bạn say đắm!`,
    (s, b, n, c) => `☀️ ${s === 'Summer' ? 'Mùa hè năm nay' : 'Dịp này'}, không đâu lý tưởng hơn một bãi biển tuyệt đẹp — và ${n} là câu trả lời!`,
  ],
  mountain: [
    (s, b, n, c) => `🏔️ Nếu bạn muốn chinh phục đỉnh cao — ${n} là thử thách xứng đáng nhất ở ${c}!`,
    (s, b, n, c) => `🌄 Nếu bạn yêu bình minh phủ mây và không khí trong lành — đây là nơi tâm hồn được tự do!`,
    (s, b, n, c) => `🧗 Nếu bạn tìm cảm giác chinh phục và tự hào — những đỉnh núi ${n} đang chờ bước chân bạn!`,
    (s, b, n, c) => `🌲 Rừng núi ${c} khoác lên mình màu sắc huyền ảo ${s === 'Autumn' ? 'mùa thu' : 'mùa này'} — cảnh tượng khó quên!`,
    (s, b, n, c) => `⛺ Nếu bạn thích cắm trại dưới bầu trời đầy sao — ${n} là điểm đến hoàn hảo cho bạn!`,
  ],
  cultural: [
    (s, b, n, c) => `🏛️ Nếu bạn muốn chạm vào lịch sử ngàn năm — ${n} sẽ kể cho bạn nghe những câu chuyện phi thường!`,
    (s, b, n, c) => `🎭 Văn hóa ${c} đặc sắc đến mức mỗi góc phố ${n} đều là một bảo tàng sống!`,
    (s, b, n, c) => `🗿 Nếu bạn thích khám phá di sản cổ đại — đây là nơi thời gian như ngừng trôi!`,
    (s, b, n, c) => `🎨 Nếu bạn mê ẩm thực địa phương và nghệ thuật truyền thống — ${n} sẽ không bao giờ làm bạn thất vọng!`,
    (s, b, n, c) => `📜 Mỗi góc nhỏ của ${n} đều thấm đẫm lịch sử — một chuyến đi học hỏi thực sự giá trị!`,
    (s, b, n, c) => `🏮 ${c} nổi tiếng với các lễ hội truyền thống rực rỡ — ${s === 'Spring' ? 'mùa xuân là thời điểm lý tưởng nhất!' : 'và ${n} là cổng vào thế giới đó!'}`,
  ],
  nature: [
    (s, b, n, c) => `🌿 Nếu bạn cần thoát khỏi thành phố và lấy lại năng lượng — thiên nhiên ${n} sẽ chữa lành bạn!`,
    (s, b, n, c) => `🦋 Nếu bạn yêu tiếng chim hót và hương rừng sau mưa — đây là nơi tâm hồn bạn thuộc về!`,
    (s, b, n, c) => `🌈 Vẻ đẹp hoang sơ của ${n} nhắc nhở ta rằng thiên nhiên luôn là nghệ sĩ vĩ đại nhất!`,
    (s, b, n, c) => `🌊 Thác nước, rừng già, suối trong — ${n} có tất cả những gì bạn cần cho một chuyến đi thực sự!`,
    (s, b, n, c) => `🍃 Nếu bạn tìm góc yên tĩnh để đọc sách và ngắm cảnh — ${n} chính là nơi đó!`,
  ],
  adventure: [
    (s, b, n, c) => `🪂 Nếu bạn sống để tìm kiếm cảm giác mạnh — ${n} có đủ thứ để tim bạn đập rộn ràng!`,
    (s, b, n, c) => `🚵 Nếu bạn chưa thử thách bản thân đến giới hạn — ${c} đang mời bạn đến và chinh phục!`,
    (s, b, n, c) => `⚡ Kayak, leo núi, nhảy dù, lặn biển — ${n} gói gọn tất cả trong một hành trình phiêu lưu!`,
    (s, b, n, c) => `🏕️ Nếu bạn thích những câu chuyện kể lại ở bàn nhậu về "lần mà tôi gần như..." — đây chính là chuyến đi đó!`,
    (s, b, n, c) => `🎯 Cuộc sống quá ngắn để chỉ ở nhà — ${n} đang thử thách bạn bước ra khỏi vùng an toàn!`,
  ],
  city: [
    (s, b, n, c) => `🏙️ Nếu bạn thích nhịp sống không bao giờ ngủ — ${n} là thành phố sẽ khiến bạn mê mẩn cả ngày lẫn đêm!`,
    (s, b, n, c) => `🍜 Ẩm thực đường phố ${c}, shopping mall hiện đại và nightlife sôi động — ${n} có tất cả!`,
    (s, b, n, c) => `🚇 Nếu bạn muốn cảm nhận nhịp đập của một đô thị châu Á hiện đại — ${n} là điểm đến không thể bỏ qua!`,
    (s, b, n, c) => `🌃 Skyline của ${n} về đêm là một trong những cảnh tượng đẹp nhất bạn sẽ từng thấy!`,
    (s, b, n, c) => `☕ Quán cà phê độc đáo, gallery nghệ thuật, khu phố cổ — ${n} là thành phố cho những tâm hồn khám phá!`,
  ],
  wellness: [
    (s, b, n, c) => `🧘 Nếu bạn cần buông bỏ mọi stress — spa và resort ${n} sẽ đưa bạn về trạng thái bình an tuyệt đối!`,
    (s, b, n, c) => `🛁 Nếu bạn xứng đáng được chiều chuộng sau một năm làm việc vất vả — ${n} chính là phần thưởng dành cho bạn!`,
    (s, b, n, c) => `🌸 Yoga bình minh, massage đá nóng, bữa ăn healthy — ${n} có đủ công thức để tái sinh cơ thể và tâm trí!`,
    (s, b, n, c) => `💆 Nếu bạn muốn ngủ thật ngon, ăn thật ngon và không nghĩ đến công việc — đây là nơi dành cho bạn!`,
    (s, b, n, c) => `🏝️ Nghỉ dưỡng ${b === 'Luxury' ? 'sang trọng' : 'dễ chịu'} tại ${n} — khoảng thời gian chỉ dành riêng cho chính bạn!`,
  ],
  theme: [
    (s, b, n, c) => `🎡 Nếu bạn muốn cười thật to, la thật lớn và vui hết mình — ${n} là điểm đến cho bạn!`,
    (s, b, n, c) => `🎢 Từ trò chơi cảm giác mạnh đến show diễn hoành tráng — ${n} đảm bảo bạn không có một giây nhàm chán!`,
    (s, b, n, c) => `✨ Cả gia đình, cả hội bạn hay chỉ riêng bạn — ${n} đều có thứ gì đó để khiến bạn rạng ngời!`,
    (s, b, n, c) => `🌟 Nếu bạn muốn tạo ra những kỷ niệm khó quên với người thân — ${n} chính là nơi làm điều đó!`,
  ],
  default: [
    (s, b, n, c) => `✨ ${n} nằm trong top những điểm đến được yêu thích nhất ${c} — và hôm nay đang chờ bạn khám phá!`,
    (s, b, n, c) => `🌍 Nếu bạn chưa từng đặt chân đến ${c} — ${n} là điểm khởi đầu hoàn hảo nhất!`,
    (s, b, n, c) => `🗺️ Có những nơi chỉ cần nhìn ảnh đã muốn đặt vé ngay — ${n} là một trong số đó!`,
    (s, b, n, c) => `💫 Mỗi chuyến đi đều thay đổi bạn một chút — và ${n} hứa hẹn sẽ thay đổi bạn rất nhiều!`,
    (s, b, n, c) => `🎒 Đừng đợi "khi nào rảnh" nữa — ${n} đang ở đó, tuyệt đẹp và sẵn sàng đón bạn!`,
    (s, b, n, c) => `📸 Một nghìn tấm ảnh cũng không đủ để lưu lại vẻ đẹp của ${n} — bạn cần tự mình đến và trải nghiệm!`,
    (s, b, n, c) => `🌺 Được chọn lọc đặc biệt cho ${s === 'Summer' ? 'mùa hè' : s === 'Winter' ? 'mùa đông' : s === 'Autumn' ? 'mùa thu' : 'mùa xuân'} — ${n} là lựa chọn xứng đáng với kỳ nghỉ của bạn!`,
    (s, b, n, c) => `🏆 ${b === 'Budget' ? 'Chi phí hợp lý' : b === 'Luxury' ? 'Trải nghiệm sang trọng' : 'Giá trị tuyệt vời'} tại ${n} — không phải ai cũng biết đến địa điểm tuyệt vời này!`,
  ],
};

function getDestTagline(dest, prefs) {
  const type   = (dest.Type || '').toLowerCase();
  const name   = dest['Destination Name'] || 'điểm đến này';
  const country= dest.Country || '';
  const season = prefs?.season || '';
  const budget = prefs?.budget || '';
  const seed   = name + country; // stable but unique per destination

  // Chọn pool phù hợp theo type
  let pool;
  if (type.includes('beach') || type.includes('island') || type.includes('coastal'))
    pool = TAGLINE_POOL.beach;
  else if (type.includes('mountain') || type.includes('trek') || type.includes('highland'))
    pool = TAGLINE_POOL.mountain;
  else if (type.includes('cultur') || type.includes('histor') || type.includes('heritage') || type.includes('temple'))
    pool = TAGLINE_POOL.cultural;
  else if (type.includes('nature') || type.includes('eco') || type.includes('forest') || type.includes('wildlife'))
    pool = TAGLINE_POOL.nature;
  else if (type.includes('adventure') || type.includes('sport') || type.includes('extreme'))
    pool = TAGLINE_POOL.adventure;
  else if (type.includes('city') || type.includes('urban') || type.includes('metropolis') || type.includes('shopping'))
    pool = TAGLINE_POOL.city;
  else if (type.includes('wellness') || type.includes('spa') || type.includes('resort') || type.includes('retreat'))
    pool = TAGLINE_POOL.wellness;
  else if (type.includes('theme') || type.includes('park') || type.includes('entertainment') || type.includes('amusement'))
    pool = TAGLINE_POOL.theme;
  else {
    pool = TAGLINE_POOL.default;
  }

  const fn = pickOne(pool, seed);
  return fn(season, budget, name, country);
}



function DestResultCard({ dest, prefs, rank, onClick }) {
  const imgUrl = dest.image || getDestinationImage(dest['Destination Name'], dest.Type);
  const tagline = getDestTagline(dest, prefs);
  const rating = dest['Avg Rating'] || dest['avg_rating'];
  const cost = dest['Avg Cost (USD/day)'];
  return (
    <div className="wizard-dest-card" onClick={onClick}>
      <div className="wizard-dest-img-wrap">
        <img
          src={imgUrl}
          alt={dest['Destination Name']}
          onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600'; }}
        />
        {/* Rank badge */}
        {rank <= 3 && (
          <span className="wizard-dest-rank-badge">
            {rank === 1 ? '🥇' : rank === 2 ? '🥈' : '🥉'}
          </span>
        )}
        {/* Rating badge */}
        {rating && (
          <span className="wizard-dest-score-badge">
            ★ {parseFloat(rating).toFixed(1)}
          </span>
        )}
        {/* Image gradient overlay */}
        <div className="wizard-dest-img-overlay" />
      </div>
      <div className="wizard-dest-body">
        {/* Type chip */}
        <div className="wizard-dest-type-chip">
          {dest.Type || 'Điểm đến'}
        </div>
        <div className="wizard-dest-name">{dest['Destination Name']}</div>
        <div className="wizard-dest-country">
          {dest.country_flag || '🌍'} {dest.Country}
          {cost && <span className="wizard-dest-cost"> · ${cost}/ngày</span>}
        </div>
        {/* Emotional tagline */}
        <div className="wizard-dest-tagline">{tagline}</div>
        {/* Info pills */}
        <div className="wizard-dest-info-pills">
          {dest['Best Season'] && (
            <span className="wizard-info-pill">📅 {dest['Best Season']}</span>
          )}
          {dest['UNESCO Site'] === 'Yes' && (
            <span className="wizard-info-pill wizard-info-pill--special">🏅 UNESCO</span>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Main Page Component ───────────────────────────────────────────────────────

function RecommendPage() {
  const navigate = useNavigate();

  // Wizard state
  const [step, setStep]         = useState(0); // 0,1,2 = input steps; 3 = results
  const [season, setSeason]     = useState('');
  const [category, setCategory] = useState('');
  const [budget, setBudget]     = useState('');

  // Results state
  const [results, setResults]           = useState([]);
  const [matchedRules, setMatchedRules] = useState([]);
  const [loading, setLoading]           = useState(false);
  const [error, setError]               = useState(null);

  // ── Navigation helpers ────────────────────────────────────────
  const canProceed = () => {
    if (step === 0) return !!season;
    if (step === 1) return !!category;
    if (step === 2) return !!budget;
    return false;
  };

  const handleNext = async () => {
    if (step < 2) {
      setStep(s => s + 1);
      return;
    }
    // Step 2 → fetch results
    setStep(3);
    setLoading(true);
    setError(null);
    try {
      const response = await recommendationsApi.getFiltered({
        season, category, budget, limit: 12
      });
      if (response.data.success) {
        setResults(response.data.recommendations || []);
        setMatchedRules(response.data.matched_rules || []);
      }
    } catch (err) {
      setError('Không thể tải gợi ý. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setStep(0);
    setSeason('');
    setCategory('');
    setBudget('');
    setResults([]);
    setMatchedRules([]);
    setError(null);
  };

  // ── Render ────────────────────────────────────────────────────
  return (
    <div className="recommend-page">
      <div className="wizard-container">
        {/* Title */}
        <h1 className="wizard-title">Gợi Ý<br /><em>Hành Trình</em></h1>
        <p className="wizard-subtitle">
          Trả lời 3 câu hỏi ngắn để nhận gợi ý điểm đến được cá nhân hóa bằng AI khai phá dữ liệu.
        </p>

        {/* Progress */}
        <ProgressBar currentStep={step} />

        {/* ── Step 0: Season ───────────────────────────────────── */}
        {step === 0 && (
          <div className="wizard-step-card">
            <div className="wizard-step-heading">Bước 1 / 3</div>
            <h2 className="wizard-step-question">Bạn muốn đi du lịch vào mùa nào?</h2>
            <div className="wizard-option-grid">
              {SEASONS.map(s => (
                <OptionCard
                  key={s.value}
                  emoji={s.emoji}
                  label={s.label}
                  desc={s.desc}
                  selected={season === s.value}
                  onClick={() => setSeason(s.value)}
                />
              ))}
            </div>
            <div className="wizard-nav">
              <span />
              <button id="btn-next-step0" className="wizard-btn-next" disabled={!canProceed()} onClick={handleNext}>
                Tiếp theo <span className="material-symbols-outlined" style={{ fontSize: 18 }}>arrow_forward</span>
              </button>
            </div>
          </div>
        )}

        {/* ── Step 1: Category ─────────────────────────────────── */}
        {step === 1 && (
          <div className="wizard-step-card">
            <div className="wizard-step-heading">Bước 2 / 3</div>
            <h2 className="wizard-step-question">Bạn thích phong cách du lịch nào?</h2>
            <div className="wizard-option-grid">
              {CATEGORIES.map(c => (
                <OptionCard
                  key={c.value}
                  emoji={c.emoji}
                  label={c.label}
                  selected={category === c.value}
                  onClick={() => setCategory(c.value)}
                />
              ))}
            </div>
            <div className="wizard-nav">
              <button id="btn-back-step1" className="wizard-btn-back" onClick={() => setStep(0)}>
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>arrow_back</span> Quay lại
              </button>
              <button id="btn-next-step1" className="wizard-btn-next" disabled={!canProceed()} onClick={handleNext}>
                Tiếp theo <span className="material-symbols-outlined" style={{ fontSize: 18 }}>arrow_forward</span>
              </button>
            </div>
          </div>
        )}

        {/* ── Step 2: Budget ───────────────────────────────────── */}
        {step === 2 && (
          <div className="wizard-step-card">
            <div className="wizard-step-heading">Bước 3 / 3</div>
            <h2 className="wizard-step-question">Ngân sách mỗi ngày của bạn là bao nhiêu?</h2>
            <div className="wizard-budget-row">
              {BUDGETS.map(b => (
                <div
                  key={b.value}
                  id={`budget-${b.value}`}
                  className={`wizard-budget-option ${budget === b.value ? 'selected' : ''}`}
                  onClick={() => setBudget(b.value)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => e.key === 'Enter' && setBudget(b.value)}
                >
                  <div className="wizard-budget-badge">{b.emoji} {b.label}</div>
                  <div className="wizard-budget-label">{b.label}</div>
                  <div className="wizard-budget-range">{b.range}</div>
                </div>
              ))}
            </div>
            <div className="wizard-nav">
              <button id="btn-back-step2" className="wizard-btn-back" onClick={() => setStep(1)}>
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>arrow_back</span> Quay lại
              </button>
              <button id="btn-find-results" className="wizard-btn-next" disabled={!canProceed()} onClick={handleNext}>
                ✨ Tìm điểm đến phù hợp
              </button>
            </div>
          </div>
        )}

        {/* ── Step 3: Results ──────────────────────────────────── */}
        {step === 3 && (
          <div className="wizard-results">
            {loading && (
              <div className="wizard-loading">
                <div className="wizard-spinner" />
                <p style={{ color: '#87717a', fontSize: 14 }}>Đang phân tích với thuật toán Hybrid Recommender...</p>
              </div>
            )}

            {error && !loading && (
              <div className="wizard-no-results">
                <div style={{ fontSize: '2.5rem', marginBottom: 12 }}>😔</div>
                <p style={{ marginBottom: 16 }}>{error}</p>
                <button className="wizard-reset-btn" onClick={handleReset}>
                  🔄 Thử lại
                </button>
              </div>
            )}

            {!loading && !error && (
              <>
                {/* Results header */}
                <div className="wizard-results-header">
                  <div className="wizard-results-emoji">✈️</div>
                  <h2 className="wizard-results-title">
                    {results.length > 0
                      ? `${results.length} Điểm Đến Dành Riêng Cho Bạn`
                      : 'Chưa tìm thấy kết quả'}
                  </h2>
                  <p className="wizard-results-sub">
                    Dựa trên sở thích của bạn, chúng tôi đã tuyển chọn những điểm đến tuyệt vời nhất
                  </p>
                  {/* Selection summary pills */}
                  <div className="wizard-selection-pills">
                    {season && (
                      <span className="wizard-sel-pill">
                        {SEASONS.find(s => s.value === season)?.emoji} {SEASONS.find(s => s.value === season)?.label}
                      </span>
                    )}
                    {category && (
                      <span className="wizard-sel-pill">
                        {CATEGORIES.find(c => c.value === category)?.emoji} {CATEGORIES.find(c => c.value === category)?.label}
                      </span>
                    )}
                    {budget && (
                      <span className="wizard-sel-pill">
                        {BUDGETS.find(b => b.value === budget)?.emoji} {BUDGETS.find(b => b.value === budget)?.label}
                      </span>
                    )}
                  </div>
                </div>

                {results.length > 0 ? (
                  <div className="wizard-results-grid">
                    {results.map((dest, idx) => (
                      <DestResultCard
                        key={idx}
                        dest={dest}
                        prefs={{ season, category, budget }}
                        rank={idx + 1}
                        onClick={() => navigate(`/destinations/${encodeURIComponent(dest['Destination Name'])}`)}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="wizard-no-results">
                    <div style={{ fontSize: '3rem', marginBottom: 16 }}>🔍</div>
                    <p style={{ fontSize: 16, marginBottom: 8 }}>Không tìm thấy điểm đến phù hợp</p>
                    <p style={{ fontSize: 13, opacity: 0.7 }}>Thử thay đổi mùa, phong cách hoặc ngân sách để xem nhiều gợi ý hơn.</p>
                  </div>
                )}

                <div style={{ textAlign: 'center', marginTop: 8 }}>
                  <button id="btn-reset-wizard" className="wizard-reset-btn" onClick={handleReset}>
                    🔄 Tìm kiếm lại với tiêu chí khác
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default RecommendPage;
