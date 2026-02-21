# SmartBuddy AI - Technical Documentation

## 🏗️ System Architecture

### Overview
SmartBuddy AI is a Flask-based web application that combines mental health support with academic resource management. The system uses classical NLP techniques for emotion processing and JSON-based storage for data persistence.

### Technology Stack
- **Backend**: Python 3.8+, Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **NLP**: NLTK, custom classical NLP pipeline
- **Storage**: JSON files with file system for PDFs
- **Authentication**: Flask sessions with password hashing

## 🔧 Core Components

### 1. Flask Application (`server.py`)

#### Main Application Structure
```python
app = Flask(__name__)
app.secret_key = 'your-secret-key'
data_manager = DataManager()
notes_manager = NotesManager(data_manager)
pyq_manager = PYQManager(data_manager)
nlp_processor = NLPProcessor()
mental_health_nlp = MentalHealthNLP()
```

#### Key Routes
- **Authentication**: `/api/auth`, `/api/change_chatbot_password`
- **Notes Management**: `/api/subjects`, `/api/add_subject`, `/api/edit_subject`
- **PYQ Management**: `/api/pyq`, `/api/pyq/upload`, `/api/pyq/edit`
- **Chatbot**: `/api/chat`, `/api/feedback`
- **File Downloads**: `/api/download_unit/<subject>/<unit>`, `/api/pyq/download/<id>`

### 2. Data Management (`DataManager`)

#### JSON File Operations
```python
class DataManager:
    def load_json(self, filepath: Path) -> Dict[str, Any]
    def save_json(self, filepath: Path, data: Dict[str, Any]) -> bool
    def hash_password(self, password: str) -> str
    def verify_password(self, password: str, hashed: str) -> bool
```

#### Data Files Structure
- `subjects.json`: Academic notes and units
- `pyq.json`: Previous year questions and documents
- `admin.json`: Administrator credentials
- `auth.json`: Chatbot authentication data

### 3. Notes Management (`NotesManager`)

#### Subject Operations
```python
def add_subject(self, subject_name: str, keywords: str) -> bool
def edit_subject(self, old_name: str, new_name: str, keywords: str) -> bool
def delete_subject(self, subject_name: str) -> bool
def get_subjects(self) -> Dict[str, Any]
```

#### Unit Operations
```python
def add_unit(self, subject_name: str, unit_name: str, file, keywords: str) -> bool
def edit_unit(self, subject_name: str, old_unit_name: str, new_unit_name: str, keywords: str) -> bool
def delete_unit(self, subject_name: str, unit_name: str) -> bool
def search_units(self, query: str, nlp_processor) -> List[Dict]
```

### 4. PYQ Management (`PYQManager`)

#### Document Operations
```python
def add_pyq(self, name: str, file_type: str, file, keywords: str) -> Dict[str, Any]
def edit_pyq(self, pyq_id: str, name: str, keywords: str, file_type: str) -> Dict[str, Any]
def delete_pyq(self, pyq_id: str) -> Dict[str, Any]
def get_pyqs(self) -> Dict[str, Any]
def search_pyqs(self, query: str, nlp_processor) -> List[Dict]
```

## 🧠 Mental Health NLP Pipeline

### 1. Text Preprocessing
```python
def preprocess_text(self, text: str) -> str:
    # Convert to lowercase
    text = text.lower()
    # Remove special characters (keep emotional punctuation)
    text = re.sub(r'[^\w\s!?.,]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text
```

### 2. Tokenization & Lemmatization
```python
def tokenize(self, text: str) -> List[str]:
    try:
        tokens = word_tokenize(text)
    except:
        tokens = text.split()
    return [token for token in tokens if token not in self.stop_words]

def lemmatize(self, tokens: List[str]) -> List[str]:
    try:
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    except:
        return tokens
```

### 3. Emotion Detection with Fuzzy Matching
```python
def detect_emotion(self, text: str) -> Tuple[str, float]:
    emotion_scores = Counter()
    
    for emotion, keywords in self.emotion_keywords.items():
        for keyword in keywords:
            # Exact match (highest weight)
            if keyword in tokens:
                emotion_scores[emotion] += 2.0
            # Phrase match (medium weight)
            elif keyword in preprocessed:
                emotion_scores[emotion] += 1.5
            # Fuzzy match for spelling mistakes
            else:
                for token in tokens:
                    similarity = difflib.SequenceMatcher(None, keyword, token).ratio()
                    if similarity > 0.6:  # 60% threshold for typos
                        emotion_scores[emotion] += 0.8
```

### 4. Intent Detection
```python
def detect_intent(self, text: str) -> str:
    text_lower = text.lower()
    
    # Mental health detection with fuzzy matching
    text_words = text_lower.split()
    for word in text_words:
        # Direct match
        if any(keyword in word for keyword in all_emotional_keywords):
            return 'mental_health'
        # Fuzzy match for spelling mistakes
        for keyword in all_emotional_keywords:
            if difflib.SequenceMatcher(None, word, keyword).ratio() >= 0.7:
                return 'mental_health'
```

### 5. Response Generation
```python
def process_query(self, text: str) -> Dict[str, Any]:
    # Step 1: Emotion detection (FIRST PRIORITY)
    emotion, emotion_confidence = self.detect_emotion(text)
    
    # Step 2: Extract keywords for context
    keywords = self.extract_keywords(text)
    context = self._build_context_string(keywords)
    
    # Step 3: Generate emotion-based response
    if emotion != 'neutral':
        templates = self.response_templates.get(emotion, self.response_templates['general_support'])
        response_template = random.choice(templates)
        response = response_template.format(context=context)
        return {'type': 'text', 'message': response}
```

## 🎨 Frontend Architecture

### 1. HTML Structure

#### Main Chatbot Interface (`index.html`)
```html
<div class="chat-container">
    <div class="chat-header">
        <h2>SmartBuddy AI</h2>
        <div class="status-indicator"></div>
    </div>
    <div class="chat-messages" id="chatContainer"></div>
    <div class="chat-input">
        <input type="text" id="messageInput" placeholder="Type your message...">
        <button onclick="sendMessage()">Send</button>
    </div>
</div>
```

#### Admin Panel (`admin.html`)
```html
<div class="admin-container">
    <nav class="sidebar">
        <ul class="nav-menu">
            <li onclick="switchView('dashboard')">📊 Dashboard</li>
            <li onclick="switchView('notes')">📚 Notes Management</li>
            <li onclick="switchView('pyq')">📄 PYQ & Others</li>
            <li onclick="switchView('chatbot-users')">👥 Chatbot Users</li>
        </ul>
    </nav>
    <main class="content">
        <div id="dashboard-view" class="view"></div>
        <div id="notes-view" class="view"></div>
        <div id="pyq-view" class="view"></div>
    </main>
</div>
```

### 2. JavaScript Modules

#### Chat Functionality (`script.js`)
```javascript
class ChatBot {
    async sendMessage() {
        const message = document.getElementById('messageInput').value;
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        this.displayResponse(data);
    }
    
    displayResponse(data) {
        switch(data.type) {
            case 'text': this.addMessage(data.message, 'assistant'); break;
            case 'notes_results': this.displayNotesResults(data); break;
            case 'pyq_results': this.displayPyqResults(data); break;
        }
    }
}
```

#### Admin Functions
```javascript
// Subject Management
async function editSubject(name) {
    document.getElementById(`subject-edit-${name}`).style.display = 'block';
}

async function saveSubjectEdit(oldName) {
    const newName = document.getElementById(`subject-edit-name-${oldName}`).value;
    const keywords = document.getElementById(`subject-edit-keywords-${oldName}`).value;
    
    const response = await fetch('/api/edit_subject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ old_name: oldName, new_name: newName, keywords })
    });
}

// File Upload
async function uploadFile(subject) {
    const formData = new FormData();
    formData.append('file', document.getElementById(`unit-file-${subject}`).files[0]);
    formData.append('unit_name', document.getElementById(`unit-name-${subject}`).value);
    formData.append('keywords', document.getElementById(`unit-keywords-${subject}`).value);
    
    await fetch(`/api/add_unit/${subject}`, {
        method: 'POST',
        body: formData
    });
}
```

### 3. CSS Architecture

#### Responsive Design
```css
.chat-container {
    max-width: 800px;
    margin: 0 auto;
    height: 100vh;
    display: flex;
    flex-direction: column;
}

@media (max-width: 768px) {
    .chat-container {
        margin: 0;
        height: 100vh;
    }
    
    .admin-container {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
        height: auto;
    }
}
```

#### Component Styling
```css
.message {
    margin: 10px 0;
    padding: 12px 16px;
    border-radius: 18px;
    max-width: 70%;
}

.message.user {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    margin-left: auto;
}

.message.assistant {
    background: #f8f9fa;
    color: #333;
    margin-right: auto;
}
```

## 🔒 Security Implementation

### 1. Authentication System
```python
def hash_password(self, password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(self, password: str, hashed: str) -> bool:
    """Verify password against stored hash"""
    salt, password_hash = hashed.split(':')
    return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
```

### 2. File Upload Security
```python
def secure_file_upload(file, upload_folder: Path) -> str:
    """Secure file upload with validation"""
    # Check file extension
    if not file.filename.endswith('.pdf'):
        raise ValueError("Only PDF files are allowed")
    
    # Generate secure filename
    filename = werkzeug.utils.secure_filename(file.filename)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    secure_name = f"{timestamp}_{filename}"
    
    # Validate file size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)     # Seek back to start
    
    if size > 10 * 1024 * 1024:  # 10MB limit
        raise ValueError("File too large")
    
    # Save file
    filepath = upload_folder / secure_name
    file.save(str(filepath))
    
    return secure_name
```

### 3. Input Validation
```python
def validate_input(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate input data"""
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    
    # Sanitize string inputs
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = bleach.clean(value.strip())
    
    return True
```

## 📊 Performance Optimization

### 1. NLP Caching
```python
class CachedNLP:
    def __init__(self):
        self.emotion_cache = {}
        self.sentiment_cache = {}
    
    def detect_emotion_cached(self, text: str) -> Tuple[str, float]:
        cache_key = hash(text.lower())
        if cache_key in self.emotion_cache:
            return self.emotion_cache[cache_key]
        
        result = self.detect_emotion(text)
        self.emotion_cache[cache_key] = result
        return result
```

### 2. Lazy Loading
```javascript
class LazyLoader {
    constructor() {
        this.loadedViews = new Set();
    }
    
    async loadView(viewName) {
        if (!this.loadedViews.has(viewName)) {
            await this.loadViewData(viewName);
            this.loadedViews.add(viewName);
        }
        this.showView(viewName);
    }
}
```

### 3. Database Optimization
```python
class OptimizedDataManager:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    def load_json_cached(self, filepath: Path) -> Dict[str, Any]:
        now = time.time()
        cache_key = str(filepath)
        
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if now - timestamp < self.cache_timeout:
                return data
        
        data = self.load_json(filepath)
        self.cache[cache_key] = (data, now)
        return data
```

## 🧪 Testing Strategy

### 1. Unit Tests
```python
import unittest
from mental_health_nlp import MentalHealthNLP

class TestMentalHealthNLP(unittest.TestCase):
    def setUp(self):
        self.nlp = MentalHealthNLP()
    
    def test_emotion_detection(self):
        emotion, confidence = self.nlp.detect_emotion("I am very happy today")
        self.assertEqual(emotion, 'happy')
        self.assertGreater(confidence, 0.5)
    
    def test_fuzzy_matching(self):
        emotion, confidence = self.nlp.detect_emotion("I feel hapy")
        self.assertEqual(emotion, 'happy')  # Should detect "happy" from "hapy"
    
    def test_indirect_expressions(self):
        emotion, confidence = self.nlp.detect_emotion("I feel heavy today")
        self.assertIn(emotion, ['sad', 'depressed'])
```

### 2. Integration Tests
```python
class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_chat_endpoint(self):
        response = self.app.post('/api/chat', 
            json={'message': 'I am feeling anxious'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['type'], 'text')
        self.assertIn('message', data)
    
    def test_file_upload(self):
        with open('test.pdf', 'rb') as f:
            response = self.app.post('/api/add_unit/Math',
                data={'file': f, 'unit_name': 'Test Unit', 'keywords': 'test'},
                content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
```

### 3. Frontend Tests
```javascript
describe('ChatBot Interface', () => {
    test('should send message and receive response', async () => {
        const mockFetch = jest.fn().mockResolvedValue({
            json: () => Promise.resolve({
                type: 'text',
                message: 'I understand you\'re feeling anxious.'
            })
        });
        global.fetch = mockFetch;
        
        await sendMessage();
        expect(mockFetch).toHaveBeenCalledWith('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: 'test message' })
        });
    });
});
```

## 📈 Monitoring & Analytics

### 1. Logging System
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smartbuddy.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.path}")

@app.after_request
def log_response(response):
    logger.info(f"Response: {response.status_code}")
    return response
```

### 2. Performance Metrics
```python
import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

@app.route('/api/chat')
@measure_time
def chat():
    # Chat logic here
    pass
```

### 3. Error Tracking
```python
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong'
    }), 500
```

## 🚀 Deployment Guide

### 1. Production Setup
```bash
# Install production dependencies
pip install gunicorn

# Set environment variables
export FLASK_ENV=production
export SECRET_KEY='your-production-secret-key'

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

### 2. Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "server:app"]
```

### 3. Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/your/static/files;
    }
}
```

## 🔮 Future Architecture Plans

### 1. Microservices Migration
- **Chat Service**: Dedicated mental health NLP service
- **File Service**: Separate file management microservice
- **Auth Service**: Centralized authentication service
- **Analytics Service**: Usage tracking and insights

### 2. Database Migration
```python
# Current: JSON files
# Future: PostgreSQL with SQLAlchemy

from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Subject(Base):
    __tablename__ = 'subjects'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    keywords = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

### 3. API Versioning
```python
@app.route('/api/v1/chat')
def chat_v1():
    # Current implementation
    pass

@app.route('/api/v2/chat')
def chat_v2():
    # Enhanced implementation with GPT integration
    pass
```

---

This technical documentation provides comprehensive details about SmartBuddy AI's implementation, architecture, and future development plans.
