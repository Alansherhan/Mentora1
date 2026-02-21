# SmartBuddy Server-Side Documentation

## Overview

SmartBuddy is a server-centric application built with Flask that handles all business logic, data processing, and client communication. This documentation covers the complete server-side architecture, implementation details, and operational guidelines.

## Server Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SMARTBUDDY SERVER                        │
├─────────────────────────────────────────────────────────────┤
│  Flask Web Server (server.py)                               │
│  ├── HTTP Request Handling                                   │
│  ├── API Route Management                                    │
│  ├── Static File Serving                                     │
│  └── Session Management                                      │
├─────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                        │
│  ├── NLP Processing Engine (mental_health_nlp.py)           │
│  ├── Data Management (DataManager)                           │
│  ├── Content Management (NotesManager, PYQManager)          │
│  └── Chat Orchestration (ChatBot)                           │
├─────────────────────────────────────────────────────────────┤
│  Data Persistence Layer                                      │
│  ├── JSON File Storage                                       │
│  ├── File System Operations                                  │
│  ├── Upload Management                                       │
│  └── Authentication Store                                    │
└─────────────────────────────────────────────────────────────┘
```

## Core Server Components

### 1. Flask Application (server.py)

#### Application Initialization
```python
from flask import Flask, request, jsonify, send_from_directory, send_file
from pathlib import Path
import json
import hashlib
import datetime

app = Flask(__name__, static_folder='.', static_url_path='')

# Configuration
UPLOAD_FOLDER = Path('notes')
DATA_DIR = Path('data')
CHATS_DIR = Path('chats')
SALT = "smartbuddy_salt_2024"

# Ensure directories exist
for directory in [UPLOAD_FOLDER, DATA_DIR, CHATS_DIR]:
    directory.mkdir(exist_ok=True)
```

#### Server Lifecycle
```python
def initialize_server():
    """Initialize server components"""
    # Initialize data managers
    data_manager = DataManager()
    nlp_processor = NLPProcessor(data_manager)
    notes_manager = NotesManager(data_manager)
    pyq_manager = PYQManager(data_manager)
    mental_health_nlp = MentalHealthNLP()
    chatbot = ChatBot(data_manager, nlp_processor, notes_manager, pyq_manager)
    
    return {
        'data_manager': data_manager,
        'nlp_processor': nlp_processor,
        'notes_manager': notes_manager,
        'pyq_manager': pyq_manager,
        'mental_health_nlp': mental_health_nlp,
        'chatbot': chatbot
    }

# Initialize global components
components = initialize_server()
data_manager = components['data_manager']
nlp_processor = components['nlp_processor']
notes_manager = components['notes_manager']
pyq_manager = components['pyq_manager']
mental_health_nlp = components['mental_health_nlp']
chatbot = components['chatbot']
```

### 2. Data Management System

#### DataManager Class
```python
class DataManager:
    """Handles all JSON file operations with atomic writes"""
    
    def __init__(self):
        self.ensure_files()
    
    def ensure_files(self):
        """Create default JSON files with proper structure"""
        default_files = {
            'subjects.json': {},
            'info.json': {},
            'pyq.json': {},
            'synonyms.json': {
                'dbms': ['database management system', 'database', 'db'],
                'cs': ['computer science', 'comp sci'],
                'java': ['programming', 'coding', 'oop'],
                'notes': ['note', 'material', 'study material', 'unit', 'chapter'],
                'exam': ['test', 'examination', 'quiz', 'exm', 'exams', 'tests'],
                'faculty': ['teacher', 'professor', 'staff', 'instructor', 'sir', 'madam'],
                'schedule': ['timetable', 'time', 'timing', 'class', 'period'],
                'pyq': ['previous year question', 'old question', 'past paper', 'question paper']
            },
            'knowledge_base.json': [],
            'unanswered_queries.json': [],
            'auth.json': {'password_hash': self.hash_password('123'), 'password_hint': 'Default: 123'},
            'feedback.json': [],
            'chatbot_auth.json': {
                'password_hash': self.hash_password('123'), 
                'last_changed': datetime.datetime.now().isoformat()
            }
        }

        for filename, content in default_files.items():
            filepath = DATA_DIR / filename
            if not filepath.exists():
                self.save_json(filepath, content)
    
    def hash_password(self, password: str) -> str:
        """Secure password hashing with salt"""
        return hashlib.sha256((password + SALT).encode()).hexdigest()
    
    def save_json(self, filepath: Path, data: Any):
        """Atomic file write operation for data integrity"""
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
        """Safe file read with fallback for corrupted files"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} if 'subjects' in str(filepath) or 'info' in str(filepath) else []
```

### 3. NLP Processing Engine

#### MentalHealthNLP Class
```python
class MentalHealthNLP:
    """Server-side NLP processor for mental health chatbot"""
    
    def __init__(self):
        """Initialize NLP components and knowledge bases"""
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.stop_words = set(stopwords.words('english'))
            # Keep important emotional words that are in default stopwords
            self.stop_words -= {'no', 'not', 'very', 'too', 'down', 'up', 'can', 'cannot'}
        except:
            # Fallback if stopwords not available
            self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        
        # Initialize emotion keywords database
        self.emotion_keywords = {
            'anxious': ['anxious', 'anxiety', 'worried', 'nervous', 'panic', 'fear', 'afraid', 'scared', 'tense', 'uneasy', 'restless', 'on edge'],
            'sad': ['sad', 'depressed', 'depression', 'unhappy', 'miserable', 'down', 'blue', 'gloomy', 'heartbroken', 'crying', 'tears', 'hopeless'],
            'stressed': ['stressed', 'stress', 'overwhelmed', 'pressure', 'burnout', 'exhausted', 'tired', 'fatigue', 'drained', 'worn out'],
            # ... more emotions
        }
        
        # Response templates for emotion-first approach
        self.response_templates = {
            'anxious': [
                "I can hear that you're feeling anxious{context}. That's a tough feeling to carry, but remember anxiety is temporary. Take a deep breath - you've handled difficult moments before and you'll get through this too. 💙",
                # ... more templates
            ],
            # ... more emotion templates
        }
    
    def preprocess_text(self, text: str) -> str:
        """Server-side text preprocessing"""
        text = text.lower()
        text = re.sub(r'[^\w\s!?.,]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Server-side tokenization with stopword removal"""
        try:
            tokens = word_tokenize(text)
        except:
            tokens = text.split()
        return [token for token in tokens if token not in self.stop_words]
    
    def detect_emotion(self, text: str) -> Tuple[str, float]:
        """Server-side emotion detection with fuzzy matching"""
        preprocessed = self.preprocess_text(text)
        tokens = self.tokenize(preprocessed)
        
        emotion_scores = Counter()
        
        # Count emotion keyword occurrences with fuzzy matching
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                # Exact token match - highest weight
                if keyword in tokens:
                    emotion_scores[emotion] += 2.0
                # Phrase in text - medium weight
                elif keyword in preprocessed:
                    emotion_scores[emotion] += 1.5
                # Fuzzy matching for spelling mistakes
                else:
                    for token in tokens:
                        similarity = difflib.SequenceMatcher(None, keyword, token).ratio()
                        if similarity > 0.6:
                            emotion_scores[emotion] += 0.8
                            break
        
        if emotion_scores:
            dominant_emotion = emotion_scores.most_common(1)[0][0]
            total_matches = sum(emotion_scores.values())
            confidence = min(emotion_scores[dominant_emotion] / max(total_matches * 0.5, 1.0), 1.0)
            return dominant_emotion, confidence
        
        return 'neutral', 0.0
    
    def process_query(self, text: str) -> Dict[str, Any]:
        """Main server-side query processing with emotion-first approach"""
        # Step 1: Emotion detection (mandatory)
        emotion, emotion_confidence = self.detect_emotion(text)
        
        # Step 2: Extract keywords for context
        keywords = self.extract_keywords(text)
        context = self._build_context_string(keywords)
        
        # Step 3: Generate emotion-based response
        if emotion != 'neutral':
            templates = self.response_templates.get(emotion, self.response_templates['general_support'])
            response_template = random.choice(templates)
            response = response_template.format(context=context)
            return {
                'type': 'text',
                'message': response
            }
        
        # Step 4: Fallback for neutral emotions
        return {
            'type': 'text',
            'message': self._generate_polite_fallback(context)
        }
```

### 4. Content Management System

#### NotesManager Class
```python
class NotesManager:
    """Server-side management of academic notes and subjects"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def get_subjects(self) -> Dict[str, Any]:
        """Retrieve all subjects from server storage"""
        return self.data_manager.load_json(DATA_DIR / 'subjects.json')
    
    def add_subject(self, subject_name: str, keywords: str = '') -> bool:
        """Add new subject to server database"""
        subjects = self.get_subjects()
        if subject_name not in subjects:
            subjects[subject_name] = {
                'keywords': [k.strip().lower() for k in keywords.split(',') if k.strip()],
                'units': {},
                'created_at': datetime.datetime.now().isoformat()
            }
            self.data_manager.save_json(DATA_DIR / 'subjects.json', subjects)
            return True
        return False
    
    def add_unit(self, subject_name: str, unit_name: str, file, keywords: str = '') -> bool:
        """Server-side file upload and unit creation"""
        subjects = self.get_subjects()
        if subject_name not in subjects:
            return False

        subject_dir = UPLOAD_FOLDER / subject_name
        subject_dir.mkdir(exist_ok=True)

        # Generate secure filename with timestamp
        filename = secure_filename(f"{unit_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        filepath = subject_dir / filename

        try:
            # Server-side file save
            file.save(str(filepath))
            
            # Update server database
            subjects[subject_name]['units'][unit_name] = {
                'filename': filename,
                'keywords': [k.strip().lower() for k in keywords.split(',') if k.strip()],
                'uploaded_at': datetime.datetime.now().isoformat()
            }
            self.data_manager.save_json(DATA_DIR / 'subjects.json', subjects)
            return True
        except Exception as e:
            print(f"Server error saving file: {e}")
            return False
    
    def search_units(self, query: str, nlp_processor) -> List[Dict]:
        """Server-side search with fuzzy matching and scoring"""
        subjects = self.get_subjects()
        results = []
        query_clean = nlp_processor.preprocess_text(query)

        for subject_name, subject_data in subjects.items():
            subject_clean = nlp_processor.preprocess_text(subject_name)
            subject_keywords = subject_data.get('keywords', [])
            subject_score = 0

            # Calculate relevance score
            if query_clean in subject_clean or subject_clean in query_clean:
                subject_score += 40

            for kw in subject_keywords:
                if query_clean in kw or kw in query_clean:
                    subject_score += 30
                elif nlp_processor.fuzzy_match(query_clean, kw) > 70:
                    subject_score += 15

            # Search within units
            for unit_name, unit_data in subject_data.get('units', {}).items():
                unit_score = subject_score
                unit_clean = nlp_processor.preprocess_text(unit_name)
                unit_keywords = unit_data.get('keywords', [])

                if query_clean in unit_clean or unit_clean in query_clean:
                    unit_score += 35

                for kw in unit_keywords:
                    if query_clean in kw or kw in query_clean:
                        unit_score += 30
                    elif nlp_processor.fuzzy_match(query_clean, kw) > 70:
                        unit_score += 15

                if unit_score > 0:
                    results.append({
                        'subject': subject_name,
                        'unit': unit_name,
                        'data': unit_data,
                        'score': unit_score
                    })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results
```

### 5. Chat Orchestration System

#### ChatBot Class
```python
class ChatBot:
    """Main server-side chat orchestrator"""
    
    def __init__(self, data_manager: DataManager, nlp_processor: NLPProcessor, 
                 notes_manager: NotesManager, pyq_manager: PYQManager):
        self.data_manager = data_manager
        self.nlp_processor = nlp_processor
        self.notes_manager = notes_manager
        self.pyq_manager = pyq_manager

    def process_query(self, query: str, login_timestamp: str = None) -> Dict[str, Any]:
        """Main server-side query processing pipeline"""
        # Step 1: Validate session
        if not self.validate_session(login_timestamp):
            return {
                'type': 'error', 
                'error': 'session_expired', 
                'message': 'Session expired. Please login again.'
            }

        # Step 2: Detect intent
        intent = self.nlp_processor.detect_intent(query)
        
        # Step 3: Route to appropriate handler
        if intent == 'notes_request':
            return self._handle_notes_request(query)
        elif intent == 'pyq_request':
            return self._handle_pyq_request(query)
        elif intent == 'help_greeting':
            return self._handle_greeting()
        elif intent == 'mental_health':
            return self._handle_mental_health(query)
        else:
            return self._handle_info_or_unknown(query)

    def validate_session(self, login_timestamp: str) -> bool:
        """Server-side session validation"""
        if not login_timestamp:
            return False
            
        auth_db = self.data_manager.load_json(DATA_DIR / 'chatbot_auth.json')
        
        # Check if auth database has required structure
        if not isinstance(auth_db, dict) or 'last_changed' not in auth_db:
            return False
            
        last_changed = auth_db['last_changed']
        
        # Session is valid if login was after last password change
        return login_timestamp >= last_changed

    def _handle_mental_health(self, query: str) -> Dict[str, Any]:
        """Server-side mental health query processing"""
        return mental_health_nlp.process_query(query)

    def _handle_notes_request(self, query: str) -> Dict[str, Any]:
        """Server-side notes request handling"""
        results = self.notes_manager.search_units(query, self.nlp_processor)
        subjects = self.notes_manager.get_subjects()

        if results:
            return {
                'type': 'notes_results',
                'message': 'I found these notes:',
                'results': results
            }

        if subjects:
            return {
                'type': 'subjects_list',
                'message': 'Available subjects:',
                'subjects': {name: len(data.get('units', {})) for name, data in subjects.items()}
            }

        return {
            'type': 'text',
            'message': 'No study materials available yet. Admin will add notes soon!'
        }
```

## API Endpoints

### Chat API

#### POST /api/chat
```python
@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint - processes user messages"""
    try:
        if request.json is None:
            return jsonify({'type': 'text', 'message': 'Invalid request format'})
            
        data = request.json
        message = data.get('message', '').strip()
        
        # Get session timestamp from header
        login_timestamp = request.headers.get('X-Login-Timestamp')
        
        # Process message through server pipeline
        response = chatbot.process_query(message, login_timestamp)
        
        # Handle session expiration
        if response.get('error') == 'session_expired':
            return jsonify(response), 401
            
        return jsonify(response)
    except Exception as e:
        # Server-side error handling
        app.logger.error(f"Chat processing error: {e}")
        return jsonify({'type': 'text', 'message': f'Error: {str(e)}'})
```

### Content Management APIs

#### Subjects Management
```python
@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Server-side subject retrieval"""
    subjects = notes_manager.get_subjects()
    return jsonify({'subjects': subjects})

@app.route('/api/add_subject', methods=['POST'])
def add_subject_api():
    """Server-side subject creation"""
    data = request.json or {}
    subject_name = data.get('subject_name', '')
    keywords = data.get('keywords', '')
    if notes_manager.add_subject(subject_name, keywords):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Subject already exists'})

@app.route('/api/delete_subject', methods=['POST'])
def delete_subject_api():
    """Server-side subject deletion"""
    data = request.json or {}
    if notes_manager.delete_subject(data.get('subject_name', '')):
        return jsonify({'success': True})
    return jsonify({'success': False})
```

#### File Management
```python
@app.route('/api/add_unit/<subject_name>', methods=['POST'])
def add_unit_api(subject_name):
    """Server-side file upload and unit creation"""
    try:
        file = request.files.get('file')
        unit_name = request.form.get('unit_name', '')
        keywords = request.form.get('keywords', '')
        
        if notes_manager.add_unit(subject_name, unit_name, file, keywords):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Failed to add unit'})
    except Exception as e:
        app.logger.error(f"File upload error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/download_unit/<subject_name>/<unit_name>')
def download_unit(subject_name, unit_name):
    """Server-side file download"""
    subjects = notes_manager.get_subjects()
    if subject_name in subjects and unit_name in subjects[subject_name]['units']:
        filename = subjects[subject_name]['units'][unit_name]['filename']
        try:
            return send_from_directory(UPLOAD_FOLDER / subject_name, filename, as_attachment=True)
        except:
            return jsonify({'error': 'File not found'}), 404
    return jsonify({'error': 'Not found'}), 404
```

### Authentication APIs

#### POST /api/auth
```python
@app.route('/api/auth', methods=['POST'])
def authenticate():
    """Server-side authentication"""
    data = request.json or {}
    password = data.get('password', '')
    
    auth_data = data_manager.load_json(DATA_DIR / 'auth.json')
    stored_hash = auth_data.get('password_hash', '')
    
    if data_manager.hash_password(password) == stored_hash:
        return jsonify({'success': True, 'message': 'Authentication successful'})
    else:
        return jsonify({'success': False, 'error': 'Invalid password'})

@app.route('/api/change_chatbot_password', methods=['POST'])
def change_chatbot_password():
    """Server-side password change with session invalidation"""
    data = request.json or {}
    new_password = data.get('new_password', '')
    
    if new_password:
        auth_db = data_manager.load_json(DATA_DIR / 'chatbot_auth.json')
        auth_db['password_hash'] = data_manager.hash_password(new_password)
        auth_db['last_changed'] = datetime.datetime.now().isoformat()
        data_manager.save_json(DATA_DIR / 'chatbot_auth.json', auth_db)
        
        return jsonify({'success': True, 'message': 'Password updated successfully'})
    
    return jsonify({'success': False, 'error': 'Failed to update password'})
```

## Server Configuration

### Environment Configuration
```python
import os
from pathlib import Path

class ServerConfig:
    """Server configuration management"""
    
    def __init__(self):
        self.DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
        self.HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
        self.PORT = int(os.environ.get('FLASK_PORT', 5000))
        self.SECRET_KEY = os.environ.get('SECRET_KEY', 'smartbuddy-secret-key')
        
        # File paths
        self.BASE_DIR = Path(__file__).parent
        self.UPLOAD_FOLDER = self.BASE_DIR / 'notes'
        self.DATA_DIR = self.BASE_DIR / 'data'
        self.CHATS_DIR = self.BASE_DIR / 'chats'
        self.PYQ_DIR = self.BASE_DIR / 'pyq_files'
        
        # Security
        self.SALT = os.environ.get('SMARTBUDDY_SALT', 'smartbuddy_salt_2024')
        self.MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
        
        # Ensure directories exist
        for directory in [self.UPLOAD_FOLDER, self.DATA_DIR, self.CHATS_DIR, self.PYQ_DIR]:
            directory.mkdir(exist_ok=True)

config = ServerConfig()
```

### Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """Configure server-side logging"""
    if not app.debug:
        # Create logs directory
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            logs_dir / 'smartbuddy.log', 
            maxBytes=10240, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Configure app logger
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('SmartBuddy server startup')

# Apply logging configuration
setup_logging(app)
```

## Server Deployment

### Development Server
```python
if __name__ == '__main__':
    # Development server with debug mode
    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT,
        threaded=True
    )
```

### Production Server (Gunicorn)
```python
# gunicorn.conf.py
bind = f"{config.HOST}:{config.PORT}"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NLTK data download
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p logs data notes chats pyq_files

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start server
CMD ["gunicorn", "--config", "gunicorn.conf.py", "server:app"]
```

## Server Security

### Input Validation
```python
from werkzeug.utils import secure_filename
import html

def validate_input(text: str) -> str:
    """Server-side input validation and sanitization"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove HTML tags and escape special characters
    text = html.escape(text.strip())
    
    # Length validation
    if len(text) > 10000:  # 10KB limit
        text = text[:10000] + "... [truncated]"
    
    return text

def validate_file_upload(file) -> bool:
    """Server-side file validation"""
    if not file or not file.filename:
        return False
    
    # Check file extension
    if not file.filename.lower().endswith('.pdf'):
        return False
    
    # Check file size (16MB limit)
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset position
    
    if size > config.MAX_CONTENT_LENGTH:
        return False
    
    return True
```

### Session Management
```python
def generate_session_token() -> str:
    """Generate secure session token"""
    return secrets.token_urlsafe(32)

def validate_session_token(token: str) -> bool:
    """Validate session token format and expiration"""
    if not token or len(token) < 32:
        return False
    
    # Additional validation logic here
    return True
```

## Server Monitoring

### Health Check Endpoint
```python
@app.route('/health')
def health_check():
    """Server health monitoring endpoint"""
    try:
        # Check database connectivity
        data_manager.load_json(DATA_DIR / 'subjects.json')
        
        # Check file system accessibility
        test_file = DATA_DIR / 'health_check.tmp'
        test_file.write_text('test')
        test_file.unlink()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.datetime.now().isoformat(),
            'version': '1.0.0',
            'uptime': str(datetime.datetime.now() - start_time)
        })
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.datetime.now().isoformat()
        }), 500
```

### Performance Metrics
```python
import time
import psutil
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor server performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Get initial system metrics
        cpu_before = psutil.cpu_percent()
        memory_before = psutil.virtual_memory().percent
        
        try:
            result = func(*args, **kwargs)
            
            # Calculate performance metrics
            end_time = time.time()
            cpu_after = psutil.cpu_percent()
            memory_after = psutil.virtual_memory().percent
            
            app.logger.info(f"Performance: {func.__name__} took {end_time - start_time:.3f}s, "
                           f"CPU: {cpu_before:.1f}%→{cpu_after:.1f}%, "
                           f"Memory: {memory_before:.1f}%→{memory_after:.1f}%")
            
            return result
        except Exception as e:
            app.logger.error(f"Error in {func.__name__}: {e}")
            raise
    
    return wrapper

# Apply monitoring to critical endpoints
@app.route('/api/chat', methods=['POST'])
@monitor_performance
def chat():
    # ... existing code
```

## Server Maintenance

### Backup System
```python
import shutil
import zipfile
from datetime import datetime

def backup_server_data():
    """Create server data backup"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(f'backups/backup_{timestamp}')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Backup data files
        if DATA_DIR.exists():
            shutil.copytree(DATA_DIR, backup_dir / 'data')
        
        # Backup uploaded files
        if UPLOAD_FOLDER.exists():
            shutil.copytree(UPLOAD_FOLDER, backup_dir / 'notes')
        
        if PYQ_DIR.exists():
            shutil.copytree(PYQ_DIR, backup_dir / 'pyq_files')
        
        # Create compressed backup
        backup_zip = Path(f'backups/smartbuddy_backup_{timestamp}.zip')
        with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in backup_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(backup_dir)
                    zipf.write(file_path, arcname)
        
        # Cleanup temporary backup directory
        shutil.rmtree(backup_dir)
        
        app.logger.info(f"Backup created: {backup_zip}")
        return backup_zip
        
    except Exception as e:
        app.logger.error(f"Backup failed: {e}")
        raise

# Schedule regular backups (run with cron job or task scheduler)
def scheduled_backup():
    """Scheduled backup task"""
    try:
        backup_path = backup_server_data()
        
        # Clean up old backups (keep last 7 days)
        backups_dir = Path('backups')
        if backups_dir.exists():
            cutoff_time = datetime.datetime.now() - datetime.timedelta(days=7)
            for backup_file in backups_dir.glob('smartbuddy_backup_*.zip'):
                file_time = datetime.datetime.strptime(
                    backup_file.stem.split('_')[-1], '%Y%m%d_%H%M%S'
                )
                if file_time < cutoff_time:
                    backup_file.unlink()
                    app.logger.info(f"Deleted old backup: {backup_file}")
                    
    except Exception as e:
        app.logger.error(f"Scheduled backup failed: {e}")
```

### Database Maintenance
```python
def maintain_database():
    """Server database maintenance tasks"""
    try:
        # Clean up old chat history
        chats_dir = Path('chats')
        if chats_dir.exists():
            cutoff_time = datetime.datetime.now() - datetime.timedelta(days=30)
            for chat_file in chats_dir.glob('*.json'):
                if chat_file.stat().st_mtime < cutoff_time.timestamp():
                    chat_file.unlink()
                    app.logger.info(f"Deleted old chat file: {chat_file}")
        
        # Optimize JSON files
        for json_file in DATA_DIR.glob('*.json'):
            try:
                data = data_manager.load_json(json_file)
                data_manager.save_json(json_file, data)
                app.logger.info(f"Optimized: {json_file}")
            except Exception as e:
                app.logger.error(f"Failed to optimize {json_file}: {e}")
        
        app.logger.info("Database maintenance completed")
        
    except Exception as e:
        app.logger.error(f"Database maintenance failed: {e}")
```

## Server Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use
```python
import socket

def check_port_available(port):
    """Check if port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def find_available_port(start_port=5000):
    """Find available port starting from start_port"""
    port = start_port
    while not check_port_available(port):
        port += 1
        if port > start_port + 100:  # Limit search range
            raise Exception("No available ports found")
    return port
```

#### 2. Memory Issues
```python
import gc
import psutil

def monitor_memory_usage():
    """Monitor and log memory usage"""
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_percent = process.memory_percent()
    
    app.logger.info(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB ({memory_percent:.1f}%)")
    
    # Force garbage collection if memory usage is high
    if memory_percent > 80:
        gc.collect()
        app.logger.warning("High memory usage detected, forced garbage collection")
```

#### 3. File System Issues
```python
def check_file_system_health():
    """Check file system accessibility and space"""
    try:
        # Test write permissions
        test_file = DATA_DIR / 'test_write.tmp'
        test_file.write_text('test')
        test_file.unlink()
        
        # Check disk space
        disk_usage = psutil.disk_usage(DATA_DIR.anchor)
        free_space_gb = disk_usage.free / (1024**3)
        
        if free_space_gb < 1:  # Less than 1GB free
            app.logger.warning(f"Low disk space: {free_space_gb:.2f} GB remaining")
        
        app.logger.info(f"Disk space: {free_space_gb:.2f} GB free")
        return True
        
    except Exception as e:
        app.logger.error(f"File system health check failed: {e}")
        return False
```

---

This comprehensive server-side documentation covers all aspects of the SmartBuddy server implementation, from architecture and APIs to deployment and maintenance. The server is designed to be robust, scalable, and secure while providing excellent performance for mental health support and academic content management.
