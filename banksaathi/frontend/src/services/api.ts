/**
 * BankSathi Frontend API Client
 *
 * Handles HTTP requests, JWT storage, and demo auto-login for seamless testing.
 */
import axios from 'axios'

const API_BASE = '/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach Bearer token from localStorage
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('banksaathi_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const DEMO_ROLES = {
  mother: {
    phone: '9999999001',
    name: 'Meena Devi',
    password: 'demoPassword123!',
    roleLabel: 'Mother (Meena Devi)',
  },
  daughter: {
    phone: '9999999002',
    name: 'Ananya (Daughter)',
    password: 'daughterPassword123!',
    roleLabel: 'Daughter (Ananya)',
  },
} as const

export type DemoRole = keyof typeof DEMO_ROLES

export function getCurrentDemoRole(): DemoRole {
  return (localStorage.getItem('banksaathi_current_role') as DemoRole) || 'mother'
}

export async function loginDemoRole(role: DemoRole): Promise<string> {
  const creds = DEMO_ROLES[role]
  try {
    const loginRes = await axios.post(`${API_BASE}/auth/login`, {
      phone: creds.phone,
      password: creds.password,
    })
    const token = loginRes.data.access_token
    localStorage.setItem('banksaathi_token', token)
    localStorage.setItem('banksaathi_current_role', role)
    return token
  } catch (err: any) {
    if (err.response?.status === 401 || err.response?.status === 404) {
      try {
        await axios.post(`${API_BASE}/auth/register`, {
          phone: creds.phone,
          name: creds.name,
          password: creds.password,
        })
      } catch {
        // Ignored if already registered
      }
      const loginRes = await axios.post(`${API_BASE}/auth/login`, {
        phone: creds.phone,
        password: creds.password,
      })
      const token = loginRes.data.access_token
      localStorage.setItem('banksaathi_token', token)
      localStorage.setItem('banksaathi_current_role', role)
      return token
    }
    throw err
  }
}

// Auto-login demo user helper (defaults to Mother: Meena Devi)
export async function ensureDemoUser(): Promise<string> {
  const existingToken = localStorage.getItem('banksaathi_token')
  if (existingToken) return existingToken
  return loginDemoRole('mother')
}

// ── Types ───────────────────────────────────────────────────────────────────

export interface UserProfile {
  id: string
  name: string
  role: string
  created_at: string
}

export interface AccessibilityProfile {
  user_id: string
  language: string
  font_scale: number
  high_contrast: boolean
  screen_reader: boolean
  speech_rate: number
  confirmation_mode: string
  fraud_protection: string
}

export interface Beneficiary {
  id: string
  display_name: string
  masked_account: string
  trust_level: string
  first_seen_at: string
  last_used_at: string | null
}

export interface SecondOpinionSummary {
  has_notification: boolean
  notification_id?: string
  notification_status?: string
  risk_level?: string
  relationship_label?: string
  response?: string
  responder_name?: string
  comment?: string
}

export interface Transaction {
  id: string
  user_id: string
  beneficiary_id: string | null
  beneficiary_name: string | null
  amount: string
  currency: string
  intent: string
  status: string
  risk_score: number | null
  risk_level: string | null
  risk_reasons: { reasons: string[] } | null
  bank_reference: string | null
  second_opinion?: SecondOpinionSummary | null
  created_at: string
  updated_at: string
}

export interface IntentResult {
  intent: string
  amount: string | null
  currency: string
  beneficiary_name: string | null
  confidence: number
  clarification_needed: boolean
  clarification_question: string | null
}

export interface TrustedCircleMember {
  id: string
  user_id: string
  trusted_person_id: string
  trusted_person_name?: string | null
  relationship_label: string
  status: string
  permissions: Record<string, boolean>
  created_at: string
  verified_at?: string | null
}

export interface SecondOpinionResponseDetail {
  id: string
  responder_id: string
  responder_name?: string | null
  response: string
  comment?: string | null
  created_at: string
}

export interface TrustedCircleNotification {
  id: string
  transaction_id: string
  risk_level: string
  risk_reasons: { reasons?: string[] }
  amount_display: string
  beneficiary_display: string
  user_name?: string | null
  status: string
  created_at: string
  expires_at: string
  second_opinion?: SecondOpinionResponseDetail | null
}

export interface CommunitySession {
  id: string
  host_id: string
  topic: string
  description: string | null
  scheduled_at: string
  status: string
  max_participants: number
  duration_minutes: number
  created_at: string
}

export interface VoiceSummary {
  speech_text: string
  caption_text: string
  language: string
  confirm_prompt: string
  cancel_prompt: string
}

// ── API Methods ─────────────────────────────────────────────────────────────

export const api = {
  // Auth & Profile
  getMe: () => apiClient.get<UserProfile>('/users/me'),
  getPreferences: () => apiClient.get<AccessibilityProfile>('/users/me/preferences'),
  updatePreferences: (data: Partial<AccessibilityProfile>) =>
    apiClient.patch<AccessibilityProfile>('/users/me/preferences', data),

  // Beneficiaries
  listBeneficiaries: () => apiClient.get<Beneficiary[]>('/users/me/beneficiaries'),
  addBeneficiary: (data: { display_name: string; masked_account: string }) =>
    apiClient.post<Beneficiary>('/users/me/beneficiaries', data),

  // AI Intent
  parseIntent: (text: string) =>
    apiClient.post<IntentResult>('/ai/parse-intent', { text }),

  // Transactions
  createDraft: (data: {
    intent: string
    amount: string
    currency?: string
    beneficiary_name?: string
    beneficiary_id?: string
    raw_input?: string
  }) => apiClient.post<Transaction>('/transactions/draft', data),

  assessRisk: (id: string, context?: { is_untrusted_device?: boolean; is_unusual_time?: boolean }) =>
    apiClient.post<Transaction>(`/transactions/${id}/risk-assess`, context || {}),

  getTransaction: (id: string) => apiClient.get<Transaction>(`/transactions/${id}`),

  listTransactions: () => apiClient.get<Transaction[]>('/transactions'),

  confirmTransaction: (id: string) =>
    apiClient.post<Transaction>(`/transactions/${id}/confirm`, { confirmed: true }),

  cancelTransaction: (id: string) =>
    apiClient.post<Transaction>(`/transactions/${id}/cancel`),

  // Voice
  synthesizeVoiceSummary: (transaction_id: string) =>
    apiClient.post<VoiceSummary>('/voice/synthesize-summary', { transaction_id }),

  // Trusted Circle
  inviteTrustedMember: (phone: string, relationship_label = 'Family') =>
    apiClient.post<TrustedCircleMember>('/trusted-circle/members/invite', {
      phone,
      relationship_label,
    }),

  listTrustedMembers: () =>
    apiClient.get<TrustedCircleMember[]>('/trusted-circle/members'),

  revokeTrustedMember: (memberId: string) =>
    apiClient.delete(`/trusted-circle/members/${memberId}`),

  listTrustedNotifications: () =>
    apiClient.get<TrustedCircleNotification[]>('/trusted-circle/notifications'),

  getTrustedNotification: (notificationId: string) =>
    apiClient.get<TrustedCircleNotification>(`/trusted-circle/notifications/${notificationId}`),

  submitSecondOpinion: (
    notificationId: string,
    response: 'LOOKS_EXPECTED' | 'NOT_RECOGNIZED' | 'REQUEST_USER_VERIFICATION',
    comment?: string
  ) =>
    apiClient.post<SecondOpinionResponseDetail>(
      `/trusted-circle/notifications/${notificationId}/response`,
      { response, comment }
    ),

  // Community
  listCommunitySessions: () => apiClient.get<CommunitySession[]>('/community/sessions'),

  joinCommunitySession: (sessionId: string) =>
    apiClient.post(`/community/sessions/${sessionId}/join`),
}
