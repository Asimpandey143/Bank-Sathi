/**
 * Web Speech API Service — Production-Grade Voice Runtime for BankSathi
 *
 * Integrated from EchoDrive Real-Time Voice Architecture:
 * - Continuous SpeechRecognition with auto-reconnect
 * - Acoustic Self-Echo Filtering (prevents microphone hearing browser speakers)
 * - Deterministic Barge-In Interruption with instant browser audio cancellation
 * - SpeechSynthesis Queue & Watchdog Timer (fixes Chrome/Edge speech hang bug)
 * - Natural Indian English (en-IN) and Hindi (hi-IN) voice selection
 * - Dynamic Turn Accumulation with silence debouncing for senior citizen pace
 */

export type VoiceState = 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING' | 'INTERRUPTING' | 'ACKNOWLEDGING'

declare global {
  interface Window {
    SpeechRecognition?: any
    webkitSpeechRecognition?: any
  }
}

export class VoiceService {
  private recognition: any = null
  private state: VoiceState = 'IDLE'
  private lang: string = 'en-IN'
  private accumulatedSpeech = ''
  private turnDebounceTimer: any = null
  private watchdogTimer: any = null
  private isRecognitionActive = false
  private isExplicitlyStopping = false
  private currentSpeakingText = ''
  private isSpeakingChunk = false
  private activeUtterance: SpeechSynthesisUtterance | null = null
  private speechQueue: { text: string; onStart?: () => void; onEnd?: () => void }[] = []

  // Event callbacks
  private onStateChangeCallback?: (state: VoiceState) => void
  private onInterimCallback?: (text: string) => void
  private onTurnCompleteCallback?: (text: string) => void
  private onErrorCallback?: (err: any) => void

  constructor() {
    this.initRecognition()
  }

  private initRecognition() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRec) {
      console.warn('[VoiceService] Web Speech API is not supported in this browser.')
      return
    }

    this.recognition = new SpeechRec()
    this.recognition.continuous = true
    this.recognition.interimResults = true
    this.recognition.lang = this.lang

    this.recognition.onstart = () => {
      this.isRecognitionActive = true
      if (this.state !== 'SPEAKING' && this.state !== 'THINKING' && this.state !== 'INTERRUPTING') {
        this.setState('LISTENING')
      }
    }

    this.recognition.onresult = (event: any) => {
      let interimTranscript = ''
      let finalTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const trans = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalTranscript += trans
        } else {
          interimTranscript += trans
        }
      }

      const activeText = (finalTranscript || interimTranscript).trim().toLowerCase()

      // ── Acoustic Self-Echo Filter (Borrowed from EchoDrive) ───────────────
      // If assistant is currently speaking through device speakers, discard incoming
      // microphone audio if it matches what the assistant is speaking!
      if (activeText && (this.state === 'SPEAKING' || this.isSpeakingChunk)) {
        const normalizedSpeaking = (this.currentSpeakingText || '').toLowerCase()
        const isSelfEcho =
          normalizedSpeaking.length > 0 &&
          (normalizedSpeaking.includes(activeText) ||
            activeText.includes(normalizedSpeaking.slice(0, Math.min(25, normalizedSpeaking.length))))

        if (!isSelfEcho && activeText.length > 2) {
          // User genuinely interrupted!
          console.log('[VoiceService] Barge-In detected while speaking:', activeText)
          this.handleBargeIn(activeText)
        } else {
          // Discard echo
          return
        }
      } else if (activeText && this.state === 'THINKING') {
        // User interrupted thinking
        this.handleBargeIn(activeText)
      }

      if (interimTranscript.trim() && this.onInterimCallback) {
        const preview = (this.accumulatedSpeech ? this.accumulatedSpeech + ' ' : '') + interimTranscript.trim()
        this.onInterimCallback(preview)
      }

      if (finalTranscript.trim()) {
        const newSegment = finalTranscript.trim()
        this.accumulatedSpeech = (this.accumulatedSpeech ? this.accumulatedSpeech + ' ' : '') + newSegment
        if (this.onInterimCallback) {
          this.onInterimCallback(this.accumulatedSpeech)
        }

        // Dynamic turn silence debounce (650ms for senior comfort)
        if (this.turnDebounceTimer) clearTimeout(this.turnDebounceTimer)
        const debounceMs = (this.state === 'ACKNOWLEDGING' || this.state === 'INTERRUPTING') ? 1200 : 650

        this.turnDebounceTimer = setTimeout(() => {
          if (this.accumulatedSpeech.trim()) {
            const fullSpeech = this.accumulatedSpeech.trim()
            this.accumulatedSpeech = ''
            if (this.onTurnCompleteCallback) {
              this.onTurnCompleteCallback(fullSpeech)
            }
          }
        }, debounceMs)
      }
    }

    this.recognition.onerror = (event: any) => {
      if (event.error !== 'no-speech') {
        console.warn('[VoiceService] Recognition notice:', event.error)
        if (this.onErrorCallback) this.onErrorCallback(event.error)
      }
    }

    this.recognition.onend = () => {
      this.isRecognitionActive = false
      // Auto-reconnect if not explicitly stopped
      if (this.state !== 'IDLE' && !this.isExplicitlyStopping) {
        setTimeout(() => {
          try {
            if (this.state !== 'IDLE' && !this.isRecognitionActive && !this.isExplicitlyStopping) {
              this.recognition?.start()
            }
          } catch {
            // Already started or busy
          }
        }, 150)
      }
    }
  }

  isSupported(): boolean {
    return this.recognition !== null
  }

  getState(): VoiceState {
    return this.state
  }

  setState(newState: VoiceState) {
    this.state = newState
    if (this.onStateChangeCallback) {
      this.onStateChangeCallback(newState)
    }
  }

  setLanguage(langCode: 'en-IN' | 'hi-IN') {
    this.lang = langCode
    if (this.recognition) {
      this.recognition.lang = langCode
    }
  }

  getLanguage(): string {
    return this.lang
  }

  onStateChange(cb: (state: VoiceState) => void) {
    this.onStateChangeCallback = cb
  }

  // ── Continuous Turn-Based Listening ─────────────────────────────────────────
  startContinuousSession(
    onInterim: (text: string) => void,
    onTurnComplete: (text: string) => void,
    onError: (err: any) => void
  ): boolean {
    if (!this.recognition) {
      onError('Speech recognition not supported in this browser.')
      return false
    }

    this.onInterimCallback = onInterim
    this.onTurnCompleteCallback = onTurnComplete
    this.onErrorCallback = onError
    this.isExplicitlyStopping = false
    this.accumulatedSpeech = ''

    if (this.isRecognitionActive) {
      this.setState('LISTENING')
      return true
    }

    try {
      this.recognition.start()
      this.setState('LISTENING')
      return true
    } catch {
      this.setState('LISTENING')
      return true
    }
  }

  // Backward compatible single-turn listener
  startListening(
    onResult: (text: string, isFinal: boolean) => void,
    onError: (err: any) => void,
    onEnd: () => void
  ): boolean {
    return this.startContinuousSession(
      (interim) => onResult(interim, false),
      (finalText) => {
        onResult(finalText, true)
        onEnd()
      },
      onError
    )
  }

  stopListening() {
    this.isExplicitlyStopping = true
    if (this.turnDebounceTimer) clearTimeout(this.turnDebounceTimer)
    this.accumulatedSpeech = ''
    if (this.recognition && this.isRecognitionActive) {
      try {
        this.recognition.stop()
      } catch {
        // Ignore
      }
      this.isRecognitionActive = false
    }
    this.setState('IDLE')
  }

  // ── Deterministic Barge-In Cancellation ─────────────────────────────────────
  handleBargeIn(triggerWord = '') {
    if (this.state === 'INTERRUPTING' || this.state === 'ACKNOWLEDGING') return

    console.log('⚡ [VoiceService] Immediate Barge-In triggered by:', triggerWord || 'voice onset')

    // 1. Clear pending speech queue
    this.speechQueue = []
    this.isSpeakingChunk = false
    this.currentSpeakingText = ''
    if (this.watchdogTimer) clearTimeout(this.watchdogTimer)

    // 2. Cancel active browser audio synchronously
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
    this.activeUtterance = null

    // 3. Immediately transition to INTERRUPTING
    this.setState('INTERRUPTING')

    // 4. Quick acknowledgment ("OK, listening...")
    setTimeout(() => {
      this.setState('ACKNOWLEDGING')
      this.speakQuickAck(() => {
        this.setState('LISTENING')
      })
    }, 100)
  }

  private speakQuickAck(onDone: () => void) {
    if (!('speechSynthesis' in window)) {
      onDone()
      return
    }

    const ackUtterance = new SpeechSynthesisUtterance('OK.')
    ackUtterance.rate = 1.15
    ackUtterance.lang = this.lang

    const voices = window.speechSynthesis.getVoices()
    const match = voices.find(
      (v) =>
        v.lang.startsWith('en') &&
        (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('India') || v.name.includes('Heera'))
    )
    if (match) ackUtterance.voice = match

    ackUtterance.onend = () => onDone()
    ackUtterance.onerror = () => onDone()

    try {
      window.speechSynthesis.speak(ackUtterance)
    } catch {
      onDone()
    }
  }

  // ── High-Reliability Speech Playback with Watchdog ───────────────────────────
  speak(text: string, rate = 0.95, onStart?: () => void, onEnd?: () => void) {
    if (!('speechSynthesis' in window) || !text.trim()) {
      if (onEnd) onEnd()
      return
    }

    // Cancel current speech if any
    this.cancelSpeech()

    this.speechQueue.push({ text: text.trim(), onStart, onEnd })
    this.processSpeechQueue(rate)
  }

  private processSpeechQueue(rate: number) {
    if (this.isSpeakingChunk || this.speechQueue.length === 0) return

    const item = this.speechQueue.shift()
    if (!item) return

    this.isSpeakingChunk = true
    this.currentSpeakingText = item.text
    this.setState('SPEAKING')

    const utterance = new SpeechSynthesisUtterance(item.text)
    utterance.rate = rate
    utterance.lang = this.lang

    // Pick warm natural Indian English or Hindi voice
    const voices = window.speechSynthesis.getVoices()
    const targetLang = this.lang.toLowerCase().replace('_', '-')
    let selectedVoice = voices.find((v) => v.lang.toLowerCase().replace('_', '-') === targetLang)

    if (!selectedVoice) {
      selectedVoice = voices.find(
        (v) =>
          v.lang.startsWith('en') &&
          (v.name.includes('India') ||
            v.name.includes('Google') ||
            v.name.includes('Natural') ||
            v.name.includes('Heera') ||
            v.name.includes('Neerja'))
      )
    }
    if (selectedVoice) utterance.voice = selectedVoice

    const finishUtterance = () => {
      if (this.watchdogTimer) clearTimeout(this.watchdogTimer)
      this.isSpeakingChunk = false
      this.currentSpeakingText = ''
      this.activeUtterance = null

      if (item.onEnd) {
        try {
          item.onEnd()
        } catch (e) {
          console.error(e)
        }
      }

      if (this.speechQueue.length > 0) {
        this.processSpeechQueue(rate)
      } else {
        if (this.state === 'SPEAKING') {
          this.setState('LISTENING')
        }
      }
    }

    utterance.onstart = () => {
      this.activeUtterance = utterance
      if (item.onStart) item.onStart()

      // Watchdog timer: 140ms per character with minimum 5000ms
      const estimatedMs = Math.max(5000, item.text.length * 140)
      if (this.watchdogTimer) clearTimeout(this.watchdogTimer)
      this.watchdogTimer = setTimeout(() => {
        console.log('[VoiceService] Watchdog timer advancing speech.')
        finishUtterance()
      }, estimatedMs)
    }

    utterance.onend = () => finishUtterance()
    utterance.onerror = (err) => {
      console.warn('[VoiceService] Playback warning:', err)
      finishUtterance()
    }

    try {
      window.speechSynthesis.speak(utterance)
    } catch (e) {
      console.error('[VoiceService] SpeechSynthesis error:', e)
      finishUtterance()
    }
  }

  cancelSpeech() {
    this.speechQueue = []
    this.isSpeakingChunk = false
    this.currentSpeakingText = ''
    if (this.watchdogTimer) clearTimeout(this.watchdogTimer)
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
    this.activeUtterance = null
  }
}

export const voice = new VoiceService()
