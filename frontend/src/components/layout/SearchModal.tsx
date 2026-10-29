import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Search,
  X,
  Cpu,
  Layers,
  FlaskConical,
  BookOpen,
  ArrowRight,
  RotateCcw,
} from 'lucide-react';

export interface SearchItem {
  id: string;
  title: string;
  description: string;
  category: 'Simulation' | 'Algorithm' | 'Lab' | 'Docs';
  path: string;
  keywords: string[];
}

const SEARCH_ITEMS: SearchItem[] = [
  // CPU
  {
    id: 'cpu-main',
    title: 'CPU Scheduling Lab',
    description: 'FCFS, SJF, SRTF, Round Robin, Priority preemptive and non-preemptive',
    category: 'Simulation',
    path: '/cpu',
    keywords: ['cpu', 'processor', 'scheduling', 'gantt', 'turnaround', 'waiting'],
  },
  {
    id: 'cpu-fcfs',
    title: 'First Come First Served (FCFS)',
    description: 'Non-preemptive CPU scheduling servicing processes by arrival time',
    category: 'Algorithm',
    path: '/cpu',
    keywords: ['fcfs', 'first come', 'queue', 'fifo', 'convoy'],
  },
  {
    id: 'cpu-sjf',
    title: 'Shortest Job First (SJF)',
    description: 'Non-preemptive scheduling based on shortest execution burst time',
    category: 'Algorithm',
    path: '/cpu',
    keywords: ['sjf', 'shortest job', 'burst time', 'optimal waiting'],
  },
  {
    id: 'cpu-srtf',
    title: 'Shortest Remaining Time First (SRTF)',
    description: 'Preemptive variant of SJF scheduling based on remaining burst time',
    category: 'Algorithm',
    path: '/cpu?demo=srtf',
    keywords: ['srtf', 'preemptive sjf', 'remaining time', 'preemption'],
  },
  {
    id: 'cpu-rr',
    title: 'Round Robin (RR)',
    description: 'Preemptive circular time-sliced scheduling with configurable time quantum',
    category: 'Algorithm',
    path: '/cpu?demo=rr',
    keywords: ['rr', 'round robin', 'time quantum', 'preemptive', 'slice'],
  },
  {
    id: 'cpu-priority',
    title: 'Priority Scheduling',
    description: 'Preemptive and Non-Preemptive scheduling by assigned process priority',
    category: 'Algorithm',
    path: '/cpu?demo=priority',
    keywords: ['priority', 'preemptive priority', 'starvation', 'aging'],
  },

  // Memory
  {
    id: 'mem-main',
    title: 'Memory Management Lab',
    description: 'Dynamic partition allocation with fragmentation metrics',
    category: 'Simulation',
    path: '/memory',
    keywords: ['memory', 'ram', 'partitioning', 'fragmentation', 'holes', 'allocation'],
  },
  {
    id: 'mem-first-fit',
    title: 'First Fit Allocation',
    description: 'Allocates the first free memory block large enough for the process',
    category: 'Algorithm',
    path: '/memory',
    keywords: ['first fit', 'memory', 'allocation', 'partition'],
  },
  {
    id: 'mem-best-fit',
    title: 'Best Fit Allocation',
    description: 'Allocates the smallest free block adequate for the process size',
    category: 'Algorithm',
    path: '/memory',
    keywords: ['best fit', 'memory', 'smallest hole', 'external fragmentation'],
  },
  {
    id: 'mem-worst-fit',
    title: 'Worst Fit Allocation',
    description: 'Allocates the largest free block to retain large usable leftover gaps',
    category: 'Algorithm',
    path: '/memory',
    keywords: ['worst fit', 'memory', 'largest hole'],
  },
  {
    id: 'mem-next-fit',
    title: 'Next Fit Allocation',
    description: 'Circular variant of First Fit resuming search from previous allocation',
    category: 'Algorithm',
    path: '/memory',
    keywords: ['next fit', 'memory', 'circular search'],
  },

  // Paging
  {
    id: 'paging-main',
    title: 'Page Replacement Lab',
    description: 'Virtual memory frame allocation, page faults, and page hit analysis',
    category: 'Simulation',
    path: '/paging',
    keywords: ['paging', 'virtual memory', 'page fault', 'hit ratio', 'belady'],
  },
  {
    id: 'paging-fifo',
    title: 'FIFO Page Replacement',
    description: 'Replaces the oldest page present in the allocated frames queue',
    category: 'Algorithm',
    path: '/paging?demo=fifo',
    keywords: ['fifo', 'first in first out', 'page fault', 'belady anomaly'],
  },
  {
    id: 'paging-lru',
    title: 'LRU (Least Recently Used)',
    description: 'Evicts the page that has not been referenced for the longest time',
    category: 'Algorithm',
    path: '/paging?demo=lru',
    keywords: ['lru', 'least recently used', 'stack algorithm'],
  },
  {
    id: 'paging-opt',
    title: 'Optimal Page Replacement (Bélády)',
    description: 'Theoretical optimum replacing page not used for the longest future time',
    category: 'Algorithm',
    path: '/paging?demo=optimal',
    keywords: ['optimal', 'belady', 'min page fault', 'benchmark'],
  },
  {
    id: 'paging-clock',
    title: 'Second Chance (Clock)',
    description: 'Approximates LRU using reference bits in a circular queue',
    category: 'Algorithm',
    path: '/paging',
    keywords: ['second chance', 'clock', 'reference bit', 'lru approximation'],
  },

  // Deadlock
  {
    id: 'deadlock-main',
    title: 'Deadlock Analysis Lab',
    description: "Banker's Algorithm safety verification, resource allocation matrix, and cycle detection",
    category: 'Simulation',
    path: '/deadlock',
    keywords: ['deadlock', 'banker', 'safe sequence', 'resource allocation', 'rag', 'cycle'],
  },
  {
    id: 'deadlock-safe',
    title: "Banker's Algorithm: Safe State Preset",
    description: 'Silberschatz textbook demonstration with verified safe execution sequence',
    category: 'Algorithm',
    path: '/deadlock?demo=safe',
    keywords: ['safe state', 'bankers algorithm', 'avoidance', 'work vector'],
  },
  {
    id: 'deadlock-unsafe',
    title: "Banker's Algorithm: Unsafe State Preset",
    description: 'Resource contention scenario leading to deadlock vulnerability',
    category: 'Algorithm',
    path: '/deadlock?demo=unsafe',
    keywords: ['unsafe state', 'deadlock risk', 'banker'],
  },

  // Disk
  {
    id: 'disk-main',
    title: 'Disk Scheduling Lab',
    description: 'Track seek optimization with seek sequence visualization and head metrics',
    category: 'Simulation',
    path: '/disk',
    keywords: ['disk', 'seek time', 'head movement', 'hard drive', 'cylinder'],
  },
  {
    id: 'disk-scan',
    title: 'SCAN (Elevator Algorithm)',
    description: 'Moves head in one direction servicing tracks, then reverses direction',
    category: 'Algorithm',
    path: '/disk?demo=scan',
    keywords: ['scan', 'elevator', 'disk scheduling', 'head movement'],
  },
  {
    id: 'disk-cscan',
    title: 'C-SCAN (Circular SCAN)',
    description: 'Services requests in one direction and returns to beginning track',
    category: 'Algorithm',
    path: '/disk',
    keywords: ['c-scan', 'circular scan', 'uniform waiting'],
  },
  {
    id: 'disk-look',
    title: 'LOOK & C-LOOK',
    description: 'SCAN variants that reverse at the final request rather than disk edges',
    category: 'Algorithm',
    path: '/disk',
    keywords: ['look', 'c-look', 'disk seek'],
  },

  // Sync
  {
    id: 'sync-main',
    title: 'Process Synchronization Lab',
    description: 'Deterministic step simulations for Producer-Consumer & Dining Philosophers',
    category: 'Simulation',
    path: '/sync',
    keywords: ['sync', 'concurrency', 'mutex', 'semaphore', 'race condition', 'critical section'],
  },

  // Lab & Docs
  {
    id: 'lab-main',
    title: 'Algorithm Comparison Lab',
    description: 'Run and compare multiple scheduling and paging algorithms side-by-side',
    category: 'Lab',
    path: '/lab',
    keywords: ['lab', 'compare', 'benchmark', 'comparison', 'metrics'],
  },
  {
    id: 'docs-main',
    title: 'Documentation & Theory Guides',
    description: 'Comprehensive guides for OS algorithms, complexities, and learning notes',
    category: 'Docs',
    path: '/docs',
    keywords: ['docs', 'documentation', 'theory', 'notes', 'reference', 'complexity'],
  },
];

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => inputRef.current?.focus(), 50);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  const handleClose = useCallback(() => {
    setQuery('');
    onClose();
  }, [onClose]);

  // Keyboard navigation & close on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        handleClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, handleClose]);

  if (!isOpen) return null;

  const normalizedQuery = query.trim().toLowerCase();
  const filteredItems = normalizedQuery
    ? SEARCH_ITEMS.filter((item) => {
        const titleMatch = item.title.toLowerCase().includes(normalizedQuery);
        const descMatch = item.description.toLowerCase().includes(normalizedQuery);
        const catMatch = item.category.toLowerCase().includes(normalizedQuery);
        const keyMatch = item.keywords.some((k) => k.toLowerCase().includes(normalizedQuery));
        return titleMatch || descMatch || catMatch || keyMatch;
      })
    : SEARCH_ITEMS;

  const handleSelect = (path: string) => {
    navigate(path);
    onClose();
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Simulation':
        return <Cpu size={14} color="var(--color-accent-cyan)" />;
      case 'Algorithm':
        return <Layers size={14} color="var(--color-accent-indigo)" />;
      case 'Lab':
        return <FlaskConical size={14} color="var(--color-accent-purple)" />;
      case 'Docs':
        return <BookOpen size={14} color="var(--color-accent-emerald)" />;
      default:
        return <Search size={14} />;
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        background: 'rgba(0, 0, 0, 0.65)',
        backdropFilter: 'blur(6px)',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '12vh',
      }}
      onClick={handleClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: -10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96, y: -10 }}
        transition={{ duration: 0.15 }}
        style={{
          width: '100%',
          maxWidth: 620,
          background: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border-default)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          maxHeight: '75vh',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            padding: '14px 18px',
            borderBottom: '1px solid var(--color-border-default)',
            gap: 12,
            background: 'var(--color-bg-primary)',
          }}
        >
          <Search size={18} color="var(--color-text-muted)" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search simulations, algorithms, or topics (e.g. FCFS, Banker's, LRU, SCAN)..."
            style={{
              flex: 1,
              background: 'none',
              border: 'none',
              outline: 'none',
              color: 'var(--color-text-primary)',
              fontSize: '0.95rem',
              fontWeight: 500,
            }}
          />
          {query && (
            <button
              onClick={() => setQuery('')}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: 'var(--color-text-muted)',
                padding: '4px',
                display: 'flex',
                alignItems: 'center',
                borderRadius: '4px',
              }}
              title="Clear Search"
            >
              <RotateCcw size={14} />
            </button>
          )}
          <button
            onClick={handleClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--color-text-muted)',
              padding: '4px',
              display: 'flex',
              alignItems: 'center',
              borderRadius: '4px',
            }}
            title="Close (Esc)"
          >
            <X size={16} />
          </button>
        </div>

        {/* Results List */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '8px',
            display: 'flex',
            flexDirection: 'column',
            gap: 4,
          }}
        >
          {filteredItems.length === 0 ? (
            <div
              style={{
                padding: '36px 20px',
                textAlign: 'center',
                color: 'var(--color-text-tertiary)',
                fontSize: '0.88rem',
              }}
            >
              <p>No matching simulations or algorithms found for <strong>"{query}"</strong></p>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setQuery('')}
                style={{ marginTop: 12, gap: 6 }}
              >
                <RotateCcw size={13} /> Reset Search Query
              </button>
            </div>
          ) : (
            filteredItems.map((item) => (
              <div
                key={item.id}
                onClick={() => handleSelect(item.path)}
                style={{
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  transition: 'background 0.15s',
                  gap: 12,
                }}
                className="search-result-item"
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'var(--color-bg-elevated)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
                  <div
                    style={{
                      width: 28,
                      height: 28,
                      borderRadius: 6,
                      background: 'var(--color-bg-elevated)',
                      border: '1px solid var(--color-border-default)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                    }}
                  >
                    {getCategoryIcon(item.category)}
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span
                        style={{
                          fontSize: '0.88rem',
                          fontWeight: 600,
                          color: 'var(--color-text-primary)',
                        }}
                      >
                        {item.title}
                      </span>
                      <span
                        style={{
                          fontSize: '0.65rem',
                          fontWeight: 600,
                          textTransform: 'uppercase',
                          padding: '1px 6px',
                          borderRadius: 4,
                          background: 'var(--color-bg-primary)',
                          border: '1px solid var(--color-border-default)',
                          color: 'var(--color-text-muted)',
                        }}
                      >
                        {item.category}
                      </span>
                    </div>
                    <p
                      style={{
                        fontSize: '0.78rem',
                        color: 'var(--color-text-tertiary)',
                        margin: 0,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {item.description}
                    </p>
                  </div>
                </div>

                <ArrowRight size={14} color="var(--color-text-muted)" style={{ flexShrink: 0 }} />
              </div>
            ))
          )}
        </div>

        {/* Footer info */}
        <div
          style={{
            padding: '8px 16px',
            borderTop: '1px solid var(--color-border-default)',
            background: 'var(--color-bg-primary)',
            fontSize: '0.72rem',
            color: 'var(--color-text-muted)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span>
            Showing {filteredItems.length} of {SEARCH_ITEMS.length} resources
          </span>
          <div style={{ display: 'flex', gap: 10 }}>
            <span>
              <kbd style={{ padding: '1px 4px', borderRadius: 3, background: 'var(--color-bg-elevated)' }}>Esc</kbd> to close
            </span>
            <span>
              <kbd style={{ padding: '1px 4px', borderRadius: 3, background: 'var(--color-bg-elevated)' }}>Click</kbd> to navigate
            </span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
