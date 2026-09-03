/**
 * Web Speech API Service
 *
 * Provides:
 * - Speech recognition (STT) via webkitSpeechRecognition / SpeechRecognition
 * - Speech synthesis (TTS) with rate and pitch control
 * - Visual caption callback for WCAG AAA synchronization
 */

// Browser Web Speech recognition interface
declare global {
  interface Window {
    SpeechRecognition?: any
    webkitSpeechRecognition?: any
  }
}

export class VoiceService {
  private recognition: any = null
  private isListening = false

  constructor() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRec) {
      this.recognition = new SpeechRec()
      this.recognition.continuous = false
      this.recognition.interimResults = true
      this.recognition.lang = 'en-IN'
    }
  }

  isSupported(): boolean {
    return this.recognition !== null
  }

  startListening(
    onResult: (text: string, isFinal: boolean) => void,
    onError: (err: any) => void,
    onEnd: () => void
  ): boolean {
    if (!this.recognition) {
      onError('Speech recognition not supported in this browser.')
      return false
    }

    if (this.isListening) {
      this.recognition.stop()
    }

    this.recognition.onresult = (event: any) => {
      let transcript = ''
      let isFinal = false
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        transcript += event.results[i][0].transcript
        if (event.results[i].isFinal) {
          isFinal = true
        }
      }
      onResult(transcript, isFinal)
    }

    this.recognition.onerror = (event: any) => {
      this.isListening = false
      onError(event.error)
    }

    this.recognition.onend = () => {
      this.isListening = false
      onEnd()
    }

    try {
      this.recognition.start()
      this.isListening = true
      return true
    } catch (err) {
      this.isListening = false
      onError(err)
      return false
    }
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop()
      this.isListening = false
    }
  }

  speak(text: string, rate = 1.0, onStart?: () => void, onEnd?: () => void) {
    if (!('speechSynthesis' in window)) return

    window.speechSynthesis.cancel() // Stop any current speech
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = rate
    utterance.lang = 'en-IN'

    if (onStart) utterance.onstart = onStart
    if (onEnd) utterance.onend = onEnd

    window.speechSynthesis.speak(utterance)
  }

  cancelSpeech() {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
  }
}

export const voice = new VoiceService()
