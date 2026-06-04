import React, { useState, useEffect } from 'react';
import { adminApi, destinationsApi, dataApi } from '../services/api';
import './AdminPage.css';

const AdminPage = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  
  // Dashboard stats & profiles
  const [stats, setStats] = useState(null);
  const [clusterProfiles, setClusterProfiles] = useState([]);
  const [ratings, setRatings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Algorithm Parameters
  const [minSupport, setMinSupport] = useState(0.01);
  const [minConfidence, setMinConfidence] = useState(0.1);
  const [minLift, setMinLift] = useState(1.0);
  const [nClusters, setNClusters] = useState(5);

  // Status for long running actions
  const [actionLoading, setActionLoading] = useState({
    apriori: false,
    clustering: false,
    cf: false,
    delete: null // will hold rating key
  });

  // Modal states for stats detail panels
  const [activeModal, setActiveModal] = useState(null);
  const [modalData, setModalData] = useState([]);
  const [modalLoading, setModalLoading] = useState(false);
  const [modalSearch, setModalSearch] = useState('');

  const handleOpenModal = async (type) => {
    setActiveModal(type);
    setModalData([]);
    setModalLoading(true);
    setModalSearch('');
    try {
      if (type === 'destinations') {
        const res = await destinationsApi.getAll({ limit: 500 });
        if (res.data.success) {
          setModalData(res.data.destinations || []);
        }
      } else if (type === 'countries') {
        const res = await dataApi.getSummary();
        if (res.data.success) {
          setModalData(res.data.data.countries || []);
        }
      } else if (type === 'rules') {
        const res = await adminApi.getRules();
        if (res.data.success) {
          setModalData(res.data.rules || []);
        }
      }
    } catch (err) {
      console.error('Failed to load stats details:', err);
    } finally {
      setModalLoading(false);
    }
  };

  // Check session storage on mount
  useEffect(() => {
    const adminSession = sessionStorage.getItem('admin_authenticated');
    if (adminSession === 'true') {
      setIsAuthenticated(true);
      fetchAdminData();
    }
  }, []);

  const handleLogin = (e) => {
    e.preventDefault();
    if (password === 'admin' || password === 'admin123') {
      sessionStorage.setItem('admin_authenticated', 'true');
      setIsAuthenticated(true);
      setLoginError('');
      fetchAdminData();
    } else {
      setLoginError('Mật khẩu không chính xác. Thử lại với "admin" hoặc "admin123"!');
    }
  };

  const fetchAdminData = async () => {
    setLoading(true);
    setError('');
    try {
      const statsRes = await adminApi.getStats();
      if (statsRes.data.success) {
        setStats(statsRes.data.stats);
        setClusterProfiles(statsRes.data.cluster_profiles || []);
      }

      const ratingsRes = await adminApi.getRatings();
      if (ratingsRes.data.success) {
        setRatings(ratingsRes.data.ratings || []);
      }
    } catch (err) {
      console.error(err);
      setError('Lỗi khi tải dữ liệu từ máy chủ.');
    } finally {
      setLoading(false);
    }
  };

  // Run Apriori Mining
  const handleRunApriori = async () => {
    setActionLoading(prev => ({ ...prev, apriori: true }));
    setError('');
    setSuccessMessage('');
    try {
      const res = await adminApi.runApriori(minSupport, minConfidence, minLift);
      if (res.data.success) {
        setSuccessMessage(res.data.message);
        // Refresh stats
        fetchAdminData();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể chạy Apriori.');
    } finally {
      setActionLoading(prev => ({ ...prev, apriori: false }));
    }
  };

  // Run Clustering
  const handleRunClustering = async () => {
    setActionLoading(prev => ({ ...prev, clustering: true }));
    setError('');
    setSuccessMessage('');
    try {
      const res = await adminApi.runClustering(nClusters);
      if (res.data.success) {
        setSuccessMessage(res.data.message);
        setClusterProfiles(res.data.profiles || []);
        fetchAdminData();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể chạy K-Means.');
    } finally {
      setActionLoading(prev => ({ ...prev, clustering: false }));
    }
  };

  // Refresh Similarity Matrix
  const handleRefreshCF = async () => {
    setActionLoading(prev => ({ ...prev, cf: true }));
    setError('');
    setSuccessMessage('');
    try {
      const res = await adminApi.refreshCF();
      if (res.data.success) {
        setSuccessMessage(res.data.message);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể cập nhật Collaborative Filtering.');
    } finally {
      setActionLoading(prev => ({ ...prev, cf: false }));
    }
  };

  // Delete User Rating
  const handleDeleteRating = async (userId, destName) => {
    const itemKey = `${userId}_${destName}`;
    if (!window.confirm(`Bạn có chắc chắn muốn xóa đánh giá của ${userId} cho ${destName}?`)) {
      return;
    }

    setActionLoading(prev => ({ ...prev, delete: itemKey }));
    setError('');
    setSuccessMessage('');
    try {
      const res = await adminApi.deleteRating(userId, destName);
      if (res.data.success) {
        setSuccessMessage(res.data.message);
        // Refresh local array directly
        setRatings(prev => prev.filter(r => !(r.user_id === userId && r.destination_name === destName)));
        // Refresh stats
        fetchAdminData();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Lỗi khi xóa đánh giá.');
    } finally {
      setActionLoading(prev => ({ ...prev, delete: null }));
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem('admin_authenticated');
    setIsAuthenticated(false);
    setPassword('');
  };

  const renderDestinationsList = () => {
    const filtered = modalData.filter(d => 
      d['Destination Name']?.toLowerCase().includes(modalSearch.toLowerCase()) ||
      d['Country']?.toLowerCase().includes(modalSearch.toLowerCase()) ||
      d['Type']?.toLowerCase().includes(modalSearch.toLowerCase())
    );
    
    return (
      <div className="table-responsive" style={{ maxHeight: '55vh' }}>
        <table className="admin-table">
          <thead>
            <tr>
              <th>Điểm Đến</th>
              <th>Quốc Gia</th>
              <th>Thể Loại</th>
              <th>Chi Phí Avg</th>
              <th>Mùa</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((d, i) => (
              <tr key={i}>
                <td className="dest-name-cell">{d['Destination Name']}</td>
                <td>{d['Country']}</td>
                <td>
                  <span className={`cluster-badge cost-${d['Cluster']?.toLowerCase() || 'moderate'}`}>
                    {d['Type']}
                  </span>
                </td>
                <td>${d['Cost'] || d['Avg Cost (USD/day)']}</td>
                <td>{d['Season'] || d['Best Season']}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderCountriesList = () => {
    const filtered = modalData.filter(c => 
      c.toLowerCase().includes(modalSearch.toLowerCase())
    );
    
    return (
      <div className="admin-modal-grid" style={{ maxHeight: '55vh' }}>
        {filtered.map((c, i) => (
          <div key={i} className="admin-modal-card">
            🌍 {c}
          </div>
        ))}
      </div>
    );
  };

  const renderRulesList = () => {
    const filtered = modalData.filter(r => 
      r.rule?.toLowerCase().includes(modalSearch.toLowerCase())
    );
    
    return (
      <div className="table-responsive" style={{ maxHeight: '55vh' }}>
        <table className="admin-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Luật Kết Hợp (Apriori)</th>
              <th className="text-center">Support</th>
              <th className="text-center">Confidence</th>
              <th className="text-center">Lift</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r, i) => (
              <tr key={i}>
                <td>{i + 1}</td>
                <td style={{ fontFamily: 'monospace', fontSize: '11px' }}>{r.rule}</td>
                <td className="text-center">{(r.support * 100).toFixed(2)}%</td>
                <td className="text-center">{(r.confidence * 100).toFixed(1)}%</td>
                <td className="text-center">{r.lift?.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  // Password Gate Interface
  if (!isAuthenticated) {
    return (
      <div className="admin-login-container">
        <div className="admin-login-card glass-panel">
          <h2>🔒 Đăng Nhập Quản Trị Viên</h2>
          <p className="login-subtitle">Nhập mật khẩu để truy cập công cụ khai phá dữ liệu</p>
          
          <form onSubmit={handleLogin}>
            <div className="input-group">
              <input
                type="password"
                placeholder="Nhập mật khẩu (ví dụ: admin)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoFocus
              />
            </div>
            {loginError && <div className="login-error">{loginError}</div>}
            <button type="submit" className="login-button font-heading">
              XÁC THỰC
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-page-container">
      {/* Header section */}
      <div className="admin-header glass-panel">
        <div>
          <h1 className="font-heading">⚙️ Trang Quản Trị Hệ Thống</h1>
          <p>Trực quan hóa thống kê và vận hành các thuật toán Khai phá dữ liệu</p>
        </div>
        <button className="logout-btn btn-secondary" onClick={handleLogout}>
          Đăng xuất 🚪
        </button>
      </div>

      {/* Message Notifications */}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}
      {error && <div className="alert alert-error">❌ {error}</div>}

      {/* Main Grid */}
      {loading ? (
        <div className="admin-loading-wrapper glass-panel">
          <div className="spinner"></div>
          <p>Đang tải dữ liệu thống kê từ máy chủ...</p>
        </div>
      ) : (
        <>
          {/* Stats Dashboard */}
          {stats && (
            <div className="stats-grid">
              <div className="stat-card glass-panel clickable-stat-card" onClick={() => handleOpenModal('destinations')} style={{ cursor: 'pointer' }}>
                <span className="stat-icon">🏨</span>
                <div className="stat-info">
                  <h3>Tổng Điểm Đến</h3>
                  <p className="stat-value">{stats.total_destinations}</p>
                </div>
              </div>
              <div className="stat-card glass-panel clickable-stat-card" onClick={() => handleOpenModal('countries')} style={{ cursor: 'pointer' }}>
                <span className="stat-icon">🌍</span>
                <div className="stat-info">
                  <h3>Tổng Quốc Gia</h3>
                  <p className="stat-value">{stats.total_countries}</p>
                </div>
              </div>
              <div className="stat-card glass-panel clickable-stat-card" onClick={() => handleOpenModal('rules')} style={{ cursor: 'pointer' }}>
                <span className="stat-icon">📜</span>
                <div className="stat-info">
                  <h3>Luật Apriori</h3>
                  <p className="stat-value">{stats.total_rules}</p>
                </div>
              </div>
            </div>
          )}

          {/* Core Algorithm Operations Panel */}
          <div className="admin-sections-grid">
            {/* Left Col: Algorithm Triggers */}
            <div className="admin-column">
              <div className="admin-card glass-panel">
                <h2 className="card-title font-heading">🧩 Khai Phá Luật Kết Hợp (Apriori)</h2>
                <p className="card-desc">Quét toàn bộ giao dịch hành trình của khách hàng trong MongoDB để khai phá và tạo luật đề xuất mới.</p>
                
                <div className="param-group">
                  <div className="param-row">
                    <label>Min Support: <code>{minSupport}</code></label>
                    <input 
                      type="range" 
                      min="0.005" 
                      max="0.05" 
                      step="0.005" 
                      value={minSupport} 
                      onChange={(e) => setMinSupport(parseFloat(e.target.value))}
                    />
                  </div>
                  <div className="param-row">
                    <label>Min Confidence: <code>{minConfidence}</code></label>
                    <input 
                      type="range" 
                      min="0.05" 
                      max="0.5" 
                      step="0.05" 
                      value={minConfidence} 
                      onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
                    />
                  </div>
                  <div className="param-row">
                    <label>Min Lift: <code>{minLift}</code></label>
                    <input 
                      type="range" 
                      min="0.5" 
                      max="2.0" 
                      step="0.1" 
                      value={minLift} 
                      onChange={(e) => setMinLift(parseFloat(e.target.value))}
                    />
                  </div>
                </div>

                <button 
                  className="btn-primary run-btn" 
                  onClick={handleRunApriori} 
                  disabled={actionLoading.apriori}
                >
                  {actionLoading.apriori ? (
                    <>
                      <span className="btn-spinner"></span> Đang chạy thuật toán...
                    </>
                  ) : (
                    'Chạy lại Apriori Mining ⚙️'
                  )}
                </button>
              </div>

              <div className="admin-card glass-panel">
                <h2 className="card-title font-heading">📊 Phân Cụm Điểm Đến (K-Means)</h2>
                <p className="card-desc">Sử dụng K-Means Clustering để phân chia các địa điểm thành nhóm chi phí & mua sắm.</p>
                
                <div className="param-group">
                  <div className="param-row flex-row">
                    <label>Số lượng Cụm (K):</label>
                    <select 
                      value={nClusters} 
                      onChange={(e) => setNClusters(parseInt(e.target.value))}
                      className="admin-select"
                    >
                      {[3, 4, 5, 6, 7, 8].map(k => (
                        <option key={k} value={k}>{k} Cụm</option>
                      ))}
                    </select>
                  </div>
                </div>

                <button 
                  className="btn-primary run-btn bg-purple" 
                  onClick={handleRunClustering} 
                  disabled={actionLoading.clustering}
                >
                  {actionLoading.clustering ? (
                    <>
                      <span className="btn-spinner"></span> Đang chạy phân cụm...
                    </>
                  ) : (
                    'Chạy lại Phân Cụm K-Means 📊'
                  )}
                </button>
              </div>

              <div className="admin-card glass-panel">
                <h2 className="card-title font-heading">🔄 Gợi Ý Lọc Cộng Tác (CF)</h2>
                <p className="card-desc">Tính toán lại ma trận tương đồng (Cosine Similarity Matrix) giữa các địa điểm dựa trên đánh giá hiện tại.</p>
                <button 
                  className="btn-primary run-btn bg-cyan" 
                  onClick={handleRefreshCF} 
                  disabled={actionLoading.cf}
                >
                  {actionLoading.cf ? (
                    <>
                      <span className="btn-spinner"></span> Đang tính toán ma trận...
                    </>
                  ) : (
                    'Cập nhật Collaborative Filtering Matrix 🔄'
                  )}
                </button>
              </div>
            </div>

            {/* Right Col: Cluster profiles & ratings list */}
            <div className="admin-column">
              {/* Cluster Profiles Table */}
              <div className="admin-card glass-panel">
                <h2 className="card-title font-heading">📈 Hồ Sơ Cụm Địa Điểm (K-Means Clusters)</h2>
                <div className="table-responsive">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Cụm ID</th>
                        <th>Phân Loại Giá</th>
                        <th>Số Điểm Đến</th>
                        <th>Chi Phí TB</th>
                      </tr>
                    </thead>
                    <tbody>
                      {clusterProfiles.length === 0 ? (
                        <tr>
                          <td colSpan="4" className="text-center">Không có dữ liệu cụm. Hãy chạy lại thuật toán phân cụm.</td>
                        </tr>
                      ) : (
                        clusterProfiles.map((cluster) => (
                          <tr key={cluster.Cluster}>
                            <td><code>Cụm {cluster.Cluster}</code></td>
                            <td>
                              <span className={`cluster-badge cost-${cluster.Cost_Level?.toLowerCase() || 'moderate'}`}>
                                {cluster.Cost_Level}
                              </span>
                            </td>
                            <td>{cluster.Size}</td>
                            <td>${cluster.Avg_Cost_Per_Day?.toFixed(1)} /ngày</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Ratings List Table */}
              <div className="admin-card glass-panel">
                <h2 className="card-title font-heading">⭐ Đánh Giá Người Dùng (Ratings)</h2>
                <p className="card-desc font-12">Danh sách 150 đánh giá mới nhất (Ưu tiên đánh giá thật trước).</p>
                <div className="table-responsive scrollable-table">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>User ID</th>
                        <th>Điểm Đến</th>
                        <th>Điểm</th>
                        <th>Loại</th>
                        <th>Hành động</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ratings.length === 0 ? (
                        <tr>
                          <td colSpan="5" className="text-center">Chưa có đánh giá nào.</td>
                        </tr>
                      ) : (
                        ratings.map((rate, index) => {
                          const itemKey = `${rate.user_id}_${rate.destination_name}_${index}`;
                          return (
                            <tr key={itemKey}>
                              <td className="user-id-cell" title={rate.user_id}>
                                {rate.user_id}
                              </td>
                              <td className="dest-name-cell">
                                {rate.destination_name}
                              </td>
                              <td className="rating-cell">
                                <span className="star-highlight">{rate.rating} ⭐</span>
                              </td>
                              <td>
                                {rate.is_real ? (
                                  <span className="badge-real">Thật</span>
                                ) : (
                                  <span className="badge-sim">Giả</span>
                                )}
                              </td>
                              <td>
                                <button
                                  className="btn-danger"
                                  onClick={() => handleDeleteRating(rate.user_id, rate.destination_name)}
                                  disabled={actionLoading.delete === itemKey}
                                >
                                  {actionLoading.delete === itemKey ? 'Đang xóa...' : 'Xóa 🗑️'}
                                </button>
                              </td>
                            </tr>
                          );
                        })
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {activeModal && (
        <div className="admin-modal-overlay" onClick={() => setActiveModal(null)}>
          <div className="admin-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="admin-modal-header">
              <h2>
                {activeModal === 'destinations' && <>🏨 Danh Sách Điểm Đến ({modalData.length})</>}
                {activeModal === 'countries' && <>🌍 Danh Sách Quốc Gia ({modalData.length})</>}
                {activeModal === 'rules' && <>📜 Danh Sách Luật Apriori ({modalData.length})</>}
              </h2>
              <button className="admin-modal-close" onClick={() => setActiveModal(null)}>&times;</button>
            </div>
            
            <div className="admin-modal-body">
              <input 
                type="text" 
                className="admin-modal-search" 
                placeholder="Tìm kiếm..." 
                value={modalSearch} 
                onChange={(e) => setModalSearch(e.target.value)} 
              />
              
              {modalLoading ? (
                <div className="admin-modal-loading">
                  <div className="modal-spinner"></div>
                  <p>Đang tải dữ liệu...</p>
                </div>
              ) : (
                <div className="admin-modal-list-container">
                  {activeModal === 'destinations' && renderDestinationsList()}
                  {activeModal === 'countries' && renderCountriesList()}
                  {activeModal === 'rules' && renderRulesList()}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPage;
