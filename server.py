from flask import Flask, request, jsonify, send_from_directory, send_file
from pathlib import Path
import json
import hashlib
import datetime
import re
import difflib
import os
from typing import Dict, List, Any, Optional
from werkzeug.utils import secure_filename
from mental_health_nlp import MentalHealthNLP

# Base directory - ensures paths work on PythonAnywhere
BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path='')

# Configuration
UPLOAD_FOLDER = BASE_DIR / 'notes'
DATA_DIR = BASE_DIR / 'data'
CHATS_DIR = BASE_DIR / 'chats'
SALT = "smartbuddy_salt_2024"

# Ensure directories
for directory in [UPLOAD_FOLDER, DATA_DIR, CHATS_DIR]:
    directory.mkdir(exist_ok=True)

# ============= DATA MANAGER =============
class DataManager:
    def __init__(self):
        self.ensure_files()

    def ensure_files(self):
        """Create default JSON files - EMPTY, TRULY DYNAMIC"""
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
        return hashlib.sha256((password + SALT).encode()).hexdigest()

    def save_json(self, filepath: Path, data: Any):
        temp_path = filepath.with_suffix('.tmp')
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            temp_path.replace(filepath)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e

    def load_json(self, filepath: Path) -> Any:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} if 'subjects' in str(filepath) or 'info' in str(filepath) else []

# ============= NLP PROCESSOR =============
class NLPProcessor:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.synonyms = data_manager.load_json(DATA_DIR / 'synonyms.json')

    def preprocess_text(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def expand_synonyms(self, text: str) -> List[str]:
        words = text.split()
        expanded_terms = set(words)
        for word in words:
            for key, synonyms_list in self.synonyms.items():
                if word in synonyms_list or word == key:
                    expanded_terms.add(key)
                    expanded_terms.update(synonyms_list)
        return list(expanded_terms)

    def fuzzy_match(self, query: str, target: str, threshold: float = 0.6) -> float:
        query_clean = self.preprocess_text(query)
        target_clean = self.preprocess_text(target)
        ratio = difflib.SequenceMatcher(None, query_clean, target_clean).ratio()
        return ratio * 100

    def detect_intent(self, text: str) -> str:
        text_lower = text.lower().strip()
        expanded_terms = self.expand_synonyms(text_lower)
        all_terms = set([text_lower] + expanded_terms)

        # Check for greetings - enhanced detection (FIRST to catch simple greetings)
        greeting_words = ['hi', 'hello', 'hey', 'hola', 'good morning', 'good evening', 'good afternoon', 'whats up', 'sup']
        if any(greeting in text_lower for greeting in greeting_words) and len(text_lower.split()) <= 4:
            return 'help_greeting'
        
        # ACADEMIC INTENT DETECTION (Check FIRST to avoid mental health override)
        academic_keywords = [
            'note', 'notes', 'material', 'pdf', 'unit', 'chapter', 'subject', 'study', 'studying',
            'pyq', 'previous year', 'past paper', 'old paper', 'question paper', 'exam paper',
            'computer science', 'mathematics', 'physics', 'chemistry', 'programming', 'coding',
            'algorithm', 'data structure', 'database', 'java', 'python', 'c++', 'javascript',
            'faculty', 'teacher', 'professor', 'timetable', 'schedule', 'class', 'lecture'
        ]
        
        # Check for academic content with high priority
        text_words = text_lower.split()
        academic_score = 0
        
        for word in text_words:
            # Direct academic keyword match
            if any(keyword in word or word in keyword for keyword in academic_keywords):
                academic_score += 2
        
        # Check academic phrases
        academic_phrases = [
            'i need notes', 'show me notes', 'get notes', 'study material', 'previous year questions',
            'past papers', 'question papers', 'exam papers', 'computer science notes', 'math notes',
            'physics notes', 'programming notes', 'coding notes', 'algorithm notes', 'data structure notes'
        ]
        
        for phrase in academic_phrases:
            if phrase in text_lower:
                academic_score += 3
        
        # If academic content detected, prioritize it
        if academic_score >= 2:
            # Check specifically for PYQ
            if any(word in text_lower for word in ['pyq', 'previous year', 'past paper', 'old paper', 'question paper']):
                return 'pyq_request'
            # Otherwise it's notes request
            elif any(word in text_lower for word in ['note', 'notes', 'material', 'pdf', 'unit', 'chapter', 'subject']):
                return 'notes_request'
        
        # Check for information requests - ENHANCED detection
        info_keywords = [
            'what is', 'what are', 'how to', 'tell me about', 'information', 'info', 'details',
            'explain', 'describe', 'definition', 'meaning', 'help me understand', 'can you explain',
            'teacher', 'teachers', 'faculty', 'staff', 'professor', 'instructor', 'who is', 'about'
        ]
        
        # Check for direct info requests
        for phrase in info_keywords:
            if phrase in text_lower:
                return 'info_request'
        
        # Check for teacher/faculty specific queries
        teacher_keywords = ['teacher', 'teachers', 'faculty', 'staff', 'professor', 'instructor']
        if any(keyword in text_lower for keyword in teacher_keywords):
            return 'info_request'
        
        # NOW check for mental health - ENHANCED detection for better emotional support
        # Check for emotional patterns
        emotional_patterns = ['i feel', 'feeling', 'i am', 'im feeling', 'makes me feel', 'i am so', 'im so', 'i am really', 'im really']
        has_emotional_pattern = any(pattern in text_lower for pattern in emotional_patterns)
        
        # Expanded emotional keywords for better detection
        emotional_keywords = [
            'sad', 'depressed', 'depression', 'anxious', 'anxiety', 'worried', 'worry', 'scared', 'afraid', 'panic',
            'overwhelmed', 'stress', 'stressed', 'lonely', 'angry', 'mad', 'frustrated', 'hopeless', 'helpless',
            'crying', 'tears', 'empty', 'numb', 'happy', 'excited', 'good', 'great', 'wonderful', 'amazing',
            'tired', 'exhausted', 'drained', 'confused', 'lost', 'disappointed', 'proud', 'relieved', 'grateful',
            'motivated', 'calm', 'peaceful', 'guilty', 'ashamed', 'embarrassed', 'hurt', 'pain', 'broken',
            'mental health', 'therapy', 'counseling', 'upset', 'miserable', 'devastated', 'crushed'
        ]
        
        # Check for emotional keywords
        has_emotional_keywords = any(keyword in text_lower for keyword in emotional_keywords)
        
        # Prioritize mental health for emotional support
        if has_emotional_pattern or has_emotional_keywords:
            return 'mental_health'
            
        return 'info_or_unknown'

# ============= NOTES MANAGER =============
class NotesManager:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def get_subjects(self) -> Dict[str, Any]:
        return self.data_manager.load_json(DATA_DIR / 'subjects.json')

    def add_subject(self, subject_name: str, keywords: str = '') -> bool:
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

    def delete_subject(self, subject_name: str) -> bool:
        subjects = self.get_subjects()
        if subject_name in subjects:
            subject_dir = UPLOAD_FOLDER / subject_name
            if subject_dir.exists():
                import shutil
                shutil.rmtree(subject_dir)
            del subjects[subject_name]
            self.data_manager.save_json(DATA_DIR / 'subjects.json', subjects)
            return True
        return False

    def add_unit(self, subject_name: str, unit_name: str, file, keywords: str = '') -> bool:
        subjects = self.get_subjects()
        if subject_name not in subjects:
            return False

        subject_dir = UPLOAD_FOLDER / subject_name
        subject_dir.mkdir(exist_ok=True)

        filename = secure_filename(f"{unit_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        filepath = subject_dir / filename

        try:
            file.save(str(filepath))
            subjects[subject_name]['units'][unit_name] = {
                'filename': filename,
                'keywords': [k.strip().lower() for k in keywords.split(',') if k.strip()],
                'uploaded_at': datetime.datetime.now().isoformat()
            }
            self.data_manager.save_json(DATA_DIR / 'subjects.json', subjects)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def delete_unit(self, subject_name: str, unit_name: str) -> bool:
        subjects = self.get_subjects()
        if subject_name in subjects and unit_name in subjects[subject_name]['units']:
            filename = subjects[subject_name]['units'][unit_name].get('filename', '')
            filepath = UPLOAD_FOLDER / subject_name / filename
            if filepath.exists():
                filepath.unlink()
            del subjects[subject_name]['units'][unit_name]
            self.data_manager.save_json(DATA_DIR / 'subjects.json', subjects)
            return True
        return False

    def search_units(self, query: str, nlp_processor) -> List[Dict]:
        """Search all subjects and units for matching content - case insensitive"""
        subjects = self.get_subjects()
        results = []
        query_clean = nlp_processor.preprocess_text(query)

        for subject_name, subject_data in subjects.items():
            subject_clean = nlp_processor.preprocess_text(subject_name)
            subject_keywords = subject_data.get('keywords', [])
            subject_score = 0

            # Case-insensitive subject name matching
            if query_clean in subject_clean or subject_clean in query_clean:
                subject_score += 40

            # Case-insensitive keyword matching for subjects
            for kw in subject_keywords:
                kw_clean = nlp_processor.preprocess_text(kw)  # Ensure keyword is also cleaned
                if query_clean in kw_clean or kw_clean in query_clean:
                    subject_score += 30
                elif nlp_processor.fuzzy_match(query_clean, kw_clean) > 70:
                    subject_score += 15

            for unit_name, unit_data in subject_data.get('units', {}).items():
                unit_score = subject_score
                unit_clean = nlp_processor.preprocess_text(unit_name)
                unit_keywords = unit_data.get('keywords', [])

                # Case-insensitive unit name matching
                if query_clean in unit_clean or unit_clean in query_clean:
                    unit_score += 35

                # Case-insensitive keyword matching for units
                for kw in unit_keywords:
                    kw_clean = nlp_processor.preprocess_text(kw)  # Ensure keyword is also cleaned
                    if query_clean in kw_clean or kw_clean in query_clean:
                        unit_score += 30
                    elif nlp_processor.fuzzy_match(query_clean, kw_clean) > 70:
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

    def edit_subject(self, old_name: str, new_name: str, keywords: str) -> bool:
        """Edit subject name and keywords"""
        subjects = self.get_subjects()
        if old_name in subjects:
            # Handle renaming (create new entry with new name)
            if old_name != new_name and new_name not in subjects:
                subjects[new_name] = subjects[old_name]
                subjects[new_name]['keywords'] = [k.strip().lower() for k in keywords.split(',') if k.strip()]
                subjects[new_name]['updated_at'] = datetime.datetime.now().isoformat()
                
                # Rename the folder if it exists
                old_folder = UPLOAD_FOLDER / old_name
                new_folder = UPLOAD_FOLDER / new_name
                if old_folder.exists():
                    import shutil
                    shutil.move(str(old_folder), str(new_folder))
                
                del subjects[old_name]
            else:
                # Just update keywords
                subjects[old_name]['keywords'] = [k.strip().lower() for k in keywords.split(',') if k.strip()]
                subjects[old_name]['updated_at'] = datetime.datetime.now().isoformat()
            
            self.data_manager.save_json(DATA_DIR / 'subjects.json', subjects)
            return True
        return False

    def edit_unit(self, subject_name: str, old_unit_name: str, new_unit_name: str, keywords: str) -> bool:
        """Edit unit name and keywords"""
        subjects = self.get_subjects()
        if subject_name in subjects and old_unit_name in subjects[subject_name]['units']:
            unit_data = subjects[subject_name]['units'][old_unit_name]
            
            # Handle renaming
            if old_unit_name != new_unit_name:
                subjects[subject_name]['units'][new_unit_name] = unit_data
                subjects[subject_name]['units'][new_unit_name]['keywords'] = [k.strip().lower() for k in keywords.split(',') if k.strip()]
                subjects[subject_name]['units'][new_unit_name]['updated_at'] = datetime.datetime.now().isoformat()
                del subjects[subject_name]['units'][old_unit_name]
            else:
                # Just update keywords
                subjects[subject_name]['units'][old_unit_name]['keywords'] = [k.strip().lower() for k in keywords.split(',') if k.strip()]
                subjects[subject_name]['units'][old_unit_name]['updated_at'] = datetime.datetime.now().isoformat()
            
            self.data_manager.save_json(DATA_DIR / 'subjects.json', subjects)
            return True
        return False

# ============= PYQ MANAGER =============
class PYQManager:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.pyq_dir = BASE_DIR / 'pyq_files'
        self.pyq_dir.mkdir(exist_ok=True)

    def get_pyqs(self) -> Dict[str, Any]:
        return self.data_manager.load_json(DATA_DIR / 'pyq.json')

    def add_pyq(self, name: str, keywords: str, file_type: str, file) -> Dict[str, Any]:
        pyqs = self.get_pyqs()
        
        # Generate unique ID
        pyq_id = str(len(pyqs) + 1)
        
        # Generate secure filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"{name}_{timestamp}.pdf")
        filepath = self.pyq_dir / filename

        try:
            # Save file
            file.save(str(filepath))
            
            # Save metadata
            pyqs[pyq_id] = {
                'id': pyq_id,
                'name': name,
                'keywords': [k.strip().lower() for k in keywords.split(',') if k.strip()],
                'type': file_type,
                'filename': filename,
                'uploaded_at': datetime.datetime.now().isoformat()
            }
            
            self.data_manager.save_json(DATA_DIR / 'pyq.json', pyqs)
            return {'success': True, 'id': pyq_id}
            
        except Exception as e:
            print(f"Error saving PYQ: {e}")
            return {'success': False, 'error': str(e)}

    def edit_pyq(self, pyq_id: str, name: str, keywords: str, file_type: str) -> Dict[str, Any]:
        pyqs = self.get_pyqs()
        
        if pyq_id not in pyqs:
            return {'success': False, 'error': 'PYQ not found'}
        
        try:
            pyqs[pyq_id]['name'] = name
            pyqs[pyq_id]['keywords'] = [k.strip().lower() for k in keywords.split(',') if k.strip()]
            pyqs[pyq_id]['type'] = file_type
            pyqs[pyq_id]['updated_at'] = datetime.datetime.now().isoformat()
            
            self.data_manager.save_json(DATA_DIR / 'pyq.json', pyqs)
            return {'success': True}
            
        except Exception as e:
            print(f"Error editing PYQ: {e}")
            return {'success': False, 'error': str(e)}

    def delete_pyq(self, pyq_id: str) -> Dict[str, Any]:
        pyqs = self.get_pyqs()
        
        if pyq_id not in pyqs:
            return {'success': False, 'error': 'PYQ not found'}
        
        try:
            # Delete file
            filename = pyqs[pyq_id].get('filename', '')
            if filename:
                filepath = self.pyq_dir / filename
                if filepath.exists():
                    filepath.unlink()
            
            # Delete metadata
            del pyqs[pyq_id]
            self.data_manager.save_json(DATA_DIR / 'pyq.json', pyqs)
            return {'success': True}
            
        except Exception as e:
            print(f"Error deleting PYQ: {e}")
            return {'success': False, 'error': str(e)}

    def search_pyqs(self, query: str, nlp_processor) -> List[Dict]:
        """Search all PYQs for matching content - case insensitive"""
        pyqs = self.get_pyqs()
        results = []
        query_clean = nlp_processor.preprocess_text(query)

        for pyq_id, pyq_data in pyqs.items():
            score = 0
            name_clean = nlp_processor.preprocess_text(pyq_data['name'])
            keywords = pyq_data.get('keywords', [])
            file_type = pyq_data.get('type', '').lower()

            # Case-insensitive name match
            if query_clean in name_clean or name_clean in query_clean:
                score += 40

            # Case-insensitive keywords match
            for kw in keywords:
                kw_clean = nlp_processor.preprocess_text(kw)  # Ensure keyword is also cleaned
                if query_clean in kw_clean or kw_clean in query_clean:
                    score += 30
                elif nlp_processor.fuzzy_match(query_clean, kw_clean) > 70:
                    score += 15

            # Case-insensitive type match
            type_clean = nlp_processor.preprocess_text(file_type)
            if query_clean in type_clean or type_clean in query_clean:
                score += 20

            if score > 0:
                results.append({
                    'id': pyq_id,
                    'data': pyq_data,
                    'score': score
                })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results

# ============= CHATBOT =============
class ChatBot:
    def __init__(self, data_manager: DataManager, nlp_processor: NLPProcessor, notes_manager: NotesManager, pyq_manager: PYQManager):
        self.data_manager = data_manager
        self.nlp_processor = nlp_processor
        self.notes_manager = notes_manager
        self.pyq_manager = pyq_manager

    def process_query(self, query: str, login_timestamp: str = None) -> Dict[str, Any]:
        # Validate Session
        if not self.validate_session(login_timestamp):
            return {'type': 'error', 'error': 'session_expired', 'message': 'Session expired. Please login again.'}

        # TEMPORARY DEBUG: Force info handler for specific test queries
        test_queries = ['fee structure', 'fees', 'fee', 'structure', 'teacher', 'teachers']
        if any(test_query in query.lower() for test_query in test_queries):
            print(f"DEBUG: FORCING info handler for test query: '{query}'")
            return self._handle_info_request(query)

        # IMMEDIATE EMOTIONAL CHECK - Priority over everything else
        if self._might_be_emotional(query):
            print("DEBUG: IMMEDIATE emotional detection - routing to mental health")
            return self._handle_mental_health(query)

        intent = self.nlp_processor.detect_intent(query)
        
        # Debug logging (can be removed in production)
        print(f"DEBUG: Query='{query}', Intent='{intent}'")
        
        if intent == 'notes_request':
            return self._handle_notes_request(query)
        elif intent == 'pyq_request':
            return self._handle_pyq_request(query)
        elif intent == 'info_request':
            return self._handle_info_request(query)
        elif intent == 'help_greeting':
            return self._handle_greeting()
        elif intent == 'mental_health':
            return self._handle_mental_health(query)
        else:
            return self._handle_info_or_unknown(query)

    def _might_be_emotional(self, query: str) -> bool:
        """Check if query might contain emotional content - AGGRESSIVE DETECTION"""
        emotional_indicators = [
            # Direct emotion words
            'feel', 'feeling', 'sad', 'happy', 'angry', 'worried', 'anxious', 'stressed', 
            'depressed', 'excited', 'tired', 'overwhelmed', 'confused', 'lonely', 'proud',
            'disappointed', 'relieved', 'grateful', 'motivated', 'calm', 'guilty', 'hurt',
            # Personal state indicators
            'i am', 'im', 'i feel', 'makes me', 'emotion', 'mood', 'i feel so', 'i am so',
            # Extended emotional vocabulary
            'cry', 'crying', 'tears', 'upset', 'frustrated', 'annoyed', 'mad', 'furious',
            'scared', 'afraid', 'panic', 'terrified', 'nervous', 'uneasy', 'restless',
            'exhausted', 'drained', 'burned out', 'fatigue', 'sleepy', 'drowsy',
            'hopeless', 'helpless', 'worthless', 'empty', 'numb', 'broken', 'crushed',
            'joy', 'joyful', 'cheerful', 'delighted', 'glad', 'pleased', 'thrilled',
            'peaceful', 'relaxed', 'serene', 'content', 'satisfied', 'at ease'
        ]
        query_lower = query.lower()
        
        # Check for any emotional indicators
        has_emotional = any(indicator in query_lower for indicator in emotional_indicators)
        
        # Additional check: if query is short and personal, likely emotional
        personal_patterns = ['i am', 'im', 'i feel', 'i feel so', 'i am so', 'i am really', 'im really']
        is_personal = any(pattern in query_lower for pattern in personal_patterns)
        
        # If it's personal OR has emotional words, treat as emotional
        result = has_emotional or is_personal
        
        print(f"DEBUG: Emotional check - has_emotional={has_emotional}, is_personal={is_personal}, result={result}")
        return result

    def validate_session(self, login_timestamp: str) -> bool:
        if not login_timestamp:
            return False
            
        auth_db = self.data_manager.load_json(DATA_DIR / 'chatbot_auth.json')
        
        # If legacy or missing, block access
        if not isinstance(auth_db, dict) or 'last_changed' not in auth_db:
             return False # Force reset/re-init
             
        last_changed = auth_db['last_changed']
        
        # If login was BEFORE the last password change, it's invalid
        return login_timestamp >= last_changed

    def _handle_notes_request(self, query: str) -> Dict[str, Any]:
        results = self.notes_manager.search_units(query, self.nlp_processor)
        subjects = self.notes_manager.get_subjects()

        if results:
            return {
                'type': 'notes_results',
                'message': ' I found these notes:',
                'results': results
            }

        if subjects:
            return {
                'type': 'subjects_list',
                'message': ' Available subjects:',
                'subjects': {name: len(data.get('units', {})) for name, data in subjects.items()}
            }

        return {
            'type': 'text',
            'message': ' No study materials available yet. Admin will add notes soon!'
        }

    def _handle_pyq_request(self, query: str) -> Dict[str, Any]:
        """Handle PYQ (Previous Year Questions) requests"""
        results = self.pyq_manager.search_pyqs(query, self.nlp_processor)
        pyqs = self.pyq_manager.get_pyqs()

        if results:
            return {
                'type': 'pyq_results',
                'message': ' I found these PYQ materials:',
                'results': results
            }

        if pyqs:
            # Group by type
            by_type = {}
            for pyq_data in pyqs.values():
                pyq_type = pyq_data.get('type', 'Others')
                by_type[pyq_type] = by_type.get(pyq_type, 0) + 1
            
            return {
                'type': 'pyq_list',
                'message': ' Available PYQ materials:',
                'types': by_type
            }

        return {
            'type': 'text',
            'message': ' No PYQ materials available yet. Admin will add them soon!'
        }

    def _handle_greeting(self) -> Dict[str, Any]:
        # Use NLP to generate warm, positive greeting
        message = mental_health_nlp.generate_greeting()
        return {'type': 'text', 'message': message}

    def _handle_mental_health(self, query: str) -> Dict[str, Any]:
        # Use NLP to process mental health query and generate empathetic response
        print(f"DEBUG: Mental health handler called with query: '{query}'")
        response = mental_health_nlp.process_query(query)
        print(f"DEBUG: Mental health response: '{response.get('message', 'No message')[:100]}...'")
        return response

    def _handle_info_request(self, query: str) -> Dict[str, Any]:
        """Handle information requests with priority to info.json - NEW STRUCTURE"""
        print(f"DEBUG: Info request for query: '{query}'")
        
        info_data = self.data_manager.load_json(DATA_DIR / 'info.json')
        if not info_data:
            print("DEBUG: No info data found")
            return self._handle_info_or_unknown(query)
        
        print(f"DEBUG: Info data structure:")
        for category, data in info_data.items():
            print(f"  Category: '{category}'")
            print(f"    Data keys: {list(data.keys())}")
            if 'items' in data:
                print(f"    Items count: {len(data['items'])}")
                for i, item in enumerate(data['items']):
                    print(f"      Item {i+1}: keywords={item.get('keywords', [])}, content_length={len(item.get('content', ''))}")
            else:
                print(f"    No items found in this category")

        query_clean = self.nlp_processor.preprocess_text(query)
        query_words = query_clean.split()
        print(f"DEBUG: Processed query: '{query_clean}', words: {query_words}")
        found_items = []
        
        # Search through all sections and their items
        for category, category_data in info_data.items():
            # NO CATEGORY MATCHING - Only exact keyword matching in items
            score = 0
            
            # Check items within the category
            items = category_data.get('items', [])
            if items:
                for item in items:
                    item_score = score
                    item_title = item.get('title', '')
                    item_content = item.get('content', '')
                    item_keywords = item.get('keywords', [])
                    
                    # EXACT KEYWORD MATCHING ONLY - No fuzzy matching
                    print(f"DEBUG: Checking item with keywords: {item_keywords}")
                    exact_match_found = False
                    
                    # Check for EXACT keyword match (case-insensitive)
                    query_clean_lower = query_clean.lower()
                    for kw in item_keywords:
                        kw_clean = self.nlp_processor.preprocess_text(kw).lower()
                        print(f"DEBUG: Processing keyword: '{kw}' -> '{kw_clean}'")
                        
                        # EXACT MATCH ONLY: Query must exactly match a keyword
                        if query_clean_lower == kw_clean:
                            item_score += 100  # High score for exact match
                            exact_match_found = True
                            print(f"DEBUG: EXACT keyword match found! '{query_clean_lower}' == '{kw_clean}' +100")
                            break  # Stop checking other keywords for this item
                    
                    # Only add item if there was an exact keyword match
                    if exact_match_found:
                        print(f"DEBUG: Found matching item! Score: {item_score}, Category: {category}")
                        found_items.append({
                            'category': category,
                            'title': item_title,
                            'content': item_content,
                            'score': item_score
                        })
                    else:
                        print(f"DEBUG: No exact keyword match for this item - skipping")
            else:
                # No items, check if category itself matches
                if score > 0:
                    found_items.append({
                        'category': category,
                        'title': category,
                        'content': f"Information about {category}",
                        'score': score
                    })

        # Sort by score and return ALL matching results
        print(f"DEBUG: Total items found: {len(found_items)}")
        if found_items:
            found_items.sort(key=lambda x: x['score'], reverse=True)
            print(f"DEBUG: Sorted items by score:")
            for i, item in enumerate(found_items):
                print(f"  {i+1}. {item['category']} (score: {item['score']})")
            
            # Filter out items with empty or generic content
            valid_items = [item for item in found_items if item['content'] and item['content'] != f"Information about {item['category']}"]
            
            if valid_items:
                # Build response with ALL matching items - CONTENT ONLY as requested
                response_parts = []
                
                if len(valid_items) == 1:
                    # Single item - show content directly
                    response_parts.append(valid_items[0]['content'])
                else:
                    # Multiple items - show all content with clear separation
                    response_parts.append(f"Found {len(valid_items)} items matching your query:")
                    response_parts.append("\n")
                    
                    for i, item in enumerate(valid_items, 1):
                        response_parts.append(f"{i}. {item['content']}")
                        if i < len(valid_items):
                            response_parts.append("\n\n---\n\n")
                
                return {
                    'type': 'text', 
                    'message': ''.join(response_parts)
                }
            else:
                # Only found empty/generic items
                return {
                    'type': 'text', 
                    'message': f"📚 **Information Found**\n\nI found information matching your query, but the detailed content is currently being updated by the admin. Please check back later for more specific information."
                }

        # Rest of the function remains the same
        """Handle information requests with priority to info.json - RETURNS ALL MATCHES"""
        info_data = self.data_manager.load_json(DATA_DIR / 'info.json')
        if not info_data:
             return self._handle_info_or_unknown(query)

        query_clean = self.nlp_processor.preprocess_text(query)
        found_items = []
        
        # 1. Search Items inside Sections
        for category, category_data in info_data.items():
            if 'items' in category_data and isinstance(category_data['items'], list):
                for item in category_data['items']:
                    score = 0
                    item_title = item.get('title', '')
                    item_content = item.get('content', '')
                    item_keywords = item.get('keywords', [])
                    
                    # Match Keywords (High Priority)
                    for kw in item_keywords:
                        kw_clean = self.nlp_processor.preprocess_text(kw)
                        if query_clean == kw_clean: # Exact match
                            score += 100
                        elif query_clean in kw_clean or kw_clean in query_clean:
                            score += 50
                        elif self.nlp_processor.fuzzy_match(query_clean, kw_clean) > 85:
                            score += 30
                            
                    # Match Title
                    title_clean = self.nlp_processor.preprocess_text(item_title)
                    if query_clean in title_clean or title_clean in query_clean:
                        score += 60
                    elif self.nlp_processor.fuzzy_match(query_clean, title_clean) > 85:
                        score += 40

                    # Match Content
                    content_clean = self.nlp_processor.preprocess_text(item_content)
                    if query_clean in content_clean:
                         score += 20

                    if score >= 50: # Threshold for relevance
                        found_items.append({
                            'category': category,
                            'title': item_title,
                            'content': item_content,
                            'score': score
                        })

        # 2. Search Sections (if no specific items found or as supplement)
        # (Optional: we can include section matches if query matches section name)
        for category, category_data in info_data.items():
             cat_clean = self.nlp_processor.preprocess_text(category)
             if query_clean in cat_clean or cat_clean in query_clean or self.nlp_processor.fuzzy_match(query_clean, cat_clean) > 85:
                 # Check if we already have items from this category? Maybe just add the category generic info if it exists
                 pass 

        # Sort by score
        found_items.sort(key=lambda x: x['score'], reverse=True)

        if found_items:
            # Format found items - CONTENT ONLY
            # Join multiple matches with a separator, but no headers/titles as requested
            message_parts = []
            for item in found_items:
                message_parts.append(item['content'])
            
            final_message = "\n\n---\n\n".join(message_parts)
            return {'type': 'text', 'message': final_message.strip()}

        # 3. Knowledge Base Fallback
        knowledge_base = self.data_manager.load_json(DATA_DIR / 'knowledge_base.json')
        for qa in knowledge_base:
            if self.nlp_processor.fuzzy_match(query, qa.get('question', '')) > 75:
                return {'type': 'text', 'message': qa.get('answer', '')}

        # 4. Unanswered / Fallback
        unanswered = self.data_manager.load_json(DATA_DIR / 'unanswered_queries.json')
        unanswered.append({'query': query, 'asked_at': datetime.datetime.now().isoformat()})
        self.data_manager.save_json(DATA_DIR / 'unanswered_queries.json', unanswered)

        return {
            'type': 'text',
            'message': "I'm sorry, I don't have specific information about that topic. The admin will add relevant information soon. Is there anything else I can help you with today?"
        }

    def _handle_info_or_unknown(self, query: str) -> Dict[str, Any]:
        """Fallback handler for unknown queries - ONLY gives polite responses"""
        
        # Save as unanswered for admin review
        unanswered = self.data_manager.load_json(DATA_DIR / 'unanswered_queries.json')
        unanswered.append({'query': query, 'asked_at': datetime.datetime.now().isoformat()})
        self.data_manager.save_json(DATA_DIR / 'unanswered_queries.json', unanswered)

        # Return a polite, generic fallback - NO unrelated suggestions
        return {
            'type': 'text',
            'message': "I'm sorry, I don't have information about that specific topic. The admin will add relevant content to help with such questions in the future."
        }

# Initialize
data_manager = DataManager()
nlp_processor = NLPProcessor(data_manager)
notes_manager = NotesManager(data_manager)
pyq_manager = PYQManager(data_manager)
mental_health_nlp = MentalHealthNLP()
chatbot = ChatBot(data_manager, nlp_processor, notes_manager, pyq_manager)

# ============= ROUTES =============
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

# Chat API
# Chat API
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        if request.json is None:
            return jsonify({'type': 'text', 'message': 'Invalid request format'})
            
        data = request.json
        message = data.get('message', '').strip()
        
        # Get session header
        login_timestamp = request.headers.get('X-Login-Timestamp')
        
        # Also check body (fallback logic if needed, but header is standard)
        if not login_timestamp:
             login_timestamp = data.get('login_timestamp')

        response = chatbot.process_query(message, login_timestamp)
        
        # If error is session_expired, return 401 status code so frontend handles it
        if response.get('error') == 'session_expired':
             return jsonify(response), 401
             
        return jsonify(response)
    except Exception as e:
        return jsonify({'type': 'text', 'message': f'Error: {str(e)}'})

# ============= SUBJECTS API =============
@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    subjects = notes_manager.get_subjects()
    return jsonify({'subjects': subjects})

@app.route('/api/add_subject', methods=['POST'])
def add_subject_api():
    data = request.json or {}
    subject_name = data.get('subject_name', '')
    keywords = data.get('keywords', '')
    if notes_manager.add_subject(subject_name, keywords):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Subject already exists'})

@app.route('/api/delete_subject', methods=['POST'])
def delete_subject_api():
    data = request.json or {}
    if notes_manager.delete_subject(data.get('subject_name', '')):
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/edit_subject', methods=['POST'])
def edit_subject_api():
    data = request.json or {}
    old_name = data.get('old_name', '')
    new_name = data.get('new_name', '')
    keywords = data.get('keywords', '')
    
    if notes_manager.edit_subject(old_name, new_name, keywords):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Failed to edit subject'})

# ============= UNITS API =============
@app.route('/api/add_unit/<subject_name>', methods=['POST'])
def add_unit_api(subject_name):
    try:
        file = request.files.get('file')
        unit_name = request.form.get('unit_name', '')
        keywords = request.form.get('keywords', '')
        if notes_manager.add_unit(subject_name, unit_name, file, keywords):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Failed to add unit'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete_unit', methods=['POST'])
def delete_unit_api():
    data = request.json or {}
    if notes_manager.delete_unit(data.get('subject_name', ''), data.get('unit_name', '')):
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/edit_unit', methods=['POST'])
def edit_unit_api():
    data = request.json or {}
    subject = data.get('subject', '')
    old_unit_name = data.get('old_unit_name', '')
    new_unit_name = data.get('new_unit_name', '')
    keywords = data.get('keywords', '')
    
    if notes_manager.edit_unit(subject, old_unit_name, new_unit_name, keywords):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Failed to edit unit'})

@app.route('/api/download_unit/<subject_name>/<unit_name>')
def download_unit(subject_name, unit_name):
    subjects = notes_manager.get_subjects()
    if subject_name in subjects and unit_name in subjects[subject_name]['units']:
        filename = subjects[subject_name]['units'][unit_name]['filename']
        try:
            return send_from_directory(UPLOAD_FOLDER / subject_name, filename, as_attachment=True)
        except:
            return jsonify({'error': 'File not found'}), 404
    return jsonify({'error': 'Not found'}), 404

# ============= INFO MANAGEMENT API =============
@app.route('/api/info', methods=['GET'])
def get_info():
    info_data = data_manager.load_json(DATA_DIR / 'info.json')
    return jsonify({'info': info_data})

@app.route('/api/test_info', methods=['GET'])
def test_info():
    """Test endpoint to debug info matching"""
    test_query = "fee structure"
    print(f"=== TESTING INFO HANDLER ===")
    response = chatbot._handle_info_request(test_query)
    print(f"=== TEST RESPONSE ===")
    print(response)
    return jsonify({
        'query': test_query,
        'response': response,
        'debug': 'Check server console for detailed debug output'
    })

@app.route('/api/add_section', methods=['POST'])
def add_section():
    data = request.json or {}
    category = data.get('category', '')
    keywords = data.get('keywords', '')
    
    if not category:
        return jsonify({'success': False, 'error': 'Section name is required'})
        
    info_data = data_manager.load_json(DATA_DIR / 'info.json')
    
    if category in info_data:
        return jsonify({'success': False, 'error': 'Section already exists'})
        
    info_data[category] = {
        'keywords': [], # No section-level keywords anymore
        'items': [], 
        'created_at': datetime.datetime.now().isoformat()
    }
    
    data_manager.save_json(DATA_DIR / 'info.json', info_data)
    return jsonify({'success': True})

@app.route('/api/delete_section', methods=['POST'])
def delete_section():
    data = request.json or {}
    category = data.get('category', '')
    info_data = data_manager.load_json(DATA_DIR / 'info.json')
    if category in info_data:
        del info_data[category]
        data_manager.save_json(DATA_DIR / 'info.json', info_data)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/edit_section', methods=['POST'])
def edit_section():
    data = request.json or {}
    original_category = data.get('original_category', '')
    new_category = data.get('new_category', '')
    keywords = data.get('keywords', [])
    
    if not original_category or not new_category:
        return jsonify({'success': False, 'error': 'Missing required fields'})
    
    info_data = data_manager.load_json(DATA_DIR / 'info.json')
    
    if original_category not in info_data:
        return jsonify({'success': False, 'error': 'Original category not found'})
    
    if original_category != new_category and new_category in info_data:
        return jsonify({'success': False, 'error': 'New category name already exists'})
    
    # Update data
    section_data = info_data[original_category]
    # Keep existing keywords or set to empty if we want to enforce removal
    # Since specific keywords are on items now, we can just leave this alone or clear it.
    # Let's clear it to be safe/clean.
    section_data['keywords'] = [] 
    section_data['updated_at'] = datetime.datetime.now().isoformat()
    
    # Handle rename
    if original_category != new_category:
        del info_data[original_category]
        info_data[new_category] = section_data
        
    data_manager.save_json(DATA_DIR / 'info.json', info_data)
    return jsonify({'success': True})

# --- ITEM APIs ---

@app.route('/api/add_info_item', methods=['POST'])
def add_info_item():
    data = request.json or {}
    section = data.get('section', '')
    title = data.get('title', '')
    content = data.get('content', '')
    keywords = data.get('keywords', '')
    
    if not section or not content:
        return jsonify({'success': False, 'error': 'Section and content are required'})
        
    info_data = data_manager.load_json(DATA_DIR / 'info.json')
    
    if section not in info_data:
        return jsonify({'success': False, 'error': 'Section not found'})
        
    # Initialize items list if it doesn't exist (migration support)
    if 'items' not in info_data[section]:
        info_data[section]['items'] = []
        
    # Generate a meaningful title from content if not provided
    if not title:
        title = content[:50] + ('...' if len(content) > 50 else '')
    
    new_item = {
        'id': str(datetime.datetime.now().timestamp()).replace('.', ''),
        'title': title,
        'content': content,
        'keywords': [k.strip().lower() for k in keywords.split(',') if k.strip()],
        'created_at': datetime.datetime.now().isoformat()
    }
    
    info_data[section]['items'].append(new_item)
    data_manager.save_json(DATA_DIR / 'info.json', info_data)
    return jsonify({'success': True})

@app.route('/api/edit_info_item', methods=['POST'])
def edit_info_item():
    data = request.json or {}
    section = data.get('section', '')
    item_id = data.get('id', '')
    title = data.get('title', '')
    content = data.get('content', '')
    keywords = data.get('keywords', [])
    
    if not section or not item_id:
        return jsonify({'success': False, 'error': 'Missing ID'})
        
    info_data = data_manager.load_json(DATA_DIR / 'info.json')
    
    if section not in info_data or 'items' not in info_data[section]:
        return jsonify({'success': False, 'error': 'Section or items not found'})
        
    found = False
    for item in info_data[section]['items']:
        if item.get('id') == item_id:
            # Generate title from content if not provided
            if not title:
                title = content[:50] + ('...' if len(content) > 50 else '')
            item['title'] = title
            item['content'] = content
            # Handle keywords list vs string
            if isinstance(keywords, str):
                 item['keywords'] = [k.strip().lower() for k in keywords.split(',') if k.strip()]
            else:
                 item['keywords'] = keywords
            item['updated_at'] = datetime.datetime.now().isoformat()
            found = True
            break
            
    if found:
        data_manager.save_json(DATA_DIR / 'info.json', info_data)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Item not found'})

@app.route('/api/delete_info_item', methods=['POST'])
def delete_info_item():
    data = request.json or {}
    section = data.get('section', '')
    item_id = data.get('id', '')
    
    info_data = data_manager.load_json(DATA_DIR / 'info.json')
    
    if section in info_data and 'items' in info_data[section]:
        initial_len = len(info_data[section]['items'])
        info_data[section]['items'] = [i for i in info_data[section]['items'] if i.get('id') != item_id]
        
        if len(info_data[section]['items']) < initial_len:
            data_manager.save_json(DATA_DIR / 'info.json', info_data)
            return jsonify({'success': True})
            
    return jsonify({'success': False, 'error': 'Item not found'})

# ============= KNOWLEDGE BASE API =============
@app.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    knowledge = data_manager.load_json(DATA_DIR / 'knowledge_base.json')
    return jsonify({'knowledge': knowledge})

@app.route('/api/add_knowledge', methods=['POST'])
def add_knowledge():
    data = request.json or {}
    if not data:
        return jsonify({'success': False, 'error': 'Invalid request'})
    question = data.get('question', '')
    answer = data.get('answer', '')
    knowledge = data_manager.load_json(DATA_DIR / 'knowledge_base.json')
    knowledge.append({
        'id': len(knowledge) + 1,
        'question': question,
        'answer': answer,
        'created_at': datetime.datetime.now().isoformat()
    })
    data_manager.save_json(DATA_DIR / 'knowledge_base.json', knowledge)
    return jsonify({'success': True})

@app.route('/api/delete_knowledge', methods=['POST'])
def delete_knowledge():
    data = request.json or {}
    qa_id = data.get('id')
    knowledge = data_manager.load_json(DATA_DIR / 'knowledge_base.json')
    knowledge = [qa for qa in knowledge if qa.get('id') != qa_id]
    data_manager.save_json(DATA_DIR / 'knowledge_base.json', knowledge)
    return jsonify({'success': True})

# ============= UNANSWERED API =============
@app.route('/api/unanswered', methods=['GET'])
def get_unanswered():
    unanswered = data_manager.load_json(DATA_DIR / 'unanswered_queries.json')
    return jsonify({'unanswered': unanswered})

@app.route('/api/delete_unanswered', methods=['POST'])
def delete_unanswered():
    data = request.json or {}
    query_to_delete = data.get('query', '')
    
    if not query_to_delete:
        return jsonify({'success': False, 'error': 'Query is required'})
    
    unanswered = data_manager.load_json(DATA_DIR / 'unanswered_queries.json')
    original_length = len(unanswered)
    
    # Remove the query that matches exactly
    unanswered = [q for q in unanswered if q.get('query', '') != query_to_delete]
    
    if len(unanswered) < original_length:
        data_manager.save_json(DATA_DIR / 'unanswered_queries.json', unanswered)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Query not found'})

# ============= FEEDBACK API =============
@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    feedback = data_manager.load_json(DATA_DIR / 'feedback.json')
    return jsonify({'feedback': feedback})

@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json or {}
        text = data.get('feedback', '').strip()
        if not text:
            return jsonify({'success': False, 'error': 'Feedback cannot be empty'})
        
        feedback = data_manager.load_json(DATA_DIR / 'feedback.json')
        feedback.append({
            'text': text,
            'submitted_at': datetime.datetime.now().isoformat()
        })
        data_manager.save_json(DATA_DIR / 'feedback.json', feedback)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete_feedback', methods=['POST'])
def delete_feedback():
    try:
        data = request.json or {}
        # Do NOT strip(), we need exact match for deletion
        text = data.get('text', '')
        timestamp = data.get('submitted_at', '')
        
        feedback = data_manager.load_json(DATA_DIR / 'feedback.json')
        
        # Filter out item matching (text OR message) AND (submitted_at OR created_at)
        new_feedback = []
        for f in feedback:
            f_text = f.get('text') or f.get('message') or ''
            f_time = f.get('submitted_at') or f.get('created_at') or ''
            
            # If both match, it's the item to delete -> skip it
            if f_text == text and f_time == timestamp:
                continue
            new_feedback.append(f)
        
        data_manager.save_json(DATA_DIR / 'feedback.json', new_feedback)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============= CHATBOT AUTH API =============
@app.route('/api/chatbot/login', methods=['POST'])
def chatbot_login():
    try:
        data = request.json or {}
        password = data.get('password', '').strip()
        
        # Load as dict (new structure)
        auth_db = data_manager.load_json(DATA_DIR / 'chatbot_auth.json')
        
        # If legacy list, migrate on fly or fail? Better to use new structure. 
        # But for robustness, let's assume migration happens or file is overwritten.
        # Check hash
        if isinstance(auth_db, list):
             # Legacy fallback: check strictly against '123' or wipe
             # For this task, we assume we will overwrite the file or migration is manual
             # Let's just validate against what's there if it matches hash logic
             pass

        if 'password_hash' in auth_db and data_manager.hash_password(password) == auth_db['password_hash']:
            # Success: Return token (login time)
            return jsonify({
                'success': True, 
                'department': 'General', # Deprecated but kept for frontend compat
                'login_timestamp': datetime.datetime.now().isoformat()
            })
        
        return jsonify({'success': False, 'error': 'Invalid password'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/change_chatbot_password', methods=['POST'])
def change_chatbot_password():
    try:
        data = request.json or {}
        current_pwd = data.get('current_password', '')
        new_pwd = data.get('new_password', '')
        
        auth_db = data_manager.load_json(DATA_DIR / 'chatbot_auth.json')
        
        # Verify current - if legacy list, hard fail or migrated?
        # We will reset the file in next step, so assume dict
        
        if 'password_hash' not in auth_db:
             # Should not happen if initialized correctly
             return jsonify({'success': False, 'error': 'Auth DB error'})

        if data_manager.hash_password(current_pwd) != auth_db['password_hash']:
             return jsonify({'success': False, 'error': 'Incorrect current password'})
             
        # Update
        auth_db['password_hash'] = data_manager.hash_password(new_pwd)
        auth_db['last_changed'] = datetime.datetime.now().isoformat()
        
        data_manager.save_json(DATA_DIR / 'chatbot_auth.json', auth_db)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============= PYQ API =============
@app.route('/api/pyq/list', methods=['GET'])
def get_pyq_list():
    pyqs = pyq_manager.get_pyqs()
    return jsonify({'pyqs': list(pyqs.values())})

@app.route('/api/pyq/upload', methods=['POST'])
def upload_pyq():
    try:
        file = request.files.get('file')
        name = request.form.get('name', '')
        keywords = request.form.get('keywords', '')
        file_type = request.form.get('type', 'Others')
        
        if not file or not name:
            return jsonify({'success': False, 'error': 'File and name are required'})
            
        result = pyq_manager.add_pyq(name, keywords, file_type, file)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pyq/edit', methods=['POST'])
def edit_pyq():
    try:
        data = request.json or {}
        pyq_id = data.get('id', '')
        name = data.get('name', '')
        keywords = data.get('keywords', '')
        file_type = data.get('type', 'Others')
        
        result = pyq_manager.edit_pyq(pyq_id, name, keywords, file_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pyq/delete', methods=['POST'])
def delete_pyq():
    try:
        data = request.json or {}
        pyq_id = data.get('id', '')
        
        result = pyq_manager.delete_pyq(pyq_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pyq/download/<pyq_id>')
def download_pyq(pyq_id):
    try:
        pyqs = pyq_manager.get_pyqs()
        
        if pyq_id not in pyqs:
            return 'PYQ not found', 404
            
        filename = pyqs[pyq_id].get('filename', '')
        if not filename:
            return 'File not found', 404
            
        filepath = pyq_manager.pyq_dir / filename
        
        if not filepath.exists():
            return 'File not found on disk', 404
            
        return send_file(str(filepath), as_attachment=True, download_name=filename)
    except Exception as e:
        return f'Error: {str(e)}', 500

# ============= ADMIN AUTH =============
@app.route('/api/admin/auth', methods=['POST'])
def admin_auth():
    data = request.json or {}
    password = data.get('password', '')
    auth_data = data_manager.load_json(DATA_DIR / 'auth.json')
    if data_manager.hash_password(password) == auth_data['password_hash']:
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False})

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    subjects = notes_manager.get_subjects()
    pyqs = pyq_manager.get_pyqs()
    info_data = data_manager.load_json(DATA_DIR / 'info.json')
    unanswered = data_manager.load_json(DATA_DIR / 'unanswered_queries.json')
    knowledge = data_manager.load_json(DATA_DIR / 'knowledge_base.json')
    return jsonify({
        'subjects': len(subjects),
        'pyqs': len(pyqs),
        'info_sections': len(info_data),
        'unanswered': len(unanswered),
        'knowledge': len(knowledge)
    })

@app.route('/api/admin/change_password', methods=['POST'])
def change_password():
    data = request.json or {}
    old_pwd = data.get('old_password', '')
    new_pwd = data.get('new_password', '')
    hint = data.get('hint', '')
    auth_data = data_manager.load_json(DATA_DIR / 'auth.json')
    if data_manager.hash_password(old_pwd) == auth_data['password_hash']:
        auth_data['password_hash'] = data_manager.hash_password(new_pwd)
        auth_data['password_hint'] = hint
        data_manager.save_json(DATA_DIR / 'auth.json', auth_data)
        return jsonify({'success': True})
    return jsonify({'success': False})

# ============= CHAT MANAGEMENT API =============
@app.route('/api/save_chat', methods=['POST'])
def save_chat():
    try:
        data = request.json or {}
        chat_id = data.get('chat_id')
        messages = data.get('messages', [])

        # ✅ Messages already have full structure from frontend:
        # {role, type, content, metadata, timestamp}
        # Just save them as-is!

        chat_data = {
            'id': chat_id,
            'name': f"Chat {len(list(CHATS_DIR.glob('*.json'))) + 1}",
            'messages': messages,  # ✅ Full rich message objects
            'created_at': datetime.datetime.now().isoformat()
        }
        filepath = CHATS_DIR / f"{chat_id}.json"
        data_manager.save_json(filepath, chat_data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_chats', methods=['GET'])
def get_chats():
    try:
        chats = []
        for chat_file in sorted(CHATS_DIR.glob('*.json'), reverse=True):
            chat_data = data_manager.load_json(chat_file)
            chats.append({
                'id': chat_data.get('id'),
                'name': chat_data.get('name', 'Chat'),
                'created_at': chat_data.get('created_at', ''),
                'message_count': len(chat_data.get('messages', []))
            })
        return jsonify({'chats': chats})
    except Exception as e:
        return jsonify({'chats': [], 'error': str(e)})

@app.route('/api/load_chat/<chat_id>')
def load_chat(chat_id):
    try:
        filepath = CHATS_DIR / f"{chat_id}.json"
        if filepath.exists():
            chat_data = data_manager.load_json(filepath)
            return jsonify({'messages': chat_data.get('messages', [])})
        return jsonify({'messages': [], 'error': 'Chat not found'})
    except Exception as e:
        return jsonify({'messages': [], 'error': str(e)})

# ✅ FIX #2 & #3: RENAME AND DELETE CHAT
@app.route('/api/rename_chat', methods=['POST'])
def rename_chat():
    try:
        data = request.json or {}
        chat_id = data.get('chat_id', '')
        new_name = data.get('name', '')
        
        filepath = CHATS_DIR / f"{chat_id}.json"
        if filepath.exists():
            chat_data = data_manager.load_json(filepath)
            chat_data['name'] = new_name
            data_manager.save_json(filepath, chat_data)
            return jsonify({'success': True, 'name': new_name})
        return jsonify({'success': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete_chat', methods=['POST'])
@app.route('/api/delete_chat/<chat_id>', methods=['DELETE', 'POST'])
def delete_chat(chat_id=None):
    try:
        # Handle both POST with body and URL parameter
        if chat_id is None:
            data = request.json or {}
            chat_id = data.get('chat_id')
        
        if not chat_id:
            return jsonify({'success': False, 'error': 'No chat ID provided'})
        
        filepath = CHATS_DIR / f"{chat_id}.json"
        if filepath.exists():
            filepath.unlink()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ✅ FIX #4: GET PASSWORD HINT
@app.route('/api/admin/hint', methods=['GET'])
def get_password_hint():
    try:
        auth_data = data_manager.load_json(DATA_DIR / 'auth.json')
        hint = auth_data.get('password_hint', 'No hint set')
        return jsonify({'hint': hint})
    except Exception as e:
        return jsonify({'hint': '', 'error': str(e)})

if __name__ == '__main__':
    import socket
    import ssl
    # Get the local IP address for mobile access
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    # Check if SSL certs exist for HTTPS
    cert_file = Path('cert.pem')
    key_file = Path('key.pem')
    use_ssl = cert_file.exists() and key_file.exists()

    protocol = "https" if use_ssl else "http"
    print("\n" + "="*70)
    print("Mentora AI - Complete Rebuild (100% DYNAMIC)")
    print("="*70)
    print(f"Chat:  {protocol}://localhost:3003")
    print(f"Admin: {protocol}://localhost:3003/admin (pwd: 123)")
    print(f"\n📱 Mobile Access (same WiFi):")
    print(f"   Chat:  {protocol}://{local_ip}:3003")
    print(f"   Admin: {protocol}://{local_ip}:3003/admin")
    if use_ssl:
        print(f"\n🔒 HTTPS enabled (self-signed cert)")
        print(f"   ⚠️  Accept the certificate warning on your phone browser")
    print("="*70 + "\n")

    if use_ssl:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(str(cert_file), str(key_file))
        app.run(debug=True, host='0.0.0.0', port=3003, use_reloader=False, ssl_context=ssl_context)
    else:
        app.run(debug=True, host='0.0.0.0', port=3003, use_reloader=False)
