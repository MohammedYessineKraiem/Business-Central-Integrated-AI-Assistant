(function () {
        // 📦 [1] Create and inject the entire chat UI inside Business Central
    document.body.innerHTML = `
        <div class="container" id="chat-container">
            <div class="floating-particles"></div>
            
            <!-- Resize handles -->
            <div class="resize-handle top" data-direction="top"></div>
            <div class="resize-handle bottom" data-direction="bottom"></div>
            <div class="resize-handle left" data-direction="left"></div>
            <div class="resize-handle right" data-direction="right"></div>
            <div class="resize-handle top-left" data-direction="top-left"></div>
            <div class="resize-handle top-right" data-direction="top-right"></div>
            <div class="resize-handle bottom-left" data-direction="bottom-left"></div>
            <div class="resize-handle bottom-right" data-direction="bottom-right"></div>
            
            <div class="header" id="header">
                <div class="logo">
                    <div class="logo-icon">🤖</div>
                    <h1>XPilot Assistant</h1>
                </div>
                <div class="controls">
                    <div class="model-selector">
                        <select id="model-select">
                            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                            <option value="groq">Groq</option>
                            <option value="mistral-7b">Mistral 7B</option>
                            <option value="together-ai">Together AI</option>
                            <option value="claude-3">Claude 3</option>
                        </select>
                    </div>
                    <div class="mode-selector">
                        <select id="mode-select">
                            <option value="all">All (Hybrid)</option>
                            <option value="ask">Ask</option>
                            <option value="agent">Agent</option>
                        </select>
                    </div>
                    <button class="dashboard-btn" id="open-dashboard">📊</button>
                </div>
            </div>

            <div class="chat-window" id="chat-window">
                <div class="welcome-message">
                    <p>✨ Welcome to XPilot Assistant! ✨</p>
                    <p>Choose your AI model and start chatting. I'm here to help with anything you need.</p>
                </div>
            </div>

            <div class="input-area">
                <div class="input-container">
                    <input type="text" class="prompt-input" id="prompt-input" placeholder="Type your message..." />
                    <button class="send-btn" id="send-btn">
                        <span>Send</span>
                        <span>🚀</span>
                    </button>
                </div>
            </div>
        </div>
    `;

    // Dragging and resizing functionality
    const container = document.getElementById('chat-container');
    const header = document.getElementById('header');
    const resizeHandles = document.querySelectorAll('.resize-handle');
    
    let isDragging = false;
    let isResizing = false;
    let currentResizeHandle = null;
    let startX = 0;
    let startY = 0;
    let startWidth = 0;
    let startHeight = 0;
    let startLeft = 0;
    let startTop = 0;
    let dragOffsetX = 0;
    let dragOffsetY = 0;

    // Initialize container position
    function initializeContainer() {
        const rect = container.getBoundingClientRect();
        startLeft = rect.left;
        startTop = rect.top;
        startWidth = rect.width;
        startHeight = rect.height;
        
        // Set initial position
        container.style.left = startLeft + 'px';
        container.style.top = startTop + 'px';
        container.style.width = startWidth + 'px';
        container.style.height = startHeight + 'px';
        container.style.transform = 'none';
    }

    // Dragging functionality
    function startDrag(e) {
        // Don't start drag if clicking on interactive elements
        if (e.target.tagName === 'SELECT' || e.target.tagName === 'BUTTON' || e.target.tagName === 'INPUT') {
            return;
        }
        
        isDragging = true;
        container.classList.add('dragging');
        
        const rect = container.getBoundingClientRect();
        dragOffsetX = e.clientX - rect.left;
        dragOffsetY = e.clientY - rect.top;
        
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', endDrag);
        e.preventDefault();
    }

    function drag(e) {
        if (!isDragging) return;
        
        let newLeft = e.clientX - dragOffsetX;
        let newTop = e.clientY - dragOffsetY;
        
        // Keep container within viewport bounds
        const maxLeft = window.innerWidth - container.offsetWidth;
        const maxTop = window.innerHeight - container.offsetHeight;
        
        newLeft = Math.max(0, Math.min(newLeft, maxLeft));
        newTop = Math.max(0, Math.min(newTop, maxTop));
        
        container.style.left = newLeft + 'px';
        container.style.top = newTop + 'px';
    }

    function endDrag() {
        isDragging = false;
        container.classList.remove('dragging');
        document.removeEventListener('mousemove', drag);
        document.removeEventListener('mouseup', endDrag);
    }

    // Resizing functionality
    function startResize(e, handle) {
        isResizing = true;
        currentResizeHandle = handle;
        container.classList.add('resizing');
        handle.classList.add('active');
        
        const rect = container.getBoundingClientRect();
        startX = e.clientX;
        startY = e.clientY;
        startWidth = rect.width;
        startHeight = rect.height;
        startLeft = rect.left;
        startTop = rect.top;
        
        document.addEventListener('mousemove', resize);
        document.addEventListener('mouseup', endResize);
        e.preventDefault();
        e.stopPropagation();
    }

    function resize(e) {
        if (!isResizing) return;
        
        const deltaX = e.clientX - startX;
        const deltaY = e.clientY - startY;
        const direction = currentResizeHandle.dataset.direction;
        
        let newWidth = startWidth;
        let newHeight = startHeight;
        let newLeft = startLeft;
        let newTop = startTop;
        
        const minWidth = 400;
        const minHeight = 300;
        const maxWidth = window.innerWidth;
        const maxHeight = window.innerHeight;
        
        switch (direction) {
            case 'right':
                newWidth = Math.max(minWidth, Math.min(maxWidth - startLeft, startWidth + deltaX));
                break;
            case 'bottom':
                newHeight = Math.max(minHeight, Math.min(maxHeight - startTop, startHeight + deltaY));
                break;
            case 'left':
                newWidth = Math.max(minWidth, startWidth - deltaX);
                newLeft = Math.max(0, Math.min(startLeft + deltaX, startLeft + startWidth - minWidth));
                break;
            case 'top':
                newHeight = Math.max(minHeight, startHeight - deltaY);
                newTop = Math.max(0, Math.min(startTop + deltaY, startTop + startHeight - minHeight));
                break;
            case 'bottom-right':
                newWidth = Math.max(minWidth, Math.min(maxWidth - startLeft, startWidth + deltaX));
                newHeight = Math.max(minHeight, Math.min(maxHeight - startTop, startHeight + deltaY));
                break;
            case 'bottom-left':
                newWidth = Math.max(minWidth, startWidth - deltaX);
                newHeight = Math.max(minHeight, Math.min(maxHeight - startTop, startHeight + deltaY));
                newLeft = Math.max(0, Math.min(startLeft + deltaX, startLeft + startWidth - minWidth));
                break;
            case 'top-right':
                newWidth = Math.max(minWidth, Math.min(maxWidth - startLeft, startWidth + deltaX));
                newHeight = Math.max(minHeight, startHeight - deltaY);
                newTop = Math.max(0, Math.min(startTop + deltaY, startTop + startHeight - minHeight));
                break;
            case 'top-left':
                newWidth = Math.max(minWidth, startWidth - deltaX);
                newHeight = Math.max(minHeight, startHeight - deltaY);
                newLeft = Math.max(0, Math.min(startLeft + deltaX, startLeft + startWidth - minWidth));
                newTop = Math.max(0, Math.min(startTop + deltaY, startTop + startHeight - minHeight));
                break;
        }
        
        container.style.width = newWidth + 'px';
        container.style.height = newHeight + 'px';
        container.style.left = newLeft + 'px';
        container.style.top = newTop + 'px';
    }

    function endResize() {
        isResizing = false;
        container.classList.remove('resizing');
        if (currentResizeHandle) {
            currentResizeHandle.classList.remove('active');
        }
        currentResizeHandle = null;
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', endResize);
    }

    // Event listeners for dragging and resizing
    header.addEventListener('mousedown', startDrag);
    
    resizeHandles.forEach(handle => {
        handle.addEventListener('mousedown', (e) => startResize(e, handle));
    });

    // Initialize container position after DOM is ready
    setTimeout(() => {
        initializeContainer();
    }, 0);

    // Initialize particles
    function createParticles() {
        const particleContainer = document.querySelector('.floating-particles');
        setInterval(() => {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 2 + 's';
            particleContainer.appendChild(particle);

            setTimeout(() => {
                particle.remove();
            }, 8000);
        }, 3000);
    }

    // Chat functionality
    const chatWindow = document.getElementById('chat-window');
    const promptInput = document.getElementById('prompt-input');
    const sendBtn = document.getElementById('send-btn');
    const modelSelect = document.getElementById('model-select');
    const modeSelect = document.getElementById('mode-select');
    //functions 

    // API endpoints for different modes
    const endpoints = {
    chat: 'http://localhost:5135/copilot/chat',
    agent: 'http://localhost:5135/copilot/command',
    unified: 'http://localhost:5135/copilot/unified' // Optional future use
};


    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'bubble';
        bubbleDiv.textContent = text;
        
        messageDiv.appendChild(bubbleDiv);
        chatWindow.appendChild(messageDiv);
        
        // Remove welcome message if it exists
        const welcomeMsg = chatWindow.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }
        
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.innerHTML = `
            <div class="typing-indicator" style="display: flex;">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <span>XPilot is thinking...</span>
            </div>
        `;
        chatWindow.appendChild(typingDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return typingDiv;
    }

    function removeTypingIndicator(indicator) {
        if (indicator) {
            indicator.remove();
        }
    }
    async function sendMessage() {
        const prompt = promptInput.value.trim();
        const model = modelSelect.value;
        const mode = modeSelect.value;

        if (!prompt) return;

        appendMessage('user', prompt);
        promptInput.value = '';

        const typingIndicator = showTypingIndicator();

        try {
            let response = '';

            if (mode === 'ask') {
                response = await callALSendPrompt(prompt, model);
            } else if (mode === 'agent') {
                response = await callALSendCommand(prompt, model);
            } else if (mode === 'all' || mode === 'hybrid') {
                const classification = await callALSendClassification(prompt, model);

                if (classification === 'Question') {
                    response = await callALSendPrompt(prompt, model);
                } else if (classification === 'Command') {
                    response = await callALSendCommand(prompt, model);
                } else {
                    showToast("🧐 Prompt could not be classified.", 4000);
                    
                }
            } else {
                throw new Error(`Unsupported mode: ${mode}`);
            }
            showResponseFromAL(response);
            removeTypingIndicator(typingIndicator);
            appendMessage('bot', response);
            showToast("✅ Response received", 2500);
        } catch (error) {
            removeTypingIndicator(typingIndicator);
            appendMessage('bot', `⚠️ Error: ${error}`);
            showToast(`❌ Error: ${error.message}`, 5000);
        }

    }
    function callALSendPrompt(prompt, model) {
        return new Promise((resolve, reject) => {
            // Increase timeout to 10 seconds to avoid premature timeouts
            let timeout = setTimeout(() => reject("AL timeout"), 10000);

            // This function will be called by AL to send the response back
            window.ReceiveALResponse = (responseText) => {
                clearTimeout(timeout); // clear timeout on success
                resolve(responseText); // resolve promise with response
            };

            // Call AL extensibility method with prompt and model
            Microsoft.Dynamics.NAV.InvokeExtensibilityMethod(
                'SendPrompt',
                [prompt, model]
            );
        });
    }

    function callALSendCommand(prompt, model) {
        return new Promise((resolve, reject) => {
            let timeout = setTimeout(() => reject("AL timeout"), 3000);

            // Define what happens when AL responds
            window.ReceiveALResponse = (responseText) => {
                clearTimeout(timeout);
                resolve(responseText);
            };

            // Trigger AL from JS using the extensibility method
            Microsoft.Dynamics.NAV.InvokeExtensibilityMethod(
                'SendCommand',
                [prompt, model]
            );
        });
    }

    function callALSendClassification(prompt, model) {
        return new Promise((resolve, reject) => {
            let timeout = setTimeout(() => reject("Timeout on classification"), 10000);

            window.ReceiveALResponse = (responseText) => {
                clearTimeout(timeout);
                resolve(responseText);
            };

            Microsoft.Dynamics.NAV.InvokeExtensibilityMethod("SendClassification", [prompt, model]);
        });
    }
    function showResponseFromAL(rawText) {
        const box = document.getElementById("response-box");
        if (box) {
            box.innerHTML = rawText.replace(/\n/g, "<br>");
        } else {
            console.error("❌ #response-box not found");
        }
    }



    function showToast(message, duration = 3000) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 100); // fade-in
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300); // fade-out and remove
        }, duration);
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    
    promptInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    document.getElementById('open-dashboard').addEventListener('click', () => {
        window.open('https://your-dashboard-url.com', '_blank');
    });

    // Auto-resize input
    promptInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });

    // Initialize particles
    createParticles();

    // Add some sample messages for demo
    setTimeout(() => {
        appendMessage('bot', 'Hello! I\'m XPilot Assistant. How can I help you today?');
    }, 1000);

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // ESC to center the container
        if (e.key === 'Escape') {
            container.style.left = '50%';
            container.style.top = '50%';
            container.style.transform = 'translate(-50%, -50%)';
            setTimeout(() => {
                container.style.transform = 'none';
                const rect = container.getBoundingClientRect();
                container.style.left = rect.left + 'px';
                container.style.top = rect.top + 'px';
            }, 300);
        }
        
        // Ctrl+R to reset size
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            container.style.width = '900px';
            container.style.height = '700px';
        }
    });

    // Handle window resize
    window.addEventListener('resize', () => {
        const rect = container.getBoundingClientRect();
        
        // Keep container within bounds
        let newLeft = rect.left;
        let newTop = rect.top;
        
        const maxLeft = window.innerWidth - rect.width;
        const maxTop = window.innerHeight - rect.height;
        
        if (newLeft > maxLeft) newLeft = maxLeft;
        if (newTop > maxTop) newTop = maxTop;
        if (newLeft < 0) newLeft = 0;
        if (newTop < 0) newTop = 0;
        
        container.style.left = newLeft + 'px';
        container.style.top = newTop + 'px';
    });

    // Double-click header to toggle size
    let isMaximized = false;
    let previousSize = { width: 900, height: 700, left: 0, top: 0 };
    
    header.addEventListener('dblclick', (e) => {
        e.preventDefault();
        
        if (!isMaximized) {
            // Store current size and position
            const rect = container.getBoundingClientRect();
            previousSize = {
                width: rect.width,
                height: rect.height,
                left: rect.left,
                top: rect.top
            };
            
            // Maximize
            container.style.width = (window.innerWidth - 20) + 'px';
            container.style.height = (window.innerHeight - 20) + 'px';
            container.style.left = '10px';
            container.style.top = '10px';
            isMaximized = true;
        } else {
            // Restore
            container.style.width = previousSize.width + 'px';
            container.style.height = previousSize.height + 'px';
            container.style.left = previousSize.left + 'px';
            container.style.top = previousSize.top + 'px';
            isMaximized = false;
        }
    });
})();