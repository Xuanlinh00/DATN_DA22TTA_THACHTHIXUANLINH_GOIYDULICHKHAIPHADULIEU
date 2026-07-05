import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { chatApi } from '../services/api';
import { getDatasetImage, getDestinationImage, getFallbackImage, resolveCategoryKey } from '../services/imageService';
import { useRecommendation } from '../contexts/RecommendationContext';
import { useAuth } from '../contexts/AuthContext';
import { translateCountry, translateCategory, stripDisplayName } from '../utils/translator';
import './ChatbotWidget.css';

// ── LocalStorage keys ────────────────────────────────────────────────────────
const GUEST_SESSIONS_KEY = 'Nâu_guest_sessions';
const ACTIVE_SESSION_ID_KEY = 'Nâu_active_session_id';

const CHATBOT_SIZE_KEY = 'Nau_chatbot_size';
const CHATBOT_SIZE_OPTIONS = {
  compact: { label: 'S', title: 'Kích cỡ nhỏ', width: 360, height: 500 },
  default: { label: 'M', title: 'Kích cỡ vừa', width: 440, height: 580 },
  large: { label: 'L', title: 'Kích cỡ lớn', width: 560, height: 700 },
};
const DEFAULT_CHATBOT_SIZE = { width: 440, height: 580 };
const MIN_CHATBOT_SIZE = { width: 340, height: 440 };
const MAX_CHATBOT_SIZE = { width: 720, height: 820 };

function clampNumber(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function getViewportMaxSize() {
  if (typeof window === 'undefined') return MAX_CHATBOT_SIZE;
  return {
    width: Math.min(MAX_CHATBOT_SIZE.width, Math.max(MIN_CHATBOT_SIZE.width, window.innerWidth - 32)),
    height: Math.min(MAX_CHATBOT_SIZE.height, Math.max(MIN_CHATBOT_SIZE.height, window.innerHeight - 120)),
  };
}

function normalizeChatbotSize(size) {
  const max = getViewportMaxSize();
  return {
    width: clampNumber(Number(size?.width) || DEFAULT_CHATBOT_SIZE.width, MIN_CHATBOT_SIZE.width, max.width),
    height: clampNumber(Number(size?.height) || DEFAULT_CHATBOT_SIZE.height, MIN_CHATBOT_SIZE.height, max.height),
  };
}

function loadChatbotSize() {
  try {
    const saved = localStorage.getItem(CHATBOT_SIZE_KEY);
    if (!saved) return DEFAULT_CHATBOT_SIZE;
    if (CHATBOT_SIZE_OPTIONS[saved]) return CHATBOT_SIZE_OPTIONS[saved];
    return normalizeChatbotSize(JSON.parse(saved));
  } catch {
    return DEFAULT_CHATBOT_SIZE;
  }
}

const DEFAULT_MESSAGE = {
  sender: 'bot',
  text: 'Xin chào! Tôi là **Trợ lý Gợi ý Du lịch AI** — hệ thống được xây dựng cho đồ án Khai phá Dữ liệu.\n\nTôi có thể giúp bạn tìm ra điểm đến hoàn hảo dựa trên sở thích cá nhân bằng cách phân tích dữ liệu:\n• 🗺 **Gợi ý điểm đến** theo mùa (Xuân, Hè...), ngân sách và loại hình (Biển, Núi...)\n• ⚖️ **So sánh** các địa điểm du lịch khác nhau\n• 📋 Lên **lịch trình** chi tiết cho điểm đến bạn chọn\n• 💰 Tư vấn **chi phí & ngân sách** phù hợp\n• 🛂 Hỗ trợ thông tin **visa, thời tiết, ẩm thực** tại nơi bạn muốn đến\n\nHãy cho tôi biết bạn muốn một chuyến đi như thế nào nhé? (Ví dụ: *"Gợi ý cho tôi chỗ đi biển mùa hè giá rẻ"* 😊)',
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
const SEASON_LABELS = { Spring: 'Xuân', Summer: 'Hè', Autumn: 'Thu', Winter: 'Đông' };
const CATEGORY_LABELS = {
  Beach: 'Biển & Đảo', Mountain: 'Núi & Rừng', Cultural: 'Văn Hoá & Lịch Sử',
  Historical: 'Lịch sử', City: 'Thành Phố', Adventure: 'Phiêu Lưu',
  Wellness: 'Nghỉ Dưỡng', Nature: 'Thiên Nhiên', 'Theme Park': 'Vui Chơi',
};
const BUDGET_LABELS = { Budget: 'Tiết Kiệm', Moderate: 'Bình Dân', Expensive: 'Cao Cấp', Luxury: 'Sang Trọng' };

function buildDestinationContextItem(destination, index) {
  return {
    rank: index + 1,
    name: destination['Destination Name'],
    country: destination['Country'],
    type: destination['Type'],
    cost: destination['Avg Cost (USD/day)'],
    rating: destination['Avg Rating'] ?? destination['Rating'],
    season: destination['Best Season'],
    description: destination['Description'],
    continent: destination['Continent'],
    cluster: destination['Cluster'],
    recommendationScore: destination['recommendation_score'] ?? destination['match_score'] ?? destination['score'],
  };
}

function ChatbotWidget() {
  const navigate = useNavigate();
  const location = useLocation();
  const { criteria, results: recResults, matchedRules } = useRecommendation();
  const { user, isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [chatSize, setChatSize] = useState(loadChatbotSize);
  const messagesEndRef = useRef(null);

  // Sessions and Active Session states
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState('');

  // Track whether we already injected a context message for the current criteria
  const lastContextRef = useRef(null);

  // Memoize currently viewed destination from URL path
  const viewingDest = React.useMemo(() => {
    if (location.pathname.startsWith('/destinations/')) {
      return decodeURIComponent(location.pathname.replace('/destinations/', ''));
    }
    return null;
  }, [location.pathname]);

  const BASE_QUICK_PROMPTS = [
    '🗺 Gợi ý đi biển mùa hè, chi phí tiết kiệm',
    '🏔 Tôi muốn đi du lịch núi, ngân sách bình dân',
    '🏛 Gợi ý điểm đến lịch sử ở Châu Á',
    '🏖 Tư vấn chuyến đi nghỉ dưỡng cho gia đình',
    '🌸 Gợi ý địa điểm đi chơi vào mùa xuân',
    '❄️ Tôi muốn tìm nơi có tuyết vào mùa đông',
    '🎒 Du lịch khám phá thiên nhiên cho người đi một mình',
    '⚖️ So sánh du lịch Thái Lan và Singapore',
    '📋 Lên lịch trình khám phá Nhật Bản 5 ngày',
    '💰 Du lịch Châu Âu cần ngân sách khoảng bao nhiêu?'
  ];

  // ── Tạo quick prompts cá nhân hóa dựa trên sở thích đã lưu của người dùng ──
  const QUICK_PROMPTS = React.useMemo(() => {
    if (viewingDest) {
      return [
        `🌤 Thời tiết tại ${viewingDest}`,
        `🍜 Đặc sản ẩm thực tại ${viewingDest}`,
        `🚌 Cách di chuyển đến ${viewingDest}`,
        `📋 Lịch trình gợi ý đi ${viewingDest}`,
        `💰 Chi phí du lịch tại ${viewingDest}`,
        ...BASE_QUICK_PROMPTS
      ].slice(0, 10);
    }

    if (!isAuthenticated || !user?.preferences) return BASE_QUICK_PROMPTS;
    const prefs = user.preferences;
    const personalized = [];

    if (prefs.season && prefs.category) {
      const s = SEASON_LABELS[prefs.season] || prefs.season;
      const c = CATEGORY_LABELS[prefs.category] || prefs.category;
      personalized.push(`✨ Gợi ý ${c.toLowerCase()} mùa ${s.toLowerCase()} cho tôi`);
    }
    if (prefs.category && prefs.budget) {
      const b = BUDGET_LABELS[prefs.budget] || prefs.budget;
      const c = CATEGORY_LABELS[prefs.category] || prefs.category;
      personalized.push(`💡 ${c} phù hợp ngân sách ${b.toLowerCase()}`);
    }
    if (prefs.season && !prefs.category) {
      const s = SEASON_LABELS[prefs.season] || prefs.season;
      personalized.push(`🌍 Đâu là điểm đến tốt nhất mùa ${s.toLowerCase()} cho tôi?`);
    }
    // Đặt gợi ý cá nhân hóa lên đầu, giữ tổng <= 10
    return [...personalized, ...BASE_QUICK_PROMPTS].slice(0, 10);
  }, [viewingDest, isAuthenticated, user?.preferences]);

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
  const currentChatSize = normalizeChatbotSize(chatSize);
  const handleResizeStart = (event) => {
    event.preventDefault();
    event.stopPropagation();

    const startX = event.clientX;
    const startY = event.clientY;
    const startSize = normalizeChatbotSize(chatSize);

    const handleMouseMove = (moveEvent) => {
      const max = getViewportMaxSize();
      setChatSize({
        width: clampNumber(startSize.width + (startX - moveEvent.clientX), MIN_CHATBOT_SIZE.width, max.width),
        height: clampNumber(startSize.height + (moveEvent.clientY - startY), MIN_CHATBOT_SIZE.height, max.height),
      });
    };

    const handleMouseUp = (upEvent) => {
      const max = getViewportMaxSize();
      const finalSize = {
        width: clampNumber(startSize.width + (startX - upEvent.clientX), MIN_CHATBOT_SIZE.width, max.width),
        height: clampNumber(startSize.height + (upEvent.clientY - startY), MIN_CHATBOT_SIZE.height, max.height),
      };
      setChatSize(finalSize);
      localStorage.setItem(CHATBOT_SIZE_KEY, JSON.stringify(finalSize));
      document.body.classList.remove('chatbot-resizing');
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };

    document.body.classList.add('chatbot-resizing');
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
  };

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
    const resultNames = (recResults || []).map(d => d['Destination Name']).filter(Boolean);
    const fingerprint = JSON.stringify({ criteria, resultNames });
    if (lastContextRef.current === fingerprint) return;
    lastContextRef.current = fingerprint;

    const seasonLabel = SEASON_LABELS[criteria.season] || criteria.season || '';
    const categoryLabel = CATEGORY_LABELS[criteria.category] || criteria.category || '';
    const budgetLabel = BUDGET_LABELS[criteria.budget] || criteria.budget || '';

    const destNames = resultNames.slice(0, 8);
    const destList = destNames.length > 0
      ? `\nCác điểm đến đã gợi ý: **${destNames.join('**, **')}**${recResults.length > 8 ? ` và ${recResults.length - 8} điểm đến khác` : ''}`
      : '';

    const contextMsg = {
      sender: 'bot',
      text: `Tôi đã nhận được tiêu chí gợi ý của bạn:\n\n` +
        `• Mùa: **${seasonLabel || 'Chưa chọn'}**\n` +
        `• Phong cách: **${categoryLabel || 'Chưa chọn'}**\n` +
        `• Ngân sách: **${budgetLabel || 'Chưa chọn'}**` +
        destList +
        `\n\nHãy hỏi tôi bất cứ điều gì về những điểm đến này nhé! Ví dụ: *"Điểm nào phù hợp cho gia đình?"* hoặc *"So sánh 2 điểm đến đầu tiên"*.`,
      recommendations: [],
      isContextMessage: true,
      contextFingerprint: fingerprint,
    };

    setSessions(prevSessions => {
      const updated = prevSessions.map(s => {
        if (s.session_id === activeSessionId) {
          const exists = s.messages.some(m => m.isContextMessage && m.contextFingerprint === fingerprint);
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

  // ── Inject viewing destination context message ─────────────────────────────
  useEffect(() => {
    if (!isOpen || !viewingDest || !activeSessionId) return;

    // Build a fingerprint so we only inject once per unique destination
    const fingerprint = `view_dest_${viewingDest}`;
    if (lastContextRef.current === fingerprint) return;
    lastContextRef.current = fingerprint;

    const contextMsg = {
      sender: 'bot',
      text: `Tôi thấy bạn đang tìm hiểu về **${viewingDest}**.\n\n` +
        `Bạn có muốn biết thêm thông tin về nơi này không? Tôi có thể tư vấn cho bạn:\n` +
        `• 🌦 **Thời tiết & Khí hậu** phù hợp nhất\n` +
        `• 🍜 **Đặc sản ẩm thực** phải thử\n` +
        `• 🚌 **Cách di chuyển & phương tiện** tối ưu\n` +
        `• 💰 **Chi phí & ngân sách** cần chuẩn bị\n` +
        `• 📋 **Lịch trình** tham quan chi tiết\n\n` +
        `Hãy nhấp vào các gợi ý nhanh bên dưới hoặc nhập câu hỏi của bạn nhé!`,
      recommendations: [],
      isContextMessage: true,
    };

    setSessions(prevSessions => {
      const updated = prevSessions.map(s => {
        if (s.session_id === activeSessionId) {
          // Check if this context message already exists in this session to prevent duplicates
          const exists = s.messages.some(m => m.isContextMessage && m.text.includes(viewingDest));
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
  }, [isOpen, viewingDest, activeSessionId, isAuthenticated, user]);

  // ── Build recommendation context payload for backend ──────────────────────
  const buildRecommendationContext = useCallback(() => {
    const context = {};
    if (criteria) {
      context.criteria = criteria;
      context.destinations = (recResults || []).map(buildDestinationContextItem);
      context.destination_count = context.destinations.length;
      context.matched_rules = matchedRules || [];
    }
    if (viewingDest) {
      context.currentViewingDestination = viewingDest;
    }
    // Truyền thông tin người dùng để backend cá nhân hóa câu trả lời
    if (isAuthenticated && user) {
      context.user_profile = {
        name: user.fullName || user.username,
        username: user.username,
        preferences: user.preferences || null,
      };
    }
    return Object.keys(context).length > 0 ? context : null;
  }, [criteria, recResults, matchedRules, viewingDest, isAuthenticated, user]);

  const handleSend = async (text) => {
    const userText = text || inputValue;
    if (!userText.trim()) return;
    setInputValue('');

    const newMsgs = [...messages, { sender: 'user', text: userText }];
    updateActiveSessionMessages(newMsgs);
    setLoading(true);

    try {
      // Lọc bỏ isContextMessage (tin nhắn ngữ cảnh tự động inject) trước khi gửi lên backend
      // để tránh làm nhiễu loạn lịch sử hội thoại của Gemini
      const history = newMsgs
        .filter(m => !m.isContextMessage)
        .map(m => ({
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
          text: `Xin lỗi, có sự cố xảy ra: ${response.data.detail || 'Vui lòng thử lại sau.'}`,
          recommendations: []
        };
        updateActiveSessionMessages([...newMsgs, errorMsg]);
      }
    } catch (err) {
      // Hiển thị chi tiết lỗi từ server nếu có (err.response.data.detail)
      const serverDetail = err.response?.data?.detail;
      const busyMsg = {
        sender: 'bot',
        text: serverDetail
          ? `Có lỗi từ máy chủ: ${serverDetail}`
          : 'Máy chủ đang bận hoặc mất kết nối. Bạn vui lòng thử lại nhé!',
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
    // Reset lastContextRef TRƯỚC khi update messages để tránh race condition
    // với useEffect inject context (nếu set sau, effect có thể đã chạy với ref cũ)
    lastContextRef.current = null;
    updateActiveSessionMessages([DEFAULT_MESSAGE]);
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
    // Tách theo **bold** và *italic*, render thành các thẻ HTML tương ứng
    const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**'))
        return <strong key={i} className="font-bold text-primary">{part.slice(2, -2)}</strong>;
      if (part.startsWith('*') && part.endsWith('*') && part.length > 2)
        return <em key={i} className="italic text-on-surface/80">{part.slice(1, -1)}</em>;
      return part;
    });
  };

  return (
    <div className="fixed bottom-8 right-8 z-50 flex flex-col items-end gap-4 text-left">
      
      {/* Chat Window */}
      {isOpen && (
        <div 
          className="chatbot-window relative bg-white/90 backdrop-blur-2xl rounded-2xl shadow-2xl glass flex flex-col mb-4 overflow-hidden border border-white/30"
          style={{ width: currentChatSize.width, height: currentChatSize.height, maxHeight: 'calc(100vh - 120px)' }}
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

          {/* Header – cá nhân hóa tên khi đã đăng nhập */}
          <div className="p-5 bg-primary/10 rounded-t-2xl border-b border-primary/10 flex justify-between items-center">
            <div className="min-w-0 flex-1 mr-2 flex items-center gap-2">
              {/* Avatar chữ cái đầu khi đăng nhập */}
              {isAuthenticated && user ? (
                <div className="w-7 h-7 rounded-full bg-primary text-white text-[10px] font-bold flex items-center justify-center shrink-0 shadow-sm">
                  {(user.fullName || user.username || '?').charAt(0).toUpperCase()}
                </div>
              ) : (
                <span className="material-symbols-outlined text-primary text-lg shrink-0" style={{ fontVariationSettings: "'FILL' 1" }}>auto_awesome</span>
              )}
              <div className="min-w-0">
                <h4 className="text-xs font-bold text-primary truncate leading-tight">
                  {activeSessionObj?.title || 'NÂU AI'}
                </h4>
                <p className="text-[9px] text-on-surface-variant font-label-caps uppercase tracking-wider mt-0.5 flex items-center gap-1">
                  {isAuthenticated && user
                    ? <><span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block"/>{user.fullName || user.username}</>  
                    : 'NÂU AI · Khách'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1 shrink-0">
              {/* New chat button */}
              <button
                className="material-symbols-outlined text-on-surface-variant p-1 hover:bg-primary-container/20 hover:text-primary rounded-full flex items-center justify-center transition-colors text-sm"
                onClick={handleNewChat}
                title="Tạo cuộc trò chuyện mới"
              >
                add_comment
              </button>
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
                      <p className="text-[10px] font-bold text-primary uppercase tracking-wider mb-2">Đề xuất điểm đến:</p>
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
                              src={getDatasetImage(dest) || getDestinationImage(dest['Destination Name'], dest.Type, dest.Country)}
                              alt=""
                              onError={e => { e.target.src = getFallbackImage(dest['Destination Name'], dest.Type); }}
                            />
                            <div className="min-w-0 flex-1">
                              <h5 className="font-bold text-xs text-primary truncate leading-tight">{stripDisplayName(dest['Destination Name'])}</h5>
                              <p className="text-[9px] text-secondary font-medium truncate mt-0.5">{translateCountry(dest.Country)}</p>
                              <div className="flex gap-2 mt-1">
                                <span className="text-[8px] text-secondary font-bold uppercase">{translateCategory(resolveCategoryKey(dest.Type, dest['Destination Name']))}</span>
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
          {/* Hiển thị Quick Prompts khi chưa có tin nhắn thật nào (không đếm context messages tự động) */}
          {messages.filter(m => !m.isContextMessage).length <= 1 && !loading && (
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

          {/* Context / Personalization indicator bar */}
          {(criteria || (isAuthenticated && user?.preferences)) && (
            <div className="px-4 py-1.5 bg-amber-50/60 border-t border-amber-200/30 flex items-center gap-1.5 text-[9px] text-amber-700 flex-wrap">
              <span className="material-symbols-outlined text-xs">auto_awesome</span>
              {/* Hiển thị ngữ cảnh wizard trước */}
              {criteria ? (
                <>
                  <span className="font-semibold">Gợi ý:</span>
                  {criteria.season && <span className="bg-amber-100/80 rounded-full px-1.5 py-0.5">{SEASON_LABELS[criteria.season]}</span>}
                  {criteria.category && <span className="bg-amber-100/80 rounded-full px-1.5 py-0.5">{CATEGORY_LABELS[criteria.category]}</span>}
                  {criteria.budget && <span className="bg-amber-100/80 rounded-full px-1.5 py-0.5">{BUDGET_LABELS[criteria.budget]}</span>}
                </>
              ) : (
                /* Hiển thị sở thích đã lưu khi chưa có wizard context */
                isAuthenticated && user?.preferences && (
                  <>
                    <span className="font-semibold">Sở thích của bạn:</span>
                    {user.preferences.season && <span className="bg-amber-100/80 rounded-full px-1.5 py-0.5">{SEASON_LABELS[user.preferences.season]}</span>}
                    {user.preferences.category && <span className="bg-amber-100/80 rounded-full px-1.5 py-0.5">{CATEGORY_LABELS[user.preferences.category]}</span>}
                    {user.preferences.budget && <span className="bg-amber-100/80 rounded-full px-1.5 py-0.5">{BUDGET_LABELS[user.preferences.budget]}</span>}
                  </>
                )
              )}
            </div>
          )}

          {/* Input Form – placeholder cá nhân hóa theo tên */}
          <form className="p-3 border-t border-primary/10 flex gap-2 bg-white/40" onSubmit={handleFormSubmit}>
            <input 
              type="text"
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              placeholder={
                isAuthenticated && user
                  ? `Hỏi tôi bất cứ điều gì, ${user.fullName?.split(' ').pop() || user.username}...`
                  : 'Nhắn tin với NÂU AI...'
              }
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
          <button
            type="button"
            className="chatbot-resize-handle"
            onMouseDown={handleResizeStart}
            title="Kéo để tùy chỉnh kích thước chatbot"
            aria-label="Kéo để tùy chỉnh kích thước chatbot"
          />
        </div>
      )}

      {/* Floating Action Button (FAB) – badge online khi đã đăng nhập */}
      <button 
        className="w-16 h-16 bg-primary text-white rounded-full shadow-[0_20px_40px_rgba(164,48,115,0.3)] flex items-center justify-center hover:scale-110 active:scale-95 transition-all group border border-white/20 relative"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle AI Concierge Chat"
      >
        <span 
          className="material-symbols-outlined text-3xl group-hover:rotate-12 transition-transform" 
          style={{ fontVariationSettings: "'FILL' 1" }}
        >
          auto_awesome
        </span>
        {/* Badge nhỏ hiển thị avatar chữ cái khi đã đăng nhập */}
        {isAuthenticated && user && !isOpen && (
          <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-green-400 border-2 border-white text-[8px] font-bold text-white flex items-center justify-center shadow">
            {(user.fullName || user.username || '?').charAt(0).toUpperCase()}
          </span>
        )}
      </button>

    </div>
  );
}

export default ChatbotWidget;
