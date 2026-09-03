/**
 * Accessible Dashboard Page (Google Pay / GPay India Format)
 * Inspired by Google Pay UI/UX Design System from Google Stitch MCP
 *
 * Implements:
 * - Google Pay clean white Material 3 layout with pure white canvas & subtle tonal layers
 * - GPay Pill search & voice bar ("Pay anyone by voice or name")
 * - 4-Column circular quick actions: Scan QR, Pay Contacts, Bank Transfer, Trusted Circle
 * - "People" horizontal scrollable contact avatars (Ravi Kumar, Ananya, Electricity, Kirana)
 * - "Trusted Circle Protection" shield card with active second-opinion status
 * - "Manage your money": Check bank balance with audio voice reading & transaction history
 * - Floating Google Blue voice microphone FAB
 */
import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Header } from '../components/Header'
import { CaptionsBanner } from '../components/CaptionsBanner'
import { useAccessibility } from '../context/AccessibilityContext'
import { api, Transaction, ensureDemoUser } from '../services/api'
import { voice } from '../services/voice'

export const DashboardPage: React.FC = () => {
  const { speakWithCaptions } = useAccessibility()
  const navigate = useNavigate()

  const [userName, setUserName] = useState<string>('Meena Devi')
  const [balance] = useState<string>('50,000.00')
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [isListening, setIsListening] = useState<boolean>(false)
  const [speechTranscript, setSpeechTranscript] = useState<string>('')
  const [showBalance, setShowBalance] = useState<boolean>(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    setLoading(true)
    try {
      await ensureDemoUser()
      const [userRes, txRes] = await Promise.all([
        api.getMe().catch(() => null),
        api.listTransactions().catch(() => null),
      ])

      if (userRes?.data?.name) {
        setUserName(userRes.data.name)
      }
      if (txRes?.data) {
        setTransactions(txRes.data)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleReadBalance = () => {
    speakWithCaptions(
      `Your current available balance in State Bank of India account ending in 4 3 2 1 is 50,000 rupees.`
    )
  }

  const handleVoiceQuickAction = () => {
    if (isListening) {
      setIsListening(false)
      voice.stopListening()
      return
    }

    setSpeechTranscript('Listening... Speak your command (e.g. "Send 5,000 to Ravi")')
    speakWithCaptions('Listening. Please tell me who you want to pay, and how much.')

    const started = voice.startListening(
      (transcript: string, isFinal: boolean) => {
        setSpeechTranscript(transcript)
        if (isFinal && transcript.trim()) {
          setIsListening(false)
          navigate(`/transactions/new?q=${encodeURIComponent(transcript)}`)
        }
      },
      () => {
        setIsListening(false)
        setSpeechTranscript('Voice not detected. Click below to type.')
      },
      () => {
        setIsListening(false)
      }
    )

    if (started) {
      setIsListening(true)
    }
  }

  return (
    <div className="page" style={{ background: '#ffffff' }}>
      <Header />
      <CaptionsBanner />

      <main className="container" style={{ padding: 'var(--space-4) var(--space-4) var(--space-16) var(--space-4)' }}>
        {/* ── 0. Top User Profile Greeting (GPay Format) ────────────────────── */}
        <section style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-4)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <div
              style={{
                width: '46px',
                height: '46px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%)',
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 700,
                fontSize: '1.1rem',
                boxShadow: '0 2px 8px rgba(26, 115, 232, 0.25)',
              }}
              aria-hidden="true"
            >
              MD
            </div>
            <div>
              <div style={{ fontSize: 'var(--text-lg)', fontWeight: 700, color: 'var(--color-text)' }}>
                Namaste, {userName}
              </div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                State Bank of India ••4321
              </div>
            </div>
          </div>
          <span className="badge badge-low">UPI SAFE</span>
        </section>
        {/* ── 1. GPay Style Search / Voice Bar ───────────────────────────────── */}
        <section style={{ marginBottom: 'var(--space-6)' }} aria-label="Voice and Search Bar">
          <div
            className="gpay-search-pill"
            onClick={handleVoiceQuickAction}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && handleVoiceQuickAction()}
            aria-label="Pay anyone by voice or name. Click to speak."
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
              <span style={{ fontSize: '1.3rem', color: '#1a73e8' }} aria-hidden="true">
                🔍
              </span>
              <span style={{ color: 'var(--color-text-muted)', fontSize: 'var(--text-base)', fontWeight: 500 }}>
                {isListening ? 'Listening... Speak now' : 'Pay anyone by voice or name'}
              </span>
            </div>

            <button
              type="button"
              className={`btn ${isListening ? 'pulse' : ''}`}
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                padding: 0,
                background: isListening ? '#dc2626' : '#1a73e8',
                color: '#ffffff',
                border: 'none',
                boxShadow: '0 2px 8px rgba(26, 115, 232, 0.3)',
              }}
              aria-label={isListening ? 'Stop voice listening' : 'Start voice command'}
              onClick={(e) => {
                e.stopPropagation()
                handleVoiceQuickAction()
              }}
            >
              <span style={{ fontSize: '1.25rem' }}>{isListening ? '⏹️' : '🎙️'}</span>
            </button>
          </div>

          {speechTranscript && (
            <div
              style={{
                marginTop: 'var(--space-3)',
                padding: 'var(--space-3) var(--space-4)',
                background: '#e8f0fe',
                borderRadius: 'var(--radius-lg)',
                color: '#1a73e8',
                fontWeight: 600,
                fontSize: 'var(--text-sm)',
                textAlign: 'center',
              }}
              role="status"
              aria-live="polite"
            >
              "{speechTranscript}"
            </div>
          )}
        </section>

        {/* ── 2. GPay 4-Column Quick Actions ─────────────────────────────────── */}
        <section aria-label="Quick Actions" style={{ marginBottom: 'var(--space-6)' }}>
          <div className="gpay-action-grid">
            {/* Scan QR */}
            <Link to="/transactions/new" className="gpay-circle-action" aria-label="Scan any QR code">
              <div className="gpay-circle-btn gpay-circle-blue">
                <span aria-hidden="true">📷</span>
              </div>
              <span className="gpay-circle-label">Scan QR</span>
            </Link>

            {/* Pay Contacts */}
            <Link to="/transactions/new" className="gpay-circle-action" aria-label="Pay Phone Contacts">
              <div className="gpay-circle-btn gpay-circle-green">
                <span aria-hidden="true">👤</span>
              </div>
              <span className="gpay-circle-label">Pay Contacts</span>
            </Link>

            {/* Bank Transfer */}
            <Link to="/transactions/new" className="gpay-circle-action" aria-label="Bank Transfer">
              <div className="gpay-circle-btn gpay-circle-yellow">
                <span aria-hidden="true">🏛️</span>
              </div>
              <span className="gpay-circle-label">Bank Transfer</span>
            </Link>

            {/* Trusted Circle */}
            <Link to="/trusted-circle" className="gpay-circle-action" aria-label="Trusted Circle Safety Hub">
              <div className="gpay-circle-btn gpay-circle-shield">
                <span aria-hidden="true">🛡️</span>
              </div>
              <span className="gpay-circle-label">Trusted Circle</span>
            </Link>
          </div>
        </section>

        {/* ── 3. GPay "People" Section (Horizontal Scrollable Avatars) ────────── */}
        <section style={{ marginBottom: 'var(--space-6)' }} aria-label="Frequent People">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
            <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: 700 }}>People</h2>
            <Link to="/transactions/new" style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: '#1a73e8' }}>
              + Send New
            </Link>
          </div>

          <div className="gpay-people-scroll">
            {/* Ravi Kumar */}
            <Link
              to="/transactions/new?q=Send+1200+to+Ravi"
              className="gpay-person-card"
              aria-label="Pay Ravi Kumar (frequent recipient)"
            >
              <div className="gpay-avatar" style={{ background: 'linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%)' }}>
                RK
              </div>
              <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text)', textAlign: 'center' }}>
                Ravi Kumar
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>₹1,200 avg</span>
            </Link>

            {/* Ananya (Daughter) */}
            <Link
              to="/transactions/new?q=Send+500+to+Ananya"
              className="gpay-person-card"
              aria-label="Pay Daughter Ananya"
            >
              <div className="gpay-avatar" style={{ background: 'linear-gradient(135deg, #059669 0%, #047857 100%)' }}>
                AD
              </div>
              <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text)', textAlign: 'center' }}>
                Ananya (Daughter)
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-risk-low)', fontWeight: 600 }}>Protector</span>
            </Link>

            {/* Electricity Bill */}
            <Link
              to="/transactions/new?q=Pay+Electricity+Bill"
              className="gpay-person-card"
              aria-label="Pay Electricity Bill"
            >
              <div className="gpay-avatar" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
                💡
              </div>
              <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text)', textAlign: 'center' }}>
                Electricity
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Bill Pay</span>
            </Link>

            {/* Sharma Kirana */}
            <Link
              to="/transactions/new?q=Pay+Sharma+Kirana"
              className="gpay-person-card"
              aria-label="Pay Sharma Kirana Store"
            >
              <div className="gpay-avatar" style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)' }}>
                🛒
              </div>
              <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text)', textAlign: 'center' }}>
                Sharma Kirana
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Groceries</span>
            </Link>

            {/* Community Literacy Classes */}
            <Link
              to="/community"
              className="gpay-person-card"
              aria-label="Join Community Classes"
            >
              <div className="gpay-avatar" style={{ background: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)' }}>
                👥
              </div>
              <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text)', textAlign: 'center' }}>
                Community
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Classes</span>
            </Link>
          </div>
        </section>

        {/* ── 4. GPay Safety & Shield Card (Trusted Circle Protection) ────────── */}
        <section style={{ marginBottom: 'var(--space-6)' }} aria-label="Security and Protection">
          <div
            style={{
              background: '#ffffff',
              border: '1.5px solid rgba(0, 86, 210, 0.2)',
              borderRadius: 'var(--radius-xl)',
              padding: 'var(--space-4) var(--space-5)',
              boxShadow: '0 4px 16px rgba(0, 32, 128, 0.05)',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <span style={{ fontSize: '1.5rem', color: '#1a73e8' }} aria-hidden="true">
                  🛡️
                </span>
                <h2 style={{ fontSize: 'var(--text-base)', fontWeight: 700, margin: 0 }}>
                  Trusted Circle Protection
                </h2>
              </div>
              <span className="badge badge-low">ACTIVE SHIELD</span>
            </div>

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: 'var(--space-3) var(--space-4)',
                background: '#f8fafd',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid rgba(0, 86, 210, 0.08)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                <div
                  style={{
                    width: '42px',
                    height: '42px',
                    borderRadius: '50%',
                    background: '#e8f0fe',
                    color: '#1a73e8',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    fontSize: '1rem',
                  }}
                >
                  A
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 'var(--text-sm)', color: 'var(--color-text)' }}>
                    Daughter (Ananya)
                  </div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-risk-low)', fontWeight: 600 }}>
                    ✓ Second Opinion Ready • Shared guidance, no PIN access
                  </div>
                </div>
              </div>

              <Link
                to="/trusted-circle"
                className="btn btn-secondary"
                style={{ minHeight: '36px', padding: 'var(--space-1) var(--space-3)', fontSize: 'var(--text-xs)' }}
              >
                Manage
              </Link>
            </div>
          </div>
        </section>

        {/* ── 5. GPay "Manage Your Money" Section ─────────────────────────────── */}
        <section aria-label="Manage your money">
          <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: 700, marginBottom: 'var(--space-3)' }}>
            Manage your money
          </h2>

          {/* Check Bank Balance Card */}
          <div className="gpay-manage-row" role="region" aria-label="Bank Balance Details">
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '50%',
                  background: '#e8f0fe',
                  color: '#1a73e8',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.3rem',
                }}
                aria-hidden="true"
              >
                🏦
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: 'var(--text-base)', color: 'var(--color-text)' }}>
                  State Bank of India (••4321)
                </div>
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                  Savings Account
                </div>
              </div>
            </div>

            <div
              style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', cursor: 'pointer' }}
              onClick={() => setShowBalance(!showBalance)}
              title="Click to hide or show balance"
            >
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                  {showBalance ? 'Available (Tap to hide)' : 'Hidden (Tap to show)'}
                </div>
                <div style={{ fontWeight: 800, fontSize: 'var(--text-lg)', color: 'var(--color-text)' }}>
                  {showBalance ? `₹${balance}` : '••••••'}
                </div>
              </div>

              <button
                type="button"
                onClick={handleReadBalance}
                className="btn btn-secondary"
                style={{
                  minHeight: '40px',
                  width: '40px',
                  borderRadius: '50%',
                  padding: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.2rem',
                }}
                title="Read Balance Aloud"
                aria-label="Read Balance Aloud"
              >
                🔊
              </button>
            </div>
          </div>

          {/* See Transaction History Row */}
          <Link
            to="/transactions/new"
            className="gpay-manage-row"
            aria-label="View complete transaction history"
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '50%',
                  background: '#f1f3f4',
                  color: 'var(--color-text)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.3rem',
                }}
                aria-hidden="true"
              >
                📜
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: 'var(--text-base)', color: 'var(--color-text)' }}>
                  See transaction history
                </div>
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                  {transactions.length} recent transactions
                </div>
              </div>
            </div>

            <span style={{ fontSize: '1.4rem', color: 'var(--color-text-muted)' }}>›</span>
          </Link>

          {/* Recent Transaction Previews */}
          {loading ? (
            <div style={{ textAlign: 'center', padding: 'var(--space-4)' }}>
              <div className="spinner" style={{ margin: '0 auto' }}></div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', marginTop: 'var(--space-2)' }}>
              {transactions.slice(0, 3).map((tx) => (
                <div
                  key={tx.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: 'var(--space-3) var(--space-4)',
                    background: '#ffffff',
                    border: '1px solid rgba(0, 0, 0, 0.06)',
                    borderRadius: 'var(--radius-md)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                    <div
                      style={{
                        width: '38px',
                        height: '38px',
                        borderRadius: '50%',
                        background: tx.status === 'COMPLETED' ? '#e6f4ea' : '#fef7e0',
                        color: tx.status === 'COMPLETED' ? '#1e8e3e' : '#f29900',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 700,
                        fontSize: '0.9rem',
                      }}
                    >
                      {tx.beneficiary_name ? tx.beneficiary_name.charAt(0) : '₹'}
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: 'var(--text-sm)' }}>
                        {tx.beneficiary_name || 'Payment'}
                      </div>
                      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                        {new Date(tx.created_at).toLocaleDateString()} • {tx.intent}
                      </div>
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 700, fontSize: 'var(--text-sm)' }}>
                      ₹{parseFloat(tx.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </div>
                    <span
                      className={`badge ${
                        tx.status === 'COMPLETED'
                          ? 'badge-low'
                          : tx.status === 'BLOCKED'
                          ? 'badge-critical'
                          : 'badge-medium'
                      }`}
                      style={{ fontSize: '0.65rem', padding: '1px 6px' }}
                    >
                      {tx.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* ── Floating Voice Assistant FAB (Google Blue) ───────────────────────── */}
      <button
        type="button"
        className={`fab-voice ${isListening ? 'pulse' : ''}`}
        onClick={handleVoiceQuickAction}
        aria-label={isListening ? 'Stop voice assistant' : 'Activate voice assistant'}
        title="Voice Assistant"
        style={{
          background: isListening ? '#dc2626' : 'linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%)',
        }}
      >
        <span style={{ fontSize: '2rem' }} aria-hidden="true">
          {isListening ? '⏹️' : '🎙️'}
        </span>
      </button>
    </div>
  )
}
