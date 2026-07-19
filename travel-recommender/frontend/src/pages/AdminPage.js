import React, { useState, useEffect } from 'react';
import { adminApi, destinationsApi } from '../services/api';
import {
  ScatterChart, Scatter, BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './AdminPage.css';

const COLORS = ['#c24482', '#7c3aed', '#0284c7', '#16a34a', '#ea580c', '#f59e0b', '#3b82f6', '#ec4899'];
const CONTINENT_COLORS = {
  'Asia': '#c24482',
  'Europe': '#7c3aed',
  'Americas': '#0284c7',
  'Africa': '#ea580c',
  'Oceania': '#16a34a',
  'Other': '#6b7280'
};
const COST_COLORS = {
  'Budget': '#16a34a',
  'Moderate': '#0284c7',
  'Expensive': '#ea580c',
  'Luxury': '#c24482'
};

const AdminPage = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  
  // Dashboard Core Data
  const [stats, setStats] = useState(null);
  const [rules, setRules] = useState([]);
  const [ratings, setRatings] = useState([]);
  const [clusterProfiles, setClusterProfiles] = useState([]);
  const [destinations, setDestinations] = useState([]);
  const [users, setUsers] = useState([]);
  const [elbowData, setElbowData] = useState([]);
  const [loading, setLoading] = useState(false);

  // Layout Tab Navigation
  const [activeTab, setActiveTab] = useState('overview');

  // Algorithm Control States
  const [minSupport, setMinSupport] = useState(0.01);
  const [minConfidence, setMinConfidence] = useState(0.1);
  const [minLift, setMinLift] = useState(1.0);
  const [nClusters, setNClusters] = useState(5);
  const [actionLoading, setActionLoading] = useState({
    apriori: false,
    clustering: false,
    cf: false,
    imageUpload: false,
    imageFetch: false
  });

  // Apriori comparison
  const [prevRulesCount, setPrevRulesCount] = useState(null);
  const [runComparison, setRunComparison] = useState(null);

  // Overview Card Modals
  const [activeModal, setActiveModal] = useState(null);
  const [modalSearch, setModalSearch] = useState('');

  // Destination CRUD states
  const [isDestModalOpen, setIsDestModalOpen] = useState(false);
  const [destFormMode, setDestFormMode] = useState('add'); // 'add' | 'edit'
  const [selectedDestName, setSelectedDestName] = useState('');
  const [destForm, setDestForm] = useState({
    destination_name: '',
    country: '',
    continent: 'Asia',
    type: 'Cultural',
    best_season: 'Summer',
    avg_cost: 100,
    cost_category: 'Moderate',
    description: '',
    image: '',
    latitude: '',
    longitude: ''
  });

  // Apriori Rules search & pagination
  const [rulesSearch, setRulesSearch] = useState('');
  const [rulesSortKey, setRulesSortKey] = useState('lift');
  const [rulesSortOrder, setRulesSortOrder] = useState('desc');
  const [rulesPage, setRulesPage] = useState(1);
  const rulesPerPage = 15;

  // Destinations search & pagination
  const [destsSearch, setDestsSearch] = useState('');
  const [destsPage, setDestsPage] = useState(1);
  const destsPerPage = 10;

  // Check session storage on mount
  useEffect(() => {
    const adminSession = sessionStorage.getItem('admin_authenticated');
    if (adminSession === 'true') {
      setIsAuthenticated(true);
      fetchAllData();
    }
  }, []);

  useEffect(() => {
    setRulesPage(1);
  }, [rulesSearch, rulesSortKey, rulesSortOrder]);

  useEffect(() => {
    setDestsPage(1);
  }, [destsSearch]);

  const handleLogin = (e) => {
    e.preventDefault();
    if (password === 'admin' || password === 'admin123') {
      sessionStorage.setItem('admin_authenticated', 'true');
      setIsAuthenticated(true);
      fetchAllData();
      toast.success('Xác thực thành công!');
    } else {
      toast.error('Mật khẩu không chính xác. Thử lại với "admin" hoặc "admin123"!');
    }
  };

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [statsRes, rulesRes, ratingsRes, destsRes, usersRes, elbowRes] = await Promise.all([
        adminApi.getStats(),
        adminApi.getRules(),
        adminApi.getRatings(1000),
        destinationsApi.getAll({ limit: 1000 }),
        adminApi.getUsers(),
        adminApi.getClusteringElbow().catch(() => ({ data: { success: false, sse: {} } }))
      ]);

      if (statsRes.data.success) {
        setStats(statsRes.data.stats);
        setClusterProfiles(statsRes.data.cluster_profiles || []);
      }
      if (rulesRes.data.success) {
        const rulesList = rulesRes.data.rules || [];
        setRules(rulesList);
        if (prevRulesCount === null) {
          setPrevRulesCount(rulesList.length);
        }
      }
      if (ratingsRes.data.success) {
        setRatings(ratingsRes.data.ratings || []);
      }
      if (destsRes.data.success) {
        setDestinations(destsRes.data.destinations || []);
      }
      if (usersRes.data.success) {
        setUsers(usersRes.data.users || []);
      }
      if (elbowRes.data.success && elbowRes.data.sse) {
        const formatted = Object.entries(elbowRes.data.sse).map(([k, sse]) => ({
          k: parseInt(k),
          sse: sse
        })).sort((a, b) => a.k - b.k);
        setElbowData(formatted);
      }
    } catch (err) {
      console.error(err);
      toast.error('Lỗi khi tải dữ liệu thống kê hệ thống.');
    } finally {
      setLoading(false);
    }
  };

  // Algorithm Executions
  const handleRunApriori = async () => {
    setActionLoading(prev => ({ ...prev, apriori: true }));
    const startTime = Date.now();
    try {
      const currentCount = rules.length;
      const res = await adminApi.runApriori(minSupport, minConfidence, minLift);
      const duration = ((Date.now() - startTime) / 1000).toFixed(2);
      if (res.data.success) {
        const newCount = res.data.count;
        const diff = newCount - currentCount;
        const diffText = diff >= 0 ? `(+${diff} luật so với lần chạy trước)` : `(${diff} luật so với lần chạy trước)`;
        setRunComparison({
          count: newCount,
          duration: duration,
          diffText: diffText,
          timestamp: new Date().toLocaleTimeString()
        });
        toast.success(`Tạo mới ${newCount} luật trong ${duration}s! ${diffText}`);
        setPrevRulesCount(newCount);
        fetchAllData();
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Không thể chạy Apriori.');
    } finally {
      setActionLoading(prev => ({ ...prev, apriori: false }));
    }
  };

  const handleRunClustering = async () => {
    setActionLoading(prev => ({ ...prev, clustering: true }));
    try {
      const res = await adminApi.runClustering(nClusters);
      if (res.data.success) {
        toast.success(`Phân cụm K-Means thành công với k=${nClusters} cụm!`);
        fetchAllData();
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Không thể chạy K-Means.');
    } finally {
      setActionLoading(prev => ({ ...prev, clustering: false }));
    }
  };

  const handleRefreshCF = async () => {
    setActionLoading(prev => ({ ...prev, cf: true }));
    try {
      const res = await adminApi.refreshCF();
      if (res.data.success) {
        toast.success(res.data.message || 'Cập nhật ma trận CF thành công.');
        fetchAllData();
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Không thể cập nhật Collaborative Filtering.');
    } finally {
      setActionLoading(prev => ({ ...prev, cf: false }));
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem('admin_authenticated');
    setIsAuthenticated(false);
    setPassword('');
  };


  const anonymizeUserId = (userId) => {
    const text = String(userId || 'anonymous');
    let hash = 0;
    for (let i = 0; i < text.length; i += 1) {
      hash = ((hash << 5) - hash + text.charCodeAt(i)) | 0;
    }
    return `USER-${Math.abs(hash).toString(16).toUpperCase().padStart(6, '0').slice(0, 6)}`;
  };

  const toNumber = (value, fallback = 0) => {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  };

  const getRuleItems = (rule) => {
    const items = [
      ...(Array.isArray(rule.antecedents) ? rule.antecedents : []),
      ...(Array.isArray(rule.consequents) ? rule.consequents : [])
    ].filter(Boolean);
    if (items.length > 0) return items.map(item => String(item).trim()).filter(Boolean);

    const braceMatches = String(rule.rule || '').match(/\{([^}]+)\}/g);
    if (braceMatches) {
      return braceMatches
        .flatMap(match => match.slice(1, -1).split(','))
        .map(item => item.trim())
        .filter(Boolean);
    }

    return String(rule.rule || '').split(/=>|,|\|/).map(item => item.trim()).filter(Boolean);
  };

  const formatRuleLabel = (rule) => {
    if (rule.rule) return rule.rule;
    const left = Array.isArray(rule.antecedents) ? rule.antecedents.join(', ') : '';
    const right = Array.isArray(rule.consequents) ? rule.consequents.join(', ') : '';
    if (left || right) return `${left || '?'} => ${right || '?'}`;
    return 'Unknown rule';
  };
  // User Accounts
  const handleToggleLock = async (username) => {
    try {
      const res = await adminApi.toggleUserLock(username);
      if (res.data.success) {
        toast.success(res.data.message);
        fetchAllData();
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Lỗi khi khóa/mở khóa tài khoản.');
    }
  };

  // Review Ratings
  const handleDeleteRating = async (userId, destName) => {
    if (!window.confirm(`Xóa đánh giá của ${userId} cho điểm đến ${destName}?`)) return;
    try {
      const res = await adminApi.deleteRating(userId, destName);
      if (res.data.success) {
        toast.success(res.data.message);
        fetchAllData();
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Lỗi khi xóa đánh giá.');
    }
  };

  const handleSaveDestination = (e) => {
    e.preventDefault();
  };

  // Image Upload / Auto-Fetch
  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setActionLoading(prev => ({ ...prev, imageUpload: true }));
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await adminApi.uploadDestinationImage(destForm.destination_name, formData);
      if (res.data.success) {
        setDestForm(prev => ({ ...prev, image: res.data.image_url }));
        toast.success('Upload hình ảnh thành công!');
      }
    } catch (err) {
      toast.error('Lỗi khi upload tệp ảnh.');
    } finally {
      setActionLoading(prev => ({ ...prev, imageUpload: false }));
    }
  };

  const handleImageAutoFetch = async () => {
    if (!destForm.destination_name) {
      toast.warning('Vui lòng điền Tên điểm đến trước.');
      return;
    }
    setActionLoading(prev => ({ ...prev, imageFetch: true }));
    try {
      const apiBase = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const actualFetchRes = await fetch(`${apiBase.replace('/api', '')}/api/destinations/${encodeURIComponent(destForm.destination_name)}/fetch-image?country=${encodeURIComponent(destForm.country)}&dest_type=${encodeURIComponent(destForm.type)}`);
      const imgData = await actualFetchRes.json();
      if (imgData.success) {
        setDestForm(prev => ({ ...prev, image: imgData.image_url }));
        toast.success('Đã tự động tải ảnh chất lượng từ Unsplash/Wikimedia!');
      } else {
        toast.error('Không tìm thấy ảnh phù hợp.');
      }
    } catch (err) {
      toast.error('Lỗi khi tự động tải ảnh từ API.');
    } finally {
      setActionLoading(prev => ({ ...prev, imageFetch: false }));
    }
  };

  const handleImageDelete = async () => {
    if (!destForm.destination_name) return;
    if (destFormMode === 'add') {
      setDestForm(prev => ({ ...prev, image: '' }));
      return;
    }
    try {
      const res = await adminApi.deleteDestinationImage(destForm.destination_name);
      if (res.data.success) {
        setDestForm(prev => ({ ...prev, image: '' }));
        toast.success('Đã xóa hình ảnh điểm đến.');
      }
    } catch (err) {
      toast.error('Lỗi khi xóa hình ảnh.');
    }
  };

  // Live Data Processing & Formatting for Recharts
  const scatterData = rules.map(r => ({
    support: parseFloat((toNumber(r.support) * 100).toFixed(3)),
    confidence: parseFloat((toNumber(r.confidence) * 100).toFixed(1)),
    lift: parseFloat(toNumber(r.lift).toFixed(3)),
    rule: formatRuleLabel(r),
    rec_score: parseFloat(toNumber(r.recommendation_score, toNumber(r.confidence) * toNumber(r.lift)).toFixed(3))
  })).filter(item => item.support > 0 && item.confidence > 0);

  const getLiftColor = (lift) => {
    if (lift > 3.0) return '#e11d48'; // deep rose
    if (lift > 2.0) return '#f43f5e'; // rose
    if (lift > 1.5) return '#fb7185'; // pink-rose
    if (lift > 1.0) return '#fda4af'; // light-pink
    return '#fecdd3'; // very light-pink
  };

  const liftHistogram = (() => {
    const bins = [0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 10];
    const data = bins.map((bin, i) => {
      if (i === bins.length - 1) return null;
      const nextBin = bins[i + 1];
      const count = rules.filter(r => toNumber(r.lift) >= bin && toNumber(r.lift) < nextBin).length;
      return {
        range: `${bin}-${nextBin}`,
        count
      };
    }).filter(x => x !== null && x.count > 0);
    return data;
  })();

  const topItems = (() => {
    const counts = {};
    rules.forEach(r => {
      getRuleItems(r).forEach(item => {
        counts[item] = (counts[item] || 0) + 1;
      });
    });
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 15)
      .map(([name, count]) => ({ name, count }));
  })();

  const clusterScatter = destinations.map(d => ({
    cost: d['Avg Cost (USD/day)'] || d.Cost || 0.0,
    rating: d['Average Rating'] || d.Rating || d['Avg Rating'] || 3.0,
    cluster: d.Cluster !== undefined ? d.Cluster : 0,
    name: d['Destination Name'] || d.name
  }));

  const kmeansBarData = clusterProfiles.map(c => ({
    name: `Cụm ${c.Cluster} (${c.Cost_Level})`,
    count: c.Size || 0
  }));

  const ratingDistribution = [1, 2, 3, 4, 5].map(star => ({
    star: `${star} ⭐`,
    count: ratings.filter(r => Math.round(r.rating) === star).length
  }));

  const realVsSimData = (() => {
    const real = stats?.real_ratings || ratings.filter(r => r.is_real).length || 0;
    const total = stats?.total_ratings || ratings.length || 0;
    const sim = Math.max(0, total - real);
    return [
      { name: 'Đánh giá Thực', value: real, color: '#c24482' },
      { name: 'Đánh giá Mô phỏng', value: sim, color: '#fd662f' }
    ];
  })();

  const reviewsTimeline = (() => {
    const monthlyData = {};
    ratings.forEach(r => {
      if (r.timestamp) {
        const month = r.timestamp.substring(0, 7); // "YYYY-MM"
        monthlyData[month] = (monthlyData[month] || 0) + 1;
      }
    });
    const entries = Object.entries(monthlyData);
    return entries.map(([name, count]) => ({ name, count })).sort((a, b) => a.name.localeCompare(b.name));
  })();

  const destContinentData = (() => {
    const counts = {};
    destinations.forEach(d => {
      const c = d.Continent || 'Asia';
      counts[c] = (counts[c] || 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({
      name,
      value,
      color: CONTINENT_COLORS[name] || '#6b7280'
    }));
  })();

  const destCostData = (() => {
    const categories = ['Budget', 'Moderate', 'Expensive', 'Luxury'];
    const counts = { Budget: 0, Moderate: 0, Expensive: 0, Luxury: 0 };
    destinations.forEach(d => {
      const cat = d.Cost_Category || 'Moderate';
      if (counts[cat] !== undefined) counts[cat]++;
    });
    return categories.map(name => ({
      name,
      count: counts[name],
      fill: COST_COLORS[name]
    }));
  })();

  // Modals List Filtering
  const getFilteredModalData = () => {
    if (activeModal === 'destinations') {
      return destinations.filter(d =>
        d['Destination Name']?.toLowerCase().includes(modalSearch.toLowerCase()) ||
        d.Country?.toLowerCase().includes(modalSearch.toLowerCase()) ||
        d.Type?.toLowerCase().includes(modalSearch.toLowerCase())
      );
    }
    if (activeModal === 'countries') {
      const countries = Array.from(new Set(destinations.map(d => d.Country).filter(Boolean)));
      return countries.filter(c => c.toLowerCase().includes(modalSearch.toLowerCase()));
    }
    if (activeModal === 'rules') {
      return rules.filter(r =>
        formatRuleLabel(r).toLowerCase().includes(modalSearch.toLowerCase())
      );
    }
    if (activeModal === 'users_ratings') {
      return users.filter(u =>
        u.username?.toLowerCase().includes(modalSearch.toLowerCase()) ||
        u.email?.toLowerCase().includes(modalSearch.toLowerCase())
      );
    }
    return [];
  };

  // Rules Paginated
  const sortedAndFilteredRules = rules
    .filter(r => formatRuleLabel(r).toLowerCase().includes(rulesSearch.toLowerCase()))
    .sort((a, b) => {
      let valA = a[rulesSortKey];
      let valB = b[rulesSortKey];
      if (rulesSortKey === 'recommendation_score') {
        valA = a.recommendation_score || (a.confidence * a.lift);
        valB = b.recommendation_score || (b.confidence * b.lift);
      }
      if (rulesSortOrder === 'asc') return valA > valB ? 1 : -1;
      return valA < valB ? 1 : -1;
    });

  const paginatedRules = sortedAndFilteredRules.slice(
    (rulesPage - 1) * rulesPerPage,
    rulesPage * rulesPerPage
  );
  const rulesTotalPages = Math.max(1, Math.ceil(sortedAndFilteredRules.length / rulesPerPage));

  const handleRulesSort = (key) => {
    if (rulesSortKey === key) {
      setRulesSortOrder(rulesSortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setRulesSortKey(key);
      setRulesSortOrder('desc');
    }
    setRulesPage(1);
  };

  // Destinations Paginated
  const filteredDests = destinations.filter(d =>
    d['Destination Name']?.toLowerCase().includes(destsSearch.toLowerCase()) ||
    d.Country?.toLowerCase().includes(destsSearch.toLowerCase()) ||
    d.Type?.toLowerCase().includes(destsSearch.toLowerCase())
  );

  const paginatedDests = filteredDests.slice(
    (destsPage - 1) * destsPerPage,
    destsPage * destsPerPage
  );
  const destsTotalPages = Math.max(1, Math.ceil(filteredDests.length / destsPerPage));

  if (!isAuthenticated) {
    return (
      <div className="admin-login-container">
        <ToastContainer position="top-right" autoClose={3000} />
        <div>
          <div className="admin-login-card glass-panel">
            <h2 className="font-heading">Khai Phá Dữ Liệu Du Lịch</h2>
            <p className="login-subtitle">Nhập mật khẩu quản trị viên để đăng nhập Dashboard Thống kê</p>
            <form onSubmit={handleLogin}>
              <div className="input-group">
                <input
                  type="password"
                  placeholder="Nhập mật khẩu"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoFocus
                />
              </div>
              <button type="submit" className="login-button font-heading">
                XÁC THỰC TRUY CẬP
              </button>
            </form>
          </div>
          <div style={{
            marginTop: '1.5rem',
            textAlign: 'center',
            color: 'var(--on-surface-variant, #544249)',
            fontSize: '0.85rem',
            opacity: 0.8
          }}>
            GVHD: ThS. Phạm Thị Trúc Mai | Sinh viên thực hiện: Thạch Thị Xuân Linh_DA22TTA_110122013
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-page-container admin-page-new">
      <ToastContainer position="top-right" autoClose={3000} />
      
      {/* Header section */}
      <header className="admin-header-new glass-panel-new">
        <div>
          <span className="admin-eyebrow-new font-label-caps">ADMIN MANAGEMENT</span>
          <h1 className="font-headline-lg">Hệ Thống Thống Kê & Khai Phá Dữ Liệu</h1>
          <p className="font-body-md" style={{ margin: 0, opacity: 0.8 }}>
            Phân tích luật kết hợp Apriori, phân cụm K-Means địa điểm, quản lý điểm đến và tài khoản
          </p>
        </div>
        <button className="btn-logout-new" onClick={handleLogout}>
          🚪 Đăng xuất
        </button>
      </header>

      {/* 4 KPI Cards Dashboard Overview */}
      <section className="stats-grid-new">
        <button className="stat-card-new glass-panel-new" onClick={() => setActiveModal('destinations')}>
          <div className="stat-icon-new primary">🗺️</div>
          <div>
            <div className="stat-label-new font-label-caps">Điểm Đến</div>
            <h2 className="stat-value-new font-display-lg">{stats?.total_destinations || 0}</h2>
          </div>
        </button>
        <button className="stat-card-new glass-panel-new" onClick={() => setActiveModal('countries')}>
          <div className="stat-icon-new secondary">🌍</div>
          <div>
            <div className="stat-label-new font-label-caps">Quốc Gia</div>
            <h2 className="stat-value-new font-display-lg">{stats?.total_countries || 0}</h2>
          </div>
        </button>
        <button className="stat-card-new glass-panel-new" onClick={() => setActiveModal('rules')}>
          <div className="stat-icon-new tertiary">📋</div>
          <div>
            <div className="stat-label-new font-label-caps">Luật Apriori</div>
            <h2 className="stat-value-new font-display-lg">{rules.length || 0}</h2>
          </div>
        </button>
        <button className="stat-card-new glass-panel-new" onClick={() => setActiveModal('users_ratings')}>
          <div className="stat-icon-new neutral">⭐</div>
          <div>
            <div className="stat-label-new font-label-caps">Người Dùng / Đánh Giá</div>
            <h2 className="stat-value-new font-display-lg" style={{ fontSize: '24px', lineHeight: '2.4' }}>
              {stats?.total_users || 0} U / {stats?.total_ratings || 0} R
            </h2>
          </div>
        </button>
      </section>

      {/* Tabs Navigation */}
      <nav className="tabs-nav-new">
        <button className={`tab-btn-new ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
          📊 Thống kê Tổng Quan
        </button>
        <button className={`tab-btn-new ${activeTab === 'apriori' ? 'active' : ''}`} onClick={() => setActiveTab('apriori')}>
          🔍 Luật Kết Hợp Apriori
        </button>
        <button className={`tab-btn-new ${activeTab === 'kmeans' ? 'active' : ''}`} onClick={() => setActiveTab('kmeans')}>
          🗂️ Phân Cụm K-Means
        </button>
        <button className={`tab-btn-new ${activeTab === 'reviews' ? 'active' : ''}`} onClick={() => setActiveTab('reviews')}>
          ⭐ Đánh Giá ({ratings.length})
        </button>
        <button className={`tab-btn-new ${activeTab === 'destinations' ? 'active' : ''}`} onClick={() => setActiveTab('destinations')}>
          📍 Quản Lý Điểm Đến ({destinations.length})
        </button>
        <button className={`tab-btn-new ${activeTab === 'users' ? 'active' : ''}`} onClick={() => setActiveTab('users')}>
          👥 Quản Lý Tài Khoản ({users.length})
        </button>
      </nav>

      {/* Loading Wrapper */}
      {loading ? (
        <div className="admin-loading-wrapper glass-panel-new">
          <div className="spinner"></div>
          <p>Đang đồng bộ dữ liệu hệ thống từ MongoDB...</p>
        </div>
      ) : (
        <div className="tab-container">
          
          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="tab-pane-new">
              <div className="section-grid-new cols-2">
                <div className="section-card-new glass-panel-new">
                  <h3 className="section-title-new font-headline-md">Phân Bố Châu Lục</h3>
                  <div style={{ height: '300px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={destContinentData}
                          dataKey="value"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          outerRadius={90}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        >
                          {destContinentData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => [`${value} điểm đến`, 'Số lượng']} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="section-card-new glass-panel-new">
                  <h3 className="section-title-new font-headline-md">Phân Bố Theo Mức Chi Phí</h3>
                  <div style={{ height: '300px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={destCostData}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip formatter={(value) => [`${value} địa điểm`, 'Tổng số']} />
                        <Bar dataKey="count">
                          {destCostData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              <div className="section-grid-new cols-3">
                <div className="section-card-new glass-panel-new">
                  <h4 className="section-subtitle-new font-label-caps">Trạng Thái Thuật Toán</h4>
                  <div className="health-indicators" style={{ display: 'grid', gap: '1rem', marginTop: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>Luật kết hợp Apriori</span>
                      <span className="badge" style={{ backgroundColor: '#dcfce7', color: '#15803d' }}>Hoạt động ({rules.length} luật)</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>Phân cụm K-Means</span>
                      <span className="badge" style={{ backgroundColor: '#f3e8ff', color: '#7e22ce' }}>Đã chia {clusterProfiles.length} cụm</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>Lọc cộng tác (CF)</span>
                      <span className="badge" style={{ backgroundColor: '#e0f2fe', color: '#0369a1' }}>Đã tạo ma trận</span>
                    </div>
                  </div>
                </div>

                <div className="section-card-new glass-panel-new">
                  <h4 className="section-subtitle-new font-label-caps">Dữ Liệu Đánh Giá</h4>
                  <div className="health-indicators" style={{ display: 'grid', gap: '1rem', marginTop: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>Đánh giá thực tế</span>
                      <strong>{stats?.real_ratings || 0}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>Đánh giá mô phỏng</span>
                      <strong>{Math.max(0, (stats?.total_ratings || 0) - (stats?.real_ratings || 0))}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>Người dùng đã đăng ký</span>
                      <strong>{stats?.total_users || 0}</strong>
                    </div>
                  </div>
                </div>

                <div className="section-card-new glass-panel-new">
                  <h4 className="section-subtitle-new font-label-caps">Thông Tin Hệ Thống</h4>
                  <p className="font-body-md" style={{ marginTop: '1rem', lineHeight: '1.6' }}>
                    Hệ thống đề xuất du lịch sử dụng mô hình lai kết hợp **Content-Based Filtering (TF-IDF)** và **Apriori Association Rules** làm cốt lõi, bổ trợ bởi **Collaborative Filtering** và phân cụm **K-Means**.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: APRIORI */}
          {activeTab === 'apriori' && (
            <div className="tab-pane-new">
              <div className="section-grid-new kmeans-layout">
                {/* Control Sidebar */}
                <div className="section-card-new glass-panel-new" style={{ alignSelf: 'start' }}>
                  <h3 className="section-title-new font-headline-md">Điều Chỉnh Thuật Toán</h3>
                  <div className="form-group-new">
                    <label className="form-label-new">Min Support: <code>{minSupport}</code></label>
                    <input
                      type="range" min="0.005" max="0.05" step="0.005"
                      value={minSupport} onChange={(e) => setMinSupport(parseFloat(e.target.value))}
                      className="slider-new"
                    />
                  </div>
                  <div className="form-group-new">
                    <label className="form-label-new">Min Confidence: <code>{minConfidence}</code></label>
                    <input
                      type="range" min="0.05" max="0.5" step="0.05"
                      value={minConfidence} onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
                      className="slider-new"
                    />
                  </div>
                  <div className="form-group-new">
                    <label className="form-label-new">Min Lift: <code>{minLift}</code></label>
                    <input
                      type="range" min="0.5" max="3.0" step="0.1"
                      value={minLift} onChange={(e) => setMinLift(parseFloat(e.target.value))}
                      className="slider-new"
                    />
                  </div>
                  <button
                    className="btn-primary-new"
                    onClick={handleRunApriori}
                    disabled={actionLoading.apriori}
                    style={{ marginTop: '1rem' }}
                  >
                    {actionLoading.apriori ? '⏳ Đang Chạy...' : '▶️ Chạy Lại Apriori'}
                  </button>

                  {runComparison && (
                    <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(194, 68, 130, 0.08)', borderRadius: '12px' }}>
                      <h4 className="font-label-caps" style={{ margin: '0 0 0.5rem', color: 'var(--primary)' }}>Lần Chạy Vừa Rồi</h4>
                      <p className="font-body-md" style={{ margin: 0 }}>
                        Tạo <strong>{runComparison.count}</strong> luật trong <strong>{runComparison.duration}s</strong>.<br />
                        <span style={{ fontSize: '13px', color: '#c24482', fontWeight: 600 }}>{runComparison.diffText}</span>
                      </p>
                    </div>
                  )}
                </div>

                {/* Visualizations Area */}
                <div style={{ display: 'grid', gap: '1.5rem' }}>
                  <div className="section-grid-new cols-2">
                    <div className="section-card-new glass-panel-new">
                      <h3 className="section-title-new font-headline-md">Đồ Thị Support vs Confidence</h3>
                      <div style={{ height: '280px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <ScatterChart margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                            <XAxis dataKey="support" type="number" name="Support" unit="%" label={{ value: 'Support %', position: 'bottom', offset: 0 }} />
                            <YAxis dataKey="confidence" type="number" name="Confidence" unit="%" label={{ value: 'Confidence %', angle: -90, position: 'insideLeft' }} />
                            <Tooltip
                              cursor={{ strokeDasharray: '3 3' }}
                              content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                  const data = payload[0].payload;
                                  return (
                                    <div className="glass-panel-new" style={{ padding: '0.75rem', border: '1px solid var(--primary)', background: '#fff' }}>
                                      <p style={{ margin: '0 0 0.25rem', fontSize: '11px', fontFamily: 'monospace', maxWidth: '300px', wordBreak: 'break-all' }}>{data.rule}</p>
                                      <div style={{ fontSize: '12px' }}>
                                        <strong>Support:</strong> {data.support}%<br />
                                        <strong>Confidence:</strong> {data.confidence}%<br />
                                        <strong>Lift:</strong> {data.lift}<br />
                                        <strong>Rec Score:</strong> {data.rec_score}
                                      </div>
                                    </div>
                                  );
                                }
                                return null;
                              }}
                            />
                            <Scatter name="Rules" data={scatterData}>
                              {scatterData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={getLiftColor(entry.lift)} />
                              ))}
                            </Scatter>
                          </ScatterChart>
                        </ResponsiveContainer>
                      </div>
                      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', fontSize: '11px', marginTop: '10px' }}>
                        <span>Lift:</span>
                        <span><span style={{ color: '#fda4af' }}>■</span> &lt; 1.5</span>
                        <span><span style={{ color: '#fb7185' }}>■</span> 1.5 - 2.0</span>
                        <span><span style={{ color: '#f43f5e' }}>■</span> 2.0 - 3.0</span>
                        <span><span style={{ color: '#e11d48' }}>■</span> &gt; 3.0</span>
                      </div>
                    </div>

                    <div className="section-card-new glass-panel-new">
                      <h3 className="section-title-new font-headline-md">Phân Phối Chỉ Số Lift</h3>
                      <div style={{ height: '280px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={liftHistogram}>
                            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                            <XAxis dataKey="range" label={{ value: 'Khoảng chỉ số Lift', position: 'bottom', offset: 0 }} />
                            <YAxis />
                            <Tooltip formatter={(value) => [`${value} luật`, 'Số lượng']} />
                            <Bar dataKey="count" fill="#7c3aed" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>

                  <div className="section-card-new glass-panel-new">
                    <h3 className="section-title-new font-headline-md">Top 15 Thuộc Tính Phổ Biến</h3>
                    <div style={{ height: '320px' }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={topItems} layout="vertical" margin={{ left: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                          <XAxis type="number" label={{ value: 'Tần suất xuất hiện trong tập luật', position: 'bottom', offset: 0 }} />
                          <YAxis dataKey="name" type="category" width={140} />
                          <Tooltip formatter={(value) => [`Xuất hiện ${value} lần`, 'Tần suất']} />
                          <Bar dataKey="count" fill="#0284c7" radius={[0, 4, 4, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>
              </div>

              {/* Rules List Table */}
              <div className="section-card-new glass-panel-new" style={{ marginTop: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                  <h3 className="font-headline-md" style={{ margin: 0 }}>Danh Sách Luật Kết Hợp Apriori ({sortedAndFilteredRules.length} luật)</h3>
                  <input
                    type="text"
                    placeholder="Tìm theo Antecedent hoặc Consequent..."
                    value={rulesSearch}
                    onChange={(e) => { setRulesSearch(e.target.value); setRulesPage(1); }}
                    className="admin-modal-search"
                    style={{ width: '320px', margin: 0 }}
                  />
                </div>
                <div className="table-responsive">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>STT</th>
                        <th style={{ width: '45%' }}>Quy Luật</th>
                        <th className="text-center clickable-stat-card" onClick={() => handleRulesSort('support')}>Support {rulesSortKey === 'support' && (rulesSortOrder === 'desc' ? '▼' : '▲')}</th>
                        <th className="text-center clickable-stat-card" onClick={() => handleRulesSort('confidence')}>Confidence {rulesSortKey === 'confidence' && (rulesSortOrder === 'desc' ? '▼' : '▲')}</th>
                        <th className="text-center clickable-stat-card" onClick={() => handleRulesSort('lift')}>Lift {rulesSortKey === 'lift' && (rulesSortOrder === 'desc' ? '▼' : '▲')}</th>
                        <th className="text-center clickable-stat-card" onClick={() => handleRulesSort('recommendation_score')}>Rec Score {rulesSortKey === 'recommendation_score' && (rulesSortOrder === 'desc' ? '▼' : '▲')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {paginatedRules.map((r, i) => {
                        const recScore = toNumber(r.recommendation_score, toNumber(r.confidence) * toNumber(r.lift));
                        const left = Array.isArray(r.antecedents) ? r.antecedents.join(', ') : formatRuleLabel(r).split(' => ')[0];
                        const right = Array.isArray(r.consequents) ? r.consequents.join(', ') : formatRuleLabel(r).split(' => ')[1];
                        return (
                          <tr key={i}>
                            <td>{(rulesPage - 1) * rulesPerPage + i + 1}</td>
                            <td>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
                                <span style={{ padding: '3px 8px', background: 'rgba(124, 58, 237, 0.08)', borderRadius: '6px', fontFamily: 'monospace' }}>{left}</span>
                                <span style={{ color: 'var(--primary)' }}>➜</span>
                                <span style={{ padding: '3px 8px', background: 'rgba(22, 163, 74, 0.08)', borderRadius: '6px', fontFamily: 'monospace' }}>{right}</span>
                              </div>
                            </td>
                            <td className="text-center font-bold">{(toNumber(r.support) * 100).toFixed(2)}%</td>
                            <td className="text-center font-bold">{(toNumber(r.confidence) * 100).toFixed(1)}%</td>
                            <td className="text-center text-rose-600 font-bold">{toNumber(r.lift).toFixed(2)}</td>
                            <td className="text-center text-cyan-700 font-bold">{recScore.toFixed(3)}</td>
                          </tr>
                        );
                      })}
                      {paginatedRules.length === 0 && (
                        <tr>
                          <td colSpan="6" className="text-center font-body-md" style={{ padding: '2rem' }}>Không tìm thấy luật kết hợp phù hợp.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
                <div className="pagination" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1.5rem', marginTop: '1.5rem' }}>
                  <button
                    className="btn-neutral-new" style={{ padding: '8px 16px', fontSize: '13px' }}
                    onClick={() => setRulesPage(p => Math.max(1, p - 1))} disabled={rulesPage === 1}
                  >
                    ◀️ Trang trước
                  </button>
                  <span className="font-body-md">Trang <strong>{Math.min(rulesPage, rulesTotalPages)}</strong> / {rulesTotalPages}</span>
                  <button
                    className="btn-neutral-new" style={{ padding: '8px 16px', fontSize: '13px' }}
                    onClick={() => setRulesPage(p => Math.min(rulesTotalPages, p + 1))}
                    disabled={rulesPage >= rulesTotalPages}
                  >
                    Trang sau ▶️
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: K-MEANS */}
          {activeTab === 'kmeans' && (
            <div className="tab-pane-new">
              <div className="section-grid-new kmeans-layout">
                {/* Control Sidebar */}
                <div className="section-card-new glass-panel-new" style={{ alignSelf: 'start' }}>
                  <h3 className="section-title-new font-headline-md">Điều Chỉnh Phân Cụm</h3>
                  <div className="form-group-new">
                    <label className="form-label-new">Chọn Số Cụm (K):</label>
                    <select
                      value={nClusters}
                      onChange={(e) => setNClusters(parseInt(e.target.value))}
                      className="select-new"
                    >
                      {[3, 4, 5, 6, 7, 8, 9, 10].map(k => (
                        <option key={k} value={k}>{k} Cụm</option>
                      ))}
                    </select>
                  </div>
                  <button
                    className="btn-primary-new bg-purple"
                    onClick={handleRunClustering}
                    disabled={actionLoading.clustering}
                    style={{ background: 'var(--secondary)' }}
                  >
                    {actionLoading.clustering ? '⏳ Đang Chạy...' : '▶️ Chạy Lại K-Means'}
                  </button>

                  {/* Elbow Chart */}
                  {elbowData.length > 0 && (
                    <div style={{ marginTop: '2rem' }}>
                      <h4 className="font-label-caps" style={{ marginBottom: '1rem' }}>Đồ Thị Cực Trị Elbow (SSE)</h4>
                      <div style={{ height: '180px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={elbowData} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
                            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                            <XAxis dataKey="k" />
                            <YAxis />
                            <Tooltip formatter={(value) => [value.toFixed(1), 'SSE']} />
                            <Line type="monotone" dataKey="sse" stroke="var(--primary)" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                      <p className="font-body-md" style={{ fontSize: '11px', opacity: 0.8, marginTop: '8px', textAlign: 'center' }}>
                        Điểm khuỷu tay (elbow) là số cụm tối ưu nhất cho cấu trúc dữ liệu.
                      </p>
                    </div>
                  )}
                </div>

                {/* Charts Area */}
                <div style={{ display: 'grid', gap: '1.5rem' }}>
                  <div className="section-grid-new cols-2">
                    <div className="section-card-new glass-panel-new">
                      <h3 className="section-title-new font-headline-md">Phân Bố Chi Phí vs Rating Theo Cụm</h3>
                      <div style={{ height: '280px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <ScatterChart margin={{ top: 10, right: 10, bottom: 20, left: -10 }}>
                            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                            <XAxis dataKey="cost" type="number" name="Cost" unit="$/day" label={{ value: 'Cost (USD/day)', position: 'bottom', offset: 0 }} />
                            <YAxis dataKey="rating" type="number" name="Rating" domain={[1, 5]} label={{ value: 'Rating Stars', angle: -90, position: 'insideLeft' }} />
                            <Tooltip
                              cursor={{ strokeDasharray: '3 3' }}
                              content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                  const data = payload[0].payload;
                                  return (
                                    <div className="glass-panel-new" style={{ padding: '0.75rem', border: '1px solid var(--secondary)', background: '#fff' }}>
                                      <strong style={{ fontSize: '13px' }}>{data.name}</strong>
                                      <div style={{ fontSize: '12px', marginTop: '4px' }}>
                                        Cụm: <code>#{data.cluster}</code><br />
                                        Chi phí: ${data.cost}/ngày<br />
                                        Đánh gia: {data.rating} ⭐
                                      </div>
                                    </div>
                                  );
                                }
                                return null;
                              }}
                            />
                            {Array.from({ length: 11 }).map((_, c) => (
                              <Scatter
                                key={c}
                                name={`Cụm ${c}`}
                                data={clusterScatter.filter(d => d.cluster === c)}
                                fill={COLORS[c % COLORS.length]}
                              />
                            ))}
                          </ScatterChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    <div className="section-card-new glass-panel-new">
                      <h3 className="section-title-new font-headline-md">Quy Mô Điểm Đến Từng Cụm</h3>
                      <div style={{ height: '280px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={kmeansBarData}>
                            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip formatter={(value) => [`${value} điểm đến`, 'Quy mô']} />
                            <Bar dataKey="count" fill="#7c3aed" radius={[4, 4, 0, 0]}>
                              {kmeansBarData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Profiles Table */}
              <div className="section-card-new glass-panel-new" style={{ marginTop: '2rem' }}>
                <h3 className="section-title-new font-headline-md">Bảng Hồ Sơ Phân Cụm Địa Điểm (Cluster Profiles)</h3>
                <div className="table-responsive">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Cụm</th>
                        <th>Phân Khúc Mức Chi Phí</th>
                        <th className="text-center">Số Lượng Điểm Đến</th>
                        <th className="text-center">Chi Phí TB ($/ngày)</th>
                        <th className="text-center">Rating Trung Bình</th>
                        <th>Ví Dụ Điển Hình</th>
                      </tr>
                    </thead>
                    <tbody>
                      {clusterProfiles.map((c) => {
                        const inCluster = destinations.filter(d => d.Cluster === c.Cluster);
                        const examples = inCluster
                          .sort((a, b) => (b['Average Rating'] || 0) - (a['Average Rating'] || 0))
                          .slice(0, 3)
                          .map(d => d['Destination Name'] || d.name)
                          .join(', ');
                        
                        return (
                          <tr key={c.Cluster}>
                            <td className="font-bold"><code>#{c.Cluster}</code></td>
                            <td>
                              <span className={`cluster-badge cost-${c.Cost_Level?.toLowerCase() || 'moderate'}`}>
                                {c.Cost_Level}
                              </span>
                            </td>
                            <td className="text-center font-bold">{c.Size} địa điểm</td>
                            <td className="text-center text-rose-600 font-bold">${c.Avg_Cost_Per_Day?.toFixed(1)}</td>
                            <td className="text-center text-yellow-600 font-bold">⭐ {c.Avg_Rating?.toFixed(2)}</td>
                            <td style={{ fontSize: '13px', opacity: 0.9 }}>{examples || 'Chưa phân cụm'}</td>
                          </tr>
                        );
                      })}
                      {clusterProfiles.length === 0 && (
                        <tr>
                          <td colSpan="6" className="text-center" style={{ padding: '2rem' }}>Chưa có hồ sơ phân cụm. Vui lòng bấm chạy K-Means.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: REVIEWS */}
          {activeTab === 'reviews' && (
            <div className="tab-pane-new">
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
                <button
                  className="btn-secondary-new"
                  onClick={handleRefreshCF}
                  disabled={actionLoading.cf}
                  style={{ width: 'auto', padding: '10px 24px' }}
                >
                  {actionLoading.cf ? '⏳ Đang tính toán...' : '🔄 Cập Nhật Ma Trận Collaborative Filtering'}
                </button>
              </div>

              <div className="section-grid-new cols-3">
                <div className="section-card-new glass-panel-new">
                  <h3 className="section-title-new font-headline-md">Phân Bố Số Sao (1-5 Sao)</h3>
                  <div style={{ height: '240px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={ratingDistribution}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                        <XAxis dataKey="star" />
                        <YAxis />
                        <Tooltip formatter={(value) => [`${value} đánh giá`, 'Tần số']} />
                        <Bar dataKey="count" fill="#16a34a" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="section-card-new glass-panel-new">
                  <h3 className="section-title-new font-headline-md">Tỷ Lệ Đánh Giá Thực vs Giả Lập</h3>
                  <div style={{ height: '240px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={realVsSimData}
                          dataKey="value"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={80}
                          paddingAngle={5}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        >
                          {realVsSimData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => [`${value} lượt`, 'Số lượng']} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="section-card-new glass-panel-new">
                  <h3 className="section-title-new font-headline-md">Tương Tác Theo Thời Gian</h3>
                  <div style={{ height: '240px' }}>
                    {reviewsTimeline.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={reviewsTimeline}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip formatter={(value) => [value, 'Số lượng review']} />
                        <Line type="monotone" dataKey="count" stroke="#c24482" strokeWidth={2.5} dot={{ r: 4 }} />
                      </LineChart>
                    </ResponsiveContainer>
                    ) : (
                      <div className="empty-chart-state">Chua co du lieu timestamp de ve bieu do thoi gian.</div>
                    )}
                  </div>
                </div>
              </div>

              {/* Recent Ratings List Table */}
              <div className="section-card-new glass-panel-new" style={{ marginTop: '2rem' }}>
                <h3 className="section-title-new font-headline-md">Danh Sách Đánh Giá Gần Nhất ({ratings.length} đánh giá)</h3>
                <div className="table-responsive" style={{ maxHeight: '600px' }}>
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Người Dùng</th>
                        <th>Điểm Đến Thụ Hưởng</th>
                        <th className="text-center">Số Sao</th>
                        <th className="text-center">Hành Động</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ratings.slice(0, 150).map((r, i) => (
                        <tr key={i}>
                          <td className="font-bold"><code>{anonymizeUserId(r.user_id)}</code></td>
                          <td className="dest-name-cell">{r.destination_name}</td>
                          <td className="text-center text-yellow-600 font-bold" style={{ fontSize: '15px' }}>
                            {'⭐'.repeat(Math.round(r.rating))} <span style={{ fontSize: '12px', color: '#6b7280' }}>({r.rating})</span>
                          </td>
                          <td className="text-center">
                            <button
                              className="logout-btn"
                              style={{ padding: '6px 12px', fontSize: '12px', borderColor: '#fca5a5', color: '#ef4444' }}
                              onClick={() => handleDeleteRating(r.user_id, r.destination_name)}
                            >
                              🗑️ Xóa
                            </button>
                          </td>
                        </tr>
                      ))}
                      {ratings.length === 0 && (
                        <tr>
                          <td colSpan="4" className="text-center" style={{ padding: '2rem' }}>Không có lượt đánh giá nào trong hệ thống.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: DESTINATIONS */}
          {activeTab === 'destinations' && (
            <div className="tab-pane-new">
              <div className="section-card-new glass-panel-new">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                  <h3 className="font-headline-md" style={{ margin: 0 }}>Danh sách địa danh từ dataset</h3>
                  <div style={{ display: 'flex', gap: '1rem' }}>
                    <input
                      type="text"
                      placeholder="Tìm tên, quốc gia, thể loại..."
                      value={destsSearch}
                      onChange={(e) => { setDestsSearch(e.target.value); setDestsPage(1); }}
                      className="admin-modal-search"
                      style={{ width: '280px', margin: 0 }}
                    />
                  </div>
                </div>

                <div className="table-responsive">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Ảnh</th>
                        <th>Tên Điểm Đến</th>
                        <th>Quốc Gia</th>
                        <th>Châu Lục</th>
                        <th>Thể Loại</th>
                        <th>Chi Phí Avg</th>
                        <th className="text-center">Rating</th>
                        <th className="text-center">Cluster</th>
                      </tr>
                    </thead>
                    <tbody>
                      {paginatedDests.map((d, i) => {
                        const name = d['Destination Name'] || d.name;
                        return (
                          <tr key={i}>
                            <td>
                              {d.image ? (
                                <img src={d.image} alt={name} style={{ width: '60px', height: '40px', objectFit: 'cover', borderRadius: '4px' }} />
                              ) : (
                                <div style={{ width: '60px', height: '40px', background: '#e5e7eb', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', color: '#9ca3af' }}>N/A</div>
                              )}
                            </td>
                            <td className="dest-name-cell">{name}</td>
                            <td>{d.Country}</td>
                            <td>{d.Continent || 'Asia'}</td>
                            <td>{d.Type}</td>
                            <td className="font-bold text-rose-600">${d['Avg Cost (USD/day)'] || d.Cost}/ngày</td>
                            <td className="text-center font-bold">⭐ {d['Average Rating'] || d.Rating || d['Avg Rating'] || '3.0'}</td>
                            <td className="text-center font-bold"><code>#{d.Cluster !== undefined ? d.Cluster : '0'}</code></td>
                          </tr>
                        );
                      })}
                      {paginatedDests.length === 0 && (
                        <tr>
                          <td colSpan="8" className="text-center" style={{ padding: '2rem' }}>Không tìm thấy điểm đến phù hợp.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>

                <div className="pagination" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1.5rem', marginTop: '1.5rem' }}>
                  <button
                    className="btn-neutral-new" style={{ padding: '8px 16px', fontSize: '13px' }}
                    onClick={() => setDestsPage(p => Math.max(1, p - 1))} disabled={destsPage === 1}
                  >
                    ◀️ Trang trước
                  </button>
                  <span className="font-body-md">Trang <strong>{Math.min(destsPage, destsTotalPages)}</strong> / {destsTotalPages}</span>
                  <button
                    className="btn-neutral-new" style={{ padding: '8px 16px', fontSize: '13px' }}
                    onClick={() => setDestsPage(p => Math.min(destsTotalPages, p + 1))}
                    disabled={destsPage >= destsTotalPages}
                  >
                    Trang sau ▶️
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: USERS */}
          {activeTab === 'users' && (
            <div className="tab-pane-new">
              <div className="section-card-new glass-panel-new">
                <h3 className="section-title-new font-headline-md">Quản Lý Tài Khoản Khách Hàng</h3>
                <div className="table-responsive">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Tên Đăng Nhập</th>
                        <th>Họ Và Tên</th>
                        <th>Email Liên Hệ</th>
                        <th className="text-center">Số Lượt Đánh Giá</th>
                        <th>Ngày Đăng Ký</th>
                        <th className="text-center">Trạng Thái</th>
                        <th className="text-center">Hành Động</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((u, i) => (
                        <tr key={i}>
                          <td className="font-bold">{u.username}</td>
                          <td>{u.full_name || 'N/A'}</td>
                          <td>{u.email}</td>
                          <td className="text-center font-bold text-cyan-600">{u.reviews_count || 0}</td>
                          <td>{u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}</td>
                          <td className="text-center">
                            <span className={`badge ${u.status === 'locked' ? 'bg-red-100 text-red-800' : 'bg-emerald-100 text-emerald-800'}`}>
                              {u.status === 'locked' ? 'Bị Khóa' : 'Hoạt Động'}
                            </span>
                          </td>
                          <td className="text-center">
                            <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                              <button
                                className="btn-logout-new"
                                style={{ padding: '6px 12px', fontSize: '12px', borderColor: u.status === 'locked' ? '#a7f3d0' : '#fbcfe8', color: u.status === 'locked' ? '#059669' : '#db2777' }}
                                onClick={() => handleToggleLock(u.username)}
                              >
                                {u.status === 'locked' ? '🔓 Mở khóa' : '🔒 Khóa'}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                      {users.length === 0 && (
                        <tr>
                          <td colSpan="7" className="text-center" style={{ padding: '2rem' }}>Không tìm thấy tài khoản người dùng.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

        </div>
      )}

      {/* KPI Detail Modal Overlay */}
      {activeModal && (
        <div className="admin-modal-overlay" onClick={() => setActiveModal(null)}>
          <div className="admin-modal-content" onClick={(e) => e.stopPropagation()} style={{ width: '70%', maxWidth: '900px' }}>
            <div className="admin-modal-header">
              <h2 className="font-headline-md">
                {activeModal === 'destinations' && `Danh Sách Điểm Đến (${destinations.length} địa điểm)`}
                {activeModal === 'countries' && `Danh Sách Quốc Gia (${Array.from(new Set(destinations.map(d => d.Country))).length} quốc gia)`}
                {activeModal === 'rules' && `Danh Sách Luật Kết Hợp Apriori (${rules.length} quy luật)`}
                {activeModal === 'users_ratings' && 'Danh Sách Tài Khoản & Review'}
              </h2>
              <button className="admin-modal-close" onClick={() => setActiveModal(null)}>&times;</button>
            </div>
            <div className="admin-modal-body">
              <input
                type="text"
                className="admin-modal-search"
                placeholder="Tìm kiếm thông tin nhanh..."
                value={modalSearch}
                onChange={(e) => setModalSearch(e.target.value)}
                autoFocus
              />
              
              <div className="admin-modal-list-container" style={{ maxHeight: '450px', overflowY: 'auto' }}>
                {activeModal === 'destinations' && (
                  <table className="admin-table compact-table">
                    <thead>
                      <tr>
                        <th>Tên</th>
                        <th>Quốc Gia</th>
                        <th>Châu Lục</th>
                        <th>Thể Loại</th>
                        <th>Chi Phí Avg</th>
                      </tr>
                    </thead>
                    <tbody>
                      {getFilteredModalData().map((d, index) => (
                        <tr key={index}>
                          <td className="font-bold">{d['Destination Name'] || d.name}</td>
                          <td>{d.Country}</td>
                          <td>{d.Continent || 'Asia'}</td>
                          <td>{d.Type}</td>
                          <td>${d['Avg Cost (USD/day)'] || d.Cost}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}

                {activeModal === 'countries' && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '1rem', padding: '1rem 0' }}>
                    {getFilteredModalData().map((c, index) => (
                      <div key={index} className="glass-panel-new" style={{ padding: '0.75rem 1rem', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', fontWeight: 600 }}>
                        📍 {c}
                      </div>
                    ))}
                  </div>
                )}

                {activeModal === 'rules' && (
                  <table className="admin-table compact-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Luật Apriori</th>
                        <th className="text-center">Support</th>
                        <th className="text-center">Confidence</th>
                        <th className="text-center">Lift</th>
                      </tr>
                    </thead>
                    <tbody>
                      {getFilteredModalData().map((r, index) => (
                        <tr key={index}>
                          <td>{index + 1}</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{formatRuleLabel(r)}</td>
                          <td className="text-center">{(toNumber(r.support) * 100).toFixed(2)}%</td>
                          <td className="text-center">{(toNumber(r.confidence) * 100).toFixed(1)}%</td>
                          <td className="text-center">{toNumber(r.lift).toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}

                {activeModal === 'users_ratings' && (
                  <table className="admin-table compact-table">
                    <thead>
                      <tr>
                        <th>Tên Người Dùng</th>
                        <th>Email</th>
                        <th>Vai Trò</th>
                        <th className="text-center">Số Review</th>
                        <th className="text-center">Trạng Thái</th>
                      </tr>
                    </thead>
                    <tbody>
                      {getFilteredModalData().map((u, index) => (
                        <tr key={index}>
                          <td className="font-bold">{u.username}</td>
                          <td>{u.email}</td>
                          <td>{u.role}</td>
                          <td className="text-center font-bold text-rose-500">{u.reviews_count || 0}</td>
                          <td className="text-center">
                            <span className={`badge ${u.status === 'locked' ? 'bg-red-100 text-red-800' : 'bg-emerald-100 text-emerald-800'}`}>
                              {u.status === 'locked' ? 'Bị Khóa' : 'Hoạt Động'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Destination Add / Edit CRUD Modal */}
      {isDestModalOpen && (
        <div className="admin-modal-overlay">
          <div className="admin-modal-content" style={{ width: '80%', maxWidth: '1000px' }}>
            <div className="admin-modal-header">
              <h2 className="font-headline-md">{destFormMode === 'add' ? '➕ Thêm Điểm Đến Mới' : '✏️ Chỉnh Sửa Thông Tin Điểm Đến'}</h2>
              <button className="admin-modal-close" onClick={() => setIsDestModalOpen(false)}>&times;</button>
            </div>
            
            <form onSubmit={handleSaveDestination}>
              <div className="admin-modal-body" style={{ maxHeight: '70vh', overflowY: 'auto', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', padding: '1.5rem' }}>
                
                {/* Left Form Side */}
                <div>
                  <div className="form-group-new">
                    <label className="form-label-new">Tên Điểm Đến *</label>
                    <input
                      type="text" required
                      value={destForm.destination_name}
                      onChange={(e) => setDestForm({ ...destForm, destination_name: e.target.value })}
                      disabled={destFormMode === 'edit'}
                    />
                  </div>

                  <div className="form-group-new" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <label className="form-label-new">Quốc Gia *</label>
                      <input
                        type="text" required
                        value={destForm.country}
                        onChange={(e) => setDestForm({ ...destForm, country: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="form-label-new">Châu Lục</label>
                      <select
                        value={destForm.continent}
                        onChange={(e) => setDestForm({ ...destForm, continent: e.target.value })}
                        className="select-new"
                      >
                        {['Asia', 'Europe', 'Americas', 'Africa', 'Oceania'].map(c => (
                          <option key={c} value={c}>{c}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="form-group-new" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <label className="form-label-new">Thể Loại</label>
                      <select
                        value={destForm.type}
                        onChange={(e) => setDestForm({ ...destForm, type: e.target.value })}
                        className="select-new"
                      >
                        {['Cultural', 'Adventure', 'Nature', 'Beach', 'Historical', 'Urban'].map(t => (
                          <option key={t} value={t}>{t}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="form-label-new">Mùa Lý Tưởng</label>
                      <select
                        value={destForm.best_season}
                        onChange={(e) => setDestForm({ ...destForm, best_season: e.target.value })}
                        className="select-new"
                      >
                        {['Spring', 'Summer', 'Autumn', 'Winter', 'Year-round'].map(s => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="form-group-new" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <label className="form-label-new">Chi Phí TB ($/ngày)</label>
                      <input
                        type="number" required min="1"
                        value={destForm.avg_cost}
                        onChange={(e) => setDestForm({ ...destForm, avg_cost: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="form-label-new">Phân Khúc Chi Phí</label>
                      <select
                        value={destForm.cost_category}
                        onChange={(e) => setDestForm({ ...destForm, cost_category: e.target.value })}
                        className="select-new"
                      >
                        {['Budget', 'Moderate', 'Expensive', 'Luxury'].map(c => (
                          <option key={c} value={c}>{c}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="form-group-new" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <label className="form-label-new">Vĩ độ (Latitude)</label>
                      <input
                        type="number" step="any" placeholder="Ví dụ: 21.0285"
                        value={destForm.latitude}
                        onChange={(e) => setDestForm({ ...destForm, latitude: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="form-label-new">Kinh độ (Longitude)</label>
                      <input
                        type="number" step="any" placeholder="Ví dụ: 105.8542"
                        value={destForm.longitude}
                        onChange={(e) => setDestForm({ ...destForm, longitude: e.target.value })}
                      />
                    </div>
                  </div>
                </div>

                {/* Right Form Side: Media & Description */}
                <div>
                  <div className="form-group-new">
                    <label className="form-label-new">Mô Tả Điểm Đến</label>
                    <textarea
                      value={destForm.description}
                      onChange={(e) => setDestForm({ ...destForm, description: e.target.value })}
                      rows="4"
                      style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--outline-variant)', padding: '0.75rem', fontSize: '14px', outline: 'none' }}
                      placeholder="Mô tả tóm tắt cảnh quan, sức hút và nét đặc sắc..."
                    />
                  </div>

                  {/* Media Management Area */}
                  <div className="form-group-new" style={{ border: '1px dashed var(--outline-variant)', borderRadius: '16px', padding: '1rem' }}>
                    <label className="form-label-new font-label-caps" style={{ fontWeight: 'bold' }}>Quản Lý Ảnh / Phương Tiện</label>
                    
                    {destForm.image ? (
                      <div style={{ position: 'relative', margin: '0.5rem 0 1rem 0' }}>
                        <img src={destForm.image} alt="Preview" style={{ width: '100%', height: '140px', objectFit: 'cover', borderRadius: '8px' }} />
                        <button
                          type="button"
                          onClick={handleImageDelete}
                          style={{ position: 'absolute', top: '8px', right: '8px', background: 'rgba(239, 68, 68, 0.9)', border: 'none', color: '#fff', borderRadius: '50%', width: '28px', height: '28px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}
                          title="Xóa ảnh"
                        >
                          &times;
                        </button>
                      </div>
                    ) : (
                      <div style={{ height: '100px', background: 'var(--surface-container-low)', borderRadius: '8px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--on-surface-variant)', fontSize: '13px', margin: '0.5rem 0 1rem 0' }}>
                        🖼️ Chưa có hình ảnh điểm đến
                      </div>
                    )}

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                      <label className="btn-logout-new" style={{ justifyContent: 'center', cursor: 'pointer', margin: 0, padding: '8px 12px', fontSize: '12px' }}>
                        {actionLoading.imageUpload ? '⏳ Uploading...' : '📁 Tải Ảnh Lên'}
                        <input type="file" accept="image/*" onChange={handleImageUpload} style={{ display: 'none' }} disabled={actionLoading.imageUpload} />
                      </label>
                      <button
                        type="button"
                        className="btn-logout-new"
                        style={{ padding: '8px 12px', fontSize: '12px' }}
                        onClick={handleImageAutoFetch}
                        disabled={actionLoading.imageFetch}
                      >
                        {actionLoading.imageFetch ? '⏳ Đang Tải...' : '✨ Auto-Fetch'}
                      </button>
                    </div>
                    
                    <div style={{ marginTop: '0.75rem' }}>
                      <input
                        type="text"
                        placeholder="Hoặc điền URL ảnh thủ công..."
                        value={destForm.image}
                        onChange={(e) => setDestForm({ ...destForm, image: e.target.value })}
                        style={{ fontSize: '12px', padding: '6px 12px' }}
                      />
                    </div>
                  </div>
                </div>

              </div>
              <div className="admin-modal-footer" style={{ borderTop: '1px solid rgba(135, 113, 122, 0.2)', padding: '1rem 1.5rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                <button type="button" className="btn-neutral-new" style={{ padding: '10px 24px' }} onClick={() => setIsDestModalOpen(false)}>
                  Hủy Bỏ
                </button>
                <button type="submit" className="btn-primary-new" style={{ width: 'auto', padding: '10px 32px' }}>
                  Lưu Thông Tin
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      <footer style={{
        marginTop: '3rem',
        padding: '1.5rem',
        textAlign: 'center',
        borderTop: '1px solid rgba(135, 113, 122, 0.15)',
        color: 'var(--on-surface-variant, #544249)',
        fontSize: '0.85rem',
        opacity: 0.8
      }}>
        GVHD: ThS. Phạm Thị Trúc Mai | Sinh viên thực hiện: Thạch Thị Xuân Linh_DA22TTA_110122013
      </footer>
    </div>
  );
};

export default AdminPage;
