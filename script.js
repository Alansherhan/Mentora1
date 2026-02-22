// Chat Interface Logic
let currentSubject = null;
const API_BASE = '/api';

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message) return;

    input.value = '';

    // Add user message
    addMessage(message, 'user');

    // Show typing indicator
    showTyping();

    try {
        const headers = { 'Content-Type': 'application/json' };
        if (typeof chatbotSession !== 'undefined' && chatbotSession && chatbotSession.login_timestamp) {
            headers['X-Login-Timestamp'] = chatbotSession.login_timestamp;
        }

        const [response] = await Promise.all([
            fetch('/api/chat', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ message })
            }),
            new Promise(resolve => setTimeout(resolve, 1000)) // Enforce 1s delay
        ]);

        if (response.status === 401) {
            alert('Session expired. Password has been changed. Please login again.');
            chatbotSession = null;
            checkLogin();
            removeTyping();
            return;
        }

        const data = await response.json();
        removeTyping();

        // Handle different response types
        if (data.type === 'text') {
            addMessage(data.message, 'assistant');
        } else if (data.type === 'ai_response') {
            addMessage(data.message, 'assistant', true);
        } else if (data.type === 'subjects_list') {
            displaySubjects(data);
        } else if (data.type === 'units_list') {
            displayUnits(data);
        } else if (data.type === 'notes_results') {
            displayNotesResults(data);
        } else if (data.type === 'pyq_results') {
            displayPyqResults(data);
        } else if (data.type === 'pyq_list') {
            displayPyqList(data);
        } else {
            addMessage(data.message || 'No response', 'assistant');
        }

        // Auto-scroll to bottom
        setTimeout(() => {
            const chatContainer = document.getElementById('chatContainer');
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 100);
    } catch (error) {
        removeTyping();
        addMessage('❌ Error: ' + error.message, 'assistant');
    }
}

function addMessage(text, role, isAI = false) {
    const container = document.getElementById('chatContainer');

    const message = document.createElement('div');
    message.className = `message ${role}`;
    const aiBadge = (isAI && role === 'assistant') ? '<span class="ai-badge">✨ AI</span>' : '';
    message.innerHTML = `<div class="bubble ${role}">${aiBadge}${escapeHtml(text)}</div>`;

    container.appendChild(message);
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Auth State
let chatbotSession = null;

function displaySubjects(data) {
    const container = document.getElementById('chatContainer');

    let html = `<div class="message assistant"><div class="bubble assistant">
        <p>${data.message}</p>
        <div class="subjects-grid">`;

    for (let [name, count] of Object.entries(data.subjects || {})) {
        html += `<div class="subject-card" onclick="askForUnits('${name}')">
            <strong>${name}</strong><br>
            <small>${count} units</small>
        </div>`;
    }

    html += `</div></div></div>`;

    const msg = document.createElement('div');
    msg.innerHTML = html;
    container.appendChild(msg.firstChild);
}

function displayUnits(data) {
    const container = document.getElementById('chatContainer');
    currentSubject = data.subject;

    let html = `<div class="message assistant"><div class="bubble assistant">
        <p>${data.message}</p>
        <div class="units-grid">`;

    for (let [name, unit] of Object.entries(data.units || {})) {
        html += `<div class="unit-card" onclick="downloadUnit('${data.subject}', '${name}')">
            <strong>${name}</strong><br>
            <small>📥 Download</small>
        </div>`;
    }

    html += `</div></div></div>`;

    const msg = document.createElement('div');
    msg.innerHTML = html;
    container.appendChild(msg.firstChild);
}

function displayNotesResults(data) {
    const container = document.getElementById('chatContainer');

    let html = `<div class="message assistant"><div class="bubble assistant">
        <p>${data.message}</p>
        <div class="units-grid">`;

    for (let result of data.results || []) {
        html += `<div class="unit-card" onclick="downloadUnit('${result.subject}', '${result.unit}')">
            <strong>${result.subject}</strong><br>
            ${result.unit}<br>
            <small>📥 Download</small>
        </div>`;
    }

    html += `</div></div></div>`;

    const msg = document.createElement('div');
    msg.innerHTML = html;
    container.appendChild(msg.firstChild);
}

function displayPyqResults(data) {
    const container = document.getElementById('chatContainer');

    let html = `<div class="message assistant"><div class="bubble assistant">
        <p>${data.message}</p>
        <div class="units-grid">`;

    for (let result of data.results || []) {
        html += `<div class="unit-card" onclick="downloadPyq('${result.id}')">
            <strong>${result.data.name}</strong><br>
            <small>Type: ${result.data.type}</small><br>
            <small>📥 Download</small>
        </div>`;
    }

    html += `</div></div></div>`;

    const msg = document.createElement('div');
    msg.innerHTML = html;
    container.appendChild(msg.firstChild);
}

function displayPyqList(data) {
    const container = document.getElementById('chatContainer');

    let html = `<div class="message assistant"><div class="bubble assistant">
        <p>${data.message}</p>
        <div class="subjects-grid">`;

    for (let [type, count] of Object.entries(data.types || {})) {
        html += `<div class="subject-card" onclick="quickAsk('Show me ${type} files')">
            <strong>${type}</strong><br>
            <small>${count} files</small>
        </div>`;
    }

    html += `</div></div></div>`;

    const msg = document.createElement('div');
    msg.innerHTML = html;
    container.appendChild(msg.firstChild);
}

function askForUnits(subject) {
    document.getElementById('messageInput').value = `Show me ${subject} units`;
    sendMessage();
}

async function downloadUnit(subject, unit) {
    const link = document.createElement('a');
    link.href = `/api/download_unit/${encodeURIComponent(subject)}/${encodeURIComponent(unit)}`;
    link.download = `${subject}_${unit}.pdf`;
    link.click();
}

async function downloadPyq(pyqId) {
    const link = document.createElement('a');
    link.href = `/api/pyq/download/${pyqId}`;
    link.target = '_blank';
    link.click();
}

function quickAsk(text) {
    document.getElementById('messageInput').value = text;
    sendMessage();
}

function showTyping() {
    const container = document.getElementById('chatContainer');
    const typing = document.createElement('div');
    typing.className = 'message assistant typing-msg';
    typing.innerHTML = `<div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    </div>`;
    container.appendChild(typing);
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTyping() {
    const typing = document.querySelector('.typing-msg');
    if (typing) typing.remove();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Authentication Logic
function checkLogin() {
    // Hide loading screen
    const loadingScreen = document.getElementById('loadingScreen');
    if (loadingScreen) loadingScreen.style.display = 'none';

    if (!chatbotSession) {
        document.getElementById('loginOverlay').style.display = 'flex'; // Show overlay
    } else {
        document.getElementById('loginOverlay').style.display = 'none';
    }
}

function handleLoginKey(e) {
    if (e.key === 'Enter') attemptLogin();
}

async function attemptLogin() {
    const pwd = document.getElementById('chatbotPassword').value;
    const errorDiv = document.getElementById('loginError');

    if (!pwd) {
        errorDiv.textContent = 'Please enter a password';
        return;
    }

    try {
        const res = await fetch(API_BASE + '/chatbot/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: pwd })
        });

        const data = await res.json();

        if (data.success) {
            chatbotSession = {
                department: data.department || 'General',
                login_timestamp: data.login_timestamp // Get from server
            };
            document.getElementById('loginOverlay').style.display = 'none';
            document.getElementById('chatbotPassword').value = '';
            errorDiv.textContent = '';
        } else {
            errorDiv.textContent = data.error || 'Invalid password';
        }
    } catch (e) {
        errorDiv.textContent = 'Login error. Try again.';
    }
}

// Feedback Logic
function openFeedback() {
    document.getElementById('feedbackModal').style.display = 'flex';
}

function closeFeedback() {
    document.getElementById('feedbackModal').style.display = 'none';
}

async function submitFeedback() {
    const text = document.getElementById('feedbackText').value.trim();
    if (!text) {
        alert('Please enter some feedback first!');
        return;
    }

    try {
        await fetch(API_BASE + '/submit_feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ feedback: text })
        });
        alert('Thank you for your feedback! 📝');
        document.getElementById('feedbackText').value = '';
        closeFeedback();
    } catch (e) {
        alert('Error submitting feedback');
    }
}

// Reload Logic
function reloadChat() {
    if (confirm('Reload the chatbot? This will clear your current conversation view.')) {
        initializeChat();
    }
}

function initializeChat() {
    const container = document.getElementById('chatContainer');
    container.innerHTML = `
        <div class="welcome-message">
            <h2>👋 Welcome to Mentora</h2>
            <p>Your AI-powered college assistant</p>
            <div class="quick-actions" style="display: none;">
            </div>
        </div>
    `;
    currentSubject = null;
}

// Initialize
document.addEventListener('DOMContentLoaded', function () {
    checkLogin();
    initializeChat();

    const input = document.getElementById('messageInput');
    input.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});

// Close modal on outside click
window.onclick = function (event) {
    const modal = document.getElementById('feedbackModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// ===== CUSTOM BACKGROUND IMAGE CONFIGURATION =====
const CUSTOM_BACKGROUND_IMAGE = 'bg.jpg';
const OVERLAY_OPACITY = 0.9;

function applyCustomBackground() {
    const bgElement = document.getElementById('chatBackgroundImage');
    const overlayElement = document.querySelector('.chat-overlay');

    if (bgElement && CUSTOM_BACKGROUND_IMAGE) {
        bgElement.style.backgroundImage = `url("${CUSTOM_BACKGROUND_IMAGE}")`;
    }

    if (overlayElement) {
        // Dynamic overlay based on theme
        const theme = document.documentElement.getAttribute('data-theme') || 'dark';
        const overlayColor = theme === 'light' ? 'rgba(0, 0, 0, 0)' : `rgba(0, 0, 0, ${OVERLAY_OPACITY})`;
        overlayElement.style.background = overlayColor;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);
    // applyCustomBackground is called inside applyTheme if needed, but we also have the listener below
});

// ===== THEME LOGIC =====
function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);

    // Update icons
    const icon = theme === 'light' ? '🌙' : '☀️';
    const mainToggle = document.getElementById('themeToggle');
    const loginToggle = document.getElementById('loginThemeToggle');
    if (mainToggle) mainToggle.textContent = icon;
    if (loginToggle) loginToggle.textContent = icon;

    // Update overlay
    applyCustomBackground();
}

