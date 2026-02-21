# SmartBuddy API Reference

## Overview

SmartBuddy provides a RESTful API for chat interactions, content management, and administrative functions. All API endpoints return JSON responses and follow HTTP status codes for error handling.

## Base URL

```
http://localhost:5000/api
```

## Authentication

### Session-Based Authentication

SmartBuddy uses timestamp-based session validation for chat API access.

#### Headers
```
X-Login-Timestamp: <timestamp>
```

#### Session Validation
- Sessions are validated against the last password change timestamp
- If login timestamp is older than password change, session is invalid
- Clients must handle 401 responses and prompt for re-login

## Response Format

### Success Response
```json
{
    "success": true,
    "data": { ... },
    "message": "Operation completed successfully"
}
```

### Error Response
```json
{
    "success": false,
    "error": "error_type",
    "message": "Human-readable error message"
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized (session expired)
- `404` - Not Found
- `500` - Internal Server Error

## Chat API

### Send Message

Process a chat message and get AI response.

**Endpoint:** `POST /api/chat`

**Authentication:** Required (session header)

#### Request Body
```json
{
    "message": "I'm feeling anxious about exams"
}
```

#### Response Types

##### Text Response
```json
{
    "type": "text",
    "message": "I understand you're feeling anxious about exams. That anxiety sounds overwhelming. Your body is trying to protect you, even though it feels uncomfortable. Try grounding yourself by noticing 5 things you can see and 4 you can touch. 🌿"
}
```

##### Subjects List Response
```json
{
    "type": "subjects_list",
    "message": "Available subjects:",
    "subjects": {
        "Computer Science": 5,
        "Mathematics": 3,
        "Physics": 4
    }
}
```

##### Notes Results Response
```json
{
    "type": "notes_results",
    "message": "I found these notes:",
    "results": [
        {
            "subject": "Computer Science",
            "unit": "Data Structures",
            "data": {
                "filename": "data_structures_20240101_120000.pdf",
                "keywords": ["algorithms", "trees", "graphs"],
                "uploaded_at": "2024-01-01T12:00:00"
            },
            "score": 85
        }
    ]
}
```

##### PYQ Results Response
```json
{
    "type": "pyq_results",
    "message": "I found these PYQ materials:",
    "results": [
        {
            "id": "1",
            "data": {
                "name": "Computer Science Midterm 2023",
                "type": "PYQ",
                "filename": "cs_midterm_2023.pdf",
                "keywords": ["midterm", "exam", "questions"],
                "uploaded_at": "2024-01-01T12:00:00"
            },
            "score": 90
        }
    ]
}
```

##### PYQ List Response
```json
{
    "type": "pyq_list",
    "message": "Available PYQ materials:",
    "types": {
        "PYQ": 15,
        "Timetable": 3,
        "Others": 7
    }
}
```

#### Error Response
```json
{
    "type": "error",
    "error": "session_expired",
    "message": "Session expired. Please login again."
}
```

#### Example Request
```javascript
const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-Login-Timestamp': '2024-01-01T12:00:00'
    },
    body: JSON.stringify({
        message: 'I need help with data structures'
    })
});

const data = await response.json();
console.log(data);
```

## Subjects API

### Get All Subjects

Retrieve list of all subjects with their units.

**Endpoint:** `GET /api/subjects`

**Authentication:** Not required

#### Response
```json
{
    "subjects": {
        "Computer Science": {
            "keywords": ["programming", "coding", "algorithms"],
            "units": {
                "Data Structures": {
                    "filename": "data_structures.pdf",
                    "keywords": ["arrays", "linked lists", "trees"],
                    "uploaded_at": "2024-01-01T12:00:00"
                },
                "Algorithms": {
                    "filename": "algorithms.pdf",
                    "keywords": ["sorting", "searching", "complexity"],
                    "uploaded_at": "2024-01-01T12:00:00"
                }
            },
            "created_at": "2024-01-01T12:00:00"
        },
        "Mathematics": {
            "keywords": ["calculus", "algebra", "geometry"],
            "units": {
                "Calculus I": {
                    "filename": "calculus1.pdf",
                    "keywords": ["derivatives", "integrals", "limits"],
                    "uploaded_at": "2024-01-01T12:00:00"
                }
            },
            "created_at": "2024-01-01T12:00:00"
        }
    }
}
```

### Add Subject

Create a new subject.

**Endpoint:** `POST /api/add_subject`

**Authentication:** Not required

#### Request Body
```json
{
    "subject_name": "Physics",
    "keywords": "mechanics, thermodynamics, quantum"
}
```

#### Success Response
```json
{
    "success": true
}
```

#### Error Response (Subject Exists)
```json
{
    "success": false,
    "error": "Subject already exists"
}
```

### Edit Subject

Update subject name and keywords.

**Endpoint:** `POST /api/edit_subject`

**Authentication:** Not required

#### Request Body
```json
{
    "old_name": "Physics",
    "new_name": "Advanced Physics",
    "keywords": "mechanics, thermodynamics, quantum, relativity"
}
```

#### Success Response
```json
{
    "success": true
}
```

#### Error Response
```json
{
    "success": false,
    "error": "Failed to edit subject"
}
```

### Delete Subject

Delete a subject and all its units.

**Endpoint:** `POST /api/delete_subject`

**Authentication:** Not required

#### Request Body
```json
{
    "subject_name": "Physics"
}
```

#### Success Response
```json
{
    "success": true
}
```

#### Error Response
```json
{
    "success": false
}
```

## Units API

### Add Unit

Upload a PDF unit to a subject.

**Endpoint:** `POST /api/add_unit/<subject_name>`

**Authentication:** Not required

#### Request (multipart/form-data)
```
file: <PDF file>
unit_name: "Data Structures"
keywords: "arrays, linked lists, trees, graphs"
```

#### Success Response
```json
{
    "success": true
}
```

#### Error Response
```json
{
    "success": false,
    "error": "Failed to add unit"
}
```

#### Example Request (JavaScript)
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('unit_name', 'Data Structures');
formData.append('keywords', 'arrays, linked lists, trees');

const response = await fetch('/api/add_unit/Computer Science', {
    method: 'POST',
    body: formData
});
```

### Edit Unit

Update unit name and keywords.

**Endpoint:** `POST /api/edit_unit`

**Authentication:** Not required

#### Request Body
```json
{
    "subject": "Computer Science",
    "old_unit_name": "Data Structures",
    "new_unit_name": "Advanced Data Structures",
    "keywords": "arrays, linked lists, trees, graphs, heaps"
}
```

#### Success Response
```json
{
    "success": true
}
```

#### Error Response
```json
{
    "success": false,
    "error": "Failed to edit unit"
}
```

### Delete Unit

Delete a specific unit from a subject.

**Endpoint:** `POST /api/delete_unit`

**Authentication:** Not required

#### Request Body
```json
{
    "subject_name": "Computer Science",
    "unit_name": "Data Structures"
}
```

#### Success Response
```json
{
    "success": true
}
```

#### Error Response
```json
{
    "success": false
}
```

### Download Unit

Download a unit PDF file.

**Endpoint:** `GET /api/download_unit/<subject_name>/<unit_name>`

**Authentication:** Not required

#### Response
- Returns PDF file as attachment
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="unit_file.pdf"`

#### Error Response
```json
{
    "error": "File not found"
}
```

#### Example Usage
```html
<a href="/api/download_unit/Computer Science/Data Structures" download>
    Download Data Structures PDF
</a>
```

## PYQ API

### Get All PYQs

Retrieve list of all PYQ documents.

**Endpoint:** `GET /api/pyqs`

**Authentication:** Not required

#### Response
```json
{
    "pyqs": {
        "1": {
            "id": "1",
            "name": "Computer Science Midterm 2023",
            "type": "PYQ",
            "filename": "cs_midterm_2023.pdf",
            "keywords": ["midterm", "exam", "questions"],
            "uploaded_at": "2024-01-01T12:00:00"
        },
        "2": {
            "id": "2",
            "name": "Mathematics Final Exam 2023",
            "type": "PYQ",
            "filename": "math_final_2023.pdf",
            "keywords": ["final", "exam", "calculus"],
            "uploaded_at": "2024-01-01T12:00:00"
        }
    }
}
```

### Add PYQ

Upload a new PYQ document.

**Endpoint:** `POST /api/add_pyq`

**Authentication:** Not required

#### Request (multipart/form-data)
```
file: <PDF file>
name: "Computer Science Midterm 2024"
keywords: "midterm, exam, questions, algorithms"
file_type: "PYQ"
```

#### Success Response
```json
{
    "success": true,
    "id": "3"
}
```

#### Error Response
```json
{
    "success": false,
    "error": "Failed to upload PYQ"
}
```

### Edit PYQ

Update PYQ metadata.

**Endpoint:** `POST /api/edit_pyq`

**Authentication:** Not required

#### Request Body
```json
{
    "pyq_id": "1",
    "name": "Computer Science Midterm 2023 (Updated)",
    "keywords": "midterm, exam, questions, algorithms, data structures",
    "file_type": "PYQ"
}
```

#### Success Response
```json
{
    "success": true
}
```

#### Error Response
```json
{
    "success": false,
    "error": "PYQ not found"
}
```

### Delete PYQ

Delete a PYQ document.

**Endpoint:** `POST /api/delete_pyq`

**Authentication:** Not required

#### Request Body
```json
{
    "pyq_id": "1"
}
```

#### Success Response
```json
{
    "success": true
}
```

#### Error Response
```json
{
    "success": false,
    "error": "PYQ not found"
}
```

## Info Management API

### Get Info Categories

Retrieve all information categories.

**Endpoint:** `GET /api/info`

**Authentication:** Not required

#### Response
```json
{
    "info": {
        "General": {
            "content": "SmartBuddy is your AI assistant for mental health and academic support.",
            "keywords": ["about", "help", "information"],
            "created_at": "2024-01-01T12:00:00"
        },
        "Features": {
            "content": "SmartBuddy offers emotion detection, study material management, and more.",
            "keywords": ["features", "capabilities", "what can you do"],
            "created_at": "2024-01-01T12:00:00"
        }
    }
}
```

### Add Info Category

Create a new information category.

**Endpoint:** `POST /api/add_info`

**Authentication:** Not required

#### Request Body
```json
{
    "category": "Contact",
    "content": "For support, contact the admin at admin@example.com",
    "keywords": "contact, support, email, help"
}
```

#### Success Response
```json
{
    "success": true
}
```

### Delete Info Category

Delete an information category.

**Endpoint:** `POST /api/delete_info`

**Authentication:** Not required

#### Request Body
```json
{
    "category": "Contact"
}
```

#### Success Response
```json
{
    "success": true
}
```

#### Error Response
```json
{
    "success": false
}
```

## Authentication API

### Admin Authentication

Authenticate as administrator.

**Endpoint:** `POST /api/auth`

**Authentication:** Not required

#### Request Body
```json
{
    "password": "123"
}
```

#### Success Response
```json
{
    "success": true,
    "message": "Authentication successful"
}
```

#### Error Response
```json
{
    "success": false,
    "error": "Invalid password"
}
```

### Change Chatbot Password

Update the chatbot access password.

**Endpoint:** `POST /api/change_chatbot_password`

**Authentication:** Required (admin session)

#### Request Body
```json
{
    "new_password": "newpassword123"
}
```

#### Success Response
```json
{
    "success": true,
    "message": "Password updated successfully"
}
```

#### Error Response
```json
{
    "success": false,
    "error": "Failed to update password"
}
```

## Feedback API

### Submit Feedback

Submit user feedback.

**Endpoint:** `POST /api/feedback`

**Authentication:** Not required

#### Request Body
```json
{
    "feedback": "Great app! Very helpful for managing stress.",
    "rating": 5,
    "type": "general"
}
```

#### Success Response
```json
{
    "success": true,
    "message": "Feedback submitted successfully"
}
```

#### Error Response
```json
{
    "success": false,
    "error": "Failed to submit feedback"
}
```

## Error Handling

### Common Error Codes

#### 400 Bad Request
```json
{
    "success": false,
    "error": "Invalid request format",
    "message": "Required fields are missing or invalid"
}
```

#### 401 Unauthorized
```json
{
    "success": false,
    "error": "session_expired",
    "message": "Session expired. Please login again."
}
```

#### 404 Not Found
```json
{
    "success": false,
    "error": "Not found",
    "message": "The requested resource was not found"
}
```

#### 500 Internal Server Error
```json
{
    "success": false,
    "error": "Internal server error",
    "message": "An unexpected error occurred"
}
```

### Client-Side Error Handling

#### JavaScript Example
```javascript
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`/api${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            if (response.status === 401) {
                // Handle session expired
                handleSessionExpired();
                throw new Error('Session expired');
            }
            throw new Error(data.message || 'API request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

function handleSessionExpired() {
    // Clear local session
    localStorage.removeItem('chatbotSession');
    // Redirect to login or show login modal
    showLoginModal();
}
```

## Rate Limiting

### Current Implementation
- No explicit rate limiting is currently implemented
- Consider implementing rate limiting for production use

### Recommended Rate Limits
- Chat API: 30 requests per minute per user
- File Upload: 10 uploads per minute per user
- Admin API: 100 requests per minute per admin

## Data Models

### Subject Model
```json
{
    "subject_name": {
        "keywords": ["keyword1", "keyword2"],
        "units": {
            "unit_name": {
                "filename": "file.pdf",
                "keywords": ["unit_keyword1", "unit_keyword2"],
                "uploaded_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        },
        "created_at": "2024-01-01T12:00:00",
        "updated_at": "2024-01-01T12:00:00"
    }
}
```

### PYQ Model
```json
{
    "pyq_id": {
        "id": "unique_id",
        "name": "Document Name",
        "type": "PYQ|Timetable|Others",
        "filename": "file.pdf",
        "keywords": ["keyword1", "keyword2"],
        "uploaded_at": "2024-01-01T12:00:00",
        "updated_at": "2024-01-01T12:00:00"
    }
}
```

### Chat Message Model
```json
{
    "type": "text|subjects_list|units_list|notes_results|pyq_results|pyq_list",
    "message": "Response message",
    "data": { ... }, // Optional additional data
    "timestamp": "2024-01-01T12:00:00"
}
```

## Integration Examples

### Python Client Example
```python
import requests
import json

class SmartBuddyClient:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
        self.session_timestamp = None
    
    def login(self, password):
        """Login and get session timestamp"""
        response = requests.post(f"{self.base_url}/auth", 
                                json={"password": password})
        if response.json().get('success'):
            self.session_timestamp = datetime.datetime.now().isoformat()
            return True
        return False
    
    def send_message(self, message):
        """Send chat message"""
        headers = {}
        if self.session_timestamp:
            headers['X-Login-Timestamp'] = self.session_timestamp
        
        response = requests.post(f"{self.base_url}/chat",
                                json={"message": message},
                                headers=headers)
        return response.json()
    
    def get_subjects(self):
        """Get all subjects"""
        response = requests.get(f"{self.base_url}/subjects")
        return response.json()

# Usage
client = SmartBuddyClient()
if client.login("123"):
    response = client.send_message("I'm feeling anxious")
    print(response['message'])
```

### React Component Example
```jsx
import React, { useState, useEffect } from 'react';

function SmartBuddyChat() {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [sessionTimestamp, setSessionTimestamp] = useState(null);

    useEffect(() => {
        // Initialize session
        setSessionTimestamp(new Date().toISOString());
    }, []);

    const sendMessage = async () => {
        if (!inputValue.trim()) return;

        const userMessage = { text: inputValue, sender: 'user' };
        setMessages(prev => [...prev, userMessage]);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Login-Timestamp': sessionTimestamp
                },
                body: JSON.stringify({ message: inputValue })
            });

            const data = await response.json();
            
            if (response.ok) {
                const botMessage = { text: data.message, sender: 'bot' };
                setMessages(prev => [...prev, botMessage]);
            } else if (response.status === 401) {
                // Handle session expired
                alert('Session expired. Please login again.');
            }
        } catch (error) {
            console.error('Error sending message:', error);
        }

        setInputValue('');
    };

    return (
        <div className="chat-container">
            <div className="messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.sender}`}>
                        {msg.text}
                    </div>
                ))}
            </div>
            <div className="input-area">
                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Type your message..."
                />
                <button onClick={sendMessage}>Send</button>
            </div>
        </div>
    );
}
```

## Testing the API

### Using curl

#### Chat API Test
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-Login-Timestamp: 2024-01-01T12:00:00" \
  -d '{"message": "Hello, how are you?"}'
```

#### Subjects API Test
```bash
curl -X GET http://localhost:5000/api/subjects
```

#### Add Subject Test
```bash
curl -X POST http://localhost:5000/api/add_subject \
  -H "Content-Type: application/json" \
  -d '{"subject_name": "Test Subject", "keywords": "test, example"}'
```

### Using Postman

Import the following collection configuration:

```json
{
    "info": {
        "name": "SmartBuddy API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Chat",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    },
                    {
                        "key": "X-Login-Timestamp",
                        "value": "{{timestamp}}"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\"message\": \"{{message}}\"}"
                },
                "url": {
                    "raw": "{{base_url}}/chat",
                    "host": ["{{base_url}}"],
                    "path": ["chat"]
                }
            }
        }
    ],
    "variable": [
        {
            "key": "base_url",
            "value": "http://localhost:5000/api"
        },
        {
            "key": "timestamp",
            "value": "2024-01-01T12:00:00"
        },
        {
            "key": "message",
            "value": "Hello, how are you?"
        }
    ]
}
```

## WebSocket Support (Future)

### Planned WebSocket Endpoint
```
ws://localhost:5000/ws/chat
```

### WebSocket Message Format
```json
{
    "type": "message",
    "data": {
        "message": "User message",
        "session_id": "session_token"
    }
}
```

### WebSocket Response Format
```json
{
    "type": "response",
    "data": {
        "message": "Bot response",
        "typing": false
    }
}
```

---

This API reference provides comprehensive documentation for integrating with SmartBuddy. For additional support or questions, please refer to the developer guide or contact the development team.
