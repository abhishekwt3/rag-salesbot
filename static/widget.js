// Simplified AI Chat Widget JavaScript
(function() {
  let config = {
    widgetKey: 'demo',
    apiUrl: 'http://localhost:8000',
    primaryColor: '#119da4',
    title: 'Chat Support',
    welcomeMessage: 'Hi! How can I help you today?',
    placeholderText: 'Type your message...',
    showBranding: true
  };
  
  let isOpen = false;
  let sessionId = generateSessionId();
  let isLoading = false;

  function generateSessionId() {
    return 'widget_' + Math.random().toString(36).substr(2, 9);
  }

  function createWidget() {
    const widgetHTML = `
      <div id="ai-chat-widget" class="ai-chat-widget">
        <div id="ai-chat-container" class="ai-chat-container">
          <div class="ai-chat-header">
            <h4 class="ai-chat-title">${config.title}</h4>
            <button id="ai-chat-close" class="ai-chat-close">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>
              </svg>
            </button>
          </div>
          
          <div id="ai-chat-messages" class="ai-chat-messages">
            <div class="ai-chat-message bot">
              ${config.welcomeMessage}
            </div>
          </div>
          
          <div class="ai-chat-input-container">
            <textarea 
              id="ai-chat-input" 
              class="ai-chat-input" 
              placeholder="${config.placeholderText}"
              rows="1"
            ></textarea>
            <button id="ai-chat-send" class="ai-chat-send">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            </button>
          </div>
          
          ${config.showBranding ? `
            <div class="ai-chat-branding">
              Powered by <a href="#" target="_blank">salesbot</a>
            </div>
          ` : ''}
        </div>
        
        <button id="ai-chat-toggle" class="ai-chat-toggle">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
          </svg>
        </button>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', widgetHTML);
    setupEventListeners();
  }

  function setupEventListeners() {
    const toggle = document.getElementById('ai-chat-toggle');
    const close = document.getElementById('ai-chat-close');
    const send = document.getElementById('ai-chat-send');
    const input = document.getElementById('ai-chat-input');

    toggle.addEventListener('click', toggleChat);
    close.addEventListener('click', closeChat);
    send.addEventListener('click', sendMessage);
    
    input.addEventListener('keypress', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    // Auto-resize textarea
    input.addEventListener('input', function() {
      this.style.height = 'auto';
      this.style.height = this.scrollHeight + 'px';
    });
  }

  function toggleChat() {
    const container = document.getElementById('ai-chat-container');
    if (isOpen) {
      closeChat();
    } else {
      container.classList.add('open');
      isOpen = true;
      document.getElementById('ai-chat-input').focus();
    }
  }

  function closeChat() {
    const container = document.getElementById('ai-chat-container');
    container.classList.remove('open');
    isOpen = false;
  }

  function addMessage(content, isUser = false) {
    const messages = document.getElementById('ai-chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `ai-chat-message ${isUser ? 'user' : 'bot'}`;
    messageDiv.textContent = content;
    
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
  }

  function showTyping() {
    const messages = document.getElementById('ai-chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'ai-chat-typing-indicator';
    typingDiv.className = 'ai-chat-typing';
    typingDiv.innerHTML = `
      <div class="ai-chat-typing-dot"></div>
      <div class="ai-chat-typing-dot"></div>
      <div class="ai-chat-typing-dot"></div>
    `;
    
    messages.appendChild(typingDiv);
    messages.scrollTop = messages.scrollHeight;
  }

  function hideTyping() {
    const typing = document.getElementById('ai-chat-typing-indicator');
    if (typing) {
      typing.remove();
    }
  }

  async function sendMessage() {
    if (isLoading) return;
    
    const input = document.getElementById('ai-chat-input');
    const message = input.value.trim();
    
    if (!message) return;

    // Add user message
    addMessage(message, true);
    input.value = '';
    input.style.height = 'auto';

    // Show typing indicator
    showTyping();
    isLoading = true;

    try {
      const response = await fetch(`${config.apiUrl}/widget/${config.widgetKey}/chat`, {
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
        hideTyping();
        addMessage(data.response || 'Sorry, I couldn\'t process that request.');
        
        if (data.session_id) {
          sessionId = data.session_id;
        }
      } else {
        hideTyping();
        addMessage('Sorry, I\'m having trouble right now. Please try again later.');
      }
    } catch (error) {
      console.error('Chat error:', error);
      hideTyping();
      addMessage('Connection error. Please check your internet and try again.');
    } finally {
      isLoading = false;
    }
  }

  // Initialize widget
  window.initChatWidget = function(userConfig) {
    config = { ...config, ...userConfig };
    
    // Apply custom color if provided
    if (config.primaryColor) {
      document.documentElement.style.setProperty('--primary-color', config.primaryColor);
    }
    
    createWidget();
  };

  // Auto-initialize if config is available
  if (typeof WIDGET_CONFIG !== 'undefined') {
    window.initChatWidget(WIDGET_CONFIG);
  }
})();