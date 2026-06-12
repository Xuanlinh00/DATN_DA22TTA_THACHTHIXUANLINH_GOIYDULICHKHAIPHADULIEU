import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { chatApi } from '../services/api';
import { getDestinationImage, getFallbackImage } from '../services/imageService';
import { useRecommendation } from '../contexts/RecommendationContext';
import { useAuth } from '../contexts/AuthContext';
import { translateCountry, translateCategory } from '../utils/translator';
import './ChatbotWidget.css';

// ── LocalStorage keys ────────────────────────────────────────────────────────
const GUEST_SESSIONS_KEY = 'nomadai_guest_sessions';
const ACTIVE_SESSION_ID_KEY = 'nomadai_active_session_id';

const DEFAULT_MESSAGE = {
  sender: 'bot',
  text: 'Xin chào! 👋 Tôi là **Trợ lý du lịch AI**, người đồng hành cùng bạn.\n\nTôi giúp bạn tìm kiếm và đối soát các điểm đến du lịch quốc tế dựa trên thuật toán khai phá dữ liệu.\n\nHãy nhắn cho tôi nhu cầu du lịch của bạn nhé (ví dụ: *"Gợi ý điểm du lịch biển giá rẻ vào mùa hè"*).',
  recommendations: []
};

// ── Helpers ───────────────────────────────────────────────────────────────────
function loadGuestSessions() {
  try {
    const saved = localStorage.getItem(GUEST_SESSIONS_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch { /* ignore */ }
  return [];
}

function saveGuestSessions(sessions) {
  try {
    localStorage.setItem(GUEST_SESSIONS_KEY, JSON.stringify(sessions));
  } catch { /* ignore */ }
}

// ── Vietnamese labels for context display ─────────────────────────────────────
const SEASON_LABELS = { Spring: '🌸 Xuân', Summer: '☀️ Hè', Autumn: '🍂 Thu', Winter: '❄️ Đông' };
const CATEGORY_LABELS = {
  Beach: '🏖️ Biển & Đảo', Mountain: '🏔️ Núi & Rừng', Cultural: '🏛️ Văn Hoá & Lịch Sử',
  City: '🏙️ Thành Phố', Adventure: '🪂 Phiêu Lưu', Wellness: '🧘 Nghỉ Dưỡng',
  Nature: '🌿 Thiên Nhiên', 'Theme Park': '🎡 Vui Chơi',
};
const BUDGET_LABELS = { Budget: '💚 Tiết Kiệm', Moderate: '💙 Bình Dân', Expensive: '💜 Cao Cấp', Luxury: '🌟 Sang Trọng' };

function ChatbotWidget() {
  const navigate = useNavigate();
  const { criteria, results: recResults } = useRecommendation();
  const { user, isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef(null);

  // Sessions and Active Session states
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState('');

  // Track whether we already injected a context message for the current criteria
  const lastContextRef = useRef(null);

  const QUICK_PROMPTS = [
    '🌸 Gợi ý điểm đến mùa xuân',
    '🏖️ Du lịch biển tiết kiệm',
    '🏔️ Thám hiểm núi mạo hiểm',
    '🏛️ Khám phá di sản văn hóa',
  ];

  // ── Load session list when authentication state changes ───────────────────
  const loadSessionsData = useCallback(async () => {
    if (isAuthenticated && user) {
      try {
        const response = await chatApi.getSessions(user.username);
        if (response.data.success) {
          const dbSessions = response.data.sessions || [];
          setSessions(dbSessions);
          
          let lastActiveId = localStorage.getItem(ACTIVE_SESSION_ID_KEY);
          if (!lastActiveId || !dbSessions.some(s => s.session_id === lastActiveId)) {
            if (dbSessions.length > 0) {
              lastActiveId = dbSessions[0].session_id;
            } else {
              lastActiveId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7);
              const newSess = {
                session_id: lastActiveId,
                title: 'Cuộc trò chuyện mới',
                messages: [DEFAULT_MESSAGE],
                updated_at: new Date().toISOString()
              };
              setSessions([newSess]);
              await chatApi.saveSession(newSess.session_id, user.username, newSess.title, newSess.messages);
            }
          }
          setActiveSessionId(lastActiveId);
          localStorage.setItem(ACTIVE_SESSION_ID_KEY, lastActiveId);
        }
      } catch (err) {
        console.error("Failed to load sessions from server:", err);
      }
    } else {
      // Guest mode
      const guestSess = loadGuestSessions();
      let lastActiveId = localStorage.getItem(ACTIVE_SESSION_ID_KEY);
      if (!lastActiveId || !guestSess.some(s => s.session_id === lastActiveId)) {
        if (guestSess.length > 0) {
          lastActiveId = guestSess[0].session_id;
        } else {
          lastActiveId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7);
          const newSess = {
            session_id: lastActiveId,
            title: 'Cuộc trò chuyện mới',
            messages: [DEFAULT_MESSAGE],
            updated_at: new Date().toISOString()
          };
          guestSess.push(newSess);
          saveGuestSessions(guestSess);
        }
      }
      setSessions(guestSess);
      setActiveSessionId(lastActiveId);
      localStorage.setItem(ACTIVE_SESSION_ID_KEY, lastActiveId);
    }
  }, [isAuthenticated, user]);

  useEffect(() => {
    loadSessionsData();
  }, [loadSessionsData]);

  // Derived messages state for the active session
  const activeSessionObj = sessions.find(s => s.session_id === activeSessionId);
  const messages = activeSessionObj ? activeSessionObj.messages : [DEFAULT_MESSAGE];

  // ── Auto-scroll ────────────────────────────────────────────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isOpen, showHistory]);

  // Helper to update active session messages and sync
  const updateActiveSessionMessages = useCallback(async (newMessages) => {
    if (!activeSessionId) return;

    let dynamicTitle = activeSessionObj?.title || 'Cuộc trò chuyện mới';
    if (dynamicTitle === 'Cuộc trò chuyện mới') {
      const firstUserMsg = newMessages.find(m => m.sender === 'user');
      if (firstUserMsg) {
        dynamicTitle = firstUserMsg.text.length > 25 ? firstUserMsg.text.substring(0, 25) + '...' : firstUserMsg.text;
      }
    }

    const updatedSessions = sessions.map(s => {
      if (s.session_id === activeSessionId) {
        return {
          ...s,
          title: dynamicTitle,
          messages: newMessages,
          updated_at: new Date().toISOString()
        };
      }
      return s;
    });

    // Sort by updated_at descending
    updatedSessions.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
    setSessions(updatedSessions);

    if (isAuthenticated && user) {
      try {
        await chatApi.saveSession(activeSessionId, user.username, dynamicTitle, newMessages);
      } catch (err) {
        console.error("Failed to save session to DB:", err);
      }
    } else {
      saveGuestSessions(updatedSessions);
    }
  }, [sessions, activeSessionId, activeSessionObj, isAuthenticated, user]);

  // ── Inject context message when criteria change or chatbox opens ───────────
  useEffect(() => {
    if (!isOpen || !criteria || !activeSessionId) return;

    // Build a fingerprint so we only inject once per unique criteria set
    const fingerprint = JSON.stringify(criteria);
    if (lastContextRef.current === fingerprint) return;
    lastContextRef.current = fingerprint;

    const seasonLabel = SEASON_LABELS[criteria.season] || criteria.season || '';
    const categoryLabel = CATEGORY_LABELS[criteria.category] || criteria.category || '';
    const budgetLabel = BUDGET_LABELS[criteria.budget] || criteria.budget || '';

    const destNames = (recResults || []).slice(0, 5).map(d => d['Destination Name']).filter(Boolean);
    const destList = destNames.length > 0
      ? `\n📍 Các điểm đến đã gợi ý: **${destNames.join('**, **')}**${recResults.length > 5 ? ` và ${recResults.length - 5} điểm đến khác` : ''}`
      : '';

    const contextMsg = {
      sender: 'bot',
      text: `📋 Tôi đã nhận được tiêu chí gợi ý của bạn:\n\n` +
        `• Mùa: **${seasonLabel || 'Chưa chọn'}**\n` +
        `• Phong cách: **${categoryLabel || 'Chưa chọn'}**\n` +
        `• Ngân sách: **${budgetLabel || 'Chưa chọn'}**` +
        destList +
        `\n\n💬 Hãy hỏi tôi bất cứ điều gì về những điểm đến này nhé! Ví dụ: *"Điểm nào phù hợp cho gia đình?"* hoặc *"So sánh 2 điểm đến đầu tiên"*.`,
      recommendations: [],
      isContextMessage: true,
    };

    setSessions(prevSessions => {
      const updated = prevSessions.map(s => {
        if (s.session_id === activeSessionId) {
          const exists = s.messages.some(m => m.isContextMessage && m.text.includes(seasonLabel));
          if (exists) return s;
          return {
            ...s,
            messages: [...s.messages, contextMsg],
            updated_at: new Date().toISOString()
          };
        }
        return s;
      });

      if (isAuthenticated && user) {
        const activeSess = updated.find(s => s.session_id === activeSessionId);
        if (activeSess) {
          chatApi.saveSession(activeSessionId, user.username, activeSess.title, activeSess.messages)
            .catch(err => console.error("Failed to save session to DB:", err));
        }
      } else {
        saveGuestSessions(updated);
      }

      return updated;
    });
  }, [isOpen, criteria, recResults, activeSessionId, isAuthenticated, user]);

  // ── Build recommendation context payload for backend ──────────────────────
  const buildRecommendationContext = useCallback(() => {
    if (!criteria) return null;
    return {
      criteria: criteria,
      destinations: (recResults || []).slice(0, 6).map(d => ({
        name: d['Destination Name'],
        country: d['Country'],
        type: d['Type'],
        cost: d['Avg Cost (USD/day)'],
        season: d['Best Season'],
      })),
    };
  }, [criteria, recResults]);

  const handleSend = async (text) => {
    const userText = text || inputValue;
    if (!userText.trim()) return;
    setInputValue('');

    const newMsgs = [...messages, { sender: 'user', text: userText }];
    updateActiveSessionMessages(newMsgs);
    setLoading(true);

    try {
      const history = newMsgs.map(m => ({
        role: m.sender === 'user' ? 'user' : 'model',
        parts: m.text
      }));
      const recContext = buildRecommendationContext();
      const response = await chatApi.sendMessage(userText, history, recContext, activeSessionId);

      if (response.data.success) {
        const botMsg = {
          sender: 'bot',
          text: response.data.response,
          recommendations: response.data.recommendations || []
        };
        updateActiveSessionMessages([...newMsgs, botMsg]);
      } else {
        const errorMsg = {
          sender: 'bot',
          text: '😕 Xin lỗi, tôi gặp sự cố kết nối. Vui lòng thử lại sau.',
          recommendations: []
        };
        updateActiveSessionMessages([...newMsgs, errorMsg]);
      }
    } catch (err) {
      const busyMsg = {
        sender: 'bot',
        text: '⚠️ Máy chủ đang bận. Bạn vui lòng thử lại nhé!',
        recommendations: []
      };
      updateActiveSessionMessages([...newMsgs, busyMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    handleSend();
  };

  const handleClearHistory = () => {
    updateActiveSessionMessages([DEFAULT_MESSAGE]);
    lastContextRef.current = null;
  };

  const handleNewChat = async () => {
    const newId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7);
    const newSess = {
      session_id: newId,
      title: 'Cuộc trò chuyện mới',
      messages: [DEFAULT_MESSAGE],
      updated_at: new Date().toISOString()
    };

    const updatedSessions = [newSess, ...sessions];
    setSessions(updatedSessions);
    setActiveSessionId(newId);
    localStorage.setItem(ACTIVE_SESSION_ID_KEY, newId);
    setShowHistory(false);

    if (isAuthenticated && user) {
      try {
        await chatApi.saveSession(newId, user.username, newSess.title, newSess.messages);
      } catch (err) {
        console.error("Failed to save new session to DB:", err);
      }
    } else {
      saveGuestSessions(updatedSessions);
    }
  };

  const handleDeleteSession = async (sessId, e) => {
    e.stopPropagation();

    const updatedSessions = sessions.filter(s => s.session_id !== sessId);
    let nextActiveId = activeSessionId;

    if (sessId === activeSessionId) {
      if (updatedSessions.length > 0) {
        nextActiveId = updatedSessions[0].session_id;
      } else {
        const newId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7);
        const newSess = {
          session_id: newId,
          title: 'Cuộc trò chuyện mới',
          messages: [DEFAULT_MESSAGE],
          updated_at: new Date().toISOString()
        };
        updatedSessions.push(newSess);
        nextActiveId = newId;

        if (isAuthenticated && user) {
          try {
            await chatApi.saveSession(newId, user.username, newSess.title, newSess.messages);
          } catch (err) {
            console.error("Failed to save new session to DB:", err);
          }
        }
      }
    }

    setSessions(updatedSessions);
    setActiveSessionId(nextActiveId);
    localStorage.setItem(ACTIVE_SESSION_ID_KEY, nextActiveId);

    if (isAuthenticated && user) {
      try {
        await chatApi.deleteSession(sessId);
      } catch (err) {
        console.error("Failed to delete session from server:", err);
      }
    } else {
      saveGuestSessions(updatedSessions);
    }
  };

  const renderText = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) =>
      part.startsWith('**') && part.endsWith('**')
        ? <strong key={i} className="font-bold text-primary">{part.slice(2, -2)}</strong>
        : part
    );
  };

  return (
    <div className="fixed bottom-8 right-8 z-50 flex flex-col items-end gap-4 text-left">
      
      {/* Chat Window */}
      {isOpen && (
        <div 
          className="relative w-[360px] sm:w-[440px] bg-white/90 backdrop-blur-2xl rounded-2xl shadow-2xl glass flex flex-col mb-4 overflow-hidden border border-white/30"
          style={{ height: '580px' }}
        >
          {/* History Panel Overlay */}
          {showHistory && (
            <div className="history-panel-active absolute inset-0 bg-white/95 backdrop-blur-xl z-20 flex flex-col">
              {/* History Header */}
              <div className="p-5 bg-primary/10 rounded-t-2xl border-b border-primary/10 flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <button 
                    className="material-symbols-outlined text-primary p-1 hover:bg-primary-container/20 rounded-full flex items-center justify-center transition-colors text-lg"
                    onClick={() => setShowHistory(false)}
                  >
                    arrow_back
                  </button>
                  <h4 className="font-display-lg text-sm font-bold text-primary">Lịch sử trò chuyện</h4>
                </div>
                <button
                  className="flex items-center gap-1 bg-primary text-white text-[10px] font-bold px-3 py-1.5 rounded-full hover:scale-105 active:scale-95 transition-all shadow-sm"
                  onClick={handleNewChat}
                >
                  <span className="material-symbols-outlined text-xs">add</span>
                  Mới
                </button>
              </div>

              {/* Sessions List */}
              <div className="flex-1 overflow-y-auto p-4 space-y-2">
                {sessions.map((sess) => {
                  const isActive = sess.session_id === activeSessionId;
                  const dateStr = new Date(sess.updated_at).toLocaleDateString('vi-VN', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  });
                  return (
                    <div
                      key={sess.session_id}
                      className={`group p-3 rounded-xl border transition-all flex justify-between items-center cursor-pointer ${
                        isActive
                          ? 'bg-primary-container/10 border-primary/30 shadow-sm'
                          : 'bg-white/50 border-pink-100/30 hover:border-primary/20 hover:bg-secondary-container/10'
                      }`}
                      onClick={() => {
                        setActiveSessionId(sess.session_id);
                        localStorage.setItem(ACTIVE_SESSION_ID_KEY, sess.session_id);
                        setShowHistory(false);
                      }}
                    >
                      <div className="min-w-0 flex-1 pr-2">
                        <h5 className={`font-semibold text-xs truncate ${isActive ? 'text-primary' : 'text-on-surface'}`}>
                          {sess.title || 'Cuộc trò chuyện mới'}
                        </h5>
                        <p className="text-[9px] text-text-muted mt-1 flex items-center gap-1 font-medium">
                          <span className="material-symbols-outlined text-[10px]">schedule</span>
                          {dateStr}
                        </p>
                      </div>
                      
                      <button
                        className="material-symbols-outlined text-on-surface-variant hover:text-red-500 p-1 rounded-full hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-all text-xs flex items-center justify-center shrink-0"
                        onClick={(e) => handleDeleteSession(sess.session_id, e)}
                        title="Xóa cuộc trò chuyện"
                      >
                        delete
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Header */}
          <div className="p-5 bg-primary/10 rounded-t-2xl border-b border-primary/10 flex justify-between items-center">
            <div className="min-w-0 flex-1 mr-2">
              <h4 className="font-display-lg text-sm font-bold text-primary truncate">
                {activeSessionObj?.title || 'Trợ lý du lịch AI'}
              </h4>
              <p className="text-[9px] text-on-surface-variant font-label-caps uppercase tracking-wider mt-0.5">Trợ lý du lịch AI</p>
            </div>
            <div className="flex items-center gap-1 shrink-0">
              {/* History list button */}
              <button
                className="material-symbols-outlined text-on-surface-variant p-1 hover:bg-primary-container/20 hover:text-primary rounded-full flex items-center justify-center transition-colors text-sm"
                onClick={() => setShowHistory(true)}
                title="Lịch sử trò chuyện"
              >
                history
              </button>
              {/* Clear history button */}
              <button
                className="material-symbols-outlined text-on-surface-variant p-1 hover:bg-red-100 hover:text-red-500 rounded-full flex items-center justify-center transition-colors text-sm"
                onClick={handleClearHistory}
                title="Xóa lịch sử tin nhắn"
              >
                delete_sweep
              </button>
              <button 
                className="material-symbols-outlined text-primary p-1 hover:bg-primary-container/20 rounded-full flex items-center justify-center transition-colors text-lg"
                onClick={() => setIsOpen(false)}
              >
                close
              </button>
            </div>
          </div>

          {/* Messages log */}
          <div className="flex-1 p-5 overflow-y-auto space-y-4">
            {messages.map((msg, idx) => (
              <div 
                key={idx} 
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div 
                  className={`p-3.5 rounded-2xl text-xs leading-relaxed max-w-[85%] ${
                    msg.sender === 'user'
                      ? 'bg-primary-container text-white rounded-tr-none shadow-sm'
                      : msg.isContextMessage
                        ? 'bg-amber-50/80 text-on-surface rounded-tl-none border border-amber-200/50'
                        : 'bg-secondary-container/30 text-on-surface rounded-tl-none border border-pink-100/30'
                  }`}
                >
                  <p className="whitespace-pre-line">{renderText(msg.text)}</p>

                  {/* Embedded mini destination cards */}
                  {msg.recommendations && msg.recommendations.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-pink-100/30 space-y-2">
                      <p className="text-[10px] font-bold text-primary uppercase tracking-wider mb-2">✨ Đề xuất điểm đến:</p>
                      <div className="flex flex-col gap-2 max-h-48 overflow-y-auto pr-1">
                        {msg.recommendations.map((dest, dIdx) => (
                          <div 
                            key={dIdx}
                            className="bg-white/80 p-2.5 rounded-xl border border-pink-100 hover:border-primary transition-all flex gap-3 cursor-pointer items-center"
                            onClick={() => {
                              setIsOpen(false);
                              navigate(`/destinations/${encodeURIComponent(dest['Destination Name'])}`);
                            }}
                          >
                            <img 
                              className="w-12 h-12 object-cover rounded-lg shrink-0"
                              src={dest.image || getDestinationImage(dest['Destination Name'], dest.Type, dest.Country)}
                              alt=""
                              onError={e => { e.target.src = getFallbackImage(dest['Destination Name'], dest.Type); }}
                            />
                            <div className="min-w-0 flex-1">
                              <h5 className="font-bold text-xs text-primary truncate leading-tight">{dest['Destination Name']}</h5>
                              <p className="text-[9px] text-secondary font-medium truncate mt-0.5">📍 {translateCountry(dest.Country)}</p>
                              <div className="flex gap-2 mt-1">
                                <span className="text-[8px] text-secondary font-bold uppercase">{translateCategory(dest.Type)}</span>
                                <span className="text-[8px] text-primary font-bold">${dest['Avg Cost (USD/day)']}/ngày</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Typing Indicator */}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-secondary-container/20 p-3 rounded-2xl rounded-tl-none border border-pink-100/30 flex gap-1 items-center">
                  <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick prompt chips */}
          {messages.length <= 1 && !loading && (
            <div className="px-5 pb-3 flex flex-wrap gap-1.5">
              {QUICK_PROMPTS.map(prompt => (
                <button
                  key={prompt}
                  className="bg-secondary-container/20 hover:bg-secondary-container/50 border border-pink-100/50 text-[10px] text-primary rounded-full px-3 py-1 font-semibold transition-all active:scale-95"
                  onClick={() => handleSend(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>
          )}

          {/* Context indicator bar */}
          {criteria && (
            <div className="px-4 py-1.5 bg-amber-50/60 border-t border-amber-200/30 flex items-center gap-1.5 text-[9px] text-amber-700">
              <span className="material-symbols-outlined text-xs">auto_awesome</span>
              <span className="font-semibold">Ngữ cảnh:</span>
              {criteria.season && <span className="bg-amber-100/80 rounded-full px-1.5 py-0.5">{SEASON_LABELS[criteria.season]}</span>}
              {criteria.category && <span className="bg-amber-100/80 rounded-full px-1.5 py-0.5">{CATEGORY_LABELS[criteria.category]}</span>}
              {criteria.budget && <span className="bg-amber-100/80 rounded-full px-1.5 py-0.5">{BUDGET_LABELS[criteria.budget]}</span>}
            </div>
          )}

          {/* Input Form */}
          <form className="p-3 border-t border-primary/10 flex gap-2 bg-white/40" onSubmit={handleFormSubmit}>
            <input 
              type="text"
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              placeholder="Nhắn tin với Trợ lý du lịch AI..."
              className="flex-1 bg-white/70 border border-pink-200 focus:border-primary-container focus:ring-1 focus:ring-pink-300 rounded-full px-4 py-2 text-xs focus:outline-none text-on-surface"
              disabled={loading}
            />
            <button 
              type="submit" 
              className="w-8 h-8 rounded-full bg-primary-container text-white flex items-center justify-center hover:scale-105 active:scale-95 transition-transform disabled:opacity-50"
              disabled={loading || !inputValue.trim()}
            >
              <span className="material-symbols-outlined text-sm">send</span>
            </button>
          </form>
        </div>
      )}

      {/* Floating Action Button (FAB) */}
      <button 
        className="w-16 h-16 bg-primary text-white rounded-full shadow-[0_20px_40px_rgba(164,48,115,0.3)] flex items-center justify-center hover:scale-110 active:scale-95 transition-all group border border-white/20"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle AI Concierge Chat"
      >
        <span 
          className="material-symbols-outlined text-3xl group-hover:rotate-12 transition-transform" 
          style={{ fontVariationSettings: "'FILL' 1" }}
        >
          auto_awesome
        </span>
      </button>

    </div>
  );
}

export default ChatbotWidget;
