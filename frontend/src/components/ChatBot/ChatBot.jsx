import { useRef, useState } from 'react'
import ChatBot from 'react-chatbotify'
import { sendChat } from '../../api'
import SourcePanel from '../SourcePanel/SourcePanel'
import './ChatBot.css'

export default function PolicyChatBot() {
  const lastSourcesRef = useRef([])
  const [displayedSources, setDisplayedSources] = useState([])

  const flow = {
    start: {
      message: 'Hello! Ask me anything about the loaded policy documents.',
      path: 'ask_question',
    },
    ask_question: {
      message: async (params) => {
        const userQuestion = params.userInput
        try {
          const data = await sendChat(userQuestion)
          lastSourcesRef.current = data.sources || []
          setTimeout(() => setDisplayedSources([...lastSourcesRef.current]), 0)
          return data.answer
        } catch (err) {
          lastSourcesRef.current = []
          setTimeout(() => setDisplayedSources([]), 0)
          return `Error: ${err.message}`
        }
      },
      path: 'ask_question',
    },
  }

  const settings = {
    general: {
      primaryColor: '#2563eb',
      secondaryColor: '#1e293b',
      fontFamily: 'system-ui, sans-serif',
    },
    chatHistory: {
      disabled: true,
    },
    header: {
      title: 'Policy Assistant',
      showAvatar: false,
    },
    userBubble: {
      showAvatar: false,
    },
    botBubble: {
      showAvatar: false,
    },
    botBubbleStyle: {
      backgroundColor: '#1e293b',
      color: '#f1f5f9',
      borderRadius: '12px',
    },
    userBubbleStyle: {
      backgroundColor: '#2563eb',
      color: '#ffffff',
      borderRadius: '12px',
    },
  }

  return (
    <div className="chatbot-wrapper">
      <ChatBot flow={flow} settings={settings} />
      <SourcePanel sources={displayedSources} />
    </div>
  )
}
