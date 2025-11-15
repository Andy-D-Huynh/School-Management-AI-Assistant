const API_BASE_URL = 'http://localhost:8000';

let conversationId = null;

// DOM elements
const uploadSection = document.getElementById('upload-section');
const loadingSection = document.getElementById('loading-section');
const chatSection = document.getElementById('chat-section');
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const messagesContainer = document.getElementById('messages');
const questionInput = document.getElementById('question-input');
const sendButton = document.getElementById('send-button');

// Drag and drop handlers
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type === 'application/pdf') {
        handleFileUpload(files[0]);
    } else {
        alert('Please upload a PDF file');
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

// File upload handler
async function handleFileUpload(file) {
    // Show loading, hide upload
    uploadSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');
    chatSection.classList.add('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            conversationId = data.conversation_id;
            
            // Hide loading, show chat
            loadingSection.classList.add('hidden');
            chatSection.classList.remove('hidden');
            
            // Add welcome message
            addMessage('assistant', 'PDF processed successfully! You can now ask questions about it.');
            
            // Focus input
            questionInput.focus();
        } else {
            throw new Error(data.detail || 'Failed to process PDF');
        }
    } catch (error) {
        console.error('Upload error:', error);
        alert(`Error: ${error.message}`);
        
        // Show upload section again
        loadingSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
    }
}

// Chat functionality
sendButton.addEventListener('click', sendQuestion);
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendQuestion();
    }
});

async function sendQuestion() {
    const question = questionInput.value.trim();
    
    if (!question) return;
    if (!conversationId) {
        alert('Please upload a PDF first');
        return;
    }

    // Add user message to chat
    addMessage('user', question);
    questionInput.value = '';
    
    // Show loading indicator
    const loadingMessage = addMessage('assistant', 'Thinking...', true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                conversation_id: conversationId
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Replace loading message with actual response
            loadingMessage.remove();
            addMessage('assistant', data.response);
        } else {
            throw new Error(data.detail || 'Failed to get response');
        }
    } catch (error) {
        console.error('Ask error:', error);
        loadingMessage.remove();
        addMessage('assistant', `Error: ${error.message}`);
    }
}

function addMessage(role, text, isTemporary = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    if (isTemporary) {
        messageDiv.classList.add('temporary');
    }
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.textContent = text;
    
    messageDiv.appendChild(textDiv);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageDiv;
}

