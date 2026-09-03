/**
 * BankSathi — Root Application Component
 *
 * Provides:
 * - AccessibilityProvider (dynamic font scale, high contrast, synchronized captions)
 * - Accessible routing across all 9 core user workflows
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AccessibilityProvider } from './context/AccessibilityContext'

import { OnboardingPage } from './pages/OnboardingPage'
import { DashboardPage } from './pages/DashboardPage'
import { NewTransactionPage } from './pages/NewTransactionPage'
import { TransactionReviewPage } from './pages/TransactionReviewPage'
import { TransactionResultPage } from './pages/TransactionResultPage'
import { TrustedCirclePage } from './pages/TrustedCirclePage'
import { CommunityPage } from './pages/CommunityPage'
import { SettingsPage } from './pages/SettingsPage'
import { NotFoundPage } from './pages/NotFoundPage'

export default function App() {
  return (
    <AccessibilityProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/transactions/new" element={<NewTransactionPage />} />
          <Route path="/transactions/:id/review" element={<TransactionReviewPage />} />
          <Route path="/transactions/:id/result" element={<TransactionResultPage />} />
          <Route path="/trusted-circle" element={<TrustedCirclePage />} />
          <Route path="/helper" element={<Navigate to="/trusted-circle" replace />} />
          <Route path="/community" element={<CommunityPage />} />
          <Route path="/settings" element={<SettingsPage />} />

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </AccessibilityProvider>
  )
}
