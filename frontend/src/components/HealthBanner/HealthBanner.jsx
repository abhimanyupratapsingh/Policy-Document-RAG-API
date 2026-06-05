import { useEffect, useState } from 'react'
import { fetchHealth } from '../../api'
import './HealthBanner.css'

export default function HealthBanner() {
  const [health, setHealth] = useState(null)
  const [dismissed, setDismissed] = useState(false)

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'error', ollama_reachable: false }))
  }, [])

  if (!health || dismissed) return null

  const allGood = health.status === 'ok' && health.ollama_reachable
  if (allGood) return null

  return (
    <div className={`health-banner health-banner--${allGood ? 'ok' : 'warn'}`}>
      <span>
        {!health.ollama_reachable
          ? `Ollama is not reachable. Run: ollama serve && ollama pull ${health.ollama_model ?? 'mistral'}`
          : 'Backend error — check that FastAPI is running.'}
      </span>
      <button className="health-banner__close" onClick={() => setDismissed(true)}>
        ×
      </button>
    </div>
  )
}
