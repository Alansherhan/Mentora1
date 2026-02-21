# SmartBuddy AI - API Documentation

## 📡 Overview

SmartBuddy AI provides a RESTful API for mental health chatbot functionality, academic resource management, and administrative operations. All API endpoints use JSON for request/response format.

## 🔗 Base URL
```
http://localhost:5000/api
```

## 🧠 Mental Health & Chatbot APIs

### POST /api/chat
Send a message to the SmartBuddy chatbot for mental health support or academic assistance.

**Request:**
```json
{
  "message": "I'm feeling anxious about my exams"
}
```

**Response:**
```json
{
  "type": "text",
  "message": "I can hear how overwhelmed you're feeling. That stress is real and valid. Remember: you don't have to handle everything perfectly. Good enough is enough. 💪"
}
```

**Response Types:**
- `text`: Simple text response
- `notes_results`: Search results from notes
- `pyq_results`: Search results from PYQ documents
- `subjects_list`: List of available subjects
- `units_list`: List of units in a subject
- `pyq_list`: List of PYQ documents by type

**Example Response - Notes Results:**
```json
{
  "type": "notes_results",
  "message": "Found 3 matching units in Mathematics",
  "results": [
    {
      "subject": "Mathematics",
      "unit": "Calculus Basics",
      "data": {
        "filename": "calculus_basics.pdf",
        "keywords": ["calculus", "derivatives", "limits"],
        "uploaded_at": "2024-01-15T10:30:00"
      },
      "score": 85
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request (missing message)
- `500`: Server error

### POST /api/feedback
Submit feedback about the chatbot response.

**Request:**
```json
{
  "message": "Great response!",
  "rating": 5,
  "session_id": "optional_session_identifier"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback submitted successfully"
}
```

## 🔐 Authentication APIs

### POST /api/auth
Authenticate admin user for access to admin panel.

**Request:**
```json
{
  "password": "123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Authentication successful"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Invalid password"
}
```

### POST /api/change_chatbot_password
Change the chatbot access password.

**Request:**
```json
{
  "current_password": "123",
  "new_password": "new_secure_password"
}
```

**Response:**
```json
{
  "success": true
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Incorrect current password"
}
```

### POST /api/admin/change_chatbot_password
Change chatbot password (admin endpoint).

**Request:**
```json
{
  "current_pwd": "123",
  "new_pwd": "new_secure_password"
}
```

**Response:**
```json
{
  "success": true
}
```

## 📚 Notes Management APIs

### GET /api/subjects
Get all subjects with their units and metadata.

**Response:**
```json
{
  "subjects": {
    "Mathematics": {
      "keywords": ["calculus", "algebra", "geometry"],
      "units": {
        "Calculus Basics": {
          "filename": "calculus_basics.pdf",
          "keywords": ["derivatives", "limits", "functions"],
          "uploaded_at": "2024-01-15T10:30:00"
        }
      },
      "created_at": "2024-01-01T12:00:00"
    }
  }
}
```

### POST /api/add_subject
Add a new subject.

**Request:**
```json
{
  "subject_name": "Physics",
  "keywords": "mechanics, thermodynamics, optics"
}
```

**Response:**
```json
{
  "success": true
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Subject already exists"
}
```

### POST /api/edit_subject
Edit an existing subject.

**Request:**
```json
{
  "old_name": "Mathematics",
  "new_name": "Advanced Mathematics",
  "keywords": "calculus, algebra, geometry, statistics"
}
```

**Response:**
```json
{
  "success": true
}
```

### POST /api/delete_subject
Delete a subject and all its units.

**Request:**
```json
{
  "subject_name": "Physics"
}
```

**Response:**
```json
{
  "success": true
}
```

### POST /api/add_unit/<subject_name>
Add a unit to a subject (multipart form data).

**Request (multipart/form-data):**
```
file: [PDF file]
unit_name: "Calculus Advanced"
keywords: "integration, differential equations, applications"
```

**Response:**
```json
{
  "success": true
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Failed to add unit"
}
```

### POST /api/edit_unit
Edit an existing unit.

**Request:**
```json
{
  "subject": "Mathematics",
  "old_unit_name": "Calculus Basics",
  "new_unit_name": "Calculus Fundamentals",
  "keywords": "derivatives, limits, functions, continuity"
}
```

**Response:**
```json
{
  "success": true
}
```

### POST /api/delete_unit
Delete a unit from a subject.

**Request:**
```json
{
  "subject_name": "Mathematics",
  "unit_name": "Calculus Basics"
}
```

**Response:**
```json
{
  "success": true
}
```

### GET /api/download_unit/<subject_name>/<unit_name>
Download a unit PDF file.

**Response:**
- Returns the PDF file as a download
- Content-Type: application/pdf
- Content-Disposition: attachment

**Error Response:**
```
Status: 404 Not Found
```

## 📄 PYQ Management APIs

### GET /api/pyq
Get all PYQ documents and metadata.

**Response:**
```json
{
  "pyqs": {
    "pyq_123": {
      "name": "Mathematics Final Exam 2023",
      "type": "PYQ",
      "filename": "math_final_2023.pdf",
      "keywords": ["calculus", "algebra", "final exam"],
      "uploaded_at": "2024-01-15T10:30:00"
    }
  }
}
```

### POST /api/pyq/upload
Upload a new PYQ document (multipart form data).

**Request (multipart/form-data):**
```
file: [PDF file]
name: "Physics Midterm 2023"
type: "PYQ"
keywords: "mechanics, thermodynamics, midterm"
```

**Response:**
```json
{
  "success": true,
  "pyq_id": "pyq_456"
}
```

### POST /api/pyq/edit
Edit PYQ metadata.

**Request:**
```json
{
  "id": "pyq_123",
  "name": "Mathematics Final Exam 2023 Updated",
  "keywords": "calculus, algebra, geometry, final exam",
  "type": "PYQ"
}
```

**Response:**
```json
{
  "success": true
}
```

### POST /api/pyq/delete
Delete a PYQ document.

**Request:**
```json
{
  "id": "pyq_123"
}
```

**Response:**
```json
{
  "success": true
}
```

### GET /api/pyq/download/<pyq_id>
Download a PYQ PDF file.

**Response:**
- Returns the PDF file as a download
- Content-Type: application/pdf
- Content-Disposition: attachment

**Error Response:**
```
Status: 404 Not Found
```

## 📊 Analytics & Statistics APIs

### GET /api/admin/stats
Get system statistics and usage data.

**Response:**
```json
{
  "subjects": 5,
  "pyqs": 12,
  "info_sections": 3,
  "unanswered": 2,
  "knowledge": 8,
  "total_chats": 150,
  "active_users": 25
}
```

### GET /api/search
Global search across all resources.

**Request:**
```
GET /api/search?q=calculus
```

**Response:**
```json
{
  "notes_results": [
    {
      "subject": "Mathematics",
      "unit": "Calculus Basics",
      "score": 95
    }
  ],
  "pyq_results": [
    {
      "name": "Mathematics Final Exam 2023",
      "score": 88
    }
  ]
}
```

## 🎯 NLP Processing APIs

### POST /api/nlp/analyze
Analyze text for emotion and sentiment (advanced usage).

**Request:**
```json
{
  "text": "I'm feeling happy but also a bit anxious about tomorrow"
}
```

**Response:**
```json
{
  "emotion": "happy",
  "confidence": 0.75,
  "sentiment": "mixed",
  "keywords": ["happy", "anxious"],
  "concerns": ["future"]
}
```

## 📝 Response Formats

### Success Response Format
```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response Format
```json
{
  "success": false,
  "error": "Error description"
}
```

### Chatbot Response Format
```json
{
  "type": "text|notes_results|pyq_results|subjects_list|units_list|pyq_list",
  "message": "Response message",
  "results": [ ... ] // Optional, for result types
}
```

## 🔒 Authentication

### Admin Authentication
Most admin endpoints require authentication via session:
```javascript
// First authenticate
POST /api/auth
{
  "password": "123"
}

// Then use session cookie for admin endpoints
GET /api/admin/stats
```

### Chatbot Authentication
Chatbot can be configured to require password:
```javascript
POST /api/chat
{
  "message": "Hello",
  "password": "chatbot_password" // If enabled
}
```

## 🚨 Error Handling

### Common HTTP Status Codes
- `200`: Success
- `400`: Bad Request (missing/invalid parameters)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error

### Error Response Examples
```json
// Missing required field
{
  "success": false,
  "error": "Message is required"
}

// Authentication failed
{
  "success": false,
  "error": "Invalid password"
}

// Resource not found
{
  "success": false,
  "error": "Subject not found"
}

// File upload error
{
  "success": false,
  "error": "Only PDF files are allowed"
}
```

## 📝 Request/Response Examples

### Complete Chat Flow
```javascript
// 1. Send message
POST /api/chat
{
  "message": "I need help with calculus"
}

// 2. Receive response
{
  "type": "notes_results",
  "message": "Found 2 matching units in Mathematics",
  "results": [
    {
      "subject": "Mathematics",
      "unit": "Calculus Basics",
      "data": {
        "filename": "calculus_basics.pdf",
        "keywords": ["calculus", "derivatives", "limits"],
        "uploaded_at": "2024-01-15T10:30:00"
      },
      "score": 90
    }
  ]
}

// 3. Download file
GET /api/download_unit/Mathematics/Calculus%20Basics
// Returns PDF file
```

### Complete Admin Flow
```javascript
// 1. Authenticate
POST /api/auth
{
  "password": "123"
}
// Response: { "success": true }

// 2. Add subject
POST /api/add_subject
{
  "subject_name": "Chemistry",
  "keywords": "organic, inorganic, physical"
}
// Response: { "success": true }

// 3. Add unit (multipart form)
POST /api/add_unit/Chemistry
Content-Type: multipart/form-data
// Form data with file and metadata
// Response: { "success": true }
```

## 🔄 Rate Limiting

### Current Limits
- **Chat Messages**: No limit (development)
- **File Uploads**: 10MB per file
- **API Requests**: No limit (development)

### Recommended Production Limits
- **Chat Messages**: 100 requests per hour per user
- **File Uploads**: 50MB per file, 100 uploads per day
- **Admin APIs**: 1000 requests per hour per admin

## 🧪 Testing the API

### Using curl
```bash
# Chat with the bot
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I am feeling anxious"}'

# Get subjects
curl -X GET http://localhost:5000/api/subjects

# Upload a file
curl -X POST http://localhost:5000/api/add_unit/Mathematics \
  -F "file=@test.pdf" \
  -F "unit_name=Test Unit" \
  -F "keywords=test, sample"
```

### Using JavaScript
```javascript
// Chat with the bot
async function chat(message) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  return await response.json();
}

// Get subjects
async function getSubjects() {
  const response = await fetch('/api/subjects');
  return await response.json();
}
```

### Using Python
```python
import requests

# Chat with the bot
def chat(message):
    response = requests.post('http://localhost:5000/api/chat', 
        json={'message': message})
    return response.json()

# Get subjects
def get_subjects():
    response = requests.get('http://localhost:5000/api/subjects')
    return response.json()
```

## 🔧 SDK Examples

### JavaScript SDK
```javascript
class SmartBuddyAPI {
  constructor(baseURL = 'http://localhost:5000/api') {
    this.baseURL = baseURL;
  }
  
  async chat(message) {
    const response = await fetch(`${this.baseURL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return await response.json();
  }
  
  async getSubjects() {
    const response = await fetch(`${this.baseURL}/subjects`);
    return await response.json();
  }
  
  async uploadUnit(subject, file, unitName, keywords) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('unit_name', unitName);
    formData.append('keywords', keywords);
    
    const response = await fetch(`${this.baseURL}/add_unit/${subject}`, {
      method: 'POST',
      body: formData
    });
    return await response.json();
  }
}

// Usage
const api = new SmartBuddyAPI();
const response = await api.chat("I'm feeling stressed about exams");
console.log(response.message);
```

## 📚 Integration Examples

### Web Application Integration
```javascript
// React component example
function ChatBot() {
  const [message, setMessage] = useState('');
  const [responses, setResponses] = useState([]);
  
  const sendMessage = async () => {
    const response = await api.chat(message);
    setResponses([...responses, response]);
    setMessage('');
  };
  
  return (
    <div>
      <div>
        {responses.map((resp, i) => (
          <div key={i}>{resp.message}</div>
        ))}
      </div>
      <input 
        value={message} 
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
```

### Mobile App Integration
```python
# Python Flask backend for mobile API
@app.route('/mobile/chat', methods=['POST'])
def mobile_chat():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    
    # Log for analytics
    log_user_interaction(user_id, message)
    
    # Process with SmartBuddy
    response = mental_health_nlp.process_query(message)
    
    return jsonify(response)
```

## 🔍 Debugging

### Common Issues
1. **CORS Errors**: Ensure proper headers are set
2. **File Upload Issues**: Check file size and format
3. **Authentication**: Verify session management
4. **JSON Parsing**: Ensure valid JSON format

### Debug Mode
Enable debug mode for detailed error messages:
```python
app.run(debug=True)
```

### Logging
Check server logs for detailed error information:
```bash
tail -f smartbuddy.log
```

---

This API documentation provides comprehensive information for integrating with SmartBuddy AI's RESTful API. For additional support, refer to the technical documentation or contact the development team.
