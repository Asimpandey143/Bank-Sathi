/**
 * Accessible Header Component with Interactive Demo Control Bar
 *
 * Includes:
 * - Brand logo & tagline
 * - Hackathon Demonstration Control Bar (Role switcher & 1-click demo story)
 * - Quick accessibility toggles (Font size +/- and High Contrast)
 * - Navigation links
 */
import React, { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAccessibility } from '../context/AccessibilityContext'
import { loginDemoRole, getCurrentDemoRole, DemoRole } from '../services/api'

export const Header: React.FC = () => {
  const { fontScale, setFontScale, highContrast, setHighContrast } = useAccessibility()
  const location = useLocation()
  const navigate = useNavigate()
  const [currentRole, setCurrentRole] = useState<DemoRole>(getCurrentDemoRole())
  const [switching, setSwitching] = useState<boolean>(false)

  const handleSwitchRole = async (role: DemoRole) => {
    setSwitching(true)
    try {
      await loginDemoRole(role)
      setCurrentRole(role)
      if (role === 'daughter') {
        navigate('/trusted-circle')
      } else {
        navigate('/dashboard')
      }
      window.location.reload()
    } catch {
      setSwitching(false)
    }
  }

  const handleRunDemoStory = async () => {
    setSwitching(true)
    try {
      await loginDemoRole('mother')
      setCurrentRole('mother')
      navigate('/transactions/new?q=Send+5000+to+Ravi')
      window.location.reload()
    } catch {
      setSwitching(false)
    }
  }

  return (
    <header
      role="banner"
      style={{
        borderBottom: '1px solid var(--color-border)',
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        boxShadow: '0 4px 20px -4px rgba(0, 32, 128, 0.04)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      {/* ── Hackathon Demo Bar ────────────────────────────────────────────── */}
      <div
        style={{
          background: 'linear-gradient(90deg, #004493 0%, #0056d2 60%, #1a73e8 100%)',
          color: '#ffffff',
          padding: '0.4rem 1rem',
          fontSize: '0.8rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.5rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.15)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontWeight: 800, letterSpacing: '0.05em', color: '#ffdfa0' }}>
            ⚡ LIVE DEMO CONTROLLER:
          </span>
          <span>
            Active Role:{' '}
            <strong>
              {currentRole === 'daughter' ? '🛡️ Daughter (Ananya)' : '👵 Mother (Meena Devi)'}
            </strong>
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
          <button
            type="button"
            disabled={switching}
            onClick={() => handleSwitchRole('mother')}
            style={{
              background: currentRole === 'mother' ? '#ffffff' : 'rgba(255, 255, 255, 0.18)',
              color: currentRole === 'mother' ? '#004493' : '#ffffff',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '9999px',
              padding: '2px 10px',
              fontWeight: 700,
              fontSize: '0.72rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            👵 1. Mother (Meena)
          </button>

          <button
            type="button"
            disabled={switching}
            onClick={() => handleSwitchRole('daughter')}
            style={{
              background: currentRole === 'daughter' ? '#ffffff' : 'rgba(255, 255, 255, 0.18)',
              color: currentRole === 'daughter' ? '#004493' : '#ffffff',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '9999px',
              padding: '2px 10px',
              fontWeight: 700,
              fontSize: '0.72rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            🛡️ 2. Daughter (Ananya)
          </button>

          <button
            type="button"
            disabled={switching}
            onClick={handleRunDemoStory}
            style={{
              background: 'linear-gradient(135deg, #fbbc04 0%, #f59e0b 100%)',
              color: '#1a1c20',
              border: 'none',
              borderRadius: '9999px',
              padding: '3px 12px',
              fontWeight: 800,
              fontSize: '0.72rem',
              cursor: 'pointer',
              boxShadow: '0 2px 6px rgba(0, 0, 0, 0.2)',
            }}
            title="Starts the ₹5,000 to Ravi demo payment scenario"
          >
            ▶️ Run ₹5,000 Demo Story
          </button>
        </div>
      </div>

      <div
        className="container"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 'var(--space-3)',
          paddingTop: 'var(--space-3)',
          paddingBottom: 'var(--space-3)',
        }}
      >
        {/* Logo */}
        <Link
          to="/dashboard"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)',
            textDecoration: 'none',
          }}
          aria-label="BankSathi Home"
        >
          <span style={{ fontSize: 'var(--text-3xl)' }} aria-hidden="true">
            🏦
          </span>
          <div>
            <div
              style={{
                fontFamily: 'var(--font-heading)',
                fontSize: 'var(--text-xl)',
                fontWeight: 800,
                color: 'var(--color-text)',
                lineHeight: 1.1,
              }}
            >
              BankSathi
            </div>
            <div
              style={{
                fontSize: 'var(--text-xs)',
                color: 'var(--color-text-muted)',
                fontWeight: 500,
              }}
            >
              Shared guidance, not shared access
            </div>
          </div>
        </Link>

        {/* Accessibility Quick Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          {/* Font scale decrease */}
          <button
            type="button"
            className="btn btn-secondary"
            style={{ minHeight: '38px', padding: 'var(--space-1) var(--space-3)', fontSize: '0.85rem' }}
            onClick={() => setFontScale(Math.max(0.85, fontScale - 0.15))}
            aria-label="Decrease text size"
            title="Decrease text size"
          >
            A-
          </button>

          {/* Font scale increase */}
          <button
            type="button"
            className="btn btn-secondary"
            style={{ minHeight: '38px', padding: 'var(--space-1) var(--space-3)', fontSize: '1.1rem', fontWeight: 700 }}
            onClick={() => setFontScale(Math.min(2.0, fontScale + 0.15))}
            aria-label="Increase text size"
            title="Increase text size"
          >
            A+
          </button>

          {/* High contrast toggle */}
          <button
            type="button"
            className="btn btn-secondary"
            style={{ minHeight: '38px', padding: 'var(--space-1) var(--space-3)' }}
            onClick={() => setHighContrast(!highContrast)}
            aria-label={highContrast ? 'Disable high contrast' : 'Enable high contrast'}
            title="Toggle contrast mode"
          >
            {highContrast ? '☀️ Normal' : '🌓 Contrast'}
          </button>
        </div>
      </div>

      {/* Navigation Links */}
      <nav
        aria-label="Main Navigation"
        style={{
          borderTop: '1px solid var(--color-border)',
          padding: 'var(--space-2) 0',
          background: 'rgba(255, 255, 255, 0.6)',
        }}
      >
        <div
          className="container"
          style={{
            display: 'flex',
            gap: 'var(--space-6)',
            alignItems: 'center',
            overflowX: 'auto',
          }}
        >
          <Link
            to="/dashboard"
            style={{
              fontWeight: location.pathname === '/dashboard' ? 700 : 500,
              color: location.pathname === '/dashboard' ? 'var(--color-primary)' : 'var(--color-text-muted)',
              fontSize: 'var(--text-sm)',
              padding: 'var(--space-1) 0',
              textDecoration: 'none',
              borderBottom: location.pathname === '/dashboard' ? '2px solid var(--color-primary)' : 'none',
            }}
          >
            Dashboard
          </Link>

          <Link
            to="/transactions/new"
            style={{
              fontWeight: location.pathname.startsWith('/transactions') ? 700 : 500,
              color: location.pathname.startsWith('/transactions') ? 'var(--color-primary)' : 'var(--color-text-muted)',
              fontSize: 'var(--text-sm)',
              padding: 'var(--space-1) 0',
              textDecoration: 'none',
              borderBottom: location.pathname.startsWith('/transactions') ? '2px solid var(--color-primary)' : 'none',
            }}
          >
            Send Money
          </Link>

          <Link
            to="/trusted-circle"
            style={{
              fontWeight: location.pathname === '/trusted-circle' ? 700 : 500,
              color: location.pathname === '/trusted-circle' ? 'var(--color-primary)' : 'var(--color-text-muted)',
              fontSize: 'var(--text-sm)',
              padding: 'var(--space-1) 0',
              textDecoration: 'none',
              borderBottom: location.pathname === '/trusted-circle' ? '2px solid var(--color-primary)' : 'none',
            }}
          >
            Trusted Circle
          </Link>

          <Link
            to="/community"
            style={{
              fontWeight: location.pathname === '/community' ? 700 : 500,
              color: location.pathname === '/community' ? 'var(--color-primary)' : 'var(--color-text-muted)',
              fontSize: 'var(--text-sm)',
              padding: 'var(--space-1) 0',
              textDecoration: 'none',
              borderBottom: location.pathname === '/community' ? '2px solid var(--color-primary)' : 'none',
            }}
          >
            Community
          </Link>
        </div>
      </nav>
    </header>
  )
}
