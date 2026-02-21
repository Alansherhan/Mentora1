# SmartBuddy - Mental Health Chatbot & Study Assistant

SmartBuddy is an intelligent chatbot that combines mental health support with academic assistance. It features emotion-first NLP processing, study material management, and a modern web interface.

## 🌟 Key Features

### Mental Health Support
- **Emotion-First NLP**: Advanced emotion detection using classical NLP techniques
- **Fuzzy Matching**: Handles spelling mistakes and variations in emotional expressions
- **Empathetic Responses**: Context-aware, supportive responses for various emotional states
- **14+ Emotion Types**: Supports anxiety, sadness, stress, happiness, calm, anger, guilt, pride, relief, gratitude, motivation, excitement, confusion, and loneliness
- **No Silent Failures**: Always provides a meaningful response, never says "I don't understand"

### Academic Assistant
- **Study Material Management**: Upload and organize notes by subjects and units
- **PYQ (Previous Year Questions)**: Dedicated section for exam preparation materials
- **Smart Search**: Fuzzy matching and synonym expansion for finding relevant content
- **Keyword-based Organization**: Efficient categorization with custom keywords

### Modern Web Interface
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark/Light Themes**: Toggle between visual themes
- **Real-time Chat**: Smooth chat experience with typing indicators
- **Session Management**: Secure login system with session validation
- **Chat History**: Persistent conversation history with sidebar navigation

## 🏗️ Architecture

### Backend (Flask)
- **server.py**: Main Flask application with RESTful API
- **mental_health_nlp.py**: Core NLP engine for emotion detection and response generation
- **Data Management**: JSON-based storage with atomic file operations
- **Security**: Password hashing with salt, session validation

### Frontend
- **index.html**: Main chat interface with modern CSS and JavaScript
- **admin.html**: Administrative dashboard for content management
- **script.js**: Client-side logic for chat, authentication, and UI interactions
- **Responsive CSS**: Custom CSS with animations and transitions

### Data Storage
- **JSON Files**: Lightweight, human-readable data storage
- **Organized Structure**: Separate files for subjects, PYQs, auth, chat history
- **Atomic Operations**: Temporary file pattern for data integrity

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smartbuddy
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python server.py
   ```

4. **Access the application**
   - Main Chat Interface: http://localhost:5000
   - Admin Dashboard: http://localhost:5000/admin

### Default Credentials
- **Default Password**: `123` (change immediately after first login)

## 📁 Project Structure

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
├── data/                    # Data storage directory
│   ├── subjects.json        # Study subjects and units
│   ├── pyq.json            # Previous year questions
│   ├── auth.json           # Authentication data
│   ├── chatbot_auth.json   # Chatbot session management
│   ├── synonyms.json       # Keyword synonyms
│   ├── knowledge_base.json # Q&A knowledge base
│   ├── feedback.json       # User feedback
│   └── unanswered_queries.json # Unanswered questions
├── notes/                   # Uploaded study materials
├── chats/                   # Chat history storage
└── pyq_files/              # PYQ file uploads
```

## 🧠 Mental Health NLP Engine

### Emotion Detection Algorithm
1. **Preprocessing**: Text cleaning and normalization
2. **Tokenization**: Word-level tokenization with stopword removal
3. **Lemmatization**: Reducing words to base forms
4. **Keyword Matching**: Exact, phrase, and fuzzy matching
5. **Confidence Scoring**: Weighted scoring for emotion detection
6. **Context Extraction**: Identifying concern areas (academic, social, etc.)

### Supported Emotions
- **Positive**: happy, calm, proud, relieved, grateful, motivated, excited
- **Negative**: anxious, sad, stressed, angry, guilty, lonely, confused
- **Response Generation**: Context-aware templates with personalization

### Fuzzy Matching
- **Spelling Tolerance**: 60-70% similarity threshold
- **Partial Matching**: Handles incomplete words
- **Context Awareness**: Considers sentence structure and patterns

## 📚 Academic Features

### Study Material Management
- **Subject Organization**: Hierarchical structure (Subject → Units → Files)
- **PDF Upload**: Secure file handling with validation
- **Keyword Tagging**: Custom keywords for better searchability
- **Version Control**: Timestamped uploads with metadata

### PYQ System
- **Categorized Storage**: Organized by exam type/subject
- **Smart Search**: Content-based search with ranking
- **Download Support**: Direct file downloads with proper headers

### Search Algorithm
- **Multi-field Matching**: Name, keywords, and content search
- **Scoring System**: Relevance-based result ranking
- **Synonym Expansion**: Enhanced matching using word synonyms

## 🔐 Security Features

### Authentication
- **Password Hashing**: SHA-256 with salt
- **Session Management**: Timestamp-based session validation
- **Password Change**: Secure password update with session invalidation

### Data Protection
- **File Upload Security**: Filename sanitization and type validation
- **XSS Prevention**: HTML escaping for user inputs
- **CSRF Protection**: Request validation and secure headers

## 🎨 User Interface

### Design Principles
- **Modern Aesthetics**: Gradient backgrounds, smooth animations
- **Accessibility**: High contrast, keyboard navigation
- **Responsive Design**: Mobile-first approach
- **User Experience**: Intuitive navigation and feedback

### Interactive Elements
- **Typing Indicators**: Real-time response feedback
- **Message Animations**: Smooth message appearance
- **Hover Effects**: Interactive button and card states
- **Theme Toggle**: Dark/light mode switching

## 🔧 API Endpoints

### Chat API
- `POST /api/chat` - Process chat messages
- `GET /api/subjects` - List all subjects
- `POST /api/add_subject` - Add new subject
- `POST /api/delete_subject` - Delete subject
- `POST /api/edit_subject` - Edit subject details

### Unit Management
- `POST /api/add_unit/<subject>` - Add unit to subject
- `POST /api/delete_unit` - Delete unit
- `POST /api/edit_unit` - Edit unit details
- `GET /api/download_unit/<subject>/<unit>` - Download unit file

### PYQ Management
- `GET /api/pyqs` - List all PYQs
- `POST /api/add_pyq` - Add new PYQ
- `POST /api/edit_pyq` - Edit PYQ details
- `POST /api/delete_pyq` - Delete PYQ

### Info Management
- `GET /api/info` - Get information categories
- `POST /api/add_info` - Add information category
- `POST /api/delete_info` - Delete information category

## 📚 Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Complete user manual
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Development documentation
- **[API Reference](docs/API_REFERENCE.md)** - API documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture
- **[Hardware Requirements](docs/HARDWARE_REQUIREMENTS.md)** - System requirements

## 🧪 Testing

### NLP Testing
```bash
# Test the NLP engine
python test_nlp.py

# Enhanced NLP testing
python test_nlp_enhanced.py
```

### Authentication Testing
```bash
# Test authentication system
python fix_auth.py

# Test password reset
python reset_pwd.py
```

## � Performance Considerations

### Optimization Features
- **Lazy Loading**: On-demand content loading
- **Caching**: In-memory caching for frequently accessed data
- **Atomic Operations**: Efficient file I/O with temporary files
- **Connection Pooling**: Optimized database connections

### Scalability
- **Modular Design**: Separated concerns for easy scaling
- **JSON Storage**: Lightweight and fast for small to medium datasets
- **Flask Framework**: Lightweight and performant web framework

## 🤝 Contributing

### Development Guidelines
1. **Code Style**: Follow PEP 8 for Python code
2. **Testing**: Write tests for new features
3. **Documentation**: Update documentation for changes
4. **Security**: Follow security best practices

### Feature Requests
- **New Emotions**: Add support for additional emotional states
- **Multi-language**: Extend to other languages
- **Voice Support**: Add speech-to-text and text-to-speech
- **Mobile App**: Develop native mobile applications

## � License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **NLTK**: Natural Language Toolkit for text processing
- **Flask**: Web framework for Python
- **Werkzeug**: WSGI utility library
- **Modern CSS**: Gradient designs and animations

## � Support

For support, feature requests, or bug reports, please create an issue in the repository or contact the development team.

---

**SmartBuddy** - Your intelligent companion for mental wellness and academic success. 🌟
