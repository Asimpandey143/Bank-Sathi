/**
 * 404 Not Found Page
 */
export function NotFoundPage() {
  return (
    <div className="page gradient-bg">
      <main
        className="container"
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}
        role="main"
      >
        <div className="card" style={{ width: '100%', textAlign: 'center' }}>
          <h1 aria-label="Page not found">404</h1>
          <p style={{ margin: 'var(--space-4) 0' }}>This page does not exist.</p>
          <a href="/dashboard" className="btn btn-primary" aria-label="Return to dashboard">
            Return to Dashboard
          </a>
        </div>
      </main>
    </div>
  )
}
