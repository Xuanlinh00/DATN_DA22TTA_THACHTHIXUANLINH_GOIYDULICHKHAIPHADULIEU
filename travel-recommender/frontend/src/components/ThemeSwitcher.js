import React, { useState, useEffect, useRef } from 'react';
import './ThemeSwitcher.css';

// ── Theme presets ──────────────────────────────────────────────────────────────
const THEMES = [
  {
    id: 'pink',
    name: 'Hồng Ngọc',
    emoji: '🌸',
    colors: {
      '--color-bg':           '#fffbff',
      '--color-bg-2':         '#fbf2f7',
      '--color-border':       'rgba(194,68,130,0.08)',
      '--color-border-glow':  'rgba(194,68,130,0.2)',
      '--grad-primary':       'linear-gradient(135deg,#c24482 0%,#f4a4c6 100%)',
      '--grad-hero':          'linear-gradient(135deg,#fffbff 0%,#fbe4f2 100%)',
      '--text-accent':        '#c24482',
      '--accent-cyan':        '#c24482',
      '--accent-purple':      '#aa304f',
      '--glass-border':       'rgba(194,68,130,0.1)',
      '--shadow-glow':        '0 0 24px rgba(164,48,115,0.25)',
      // Tailwind CSS vars (used by tw classes like text-primary, bg-primary etc.)
      '--tw-primary':         '194 68 130',
      '--tw-secondary':       '84 66 73',
    },
    preview: ['#c24482', '#f4a4c6', '#fbe4f2'],
  },
  {
    id: 'ocean',
    name: 'Đại Dương',
    emoji: '🌊',
    colors: {
      '--color-bg':           '#f0f9ff',
      '--color-bg-2':         '#e0f2fe',
      '--color-border':       'rgba(2,132,199,0.08)',
      '--color-border-glow':  'rgba(2,132,199,0.2)',
      '--grad-primary':       'linear-gradient(135deg,#0284c7 0%,#38bdf8 100%)',
      '--grad-hero':          'linear-gradient(135deg,#f0f9ff 0%,#bae6fd 100%)',
      '--text-accent':        '#0284c7',
      '--accent-cyan':        '#0284c7',
      '--accent-purple':      '#0ea5e9',
      '--glass-border':       'rgba(2,132,199,0.12)',
      '--shadow-glow':        '0 0 24px rgba(2,132,199,0.25)',
      '--tw-primary':         '2 132 199',
      '--tw-secondary':       '14 165,233',
    },
    preview: ['#0284c7', '#38bdf8', '#bae6fd'],
  },
  {
    id: 'forest',
    name: 'Rừng Xanh',
    emoji: '🌿',
    colors: {
      '--color-bg':           '#f0fdf4',
      '--color-bg-2':         '#dcfce7',
      '--color-border':       'rgba(22,163,74,0.08)',
      '--color-border-glow':  'rgba(22,163,74,0.2)',
      '--grad-primary':       'linear-gradient(135deg,#16a34a 0%,#4ade80 100%)',
      '--grad-hero':          'linear-gradient(135deg,#f0fdf4 0%,#bbf7d0 100%)',
      '--text-accent':        '#16a34a',
      '--accent-cyan':        '#16a34a',
      '--accent-purple':      '#15803d',
      '--glass-border':       'rgba(22,163,74,0.1)',
      '--shadow-glow':        '0 0 24px rgba(22,163,74,0.25)',
      '--tw-primary':         '22 163 74',
      '--tw-secondary':       '21 128 61',
    },
    preview: ['#16a34a', '#4ade80', '#bbf7d0'],
  },
  {
    id: 'sunset',
    name: 'Hoàng Hôn',
    emoji: '🌅',
    colors: {
      '--color-bg':           '#fff7ed',
      '--color-bg-2':         '#ffedd5',
      '--color-border':       'rgba(234,88,12,0.08)',
      '--color-border-glow':  'rgba(234,88,12,0.2)',
      '--grad-primary':       'linear-gradient(135deg,#ea580c 0%,#fb923c 100%)',
      '--grad-hero':          'linear-gradient(135deg,#fff7ed 0%,#fed7aa 100%)',
      '--text-accent':        '#ea580c',
      '--accent-cyan':        '#ea580c',
      '--accent-purple':      '#c2410c',
      '--glass-border':       'rgba(234,88,12,0.1)',
      '--shadow-glow':        '0 0 24px rgba(234,88,12,0.25)',
      '--tw-primary':         '234 88 12',
      '--tw-secondary':       '194 65 12',
    },
    preview: ['#ea580c', '#fb923c', '#fed7aa'],
  },
  {
    id: 'lavender',
    name: 'Tím Oải Hương',
    emoji: '💜',
    colors: {
      '--color-bg':           '#faf5ff',
      '--color-bg-2':         '#f3e8ff',
      '--color-border':       'rgba(124,58,237,0.08)',
      '--color-border-glow':  'rgba(124,58,237,0.2)',
      '--grad-primary':       'linear-gradient(135deg,#7c3aed 0%,#c084fc 100%)',
      '--grad-hero':          'linear-gradient(135deg,#faf5ff 0%,#ede9fe 100%)',
      '--text-accent':        '#7c3aed',
      '--accent-cyan':        '#7c3aed',
      '--accent-purple':      '#6d28d9',
      '--glass-border':       'rgba(124,58,237,0.1)',
      '--shadow-glow':        '0 0 24px rgba(124,58,237,0.25)',
      '--tw-primary':         '124 58 237',
      '--tw-secondary':       '109 40 217',
    },
    preview: ['#7c3aed', '#c084fc', '#ede9fe'],
  },
  {
    id: 'midnight',
    name: 'Đêm Tối',
    emoji: '🌙',
    colors: {
      '--color-bg':           '#0f0f1a',
      '--color-bg-2':         '#1a1a2e',
      '--color-border':       'rgba(99,102,241,0.15)',
      '--color-border-glow':  'rgba(99,102,241,0.3)',
      '--grad-primary':       'linear-gradient(135deg,#6366f1 0%,#a78bfa 100%)',
      '--grad-hero':          'linear-gradient(135deg,#0f0f1a 0%,#1e1b4b 100%)',
      '--text-accent':        '#818cf8',
      '--accent-cyan':        '#6366f1',
      '--accent-purple':      '#a78bfa',
      '--glass-border':       'rgba(99,102,241,0.2)',
      '--shadow-glow':        '0 0 24px rgba(99,102,241,0.4)',
      '--tw-primary':         '99 102 241',
      '--tw-secondary':       '167 139 250',
      '--text-primary':       '#e2e8f0',
      '--text-secondary':     '#94a3b8',
      '--text-muted':         '#64748b',
      '--glass-bg':           'rgba(15,15,26,0.75)',
    },
    preview: ['#6366f1', '#a78bfa', '#1e1b4b'],
  },
];

const STORAGE_KEY = 'Nâu_theme';

// ── Apply theme to :root ──────────────────────────────────────────────────────
function applyTheme(theme) {
  const root = document.documentElement;

  // 1. Set data-theme attribute → triggers CSS variable overrides in index.css
  root.setAttribute('data-theme', theme.id);

  // 2. Also set CSS custom properties directly (belt + suspenders)
  Object.entries(theme.colors).forEach(([key, val]) => {
    root.style.setProperty(key, val);
  });

  // Reset text/glass colors that dark theme sets when switching back to light
  if (theme.id !== 'midnight') {
    root.style.setProperty('--text-primary',   '#1f1a1e');
    root.style.setProperty('--text-secondary',  '#544249');
    root.style.setProperty('--text-muted',      '#87717a');
    root.style.setProperty('--glass-bg',        'rgba(255,255,255,0.75)');
  }

  // Store selection
  localStorage.setItem(STORAGE_KEY, theme.id);
}

// ── Main Component ────────────────────────────────────────────────────────────
function ThemeSwitcher() {
  const [open, setOpen] = useState(false);
  const [activeId, setActiveId] = useState(() => {
    return localStorage.getItem(STORAGE_KEY) || 'pink';
  });
  const panelRef = useRef(null);

  // Apply saved theme on mount
  useEffect(() => {
    const saved = THEMES.find(t => t.id === activeId) || THEMES[0];
    applyTheme(saved);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Close panel when clicking outside
  useEffect(() => {
    const handler = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    if (open) document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  const handleSelect = (theme) => {
    setActiveId(theme.id);
    applyTheme(theme);
  };

  const activeTheme = THEMES.find(t => t.id === activeId) || THEMES[0];

  return (
    <div className="theme-switcher-root" ref={panelRef}>

      {/* Trigger button */}
      <button
        id="theme-switcher-btn"
        className="theme-trigger-btn"
        onClick={() => setOpen(o => !o)}
        title="Đổi màu giao diện"
        aria-label="Mở bộ chọn chủ đề màu sắc"
      >
        <span className="theme-trigger-palette">
          {activeTheme.preview.map((c, i) => (
            <span key={i} style={{ background: c }} className="theme-trigger-dot" />
          ))}
        </span>
        <span className="theme-trigger-label">🎨</span>
      </button>

      {/* Floating panel */}
      <div className={`theme-panel ${open ? 'open' : ''}`}>
        <div className="theme-panel-header">
          <span className="theme-panel-title">🎨 Chủ Đề Màu Sắc</span>
          <button className="theme-panel-close" onClick={() => setOpen(false)}>×</button>
        </div>

        <div className="theme-grid">
          {THEMES.map(theme => (
            <button
              key={theme.id}
              id={`theme-btn-${theme.id}`}
              className={`theme-card ${activeId === theme.id ? 'active' : ''}`}
              onClick={() => handleSelect(theme)}
              title={theme.name}
            >
              {/* Color preview swatches */}
              <div className="theme-swatches">
                {theme.preview.map((c, i) => (
                  <span
                    key={i}
                    className="theme-swatch"
                    style={{ background: c, width: i === 0 ? '40%' : '30%' }}
                  />
                ))}
              </div>
              <div className="theme-card-label">
                <span className="theme-card-emoji">{theme.emoji}</span>
                <span className="theme-card-name">{theme.name}</span>
              </div>
              {activeId === theme.id && (
                <span className="theme-card-check">✓</span>
              )}
            </button>
          ))}
        </div>

        <p className="theme-hint">Chủ đề được lưu tự động cho lần sau.</p>
      </div>
    </div>
  );
}

export default ThemeSwitcher;
