import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Search, RotateCcw, HelpCircle } from 'lucide-react';
import SearchModal from './SearchModal';

const routeLabels: Record<string, { title: string; breadcrumb: string[] }> = {
  '/': { title: 'Overview', breadcrumb: ['Dashboard'] },
  '/cpu': { title: 'CPU Scheduling', breadcrumb: ['Simulations', 'CPU Scheduling'] },
  '/memory': { title: 'Memory Management', breadcrumb: ['Simulations', 'Memory Management'] },
  '/paging': { title: 'Page Replacement', breadcrumb: ['Simulations', 'Page Replacement'] },
  '/sync': { title: 'Synchronization', breadcrumb: ['Simulations', 'Synchronization'] },
  '/deadlock': { title: 'Deadlock', breadcrumb: ['Simulations', 'Deadlock'] },
  '/disk': { title: 'Disk Scheduling', breadcrumb: ['Simulations', 'Disk Scheduling'] },
  '/lab': { title: 'Algorithm Lab', breadcrumb: ['Tools', 'Algorithm Lab'] },
  '/docs': { title: 'Documentation', breadcrumb: ['Resources', 'Documentation'] },
};

export default function TopBar() {
  const location = useLocation();
  const route = routeLabels[location.pathname] || { title: 'OSim Nexus', breadcrumb: [] };

  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isResetting, setIsResetting] = useState(false);

  // Global Ctrl+K / Cmd+K shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleGlobalReset = () => {
    setIsResetting(true);
    window.dispatchEvent(new CustomEvent('osim:reset'));
    setTimeout(() => setIsResetting(false), 500);
  };

  return (
    <>
      <header
        style={{
          height: 52,
          background: 'var(--color-bg-secondary)',
          borderBottom: '1px solid var(--color-border-default)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          flexShrink: 0,
          zIndex: 30,
        }}
      >
        {/* Left: Breadcrumb */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {route.breadcrumb.map((crumb, i) => (
              <span key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                {i > 0 && <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>/</span>}
                <span
                  style={{
                    fontSize: '0.8rem',
                    color: i === route.breadcrumb.length - 1 ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)',
                    fontWeight: i === route.breadcrumb.length - 1 ? 600 : 400,
                  }}
                >
                  {crumb}
                </span>
              </span>
            ))}
          </div>
        </div>

        {/* Right: Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {/* Search / Command Palette Button */}
          <button
            className="btn btn-ghost btn-sm"
            style={{ gap: 8, color: 'var(--color-text-tertiary)' }}
            title="Search (Ctrl+K)"
            onClick={() => setIsSearchOpen(true)}
          >
            <Search size={14} />
            <span style={{ fontSize: '0.75rem' }}>Search</span>
            <kbd
              style={{
                fontSize: '0.65rem',
                padding: '1px 5px',
                borderRadius: 4,
                background: 'var(--color-bg-elevated)',
                border: '1px solid var(--color-border-default)',
                color: 'var(--color-text-muted)',
                fontFamily: 'var(--font-mono)',
              }}
            >
              ⌘K
            </kbd>
          </button>

          {/* Reset Current Module */}
          <button
            className="btn btn-ghost btn-sm"
            title="Reset current module state"
            onClick={handleGlobalReset}
            style={{
              color: isResetting ? 'var(--color-accent-cyan)' : undefined,
              transition: 'color 0.2s',
            }}
          >
            <RotateCcw
              size={14}
              style={{
                transform: isResetting ? 'rotate(-360deg)' : 'none',
                transition: isResetting ? 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)' : 'none',
              }}
            />
          </button>

          <a
            href="/docs"
            className="btn btn-ghost btn-sm"
            title="Documentation & Guides"
            style={{ textDecoration: 'none' }}
          >
            <HelpCircle size={14} />
          </a>
        </div>
      </header>

      {/* Global Search / Command Palette Dialog */}
      <SearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
    </>
  );
}
