# SmartBuddy User Guide

## Welcome to SmartBuddy!

SmartBuddy is your intelligent companion designed to support both your mental wellness and academic journey. This guide will help you make the most of all the features available.

## Getting Started

### Accessing SmartBuddy

1. **Open your web browser** and navigate to `http://localhost:5000`
2. **Login** with the provided credentials (default: password `123`)
3. **Start chatting** immediately - no setup required!

### First Steps

1. **Try a greeting**: Say "Hello" or "Hi" to meet SmartBuddy
2. **Share how you feel**: Try "I'm feeling anxious about exams" to experience mental health support
3. **Ask for study materials**: Type "Show me math notes" to explore academic features

## Mental Health Support Features

### Emotion Recognition

SmartBuddy can understand and respond to a wide range of emotions:

#### Positive Emotions:
- **Happiness**: "I'm so happy today!" 
- **Excitement**: "I'm excited about the project"
- **Gratitude**: "I'm grateful for my friends"
- **Pride**: "I'm proud of my achievements"
- **Relief**: "I'm so relieved that's over"
- **Motivation**: "I feel motivated to study"
- **Calmness**: "I feel calm and peaceful"

#### Challenging Emotions:
- **Anxiety**: "I'm feeling anxious about the exam"
- **Stress**: "I'm stressed with all this work"
- **Sadness**: "I feel sad about my grades"
- **Confusion**: "I'm confused about this topic"
- **Loneliness**: "I feel lonely in this new place"
- **Anger**: "I'm angry about the situation"
- **Guilt**: "I feel guilty about procrastinating"

### How to Get Mental Health Support

#### Direct Expression:
```
You: "I'm feeling really stressed about finals"
SmartBuddy: "I can hear how overwhelmed you're feeling about finals. That stress is real and valid. Remember: you don't have to handle everything perfectly. Good enough is enough. 💪"
```

#### Indirect Expression:
```
You: "Just feeling heavy today"
SmartBuddy: "I'm really sorry you're feeling this sadness. It's okay to feel this way - sadness shows you have a deep capacity to care. You don't have to be strong all the time. 💜"
```

#### With Typos (SmartBuddy understands!):
```
You: "Feeling hapy and exicted today"
SmartBuddy: "That's wonderful to hear! 🎉 I'm so glad you're feeling good today. Keep embracing those positive moments - they're important fuel for the challenging days. Keep shining! ✨"
```

### What SmartBuddy Offers

- **Emotional Validation**: Your feelings are acknowledged and validated
- **Supportive Guidance**: Gentle suggestions for coping strategies
- **24/7 Availability**: Always here when you need to talk
- **Confidential Space**: Safe, private conversations
- **No Judgment**: Accepting and understanding responses

**Important**: SmartBuddy provides emotional support only and is not a substitute for professional mental health care.

## Academic Assistant Features

### Study Material Management

#### Finding Notes:
1. **Simple Search**: "Show me physics notes"
2. **Subject Search**: "What subjects are available?"
3. **Keyword Search**: "Find materials about calculus"
4. **Fuzzy Search**: "Look for mathamatics" (finds mathematics)

#### Accessing Materials:
```
You: "I need notes for computer science"
SmartBuddy: [Displays available subjects and units]
You: [Click on desired unit]
SmartBuddy: [Downloads the PDF file]
```

### Previous Year Questions (PYQ)

#### Finding PYQs:
- "Show me previous year questions"
- "I need old question papers"
- "Find PYQs for mathematics"
- "Exam papers for engineering"

#### PYQ Categories:
- **Previous Year Questions**: Actual exam papers
- **Timetables**: Exam schedules
- **Others**: Additional academic resources

### Smart Search Features

#### Fuzzy Matching:
- "calclus" → "calculus"
- "phyics" → "physics"
- "prgramming" → "programming"

#### Synonym Expansion:
- "programming" finds "coding", "coding", "oop"
- "exam" finds "test", "examination", "quiz"
- "notes" finds "material", "study material", "unit"

## Chat Interface Guide

### Main Features

#### Message Input:
- **Type your message** in the input field at the bottom
- **Press Enter** or click **Send** to submit
- **Multi-line messages**: Use Shift+Enter for new lines

#### Chat History:
- **Auto-saved**: All conversations are automatically saved
- **Sidebar Access**: Click the menu icon to see chat history
- **New Chat**: Start fresh conversations anytime

#### Real-time Features:
- **Typing Indicators**: See when SmartBuddy is "thinking"
- **Smooth Animations**: Messages appear with gentle animations
- **Auto-scroll**: Chat automatically scrolls to latest messages

### Theme Customization

#### Dark Mode (Default):
- Easy on the eyes for extended use
- Professional appearance
- Reduced eye strain

#### Light Mode:
- Bright, clean interface
- Better for daytime use
- High contrast for accessibility

**How to Switch**: Look for the theme toggle button in the header

## Conversation Tips

### Best Practices

#### Be Specific:
- Instead of: "I need help"
- Try: "I'm feeling anxious about my math exam tomorrow"

#### Use Natural Language:
- "I'm worried about my grades"
- "Can you help me find physics notes?"
- "I'm feeling overwhelmed with assignments"

#### Don't Worry About:
- **Spelling mistakes**: SmartBuddy understands typos
- **Grammar**: Natural, conversational language works best
- **Perfect phrasing**: Express yourself however feels natural

### Example Conversations

#### Mental Health Support:
```
You: "I'm really worried about the upcoming exams"
SmartBuddy: "I understand you're feeling worried about the upcoming exams. That anxiety sounds overwhelming. Your body is trying to protect you, even though it feels uncomfortable. Try grounding yourself by noticing 5 things you can see and 4 you can touch. 🌿"
```

#### Academic Help:
```
You: "I need study materials for data structures"
SmartBuddy: [Displays available subjects]
You: "Click on 'Computer Science'"
SmartBuddy: [Shows available units like 'Data Structures', 'Algorithms', etc.]
```

#### Mixed Conversation:
```
You: "I'm stressed about studies and feeling lonely"
SmartBuddy: "I hear you're stressed about your studies and feeling lonely. That's such a painful combination, especially when you're working hard but still feel isolated. Your feelings are valid and you deserve connection. Be gentle with yourself and consider one small step toward connection - you deserve it. 💚"
```

## Admin Panel Guide (For Administrators)

### Accessing Admin Panel
1. Navigate to `http://localhost:5000/admin`
2. Login with admin credentials
3. Access comprehensive management features

### Content Management

#### Subject Management:
- **Add Subjects**: Create new academic subjects
- **Edit Subjects**: Modify subject names and keywords
- **Delete Subjects**: Remove subjects with confirmation
- **Keyword Management**: Add search keywords for better discovery

#### Unit Management:
- **Upload PDFs**: Drag-and-drop file uploads
- **Edit Units**: Modify unit names and keywords
- **Delete Units**: Remove individual units
- **Download Files**: Access uploaded materials

#### PYQ Management:
- **Upload Documents**: Add new PYQs and academic materials
- **Categorize**: Organize by type (PYQ, Timetable, Others)
- **Edit Metadata**: Modify names, keywords, and categories
- **Download Access**: Quick access to all uploaded files

### Security Features

#### Password Management:
- **Change Password**: Update admin password regularly
- **Session Management**: Control active sessions
- **Access Control**: Secure admin features

#### User Management:
- **Chatbot Password**: Separate password for chatbot access
- **Session Validation**: Automatic session timeout
- **Security Headers**: CSRF and XSS protection

## Troubleshooting

### Common Issues

#### Login Problems:
- **Forgot Password**: Contact administrator to reset
- **Session Expired**: Simply login again
- **Browser Issues**: Clear cache and cookies

#### File Upload Issues:
- **File Size**: Check if file is too large
- **File Type**: Only PDF files are supported
- **Network**: Check internet connection

#### Chat Issues:
- **No Response**: Check if message was sent (appears in chat)
- **Slow Response**: Network connectivity issues
- **Errors**: Refresh page and try again

### Performance Tips

#### For Best Experience:
- **Use Modern Browser**: Chrome, Firefox, Safari, or Edge
- **Stable Internet**: Ensure good connectivity
- **Regular Updates**: Keep browser updated
- **Sufficient Memory**: Close unnecessary tabs

#### Mobile Users:
- **Portrait Mode**: Best for mobile chat experience
- **Stable Connection**: WiFi preferred over mobile data
- **Touch Gestures**: Swipe for sidebar, tap for interactions

## Privacy and Security

### Your Privacy Matters

#### Data Protection:
- **Local Storage**: All data stored on your server
- **No Cloud**: No data sent to external services
- **Confidential Chats**: Conversations are private
- **Secure Authentication**: Password-protected access

#### Best Practices:
- **Strong Passwords**: Use unique, strong passwords
- **Regular Updates**: Change passwords periodically
- **Secure Network**: Use secure internet connections
- **Log Out**: Sign out when done on shared devices

## Getting Help

### Support Resources

#### Immediate Help:
- **Chat with SmartBuddy**: Always available for emotional support
- **Admin Contact**: For technical issues, contact your administrator
- **User Guide**: Refer to this guide for common questions

#### Mental Health Resources:
**Important**: SmartBuddy is not a substitute for professional mental health care. If you're experiencing severe distress:

- **Emergency Services**: Call local emergency numbers
- **Crisis Hotlines**: Contact mental health crisis lines
- **Professional Help**: Seek help from qualified mental health professionals
- **School Resources**: Use school counseling services

### Feedback and Improvement

#### Share Your Experience:
- **What Works Well**: Tell us features you find helpful
- **Improvement Suggestions**: Let us know how we can do better
- **Bug Reports**: Report any technical issues you encounter
- **Feature Requests**: Suggest new features you'd like to see

#### How to Provide Feedback:
- **Through Chat**: Simply tell SmartBuddy your feedback
- **Admin Contact**: Reach out to your system administrator
- **User Community**: Share experiences with other users

---

**Thank you for choosing SmartBuddy!** We're here to support your mental wellness and academic success. Remember, it's okay to not be okay, and we're always here to listen. 🌟

*This guide is updated regularly. Check for new features and improvements!*
