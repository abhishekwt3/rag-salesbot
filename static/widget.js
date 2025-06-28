// AI Chatbot Widget JavaScript
(function() {
  'use strict';

  let widgetConfig = {};
  let isOpen = false;
  let sessionId = null;
  let messages = [];

  // Generate session ID
  function generateSessionId() {
    return 'widget_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
  }

  // Create widget HTML
  function createWidgetHTML() {
    return `
      <!-- Chat Button -->
      <button id="ai-chat-widget-button" class="ai-chat-widget-button ${widgetConfig.position}">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
        </svg>
      </button>

      <!-- Chat Container -->
      <div id="ai-chat-widget-container" class="ai-chat-widget-container ${widgetConfig.position}">
        <!-- Header -->
        <div class="ai-chat-widget-header">
          <h3 class="ai-chat-widget-title">${widgetConfig.title}</h3>
          <button id="ai-chat-widget-close" class="ai-chat-widget-close">×</button>
        </div>

        <!-- Messages -->
        <div id="ai-chat-widget-messages" class="ai-chat-widget-messages">
          <div class="ai-chat-widget-welcome">
            ${widgetConfig.welcomeMessage}
          </div>
        </div>

        <!-- Input -->
        <div class="ai-chat-widget-input-container">
          <textarea 
            id="ai-chat-widget-input" 
            class="ai-chat-widget-input" 
            placeholder="${widgetConfig.placeholderText}"
            rows="1"
          ></textarea>
          <button id="ai-chat-widget-send" class="ai-chat-widget-send">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>

        <!-- Branding -->
        ${widgetConfig.showBranding ? `
          <div class="ai-chat-widget-branding">
            Powered by <a href="#" target="_blank">AI Assistant</a>
          </div>
        ` : ''}
      </div>
    `;
  }

  // Add message to chat
  function addMessage(content, isUser = false) {
    const messagesContainer = document.getElementById('ai-chat-widget-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `ai-chat-widget-message ${isUser ? 'user' : 'bot'}`;
    messageDiv.textContent = content;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    messages.push({ content, isUser, timestamp: Date.now() });
  }

  // Show typing indicator
  function showTyping() {
    const messagesContainer = document.getElementById('ai-chat-widget-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'ai-chat-widget-typing';
    typingDiv.className = 'ai-chat-widget-typing';
    typingDiv.innerHTML = `
      <div class="ai-chat-widget-typing-dot"></div>
      <div class="ai-chat-widget-typing-dot"></div>
      <div class="ai-chat-widget-typing-dot"></div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Hide typing indicator
  function hideTyping() {
    const typingElement = document.getElementById('ai-chat-widget-typing');
    if (typingElement) {
      typingElement.remove();
    }
  }

  // Send message to API
  async function sendMessage(message) {
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

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      sessionId = data.session_id;
      
      return data.response;
    } catch (error) {
      console.error('Widget API Error:', error);
      return "I'm sorry, I'm having trouble connecting right now. Please try again later.";
    }
  }

  // Handle input submission
  async function handleSubmit() {
    const input = document.getElementById('ai-chat-widget-input');
    const sendButton = document.getElementById('ai-chat-widget-send');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    addMessage(message, true);
    input.value = '';
    
    // Disable input
    input.disabled = true;
    sendButton.disabled = true;
    
    // Show typing
    showTyping();

    try {
      // Send to API
      const response = await sendMessage(message);
      
      // Hide typing and add response
      hideTyping();
      addMessage(response, false);
    } catch (error) {
      hideTyping();
      addMessage("I'm sorry, I encountered an error. Please try again.", false);
    } finally {
      // Re-enable input
      input.disabled = false;
      sendButton.disabled = false;
      input.focus();
    }
  }

  // Auto-resize textarea
  function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
  }

  // Toggle widget
  function toggleWidget() {
    const container = document.getElementById('ai-chat-widget-container');
    const button = document.getElementById('ai-chat-widget-button');
    
    if (isOpen) {
      container.classList.remove('show');
      isOpen = false;
    } else {
      container.classList.add('show');
      isOpen = true;
      
      // Focus input
      setTimeout(() => {
        const input = document.getElementById('ai-chat-widget-input');
        if (input) input.focus();
      }, 300);
    }
  }

  // Set up event listeners
  function setupEventListeners() {
    // Button click
    document.getElementById('ai-chat-widget-button').addEventListener('click', toggleWidget);
    
    // Close button
    document.getElementById('ai-chat-widget-close').addEventListener('click', toggleWidget);
    
    // Send button
    document.getElementById('ai-chat-widget-send').addEventListener('click', handleSubmit);
    
    // Input handling
    const input = document.getElementById('ai-chat-widget-input');
    
    // Auto-resize
    input.addEventListener('input', (e) => autoResize(e.target));
    
    // Enter to send (Shift+Enter for new line)
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    });

    // Click outside to close
    document.addEventListener('click', (e) => {
      const container = document.getElementById('ai-chat-widget-container');
      const button = document.getElementById('ai-chat-widget-button');
      
      if (isOpen && 
          !container.contains(e.target) && 
          !button.contains(e.target)) {
        toggleWidget();
      }
    });
  }

  // Apply custom colors
  function applyCustomColors() {
    const root = document.documentElement;
    root.style.setProperty('--widget-primary-color', widgetConfig.primaryColor);
    
    // Generate darker shade for hover states
    const color = widgetConfig.primaryColor;
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

    console.log('AI Chat Widget initialized successfully');
  };

  // Handle widget removal
  window.removeChatWidget = function() {
    const button = document.getElementById('ai-chat-widget-button');
    const container = document.getElementById('ai-chat-widget-container');
    
    if (button) button.remove();
    if (container) container.remove();
  };

})();