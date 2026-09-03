/**
 * New Transaction Page — Conversational Voice & Text Transfer
 *
 * Implements:
 * - Natural language input (voice and text)
 * - Real-time AI intent extraction
 * - Clarification questions when input is ambiguous
 * - One-click draft creation and progression to Transaction Review
 */
import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Header } from '../components/Header'
import { CaptionsBanner } from '../components/CaptionsBanner'
import { useAccessibility } from '../context/AccessibilityContext'
import { api, IntentResult, ensureDemoUser } from '../services/api'
import { voice } from '../services/voice'

export const NewTransactionPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { speakWithCaptions } = useAccessibility()

  const [inputQuery, setInputQuery] = useState<string>('')
  const [isListening, setIsListening] = useState<boolean>(false)
  const [parsing, setParsing] = useState<boolean>(false)
  const [parsedIntent, setParsedIntent] = useState<IntentResult | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  // Pre-fill query if passed in URL
  useEffect(() => {
    async function init() {
      await ensureDemoUser()
      const q = searchParams.get('q')
      if (q) {
        setInputQuery(q)
        handleParseIntent(q)
      }
    }
    init()
  }, [searchParams])

  const handleVoiceInput = () => {
    if (isListening) {
      voice.stopListening()
      setIsListening(false)
      return
    }

    speakWithCaptions(
      'Listening. Say your transfer command, for example: Send five thousand rupees to Ravi.',
      'Listening... Speak naturally'
    )

    const started = voice.startListening(
      (transcript, isFinal) => {
        setInputQuery(transcript)
        if (isFinal && transcript.trim()) {
          setIsListening(false)
          handleParseIntent(transcript)
        }
      },
      () => {
        setIsListening(false)
        setErrorMsg('Microphone error or speech not recognized.')
      },
      () => {
        setIsListening(false)
      }
    )

    if (started) {
      setIsListening(true)
      setErrorMsg(null)
    }
  }

  const handleParseIntent = async (text: string) => {
    if (!text.trim()) return

    setParsing(true)
    setErrorMsg(null)
    try {
      const res = await api.parseIntent(text)
      setParsedIntent(res.data)

      if (res.data.clarification_needed && res.data.clarification_question) {
        speakWithCaptions(res.data.clarification_question)
      } else if (res.data.amount && res.data.beneficiary_name) {
        speakWithCaptions(
          `Understood: Sending ${res.data.amount} rupees to ${res.data.beneficiary_name}. Tap Review to continue.`,
          `Understood: ₹${res.data.amount} to ${res.data.beneficiary_name}`
        )
      }
    } catch (err: any) {
      setErrorMsg('Failed to process command. Please try typing.')
    } finally {
      setParsing(false)
    }
  }

  const handleProceedToReview = async () => {
    if (!parsedIntent || !parsedIntent.amount) {
      setErrorMsg('Please specify an amount and recipient first.')
      return
    }

    setParsing(true)
    setErrorMsg(null)
    try {
      // 1. Create draft
      const draftRes = await api.createDraft({
        intent: parsedIntent.intent,
        amount: parsedIntent.amount,
        currency: parsedIntent.currency || 'INR',
        beneficiary_name: parsedIntent.beneficiary_name || 'Recipient',
        raw_input: inputQuery,
      })
      const txId = draftRes.data.id

      // 2. Assess risk
      await api.assessRisk(txId)

      // 3. Navigate to review screen
      navigate(`/transactions/${txId}/review`)
    } catch (err: any) {
      setErrorMsg(err.response?.data?.message || 'Failed to create transaction.')
    } finally {
      setParsing(false)
    }
  }

  const sampleChips = [
    'Send ₹5,000 to Ravi',
    'I want to pay Ravi 5k',
    'Send five thousand rupees to Ravi',
    'Pay electricity bill 1200',
  ]

  return (
    <div className="page gradient-bg">
      <Header />
      <CaptionsBanner />

      <main className="container" style={{ padding: 'var(--space-6) var(--space-4)' }}>
        <section className="card" style={{ maxWidth: '640px', margin: '0 auto' }}>
          <div className="label">Step 1 of 2: Enter Payment Details</div>
          <h1 style={{ fontSize: 'var(--text-2xl)', marginTop: 'var(--space-1)' }}>
            Speak or Type Your Payment
          </h1>
          <p style={{ marginTop: 'var(--space-1)', marginBottom: 'var(--space-4)' }}>
            Our AI assistant understands conversational Hindi & English, number words, and casual phrasing.
          </p>

          {/* Voice Mic Button */}
          <div style={{ textAlign: 'center', margin: 'var(--space-6) 0' }}>
            <button
              type="button"
              onClick={handleVoiceInput}
              className={`btn btn-primary ${isListening ? 'pulse' : ''}`}
              style={{
                minHeight: '80px',
                width: '100%',
                fontSize: 'var(--text-xl)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 'var(--space-3)',
                borderRadius: 'var(--radius-xl)',
              }}
              aria-label={isListening ? 'Stop listening' : 'Start voice input'}
            >
              <span style={{ fontSize: '2rem' }} aria-hidden="true">
                {isListening ? '⏹️' : '🎙️'}
              </span>
              <span>{isListening ? 'Listening... Tap to Stop' : 'Tap & Speak Payment'}</span>
            </button>
          </div>

          {/* Text input alternative */}
          <div style={{ marginBottom: 'var(--space-4)' }}>
            <label htmlFor="tx-input" className="label">
              Or Type Here:
            </label>
            <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
              <input
                id="tx-input"
                type="text"
                className="input"
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleParseIntent(inputQuery)}
                placeholder="e.g. Send five thousand rupees to Ravi"
                style={{ flex: 1 }}
              />
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => handleParseIntent(inputQuery)}
                disabled={parsing || !inputQuery.trim()}
                style={{ minHeight: '48px' }}
              >
                {parsing ? 'Parsing...' : 'Understand'}
              </button>
            </div>
          </div>

          {/* Sample suggestion chips */}
          <div style={{ marginBottom: 'var(--space-6)' }}>
            <div className="label" style={{ marginBottom: 'var(--space-2)' }}>
              Try speaking one of these:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
              {sampleChips.map((chip) => (
                <button
                  key={chip}
                  type="button"
                  onClick={() => {
                    setInputQuery(chip)
                    handleParseIntent(chip)
                  }}
                  className="btn btn-secondary"
                  style={{
                    minHeight: '36px',
                    padding: 'var(--space-1) var(--space-3)',
                    fontSize: 'var(--text-xs)',
                    borderRadius: 'var(--radius-full)',
                  }}
                >
                  "{chip}"
                </button>
              ))}
            </div>
          </div>

          {/* Clarification prompt */}
          {parsedIntent?.clarification_needed && (
            <div
              role="alert"
              style={{
                background: 'rgba(255, 170, 0, 0.1)',
                border: '1px solid var(--color-risk-medium)',
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-4)',
                marginBottom: 'var(--space-4)',
              }}
            >
              <div style={{ fontWeight: 700, color: 'var(--color-risk-medium)', marginBottom: '4px' }}>
                ℹ️ More Information Needed
              </div>
              <div>{parsedIntent.clarification_question}</div>
            </div>
          )}

          {/* Parsed Structure Preview */}
          {parsedIntent && !parsedIntent.clarification_needed && (
            <div
              style={{
                background: 'var(--color-surface)',
                border: '2px solid var(--color-primary)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-4)',
                marginBottom: 'var(--space-6)',
              }}
              role="status"
              aria-label="Parsed payment details"
            >
              <div
                style={{
                  fontSize: 'var(--text-xs)',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  color: 'var(--color-primary)',
                  marginBottom: 'var(--space-2)',
                }}
              >
                ✓ Structured Payment Intent Extracted
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
                <div>
                  <div className="label">Amount</div>
                  <div className="amount" style={{ fontSize: 'var(--text-2xl)', color: 'var(--color-text)' }}>
                    ₹{parsedIntent.amount}
                  </div>
                </div>

                <div>
                  <div className="label">Recipient</div>
                  <div style={{ fontSize: 'var(--text-lg)', fontWeight: 700, marginTop: '4px' }}>
                    {parsedIntent.beneficiary_name || 'None'}
                  </div>
                </div>
              </div>

              <button
                type="button"
                className="btn btn-primary btn-full"
                onClick={handleProceedToReview}
                disabled={parsing}
                style={{
                  minHeight: '56px',
                  fontSize: 'var(--text-lg)',
                  marginTop: 'var(--space-4)',
                }}
              >
                {parsing ? 'Evaluating Risk...' : 'Review & Confirm Payment →'}
              </button>
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
              }}
            >
              {errorMsg}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
