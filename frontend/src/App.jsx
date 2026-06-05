import { useState } from 'react'
import HealthBanner from './components/HealthBanner/HealthBanner'
import PolicyChatBot from './components/ChatBot/ChatBot'
import UploadForm from './components/UploadForm/UploadForm'
import CorpusInfo from './components/CorpusInfo/CorpusInfo'
import './App.css'

export default function App() {
  const [corpusVersion, setCorpusVersion] = useState(0)

  return (
    <div className="app">
      <HealthBanner />
      <div className="app__body">
        <main className="app__chat">
          <PolicyChatBot />
        </main>
        <aside className="app__sidebar">
          <UploadForm onSuccess={() => setCorpusVersion(v => v + 1)} />
          <CorpusInfo refreshTrigger={corpusVersion} />
        </aside>
      </div>
    </div>
  )
}
