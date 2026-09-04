/**
 * BankSathi Conversational Voice Assistant Modal
 *
 * Integrated from EchoDrive Real-Time Voice Runtime:
 * - Center-Stage Animated Voice Orb with responsive glow states
 *   (IDLE, LISTENING, THINKING, SPEAKING, INTERRUPTING, ACKNOWLEDGING)
 * - Acoustic Self-Echo Isolation & Deterministic Barge-In
 * - Bilingual support: English (en-IN) and Hindi (hi-IN)
 * - Groq LLM Intent & Slot Filling (Balance, Transfer, Bills, Recents)
 * - Large WCAG AAA Typography & Instant Captions
 */

import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { voice, VoiceState } from '../services/voice'
import { api } from '../services/api'
import { IntentResponse } from '../types'

// Clean inline SVG icons for zero external dependencies
const GlobeIcon: React.FC<{ size?: number }> = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <line x1="2" y1="12" x2="22" y2="12" />
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
  </svg>
)

const CloseIcon: React.FC<{ size?: number }> = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
)

const CheckCircleIcon: React.FC<{ size?: number; color?: string }> = ({ size = 24, color = '#38bdf8' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
    <polyline points="22 4 12 14.01 9 11.01" />
  </svg>
)

const ArrowRightIcon: React.FC<{ size?: number }> = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12" />
    <polyline points="12 5 19 12 12 19" />
  </svg>
)

interface VoiceAssistantModalProps {
  isOpen: boolean
  onClose: () => void
}

export const VoiceAssistantModal: React.FC<VoiceAssistantModalProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate()
  const [voiceState, setVoiceState] = useState<VoiceState>('IDLE')
  const [lang, setLang] = useState<'en-IN' | 'hi-IN'>('en-IN')
  const [transcript, setTranscript] = useState<string>('')
  const [assistantReply, setAssistantReply] = useState<string>('')
  const [lastIntent, setLastIntent] = useState<IntentResponse | null>(null)
  const [balanceDisplay, setBalanceDisplay] = useState<string | null>(null)
  const [clarificationSlot, setClarificationSlot] = useState<{ payee?: string; amount?: number } | null>(null)
  const isProcessingRef = useRef<boolean>(false)

  useEffect(() => {
    if (!isOpen) {
      voice.stopListening()
      voice.cancelSpeech()
      setVoiceState('IDLE')
      setTranscript('')
      setAssistantReply('')
      setLastIntent(null)
      setBalanceDisplay(null)
      setClarificationSlot(null)
      isProcessingRef.current = false
      return
    }

    // Modal Opened: initialize voice runtime
    voice.setLanguage(lang)
    voice.onStateChange((st) => setVoiceState(st))

    const welcomeMsg =
      lang === 'hi-IN'
        ? 'नमस्ते! मैं आपका बैंक-साथी हूँ। आप पैसे भेजने या बैलेंस जानने के लिए बोल सकते हैं।'
        : 'Namaste! I am your Bank-Sathi assistant. How can I help you today?'

    setAssistantReply(welcomeMsg)

    // Speak welcome, then start continuous listening
    voice.speak(
      welcomeMsg,
      0.95,
      () => {},
      () => {
        startListeningLoop()
      }
    )

    return () => {
      voice.stopListening()
      voice.cancelSpeech()
    }
  }, [isOpen, lang])

  const startListeningLoop = () => {
    voice.startContinuousSession(
      (interim) => {
        setTranscript(interim)
      },
      (finalText) => {
        setTranscript(finalText)
        handleUserSpeechTurn(finalText)
      },
      (err) => {
        console.warn('Voice session error:', err)
      }
    )
  }

  const handleUserSpeechTurn = async (userText: string) => {
    if (!userText.trim() || isProcessingRef.current) return
    isProcessingRef.current = true
    voice.setState('THINKING')

    try {
      // 1. Check if user is answering a clarification slot (e.g. they previously said "Send to Ravi" and now say "500")
      let queryText = userText
      if (clarificationSlot?.payee && !clarificationSlot?.amount) {
        queryText = `Send ${userText} to ${clarificationSlot.payee}`
      }

      // 2. Call backend Groq LLM intent parser
      const res = await api.parseIntent(queryText)
      const intentData: IntentResponse = res.data
      setLastIntent(intentData)

      // 3. Process Intent logic
      if (intentData.intent === 'CHECK_BALANCE') {
        const balText =
          lang === 'hi-IN'
            ? 'आपके स्टेट बैंक ऑफ़ इंडिया खाते में ₹50,000 की राशि उपलब्ध है।'
            : 'Your State Bank of India account balance is ₹50,000.'
        setBalanceDisplay('₹50,000.00')
        setAssistantReply(balText)
        voice.speak(balText, 0.95)
      } else if (intentData.intent === 'TRANSFER') {
        if (intentData.clarification_needed || (!intentData.amount && intentData.beneficiary_name)) {
          // Missing amount or payee
          const payee = intentData.beneficiary_name || clarificationSlot?.payee || ''
          setClarificationSlot({ payee })

          const askText =
            lang === 'hi-IN'
              ? `${payee} जी को आप कितने रुपये भेजना चाहते हैं?`
              : `How much money would you like to send to ${payee}?`

          setAssistantReply(askText)
          voice.speak(askText, 0.95)
        } else if (intentData.amount && intentData.beneficiary_name) {
          // Both amount and beneficiary resolved!
          setClarificationSlot(null)
          const confirmText =
            lang === 'hi-IN'
              ? `${intentData.beneficiary_name} जी को ₹${intentData.amount} भेजने की तैयारी कर रहे हैं।`
              : `Preparing to transfer ₹${intentData.amount} to ${intentData.beneficiary_name}. Taking you to review.`

          setAssistantReply(confirmText)
          voice.speak(
            confirmText,
            0.95,
            () => {},
            () => {
              // Auto-navigate to payment review with filled fields
              setTimeout(() => {
                onClose()
                navigate(
                  `/transactions/new?beneficiary=${encodeURIComponent(
                    intentData.beneficiary_name || ''
                  )}&amount=${intentData.amount}`
                )
              }, 1000)
            }
          )
        } else {
          // Generic transfer request
          const askGeneral =
            lang === 'hi-IN'
              ? 'आप किसको और कितने रुपये भेजना चाहते हैं? जैसे: रवि को पाँच सौ रुपये भेजो।'
              : 'Who would you like to pay and how much? For example: Send 500 to Ravi.'
          setAssistantReply(askGeneral)
          voice.speak(askGeneral, 0.95)
        }
      } else if (intentData.intent === 'LIST_TRANSACTIONS') {
        const historyText =
          lang === 'hi-IN'
            ? 'आपके हाल के 3 लेनदेन: किराना स्टोर ₹450, मेडिकल स्टोर ₹1,200, और बिजली बिल ₹1,800।'
            : 'You made 3 recent transactions: Grocery Store ₹450, Pharmacy ₹1,200, and Electricity ₹1,800.'
        setAssistantReply(historyText)
        voice.speak(historyText, 0.95)
      } else if (intentData.intent === 'HELP') {
        const helpText =
          lang === 'hi-IN'
            ? 'आप बोल सकते हैं: मेरा बैलेंस बताओ, शर्मा जी को 500 रुपये भेजो, या हाल के लेनदेन दिखाओ।'
            : 'You can say: Check my balance, Send 500 rupees to Ravi, or Show recent transactions.'
        setAssistantReply(helpText)
        voice.speak(helpText, 0.95)
      } else if (intentData.intent === 'CANCEL') {
        const cancelText = lang === 'hi-IN' ? 'ठीक है, रद्द कर दिया।' : 'Cancelled. Let me know if you need anything else.'
        setAssistantReply(cancelText)
        voice.speak(cancelText, 0.95, () => {}, () => onClose())
      } else {
        const fallbackText =
          intentData.clarification_question ||
          (lang === 'hi-IN'
            ? 'माफ़ कीजिए, मैं समझ नहीं पाया। आप बोल सकते हैं: बैलेंस बताओ या पैसे भेजो।'
            : "I didn't quite catch that. You can say 'Check balance' or 'Send 500 rupees to Ravi'.")
        setAssistantReply(fallbackText)
        voice.speak(fallbackText, 0.95)
      }
    } catch (err) {
      console.error('[VoiceModal] Intent processing error:', err)
      const errText =
        lang === 'hi-IN'
          ? 'नेटवर्क में रुकावट आई है, कृपया दोबारा बोलें।'
          : 'Network interruption. Please speak your command again.'
      setAssistantReply(errText)
      voice.speak(errText, 0.95)
    } finally {
      isProcessingRef.current = false
    }
  }

  const handleOrbClick = () => {
    if (voiceState === 'SPEAKING') {
      voice.handleBargeIn()
    } else if (voiceState === 'LISTENING') {
      voice.stopListening()
    } else {
      startListeningLoop()
    }
  }

  const toggleLanguage = () => {
    const nextLang = lang === 'en-IN' ? 'hi-IN' : 'en-IN'
    setLang(nextLang)
    voice.setLanguage(nextLang)
  }

  if (!isOpen) return null

  // Orb Styling according to EchoDrive real-time state machine
  const getOrbStateClass = () => {
    switch (voiceState) {
      case 'LISTENING':
        return 'orb-listening'
      case 'THINKING':
        return 'orb-thinking'
      case 'SPEAKING':
        return 'orb-speaking'
      case 'INTERRUPTING':
      case 'ACKNOWLEDGING':
        return 'orb-acknowledging'
      default:
        return 'orb-idle'
    }
  }

  const getStateLabel = () => {
    switch (voiceState) {
      case 'LISTENING':
        return lang === 'hi-IN' ? 'सुन रहा हूँ...' : 'Listening...'
      case 'THINKING':
        return lang === 'hi-IN' ? 'सोच रहा हूँ...' : 'Processing...'
      case 'SPEAKING':
        return lang === 'hi-IN' ? 'बोल रहा हूँ...' : 'Speaking...'
      case 'INTERRUPTING':
      case 'ACKNOWLEDGING':
        return lang === 'hi-IN' ? 'ठीक है, सुन रहा हूँ...' : 'OK, listening...'
      default:
        return lang === 'hi-IN' ? 'तैयार' : 'Tap to speak'
    }
  }

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        background: 'rgba(7, 9, 14, 0.88)',
        backdropFilter: 'blur(16px)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '2rem 1.5rem',
        color: '#ffffff',
        animation: 'fadeIn 0.25s ease-out',
      }}
      role="dialog"
      aria-modal="true"
      aria-label="Bank-Sathi Conversational Voice Assistant"
    >
      {/* ── Top Bar ───────────────────────────────────────────────────────── */}
      <header
        style={{
          width: '100%',
          maxWidth: '650px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              background:
                voiceState === 'LISTENING'
                  ? '#38bdf8'
                  : voiceState === 'SPEAKING'
                  ? '#00f2fe'
                  : voiceState === 'THINKING'
                  ? '#fbbf24'
                  : '#94a3b8',
              boxShadow:
                voiceState === 'LISTENING' || voiceState === 'SPEAKING' ? '0 0 12px #38bdf8' : 'none',
              transition: 'all 0.3s ease',
            }}
          />
          <span style={{ fontSize: '0.88rem', fontWeight: 600, letterSpacing: '0.5px', textTransform: 'uppercase' }}>
            {getStateLabel()}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* Language Switcher */}
          <button
            onClick={toggleLanguage}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.4rem 0.85rem',
              borderRadius: '999px',
              background: 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              color: '#ffffff',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
            aria-label="Toggle language between English and Hindi"
          >
            <GlobeIcon size={15} />
            {lang === 'en-IN' ? 'English' : 'हिन्दी'}
          </button>

          {/* Close Modal */}
          <button
            onClick={onClose}
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              background: 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
            }}
            aria-label="Close voice assistant"
          >
            <CloseIcon size={20} />
          </button>
        </div>
      </header>

      {/* ── Center Stage: EchoDrive Interactive Orb ────────────────────────── */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          flex: 1,
          width: '100%',
          maxWidth: '650px',
          margin: '1.5rem 0',
        }}
      >
        {/* Pulsating Orb */}
        <div
          onClick={handleOrbClick}
          className={`voice-orb-wrapper ${getOrbStateClass()}`}
          style={{
            cursor: 'pointer',
            position: 'relative',
            width: '180px',
            height: '180px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '50%',
            marginBottom: '2rem',
            transition: 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)',
          }}
          title="Click to interrupt or speak"
        >
          <div className="voice-orb-core" />
          <div className="voice-orb-glow" />
        </div>

        {/* Live User Interim Transcript */}
        {transcript && (
          <div
            style={{
              fontSize: '1.15rem',
              color: '#94a3b8',
              fontStyle: 'italic',
              marginBottom: '0.75rem',
              textAlign: 'center',
              maxWidth: '90%',
              lineHeight: 1.4,
            }}
          >
            "{transcript}"
          </div>
        )}

        {/* Spoken AI Response (Large WCAG AAA Captions) */}
        <div
          style={{
            fontSize: '1.35rem',
            fontWeight: 500,
            color: '#f8fafc',
            textAlign: 'center',
            maxWidth: '90%',
            minHeight: '3.5rem',
            lineHeight: 1.5,
          }}
        >
          {assistantReply}
        </div>

        {/* Balance Card Quick Display */}
        {balanceDisplay && (
          <div
            style={{
              marginTop: '1.25rem',
              padding: '1rem 1.5rem',
              borderRadius: '16px',
              background: 'rgba(26, 115, 232, 0.15)',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              animation: 'fadeIn 0.3s ease',
            }}
          >
            <CheckCircleIcon size={28} color="#38bdf8" />
            <div>
              <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>State Bank of India (••4321)</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#38bdf8' }}>{balanceDisplay}</div>
            </div>
          </div>
        )}

        {/* Resolved Transfer Card */}
        {lastIntent && lastIntent.intent === 'TRANSFER' && lastIntent.amount && lastIntent.beneficiary_name && (
          <div
            style={{
              marginTop: '1.25rem',
              padding: '1rem 1.5rem',
              borderRadius: '16px',
              background: 'rgba(16, 185, 129, 0.15)',
              border: '1px solid rgba(16, 185, 129, 0.35)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '1rem',
              width: '100%',
              maxWidth: '420px',
              animation: 'fadeIn 0.3s ease',
            }}
          >
            <div>
              <div style={{ fontSize: '0.85rem', color: '#a7f3d0' }}>Recipient: {lastIntent.beneficiary_name}</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#34d399' }}>₹{lastIntent.amount}</div>
            </div>
            <button
              onClick={() => {
                onClose()
                navigate(
                  `/transactions/new?beneficiary=${encodeURIComponent(
                    lastIntent.beneficiary_name || ''
                  )}&amount=${lastIntent.amount}`
                )
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.6rem 1.1rem',
                borderRadius: '999px',
                background: '#10b981',
                color: '#ffffff',
                border: 'none',
                fontWeight: 700,
                fontSize: '0.9rem',
                cursor: 'pointer',
              }}
            >
              Continue <ArrowRightIcon size={16} />
            </button>
          </div>
        )}
      </div>

      {/* ── Bottom Section: Quick Voice Chips & Barge-In Hint ──────────────── */}
      <footer
        style={{
          width: '100%',
          maxWidth: '650px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '0.85rem',
        }}
      >
        <div style={{ fontSize: '0.8rem', color: '#64748b', textAlign: 'center' }}>
          💡 {lang === 'hi-IN' ? 'बोलने के दौरान कभी भी रोक सकते हैं (Barge-in enabled)' : 'Speak anytime to interrupt'}
        </div>

        {/* Vernacular Quick Chips */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: '0.5rem',
          }}
        >
          <button
            onClick={() => handleUserSpeechTurn(lang === 'hi-IN' ? 'मेरा बैलेंस बताओ' : 'Check my account balance')}
            style={chipStyle}
          >
            💰 {lang === 'hi-IN' ? 'बैलेंस चेक करें' : 'Check balance'}
          </button>
          <button
            onClick={() => handleUserSpeechTurn(lang === 'hi-IN' ? 'रवि को पाँच सौ रुपये भेजो' : 'Send 500 rupees to Ravi')}
            style={chipStyle}
          >
            💸 {lang === 'hi-IN' ? 'रवि को ₹500 भेजो' : 'Send ₹500 to Ravi'}
          </button>
          <button
            onClick={() => handleUserSpeechTurn(lang === 'hi-IN' ? 'हाल के लेनदेन दिखाओ' : 'Show recent transactions')}
            style={chipStyle}
          >
            📜 {lang === 'hi-IN' ? 'हाल के लेनदेन' : 'Recent transactions'}
          </button>
          <button
            onClick={() => handleUserSpeechTurn(lang === 'hi-IN' ? 'सहायता' : 'Help')}
            style={chipStyle}
          >
            ❓ {lang === 'hi-IN' ? 'सहायता' : 'Help'}
          </button>
        </div>
      </footer>
    </div>
  )
}

const chipStyle: React.CSSProperties = {
  padding: '0.5rem 1rem',
  borderRadius: '999px',
  background: 'rgba(255, 255, 255, 0.08)',
  border: '1px solid rgba(255, 255, 255, 0.15)',
  color: '#e2e8f0',
  fontSize: '0.85rem',
  fontWeight: 500,
  cursor: 'pointer',
  transition: 'all 0.2s ease',
}
