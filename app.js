/**
 * TinyGPT-MCP Frontend Application
 * Handles UI interactions and API communication
 */

class TinyGPTApp {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
        this.isProcessing = false;
        
        this.initializeElements();
        this.setupEventListeners();
        this.initializeTheme();
        this.checkServerStatus();
    }
    
    initializeElements() {
        // Input elements
        this.promptInput = document.getElementById('prompt-input');
        this.sendButton = document.getElementById('send-button');
        this.sendText = document.getElementById('send-text');
        this.loadingSpinner = document.getElementById('loading-spinner');
        this.temperatureSlider = document.getElementById('temperature');
        this.temperatureValue = document.getElementById('temperature-value');
        
        // Response elements
        this.responseSection = document.getElementById('response-section');
        this.thoughtSection = document.getElementById('thought-section');
        this.thoughtContent = document.getElementById('thought-content');
        this.toolCallsSection = document.getElementById('tool-calls-section');
        this.toolCallsContent = document.getElementById('tool-calls-content');
        this.finalAnswerSection = document.getElementById('final-answer-section');
        this.finalAnswerContent = document.getElementById('final-answer-content');
        this.processingInfo = document.getElementById('processing-info');
        this.modelName = document.getElementById('model-name');
        this.processingTime = document.getElementById('processing-time');
        
        // Status elements
        this.statusIcon = document.getElementById('status-icon');
        this.statusText = document.getElementById('status-text');
        this.toolCount = document.getElementById('tool-count');
        
        // Theme elements
        this.themeToggle = document.getElementById('theme-toggle');
    }
    
    setupEventListeners() {
        // Send button
        this.sendButton.addEventListener('click', () => this.handleSendMessage());
        
        // Enter key in textarea (Shift+Enter for new line)
        this.promptInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
        
        // Temperature slider
        this.temperatureSlider.addEventListener('input', (e) => {
            this.temperatureValue.textContent = e.target.value;
        });
        
        // Example prompts
        document.querySelectorAll('.example-prompt').forEach(button => {
            button.addEventListener('click', (e) => {
                this.promptInput.value = e.target.textContent.replace(/^"|"$/g, '');
                this.promptInput.focus();
            });
        });
        
        // Theme toggle
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
    }
    
    initializeTheme() {
        // Check for saved theme or default to light
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            document.documentElement.classList.add('dark');
        }
    }
    
    toggleTheme() {
        const isDark = document.documentElement.classList.contains('dark');
        
        if (isDark) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }
    }
    
    async checkServerStatus() {
        try {
            const response = await fetch(`${this.apiUrl}/health`);
            const data = await response.json();
            
            if (response.ok) {
                this.updateStatus('connected', 'Connected to TinyGPT-MCP');
                await this.loadAvailableTools();
            } else {
                this.updateStatus('error', 'Server error');
            }
        } catch (error) {
            this.updateStatus('disconnected', 'Disconnected - Start the backend server');
            console.error('Server connection failed:', error);
        }
    }
    
    async loadAvailableTools() {
        try {
            const response = await fetch(`${this.apiUrl}/tools`);
            const data = await response.json();
            
            if (response.ok) {
                this.toolCount.textContent = data.total_tools;
            }
        } catch (error) {
            console.error('Failed to load tools:', error);
        }
    }
    
    updateStatus(status, message) {
        this.statusText.textContent = message;
        
        // Remove all status classes
        this.statusIcon.classList.remove('bg-green-500', 'bg-red-500', 'bg-yellow-500', 'bg-gray-400');
        
        // Add appropriate status class
        switch (status) {
            case 'connected':
                this.statusIcon.classList.add('bg-green-500');
                break;
            case 'error':
                this.statusIcon.classList.add('bg-red-500');
                break;
            case 'processing':
                this.statusIcon.classList.add('bg-yellow-500');
                break;
            default:
                this.statusIcon.classList.add('bg-gray-400');
        }
    }
    
    async handleSendMessage() {
        const prompt = this.promptInput.value.trim();
        
        if (!prompt || this.isProcessing) {
            return;
        }
        
        this.setProcessingState(true);
        this.hideResponseSections();
        
        try {
            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    temperature: parseFloat(this.temperatureSlider.value)
                })
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const data = await response.json();
            this.displayResponse(data);
            
        } catch (error) {
            this.displayError(error.message);
        } finally {
            this.setProcessingState(false);
        }
    }
    
    setProcessingState(processing) {
        this.isProcessing = processing;
        this.sendButton.disabled = processing;
        
        if (processing) {
            this.sendText.classList.add('hidden');
            this.loadingSpinner.classList.remove('hidden');
            this.updateStatus('processing', 'Processing your request...');
        } else {
            this.sendText.classList.remove('hidden');
            this.loadingSpinner.classList.add('hidden');
            this.updateStatus('connected', 'Connected to TinyGPT-MCP');
        }
    }
    
    hideResponseSections() {
        this.responseSection.classList.add('hidden');
        this.thoughtSection.classList.add('hidden');
        this.toolCallsSection.classList.add('hidden');
        this.finalAnswerSection.classList.add('hidden');
        this.processingInfo.classList.add('hidden');
    }
    
    displayResponse(data) {
        this.responseSection.classList.remove('hidden');
        
        // Display thought process
        if (data.thought && data.thought.trim()) {
            this.thoughtContent.textContent = data.thought;
            this.thoughtSection.classList.remove('hidden');
        }
        
        // Display tool calls
        if (data.tool_calls && data.tool_calls.length > 0) {
            this.displayToolCalls(data.tool_calls);
            this.toolCallsSection.classList.remove('hidden');
        }
        
        // Display final answer
        if (data.final_answer) {
            this.finalAnswerContent.innerHTML = this.formatFinalAnswer(data.final_answer);
            this.finalAnswerSection.classList.remove('hidden');
        }
        
        // Display processing info
        if (data.model_info) {
            this.modelName.textContent = data.model_info.name;
            this.processingTime.textContent = data.processing_time;
            this.processingInfo.classList.remove('hidden');
        }
    }
    
    displayToolCalls(toolCalls) {
        this.toolCallsContent.innerHTML = '';
        
        toolCalls.forEach((call, index) => {
            const toolElement = this.createToolCallElement(call, index);
            this.toolCallsContent.appendChild(toolElement);
        });
    }
    
    createToolCallElement(call, index) {
        const div = document.createElement('div');
        div.className = 'p-4 border rounded-lg bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-600';
        
        const success = call.success;
        const emoji = this.getToolEmoji(call.function);
        const statusClass = success ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400';
        const statusIcon = success ? 'fa-check-circle' : 'fa-exclamation-circle';
        
        div.innerHTML = `
            <div class="flex items-start justify-between mb-2">
                <div class="flex items-center space-x-2">
                    <span class="text-lg">${emoji}</span>
                    <span class="font-medium text-gray-800 dark:text-gray-200">${call.function}</span>
                    <i class="fas ${statusIcon} ${statusClass}"></i>
                </div>
                <span class="text-xs text-gray-500 dark:text-gray-400">#${index + 1}</span>
            </div>
            
            ${Object.keys(call.arguments).length > 0 ? `
                <div class="mb-2">
                    <span class="text-sm font-medium text-gray-600 dark:text-gray-300">Arguments:</span>
                    <div class="text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 p-2 rounded mt-1">
                        ${Object.entries(call.arguments).map(([key, value]) => 
                            `<div><strong>${key}:</strong> ${value}</div>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
            
            <div>
                <span class="text-sm font-medium text-gray-600 dark:text-gray-300">Result:</span>
                <div class="text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 p-2 rounded mt-1">
                    ${this.formatToolResult(call.result)}
                </div>
            </div>
        `;
        
        return div;
    }
    
    getToolEmoji(toolName) {
        const emojiMap = {
            'weather': '🌦',
            'crypto_price': '🪙',
            'wiki': '📚',
            'search': '🔍',
            'joke': '🤣',
            'news': '📰'
        };
        
        return emojiMap[toolName] || '🔧';
    }
    
    formatToolResult(result) {
        if (typeof result === 'object') {
            return `<pre class="whitespace-pre-wrap">${JSON.stringify(result, null, 2)}</pre>`;
        }
        
        return result.toString();
    }
    
    formatFinalAnswer(answer) {
        // Simple formatting - convert newlines to <br> and preserve spacing
        return answer.replace(/\n/g, '<br>');
    }
    
    displayError(message) {
        this.responseSection.classList.remove('hidden');
        this.finalAnswerSection.classList.remove('hidden');
        
        this.finalAnswerContent.innerHTML = `
            <div class="flex items-center space-x-2 text-red-600 dark:text-red-400">
                <i class="fas fa-exclamation-triangle"></i>
                <span><strong>Error:</strong> ${message}</span>
            </div>
            <div class="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Please make sure the backend server is running on localhost:8000
            </div>
        `;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TinyGPTApp();
});

// Add some utility functions for enhanced UX
document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scrolling to response sections
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const target = mutation.target;
                if (target.id === 'response-section' && !target.classList.contains('hidden')) {
                    // Smooth scroll to response
                    setTimeout(() => {
                        target.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 100);
                }
            }
        });
    });
    
    const responseSection = document.getElementById('response-section');
    if (responseSection) {
        observer.observe(responseSection, { attributes: true });
    }
    
    // Add auto-resize to textarea
    const textarea = document.getElementById('prompt-input');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
    }
});