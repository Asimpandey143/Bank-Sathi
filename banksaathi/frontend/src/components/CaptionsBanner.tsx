/**
 * Live Captions Banner Component
 *
 * Implements WCAG AAA synchronized visual captions for all spoken audio narration.
 * Uses aria-live="polite" for screen reader accessibility.
 */
import React from 'react'
import { useAccessibility } from '../context/AccessibilityContext'

export const CaptionsBanner: React.FC = () => {
  const { activeCaption, clearCaptions } = useAccessibility()

  if (!activeCaption) return null

  return (
    <div
      role="region"
      aria-label="Spoken audio live captions"
      aria-live="polite"
      style={{
        position: 'fixed',
        bottom: 'var(--space-4)',
        left: '50%',
        transform: 'translateX(-50%)',
        width: 'calc(100% - 32px)',
        maxWidth: '560px',
        zIndex: 100,
        background: 'rgba(15, 17, 23, 0.95)',
        border: '2px solid var(--color-primary)',
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--space-4)',
        boxShadow: 'var(--shadow-lg)',
        backdropFilter: 'blur(12px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 'var(--space-3)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        <span style={{ fontSize: 'var(--text-xl)' }} aria-hidden="true">
          💬
        </span>
        <div>
          <div
            style={{
              fontSize: 'var(--text-xs)',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: 'var(--color-primary)',
              marginBottom: '2px',
            }}
          >
            Live Audio Caption
          </div>
          <div
            style={{
              fontSize: 'var(--text-base)',
              fontWeight: 600,
              color: '#ffffff',
              lineHeight: 1.4,
            }}
          >
            {activeCaption}
          </div>
        </div>
      </div>

      <button
        type="button"
        onClick={clearCaptions}
        className="btn btn-secondary"
        style={{ minHeight: '36px', padding: '0 var(--space-2)' }}
        aria-label="Dismiss audio caption"
      >
        ✕
      </button>
    </div>
  )
}
