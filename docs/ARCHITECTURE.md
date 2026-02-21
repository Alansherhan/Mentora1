# SmartBuddy Architecture Documentation

## Overview

SmartBuddy is built on a modular architecture that separates concerns between mental health processing, academic resource management, and user interface components. The system uses Flask as the web framework with JSON-based data storage for simplicity and portability.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Data Storage  │
│                 │    │                 │    │                 │
│ • index.html    │◄──►│ • Flask App     │◄──►│ • JSON Files    │
│ • admin.html    │    │ • API Endpoints │    │ • File System   │
│ • JavaScript    │    │ • NLP Engine    │    │ • Uploads       │
│ • CSS/Styles    │    │ • Auth System   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Backend Server (`server.py`)

The main Flask application orchestrates all system components:

#### Key Classes:
- **DataManager**: Handles all JSON file operations with atomic writes
- **NLPProcessor**: Processes text queries and detects user intent
- **NotesManager**: Manages academic subjects and units
- **PYQManager**: Handles previous year questions and documents
- **ChatBot**: Main conversation orchestrator

#### Design Patterns:
- **Repository Pattern**: Data managers abstract storage operations
- **Strategy Pattern**: Different response strategies based on intent
- **Factory Pattern**: Response generation based on emotion/intent

### 2. Mental Health NLP Engine (`mental_health_nlp.py`)

#### Processing Pipeline:
1. **Text Preprocessing**
   - Lowercase conversion
   - Special character removal
   - Whitespace normalization

2. **Tokenization & Lemmatization**
   - NLTK-based tokenization
   - Stopword removal (with emotional word exceptions)
   - Word lemmatization to base forms

3. **Emotion Detection**
   - Keyword matching with fuzzy string comparison
   - Weighted scoring system
   - Confidence calculation
   - Context extraction

4. **Response Generation**
   - Template-based responses
   - Context personalization
   - Emoji integration
   - Fallback mechanisms

#### Emotion Categories:
- **Positive**: happy, calm, grateful, motivated, proud, relieved, excited
- **Negative**: anxious, sad, stressed, confused, lonely, angry, guilty
- **General Support**: fallback responses for unclear inputs

### 3. Frontend Architecture

#### Main Interface (`index.html`):
- **Responsive Design**: Mobile-first CSS Grid/Flexbox
- **Component Structure**: Modular CSS with custom properties
- **Interactive Elements**: JavaScript for real-time updates
- **Theme System**: CSS variables for dark/light modes

#### Admin Dashboard (`admin.html`):
- **Management Interface**: Content management capabilities
- **File Upload**: Drag-and-drop PDF uploads
- **Data Tables**: Dynamic content display
- **Form Validation**: Client-side input validation

#### JavaScript Logic (`script.js`):
- **API Communication**: Fetch-based HTTP requests
- **State Management**: Session handling and UI state
- **Event Handling**: User interaction processing
- **Dynamic Rendering**: Content generation and updates

## Data Architecture

### Storage Structure

```
data/
├── subjects.json           # Academic subjects and units
├── pyq.json               # Previous year questions
├── auth.json              # Admin authentication
├── chatbot_auth.json      # Chatbot session management
├── synonyms.json          # Word synonyms for search
├── knowledge_base.json    # Q&A knowledge base
├── feedback.json          # User feedback
└── unanswered_queries.json # Unanswered questions

uploads/
├── notes/                 # Subject-wise PDF storage
└── pyq_files/            # PYQ document storage

chats/                    # Chat history storage
```

### Data Models

#### Subject Model:
```json
{
  "subject_name": {
    "keywords": ["keyword1", "keyword2"],
    "units": {
      "unit_name": {
        "filename": "file.pdf",
        "keywords": ["unit_keyword1", "unit_keyword2"],
        "uploaded_at": "2024-01-01T12:00:00"
      }
    },
    "created_at": "2024-01-01T12:00:00"
  }
}
```

#### PYQ Model:
```json
{
  "pyq_id": {
    "name": "Document Name",
    "type": "PYQ|Timetable|Others",
    "filename": "file.pdf",
    "keywords": ["keyword1", "keyword2"],
    "uploaded_at": "2024-01-01T12:00:00"
  }
}
```

## API Architecture

### RESTful Endpoints

#### Chat System:
- `POST /api/chat` - Process chat messages with session validation
- Response types: text, subjects_list, units_list, notes_results, pyq_results

#### Academic Management:
- **Subjects**: CRUD operations for subject management
- **Units**: File upload and management for study materials
- **PYQs**: Document management for exam materials

#### Authentication:
- Session-based authentication with timestamp validation
- Password hashing with SHA-256 and salt
- Automatic session invalidation on password change

### Request/Response Flow

```
User Input → Frontend Validation → API Request → 
Intent Detection → NLP Processing → Response Generation → 
API Response → Frontend Rendering → User Display
```

## Security Architecture

### Authentication & Authorization:
- **Password Security**: SHA-256 hashing with unique salt
- **Session Management**: Timestamp-based validation
- **Access Control**: Role-based access for admin features

### Data Protection:
- **Input Validation**: Comprehensive sanitization
- **File Security**: Filename sanitization and type validation
- **XSS Prevention**: HTML escaping for user inputs
- **CSRF Protection**: Request validation

### File Upload Security:
- **File Type Validation**: PDF-only uploads
- **Filename Sanitization**: Secure filename generation
- **Path Validation**: Directory traversal prevention
- **Size Limits**: Configurable file size restrictions

## Performance Architecture

### Optimization Strategies:
- **Lazy Loading**: On-demand content loading
- **Caching**: In-memory caching for frequently accessed data
- **Atomic Operations**: Efficient file I/O with temporary files
- **Connection Management**: Optimized database connections

### Scalability Considerations:
- **Modular Design**: Separated concerns for easy scaling
- **JSON Storage**: Lightweight for small to medium datasets
- **Stateless Design**: Easy horizontal scaling
- **Resource Management**: Efficient memory usage

## NLP Architecture Details

### Emotion Detection Algorithm:

1. **Preprocessing Phase**:
   ```python
   def preprocess_text(self, text: str) -> str:
       text = text.lower()
       text = re.sub(r'[^\w\s!?.,]', ' ', text)
       text = re.sub(r'\s+', ' ', text).strip()
       return text
   ```

2. **Tokenization Phase**:
   ```python
   def tokenize(self, text: str) -> List[str]:
       tokens = word_tokenize(text)
       return [token for token in tokens if token not in self.stop_words]
   ```

3. **Fuzzy Matching Phase**:
   ```python
   for keyword in emotion_keywords:
       for token in tokens:
           similarity = difflib.SequenceMatcher(None, keyword, token).ratio()
           if similarity > 0.6:  # 60% similarity threshold
               emotion_scores[emotion] += 0.8
   ```

### Response Generation:
- **Template System**: Pre-defined response templates
- **Context Integration**: Dynamic context insertion
- **Personalization**: User-specific response customization
- **Fallback Strategy**: Graceful degradation for unclear inputs

## Frontend Architecture

### Component Structure:
- **Layout Components**: Header, sidebar, main content area
- **Interactive Components**: Chat interface, file upload, data tables
- **Utility Components**: Modals, loading indicators, notifications

### State Management:
- **Session State**: User authentication and preferences
- **UI State**: Theme, sidebar visibility, loading states
- **Chat State**: Message history, typing indicators

### Styling Architecture:
- **CSS Custom Properties**: Theme variables
- **Component-Based CSS**: Modular styling approach
- **Responsive Design**: Mobile-first media queries
- **Animation System**: CSS transitions and keyframes

## Deployment Architecture

### Development Environment:
- **Local Development**: Flask development server
- **Debug Mode**: Enabled for development
- **Hot Reload**: Automatic server restart on code changes

### Production Considerations:
- **WSGI Server**: Gunicorn or uWSGI for production
- **Reverse Proxy**: Nginx for load balancing and SSL
- **Process Management**: Systemd or PM2 for process management
- **Monitoring**: Logging and performance monitoring

## Integration Points

### External Dependencies:
- **NLTK**: Natural language processing
- **Flask**: Web framework
- **Werkzeug**: WSGI utilities
- **Difflib**: Fuzzy string matching

### Future Integration:
- **Database**: PostgreSQL for larger datasets
- **Cache**: Redis for performance optimization
- **Queue**: Celery for background tasks
- **Storage**: AWS S3 for file storage

## Monitoring & Logging

### Application Logging:
- **Error Logging**: Comprehensive error tracking
- **Access Logging**: Request/response logging
- **Performance Logging**: Response time tracking
- **User Activity**: Chat interaction logging

### Health Monitoring:
- **System Health**: Resource usage monitoring
- **API Health**: Endpoint availability checking
- **Database Health**: Storage system monitoring
- **User Experience**: Frontend performance tracking

This architecture provides a solid foundation for the SmartBuddy application, enabling scalability, maintainability, and extensibility while maintaining security and performance standards.
