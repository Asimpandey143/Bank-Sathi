/**
 * Transaction Review Page — The Core Accessibility & Safety Screen
 *
 * Implements:
 * - Transaction Story: Clear, human-centric summary of money movement
 * - Audio Narration: 1-click voice read-out with synchronous captions
 * - Transparent Risk Badge: Deterministic score, clear badge, and plain-language reasons
 * - User-Only Confirmation: Prominent touch target with state machine guard
 */
import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Header } from '../components/Header'
import { CaptionsBanner } from '../components/CaptionsBanner'
import { useAccessibility } from '../context/AccessibilityContext'
import { api, Transaction, ensureDemoUser } from '../services/api'

export const TransactionReviewPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { speakWithCaptions } = useAccessibility()

  const [tx, setTx] = useState<Transaction | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  useEffect(() => {
    async function fetchTx() {
      if (!id) return
      try {
        await ensureDemoUser()
        const res = await api.getTransaction(id)
        setTx(res.data)

        // Read narration automatically if transaction is loaded
        const narration = `Please review: You are sending ${res.data.amount} rupees to ${
          res.data.beneficiary_name || 'your contact'
        }. Risk level is ${res.data.risk_level || 'Low'}.`
        speakWithCaptions(narration, `Review: ₹${res.data.amount} to ${res.data.beneficiary_name}`)
      } catch (err: any) {
        setErrorMsg('Failed to load transaction details.')
      } finally {
        setLoading(false)
      }
    }
    fetchTx()
  }, [id])

  const handleReadAloud = async () => {
    if (!id || !tx) return
    try {
      const voiceRes = await api.synthesizeVoiceSummary(id)
      speakWithCaptions(voiceRes.data.speech_text, voiceRes.data.caption_text)
    } catch {
      speakWithCaptions(
        `You are sending ${tx.amount} rupees to ${tx.beneficiary_name}. Risk level: ${tx.risk_level}.`,
        `Sending ₹${tx.amount} to ${tx.beneficiary_name}`
      )
    }
  }

  const handleConfirm = async () => {
    if (!id) return
    setSubmitting(true)
    setErrorMsg(null)

    try {
      const res = await api.confirmTransaction(id)
      navigate(`/transactions/${id}/result`, { state: { transaction: res.data } })
    } catch (err: any) {
      const msg = err.response?.data?.message || 'Transaction could not be confirmed.'
      setErrorMsg(msg)
      speakWithCaptions(`Transaction failed: ${msg}`, `Error: ${msg}`)
    } finally {
      setSubmitting(false)
    }
  }

  const handleCancel = async () => {
    if (!id) return
    setSubmitting(true)
    try {
      await api.cancelTransaction(id)
      speakWithCaptions('Transaction cancelled safely.', 'Transaction cancelled.')
      navigate('/dashboard')
    } catch (err: any) {
      setErrorMsg('Failed to cancel transaction.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="page gradient-bg">
        <Header />
        <main className="container" style={{ textAlign: 'center', padding: 'var(--space-12)' }}>
          <div className="spinner" style={{ margin: '0 auto' }}></div>
          <p style={{ marginTop: 'var(--space-4)' }}>Loading transaction review...</p>
        </main>
      </div>
    )
  }

  if (!tx) {
    return (
      <div className="page gradient-bg">
        <Header />
        <main className="container" style={{ padding: 'var(--space-8)' }}>
          <div className="card" style={{ maxWidth: '540px', margin: '0 auto', textAlign: 'center' }}>
            <h2>Transaction Not Found</h2>
            <button className="btn btn-primary" onClick={() => navigate('/dashboard')} style={{ marginTop: 'var(--space-4)' }}>
              Return to Dashboard
            </button>
          </div>
        </main>
      </div>
    )
  }

  const isBlocked = tx.status === 'BLOCKED' || tx.risk_level === 'CRITICAL'
  const riskReasons = tx.risk_reasons?.reasons || []

  return (
    <div className="page gradient-bg">
      <Header />
      <CaptionsBanner />

      <main className="container" style={{ padding: 'var(--space-6) var(--space-4)' }}>
        <section
          className="card"
          style={{
            maxWidth: '640px',
            margin: '0 auto',
            border: isBlocked ? '2px solid var(--color-risk-critical)' : '1px solid var(--glass-border)',
          }}
          aria-label="Transaction Review and Confirmation"
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
            <span className="label">Step 2 of 2: Review Before Sending</span>
            <button
              type="button"
              onClick={handleReadAloud}
              className="btn btn-secondary"
              style={{ minHeight: '38px', fontSize: 'var(--text-xs)' }}
              aria-label="Read complete transaction details aloud"
            >
              🔊 Read Aloud
            </button>
          </div>

          <h1 style={{ fontSize: 'var(--text-2xl)', marginTop: 'var(--space-1)', marginBottom: 'var(--space-4)' }}>
            Transaction Story
          </h1>

          {/* Transaction Story Banner */}
          <div
            style={{
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-lg)',
              padding: 'var(--space-5)',
              marginBottom: 'var(--space-5)',
            }}
          >
            <div className="label">You are about to transfer:</div>
            <div
              className="amount"
              style={{ fontSize: 'var(--text-4xl)', color: 'var(--color-text)', margin: 'var(--space-2) 0' }}
            >
              ₹{parseFloat(tx.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
            <div style={{ fontSize: 'var(--text-lg)', fontWeight: 600 }}>
              To: <span style={{ color: 'var(--color-primary)' }}>{tx.beneficiary_name || 'Contact'}</span>
            </div>
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: 'var(--space-1)' }}>
              Purpose: {tx.intent} • Direct Mock Bank Transfer
            </div>
          </div>

          {/* Transparent Risk Assessment Section */}
          <div
            style={{
              background: isBlocked ? 'rgba(255, 68, 68, 0.08)' : 'var(--color-surface-2)',
              border: `1px solid ${
                isBlocked
                  ? 'var(--color-risk-critical)'
                  : tx.risk_level === 'HIGH'
                  ? 'var(--color-risk-high)'
                  : tx.risk_level === 'MEDIUM'
                  ? 'var(--color-risk-medium)'
                  : 'var(--color-risk-low)'
              }`,
              borderRadius: 'var(--radius-lg)',
              padding: 'var(--space-4)',
              marginBottom: 'var(--space-6)',
            }}
            role="region"
            aria-label="Security and Risk Assessment"
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div className="label">BankSathi Security Check</div>
              <span
                className={`badge ${
                  isBlocked
                    ? 'badge-critical'
                    : tx.risk_level === 'HIGH'
                    ? 'badge-high'
                    : tx.risk_level === 'MEDIUM'
                    ? 'badge-medium'
                    : 'badge-low'
                }`}
                style={{ fontSize: 'var(--text-xs)', padding: 'var(--space-1) var(--space-3)' }}
              >
                {isBlocked ? '⛔ BLOCKED (Critical Risk)' : `🛡️ ${tx.risk_level || 'LOW'} RISK`}
              </span>
            </div>

            {/* Human-readable risk explanation */}
            <div style={{ marginTop: 'var(--space-3)' }}>
              <div style={{ fontWeight: 700, fontSize: 'var(--text-sm)', marginBottom: 'var(--space-2)' }}>
                {isBlocked
                  ? 'This payment has been blocked for your safety:'
                  : 'Why this security rating was calculated:'}
              </div>

              <ul style={{ paddingLeft: 'var(--space-5)', margin: 0 }}>
                {riskReasons.length > 0 ? (
                  riskReasons.map((reason, idx) => (
                    <li key={idx} style={{ fontSize: 'var(--text-sm)', marginBottom: 'var(--space-1)' }}>
                      {reason}
                    </li>
                  ))
                ) : (
                  <li style={{ fontSize: 'var(--text-sm)' }}>
                    Payment is within your normal transaction parameters.
                  </li>
                )}
              </ul>
            </div>
          </div>

          {/* Trusted Circle Second Opinion Section */}
          {tx.second_opinion?.has_notification && (
            <div
              style={{
                background:
                  tx.second_opinion.response === 'NOT_RECOGNIZED'
                    ? 'rgba(255, 68, 68, 0.12)'
                    : tx.second_opinion.response === 'LOOKS_EXPECTED'
                    ? 'rgba(0, 200, 83, 0.12)'
                    : 'var(--color-surface)',
                border: `2px solid ${
                  tx.second_opinion.response === 'NOT_RECOGNIZED'
                    ? 'var(--color-risk-critical)'
                    : tx.second_opinion.response === 'LOOKS_EXPECTED'
                    ? 'var(--color-risk-low)'
                    : 'var(--color-primary)'
                }`,
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-4)',
                marginBottom: 'var(--space-6)',
              }}
              role="region"
              aria-label="Trusted Circle Second Opinion"
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
                <div className="label">Trusted Circle Second Opinion</div>
                <span
                  className={`badge ${
                    tx.second_opinion.response === 'NOT_RECOGNIZED'
                      ? 'badge-critical'
                      : tx.second_opinion.response === 'LOOKS_EXPECTED'
                      ? 'badge-low'
                      : 'badge-medium'
                  }`}
                >
                  {tx.second_opinion.response === 'LOOKS_EXPECTED'
                    ? '✓ LOOKS EXPECTED'
                    : tx.second_opinion.response === 'NOT_RECOGNIZED'
                    ? '⚠️ NOT RECOGNIZED'
                    : 'WAITING FOR OPINION'}
                </span>
              </div>

              {tx.second_opinion.response === 'LOOKS_EXPECTED' && (
                <div>
                  <div style={{ fontWeight: 700, color: 'var(--color-risk-low)', fontSize: 'var(--text-base)' }}>
                    Your {tx.second_opinion.relationship_label || 'daughter'} ({tx.second_opinion.responder_name || 'Trusted Contact'}) reviewed this and thinks it looks expected.
                  </div>
                  {tx.second_opinion.comment && (
                    <div style={{ fontSize: 'var(--text-sm)', marginTop: 'var(--space-1)', fontStyle: 'italic' }}>
                      "{tx.second_opinion.comment}"
                    </div>
                  )}
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: 'var(--space-2)' }}>
                    Note: This is only a second opinion. You remain 100% responsible for the final authorization decision.
                  </div>
                </div>
              )}

              {tx.second_opinion.response === 'NOT_RECOGNIZED' && (
                <div>
                  <div style={{ fontWeight: 700, color: 'var(--color-risk-critical)', fontSize: 'var(--text-base)' }}>
                    ⚠️ Your {tx.second_opinion.relationship_label || 'trusted person'} does not recognize this payment!
                  </div>
                  <div style={{ fontSize: 'var(--text-sm)', marginTop: 'var(--space-1)' }}>
                    They recommend that you verify the recipient and amount before continuing, or cancel now.
                  </div>
                  {tx.second_opinion.comment && (
                    <div style={{ fontSize: 'var(--text-sm)', marginTop: 'var(--space-1)', fontStyle: 'italic' }}>
                      Comment: "{tx.second_opinion.comment}"
                    </div>
                  )}
                </div>
              )}

              {!tx.second_opinion.response && (
                <div>
                  <div style={{ fontWeight: 600, fontSize: 'var(--text-sm)' }}>
                    🔔 Alert sent to your {tx.second_opinion.relationship_label || 'trusted family member'}.
                  </div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                    You can wait for their second opinion, or proceed on your own authority.
                  </div>
                </div>
              )}
            </div>
          )}

          {errorMsg && (
            <div
              role="alert"
              style={{
                background: 'rgba(255, 68, 68, 0.1)',
                border: '1px solid var(--color-risk-critical)',
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-3)',
                color: 'var(--color-risk-critical)',
                fontWeight: 600,
                marginBottom: 'var(--space-4)',
              }}
            >
              {errorMsg}
            </div>
          )}

          {/* Final Action Buttons (Min 56px touch target) */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {!isBlocked && (
              <button
                type="button"
                onClick={handleConfirm}
                disabled={submitting}
                className="btn btn-primary btn-full"
                style={{
                  minHeight: '64px',
                  fontSize: 'var(--text-xl)',
                  background: 'var(--color-risk-low)',
                  borderColor: 'var(--color-risk-low)',
                }}
                aria-label={`Confirm payment of ₹${tx.amount} to ${tx.beneficiary_name}`}
              >
                {submitting ? 'Executing Transfer...' : `✓ Confirm Payment of ₹${tx.amount}`}
              </button>
            )}

            <button
              type="button"
              onClick={handleCancel}
              disabled={submitting}
              className="btn btn-secondary btn-full"
              style={{ minHeight: '52px' }}
              aria-label="Cancel and return to dashboard"
            >
              {isBlocked ? '← Return to Dashboard' : '✕ Cancel Payment'}
            </button>
          </div>
        </section>
      </main>
    </div>
  )
}
