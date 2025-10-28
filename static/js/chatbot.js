/**
 * Chatbot functionality for SITREP Assistant
 */

class SitrepChatbot {
    constructor() {
        this.isOpen = false;
        this.isLoading = false;
        this.config = {
            lmStudioUrl: 'https://openrouter.ai/api/v1',
            modelName: null
        };
        this.currentStreamingMessage = null;
        this.streamingMessageId = null;
        this.sessionId = this.generateSessionId();
        
        this.initializeElements();
        this.bindEvents();
        this.initializeSocket();
        this.loadConfiguration();
    }
    
    initializeElements() {
        this.elements = {
            toggle: document.getElementById('chatbot-toggle'),
            window: document.getElementById('chatbot-window'),
            minimize: document.getElementById('chatbot-minimize-btn'),
            refresh: document.getElementById('chatbot-refresh-btn'),
            shuffle: document.getElementById('chatbot-shuffle-btn'),
            messages: document.getElementById('chatbot-messages'),
            input: document.getElementById('chatbot-input'),
            sendBtn: document.getElementById('chatbot-send-btn'),
            statusIndicator: document.getElementById('status-indicator'),
            statusText: document.getElementById('status-text'),
            
            // Configuration modal
            configBtn: document.getElementById('chatbot-config-btn'),
            configModal: document.getElementById('chatbot-config-modal'),
            configClose: document.getElementById('chatbot-config-close'),
            lmStudioUrl: document.getElementById('lm-studio-url'),
            modelSelect: document.getElementById('lm-studio-model'),
            refreshModels: document.getElementById('refresh-models-btn'),
            testConnection: document.getElementById('test-connection'),
            saveConfig: document.getElementById('save-config-btn'),
            connectionStatus: document.getElementById('connection-status')
        };
    }
    
    bindEvents() {
        // Toggle chatbot window
        this.elements.toggle.addEventListener('click', () => this.toggleWindow());
        this.elements.minimize.addEventListener('click', () => this.toggleWindow());
        
        // Refresh chat
        this.elements.refresh.addEventListener('click', () => this.refreshChat());
        
        // Shuffle questions
        this.elements.shuffle.addEventListener('click', () => this.shuffleQuestion());
        
        // Send message
        this.elements.sendBtn.addEventListener('click', () => this.sendMessage());
        this.elements.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Configuration modal
        this.elements.configBtn.addEventListener('click', () => this.openConfigModal());
        this.elements.configClose.addEventListener('click', () => this.closeConfigModal());
        this.elements.refreshModels.addEventListener('click', () => this.refreshModels());
        this.elements.testConnection.addEventListener('click', () => this.testConnection());
        this.elements.saveConfig.addEventListener('click', () => this.saveConfiguration());
        
        // Close modal when clicking outside
        this.elements.configModal.addEventListener('click', (e) => {
            if (e.target === this.elements.configModal) {
                this.closeConfigModal();
            }
        });
    }
    
    initializeSocket() {
        // Initialize Socket.IO connection
        this.socket = io();
        
        // Handle streaming chunks
        this.socket.on('chatbot_stream_chunk', (data) => {
            this.handleStreamChunk(data);
        });
        
        // Handle streaming status updates
        this.socket.on('chatbot_stream_status', (data) => {
            this.handleStreamStatus(data);
        });
        
        // Handle streaming completion
        this.socket.on('chatbot_stream_complete', (data) => {
            this.handleStreamComplete(data);
        });
        
        // Handle streaming errors
        this.socket.on('chatbot_error', (data) => {
            this.handleStreamError(data);
        });
        
        // Handle connection events
        this.socket.on('connect', () => {
            console.log('Connected to server for streaming');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
        });
    }
    
    toggleWindow() {
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            this.elements.window.classList.add('open');
            this.elements.input.focus();
        } else {
            this.elements.window.classList.remove('open');
        }
    }
    
    async sendMessage() {
        const message = this.elements.input.value.trim();
        if (!message || this.isLoading) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.elements.input.value = '';
        
        // Show loading state
        this.setLoading(true);
        
        // Create a placeholder message for streaming response
        this.currentStreamingMessage = this.addStreamingMessage();
        this.streamingMessageId = this.currentStreamingMessage.id;
        
        // Send query via Socket.IO for streaming with session ID
        this.socket.emit('chatbot_query_stream', { 
            query: message,
            session_id: this.sessionId 
        });
    }
    
    generateSessionId() {
        // Generate a simple UUID-like session ID
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    addMessage(text, sender, metadata = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'bot' ? '<i class="fa-solid fa-robot"></i>' : '<i class="fa-solid fa-user"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        
        if (metadata.isError) {
            messageText.style.background = '#dc3545';
            messageText.style.color = 'white';
        }
        
        // Format message text (support for basic markdown-like formatting)
        messageText.innerHTML = this.formatMessage(text);
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        content.appendChild(messageText);
        
        // Add metadata info for bot messages
        if (sender === 'bot' && metadata.dataContext && !metadata.isError) {
            const metaInfo = document.createElement('div');
            metaInfo.className = 'message-meta';
            metaInfo.style.fontSize = '11px';
            metaInfo.style.color = '#6c757d';
            metaInfo.style.marginTop = '4px';
            
            let metaText = `Based on ${metadata.dataCount} ${metadata.dataContext}`;
            if (metadata.hasCoordinates && metadata.coordinates) {
                metaText += ` (${metadata.coordinates.length} with coordinates)`;
            }
            
            metaInfo.textContent = metaText;
            content.appendChild(metaInfo);
            
            // Add coordinate summary if available
            if (metadata.hasCoordinates && metadata.coordinates && metadata.coordinates.length > 0) {
                const coordInfo = this.createCoordinateInfo(metadata.coordinates);
                content.appendChild(coordInfo);
            }
        }
        
        content.appendChild(messageTime);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.elements.messages.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    addStreamingMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chatbot-message bot-message streaming';
        messageDiv.id = 'streaming-message-' + Date.now();
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<i class="fa-solid fa-robot"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text streaming-text';
        messageText.innerHTML = '<span class="typing-indicator">Analyzing your query...</span>';
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        content.appendChild(messageText);
        content.appendChild(messageTime);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.elements.messages.appendChild(messageDiv);
        this.scrollToBottom();
        
        return {
            element: messageDiv,
            textElement: messageText,
            id: messageDiv.id
        };
    }
    
    handleStreamChunk(data) {
        if (!this.currentStreamingMessage) return;
        
        const textElement = this.currentStreamingMessage.textElement;
        
        if (data.partial_response) {
            // Update with partial response (streaming text)
            textElement.innerHTML = this.formatMessage(data.partial_response);
        }
        
        this.scrollToBottom();
    }
    
    handleStreamStatus(data) {
        if (!this.currentStreamingMessage) return;
        
        const textElement = this.currentStreamingMessage.textElement;
        textElement.innerHTML = `<span class="typing-indicator">${data.status}</span>`;
        
        this.scrollToBottom();
    }
    
    handleStreamComplete(data) {
        if (!this.currentStreamingMessage) return;
        
        const messageElement = this.currentStreamingMessage.element;
        const textElement = this.currentStreamingMessage.textElement;
        
        // Remove streaming class
        messageElement.classList.remove('streaming');
        textElement.classList.remove('streaming-text');
        
        // Set final response
        textElement.innerHTML = this.formatMessage(data.response.llm_response);
        
        // Add metadata if available
        if (data.response.data_context) {
            const content = messageElement.querySelector('.message-content');
            
            const metaInfo = document.createElement('div');
            metaInfo.className = 'message-meta';
            metaInfo.style.fontSize = '11px';
            metaInfo.style.color = '#6c757d';
            metaInfo.style.marginTop = '4px';
            
            let metaText = `Based on ${data.response.data_count} ${data.response.data_context}`;
            if (data.response.has_coordinates && data.response.coordinates) {
                metaText += ` (${data.response.coordinates.length} with coordinates)`;
            }
            
            metaInfo.textContent = metaText;
            content.insertBefore(metaInfo, content.lastElementChild);
            
            // Add coordinate summary if available
            if (data.response.has_coordinates && data.response.coordinates && data.response.coordinates.length > 0) {
                const coordInfo = this.createCoordinateInfo(data.response.coordinates);
                content.insertBefore(coordInfo, content.lastElementChild);
                
                // Plot coordinates on map if relevant
                this.plotCoordinatesOnMap(data.response.coordinates, data.response.is_mapping_query);
            }
        }
        
        // Reset streaming state
        this.currentStreamingMessage = null;
        this.streamingMessageId = null;
        this.setLoading(false);
        this.setStatus('Ready', 'success');
        
        this.scrollToBottom();
    }
    
    handleStreamError(data) {
        if (!this.currentStreamingMessage) return;
        
        const messageElement = this.currentStreamingMessage.element;
        const textElement = this.currentStreamingMessage.textElement;
        
        // Remove streaming class
        messageElement.classList.remove('streaming');
        textElement.classList.remove('streaming-text');
        
        // Set error message
        textElement.innerHTML = `Error: ${data.error}`;
        textElement.style.background = '#dc3545';
        textElement.style.color = 'white';
        
        // Reset streaming state
        this.currentStreamingMessage = null;
        this.streamingMessageId = null;
        this.setLoading(false);
        this.setStatus('Error', 'error');
        
        this.scrollToBottom();
    }
    
    addLoadingMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chatbot-message bot-message loading-message';
        messageDiv.id = `loading-${Date.now()}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<i class="fa-solid fa-robot"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message-loading';
        loadingDiv.innerHTML = '<div class="loading-dot"></div><div class="loading-dot"></div><div class="loading-dot"></div>';
        
        content.appendChild(loadingDiv);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.elements.messages.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv.id;
    }
    
    removeLoadingMessage(messageId) {
        const loadingMessage = document.getElementById(messageId);
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }
    
    formatMessage(text) {
        // Initialize showdown converter if not already done
        if (!this.markdownConverter) {
            this.markdownConverter = new showdown.Converter({
                tables: true,
                strikethrough: true,
                tasklists: true,
                simplifiedAutoLink: true,
                openLinksInNewWindow: true,
                backslashEscapesHTMLTags: true,
                emoji: true,
                underline: true,
                simpleLineBreaks: true,
                requireSpaceBeforeHeadingText: true
            });
        }
        
        // Convert markdown to HTML
        let html = this.markdownConverter.makeHtml(text);
        
        // Add custom styling to code blocks
        html = html.replace(/<code>/g, '<code style="background: #f1f3f4; padding: 2px 4px; border-radius: 3px; font-family: monospace;">');
        
        // Add custom styling to blockquotes
        html = html.replace(/<blockquote>/g, '<blockquote style="border-left: 4px solid #ddd; margin: 10px 0; padding: 10px 15px; background: #f9f9f9;">');
        
        return html;
    }
    
    scrollToBottom() {
        this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        this.elements.sendBtn.disabled = loading;
        this.elements.input.disabled = loading;
        
        if (loading) {
            this.setStatus('Processing...', 'connecting');
        }
    }
    
    setStatus(text, type = 'success') {
        this.elements.statusText.textContent = text;
        this.elements.statusIndicator.className = `status-indicator ${type}`;
    }
    
    refreshChat() {
        // Generate new session ID for fresh conversation
        this.sessionId = this.generateSessionId();
        
        // Clear all messages except the initial bot message
        const messages = this.elements.messages;
        
        // Remove all messages
        messages.innerHTML = '';
        
        // Clear plotted markers from the map
        this.clearChatbotMarkers();
        
        // Add the initial welcome message back
        const welcomeMessage = document.createElement('div');
        welcomeMessage.className = 'chatbot-message bot-message';
        welcomeMessage.innerHTML = `
            <div class="message-avatar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C6.48 2 2 6.48 2 12C2 13.54 2.36 14.99 3.01 16.28L2 22L7.72 20.99C9.01 21.64 10.46 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2Z" fill="currentColor"/>
                    <circle cx="9" cy="12" r="1" fill="white"/>
                    <circle cx="12" cy="12" r="1" fill="white"/>
                    <circle cx="15" cy="12" r="1" fill="white"/>
                </svg>
            </div>
            <div class="message-content">
                <div class="message-text">
                    Hello! I'm your SAM UN Assistant. I can help you with information about SITREPs, incidents, and activities. I can also plot locations on the map when relevant. How can I assist you today?
                </div>
                <div class="message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;
        
        messages.appendChild(welcomeMessage);
        
        // Clear input field
        this.elements.input.value = '';
        
        // Reset loading state
        this.setLoading(false);
        
        // Reset streaming state
        this.currentStreamingMessage = null;
        this.streamingMessageId = null;
        
        // Reset status
        this.setStatus('Ready', 'success');
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Optional: Show a brief confirmation
        this.setStatus('Chat refreshed', 'success');
        setTimeout(() => {
            this.setStatus('Ready', 'success');
        }, 2000);
    }
    
    async shuffleQuestion() {
        try {
            // Show loading state briefly
            this.setStatus('Loading question...', 'loading');
            
            // Fetch random question from the API
            const response = await fetch('/api/random-question');
            const data = await response.json();
            
            if (data.status === 'success' && data.question) {
                // Insert the question into the input box
                this.elements.input.value = data.question;
                
                // Focus on the input box
                this.elements.input.focus();
                
                // Show success status briefly
                this.setStatus('Question loaded!', 'success');
                setTimeout(() => {
                    this.setStatus('Ready', 'success');
                }, 1500);
            } else {
                throw new Error(data.error || 'Failed to fetch question');
            }
        } catch (error) {
            console.error('Error fetching random question:', error);
            this.setStatus('Error loading question', 'error');
            setTimeout(() => {
                this.setStatus('Ready', 'success');
            }, 3000);
        }
    }
    
    // Configuration methods
    openConfigModal() {
        this.elements.configModal.style.display = 'flex';
        this.loadConfigurationToModal();
        this.refreshModels();
    }
    
    closeConfigModal() {
        this.elements.configModal.style.display = 'none';
    }
    
    async loadConfiguration() {
        try {
            const response = await fetch('/api/chatbot/config');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.config = data.config;
            }
        } catch (error) {
            console.error('Error loading configuration:', error);
        }
    }
    
    loadConfigurationToModal() {
        this.elements.lmStudioUrl.value = this.config.lmStudioUrl || 'https://openrouter.ai/api/v1';
        this.elements.modelSelect.value = this.config.modelName || '';
    }
    
    async refreshModels() {
        try {
            this.elements.refreshModels.disabled = true;
            this.elements.refreshModels.textContent = 'Loading...';
            
            const response = await fetch('/api/chatbot/models');
            const data = await response.json();
            
            // Clear existing options except the first one
            this.elements.modelSelect.innerHTML = '<option value="">Auto-detect</option>';
            
            if (data.status === 'success' && data.models.length > 0) {
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    this.elements.modelSelect.appendChild(option);
                });
            }
            
        } catch (error) {
            console.error('Error refreshing models:', error);
        } finally {
            this.elements.refreshModels.disabled = false;
            this.elements.refreshModels.textContent = 'Refresh Models';
        }
    }
    
    async testConnection() {
        try {
            this.elements.testConnection.disabled = true;
            this.elements.testConnection.textContent = 'Testing...';
            this.elements.connectionStatus.textContent = '';
            
            const response = await fetch('/api/chatbot/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: 'test connection' })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.elements.connectionStatus.textContent = 'Connection successful!';
                this.elements.connectionStatus.className = 'success';
            } else {
                this.elements.connectionStatus.textContent = `Connection failed: ${data.error}`;
                this.elements.connectionStatus.className = 'error';
            }
            
        } catch (error) {
            this.elements.connectionStatus.textContent = `Connection error: ${error.message}`;
            this.elements.connectionStatus.className = 'error';
        } finally {
            this.elements.testConnection.disabled = false;
            this.elements.testConnection.textContent = 'Test Connection';
        }
    }
    
    async saveConfiguration() {
        try {
            const newConfig = {
                lm_studio_url: this.elements.lmStudioUrl.value.trim(),
                model_name: this.elements.modelSelect.value || null
            };
            
            const response = await fetch('/api/chatbot/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newConfig)
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.config.lmStudioUrl = newConfig.lm_studio_url;
                this.config.modelName = newConfig.model_name;
                this.closeConfigModal();
                this.setStatus('Configuration saved', 'success');
            } else {
                alert(`Error saving configuration: ${data.error}`);
            }
            
        } catch (error) {
            alert(`Error saving configuration: ${error.message}`);
        }
    }
    
    // Map integration methods
    clearChatbotMarkers() {
        // Check if map exists (Leaflet map)
        if (typeof window.map === 'undefined' || !window.map) {
            console.warn('Map not available for clearing markers');
            return;
        }
        
        // Clear existing chatbot markers if any
        if (window.chatbotMarkers) {
            window.chatbotMarkers.forEach(marker => {
                window.map.removeLayer(marker);
            });
        }
        window.chatbotMarkers = [];
    }
    
    plotCoordinatesOnMap(coordinates, isMappingQuery = false) {
        // Check if map exists (Leaflet map)
        if (typeof window.map === 'undefined' || !window.map) {
            console.warn('Map not available for plotting coordinates');
            return;
        }
        
        // Clear existing chatbot markers
        this.clearChatbotMarkers();
        
        // Create markers for each coordinate
        coordinates.forEach((coord, index) => {
            const marker = L.marker([coord.lat, coord.lon], {
                icon: this.createSitrepIcon(coord)
            });
            
            // Create popup content
            const popupContent = this.createPopupContent(coord);
            marker.bindPopup(popupContent);
            
            // Add to map
            marker.addTo(window.map);
            window.chatbotMarkers.push(marker);
        });
        
        // Fit map to show all markers if it's a mapping query
        if (isMappingQuery && coordinates.length > 0) {
            if (coordinates.length === 1) {
                // Single point - center and zoom
                window.map.setView([coordinates[0].lat, coordinates[0].lon], 12);
            } else {
                // Multiple points - fit bounds
                const group = new L.featureGroup(window.chatbotMarkers);
                window.map.fitBounds(group.getBounds().pad(0.1));
            }
        }
        
        // Show notification
        this.showMapNotification(coordinates.length);
    }
    
    createSitrepIcon(coord) {
        // Use the same military marker system as activity marking
        const incidentType = String(coord.incident_type || "").toLowerCase();
        const sourceCategory = String(coord.source_category || "").toLowerCase();
        
        // Priority: incident type markers override source category markers
        if (incidentType && window.MILITARY_MARKERS && window.MILITARY_MARKERS.incident_types[incidentType]) {
            const config = window.MILITARY_MARKERS.incident_types[incidentType];
            const size = config.size || "medium";
            return this.createMilitaryMarker(config, size);
        }
        
        // Fallback to source category markers
        if (sourceCategory && window.MILITARY_MARKERS && window.MILITARY_MARKERS.source_categories[sourceCategory]) {
            const config = window.MILITARY_MARKERS.source_categories[sourceCategory];
            return this.createMilitaryMarker(config, "medium");
        }
        
        // Final fallback to severity-based markers (legacy support)
        return this.createSeverityBasedIcon(coord.severity);
    }
    
    createMilitaryMarker(config, size = "medium") {
        const sizes = {
            small: { width: 24, height: 24, fontSize: "10px" },
            medium: { width: 32, height: 32, fontSize: "14px" },
            large: { width: 40, height: 40, fontSize: "18px" }
        };
        
        const sizeConfig = sizes[size] || sizes.medium;
        const shape = config.shape || "circle";
        
        let shapeStyle = "";
        switch (shape) {
            case "square":
                shapeStyle = "border-radius: 3px;";
                break;
            case "diamond":
                shapeStyle = "transform: rotate(45deg); border-radius: 3px;";
                break;
            case "triangle":
                shapeStyle = "clip-path: polygon(50% 0%, 0% 100%, 100% 100%); border-radius: 0;";
                break;
            case "circle":
            default:
                shapeStyle = "border-radius: 50%;";
                break;
        }
        
        const iconHtml = `
            <div style="
                width: ${sizeConfig.width}px; 
                height: ${sizeConfig.height}px; 
                background-color: ${config.bgColor}; 
                border: 2px solid ${config.color}; 
                ${shapeStyle}
                display: flex; 
                align-items: center; 
                justify-content: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            ">
                <i class="${config.icon}" style="
                    color: ${config.color}; 
                    font-size: ${sizeConfig.fontSize};
                    ${shape === "diamond" ? "transform: rotate(-45deg);" : ""}
                "></i>
            </div>
        `;
        
        return L.divIcon({
            className: "chatbot-military-marker",
            html: iconHtml,
            iconSize: [sizeConfig.width, sizeConfig.height],
            iconAnchor: [sizeConfig.width / 2, sizeConfig.height / 2],
            popupAnchor: [0, -sizeConfig.height / 2]
        });
    }
    
    createSeverityBasedIcon(severity) {
        // Fallback for when military markers are not available
        const colors = {
            'Critical': '#dc3545',
            'High': '#fd7e14',
            'Medium': '#ffc107',
            'Low': '#28a745',
            'Unknown': '#6c757d'
        };
        
        const color = colors[severity] || colors['Unknown'];
        
        return L.divIcon({
            className: 'chatbot-sitrep-marker',
            html: `<div style="
                background-color: ${color};
                width: 20px;
                height: 20px;
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 10px;
                font-weight: bold;
            ">!</div>`,
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
    }
    
    createPopupContent(coord) {
        return `
            <div style="max-width: 250px;">
                <h6 style="margin: 0 0 8px 0; color: #333;">${coord.title}</h6>
                <div style="margin-bottom: 4px;">
                    <strong>Severity:</strong> 
                    <span style="color: ${this.getSeverityColor(coord.severity)};">${coord.severity}</span>
                </div>
                <div style="margin-bottom: 4px;"><strong>Status:</strong> ${coord.status}</div>
                <div style="margin-bottom: 4px;"><strong>Type:</strong> ${coord.incident_type}</div>
                ${coord.unit ? `<div style="margin-bottom: 4px;"><strong>Unit:</strong> ${coord.unit}</div>` : ''}
                ${coord.description ? `<div style="margin-bottom: 8px;"><strong>Description:</strong> ${coord.description.substring(0, 100)}${coord.description.length > 100 ? '...' : ''}</div>` : ''}
                <div style="font-size: 11px; color: #666;">
                    <div>Coordinates: ${coord.lat.toFixed(6)}, ${coord.lon.toFixed(6)}</div>
                    ${coord.created_at ? `<div>Created: ${new Date(coord.created_at).toLocaleDateString()}</div>` : ''}
                </div>
            </div>
        `;
    }
    
    getSeverityColor(severity) {
        const colors = {
            'Critical': '#dc3545',
            'High': '#fd7e14',
            'Medium': '#ffc107',
            'Low': '#28a745',
            'Unknown': '#6c757d'
        };
        return colors[severity] || colors['Unknown'];
    }
    
    createCoordinateInfo(coordinates) {
        const coordDiv = document.createElement('div');
        coordDiv.className = 'coordinate-info';
        coordDiv.style.cssText = `
            margin-top: 8px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 11px;
            border-left: 3px solid #007bff;
        `;
        
        const title = document.createElement('div');
        title.style.fontWeight = 'bold';
        title.style.marginBottom = '4px';
        title.textContent = `📍 ${coordinates.length} Location${coordinates.length > 1 ? 's' : ''} Found`;
        
        const list = document.createElement('div');
        coordinates.slice(0, 3).forEach((coord, index) => {
            const item = document.createElement('div');
            item.style.marginBottom = '2px';
            item.innerHTML = `${index + 1}. ${coord.title} <span style="color: ${this.getSeverityColor(coord.severity)};">(${coord.severity})</span>`;
            list.appendChild(item);
        });
        
        if (coordinates.length > 3) {
            const more = document.createElement('div');
            more.style.fontStyle = 'italic';
            more.style.color = '#666';
            more.textContent = `... and ${coordinates.length - 3} more`;
            list.appendChild(more);
        }
        
        coordDiv.appendChild(title);
        coordDiv.appendChild(list);
        
        return coordDiv;
    }
    
    showMapNotification(count) {
        // Create a temporary notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #007bff;
            color: white;
            padding: 12px 16px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            z-index: 10000;
            font-size: 14px;
            transition: opacity 0.3s ease;
        `;
        notification.textContent = `📍 ${count} location${count > 1 ? 's' : ''} plotted on map`;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.sitrepChatbot = new SitrepChatbot();
});