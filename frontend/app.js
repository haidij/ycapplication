// YC Coach App JavaScript
class YCCoach {
    constructor() {
        this.conversationHistory = [];
        this.apiUrl = 'YOUR_API_GATEWAY_URL_HERE'; // Update this after deployment
        this.isLoading = false;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        const userInput = document.getElementById('userInput');
        const sendButton = document.getElementById('sendButton');
        
        // Send message on button click
        sendButton.addEventListener('click', () => this.sendMessage());
        
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
    
    async sendMessage() {
        if (this.isLoading) return;
        
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
            // Add to conversation history
            this.conversationHistory.push({
                role: 'user',
                content: message
            });
            
            // Call API
            const response = await this.callAPI(message);
            
            // Add AI response to chat
            this.addMessageToChat(response.response, 'ai');
            
            // Add to conversation history
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
        // For development/testing, return a mock response
        if (this.apiUrl === 'YOUR_API_GATEWAY_URL_HERE') {
            return this.getMockResponse(message);
        }
        
        const response = await fetch(this.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: this.conversationHistory
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Log usage info if available (for debugging)
        if (data.tokens_used) {
            console.log(`Tokens used: ${data.tokens_used}, Model: ${data.model_used}`);
        }
        
        return data;
    }
    
    getMockResponse(message) {
        // Enhanced mock responses that simulate the new API coaching style
        const responses = [
            "That's a good foundation! Let me help you make this more specific. When you say 'small businesses' - what size exactly? Are we talking about 1-10 employees, or something else? And what specific inventory problems do they face that existing tools don't solve?",
            
            "I can see the direction, but let's get more concrete. Instead of 'manage inventory better' - what exactly does your platform do differently? Does it predict demand, automate reordering, track across multiple locations? What's the core feature that solves their biggest pain point?",
            
            "Good progress! Now, what problem led you to build this? Did you experience inventory issues yourself, or did you discover this through talking to small business owners? Understanding your origin story will help make this more compelling.",
            
            "This is getting clearer. Let's talk about the market - what types of small businesses specifically? Restaurants, retail stores, service businesses? Each has very different inventory needs. Focusing on one type initially will make your answer much stronger.",
            
            "Excellent! Now, what do these businesses use today for inventory management? Excel spreadsheets, basic POS systems, or nothing at all? Understanding their current solution helps explain why yours is needed and different.",
            
            "Great iteration! One more key element - do you have any early validation? Even if it's just conversations with potential customers or a simple prototype test. YC loves to see some evidence that people actually want what you're building."
        ];
        
        // Simulate more intelligent response selection based on conversation length
        const responseIndex = Math.min(this.conversationHistory.length / 2, responses.length - 1);
        const selectedResponse = responses[Math.floor(responseIndex)] || responses[responses.length - 1];
        
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({ 
                    response: selectedResponse,
                    model_used: 'mock-claude-3.5-sonnet-v2',
                    tokens_used: Math.floor(Math.random() * 200) + 100
                });
            }, 1000 + Math.random() * 2000); // Simulate API delay
        });
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

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new YCCoach();
});

// Global function for the button onclick (backup)
function sendMessage() {
    if (window.ycCoach) {
        window.ycCoach.sendMessage();
    }
}
