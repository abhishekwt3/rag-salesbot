// Simple Chat Bar Widget JavaScript
;(() => {
  let widgetConfig = {}
  let sessionId = null
  const messages = []
  let isLoading = false
  let isExpanded = false

  // Generate session ID
  function generateSessionId() {
    return "salesbot_" + Math.random().toString(36).substr(2, 9) + "_" + Date.now()
  }

  // Create simple widget HTML
  function createWidgetHTML() {
    return `
      <div id="ai-chat-bar-widget" class="ai-chat-bar-widget collapsed">
        <div class="ai-chat-widget-card">
          <!-- Messages Container (hidden when collapsed) -->
          <div id="ai-chat-messages-container" class="ai-chat-messages-container">
            <div id="ai-chat-messages"></div>
          </div>

          <!-- Simple Input Bar -->
          <div id="ai-chat-input-container" class="ai-chat-input-container">
            <div class="ai-chat-input-wrapper">
              <textarea 
                id="ai-chat-input" 
                class="ai-chat-input" 
                placeholder="${widgetConfig.placeholderText || "Ask me anything..."}"
                rows="1"
                maxlength="2000"
              ></textarea>
            </div>
            <button id="ai-chat-send" class="ai-chat-send" title="Send message">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    `
  }

  // Add message to chat
  function addMessage(content, isUser = false, type = "normal") {
    const messagesContainer = document.getElementById("ai-chat-messages")
    if (!messagesContainer) return

    const messageDiv = document.createElement("div")
    let className = `ai-chat-message ${isUser ? "user" : "bot"}`
    if (type === "error") className += " error"

    messageDiv.className = className
    messageDiv.innerHTML = `
      <div class="ai-chat-message-avatar">${isUser ? "" : "🤖"}</div>
      <div class="ai-chat-message-content">${content}</div>
    `

    messagesContainer.appendChild(messageDiv)
    messages.push({ content, isUser, type, timestamp: Date.now() })

    // Auto-scroll to bottom
    const container = document.getElementById("ai-chat-messages-container")
    if (container) {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: "smooth",
      })
    }
  }

  // Show typing indicator
  function showTypingIndicator() {
    const messagesContainer = document.getElementById("ai-chat-messages")
    if (!messagesContainer) return

    hideTypingIndicator()

    const typingDiv = document.createElement("div")
    typingDiv.id = "ai-chat-typing"
    typingDiv.className = "ai-chat-typing"
    typingDiv.innerHTML = `
      <div class="ai-chat-typing-avatar">🤖</div>
      <div class="ai-chat-typing-content">
        <div class="ai-chat-typing-dot"></div>
        <div class="ai-chat-typing-dot"></div>
        <div class="ai-chat-typing-dot"></div>
      </div>
    `

    messagesContainer.appendChild(typingDiv)

    const container = document.getElementById("ai-chat-messages-container")
    if (container) {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: "smooth",
      })
    }
  }

  // Hide typing indicator
  function hideTypingIndicator() {
    const typingIndicator = document.getElementById("ai-chat-typing")
    if (typingIndicator) {
      typingIndicator.remove()
    }
  }

  // Expand widget
  function expandWidget() {
    const widget = document.getElementById("ai-chat-bar-widget")
    if (widget && !isExpanded) {
      widget.classList.remove("collapsed")
      isExpanded = true

      // Focus input after animation
      setTimeout(() => {
        const input = document.getElementById("ai-chat-input")
        if (input) {
          input.focus()
        }
      }, 300)
    }
  }

  // Add collapse widget function
  function collapseWidget() {
    const widget = document.getElementById("ai-chat-bar-widget")
    if (widget && isExpanded) {
      widget.classList.add("collapsed")
      isExpanded = false
    }
  }

  // Send message function
  async function sendMessage(message) {
    if (!message.trim() || isLoading) return

    isLoading = true
    const input = document.getElementById("ai-chat-input")
    const sendButton = document.getElementById("ai-chat-send")
    const inputContainer = document.getElementById("ai-chat-input-container")

    if (!input || !sendButton || !inputContainer) return

    // Expand widget if not already expanded
    expandWidget()

    // Add loading state
    inputContainer.classList.add("loading")
    input.disabled = true
    sendButton.disabled = true

    // Add user message
    addMessage(message, true)

    // Clear input
    input.value = ""
    autoResize(input)

    // Show typing indicator
    showTypingIndicator()

    try {
      const apiUrl = widgetConfig.apiUrl || "http://localhost:8000"
      const widgetKey = widgetConfig.widgetKey || widgetConfig.botId || "default"

      const response = await fetch(`${apiUrl}/widget/${widgetKey}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId,
          timestamp: new Date().toISOString(),
        }),
      })

      if (response.ok) {
        const data = await response.json()
        hideTypingIndicator()

        setTimeout(() => {
          addMessage(data.response || data.message || "I received your message!", false)
        }, 800)

        if (data.session_id) {
          sessionId = data.session_id
        }
      } else {
        hideTypingIndicator()
        addMessage("I'm having trouble responding right now. Please try again.", false, "error")
      }
    } catch (error) {
      console.error("Chat error:", error)
      hideTypingIndicator()
      addMessage("Unable to connect. Please check your connection and try again.", false, "error")
    } finally {
      inputContainer.classList.remove("loading")
      input.disabled = false
      sendButton.disabled = false
      input.focus()
      isLoading = false
    }
  }

  // Handle form submission
  function handleSubmit(e) {
    if (e) e.preventDefault()

    const input = document.getElementById("ai-chat-input")
    if (!input) return

    const message = input.value.trim()
    if (message) {
      sendMessage(message)
    }
  }

  // Auto-resize textarea
  function autoResize(textarea) {
    if (!textarea) return
    textarea.style.height = "auto"
    const newHeight = Math.min(Math.max(textarea.scrollHeight, 20), 100)
    textarea.style.height = newHeight + "px"
  }

  // Setup event listeners
  function setupEventListeners() {
    const sendButton = document.getElementById("ai-chat-send")
    const inputContainer = document.getElementById("ai-chat-input-container")
    const input = document.getElementById("ai-chat-input")

    // Send button click
    if (sendButton) {
      sendButton.addEventListener("click", handleSubmit)
    }

    // Click on input container when collapsed
    if (inputContainer) {
      inputContainer.addEventListener("click", (e) => {
        if (!isExpanded) {
          e.preventDefault()
          expandWidget()
        }
      })
    }

    // Input handling
    if (input) {
      // Auto-resize on input
      input.addEventListener("input", (e) => {
        autoResize(e.target)
      })

      // Keyboard handling
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault()
          handleSubmit()
        }
      })

      // Paste handling
      input.addEventListener("paste", () => {
        setTimeout(() => autoResize(input), 0)
      })
    }

    // Click outside to close
    document.addEventListener("click", (e) => {
      const widget = document.getElementById("ai-chat-bar-widget")
      if (widget && isExpanded) {
        // Check if click is outside the widget
        if (!widget.contains(e.target)) {
          collapseWidget()
        }
      }
    })

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      // Escape to collapse
      if (e.key === "Escape" && isExpanded) {
        collapseWidget()
      }
    })
  }

  // Initialize widget
  window.initChatWidget = async (config = {}) => {
    widgetConfig = {
      placeholderText: "Ask me anything...",
      apiUrl: "http://localhost:8000",
      widgetKey: "default",
      ...config,
    }

    sessionId = generateSessionId()

    // Create and inject widget HTML
    const widgetElement = document.createElement("div")
    widgetElement.innerHTML = createWidgetHTML()
    document.body.appendChild(widgetElement)

    // Set up event listeners
    setupEventListeners()

    // Initialize input
    setTimeout(() => {
      const input = document.getElementById("ai-chat-input")
      if (input) {
        autoResize(input)
      }
    }, 100)

    console.log("Simple Chat Bar Widget initialized")
  }

  // Auto-initialize if script has data attributes
  document.addEventListener("DOMContentLoaded", () => {
    const script = document.querySelector('script[src*="widget-enhanced.js"]')
    if (script) {
      const config = {}
      if (script.dataset.botId) config.widgetKey = script.dataset.botId
      if (script.dataset.apiUrl) config.apiUrl = script.dataset.apiUrl

      if (config.widgetKey) {
        window.initChatWidget(config)
      }
    }
  })

  // Expose for debugging
  window.chatWidget = {
    sendMessage,
    addMessage,
    config: widgetConfig,
    sessionId: () => sessionId,
    messages: () => messages,
  }
})()
