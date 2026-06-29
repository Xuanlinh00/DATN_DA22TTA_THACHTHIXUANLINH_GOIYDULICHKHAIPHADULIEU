import React, { useState, useEffect } from 'react';
import { adminApi, destinationsApi, dataApi } from '../services/api';
import { ScatterChart, Scatter, BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [stats, setStats] = useState(null);
  const [rules, setRules] = useState([]);
  const [ratings, setRatings] = useState([]);
  const [clusterProfiles, setClusterProfiles] = useState([]);
  const [destinations, setDestinations] = useState([]);
  const [users, setUsers] = useState([]);
  
  const [minSupport, setMinSupport] = useState(0.01);
  const [minConfidence, setMinConfidence] = useState(0.1);
  const [minLift, setMinLift] = useState(1.0);
  const [nClusters, setNClusters] = useState(5);
  
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchRule, setSearchRule] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const rulesPerPage = 50;

  useEffect(() => {
    const adminSession = sessionStorage.getItem('admin_authenticated');
    if (adminSession === 'true') {
      setIsAuthenticated(true);
      fetchAllData();
    }
  }, []);

  const handleLogin = (e) => {
    e.preventDefault();
    if (password === 'admin' || password === 'admin123') {
      sessionStorage.setItem('admin_authenticated', 'true');
      setIsAuthenticated(true);
      fetchAllData();
    } else {
      toast.error('Mật khẩu không đúng!');
    }
  };

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [statsRes, rulesRes, ratingsRes, destsRes, usersRes] = await Promise.all([
        adminApi.getStats(),
        adminApi.getRules(),
        adminApi.getRatings(),
        destinationsApi.getAll({ limit: 1000 }),
        adminApi.getUsers()
      ]);
      
      if (statsRes.data.success) {
        setStats(statsRes.data.stats);
        setClusterProfiles(statsRes.data.cluster_profiles || []);
      }
      if (rulesRes.data.success) setRules(rulesRes.data.rules || []);
      if (ratingsRes.data.success) setRatings(ratingsRes.data.ratings || []);
      if (destsRes.data.success) setDestinations(destsRes.data.destinations || []);
      if (usersRes.data.success) setUsers(usersRes.data.users || []);
    } catch (err) {
      toast.error('Lỗi tải dữ liệu');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunApriori = async () => {
    const startTime = Date.now();
    try {
      const res = await adminApi.runApriori(minSupport, minConfidence, minLift);
      const duration = ((Date.now() - startTime) / 1000).toFixed(2);
      if (res.data.success) {
        toast.success(`✅ Tạo ${res.data.rules_count || 0} luật trong ${duration}s`);
        fetchAllData();
      }
    } catch (err) {
      toast.error('Lỗi chạy Apriori');
    }
  };

  const handleRunClustering = async () => {
    try {
      const res = await adminApi.runClustering(nClusters);
      if (res.data.success) {
        toast.success(`✅ Phân cụm thành ${nClusters} nhóm`);
        fetchAllData();
      }
    } catch (err) {
      toast.error('Lỗi chạy K-Means');
    }
  };

  const handleRefreshCF = async () => {
    try {
      const res = await adminApi.refreshCF();
      if (res.data.success) {
        toast.success('✅ Cập nhật ma trận CF');
      }
    } catch (err) {
      toast.error('Lỗi refresh CF');
    }
  };

  // Data Processing
  const filteredRules = rules.filter(r => 
    r.rule?.toLowerCase().includes(searchRule.toLowerCase())
  );
  
  const paginatedRules = filteredRules.slice(
    (currentPage - 1) * rulesPerPage,
    currentPage * rulesPerPage
  );

  // Charts Data
  const scatterData = rules.map(r => ({
    support: r.support * 100,
    confidence: r.confidence * 100,
    lift: r.lift,
    rule: r.rule
  }));

  const liftHistogram = (() => {
    const bins = [0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 10];
    const counts = bins.map((bin, i) => {
      if (i === bins.length - 1) return 0;
      const nextBin = bins[i + 1];
      return {
        range: `${bin}-${nextBin}`,
        count: rules.filter(r => r.lift >= bin && r.lift < nextBin).length
      };
    });
    return counts.filter(c => c.count > 0);
  })();

  const topItems = (() => {
    const itemCounts = {};
    rules.forEach(r => {
      const items = r.rule?.match(/\{([^}]+)\}/g)?.map(s => s.slice(1, -1).split(',').map(x => x.trim())).flat() || [];
      items.forEach(item => {
        itemCounts[item] = (itemCounts[item] || 0) + 1;
      });
    });
    return Object.entries(itemCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 15)
      .map(([name, count]) => ({ name, count }));
  })();

  const clusterScatter = destinations.map(d => ({
    cost: d['Avg Cost (USD/day)'] || d.Cost || 0,
    rating: d['Average Rating'] || d.Rating || 0,
    cluster: d.Cluster || 0,
    name: d['Destination Name'] || d.name
  }));

  const clusterDistribution = clusterProfiles.map(c => ({
    name: c.Cost_Level || `Cluster ${c.Cluster}`,
    count: c.Size || 0
  }));

  const ratingDistribution = [5, 4, 3, 2, 1].map(star => ({
    star: `${star}⭐`,
    count: ratings.filter(r => r.rating === star).length
  }));

  const continentDistribution = (() => {
    const continentMap = {
      'Asia': ['Vietnam', 'Thailand', 'Japan', 'China', 'India', 'Indonesia', 'Malaysia', 'Singapore', 'Philippines', 'South Korea'],
      'Europe': ['France', 'Italy', 'Spain', 'Germany', 'UK', 'Switzerland', 'Netherlands', 'Austria', 'Greece', 'Portugal'],
      'Americas': ['USA', 'Canada', 'Mexico', 'Brazil', 'Argentina', 'Chile', 'Peru'],
      'Africa': ['Egypt', 'Morocco', 'South Africa', 'Kenya', 'Tanzania'],
      'Oceania': ['Australia', 'New Zealand', 'Fiji']
    };
    const counts = {};
    destinations.forEach(d => {
      const country = d.Country;
      for (const [continent, countries] of Object.entries(continentMap)) {
        if (countries.some(c => country?.includes(c))) {
          counts[continent] = (counts[continent] || 0) + 1;
          return;
        }
      }
      counts['Other'] = (counts['Other'] || 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  })();

  const COLORS = ['#c24482', '#7c3aed', '#0284c7', '#16a34a', '#ea580c', '#f59e0b'];

  if (!isAuthenticated) {
    return (
      <div className="admin-login-page">
        <div>
          <div className="admin-login-card glass-panel">
            <h2>Admin Dashboard</h2>
            <form onSubmit={handleLogin}>
              <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
              <button type="submit">Login</button>
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
    <div className="admin-dashboard">
      <ToastContainer position="top-right" autoClose={3000} />
      
      <header className="admin-dash-header">
        <h1 className="font-heading">📊 Admin Analytics Dashboard</h1>
        <button onClick={() => { sessionStorage.removeItem('admin_authenticated'); setIsAuthenticated(false); }}>
          Logout
        </button>
      </header>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card glass-panel">
          <div className="kpi-icon">🗺️</div>
          <div className="kpi-value">{stats?.total_destinations || 0}</div>
          <div className="kpi-label">Điểm Đến</div>
        </div>
        <div className="kpi-card glass-panel">
          <div className="kpi-icon">🌍</div>
          <div className="kpi-value">{stats?.total_countries || 0}</div>
          <div className="kpi-label">Quốc Gia</div>
        </div>
        <div className="kpi-card glass-panel">
          <div className="kpi-icon">📋</div>
          <div className="kpi-value">{rules.length}</div>
          <div className="kpi-label">Luật Apriori</div>
        </div>
        <div className="kpi-card glass-panel">
          <div className="kpi-icon">⭐</div>
          <div className="kpi-value">{ratings.length}</div>
          <div className="kpi-label">Đánh Giá</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-nav">
        {['overview', 'apriori', 'kmeans', 'reviews', 'destinations'].map(tab => (
          <button key={tab} className={activeTab === tab ? 'active' : ''} onClick={() => setActiveTab(tab)}>
            {tab === 'overview' && '📊 Tổng Quan'}
            {tab === 'apriori' && '🔍 Apriori'}
            {tab === 'kmeans' && '📊 K-Means'}
            {tab === 'reviews' && '⭐ Đánh Giá'}
            {tab === 'destinations' && '🗺️ Điểm Đến'}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        
        {activeTab === 'apriori' && (
          <div className="section glass-panel">
            <h2>🔍 Apriori Rules Analysis ({rules.length} luật)</h2>
            
            {/* Control Panel */}
            <div className="controls">
              <div className="control-group">
                <label>Min Support: {minSupport}</label>
                <input type="range" min="0.005" max="0.05" step="0.005" value={minSupport} onChange={(e) => setMinSupport(parseFloat(e.target.value))} />
              </div>
              <div className="control-group">
                <label>Min Confidence: {minConfidence}</label>
                <input type="range" min="0.05" max="0.5" step="0.05" value={minConfidence} onChange={(e) => setMinConfidence(parseFloat(e.target.value))} />
              </div>
              <div className="control-group">
                <label>Min Lift: {minLift}</label>
                <input type="range" min="0.5" max="2" step="0.1" value={minLift} onChange={(e) => setMinLift(parseFloat(e.target.value))} />
              </div>
              <button className="btn-primary" onClick={handleRunApriori}>▶️ Chạy Apriori</button>
            </div>

            {/* Charts Grid */}
            <div className="charts-grid">
              {/* Scatter */}
              <div className="chart-box">
                <h3>Support vs Confidence (màu = Lift)</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="support" name="Support %" />
                    <YAxis dataKey="confidence" name="Confidence %" />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Scatter data={scatterData} fill="#c24482" />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>

              {/* Histogram */}
              <div className="chart-box">
                <h3>Phân Phối Lift</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={liftHistogram}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="range" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#7c3aed" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Top Items */}
              <div className="chart-box full-width">
                <h3>Top 15 Items Phổ Biến</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={topItems} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={150} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#0284c7" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Rules Table */}
            <div className="rules-table-section">
              <input type="text" placeholder="Tìm luật..." value={searchRule} onChange={(e) => setSearchRule(e.target.value)} />
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Luật</th>
                      <th>Support</th>
                      <th>Confidence</th>
                      <th>Lift</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedRules.map((r, i) => (
                      <tr key={i}>
                        <td>{(currentPage - 1) * rulesPerPage + i + 1}</td>
                        <td style={{ fontSize: '0.85em', fontFamily: 'monospace' }}>{r.rule}</td>
                        <td>{(r.support * 100).toFixed(2)}%</td>
                        <td>{(r.confidence * 100).toFixed(1)}%</td>
                        <td>{r.lift?.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="pagination">
                <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1}>◀️</button>
                <span>Trang {currentPage} / {Math.ceil(filteredRules.length / rulesPerPage)}</span>
                <button onClick={() => setCurrentPage(p => Math.min(Math.ceil(filteredRules.length / rulesPerPage), p + 1))} disabled={currentPage >= Math.ceil(filteredRules.length / rulesPerPage)}>▶️</button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'kmeans' && (
          <div className="section glass-panel">
            <h2>📊 K-Means Clustering</h2>
            
            <div className="controls">
              <div className="control-group">
                <label>Số Cụm (K): {nClusters}</label>
                <input type="range" min="3" max="8" value={nClusters} onChange={(e) => setNClusters(parseInt(e.target.value))} />
              </div>
              <button className="btn-primary" onClick={handleRunClustering}>▶️ Chạy K-Means</button>
            </div>

            <div className="charts-grid">
              <div className="chart-box">
                <h3>Cost vs Rating theo Cluster</h3>
                <ResponsiveContainer width="100%" height={350}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="cost" name="Cost (USD/day)" />
                    <YAxis dataKey="rating" name="Rating" />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    {[0, 1, 2, 3, 4, 5, 6, 7].map(cluster => (
                      <Scatter key={cluster} data={clusterScatter.filter(d => d.cluster === cluster)} fill={COLORS[cluster % COLORS.length]} name={`Cluster ${cluster}`} />
                    ))}
                  </ScatterChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-box">
                <h3>Số Điểm Đến theo Cluster</h3>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={clusterDistribution}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#7c3aed" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Cluster</th>
                    <th>Loại</th>
                    <th>Số Điểm</th>
                    <th>Chi Phí TB</th>
                  </tr>
                </thead>
                <tbody>
                  {clusterProfiles.map(c => (
                    <tr key={c.Cluster}>
                      <td>#{c.Cluster}</td>
                      <td><span className="badge">{c.Cost_Level}</span></td>
                      <td>{c.Size}</td>
                      <td>${c.Avg_Cost_Per_Day?.toFixed(0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'reviews' && (
          <div className="section glass-panel">
            <h2>⭐ User Reviews Analysis</h2>
            
            <div className="controls">
              <button className="btn-primary" onClick={handleRefreshCF}>🔄 Refresh CF Matrix</button>
            </div>

            <div className="charts-grid">
              <div className="chart-box">
                <h3>Phân Phối Rating</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={ratingDistribution}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="star" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#16a34a" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-box">
                <h3>Thống Kê</h3>
                <div className="stats-box">
                  <div className="stat-item">
                    <div className="stat-value">{ratings.length}</div>
                    <div className="stat-label">Tổng Đánh Giá</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">{(ratings.reduce((s, r) => s + r.rating, 0) / ratings.length).toFixed(2)}</div>
                    <div className="stat-label">Điểm TB</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">{new Set(ratings.map(r => r.user_id)).size}</div>
                    <div className="stat-label">Users</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>User ID</th>
                    <th>Điểm Đến</th>
                    <th>Rating</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {ratings.slice(0, 50).map((r, i) => (
                    <tr key={i}>
                      <td>{r.user_id}</td>
                      <td>{r.destination_name}</td>
                      <td>{r.rating} ⭐</td>
                      <td>{r.timestamp || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'destinations' && (
          <div className="section glass-panel">
            <h2>🗺️ Destination Management</h2>
            
            <div className="charts-grid">
              <div className="chart-box">
                <h3>Phân Bố Châu Lục</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={continentDistribution} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                      {continentDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-box">
                <h3>Top 10 Điểm Đến</h3>
                <div className="top-list">
                  {destinations.slice(0, 10).map((d, i) => (
                    <div key={i} className="top-item">
                      <span className="rank">{i + 1}</span>
                      <span className="name">{d['Destination Name']}</span>
                      <span className="value">{d.Country}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Điểm Đến</th>
                    <th>Quốc Gia</th>
                    <th>Chi Phí</th>
                    <th>Rating</th>
                    <th>Cluster</th>
                  </tr>
                </thead>
                <tbody>
                  {destinations.slice(0, 50).map((d, i) => (
                    <tr key={i}>
                      <td>{d['Destination Name']}</td>
                      <td>{d.Country}</td>
                      <td>${d['Avg Cost (USD/day)'] || d.Cost}</td>
                      <td>{d['Average Rating'] || d.Rating} ⭐</td>
                      <td>{d.Cluster}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'overview' && (
          <div className="overview-grid">
            <div className="section glass-panel">
              <h3>🎯 Quick Stats</h3>
              <div className="quick-stats">
                <div>📋 <strong>{rules.length}</strong> luật Apriori</div>
                <div>📊 <strong>{clusterProfiles.length}</strong> clusters</div>
                <div>⭐ <strong>{ratings.length}</strong> reviews</div>
                <div>🗺️ <strong>{destinations.length}</strong> destinations</div>
                <div>👥 <strong>{users.length}</strong> users</div>
              </div>
            </div>

            <div className="section glass-panel">
              <h3>📈 System Health</h3>
              <div className="health-indicators">
                <div className="health-item">
                  <span className="health-label">Apriori Rules</span>
                  <span className="health-status ok">✓ Active</span>
                </div>
                <div className="health-item">
                  <span className="health-label">K-Means Clusters</span>
                  <span className="health-status ok">✓ {clusterProfiles.length} Clusters</span>
                </div>
                <div className="health-item">
                  <span className="health-label">CF Matrix</span>
                  <span className="health-status ok">✓ Ready</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
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

export default AdminDashboard;
