import { useState } from 'react'
import { ingestDocument } from '../../api'
import './UploadForm.css'

export default function UploadForm({ onSuccess }) {
  const [docId, setDocId] = useState('')
  const [text, setText] = useState('')
  const [status, setStatus] = useState(null)
  const [message, setMessage] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (!docId.trim() || !text.trim()) return

    setStatus('loading')
    setMessage('')
    try {
      const result = await ingestDocument(text.trim(), docId.trim())
      setStatus('ok')
      setMessage(`Ingested ${result.chunks_processed} chunks from "${docId}".`)
      setDocId('')
      setText('')
      if (onSuccess) onSuccess()
    } catch (err) {
      setStatus('error')
      setMessage(err.message)
    }
  }

  return (
    <form className="upload-form" onSubmit={handleSubmit}>
      <h2 className="upload-form__title">Add Document</h2>

      <label className="upload-form__label">
        Document ID
        <input
          className="upload-form__input"
          type="text"
          value={docId}
          onChange={e => setDocId(e.target.value)}
          placeholder="e.g. welfare_policy_2024"
          required
        />
      </label>

      <label className="upload-form__label">
        Document Text
        <textarea
          className="upload-form__textarea"
          value={text}
          onChange={e => setText(e.target.value)}
          rows={8}
          placeholder="Paste the full document text here..."
          required
        />
      </label>

      <button
        className="upload-form__button"
        type="submit"
        disabled={status === 'loading'}
      >
        {status === 'loading' ? 'Ingesting...' : 'Ingest Document'}
      </button>

      {message && (
        <p className={`upload-form__message upload-form__message--${status}`}>
          {message}
        </p>
      )}
    </form>
  )
}
