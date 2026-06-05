import { useEffect, useState, useCallback } from 'react'
import { fetchCorpus } from '../../api'
import './CorpusInfo.css'

export default function CorpusInfo({ refreshTrigger }) {
  const [corpus, setCorpus] = useState(null)

  const load = useCallback(() => {
    fetchCorpus().then(setCorpus).catch(() => setCorpus(null))
  }, [])

  useEffect(() => { load() }, [load, refreshTrigger])

  if (!corpus) return null

  return (
    <section className="corpus-info">
      <h3 className="corpus-info__title">
        Corpus — {corpus.total_chunks} chunks
      </h3>
      {corpus.documents.length === 0 ? (
        <p className="corpus-info__empty">No documents ingested yet.</p>
      ) : (
        <ul className="corpus-info__list">
          {corpus.documents.map(doc => (
            <li key={doc} className="corpus-info__item">
              <span className="corpus-info__doc">{doc}</span>
              <span className="corpus-info__count">
                {corpus.chunks_per_document[doc]} chunks
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
