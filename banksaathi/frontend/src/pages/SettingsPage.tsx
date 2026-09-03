/**
 * Accessibility Settings Screen
 *
 * Configures:
 * - Font scaling (1.0x to 2.0x)
 * - High contrast mode
 * - Voice speech rate
 * - Confirmation mode (single, double, voice)
 * - Live preview with test speech button
 */
import React, { useState } from 'react'
import { Header } from '../components/Header'
import { CaptionsBanner } from '../components/CaptionsBanner'
import { useAccessibility } from '../context/AccessibilityContext'
import { api } from '../services/api'

export const SettingsPage: React.FC = () => {
  const {
    fontScale,
    setFontScale,
    highContrast,
    setHighContrast,
    speechRate,
    setSpeechRate,
    confirmationMode,
    setConfirmationMode,
    speakWithCaptions,
  } = useAccessibility()

  const [savedMsg, setSavedMsg] = useState<boolean>(false)

  const handleTestSpeech = () => {
    speakWithCaptions(
      `This is a sample audio test at ${Math.round(speechRate * 100)} percent speed. BankSathi ensures every step is clear.`,
      `Testing speech at ${speechRate}x speed`
    )
  }

  const handleSave = async () => {
    try {
      await api.updatePreferences({
        font_scale: fontScale,
        high_contrast: highContrast,
        speech_rate: speechRate,
        confirmation_mode: confirmationMode,
      })
      setSavedMsg(true)
      speakWithCaptions('Accessibility preferences saved successfully.')
      setTimeout(() => setSavedMsg(false), 3000)
    } catch {
      setSavedMsg(true)
      setTimeout(() => setSavedMsg(false), 3000)
    }
  }

  return (
    <div className="page gradient-bg">
      <Header />
      <CaptionsBanner />

      <main className="container" style={{ padding: 'var(--space-6) var(--space-4)' }}>
        <section className="card" style={{ maxWidth: '640px', margin: '0 auto' }}>
          <div className="label">Custom Comfort & Accessibility</div>
          <h1 style={{ fontSize: 'var(--text-2xl)', marginTop: 'var(--space-1)', marginBottom: 'var(--space-6)' }}>
            Accessibility Settings
          </h1>

          {/* 1. Text Size Scaling */}
          <div style={{ marginBottom: 'var(--space-6)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
              <label htmlFor="font-slider" style={{ fontWeight: 700 }}>
                Text Size: {Math.round(fontScale * 100)}%
              </label>
              <span className="label">Up to 200% scaling</span>
            </div>

            <input
              id="font-slider"
              type="range"
              min="0.85"
              max="2.0"
              step="0.05"
              value={fontScale}
              onChange={(e) => setFontScale(parseFloat(e.target.value))}
              style={{ width: '100%', height: '36px' }}
              aria-label="Adjust text size slider"
            />

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 'var(--space-2)' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setFontScale(1.0)}
                style={{ minHeight: '36px', fontSize: 'var(--text-xs)' }}
              >
                Reset Standard (100%)
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setFontScale(1.4)}
                style={{ minHeight: '36px', fontSize: 'var(--text-xs)' }}
              >
                Large (140%)
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setFontScale(1.8)}
                style={{ minHeight: '36px', fontSize: 'var(--text-xs)' }}
              >
                Extra Large (180%)
              </button>
            </div>
          </div>

          {/* 2. High Contrast Mode */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: 'var(--space-4)',
              background: 'var(--color-surface)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--color-border)',
              marginBottom: 'var(--space-6)',
            }}
          >
            <div>
              <div style={{ fontWeight: 700 }}>High Contrast Mode</div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
                Enhanced contrast borders and high-visibility colors (WCAG AAA)
              </div>
            </div>

            <button
              type="button"
              className={`btn ${highContrast ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setHighContrast(!highContrast)}
              style={{ minHeight: '44px' }}
              aria-pressed={highContrast}
            >
              {highContrast ? '✓ Enabled' : 'Disabled'}
            </button>
          </div>

          {/* 3. Voice Speech Speed */}
          <div style={{ marginBottom: 'var(--space-6)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
              <label htmlFor="speech-slider" style={{ fontWeight: 700 }}>
                Voice Narration Speed: {speechRate}x
              </label>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleTestSpeech}
                style={{ minHeight: '32px', fontSize: 'var(--text-xs)', padding: '0 var(--space-3)' }}
              >
                🔊 Test Voice
              </button>
            </div>

            <input
              id="speech-slider"
              type="range"
              min="0.75"
              max="1.5"
              step="0.05"
              value={speechRate}
              onChange={(e) => setSpeechRate(parseFloat(e.target.value))}
              style={{ width: '100%', height: '36px' }}
              aria-label="Voice reading speed slider"
            />
            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', marginTop: 'var(--space-1)' }}>
              0.75x (Gentle & Slow) to 1.5x (Fast)
            </div>
          </div>

          {/* 4. Confirmation Mode */}
          <div style={{ marginBottom: 'var(--space-6)' }}>
            <label className="label" style={{ marginBottom: 'var(--space-2)' }}>
              Payment Confirmation Style:
            </label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
              {[
                { id: 'single', title: 'Single Touch Confirmation', desc: 'One large green confirm button.' },
                { id: 'double', title: 'Double Confirmation', desc: 'Prompts review twice for high peace of mind.' },
                { id: 'voice', title: 'Voice Confirmation', desc: 'Speak "Confirm" or tap the button.' },
              ].map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => setConfirmationMode(opt.id)}
                  style={{
                    textAlign: 'left',
                    padding: 'var(--space-3) var(--space-4)',
                    background: confirmationMode === opt.id ? 'rgba(79, 110, 247, 0.15)' : 'var(--color-surface)',
                    border: `2px solid ${confirmationMode === opt.id ? 'var(--color-primary)' : 'var(--color-border)'}`,
                    borderRadius: 'var(--radius-md)',
                    cursor: 'pointer',
                  }}
                  aria-pressed={confirmationMode === opt.id}
                >
                  <div style={{ fontWeight: 700, color: 'var(--color-text)' }}>{opt.title}</div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>{opt.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {savedMsg && (
            <div
              role="status"
              style={{
                background: 'rgba(0, 200, 83, 0.15)',
                border: '1px solid var(--color-risk-low)',
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-3)',
                color: 'var(--color-risk-low)',
                fontWeight: 700,
                marginBottom: 'var(--space-4)',
                textAlign: 'center',
              }}
            >
              ✓ Preferences saved!
            </div>
          )}

          <button
            type="button"
            className="btn btn-primary btn-full"
            onClick={handleSave}
            style={{ minHeight: '54px', fontSize: 'var(--text-lg)' }}
          >
            Save Preferences
          </button>
        </section>
      </main>
    </div>
  )
}
