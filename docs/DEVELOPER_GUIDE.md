# SmartBuddy Developer Guide

## Introduction

Welcome to the SmartBuddy developer guide! This comprehensive documentation will help you understand the codebase, contribute effectively, and extend the application with new features.

## Development Environment Setup

### Prerequisites
- Python 3.7 or higher
- pip package manager
- Git version control
- Modern web browser
- Code editor (VS Code recommended)

### Initial Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd smartbuddy
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Development Server**
   ```bash
   python server.py
   ```

5. **Access Application**
   - Main App: http://localhost:5000
   - Admin Panel: http://localhost:5000/admin

### Development Tools

#### Recommended VS Code Extensions:
- Python
- Pylance
- HTML/CSS Support
- JavaScript (ES6) code snippets
- Live Server
- GitLens

#### Browser Developer Tools:
- Chrome DevTools or Firefox Developer Tools
- Network tab for API debugging
- Console for JavaScript debugging
- Elements for UI inspection

## Project Architecture

### Directory Structure

```
smartbuddy/
├── server.py                 # Main Flask application
├── mental_health_nlp.py      # NLP engine for emotion processing
├── requirements.txt          # Python dependencies
├── index.html               # Main chat interface
├── admin.html               # Admin dashboard
├── script.js                # Client-side JavaScript
├── style.css                # Main stylesheet
├── style_additions.css      # Additional styles
├── test_nlp.py              # NLP testing script
├── test_nlp_enhanced.py     # Enhanced NLP testing
├── fix_auth.py              # Authentication utilities
├── reset_pwd.py             # Password reset utilities
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md      # Architecture documentation
│   ├── USER_GUIDE.md        # User guide
│   └── DEVELOPER_GUIDE.md   # Developer guide (this file)
├── data/                    # Data storage
├── notes/                   # Upload storage
├── chats/                   # Chat history
└── pyq_files/              # PYQ storage
```

### Core Components

#### 1. Flask Application (`server.py`)

The main application file contains several key classes:

```python
class DataManager:
    """Handles all JSON file operations with atomic writes"""
    
class NLPProcessor:
    """Processes text queries and detects user intent"""
    
class NotesManager:
    """Manages academic subjects and units"""
    
class PYQManager:
    """Handles previous year questions and documents"""
    
class ChatBot:
    """Main conversation orchestrator"""
```

#### 2. NLP Engine (`mental_health_nlp.py`)

The mental health processing engine:

```python
class MentalHealthNLP:
    """NLP processor for mental health chatbot using classical NLP techniques"""
    
    def detect_emotion(self, text: str) -> Tuple[str, float]
    def process_query(self, text: str) -> Dict[str, Any]
    def generate_greeting(self) -> str
```

#### 3. Frontend Components

- **index.html**: Main chat interface with embedded CSS and JavaScript
- **admin.html**: Administrative dashboard
- **script.js**: Client-side logic and API interactions

## Code Style and Standards

### Python Code Style

#### Follow PEP 8 Guidelines:
- Use 4 spaces for indentation
- Maximum line length: 88 characters
- Use snake_case for variable and function names
- Use PascalCase for class names
- Import order: standard library, third-party, local imports

#### Example:
```python
import os
import json
from typing import Dict, List, Any

import flask
from flask import Flask, request

from mental_health_nlp import MentalHealthNLP


class ExampleClass:
    """Example class following PEP 8 guidelines."""
    
    def __init__(self, parameter: str) -> None:
        self.parameter = parameter
    
    def example_method(self, data: Dict[str, Any]) -> List[str]:
        """Example method with type hints."""
        return list(data.keys())
```

### JavaScript Code Style

#### Modern JavaScript (ES6+):
- Use `const` and `let` instead of `var`
- Use arrow functions for callbacks
- Use template literals for string interpolation
- Use async/await for asynchronous operations

#### Example:
```javascript
// Good
const sendMessage = async (message) => {
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        return await response.json();
    } catch (error) {
        console.error('Error sending message:', error);
    }
};

// Avoid
function sendMessage(message) {
    return fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({message: message})
    }).then(function(response) {
        return response.json();
    }).catch(function(error) {
        console.error('Error sending message:', error);
    });
}
```

### CSS Code Style

#### BEM Methodology:
- Use Block__Element--Modifier naming
- Organize styles logically
- Use CSS custom properties for theming

#### Example:
```css
.chat-container {
    /* Block styles */
}

.chat-container__message {
    /* Element styles */
}

.chat-container__message--user {
    /* Modifier styles */
}

:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
}
```

## API Development

### RESTful API Design

#### Endpoint Structure:
```
GET    /api/subjects          # List all subjects
POST   /api/subjects          # Create new subject
GET    /api/subjects/{id}     # Get specific subject
PUT    /api/subjects/{id}     # Update subject
DELETE /api/subjects/{id}     # Delete subject
```

#### Request/Response Format:
```python
# Request
{
    "subject_name": "Computer Science",
    "keywords": "programming, coding, algorithms"
}

# Response
{
    "success": true,
    "data": {
        "id": "subject_123",
        "name": "Computer Science",
        "keywords": ["programming", "coding", "algorithms"]
    }
}
```

### Error Handling

#### Standard Error Response:
```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500
```

#### Custom Error Handling:
```python
def handle_api_error(func):
    """Decorator for API error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': 'Invalid input',
                'message': str(e)
            }), 400
        except Exception as e:
            app.logger.error(f"API Error: {e}")
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'message': 'An unexpected error occurred'
            }), 500
    return wrapper
```

## NLP Development

### Emotion Detection

#### Adding New Emotions:

1. **Update Emotion Keywords** in `mental_health_nlp.py`:
```python
self.emotion_keywords = {
    # ... existing emotions ...
    'confident': ['confident', 'self-assured', 'sure', 'certain', 'positive'],
    'hopeful': ['hopeful', 'optimistic', 'hope', 'looking forward']
}
```

2. **Add Response Templates**:
```python
self.response_templates = {
    # ... existing templates ...
    'confident': [
        "That confidence sounds wonderful{context}! You've got this! Keep believing in yourself. 💪",
        "I love that self-assured energy{context}! Your confidence will carry you through. ✨"
    ],
    'hopeful': [
        "That hopefulness is beautiful{context}! Optimism is such a powerful force. 🌟",
        "I'm glad you're feeling hopeful{context}! That positive outlook will help you achieve great things. 🌈"
    ]
}
```

#### Improving Fuzzy Matching:

```python
def detect_emotion(self, text: str) -> Tuple[str, float]:
    # ... existing code ...
    
    # Enhanced fuzzy matching
    for emotion, keywords in self.emotion_keywords.items():
        for keyword in keywords:
            # Exact match
            if keyword in tokens:
                emotion_scores[emotion] += 2.0
            # Partial match
            elif keyword in preprocessed:
                emotion_scores[emotion] += 1.5
            # Fuzzy match with configurable threshold
            else:
                for token in tokens:
                    similarity = difflib.SequenceMatcher(None, keyword, token).ratio()
                    if similarity > self.fuzzy_threshold:  # Make threshold configurable
                        emotion_scores[emotion] += 0.8
                        break
```

### Context Extraction

#### Adding New Context Types:

```python
def _build_context_string(self, keywords: Dict[str, List[str]]) -> str:
    contexts = []
    
    # Existing contexts
    if 'academic' in keywords.get('concerns', []):
        contexts.append(' about your studies')
    elif 'social' in keywords.get('concerns', []):
        contexts.append(' in your relationships')
    
    # New contexts
    elif 'financial' in keywords.get('concerns', []):
        contexts.append(' about your finances')
    elif 'career' in keywords.get('concerns', []):
        contexts.append(' about your career path')
    
    return contexts[0] if contexts else ''
```

## Frontend Development

### Component Structure

#### Chat Interface Components:

```javascript
// Message Component
function addMessage(text, role) {
    const container = document.getElementById('chatContainer');
    const message = document.createElement('div');
    message.className = `message ${role}`;
    message.innerHTML = `<div class="bubble ${role}">${escapeHtml(text)}</div>`;
    container.appendChild(message);
    scrollToBottom();
}

// Typing Indicator
function showTyping() {
    const container = document.getElementById('chatContainer');
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    container.appendChild(indicator);
    scrollToBottom();
}
```

#### API Communication:

```javascript
class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        // Add session header if available
        if (typeof chatbotSession !== 'undefined' && chatbotSession?.login_timestamp) {
            config.headers['X-Login-Timestamp'] = chatbotSession.login_timestamp;
        }
        
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async sendMessage(message) {
        return this.request('/chat', {
            method: 'POST',
            body: JSON.stringify({ message })
        });
    }
    
    async getSubjects() {
        return this.request('/subjects');
    }
}
```

### Theme System

#### CSS Custom Properties:

```css
:root {
    /* Light theme variables */
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --text-primary: #212529;
    --text-secondary: #6c757d;
    --accent: #007bff;
    --border: #dee2e6;
}

[data-theme="dark"] {
    /* Dark theme variables */
    --bg-primary: #1a1f3a;
    --bg-secondary: #0a0e27;
    --text-primary: #ffffff;
    --text-secondary: #b0b9d4;
    --accent: #667eea;
    --border: rgba(102, 126, 234, 0.2);
}
```

#### Theme Toggle:

```javascript
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update theme toggle button
    updateThemeToggle(newTheme);
}

// Initialize theme on load
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeToggle(savedTheme);
});
```

## Testing

### NLP Testing

#### Unit Tests for Emotion Detection:

```python
import unittest
from mental_health_nlp import MentalHealthNLP

class TestMentalHealthNLP(unittest.TestCase):
    def setUp(self):
        self.nlp = MentalHealthNLP()
    
    def test_happy_emotion_detection(self):
        text = "I'm feeling really happy today!"
        emotion, confidence = self.nlp.detect_emotion(text)
        self.assertEqual(emotion, 'happy')
        self.assertGreater(confidence, 0.5)
    
    def test_anxious_emotion_detection(self):
        text = "I'm worried about the upcoming exam"
        emotion, confidence = self.nlp.detect_emotion(text)
        self.assertEqual(emotion, 'anxious')
        self.assertGreater(confidence, 0.5)
    
    def test_fuzzy_matching(self):
        text = "Feeling hapy and exicted"  # Typos
        emotion, confidence = self.nlp.detect_emotion(text)
        self.assertIn(emotion, ['happy', 'excited'])
    
    def test_response_generation(self):
        text = "I'm feeling sad about my grades"
        response = self.nlp.process_query(text)
        self.assertIn('message', response)
        self.assertIn('sad', response['message'].lower())

if __name__ == '__main__':
    unittest.main()
```

#### Integration Tests:

```python
def test_full_conversation_flow():
    """Test complete conversation flow"""
    nlp = MentalHealthNLP()
    
    # Greeting
    greeting = nlp.generate_greeting()
    assert isinstance(greeting, str)
    assert len(greeting) > 0
    
    # Mental health query
    response1 = nlp.process_query("I'm feeling anxious")
    assert response1['type'] == 'text'
    assert 'anxious' in response1['message'].lower()
    
    # Academic query (should be handled by main system)
    # This would be tested in the full server integration
```

### API Testing

#### Test API Endpoints:

```python
import unittest
import json
from server import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_chat_endpoint(self):
        response = self.app.post('/api/chat', 
                                data=json.dumps({'message': 'Hello'}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    def test_subjects_endpoint(self):
        response = self.app.get('/api/subjects')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('subjects', data)
    
    def test_invalid_request(self):
        response = self.app.post('/api/chat', 
                                data='invalid json',
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
```

### Frontend Testing

#### JavaScript Unit Tests:

```javascript
// Simple test framework example
function testEscapeHtml() {
    const input = '<script>alert("xss")</script>';
    const expected = '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;';
    const result = escapeHtml(input);
    
    if (result === expected) {
        console.log('✓ escapeHtml test passed');
    } else {
        console.error('✗ escapeHtml test failed');
        console.log('Expected:', expected);
        console.log('Got:', result);
    }
}

function testAPIClient() {
    const client = new APIClient();
    
    // Test URL construction
    if (client.baseURL === '/api') {
        console.log('✓ APIClient initialization test passed');
    } else {
        console.error('✗ APIClient initialization test failed');
    }
}

// Run tests
testEscapeHtml();
testAPIClient();
```

## Database and Data Management

### JSON Data Structure

#### Data Access Patterns:

```python
class DataManager:
    def __init__(self):
        self.ensure_files()
    
    def save_json(self, filepath: Path, data: Any):
        """Atomic file write operation"""
        temp_path = filepath.with_suffix('.tmp')
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            temp_path.replace(filepath)  # Atomic operation
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e
    
    def load_json(self, filepath: Path) -> Any:
        """Safe file read with fallback"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} if 'subjects' in str(filepath) else []
```

#### Data Migration:

```python
def migrate_data_structure():
    """Migrate data between versions"""
    data_manager = DataManager()
    
    # Example: Add new field to existing subjects
    subjects = data_manager.load_json(DATA_DIR / 'subjects.json')
    
    for subject_name, subject_data in subjects.items():
        if 'description' not in subject_data:
            subject_data['description'] = f"Study materials for {subject_name}"
            subject_data['migrated_at'] = datetime.datetime.now().isoformat()
    
    data_manager.save_json(DATA_DIR / 'subjects.json', subjects)
    print("Data migration completed")
```

## Security Implementation

### Authentication Security

#### Password Hashing:

```python
import hashlib
import secrets

class SecurityManager:
    def __init__(self, salt: str):
        self.salt = salt
    
    def hash_password(self, password: str) -> str:
        """Secure password hashing with salt"""
        return hashlib.sha256((password + self.salt).encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return self.hash_password(password) == hashed
    
    def generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
```

#### Session Management:

```python
def validate_session(self, login_timestamp: str) -> bool:
    """Validate session timestamp"""
    if not login_timestamp:
        return False
        
    auth_db = self.data_manager.load_json(DATA_DIR / 'chatbot_auth.json')
    
    # Check if auth database has required structure
    if not isinstance(auth_db, dict) or 'last_changed' not in auth_db:
        return False
        
    last_changed = auth_db['last_changed']
    
    # Session is valid if login was after last password change
    return login_timestamp >= last_changed
```

### Input Validation

#### File Upload Security:

```python
from werkzeug.utils import secure_filename

def validate_file_upload(file) -> bool:
    """Validate uploaded file"""
    if not file:
        return False
    
    # Check file extension
    if not file.filename.lower().endswith('.pdf'):
        return False
    
    # Check file size (example: 10MB limit)
    if len(file.read()) > 10 * 1024 * 1024:
        file.seek(0)  # Reset file pointer
        return False
    
    file.seek(0)  # Reset file pointer
    return True

def secure_file_path(filename: str, upload_folder: str) -> str:
    """Generate secure file path"""
    secure_name = secure_filename(filename)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(upload_folder, f"{timestamp}_{secure_name}")
```

#### XSS Prevention:

```python
import html

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS"""
    return html.escape(text.strip())

def sanitize_output(text: str) -> str:
    """Sanitize output for display"""
    return html.escape(text)
```

## Performance Optimization

### Caching Strategies

#### In-Memory Caching:

```python
from functools import lru_cache
import time

class CacheManager:
    def __init__(self, ttl: int = 300):  # 5 minutes TTL
        self.ttl = ttl
        self.cache = {}
    
    def get(self, key: str):
        """Get cached value if not expired"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value):
        """Set cached value with timestamp"""
        self.cache[key] = (value, time.time())

# Usage
cache = CacheManager()

@lru_cache(maxsize=128)
def expensive_nlp_operation(text: str):
    """Cache expensive NLP operations"""
    # Perform expensive operation
    return result
```

#### Database Query Optimization:

```python
def search_units_optimized(query: str, nlp_processor) -> List[Dict]:
    """Optimized search with early termination"""
    subjects = self.get_subjects()
    query_clean = nlp_processor.preprocess_text(query)
    results = []
    
    # Early termination if query is too short
    if len(query_clean) < 2:
        return results
    
    for subject_name, subject_data in subjects.items():
        # Quick relevance check before detailed processing
        if query_clean not in subject_name.lower():
            continue
        
        # Process only relevant subjects
        subject_score = calculate_relevance(query_clean, subject_name, subject_data)
        
        if subject_score > 0:
            # Process units only for relevant subjects
            for unit_name, unit_data in subject_data.get('units', {}).items():
                unit_score = calculate_unit_relevance(query_clean, unit_name, unit_data)
                if unit_score > 0:
                    results.append({
                        'subject': subject_name,
                        'unit': unit_name,
                        'data': unit_data,
                        'score': subject_score + unit_score
                    })
    
    # Sort and limit results
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:20]  # Limit to top 20 results
```

### Frontend Optimization

#### Lazy Loading:

```javascript
class LazyLoader {
    constructor() {
        this.observer = new IntersectionObserver(this.handleIntersection.bind(this));
    }
    
    observe(element) {
        this.observer.observe(element);
    }
    
    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                this.loadContent(entry.target);
                this.observer.unobserve(entry.target);
            }
        });
    }
    
    loadContent(element) {
        // Load content when element becomes visible
        const src = element.dataset.src;
        if (src) {
            element.src = src;
        }
    }
}

// Usage for chat history
const lazyLoader = new LazyLoader();
document.querySelectorAll('.chat-message[data-src]').forEach(msg => {
    lazyLoader.observe(msg);
});
```

#### Debouncing User Input:

```javascript
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Debounce search input
const searchInput = document.getElementById('searchInput');
const debouncedSearch = debounce((query) => {
    performSearch(query);
}, 300);

searchInput.addEventListener('input', (e) => {
    debouncedSearch(e.target.value);
});
```

## Deployment

### Production Configuration

#### Gunicorn Configuration:

```bash
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### Environment Variables:

```python
# config.py
import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    UPLOAD_FOLDER = Path(os.environ.get('UPLOAD_FOLDER') or 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    SALT = os.environ.get('SALT') or 'smartbuddy_salt_2024'
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

#### Docker Deployment:

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--config", "gunicorn.conf.py", "server:app"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  smartbuddy:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - SALT=${SALT}
    restart: unless-stopped
```

### Monitoring and Logging

#### Application Logging:

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """Configure application logging"""
    if not app.debug:
        file_handler = RotatingFileHandler('logs/smartbuddy.log', 
                                         maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('SmartBuddy startup')
```

#### Health Check Endpoint:

```python
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.0.0'
    })
```

## Contributing Guidelines

### Code Review Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-emotion-detection
   ```

2. **Make Changes**
   - Follow code style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test Changes**
   ```bash
   python -m pytest tests/
   python test_nlp.py
   ```

4. **Submit Pull Request**
   - Clear description of changes
   - Link to relevant issues
   - Include screenshots for UI changes

### Commit Message Format

```
type(scope): brief description

Detailed description (optional)

- bullet point 1
- bullet point 2
```

Examples:
```
feat(nlp): add confidence emotion detection
fix(auth): resolve session validation issue
docs(readme): update installation instructions
```

### Issue Reporting

#### Bug Report Template:
```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Go to...
2. Click on...
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g. Windows 10]
- Browser: [e.g. Chrome 91]
- Python Version: [e.g. 3.9.0]
```

#### Feature Request Template:
```markdown
## Feature Description
Clear description of the feature

## Problem Statement
What problem does this solve?

## Proposed Solution
How should this be implemented?

## Alternatives Considered
Other approaches considered

## Additional Context
Any additional information
```

## Troubleshooting Common Issues

### Development Issues

#### Port Already in Use:
```bash
# Find process using port 5000
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # macOS/Linux

# Kill process
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # macOS/Linux
```

#### NLTK Download Issues:
```python
# Force NLTK data download
import nltk
nltk.download('all', force=True)
```

#### Permission Issues:
```bash
# Fix file permissions
chmod 755 smartbuddy/
chmod 644 smartbuddy/data/*.json
```

### Production Issues

#### Memory Leaks:
```python
# Monitor memory usage
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

#### Slow Response Times:
```python
# Add performance monitoring
import time

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper
```

## Future Development

### Roadmap

#### Version 2.0 Features:
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Database migration (PostgreSQL)
- [ ] Microservices architecture

#### Enhancement Ideas:
- [ ] Integration with calendar systems
- [ ] Study timer and productivity features
- [ ] Mood tracking and analytics
- [ ] Peer support features
- [ ] Integration with learning management systems

### Extension Points

#### Plugin Architecture:
```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name: str, plugin):
        """Register a new plugin"""
        self.plugins[name] = plugin
    
    def process_message(self, message: str, plugins: List[str]):
        """Process message through specified plugins"""
        for plugin_name in plugins:
            if plugin_name in self.plugins:
                message = self.plugins[plugin].process(message)
        return message

# Example plugin
class TranslationPlugin:
    def process(self, message: str):
        # Translate message logic
        return translated_message
```

#### Custom Emotion Handlers:
```python
class CustomEmotionHandler:
    def __init__(self, emotion: str, handler_func):
        self.emotion = emotion
        self.handler_func = handler_func
    
    def can_handle(self, emotion: str) -> bool:
        return emotion == self.emotion
    
    def handle(self, text: str, context: str) -> str:
        return self.handler_func(text, context)

# Usage
nlp.register_emotion_handler('custom', CustomEmotionHandler('custom', custom_handler))
```

---

This developer guide provides comprehensive information for contributing to SmartBuddy. For specific questions or issues, please refer to the project repository or contact the development team.

Happy coding! 🚀
