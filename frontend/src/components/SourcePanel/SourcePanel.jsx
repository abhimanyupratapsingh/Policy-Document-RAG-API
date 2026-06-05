import './SourcePanel.css'

export default function SourcePanel({ sources }) {
  if (!sources || sources.length === 0) return null

  return (
    <aside className="source-panel">
      <h3 className="source-panel__heading">Sources</h3>
      <ul className="source-panel__list">
        {sources.map((s, i) => (
          <li key={i} className="source-panel__item">
            <span className="source-panel__label">{s.source}</span>
            <blockquote className="source-panel__excerpt">{s.excerpt}</blockquote>
          </li>
        ))}
      </ul>
    </aside>
  )
}
