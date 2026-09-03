/**
 * Transaction Result & Receipt Screen
 *
 * Shows:
 * - Clear confirmation with visual icon + text badge
 * - Mock bank reference ID
 * - Spoken receipt readout
 * - Return to dashboard
 */
import React, { useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Header } from '../components/Header'
import { CaptionsBanner } from '../components/CaptionsBanner'
import { useAccessibility } from '../context/AccessibilityContext'
import { Transaction } from '../services/api'

export const TransactionResultPage: React.FC = () => {
  const location = useLocation()
  const { speakWithCaptions } = useAccessibility()

  const tx: Transaction | undefined = location.state?.transaction

  useEffect(() => {
    if (tx) {
      const statusText =
        tx.status === 'COMPLETED'
          ? `Payment of ${tx.amount} rupees to ${tx.beneficiary_name} was successful. Bank reference is ${tx.bank_reference}.`
          : `Payment failed. ${tx.status}`
      speakWithCaptions(statusText, `Receipt: ${tx.status} - Ref: ${tx.bank_reference || 'N/A'}`)
    }
  }, [tx])

  if (!tx) {
    return (
      <div className="page gradient-bg">
        <Header />
        <main className="container" style={{ padding: 'var(--space-8)', textAlign: 'center' }}>
          <div className="card" style={{ maxWidth: '500px', margin: '0 auto' }}>
            <h2>Transaction Summary</h2>
            <Link to="/dashboard" className="btn btn-primary" style={{ marginTop: 'var(--space-4)' }}>
              Go to Dashboard
            </Link>
          </div>
        </main>
      </div>
    )
  }

  const isSuccess = tx.status === 'COMPLETED'

  return (
    <div className="page gradient-bg">
      <Header />
      <CaptionsBanner />

      <main className="container" style={{ padding: 'var(--space-8) var(--space-4)' }}>
        <section
          className="card"
          style={{
            maxWidth: '560px',
            margin: '0 auto',
            textAlign: 'center',
            border: `2px solid ${isSuccess ? 'var(--color-risk-low)' : 'var(--color-risk-critical)'}`,
          }}
          aria-label="Transaction Receipt"
        >
          {/* Status Icon */}
          <div style={{ fontSize: '4rem', marginBottom: 'var(--space-2)' }} aria-hidden="true">
            {isSuccess ? '✅' : '❌'}
          </div>

          <span
            className={`badge ${isSuccess ? 'badge-low' : 'badge-critical'}`}
            style={{ fontSize: 'var(--text-sm)', padding: 'var(--space-1) var(--space-4)' }}
          >
            {isSuccess ? 'PAYMENT SUCCESSFUL' : 'PAYMENT FAILED'}
          </span>

          <h1 style={{ fontSize: 'var(--text-3xl)', marginTop: 'var(--space-4)' }}>
            ₹{parseFloat(tx.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </h1>

          <p style={{ fontSize: 'var(--text-lg)', fontWeight: 600, color: 'var(--color-text)' }}>
            Transferred to {tx.beneficiary_name || 'Beneficiary'}
          </p>

          {/* Receipt Info Box */}
          <div
            style={{
              background: 'var(--color-surface)',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--color-border)',
              padding: 'var(--space-4)',
              margin: 'var(--space-6) 0',
              textAlign: 'left',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-2)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="label">Bank Reference:</span>
              <span style={{ fontWeight: 700, fontFamily: 'monospace' }}>{tx.bank_reference || 'N/A'}</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="label">Date & Time:</span>
              <span style={{ fontWeight: 600 }}>{new Date().toLocaleString()}</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="label">Security Level:</span>
              <span style={{ fontWeight: 600 }}>{tx.risk_level || 'LOW'}</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="label">Payment Purpose:</span>
              <span style={{ fontWeight: 600 }}>{tx.intent}</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            <button
              type="button"
              className="btn btn-secondary btn-full"
              style={{ minHeight: '48px' }}
              onClick={() => {
                const statusText = `Payment of ${tx.amount} rupees to ${tx.beneficiary_name} was successful. Bank reference is ${tx.bank_reference}.`
                speakWithCaptions(statusText)
              }}
            >
              🔊 Read Receipt Aloud
            </button>

            <Link
              to="/dashboard"
              className="btn btn-primary btn-full"
              style={{ minHeight: '56px', fontSize: 'var(--text-lg)' }}
            >
              Return to Dashboard
            </Link>
          </div>
        </section>
      </main>
    </div>
  )
}
