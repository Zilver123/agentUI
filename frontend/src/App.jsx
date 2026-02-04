import { useState, useRef, useEffect, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'

// Generate session ID
const SESSION_ID = crypto.randomUUID()

// Icons
const SendIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M22 2L11 13M22 2L15 22L11 13M11 13L2 9L22 2" />
  </svg>
)

const PlusIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 5V19M5 12H19" />
  </svg>
)

const ToolIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
  </svg>
)

const CheckIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M20 6L9 17L4 12" />
  </svg>
)

const TrashIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M3 6H5H21M19 6V20C19 21 18 22 17 22H7C6 22 5 21 5 20V6M8 6V4C8 3 9 2 10 2H14C15 2 16 3 16 4V6" />
  </svg>
)

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [media, setMedia] = useState([])
  const [isThinking, setIsThinking] = useState(false)
  const [error, setError] = useState(null)
  const [ws, setWs] = useState(null)
  const [activeTools, setActiveTools] = useState({})

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const fileInputRef = useRef(null)

  // Connect WebSocket
  useEffect(() => {
    const wsUrl = `ws://localhost:8000/ws/${SESSION_ID}`
    const socket = new WebSocket(wsUrl)

    socket.onopen = () => {
      console.log('Connected')
      setError(null)
    }

    socket.onclose = () => {
      console.log('Disconnected')
      setError('Connection lost. Please refresh.')
    }

    socket.onerror = () => {
      setError('Failed to connect to server')
    }

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleServerMessage(data)
    }

    setWs(socket)

    return () => socket.close()
  }, [])

  // Handle server messages
  const handleServerMessage = useCallback((data) => {
    switch (data.type) {
      case 'thinking':
        setIsThinking(data.status)
        break

      case 'text_delta':
        setMessages(prev => {
          const newMessages = [...prev]
          const lastMsg = newMessages[newMessages.length - 1]
          if (lastMsg && lastMsg.role === 'assistant') {
            lastMsg.content += data.text
          } else {
            newMessages.push({ role: 'assistant', content: data.text, tools: [] })
          }
          return newMessages
        })
        break

      case 'tool_start':
        setActiveTools(prev => ({
          ...prev,
          [data.tool_id]: { name: data.name, status: 'running' }
        }))
        setMessages(prev => {
          const newMessages = [...prev]
          const lastMsg = newMessages[newMessages.length - 1]
          if (lastMsg && lastMsg.role === 'assistant') {
            lastMsg.tools = [...(lastMsg.tools || []), { id: data.tool_id, name: data.name, status: 'running' }]
          }
          return newMessages
        })
        break

      case 'tool_end':
        setActiveTools(prev => ({
          ...prev,
          [data.tool_id]: { ...prev[data.tool_id], status: 'done' }
        }))
        setMessages(prev => {
          const newMessages = [...prev]
          const lastMsg = newMessages[newMessages.length - 1]
          if (lastMsg && lastMsg.role === 'assistant' && lastMsg.tools) {
            lastMsg.tools = lastMsg.tools.map(t =>
              t.id === data.tool_id ? { ...t, status: 'done' } : t
            )
          }
          return newMessages
        })
        break

      case 'done':
        setIsThinking(false)
        break

      case 'error':
        setError(data.message)
        setIsThinking(false)
        break

      case 'cleared':
        setMessages([])
        break
    }
  }, [])

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isThinking])

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 120) + 'px'
    }
  }, [input])

  // Handle file selection
  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files)

    files.forEach(file => {
      const reader = new FileReader()
      reader.onload = (event) => {
        const base64 = event.target.result.split(',')[1]
        const isVideo = file.type.startsWith('video/')

        setMedia(prev => [...prev, {
          type: isVideo ? 'video' : 'image',
          media_type: file.type,
          data: base64,
          preview: event.target.result,
          name: file.name
        }])
      }
      reader.readAsDataURL(file)
    })

    e.target.value = ''
  }

  // Remove media
  const removeMedia = (index) => {
    setMedia(prev => prev.filter((_, i) => i !== index))
  }

  // Send message
  const sendMessage = () => {
    if ((!input.trim() && media.length === 0) || !ws || isThinking) return

    // Add user message to UI
    const userMessage = {
      role: 'user',
      content: input,
      media: media.map(m => ({ type: m.type, preview: m.preview }))
    }
    setMessages(prev => [...prev, userMessage])

    // Send to server
    ws.send(JSON.stringify({
      type: 'message',
      text: input,
      media: media.map(m => ({
        type: m.type,
        media_type: m.media_type,
        data: m.data
      }))
    }))

    // Clear input
    setInput('')
    setMedia([])
  }

  // Handle key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Clear chat
  const clearChat = () => {
    if (ws) {
      ws.send(JSON.stringify({ type: 'clear' }))
    }
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>Agent</h1>
        <button onClick={clearChat} title="Clear chat">
          <TrashIcon />
        </button>
      </header>

      {/* Error banner */}
      {error && <div className="error">{error}</div>}

      {/* Messages */}
      <div className="messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h2>Hello!</h2>
            <p>Send a message to get started.<br />You can also attach images or videos.</p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              {/* Media attachments */}
              {msg.media && msg.media.length > 0 && (
                <div className="message-media">
                  {msg.media.map((m, j) => (
                    m.type === 'video' ? (
                      <video key={j} src={m.preview} controls />
                    ) : (
                      <img key={j} src={m.preview} alt="" />
                    )
                  ))}
                </div>
              )}

              {/* Tool calls */}
              {msg.tools && msg.tools.length > 0 && (
                <div className="tools">
                  {msg.tools.map(tool => (
                    <div key={tool.id} className={`tool-call ${tool.status}`}>
                      <ToolIcon />
                      <span className="name">{tool.name}</span>
                      <span className="status">
                        {tool.status === 'running' ? 'Running...' : <CheckIcon />}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Message content */}
              {msg.content && (
                <div className="message-content">
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    msg.content
                  )}
                </div>
              )}
            </div>
          ))
        )}

        {/* Thinking indicator */}
        {isThinking && messages[messages.length - 1]?.role !== 'assistant' && (
          <div className="message assistant">
            <div className="thinking">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="input-area">
        {/* Media preview */}
        {media.length > 0 && (
          <div className="media-preview">
            {media.map((m, i) => (
              <div key={i} className="media-preview-item">
                {m.type === 'video' ? (
                  <video src={m.preview} />
                ) : (
                  <img src={m.preview} alt="" />
                )}
                <button onClick={() => removeMedia(i)}>×</button>
              </div>
            ))}
          </div>
        )}

        <div className="input-container">
          {/* Upload button */}
          <label className="upload-btn">
            <PlusIcon />
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,video/*"
              multiple
              onChange={handleFileSelect}
            />
          </label>

          {/* Text input */}
          <textarea
            ref={inputRef}
            className="text-input"
            placeholder="Message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            rows={1}
          />

          {/* Send button */}
          <button
            className="send-btn"
            onClick={sendMessage}
            disabled={(!input.trim() && media.length === 0) || isThinking}
          >
            <SendIcon />
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
