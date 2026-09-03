/**
 * Onboarding & Accessibility Personalization Screen
 *
 * Sets up user's accessibility profile on first launch.
 */
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Header } from '../components/Header'
import { CaptionsBanner } from '../components/CaptionsBanner'
import { useAccessibility } from '../context/AccessibilityContext'
import { api, ensureDemoUser } from '../services/api'

export const OnboardingPage: React.FC = () => {
  const navigate = useNavigate()
  const { setFontScale, setHighContrast, speakWithCaptions } = useAccessibility()

  const [step, setStep] = useState<number>(1)
  const [selectedLanguage, setSelectedLanguage] = useState<string>('en')
  const [textSizeChoice, setTextSizeChoice] = useState<number>(1.2)
  const [contrastChoice, setContrastChoice] = useState<boolean>(false)

  const handleFinish = async () => {
    try {
      await ensureDemoUser()
      setFontScale(textSizeChoice)
      setHighContrast(contrastChoice)
      await api.updatePreferences({
        language: selectedLanguage,
        font_scale: textSizeChoice,
        high_contrast: contrastChoice,
      })
      speakWithCaptions('Welcome to BankSathi! Your personalized accessible banking is ready.')
      navigate('/dashboard')
    } catch {
      navigate('/dashboard')
    }
  }

  return (
    <div className="page gradient-bg">
      <Header />
      <CaptionsBanner />

      <main className="container" style={{ padding: 'var(--space-8) var(--space-4)' }}>
        <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
          <div className="label">Step {step} of 3: Setup Comfort & Accessibility</div>

          {step === 1 && (
            <div>
              <h1 style={{ fontSize: 'var(--text-2xl)', marginTop: 'var(--space-2)' }}>
                Choose Your Preferred Language
              </h1>
              <p style={{ marginTop: 'var(--space-1)', marginBottom: 'var(--space-6)' }}>
                BankSathi supports voice guidance and simple words in your native tongue.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)', marginBottom: 'var(--space-6)' }}>
                {[
                  { code: 'en', label: 'English' },
                  { code: 'hi', label: 'हिन्दी (Hindi)' },
                  { code: 'mr', label: 'मराठी (Marathi)' },
                  { code: 'gu', label: 'ગુજરાતી (Gujarati)' },
                  { code: 'bn', label: 'বাংলা (Bengali)' },
                  { code: 'ta', label: 'தமிழ் (Tamil)' },
                ].map((lang) => (
                  <button
                    key={lang.code}
                    type="button"
                    onClick={() => setSelectedLanguage(lang.code)}
                    style={{
                      minHeight: '60px',
                      padding: 'var(--space-3)',
                      background: selectedLanguage === lang.code ? 'rgba(79, 110, 247, 0.15)' : 'var(--color-surface)',
                      border: `2px solid ${selectedLanguage === lang.code ? 'var(--color-primary)' : 'var(--color-border)'}`,
                      borderRadius: 'var(--radius-md)',
                      fontSize: 'var(--text-base)',
                      fontWeight: 700,
                      color: 'var(--color-text)',
                      cursor: 'pointer',
                    }}
                    aria-pressed={selectedLanguage === lang.code}
                  >
                    {lang.label}
                  </button>
                ))}
              </div>

              <button
                type="button"
                className="btn btn-primary btn-full"
                onClick={() => setStep(2)}
                style={{ minHeight: '56px', fontSize: 'var(--text-lg)' }}
              >
                Continue →
              </button>
            </div>
          )}

          {step === 2 && (
            <div>
              <h1 style={{ fontSize: 'var(--text-2xl)', marginTop: 'var(--space-2)' }}>
                Choose Your Comfortable Text Size
              </h1>
              <p style={{ marginTop: 'var(--space-1)', marginBottom: 'var(--space-6)' }}>
                Select a size that is effortless for you to read on any screen.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', marginBottom: 'var(--space-6)' }}>
                {[
                  { scale: 1.0, label: 'Standard Text', sample: 'Sample text at 100%' },
                  { scale: 1.3, label: 'Large Text (Recommended)', sample: 'Sample text at 130%' },
                  { scale: 1.6, label: 'Extra Large Text', sample: 'Sample text at 160%' },
                ].map((opt) => (
                  <button
                    key={opt.scale}
                    type="button"
                    onClick={() => {
                      setTextSizeChoice(opt.scale)
                      setFontScale(opt.scale)
                    }}
                    style={{
                      textAlign: 'left',
                      padding: 'var(--space-4)',
                      background: textSizeChoice === opt.scale ? 'rgba(79, 110, 247, 0.15)' : 'var(--color-surface)',
                      border: `2px solid ${textSizeChoice === opt.scale ? 'var(--color-primary)' : 'var(--color-border)'}`,
                      borderRadius: 'var(--radius-md)',
                      cursor: 'pointer',
                    }}
                    aria-pressed={textSizeChoice === opt.scale}
                  >
                    <div style={{ fontSize: `${opt.scale}rem`, fontWeight: 700, color: 'var(--color-text)' }}>
                      {opt.label}
                    </div>
                    <div style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)' }}>{opt.sample}</div>
                  </button>
                ))}
              </div>

              <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setStep(1)}
                  style={{ minHeight: '56px', flex: 1 }}
                >
                  ← Back
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => setStep(3)}
                  style={{ minHeight: '56px', flex: 2, fontSize: 'var(--text-lg)' }}
                >
                  Continue →
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div>
              <h1 style={{ fontSize: 'var(--text-2xl)', marginTop: 'var(--space-2)' }}>
                High Contrast Display
              </h1>
              <p style={{ marginTop: 'var(--space-1)', marginBottom: 'var(--space-6)' }}>
                Would you like extra bold contrast with stark dark backgrounds and bright text?
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)', marginBottom: 'var(--space-6)' }}>
                <button
                  type="button"
                  onClick={() => {
                    setContrastChoice(false)
                    setHighContrast(false)
                  }}
                  style={{
                    minHeight: '80px',
                    padding: 'var(--space-4)',
                    background: !contrastChoice ? 'rgba(79, 110, 247, 0.15)' : 'var(--color-surface)',
                    border: `2px solid ${!contrastChoice ? 'var(--color-primary)' : 'var(--color-border)'}`,
                    borderRadius: 'var(--radius-md)',
                    cursor: 'pointer',
                  }}
                  aria-pressed={!contrastChoice}
                >
                  <div style={{ fontSize: 'var(--text-lg)', fontWeight: 700 }}>☀️ Standard</div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>Modern dark slate</div>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setContrastChoice(true)
                    setHighContrast(true)
                  }}
                  style={{
                    minHeight: '80px',
                    padding: 'var(--space-4)',
                    background: contrastChoice ? 'rgba(79, 110, 247, 0.15)' : 'var(--color-surface)',
                    border: `2px solid ${contrastChoice ? 'var(--color-primary)' : 'var(--color-border)'}`,
                    borderRadius: 'var(--radius-md)',
                    cursor: 'pointer',
                  }}
                  aria-pressed={contrastChoice}
                >
                  <div style={{ fontSize: 'var(--text-lg)', fontWeight: 700 }}>🌓 High Contrast</div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>WCAG AAA bold</div>
                </button>
              </div>

              <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setStep(2)}
                  style={{ minHeight: '56px', flex: 1 }}
                >
                  ← Back
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={handleFinish}
                  style={{ minHeight: '56px', flex: 2, fontSize: 'var(--text-lg)' }}
                >
                  ✓ Enter BankSathi
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
