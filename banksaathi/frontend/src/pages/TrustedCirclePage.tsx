/**
 * Trusted Circle & Second Opinion Dashboard
 *
 * Implements the core safety model from BankSathi_Trusted_Circle_Change.md:
 * - "Shared guidance, not shared access"
 * - Zero screen-sharing
 * - Risk-based notification & advisory second opinion
 * - User always retains final authorization decision
 */
import React, { useEffect, useState } from 'react'
import { Header } from '../components/Header'
import { CaptionsBanner } from '../components/CaptionsBanner'
import { useAccessibility } from '../context/AccessibilityContext'
import { api, TrustedCircleMember, TrustedCircleNotification, ensureDemoUser, getCurrentDemoRole } from '../services/api'

export const TrustedCirclePage: React.FC = () => {
  const { speakWithCaptions } = useAccessibility()

  const [activeTab, setActiveTab] = useState<'user' | 'trusted'>(
    getCurrentDemoRole() === 'daughter' ? 'trusted' : 'user'
  )

  // User tab state
  const [members, setMembers] = useState<TrustedCircleMember[]>([])
  const [phoneInput, setPhoneInput] = useState<string>('9999999002')
  const [relationshipInput, setRelationshipInput] = useState<string>('Daughter')
  const [inviting, setInviting] = useState<boolean>(false)
  const [inviteSuccess, setInviteSuccess] = useState<string | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  // Trusted Person tab state
  const [notifications, setNotifications] = useState<TrustedCircleNotification[]>([])
  const [loadingNotifs, setLoadingNotifs] = useState<boolean>(false)
  const [submittingOpinion, setSubmittingOpinion] = useState<string | null>(null)
  const [opinionSuccess, setOpinionSuccess] = useState<string | null>(null)

  useEffect(() => {
    async function init() {
      await ensureDemoUser()
      loadMembers()
      loadNotifications()
    }
    init()
  }, [])

  const loadMembers = async () => {
    try {
      const res = await api.listTrustedMembers()
      setMembers(res.data)
    } catch {
      // Ignored if unauthenticated in preview
    }
  }

  const loadNotifications = async () => {
    setLoadingNotifs(true)
    try {
      const res = await api.listTrustedNotifications()
      setNotifications(res.data)
    } catch {
      // Ignored if unauthenticated in preview
    } finally {
      setLoadingNotifs(false)
    }
  }

  const handleInvite = async () => {
    if (!phoneInput.trim()) return
    setInviting(true)
    setErrorMsg(null)
    setInviteSuccess(null)

    try {
      await api.inviteTrustedMember(phoneInput, relationshipInput)
      setInviteSuccess(`Added ${relationshipInput} (${phoneInput}) to your Trusted Circle!`)
      speakWithCaptions(`Added ${relationshipInput} to your Trusted Circle.`)
      setPhoneInput('')
      await loadMembers()
    } catch (err: any) {
      setErrorMsg(err.response?.data?.message || 'Failed to add trusted member.')
    } finally {
      setInviting(false)
    }
  }

  const handleRevoke = async (memberId: string, label: string) => {
    try {
      await api.revokeTrustedMember(memberId)
      speakWithCaptions(`Revoked ${label} from your Trusted Circle.`)
      await loadMembers()
    } catch {
      setErrorMsg('Failed to revoke member.')
    }
  }

  const handleSubmitOpinion = async (
    notificationId: string,
    decision: 'LOOKS_EXPECTED' | 'NOT_RECOGNIZED' | 'REQUEST_USER_VERIFICATION'
  ) => {
    setSubmittingOpinion(notificationId)
    setOpinionSuccess(null)
    setErrorMsg(null)

    try {
      await api.submitSecondOpinion(notificationId, decision)
      const label = decision === 'LOOKS_EXPECTED' ? 'Looks Expected' : "Don't Recognize This"
      setOpinionSuccess(`Second opinion recorded: "${label}". The user will see this advisory note.`)
      speakWithCaptions(`Second opinion submitted: ${label}. You cannot approve or execute this payment.`)
      await loadNotifications()
    } catch (err: any) {
      setErrorMsg(err.response?.data?.message || 'Failed to submit second opinion.')
    } finally {
      setSubmittingOpinion(null)
    }
  }

  return (
    <div className="page gradient-bg">
      <Header />
      <CaptionsBanner />

      <main className="container" style={{ padding: 'var(--space-6) var(--space-4)' }}>
        <div style={{ maxWidth: '720px', margin: '0 auto' }}>
          {/* Core Principle Banner */}
          <div
            className="card"
            style={{
              background: 'rgba(79, 110, 247, 0.1)',
              border: '2px solid var(--color-primary)',
              marginBottom: 'var(--space-6)',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-4)',
            }}
          >
            <span style={{ fontSize: '2.8rem' }} aria-hidden="true">
              🛡️
            </span>
            <div>
              <div style={{ fontWeight: 800, fontSize: 'var(--text-lg)', color: 'var(--color-primary)' }}>
                Trusted Circle & Second Opinion
              </div>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text)', marginTop: '2px' }}>
                Your trusted family member (daughter, son, spouse) can review unusual payments and provide a{' '}
                <strong>second opinion</strong>. They <strong>NEVER</strong> get access to your OTP, PIN,
                password, or financial control. <strong>No screen sharing is used.</strong>
              </p>
            </div>
          </div>

          {/* Mode Switcher Tabs */}
          <div
            style={{
              display: 'flex',
              gap: 'var(--space-2)',
              marginBottom: 'var(--space-6)',
              background: 'var(--color-surface)',
              padding: 'var(--space-1)',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--color-border)',
            }}
          >
            <button
              type="button"
              className={`btn ${activeTab === 'user' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1, minHeight: '48px' }}
              onClick={() => setActiveTab('user')}
            >
              👵 My Trusted Circle (User View)
            </button>
            <button
              type="button"
              className={`btn ${activeTab === 'trusted' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ flex: 1, minHeight: '48px' }}
              onClick={() => setActiveTab('trusted')}
            >
              🧑‍💻 Trusted Person Dashboard (Advisory View)
            </button>
          </div>

          {/* TAB 1: User Managing Trusted Circle */}
          {activeTab === 'user' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
              {/* Add Member Card */}
              <section className="card" aria-label="Add Member to Trusted Circle">
                <h2 style={{ fontSize: 'var(--text-xl)' }}>Add a Trusted Person</h2>
                <p style={{ marginTop: 'var(--space-1)', marginBottom: 'var(--space-4)' }}>
                  Add a family member who can receive risk alerts when you make an unusual payment.
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
                  <div>
                    <label htmlFor="member-phone" className="label">
                      Mobile Number:
                    </label>
                    <input
                      id="member-phone"
                      type="tel"
                      className="input"
                      value={phoneInput}
                      onChange={(e) => setPhoneInput(e.target.value)}
                      placeholder="e.g. 9876543210"
                    />
                  </div>

                  <div>
                    <label htmlFor="relationship-select" className="label">
                      Relationship:
                    </label>
                    <select
                      id="relationship-select"
                      className="input"
                      value={relationshipInput}
                      onChange={(e) => setRelationshipInput(e.target.value)}
                    >
                      <option value="Daughter">Daughter</option>
                      <option value="Son">Son</option>
                      <option value="Spouse">Spouse</option>
                      <option value="Parent">Parent</option>
                      <option value="Trusted Friend">Trusted Friend</option>
                      <option value="Community Volunteer">Community Volunteer</option>
                    </select>
                  </div>
                </div>

                {inviteSuccess && (
                  <div
                    role="status"
                    style={{
                      background: 'rgba(0, 200, 83, 0.1)',
                      border: '1px solid var(--color-risk-low)',
                      borderRadius: 'var(--radius-md)',
                      padding: 'var(--space-3)',
                      color: 'var(--color-risk-low)',
                      fontWeight: 600,
                      marginBottom: 'var(--space-4)',
                    }}
                  >
                    ✓ {inviteSuccess}
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

                <button
                  type="button"
                  className="btn btn-primary btn-full"
                  onClick={handleInvite}
                  disabled={inviting || !phoneInput}
                  style={{ minHeight: '52px', fontSize: 'var(--text-base)' }}
                >
                  {inviting ? 'Adding...' : `Add ${relationshipInput} to Trusted Circle`}
                </button>
              </section>

              {/* Members List */}
              <section className="card" aria-label="Current Trusted Circle Members">
                <h3 style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--space-3)' }}>
                  Active Trusted Circle ({members.length})
                </h3>

                {members.length === 0 ? (
                  <p style={{ color: 'var(--color-text-muted)', textAlign: 'center', padding: 'var(--space-4)' }}>
                    No members added yet. Add a daughter or son above.
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                    {members.map((m) => (
                      <div
                        key={m.id}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: 'var(--space-3) var(--space-4)',
                          background: 'var(--color-surface)',
                          borderRadius: 'var(--radius-md)',
                          border: '1px solid var(--color-border)',
                        }}
                      >
                        <div>
                          <div style={{ fontWeight: 700, fontSize: 'var(--text-base)' }}>
                            {m.trusted_person_name || m.relationship_label}
                          </div>
                          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                            Relationship: {m.relationship_label} • Status: {m.status.toUpperCase()}
                          </div>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                          <span className="badge badge-low">Verified</span>
                          <button
                            type="button"
                            className="btn btn-secondary"
                            onClick={() => handleRevoke(m.id, m.relationship_label)}
                            style={{ minHeight: '36px', fontSize: 'var(--text-xs)' }}
                          >
                            Revoke
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            </div>
          )}

          {/* TAB 2: Trusted Person Dashboard */}
          {activeTab === 'trusted' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              <section className="card" aria-label="Trusted Person Second Opinion Console">
                <div className="label">Advisory Console</div>
                <h2 style={{ fontSize: 'var(--text-xl)', marginTop: 'var(--space-1)' }}>
                  Transactions Needing Second Opinion
                </h2>
                <p style={{ marginTop: 'var(--space-1)', marginBottom: 'var(--space-4)' }}>
                  When your family member attempts an unusual payment, it appears here for your second opinion.
                  You do <strong>not</strong> approve the payment; you provide an advisory signal.
                </p>

                {opinionSuccess && (
                  <div
                    role="status"
                    style={{
                      background: 'rgba(0, 200, 83, 0.1)',
                      border: '1px solid var(--color-risk-low)',
                      borderRadius: 'var(--radius-md)',
                      padding: 'var(--space-3)',
                      color: 'var(--color-risk-low)',
                      fontWeight: 600,
                      marginBottom: 'var(--space-4)',
                    }}
                  >
                    ✓ {opinionSuccess}
                  </div>
                )}

                {loadingNotifs ? (
                  <div style={{ textAlign: 'center', padding: 'var(--space-6)' }}>
                    <div className="spinner" style={{ margin: '0 auto' }}></div>
                  </div>
                ) : notifications.length === 0 ? (
                  <div
                    style={{
                      textAlign: 'center',
                      padding: 'var(--space-8)',
                      background: 'var(--color-surface)',
                      borderRadius: 'var(--radius-md)',
                      color: 'var(--color-text-muted)',
                    }}
                  >
                    <span style={{ fontSize: '2.5rem' }} aria-hidden="true">
                      ✨
                    </span>
                    <div style={{ marginTop: 'var(--space-2)', fontWeight: 600 }}>
                      All clear! No unusual transactions need your second opinion right now.
                    </div>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                    {notifications.map((n) => (
                      <div
                        key={n.id}
                        style={{
                          background: 'var(--color-surface)',
                          border: `2px solid ${
                            n.risk_level === 'HIGH' || n.risk_level === 'CRITICAL'
                              ? 'var(--color-risk-high)'
                              : 'var(--color-risk-medium)'
                          }`,
                          borderRadius: 'var(--radius-lg)',
                          padding: 'var(--space-4)',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div style={{ fontWeight: 700, fontSize: 'var(--text-lg)' }}>
                            🔔 BankSathi Alert for {n.user_name || 'Family Member'}
                          </div>
                          <span
                            className={`badge ${
                              n.risk_level === 'HIGH' || n.risk_level === 'CRITICAL'
                                ? 'badge-high'
                                : 'badge-medium'
                            }`}
                          >
                            {n.risk_level} RISK
                          </span>
                        </div>

                        <div
                          style={{
                            display: 'grid',
                            gridTemplateColumns: '1fr 1fr',
                            gap: 'var(--space-3)',
                            margin: 'var(--space-3) 0',
                            background: 'var(--color-surface-2)',
                            padding: 'var(--space-3)',
                            borderRadius: 'var(--radius-md)',
                          }}
                        >
                          <div>
                            <div className="label">Amount:</div>
                            <div className="amount" style={{ fontSize: 'var(--text-2xl)' }}>
                              {n.amount_display}
                            </div>
                          </div>
                          <div>
                            <div className="label">Recipient:</div>
                            <div style={{ fontWeight: 700, fontSize: 'var(--text-base)', marginTop: '4px' }}>
                              {n.beneficiary_display}
                            </div>
                          </div>
                        </div>

                        {/* Plain language reasons */}
                        <div style={{ marginBottom: 'var(--space-4)' }}>
                          <div className="label">Why BankSathi flagged this:</div>
                          <ul style={{ paddingLeft: 'var(--space-5)', margin: 'var(--space-1) 0 0 0' }}>
                            {n.risk_reasons?.reasons ? (
                              n.risk_reasons.reasons.map((r, idx) => (
                                <li key={idx} style={{ fontSize: 'var(--text-sm)' }}>
                                  {r}
                                </li>
                              ))
                            ) : (
                              <li style={{ fontSize: 'var(--text-sm)' }}>
                                Amount exceeds user's typical daily transfer baseline.
                              </li>
                            )}
                          </ul>
                        </div>

                        {/* Action buttons if pending */}
                        {n.status === 'pending' ? (
                          <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
                            <button
                              type="button"
                              className="btn btn-primary"
                              onClick={() => handleSubmitOpinion(n.id, 'LOOKS_EXPECTED')}
                              disabled={submittingOpinion === n.id}
                              style={{
                                flex: 1,
                                minHeight: '48px',
                                background: 'var(--color-risk-low)',
                                borderColor: 'var(--color-risk-low)',
                              }}
                            >
                              ✓ Looks Expected
                            </button>
                            <button
                              type="button"
                              className="btn btn-secondary"
                              onClick={() => handleSubmitOpinion(n.id, 'NOT_RECOGNIZED')}
                              disabled={submittingOpinion === n.id}
                              style={{
                                flex: 1,
                                minHeight: '48px',
                                color: 'var(--color-risk-critical)',
                                borderColor: 'var(--color-risk-critical)',
                              }}
                            >
                              ⚠️ Don't Recognize This
                            </button>
                          </div>
                        ) : (
                          <div
                            style={{
                              padding: 'var(--space-2) var(--space-3)',
                              background: 'var(--color-surface-2)',
                              borderRadius: 'var(--radius-md)',
                              fontWeight: 700,
                              fontSize: 'var(--text-sm)',
                              color:
                                n.second_opinion?.response === 'LOOKS_EXPECTED'
                                  ? 'var(--color-risk-low)'
                                  : 'var(--color-risk-critical)',
                            }}
                          >
                            ✓ Second opinion recorded: {n.second_opinion?.response || 'Responded'}
                          </div>
                        )}

                        <div
                          style={{
                            marginTop: 'var(--space-3)',
                            fontSize: 'var(--text-xs)',
                            color: 'var(--color-text-muted)',
                            textAlign: 'center',
                          }}
                        >
                          🔒 Advisory only: Your feedback guides your family member. Only they can authorize payments.
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
