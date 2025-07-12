// YC Coach App JavaScript with Login
class YCCoach {
    constructor() {
        this.conversationHistory = [];
        this.apiUrl = 'https://j59j74jwbg.execute-api.us-east-1.amazonaws.com/prod/chat';
        this.isLoading = false;
        this.isLoggedIn = false;
        this.correctPassword = 'yc-coach-2025'; // Will be replaced during deployment
        
        this.initializeApp();
    }
    
    initializeApp() {
        // Check if already logged in (session storage)
        if (sessionStorage.getItem('ycCoachLoggedIn') === 'true') {
            this.showMainApp();
        } else {
            this.showLoginScreen();
        }
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }
        
        // Logout button
        const logoutButton = document.getElementById('logoutButton');
        if (logoutButton) {
            logoutButton.addEventListener('click', () => this.handleLogout());
        }
        
        // Main app event listeners
        const userInput = document.getElementById('userInput');
        const sendButton = document.getElementById('sendButton');
        
        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        if (userInput) {
            // Send message on Ctrl+Enter
            userInput.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            // Auto-resize textarea
            userInput.addEventListener('input', () => {
                userInput.style.height = 'auto';
                userInput.style.height = userInput.scrollHeight + 'px';
            });
        }
    }
    
    handleLogin(e) {
        e.preventDefault();
        const passwordInput = document.getElementById('passwordInput');
        const loginError = document.getElementById('loginError');
        const password = passwordInput.value.trim();
        
        if (password === this.correctPassword) {
            // Successful login
            sessionStorage.setItem('ycCoachLoggedIn', 'true');
            this.isLoggedIn = true;
            this.showMainApp();
            loginError.style.display = 'none';
        } else {
            // Failed login
            loginError.textContent = 'Incorrect password. Please try again.';
            loginError.style.display = 'block';
            passwordInput.value = '';
            passwordInput.focus();
        }
    }
    
    handleLogout() {
        sessionStorage.removeItem('ycCoachLoggedIn');
        this.isLoggedIn = false;
        this.conversationHistory = [];
        this.showLoginScreen();
        
        // Clear chat
        const chatContainer = document.getElementById('chatContainer');
        if (chatContainer) {
            chatContainer.innerHTML = `
                <div class="message ai-message">
                    <div class="message-content">
                        Welcome! I'm your Y Combinator application coach. I'll help you craft compelling answers based on 30+ successful applications.
                        <br><br>
                        <strong>⚠️ Important:</strong> Please wait 30+ seconds between messages to avoid AWS rate limiting.
                        <br><br>
                        Let's start with the key question: <strong>"What is your company going to make? Please describe your product and what it does or will do."</strong>
                        <br><br>
                        Share your initial idea, and I'll help you refine it into a strong YC application response.
                    </div>
                </div>
            `;
        }
    }
    
    showLoginScreen() {
        document.getElementById('loginScreen').style.display = 'flex';
        document.getElementById('mainApp').style.display = 'none';
        
        // Focus on password input
        setTimeout(() => {
            const passwordInput = document.getElementById('passwordInput');
            if (passwordInput) {
                passwordInput.focus();
            }
        }, 100);
    }
    
    showMainApp() {
        document.getElementById('loginScreen').style.display = 'none';
        document.getElementById('mainApp').style.display = 'block';
        this.isLoggedIn = true;
    }
    
    async sendMessage() {
        if (this.isLoading || !this.isLoggedIn) return;
        
        const userInput = document.getElementById('userInput');
        const message = userInput.value.trim();
        
        if (!message) {
            this.showError('Please enter a message');
            return;
        }
        
        // Add user message to chat
        this.addMessageToChat(message, 'user');
        
        // Clear input and show loading
        userInput.value = '';
        userInput.style.height = 'auto';
        this.setLoading(true);
        
        try {
            // Call API with current conversation history (NOT including current message)
            const response = await this.callAPI(message);
            
            // Add AI response to chat
            this.addMessageToChat(response.response, 'ai');
            
            // NOW add both messages to conversation history
            this.conversationHistory.push({
                role: 'user',
                content: message
            });
            this.conversationHistory.push({
                role: 'assistant',
                content: response.response
            });
            
        } catch (error) {
            console.error('Error:', error);
            this.showError('Sorry, there was an error processing your request. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }
    
    async callAPI(message) {
        console.log('callAPI called with:', message);
        console.log('API URL:', this.apiUrl);
        console.log('Conversation history length:', this.conversationHistory.length);
        
        // Check if API URL is configured
        if (this.apiUrl === 'YOUR_API_GATEWAY_URL_HERE') {
            throw new Error('API Gateway URL not configured. Please set up API Gateway first.');
        }
        
        const requestBody = {
            message: message,
            history: this.conversationHistory,
            timestamp: Date.now()  // Cache busting
        };
        
        console.log('Request body:', requestBody);
        
        const response = await fetch(this.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.log('Error response:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        // Log usage info if available (for debugging)
        if (data.tokens_used) {
            console.log(`Tokens used: ${data.tokens_used}, Model: ${data.model_used}`);
        }
        
        return data;
    }
    
    addMessageToChat(message, sender) {
        const chatContainer = document.getElementById('chatContainer');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = message;
        
        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    showError(errorMessage) {
        this.addMessageToChat(errorMessage, 'ai');
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        const sendButton = document.getElementById('sendButton');
        const buttonText = document.getElementById('buttonText');
        const loadingSpinner = document.getElementById('loadingSpinner');
        
        if (sendButton && buttonText && loadingSpinner) {
            if (loading) {
                sendButton.disabled = true;
                buttonText.style.display = 'none';
                loadingSpinner.style.display = 'inline';
            } else {
                sendButton.disabled = false;
                buttonText.style.display = 'inline';
                loadingSpinner.style.display = 'none';
            }
        }
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.ycCoach = new YCCoach();
});

// Global function for the button onclick (backup)
function sendMessage() {
    if (window.ycCoach) {
        window.ycCoach.sendMessage();
    }
}
