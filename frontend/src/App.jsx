import { useState, useRef, useEffect, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'

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

const ExpandIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M15 3H21V9M9 21H3V15M21 3L14 10M3 21L10 14" />
  </svg>
)

const DownloadIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V15M7 10L12 15L17 10M12 15V3" />
  </svg>
)

const ShareIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M4 12V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V12M16 6L12 2L8 6M12 2V15" />
  </svg>
)

const CopyLinkIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
  </svg>
)

const CheckSmallIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M20 6L9 17L4 12" />
  </svg>
)

const CloseIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M18 6L6 18M6 6L18 18" />
  </svg>
)

// Parse options from agent message
// Returns { options: string[], questionText: string } if exactly 2 options found
// Returns { options: [], questionText: originalText } otherwise
const parseOptions = (text) => {
  const lines = text.split('\n')
  const optionMatches = []
  let questionText = text

  console.log('[parseOptions] Input text:', text.substring(0, 100) + '...')
  console.log('[parseOptions] Total lines:', lines.length)

  // Look for numbered (1. 2.) or bullet (-, •, *) options
  // STRICT: Must match exact format at line start with content after
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    let optionText = null

    // Check for numbered format (1., 2., etc.) - STRICT: only single or double digit numbers
    const numberedMatch = line.match(/^(\d{1,2})\.\s+(.+)$/)
    if (numberedMatch && numberedMatch[2].length > 0) {
      optionText = numberedMatch[2].trim()
      console.log(`[parseOptions] Line ${i} matched NUMBERED: "${line}" -> option: "${optionText}"`)
    }

    // Check for bullet format (-, •, *) - STRICT: only these exact characters
    if (!optionText) {
      const bulletMatch = line.match(/^([-•*])\s+(.+)$/)
      if (bulletMatch && bulletMatch[2].length > 0) {
        optionText = bulletMatch[2].trim()
        console.log(`[parseOptions] Line ${i} matched BULLET: "${line}" -> option: "${optionText}"`)
      }
    }

    // Debug: show lines that didn't match
    if (!optionText && line.length > 0) {
      console.log(`[parseOptions] Line ${i} NO MATCH: "${line.substring(0, 50)}"`)
    }

    if (optionText) {
      optionMatches.push({ index: i, text: optionText, originalLine: line })
    }
  }

  console.log(`[parseOptions] Found ${optionMatches.length} options`)
  
  // Only return options if EXACTLY 2 found
  if (optionMatches.length === 2) {
    console.log('[parseOptions] ✓ EXACTLY 2 options detected - showing UI')
    // Extract question text (everything before first option)
    const firstOptionIndex = optionMatches[0].index
    const questionLines = lines.slice(0, firstOptionIndex).join('\n').trim()

    return {
      options: [optionMatches[0].text, optionMatches[1].text],
      questionText: questionLines || text
    }
  }

  console.log('[parseOptions] ✗ Not exactly 2 options - no UI shown')
  // Return empty options and original text if not exactly 2
  return { options: [], questionText: text }
}

// Remove option bullets from message content for display
// Only removes bullets if exactly 2 options are found
const stripOptionsFromContent = (text, hasOptions) => {
  if (!hasOptions) return text

  const lines = text.split('\n')
  const displayLines = []
  let strippedCount = 0

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()

    // Skip lines that are numbered or bullet options (STRICT matching)
    const isNumbered = /^(\d{1,2})\.\s+(.+)$/.test(line)
    const isBullet = /^([-•*])\s+(.+)$/.test(line)

    if (!isNumbered && !isBullet) {
      displayLines.push(lines[i])
    } else {
      strippedCount++
      console.log(`[stripOptionsFromContent] Removed option line: "${line}"`)
    }
  }

  console.log(`[stripOptionsFromContent] Stripped ${strippedCount} option lines from message`)
  return displayLines.join('\n').trim()
}

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [media, setMedia] = useState([])
  const [isThinking, setIsThinking] = useState(false)
  const [isWaiting, setIsWaiting] = useState(false)
  const [error, setError] = useState(null)
  const [ws, setWs] = useState(null)
  const [responseOptions, setResponseOptions] = useState(null) // { options: [], questionText: string }
  const [responseMessageIndex, setResponseMessageIndex] = useState(null)
  const [lightbox, setLightbox] = useState(null) // { type: 'image'|'video', src: string }
  const [copiedUrl, setCopiedUrl] = useState(null) // briefly holds the URL that was just copied

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const pendingNewTurn = useRef(false)

  // WebSocket connection
  useEffect(() => {
    const socket = new WebSocket(`ws://localhost:8000/ws/${SESSION_ID}`)

    socket.onopen = () => {
      console.log('Connected')
      setError(null)
    }

    socket.onclose = () => {
      console.log('Disconnected')
      setError('Connection lost. Please refresh.')
    }

    socket.onerror = () => setError('Failed to connect to server')

    socket.onmessage = (e) => handleServerMessage(JSON.parse(e.data))

    setWs(socket)
    return () => socket.close()
  }, [])

  // Handle incoming WebSocket messages
  const handleServerMessage = useCallback((data) => {
    switch (data.type) {
      case 'thinking':
        setIsThinking(data.status)
        break

      case 'text_delta':
        setIsWaiting(false)
        setMessages(prev => {
          // Start new message after tool execution
          if (pendingNewTurn.current) {
            pendingNewTurn.current = false
            return [...prev, { role: 'assistant', content: data.text, tools: [] }]
          }

          const lastMsg = prev[prev.length - 1]
          if (lastMsg?.role === 'assistant') {
            return [
              ...prev.slice(0, -1),
              { ...lastMsg, content: lastMsg.content + data.text }
            ]
          }
          return [...prev, { role: 'assistant', content: data.text, tools: [] }]
        })
        break

      case 'tool_start':
        setIsWaiting(false)
        setMessages(prev => {
          const lastMsg = prev[prev.length - 1]
          const newTool = { id: data.tool_id, name: data.name, status: 'running' }

          if (lastMsg?.role === 'assistant') {
            return [
              ...prev.slice(0, -1),
              { ...lastMsg, tools: [...(lastMsg.tools || []), newTool] }
            ]
          }
          return [...prev, { role: 'assistant', content: '', tools: [newTool] }]
        })
        break

      case 'tool_end':
        setMessages(prev => {
          const lastMsg = prev[prev.length - 1]
          if (lastMsg?.role === 'assistant' && lastMsg.tools) {
            return [
              ...prev.slice(0, -1),
              {
                ...lastMsg,
                tools: lastMsg.tools.map(t =>
                  t.id === data.tool_id ? { ...t, status: 'done' } : t
                )
              }
            ]
          }
          return prev
        })
        break

      case 'new_turn':
        pendingNewTurn.current = true
        break

      case 'question':
        // Handle ask_question tool - set response options from tool call
        console.log('[question event] Received question:', data.question, 'with options:', data.options)
        setResponseOptions({
          question: data.question,
          options: data.options,
          questionText: data.question
        })
        setResponseMessageIndex(null) // Not tied to a specific message
        console.log('[question event] Response options set')
        break

      case 'done':
        setIsThinking(false)
        setIsWaiting(false)
        // Check if the last assistant message contains exactly 2 options (legacy text parsing)
        // Use functional updates to avoid stale closure issues
        setMessages(prevMessages => {
          const lastMsgIndex = prevMessages.length - 1
          const lastMsg = prevMessages[lastMsgIndex]

          // Check current responseOptions state
          setResponseOptions(currentOptions => {
            if (currentOptions) {
              // Already set by ask_question tool, keep it
              return currentOptions
            }

            // Try legacy text parsing
            if (lastMsg?.role === 'assistant' && lastMsg.content) {
              const parsed = parseOptions(lastMsg.content)
              if (parsed.options.length === 2) {
                setResponseMessageIndex(lastMsgIndex)
                return parsed
              }
            }
            return null
          })

          return prevMessages
        })
        break

      case 'error':
        setError(data.message)
        setIsThinking(false)
        setIsWaiting(false)
        break

      case 'cleared':
        setMessages([])
        break
    }
  }, [])

  // Auto-scroll on new messages
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

  const handleFileSelect = (e) => {
    Array.from(e.target.files).forEach(file => {
      const reader = new FileReader()
      reader.onload = (event) => {
        setMedia(prev => [...prev, {
          type: file.type.startsWith('video/') ? 'video' : 'image',
          media_type: file.type,
          data: event.target.result.split(',')[1],
          preview: event.target.result,
          name: file.name
        }])
      }
      reader.readAsDataURL(file)
    })
    e.target.value = ''
  }

  const removeMedia = (index) => {
    setMedia(prev => prev.filter((_, i) => i !== index))
  }

  const sendMessage = (text = null) => {
    const messageText = text || input
    if ((!messageText.trim() && media.length === 0) || !ws || isThinking) return

    setMessages(prev => [...prev, {
      role: 'user',
      content: messageText,
      media: media.map(m => ({ type: m.type, preview: m.preview }))
    }])

    ws.send(JSON.stringify({
      type: 'message',
      text: messageText,
      media: media.map(m => ({
        type: m.type,
        media_type: m.media_type,
        data: m.data
      }))
    }))

    setIsWaiting(true)
    setInput('')
    setMedia([])
    setResponseOptions(null)
    setResponseMessageIndex(null)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => ws?.send(JSON.stringify({ type: 'clear' }))

  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent)

  const handleDesktopDownload = async (url, type) => {
    try {
      const response = await fetch(url)
      const blob = await response.blob()
      const blobUrl = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = `popad-${Date.now()}.${type === 'video' ? 'mp4' : 'png'}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(blobUrl)
    } catch {
      window.open(url, '_blank')
    }
  }

  const handleMobileShare = async (url, type) => {
    try {
      const response = await fetch(url)
      const blob = await response.blob()
      const ext = type === 'video' ? 'mp4' : 'png'
      const mimeType = type === 'video' ? 'video/mp4' : 'image/png'
      const file = new File([blob], `popad-${Date.now()}.${ext}`, { type: mimeType })

      if (navigator.canShare?.({ files: [file] })) {
        await navigator.share({ files: [file] })
      } else {
        // Fallback: open in new tab
        window.open(url, '_blank')
      }
    } catch (err) {
      // User cancelled share or share failed — ignore AbortError
      if (err.name !== 'AbortError') {
        window.open(url, '_blank')
      }
    }
  }

  const handleDownload = (url, type) => {
    if (isMobile) {
      handleMobileShare(url, type)
    } else {
      handleDesktopDownload(url, type)
    }
  }

  const handleCopyUrl = (url) => {
    navigator.clipboard.writeText(url)
    setCopiedUrl(url)
    setTimeout(() => setCopiedUrl(null), 1500)
  }

  // Wrapper that adds preview/download/copy overlay icons to generated media
  const MediaWrapper = ({ children, src, type }) => (
    <div className="media-wrapper">
      {children}
      <div className="media-actions">
        <button className="media-action-btn" onClick={() => setLightbox({ type, src })} title="Preview">
          <ExpandIcon />
        </button>
        <button className="media-action-btn" onClick={() => handleCopyUrl(src)} title="Copy URL">
          {copiedUrl === src ? <CheckSmallIcon /> : <CopyLinkIcon />}
        </button>
        {isMobile ? (
          <button className="media-action-btn" onClick={() => handleMobileShare(src, type)} title="Save">
            <ShareIcon />
          </button>
        ) : (
          <button className="media-action-btn" onClick={() => handleDesktopDownload(src, type)} title="Download">
            <DownloadIcon />
          </button>
        )}
      </div>
    </div>
  )

  // Custom markdown renderer for video links and images
  const markdownComponents = {
    a: ({ href, children }) => {
      const isVideo = href?.endsWith('.mp4') || (href?.includes('fal.media') && href?.includes('video'))
      if (isVideo) {
        return (
          <MediaWrapper src={href} type="video">
            <video src={href} controls playsInline>
              <a href={href}>{children}</a>
            </video>
          </MediaWrapper>
        )
      }
      return <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>
    },
    img: ({ src, alt }) => (
      <MediaWrapper src={src} type="image">
        <img src={src} alt={alt || ''} />
      </MediaWrapper>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Agent</h1>
        <button onClick={clearChat} title="Clear chat">
          <TrashIcon />
        </button>
      </header>

      {error && <div className="error">{error}</div>}

      <div className="messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h2>Hello!</h2>
            <p>Send a message to get started.<br />You can also attach images or videos.</p>
          </div>
        ) : (
          messages.map((msg, i) => {
            // Check if this message has response options
            const hasOptions = responseMessageIndex === i && responseOptions?.options.length === 2
            const displayContent = hasOptions 
              ? stripOptionsFromContent(msg.content, true)
              : msg.content

            return (
              <div key={i} className={`message ${msg.role}`}>
                {msg.media?.length > 0 && (
                  <div className="message-media">
                    {msg.media.map((m, j) => (
                      m.type === 'video'
                        ? <video key={j} src={m.preview} controls />
                        : <img key={j} src={m.preview} alt="" />
                    ))}
                  </div>
                )}

                {msg.tools?.length > 0 && (
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

                {displayContent && (
                  <div className="message-content">
                    {msg.role === 'assistant' ? (
                      <ReactMarkdown components={markdownComponents}>
                        {displayContent}
                      </ReactMarkdown>
                    ) : (
                      displayContent
                    )}
                  </div>
                )}
              </div>
            )
          })
        )}

        {isWaiting && (
          <div className="message assistant">
            <div className="loading-text">
              Loading
              <span className="loading-dot" style={{ animationDelay: '0s' }}>.</span>
              <span className="loading-dot" style={{ animationDelay: '0.3s' }}>.</span>
              <span className="loading-dot" style={{ animationDelay: '0.6s' }}>.</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        {media.length > 0 && (
          <div className="media-preview">
            {media.map((m, i) => (
              <div key={i} className="media-preview-item">
                {m.type === 'video'
                  ? <video src={m.preview} />
                  : <img src={m.preview} alt="" />
                }
                <button onClick={() => removeMedia(i)}>×</button>
              </div>
            ))}
          </div>
        )}

        {responseOptions && responseOptions.options && responseOptions.options.length >= 2 && (
          <div className="response-options">
            {responseOptions.question && (
              <p className="response-question">{responseOptions.question}</p>
            )}
            {responseOptions.options.map((option, i) => (
              <button
                key={i}
                className="response-option"
                onClick={() => sendMessage(option)}
              >
                {option}
              </button>
            ))}
          </div>
        )}

        <div className="input-container">
          <label className="upload-btn">
            <PlusIcon />
            <input
              type="file"
              accept="image/*,video/*"
              multiple
              onChange={handleFileSelect}
            />
          </label>

          <textarea
            ref={inputRef}
            className="text-input"
            placeholder="Message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            rows={1}
          />

          <button
            className="send-btn"
            onClick={sendMessage}
            disabled={(!input.trim() && media.length === 0) || isThinking}
          >
            <SendIcon />
          </button>
        </div>
      </div>

      {lightbox && (
        <div className="lightbox-overlay" onClick={() => setLightbox(null)}>
          <div className="lightbox-toolbar">
            <button className="lightbox-btn" onClick={(e) => { e.stopPropagation(); handleCopyUrl(lightbox.src) }} title="Copy URL">
              {copiedUrl === lightbox.src ? <CheckSmallIcon /> : <CopyLinkIcon />}
            </button>
            {isMobile ? (
              <button className="lightbox-btn" onClick={(e) => { e.stopPropagation(); handleMobileShare(lightbox.src, lightbox.type) }} title="Save">
                <ShareIcon />
              </button>
            ) : (
              <button className="lightbox-btn" onClick={(e) => { e.stopPropagation(); handleDesktopDownload(lightbox.src, lightbox.type) }} title="Download">
                <DownloadIcon />
              </button>
            )}
            <button className="lightbox-btn" onClick={() => setLightbox(null)} title="Close">
              <CloseIcon />
            </button>
          </div>
          <div className="lightbox-content" onClick={(e) => e.stopPropagation()}>
            {lightbox.type === 'video' ? (
              <video src={lightbox.src} controls playsInline autoPlay />
            ) : (
              <img src={lightbox.src} alt="" />
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
