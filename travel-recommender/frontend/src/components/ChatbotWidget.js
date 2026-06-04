import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { chatApi } from '../services/api';
import { getDestinationImage } from '../services/imageService';
import './ChatbotWidget.css';

function ChatbotWidget() {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const [messages, setMessages] = useState([{
    sender: 'bot',
    text: 'Xin chào! 👋 Tôi là **Trợ lý du lịch AI**, người đồng hành cùng bạn.\n\nTôi giúp bạn tìm kiếm và đối soát các điểm đến du lịch quốc tế dựa trên thuật toán khai phá dữ liệu.\n\nHãy nhắn cho tôi nhu cầu du lịch của bạn nhé (ví dụ: *"Gợi ý điểm du lịch biển giá rẻ vào mùa hè"*).',
    recommendations: []
  }]);

  const QUICK_PROMPTS = [
    '🌸 Gợi ý điểm đến mùa xuân',
    '🏖️ Du lịch biển tiết kiệm',
    '🏔️ Thám hiểm núi mạo hiểm',
    '🏛️ Khám phá di sản văn hóa',
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isOpen]);

  const handleSend = async (text) => {
    const userText = text || inputValue;
    if (!userText.trim()) return;
    setInputValue('');

    setMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setLoading(true);

    try {
      const history = messages.map(m => ({
        role: m.sender === 'user' ? 'user' : 'model',
        parts: m.text
      }));
      const response = await chatApi.sendMessage(userText, history);

      if (response.data.success) {
        setMessages(prev => [...prev, {
          sender: 'bot',
          text: response.data.response,
          recommendations: response.data.recommendations || []
        }]);
      } else {
        setMessages(prev => [...prev, {
          sender: 'bot',
          text: '😕 Xin lỗi, tôi gặp sự cố kết nối. Vui lòng thử lại sau.',
          recommendations: []
        }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: '⚠️ Máy chủ đang bận. Bạn vui lòng thử lại nhé!',
        recommendations: []
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    handleSend();
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
          className="w-85 sm:w-96 bg-white/90 backdrop-blur-2xl rounded-2xl shadow-2xl glass flex flex-col mb-4 overflow-hidden border border-white/30"
          style={{ height: '500px' }}
        >
          {/* Header */}
          <div className="p-5 bg-primary/10 rounded-t-2xl border-b border-primary/10 flex justify-between items-center">
            <div>
              <h4 className="font-display-lg text-sm font-bold text-primary">Trợ lý du lịch AI</h4>
              <p className="text-[9px] text-on-surface-variant font-label-caps uppercase tracking-wider mt-0.5">Trợ lý du lịch AI</p>
            </div>
            <button 
              className="material-symbols-outlined text-primary p-1 hover:bg-primary-container/20 rounded-full flex items-center justify-center transition-colors text-lg"
              onClick={() => setIsOpen(false)}
            >
              close
            </button>
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
                              src={dest.image || getDestinationImage(dest['Destination Name'], dest.Type)}
                              alt=""
                              onError={e => { e.target.src = 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=100'; }}
                            />
                            <div className="min-w-0 flex-1">
                              <h5 className="font-bold text-xs text-primary truncate leading-tight">{dest['Destination Name']}</h5>
                              <p className="text-[9px] text-secondary font-medium truncate mt-0.5">📍 {dest.Country}</p>
                              <div className="flex gap-2 mt-1">
                                <span className="text-[8px] text-secondary font-bold uppercase">{dest.Type}</span>
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

          {/* Quick prompt chips (Visible initially or when log is clean) */}
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
