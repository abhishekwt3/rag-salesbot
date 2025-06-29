// AI Chat Bar Widget JavaScript - Enhanced Salesbot Style
;(() => {
  let widgetConfig = {}
  let isExpanded = false
  let sessionId = null
  const messages = []
  let isLoading = false

  // Generate session ID
  function generateSessionId() {
    return "salesbot_" + Math.random().toString(36).substr(2, 9) + "_" + Date.now()
  }

  // Create widget HTML with enhanced design
  function createWidgetHTML() {
    return `
      <div id="ai-chat-bar-widget" class="ai-chat-bar-widget">
        <!-- Bot Status Indicator -->
        <div class="ai-chat-bot-indicator" title="AI Assistant Online">
          🤖
        </div>

        <!-- Messages Container (expandable) -->
        <div id="ai-chat-messages-container" class="ai-chat-messages-container">
          <!-- Welcome Message -->
          <div class="ai-chat-welcome">
            <strong>Hi! I'm your AI sales assistant.</strong><br>
            ${widgetConfig.welcomeMessage || "I can help you with product information, pricing, and answer any questions about our services. What would you like to know?"}
          </div>
          
          <!-- Messages Area -->
          <div id="ai-chat-messages" class="ai-chat-messages">
          </div>
        </div>

        <!-- Expand/Collapse Button -->
        <button id="ai-chat-expand-btn" class="ai-chat-expand-btn" title="Expand chat">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 14l5-5 5 5z"/>
          </svg>
        </button>

        <!-- Input Container -->
        <div id="ai-chat-input-container" class="ai-chat-input-container">
          <textarea 
            id="ai-chat-input" 
            class="ai-chat-input" 
            placeholder="${widgetConfig.placeholderText || "Ask me anything about our products..."}"
            rows="1"
            maxlength="2000"
          ></textarea>
          <button id="ai-chat-send" class="ai-chat-send" title="Send message">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>

        <!-- Branding -->
        ${
          widgetConfig.showBranding !== false
            ? `
          <div class="ai-chat-branding">
            Powered by <a href="#" target="_blank">salesbot</a>
          </div>
        `
            : ""
        }
      </div>
    `
  }

  // Add message to chat with enhanced styling
  function addMessage(content, isUser = false, type = "normal") {
    const messagesContainer = document.getElementById("ai-chat-messages")
    const messageDiv = document.createElement("div")

    let className = `ai-chat-message ${isUser ? "user" : "bot"}`
    if (type === "error") className += " error"
    if (type === "system") className += " system"

    messageDiv.className = className
    messageDiv.textContent = content

    messagesContainer.appendChild(messageDiv)

    // Auto-scroll to bottom with smooth behavior
    messagesContainer.scrollTo({
      top: messagesContainer.scrollHeight,
      behavior: "smooth",
    })

    // Expand chat if not already expanded and it's a user message
    if (isUser && !isExpanded) {
      toggleChat()
    }
  }

  // Show enhanced typing indicator
  function showTypingIndicator() {
    const messagesContainer = document.getElementById("ai-chat-messages")
    const typingDiv = document.createElement("div")
    typingDiv.id = "ai-chat-typing"
    typingDiv.className = "ai-chat-typing"
    typingDiv.innerHTML = `
      <div class="ai-chat-typing-dot"></div>
      <div class="ai-chat-typing-dot"></div>
      <div class="ai-chat-typing-dot"></div>
    `

    messagesContainer.appendChild(typingDiv)
    messagesContainer.scrollTo({
      top: messagesContainer.scrollHeight,
      behavior: "smooth",
    })
  }

  // Hide typing indicator
  function hideTypingIndicator() {
    const typingIndicator = document.getElementById("ai-chat-typing")
    if (typingIndicator) {
      typingIndicator.remove()
    }
  }

  // Enhanced send message with better error handling
  async function sendMessage(message) {
    if (!message.trim() || isLoading) return

    isLoading = true
    const input = document.getElementById("ai-chat-input")
    const sendButton = document.getElementById("ai-chat-send")
    const inputContainer = document.getElementById("ai-chat-input-container")

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
      const response = await fetch(`${widgetConfig.apiUrl}/widget/${widgetConfig.widgetKey}/chat`, {
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

        // Simulate realistic response delay
        setTimeout(() => {
          addMessage(data.response || data.message, false)
        }, 500)

        // Update session ID if provided
        if (data.session_id) {
          sessionId = data.session_id
        }
      } else {
        hideTypingIndicator()
        addMessage("I'm having trouble responding right now. Please try again in a moment.", false, "error")
      }
    } catch (error) {
      console.error("Chat error:", error)
      hideTypingIndicator()
      addMessage("Network error. Please check your connection and try again.", false, "error")
    } finally {
      // Remove loading state
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
    const message = input.value.trim()

    if (message) {
      sendMessage(message)
    }
  }

  // Enhanced auto-resize with smooth transitions
  function autoResize(textarea) {
    textarea.style.height = "auto"
    const newHeight = Math.min(Math.max(textarea.scrollHeight, 24), 120)
    textarea.style.height = newHeight + "px"

    // Adjust container height smoothly
    const container = textarea.closest(".ai-chat-input-container")
    if (container) {
      const minHeight = 56
      const containerHeight = Math.max(minHeight, newHeight + 32)
      container.style.minHeight = containerHeight + "px"
    }
  }

  // Enhanced toggle chat with better animations
  function toggleChat() {
    const container = document.getElementById("ai-chat-messages-container")
    const expandBtn = document.getElementById("ai-chat-expand-btn")

    if (isExpanded) {
      container.classList.remove("expanded")
      expandBtn.classList.remove("expanded")
      expandBtn.title = "Expand chat"
      isExpanded = false
    } else {
      container.classList.add("expanded")
      expandBtn.classList.add("expanded")
      expandBtn.title = "Collapse chat"
      isExpanded = true

      // Focus input when expanded with delay for animation
      setTimeout(() => {
        const input = document.getElementById("ai-chat-input")
        if (input) {
          input.focus()
          // Add welcome interaction if first time
          if (messages.length === 0) {
            setTimeout(() => {
              addMessage("Feel free to ask me anything about our products or services!", false, "system")
            }, 800)
          }
        }
      }, 400)
    }
  }

  // Enhanced event listeners
  function setupEventListeners() {
    // Expand/collapse button
    document.getElementById("ai-chat-expand-btn").addEventListener("click", toggleChat)

    // Send button
    document.getElementById("ai-chat-send").addEventListener("click", handleSubmit)

    // Input handling
    const input = document.getElementById("ai-chat-input")

    // Auto-resize on input
    input.addEventListener("input", (e) => {
      autoResize(e.target)
    })

    // Enhanced keyboard handling
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        handleSubmit()
      }

      // Expand on typing if not expanded
      if (!isExpanded && e.key.length === 1) {
        toggleChat()
      }
    })

    // Focus input on click
    input.addEventListener("click", () => {
      if (!isExpanded) {
        toggleChat()
      }
    })

    // Paste handling
    input.addEventListener("paste", (e) => {
      setTimeout(() => autoResize(input), 0)
    })

    // Enhanced keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && isExpanded) {
        toggleChat()
      }

      // Ctrl/Cmd + K to focus chat
      if ((e.ctrlKey || e.metaKey) && e.key === "k" && !isExpanded) {
        e.preventDefault()
        toggleChat()
      }
    })

    // Click outside to collapse (optional)
    document.addEventListener("click", (e) => {
      const widget = document.getElementById("ai-chat-bar-widget")
      if (isExpanded && !widget.contains(e.target)) {
        // Only collapse if user clicked far from widget
        const rect = widget.getBoundingClientRect()
        const clickX = e.clientX
        const clickY = e.clientY

        if (
          clickX < rect.left - 50 ||
          clickX > rect.right + 50 ||
          clickY < rect.top - 50 ||
          clickY > rect.bottom + 50
        ) {
          toggleChat()
        }
      }
    })
  }

  // Load widget configuration with enhanced error handling
  async function loadWidgetConfig() {
    try {
      const response = await fetch(`${widgetConfig.apiUrl}/widget/${widgetConfig.widgetKey}/config`)
      if (response.ok) {
        const config = await response.json()
        Object.assign(widgetConfig, config)
      }
    } catch (error) {
      console.warn("Failed to load widget config, using defaults:", error)
    }
  }

  // Enhanced initialization
  window.initChatWidget = async (config) => {
    widgetConfig = {
      primaryColor: "#119da4",
      welcomeMessage:
        "I can help you with product information, pricing, and answer any questions about our services. What would you like to know?",
      placeholderText: "Ask me anything about our products...",
      showBranding: true,
      ...config,
    }

    sessionId = generateSessionId()

    // Load additional config from API
    await loadWidgetConfig()

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

    console.log("Enhanced Salesbot Chat Widget initialized successfully")
  }

  // Handle widget removal
  window.removeChatWidget = () => {
    const widget = document.getElementById("ai-chat-bar-widget")
    if (widget) {
      widget.style.animation = "slideOutDown 0.3s ease-in-out"
      setTimeout(() => widget.remove(), 300)
    }
  }

  // Auto-initialize fallback
  document.addEventListener("DOMContentLoaded", () => {
    const textareas = document.querySelectorAll(".ai-chat-input")
    textareas.forEach((textarea) => {
      autoResize(textarea)
    })
  })
})()
