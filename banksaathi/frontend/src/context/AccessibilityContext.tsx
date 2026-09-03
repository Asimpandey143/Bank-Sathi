/**
 * Accessibility Context & State Provider
 *
 * Implements WCAG AAA guidelines:
 * - Dynamic font scaling (applied to CSS custom properties)
 * - High contrast toggle
 * - Screen reader friendly live regions
 * - Synchronous visual captions for audio
 */
import React, { createContext, useContext, useEffect, useState } from 'react'
import { voice } from '../services/voice'

interface AccessibilityContextType {
  fontScale: number
  highContrast: boolean
  speechRate: number
  confirmationMode: string
  activeCaption: string | null
  setFontScale: (scale: number) => void
  setHighContrast: (enabled: boolean) => void
  setSpeechRate: (rate: number) => void
  setConfirmationMode: (mode: string) => void
  speakWithCaptions: (speechText: string, captionText?: string) => void
  clearCaptions: () => void
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined)

export const AccessibilityProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [fontScale, setFontScaleState] = useState<number>(() => {
    const saved = localStorage.getItem('banksaathi_font_scale')
    return saved ? parseFloat(saved) : 1.0
  })

  const [highContrast, setHighContrastState] = useState<boolean>(() => {
    return localStorage.getItem('banksaathi_high_contrast') === 'true'
  })

  const [speechRate, setSpeechRateState] = useState<number>(() => {
    const saved = localStorage.getItem('banksaathi_speech_rate')
    return saved ? parseFloat(saved) : 1.0
  })

  const [confirmationMode, setConfirmationModeState] = useState<string>('single')
  const [activeCaption, setActiveCaption] = useState<string | null>(null)

  // Apply CSS custom properties and attributes to document root
  useEffect(() => {
    const root = document.documentElement
    root.style.setProperty('--font-scale', String(fontScale))
    localStorage.setItem('banksaathi_font_scale', String(fontScale))
  }, [fontScale])

  useEffect(() => {
    const root = document.documentElement
    if (highContrast) {
      root.setAttribute('data-high-contrast', 'true')
    } else {
      root.removeAttribute('data-high-contrast')
    }
    localStorage.setItem('banksaathi_high_contrast', String(highContrast))
  }, [highContrast])

  const setFontScale = (scale: number) => {
    setFontScaleState(scale)
  }

  const setHighContrast = (enabled: boolean) => {
    setHighContrastState(enabled)
  }

  const setSpeechRate = (rate: number) => {
    setSpeechRateState(rate)
    localStorage.setItem('banksaathi_speech_rate', String(rate))
  }

  const setConfirmationMode = (mode: string) => {
    setConfirmationModeState(mode)
  }

  const speakWithCaptions = (speechText: string, captionText?: string) => {
    const caption = captionText || speechText
    setActiveCaption(caption)

    voice.speak(
      speechText,
      speechRate,
      () => setActiveCaption(caption),
      () => {
        // Keep caption visible for 2 seconds after speech completes
        setTimeout(() => setActiveCaption(null), 2500)
      }
    )
  }

  const clearCaptions = () => {
    voice.cancelSpeech()
    setActiveCaption(null)
  }

  return (
    <AccessibilityContext.Provider
      value={{
        fontScale,
        highContrast,
        speechRate,
        confirmationMode,
        activeCaption,
        setFontScale,
        setHighContrast,
        setSpeechRate,
        setConfirmationMode,
        speakWithCaptions,
        clearCaptions,
      }}
    >
      {children}
    </AccessibilityContext.Provider>
  )
}

export const useAccessibility = (): AccessibilityContextType => {
  const context = useContext(AccessibilityContext)
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider')
  }
  return context
}
