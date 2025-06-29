// AI Chat Bar Widget JavaScript - ChatGPT Style
(function() {
  'use strict';

  let widgetConfig = {};
  let isExpanded = false;
  let sessionId = null;
  let messages = [];
  let isLoading = false;

  // Generate session ID
  function generateSessionId() {
    return 'chatbar_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
  }

  // Create widget HTML
  function createWidgetHTML() {
    return `
      <div id="ai-chat-bar-widget" class="ai-chat-bar-widget">
        <!-- Messages Container (expandable) -->
        <div id="ai-chat-messages-container" class="ai-chat-messages-container">
          <!-- Welcome Message -->
          <div class="ai-chat-welcome">
            ${widgetConfig.welcomeMessage || 'Hi! How can I help you today?'}
          </div>
          
          <!-- Messages Area -->
          <div id="ai-chat-messages" class="ai-chat-messages">
          </div>
        </div>

        <!-- Expand/Collapse Button -->
        <button id="ai-chat-expand-btn" class="ai-chat-expand-btn" title="Expand chat">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 14l5-5 5 5z"/>
          </svg>
        </button>

        <!-- Input Container -->
        <div class="ai-chat-input-container">
          <textarea 
            id="ai-chat-input" 
            class="ai-chat-input" 
            placeholder="${widgetConfig.placeholderText || 'Ask me anything...'}"
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
        ${widgetConfig.showBranding ? `
          <div class="ai-chat-branding">
            Powered by <a href="#" target="_blank">AI Assistant</a>
          </div>
        ` : ''}
      </div>
    `;
  }

  // Add message to chat
  function addMessage(content, isUser = false) {
    const messagesContainer = document.getElementById('ai-chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `ai-chat-message ${isUser ? 'user' : 'bot'}`;
    messageDiv.textContent = content;
    
    messagesContainer.appendChild(messageDiv);
    
    // Auto-scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Expand chat if not already expanded and it's a user message
    if (isUser && !isExpanded) {
      toggleChat();
    }
  }

  // Show typing indicator
  function showTypingIndicator() {
    const messagesContainer = document.getElementById('ai-chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'ai-chat-typing';
    typingDiv.className = 'ai-chat-typing';
    typingDiv.innerHTML = `
      <div class="ai-chat-typing-dot"></div>
      <div class="ai-chat-typing-dot"></div>
      <div class="ai-chat-typing-dot"></div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Hide typing indicator
  function hideTypingIndicator() {
    const typingIndicator = document.getElementById('ai-chat-typing');
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }

  // Send message
  async function sendMessage(message) {
    if (!message.trim() || isLoading) return;

    isLoading = true;
    const input = document.getElementById('ai-chat-input');
    const sendButton = document.getElementById('ai-chat-send');
    
    // Disable input
    input.disabled = true;
    sendButton.disabled = true;

    // Add user message
    addMessage(message, true);
    
    // Clear input
    input.value = '';
    autoResize(input);

    // Show typing indicator
    showTypingIndicator();

    try {
      const response = await fetch(`${widgetConfig.apiUrl}/widget/${widgetConfig.widgetKey}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId
        })
      });

      if (response.ok) {
        const data = await response.json();
        hideTypingIndicator();
        addMessage(data.response, false);
        
        // Update session ID if provided
        if (data.session_id) {
          sessionId = data.session_id;
        }
      } else {
        hideTypingIndicator();
        addMessage("Sorry, I'm having trouble responding right now. Please try again.", false);
      }
    } catch (error) {
      console.error('Chat error:', error);
      hideTypingIndicator();
      addMessage("Network error. Please check your connection and try again.", false);
    } finally {
      // Re-enable input
      input.disabled = false;
      sendButton.disabled = false;
      input.focus();
      isLoading = false;
    }
  }

  // Handle form submission
  function handleSubmit(e) {
    if (e) e.preventDefault();
    
    const input = document.getElementById('ai-chat-input');
    const message = input.value.trim();
    
    if (message) {
      sendMessage(message);
    }
  }

  // Auto-resize textarea
  function autoResize(textarea) {
    textarea.style.height = '40px';
    const newHeight = Math.min(Math.max(textarea.scrollHeight, 40), 80);
    textarea.style.height = newHeight + 'px';
    
    // Adjust container height if needed
    const container = textarea.closest('.ai-chat-input-container');
    if (container) {
      const minHeight = 56;
      const containerHeight = Math.max(minHeight, newHeight + 16);
      container.style.height = containerHeight + 'px';
    }
  }

  // Toggle chat expansion
  function toggleChat() {
    const container = document.getElementById('ai-chat-messages-container');
    const expandBtn = document.getElementById('ai-chat-expand-btn');
    
    if (isExpanded) {
      container.classList.remove('expanded');
      expandBtn.classList.remove('expanded');
      expandBtn.title = 'Expand chat';
      isExpanded = false;
    } else {
      container.classList.add('expanded');
      expandBtn.classList.add('expanded');
      expandBtn.title = 'Collapse chat';
      isExpanded = true;
      
      // Focus input when expanded
      setTimeout(() => {
        const input = document.getElementById('ai-chat-input');
        if (input) input.focus();
      }, 300);
    }
  }

  // Set up event listeners
  function setupEventListeners() {
    // Expand/collapse button
    document.getElementById('ai-chat-expand-btn').addEventListener('click', toggleChat);
    
    // Send button
    document.getElementById('ai-chat-send').addEventListener('click', handleSubmit);
    
    // Input handling
    const input = document.getElementById('ai-chat-input');
    
    // Auto-resize on input
    input.addEventListener('input', (e) => {
      autoResize(e.target);
    });
    
    // Enter to send (Shift+Enter for new line)
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    });

    // Focus input on click (if not expanded, expand first)
    input.addEventListener('click', () => {
      if (!isExpanded) {
        toggleChat();
      }
    });

    // Paste handling
    input.addEventListener('paste', (e) => {
      setTimeout(() => autoResize(input), 0);
    });

    // Close on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && isExpanded) {
        toggleChat();
      }
    });

    // Click outside to collapse (optional - uncomment if desired)
    // document.addEventListener('click', (e) => {
    //   const widget = document.getElementById('ai-chat-bar-widget');
    //   if (isExpanded && !widget.contains(e.target)) {
    //     toggleChat();
    //   }
    // });
  }

  // Apply custom colors
  function applyCustomColors() {
    const root = document.documentElement;
    root.style.setProperty('--widget-primary-color', widgetConfig.primaryColor || '#2563eb');
    
    // Generate darker shade for hover states
    const color = widgetConfig.primaryColor || '#2563eb';
    const darkerColor = darkenColor(color, 0.1);
    root.style.setProperty('--widget-primary-color-dark', darkerColor);
  }

  // Darken color utility
  function darkenColor(color, amount) {
    const num = parseInt(color.replace("#", ""), 16);
    const amt = Math.round(2.55 * amount * 100);
    const R = (num >> 16) - amt;
    const G = (num >> 8 & 0x00FF) - amt;
    const B = (num & 0x0000FF) - amt;
    return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
      (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
      (B < 255 ? B < 1 ? 0 : B : 255))
      .toString(16).slice(1);
  }

  // Load widget configuration
  async function loadWidgetConfig() {
    try {
      const response = await fetch(`${widgetConfig.apiUrl}/widget/${widgetConfig.widgetKey}/config`);
      if (response.ok) {
        const config = await response.json();
        // Merge with initial config
        Object.assign(widgetConfig, config);
      }
    } catch (error) {
      console.error('Failed to load widget config:', error);
    }
  }

  // Initialize widget
  window.initChatWidget = async function(config) {
    widgetConfig = config;
    sessionId = generateSessionId();

    // Load additional config from API
    await loadWidgetConfig();

    // Create and inject widget HTML
    const widgetElement = document.createElement('div');
    widgetElement.innerHTML = createWidgetHTML();
    document.body.appendChild(widgetElement);

    // Apply custom styling
    applyCustomColors();

    // Set up event listeners
    setupEventListeners();

    // Focus on the input initially and set proper height
    setTimeout(() => {
      const input = document.getElementById('ai-chat-input');
      if (input) {
        input.focus();
        autoResize(input);
      }
    }, 100);

    console.log('AI Chat Bar Widget initialized successfully');
  };

  // Handle widget removal
  window.removeChatWidget = function() {
    const widget = document.getElementById('ai-chat-bar-widget');
    if (widget) widget.remove();
  };

  // Auto-initialize if no custom init is called (fallback)
  document.addEventListener('DOMContentLoaded', () => {
    // Auto-resize textareas on page load
    const textareas = document.querySelectorAll('.ai-chat-input');
    textareas.forEach(textarea => {
      autoResize(textarea);
    });
  });

})();