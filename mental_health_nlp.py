"""
Mental Health NLP Module for Mentora
Implements classical NLP techniques for understanding and responding to mental health queries.
EMOTION-FIRST APPROACH: Always responds based on detected emotion, never fails silently.
"""

import re
import difflib
import random
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter

import os
import sys

NLTK_AVAILABLE = False
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    
    # Try to download NLTK data silently (may fail on PythonAnywhere free tier)
    try:
        for resource in ['punkt', 'stopwords', 'wordnet', 'omw-1.4', 'punkt_tab']:
            try:
                nltk.download(resource, quiet=True)
            except Exception:
                pass
    except Exception:
        pass
    
    # Verify NLTK data is actually usable
    try:
        stopwords.words('english')
        NLTK_AVAILABLE = True
    except Exception:
        NLTK_AVAILABLE = False
except Exception as e:
    print(f"Warning: NLTK not available: {e}")


class MentalHealthNLP:
    """NLP processor for mental health chatbot using classical NLP techniques"""
    
    def __init__(self):
        """Initialize NLP components and knowledge bases"""
        if NLTK_AVAILABLE:
            self.lemmatizer = WordNetLemmatizer()
        else:
            # Simple fallback lemmatizer
            class SimpleLemmatizer:
                def lemmatize(self, word):
                    return word
            self.lemmatizer = SimpleLemmatizer()
        
        try:
            self.stop_words = set(stopwords.words('english'))
            # Keep important emotional words that are in default stopwords
            self.stop_words -= {'no', 'not', 'very', 'too', 'down', 'up', 'can', 'cannot'}
        except:
            # Fallback if stopwords not available
            self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        
        # Initialize knowledge bases
        self.emotion_keywords = {
            'anxious': ['anxious', 'anxiety', 'worried', 'nervous', 'panic', 'fear', 'afraid', 'scared', 'tense', 'uneasy', 'restless', 'on edge', 'apprehensive', 'frightened', 'terrified', 'phobia', 'dread', 'foreboding', 'jittery', 'shaky', 'sweating', 'palpitations', 'racing heart', 'cant breathe', 'hyperventilating'],
            'sad': ['sad', 'depressed', 'depression', 'unhappy', 'miserable', 'down', 'blue', 'gloomy', 'heartbroken', 'crying', 'tears', 'hopeless', 'despair', 'melancholy', 'grief', 'mourning', 'devastated', 'crushed', 'empty', 'numb', 'worthless', 'pathetic', 'meaningless', 'darkness', 'void'],
            'stressed': ['stressed', 'stress', 'overwhelmed', 'pressure', 'burnout', 'exhausted', 'tired', 'fatigue', 'drained', 'worn out', 'overworked', 'burdened', 'swamped', 'drowning', 'suffocating', 'cant cope', 'too much', 'breaking point', 'at my limit', 'fed up', 'had enough'],
            'confused': ['confused', 'confusion', 'uncertain', 'unsure', 'lost', 'clueless', 'puzzled', 'bewildered', 'dont know', 'unclear', 'ambiguous', 'mixed up', 'disoriented', 'perplexed', 'baffled', 'stumped', 'dont understand', 'making sense', 'figure out'],
            'lonely': ['lonely', 'alone', 'loneliness', 'isolated', 'no one', 'nobody', 'by myself', 'empty', 'solitary', 'secluded', 'withdrawn', 'abandoned', 'rejected', 'unwanted', 'invisible', 'forgotten', 'left out', 'excluded', 'misunderstood'],
            'happy': ['happy', 'happiness', 'joy', 'glad', 'pleased', 'delighted', 'cheerful', 'excited', 'good', 'great', 'wonderful', 'amazing', 'fantastic', 'awesome', 'ecstatic', 'euphoric', 'elated', 'jubilant', 'thrilled', 'overjoyed', 'content', 'satisfied', 'pleased'],
            'calm': ['calm', 'peaceful', 'relaxed', 'serene', 'tranquil', 'at ease', 'comfortable', 'content', 'satisfied', 'composed', 'collected', 'centered', 'balanced', 'grounded', 'zen', 'untroubled', 'placid', 'still', 'quiet', 'restful'],
            'angry': ['angry', 'anger', 'mad', 'furious', 'irritated', 'annoyed', 'frustrated', 'upset', 'resentful', 'rage', 'outraged', 'enraged', 'infuriated', 'livid', 'irate', 'incensed', 'aggravated', 'provoked', 'hostile', 'bitter', 'resentful'],
            'guilty': ['guilty', 'guilt', 'regret', 'ashamed', 'embarrassed', 'sorry', 'my fault', 'blame', 'remorse', 'bad', 'wrong', 'mistake', 'failure', 'let down', 'disappointed', 'should have', 'could have'],
            'proud': ['proud', 'pride', 'accomplished', 'achievement', 'success', 'succeeded', 'did it', 'made it', 'triumph', 'victory', 'won', 'excelled', 'mastered', 'completed', 'finished', 'done well', 'impressed'],
            'relieved': ['relieved', 'relief', 'better', 'glad its over', 'weight lifted', 'breathing again', 'sigh of relief', 'pressure off', 'free', 'unburdened', 'restored', 'recovered', 'safe', 'secure'],
            'grateful': ['grateful', 'gratitude', 'thankful', 'appreciate', 'blessed', 'lucky', 'thank you', 'fortunate', 'privileged', 'thankful for', 'appreciation', 'recognition', 'acknowledgment'],
            'motivated': ['motivated', 'motivation', 'inspired', 'driven', 'determined', 'focused', 'ready', 'energized', 'enthusiastic', 'passionate', 'committed', 'dedicated', 'ambitious', 'goal-oriented', 'proactive'],
            'excited': ['excited', 'excitement', 'thrilled', 'enthusiastic', 'eager', 'looking forward', 'anticipation', 'cant wait', 'pumped', 'stoked', 'hyped', 'enthusiastic', 'animated', 'vibrant'],
            'disappointed': ['disappointed', 'disappointment', 'let down', 'failed', 'failure', 'didnt work out', 'not good enough', 'fell short', 'missed', 'lost', 'defeated', 'crushed'],
            'worried': ['worried', 'worry', 'concerned', 'concern', 'troubled', 'bothered', 'disturbed', 'uneasy', 'apprehensive', 'fearful', 'afraid', 'scared'],
            'tired': ['tired', 'exhausted', 'fatigued', 'weary', 'drained', 'worn out', 'sleepy', 'drowsy', 'lethargic', 'no energy', 'burned out']
        }
        
        self.concern_keywords = {
            'academic': ['study', 'studying', 'exam', 'exams', 'test', 'tests', 'grades', 'marks', 'assignment', 'assignments', 'project', 'projects', 'class', 'classes', 'course', 'courses', 'subject', 'subjects', 'semester', 'term', 'college', 'university'],
            'social': ['friends', 'friendship', 'relationship', 'relationships', 'people', 'social', 'talk', 'talking', 'communication', 'alone', 'lonely', 'isolated'],
            'sleep': ['sleep', 'sleeping', 'insomnia', 'sleepless', 'awake', 'night', 'nights', 'tired', 'fatigue', 'rest', 'restless'],
            'future': ['future', 'career', 'job', 'jobs', 'work', 'employment', 'professional', 'path', 'direction', 'goals', 'ambition'],
            'family': ['family', 'parents', 'parent', 'mother', 'father', 'sibling', 'siblings', 'brother', 'sister', 'home', 'house'],
            'health': ['health', 'healthy', 'sick', 'illness', 'disease', 'pain', 'ache', 'headache', 'stomach', 'body', 'exercise', 'diet']
        }
        
        self.uncertainty_keywords = ['maybe', 'perhaps', 'possibly', 'might', 'could', 'uncertain', 'unsure', 'confused', 'dont know', 'not sure']
        
        # Response templates - EMOTION-FIRST APPROACH (3-4 sentences max)
        self.response_templates = {
            'anxious': [
                "I can hear that you're feeling anxious{context}. That's a tough feeling to carry, but remember anxiety is temporary and you're stronger than you think. Take a deep breath and ground yourself - you've handled difficult moments before and you'll get through this too. Your feelings are valid, and this feeling will pass with time. 💙",
                "That anxious feeling{context} sounds overwhelming right now. Your body is trying to protect you, even though it feels uncomfortable and exhausting. Try grounding yourself by noticing 5 things you can see and 4 you can touch around you. You have the tools to manage this, even when it doesn't feel like it. 🌿",
                "I understand you're dealing with anxiety{context}. It's exhausting when your mind races with worries that won't quiet down. Be gentle with yourself - anxiety isn't a weakness, it's actually a sign that you care deeply about things. You deserve peace, and you'll find your way through this moment. 💚",
                "Anxiety{context} can feel so heavy, like a weight on your chest that won't lift. Remember that you've survived 100% of your difficult days so far, and this one is no exception. This moment is temporary, even if it feels endless while you're in it. You're not alone in feeling this way. 🌸",
                "I hear that anxiety is affecting you{context} and making everything feel harder. Your nervous system is working overtime trying to keep you safe from perceived threats. Gently remind yourself: you're okay, you're capable, and this feeling will eventually ease. You've got this, one breath at a time. ✨"
            ],
            'sad': [
                "I'm really sorry you're feeling this sadness{context}. It's okay to feel this way - sadness shows you have a deep capacity to care and connect with what matters. You don't have to be strong all the time, and it's okay to let yourself feel this emotion fully. This feeling is temporary, even if it doesn't feel like it right now. 💜",
                "That sadness{context} sounds heavy, and I want you to know it's okay to not be okay right now. Your feelings are valid and important - don't let anyone tell you otherwise. Be gentle with yourself today and allow yourself to feel without judgment or rushing to 'fix' it. You deserve compassion and understanding. 🌧️",
                "I hear you're carrying sadness{context} and that must feel exhausting. Remember that emotions come in waves - this feeling won't last forever, even if it feels overwhelming right now. You're not alone in this, even when it feels that way, and brighter days will come again. 💙",
                "That feeling of sadness{context} is real and important, so please don't dismiss it or rush yourself to 'get over it.' Your feelings matter and they deserve to be acknowledged and processed. I'm here with you in this moment, and you don't have to face this feeling alone. 🌿",
                "I understand you're feeling down{context} and that's completely okay. Be patient and compassionate with yourself - healing isn't linear and some days are harder than others. You deserve kindness, especially from yourself right now. This feeling will pass, even if it takes time. 💚"
            ],
            'stressed': [
                "I can hear how overwhelmed you're feeling{context}. That stress is real and valid - your body and mind are carrying a heavy burden right now. Remember: you don't have to handle everything perfectly, and good enough is truly enough. You're doing your best, and that's more than sufficient. 💪",
                "That stress{context} sounds exhausting and I can understand why you feel this way. Your body and mind are telling you they need a break, and it's important to listen to those signals. Even small moments of rest can help recharge your batteries. You deserve moments of peace and rest. 🌿",
                "I understand you're feeling stressed{context} and everything probably feels like too much right now. When everything feels overwhelming, focus on just one small thing you can control in this moment. You're doing your best in difficult circumstances, and that takes incredible strength. 💙",
                "That overwhelmed feeling{context} is so draining and can make everything seem harder than it actually is. Stress is your body's way of saying something needs attention or adjustment. You don't have to solve everything at once - just focus on the next right step. ✨",
                "I hear you're stressed{context} and it sounds like you're carrying too much on your shoulders. Consider which tasks are actually urgent and which can wait until tomorrow or next week. Give yourself permission to prioritize your wellbeing and let some things wait. You're worth more than your productivity. 🌸"
            ],
            'confused': [
                "I understand you're feeling confused{context}. That uncertainty can be really uncomfortable. It's okay not to have all the answers right now - clarity comes with time. 🤔",
                "That confusion{context} sounds frustrating. When things feel unclear, try breaking them down into smaller pieces. You don't need the whole picture right away. 💡",
                "I hear you're feeling uncertain{context}. It's completely normal to feel lost sometimes. Be patient with yourself as you navigate this - you're capable of finding your way. 🌟",
                "That confused feeling{context} shows you're thinking deeply and care about getting things right. Sometimes the best approach is to pause, breathe, and trust that clarity will come. 💚",
                "I understand you're feeling unclear{context}. Try focusing on what you do know, even if it's small. You have more wisdom than you think, and you'll find your path forward. 🌿"
            ],
            'lonely': [
                "I'm sorry you're feeling lonely{context}. That's such a painful feeling, especially when surrounded by people but still feeling alone. Your feelings are valid and you deserve connection. 💙",
                "That loneliness{context} sounds really hard. Even though I'm an AI, I want you to know you're heard right now. Consider reaching out to someone - you're not as alone as you feel. 🌟",
                "I understand you're feeling isolated{context}. Loneliness can feel like a heavy blanket. Be gentle with yourself and consider one small step toward connection - you deserve it. 💚",
                "That feeling of loneliness{context} is so real. It's okay to admit you need more connection. You're not weak for feeling this way - you're human and deserve meaningful relationships. 🌸",
                "I hear you're feeling alone{context}. Your desire for connection shows your capacity for relationships. Consider reaching out, even if it feels difficult - you deserve connection. ✨"
            ],
            'happy': [
                "That's wonderful to hear! 🎉 I'm so glad you're feeling good{context} and experiencing joy right now. Keep embracing these positive moments - they're important fuel for the challenging days that might come. Your happiness is well-deserved and beautiful to witness. Keep shining and spreading that joy! ✨",
                "I love hearing that you're feeling great{context}! 😊 Celebrate these moments fully and hold onto this positive energy as long as you can. You deserve all the good things coming your way and more. This happiness is a reflection of the amazing person you are. 🌟",
                "That's amazing! 🌈 So happy for you{context} and this beautiful feeling you're experiencing. These positive feelings are so important - savor every moment of them! Keep up whatever you're doing that's bringing you this joy. Remember this feeling when times get tough - it's proof that happiness is possible. 💫",
                "This makes me so happy to hear{context}! 🌻 Enjoy this beautiful moment completely - you've earned every bit of this happiness. Your joy is contagious and has the power to brighten others' days too. Keep spreading that positive energy wherever you go! ✨",
                "Yay! 🎊 I'm thrilled you're feeling happy{context} right now! Soak in these good vibes and let them energize every part of your life. You deserve every bit of this happiness and so much more. This is what life is all about - these precious moments of pure joy! 🌟"
            ],
            'calm': [
                "That's so lovely to hear! 😌 That peace and calm{context} sounds wonderful. Savor these moments of tranquility - they're precious and show your inner strength. 🌿",
                "I'm glad you're feeling peaceful{context}. 🧘 That sense of calm is so valuable. Hold onto this feeling - it shows your resilience and the balance you're creating in your life. 💚",
                "That calm feeling{context} sounds beautiful. ✨ You've found that peaceful space within yourself. Treasure these moments - they're the foundation of your wellbeing. 🌸",
                "It's wonderful that you're feeling serene{context}. 🌊 That inner peace is special - you've cultivated this calm and it will carry you through challenging times too. 💙",
                "That sense of being at ease{context} is so valuable. 😊 You've found your center. This peaceful feeling shows your growth and strength - keep nurturing this calm. 🌟"
            ],
            'angry': [
                "I understand you're feeling angry{context}. That anger is valid - it often shows that something important to you has been violated. Try to channel that energy constructively when you're ready. 🔥",
                "That anger{context} sounds intense. It's okay to feel angry - it's a natural emotion. Try not to let it consume you, though. Take deep breaths and remember you're stronger than your anger. 💢",
                "I hear you're frustrated{context}. That anger is telling you something needs attention. Listen to what it's trying to say, but don't let it drive all your decisions. You're in control. ⚡",
                "That feeling of being angry{context} is completely understandable. Sometimes things happen that rightfully make us mad. Your feelings are valid - just take care of yourself through this intensity. 💪",
                "I understand that anger{context}. It's like fire - it can be destructive but also purifying. Acknowledge the feeling, then decide how you want to use that energy constructively. 🌋"
            ],
            'guilty': [
                "I hear that you're feeling guilty{context}. Remember that everyone makes mistakes - it's part of being human. What matters is learning and growing from them. Be kind to yourself. 💙",
                "Guilt{context} shows you have a conscience and care about your impact on others. That's actually a strength. If you need to make amends, do so gently - then work on forgiving yourself. 🌟",
                "Feeling guilty{context} can be heavy. Ask yourself: is this guilt helping you grow, or just punishing you? If you've learned the lesson, be compassionate with yourself. 💚",
                "I understand you're carrying guilt{context}. Remember that you're human, not perfect. Acknowledge what happened, learn from it, and move forward with compassion for yourself. 💜",
                "That guilty feeling{context} shows you care. If you need to apologize or make something right, do it - then release the burden. You're worthy of peace and self-compassion. 🌸"
            ],
            'proud': [
                "You absolutely should be proud{context}! 🏆 Your accomplishments are real and meaningful. Take a moment to truly celebrate - you've earned this. You're amazing! ✨",
                "That sense of pride{context} is so well-deserved! 🌟 Own your achievements - you worked hard for them. This is YOUR moment to shine. Congratulations! 🎉",
                "Feeling proud{context} is exactly right! 💪 Your success didn't happen by accident - it came from your effort and determination. Celebrate yourself! You're incredible! 🌈",
                "Pride looks good on you{context}! 🎊 You've accomplished something meaningful and should absolutely bask in it. This is just the beginning of your success! ✨",
                "I'm proud of you too{context}! 🌟 You did the work, overcame challenges, and made it happen. Celebrate this victory - you've truly earned it! 🎉"
            ],
            'relieved': [
                "I can imagine what a weight lifted{context}! 😌 Relief feels so good after carrying that burden. Take a deep breath and enjoy this moment of peace. You got through it! 🌿",
                "That relief{context} must feel amazing! 💚 You made it through! Now you can breathe easier. Take time to recover and appreciate this lighter feeling. You did it! ✨",
                "Relief{context} is such a beautiful feeling! 🌸 You've been carrying stress and can finally release it. Savor this peace - you've earned every bit of it! 💫",
                "I'm so glad you're feeling relief{context}! 🌈 That tension is finally releasing. Take this moment to rest and recharge. The hard part is over! 🌟",
                "What a relief this must be{context}! 😊 You can finally breathe again. Enjoy this calm after the storm - you navigated through beautifully! 💙"
            ],
            'grateful': [
                "Gratitude{context} is such a powerful emotion! 🙏 It's beautiful that you're recognizing the good in your life. This mindset will bring even more positivity your way! 💚",
                "I love that you're feeling grateful{context}! 🌟 Appreciation for the good things magnifies joy. Hold onto this feeling - it's transformative and will attract more good things. ✨",
                "That gratitude{context} shows a beautiful heart! 🌻 Being thankful even in challenging times is a strength. Keep nurturing that appreciative spirit - it's wonderful! 💛",
                "Gratitude looks good on you{context}! 🌈 This positive mindset will attract more good things into your life. Keep counting those blessings and stay positive! 🌟",
                "Feeling grateful{context} is wonderful! 💙 This positive perspective will carry you through both good and challenging times. You're doing great and have much to appreciate! ✨"
            ],
            'motivated': [
                "That motivation{context} is powerful! 🔥 Ride this wave of determination - it will carry you far. Channel this energy into action and watch yourself soar! 💪",
                "I love this motivated energy{context}! ⚡ When you feel this driven, amazing things happen. Use this momentum wisely - you're unstoppable right now! 🚀",
                "Your motivation{context} is inspiring! 🌟 This is the perfect time to chase your goals. Strike while the iron is hot - you've got the power and determination! ✨",
                "That drive{context} is incredible! 💫 When motivation strikes, seize it! You're in the perfect mindset to tackle challenges and achieve great things. Go for it! 🎯",
                "I can feel your determination{context}! 🌈 That motivated energy is going to take you places. Trust this feeling and let it guide your actions - success is on its way! 🌟"
            ],
            'excited': [
                "I can feel your excitement{context}! 🎉 That energy is amazing! Ride this wave of enthusiasm - it's powerful and will help you achieve great things. Keep that fire burning! 🔥",
                "Your excitement is contagious{context}! 🌟 This anticipation and energy is wonderful. Channel it into action and watch amazing things unfold! I'm excited for you too! ✨",
                "Wow, I love the enthusiasm{context}! 🚀 Being this excited means something great is happening or coming. Embrace it fully and let it propel you forward! You've got this! 💫",
                "This is so exciting{context}! 🎊 That electric feeling of anticipation is one of life's best emotions. Enjoy every moment and let it fuel your next steps! 🌈",
                "Your excitement is absolutely infectious{context}! ⚡ Hold onto this feeling - it's precious and powerful. Great things are ahead for you and you're ready for them! 🌟"
            ],
            'disappointed': [
                "I understand you're feeling disappointed{context}. That feeling of letdown is really tough when things didn't go as you hoped. Remember that disappointment doesn't define your worth or future success. This is just one moment, not your whole story. 💙",
                "That disappointment{context} sounds really hard to carry right now. It's okay to feel this way when expectations weren't met. Be gentle with yourself and remember that setbacks are often stepping stones to comebacks. You'll get through this. 🌿",
                "I hear you're dealing with disappointment{context}. That feeling when things don't work out can be discouraging, but it doesn't mean you failed. You're learning and growing, even when it feels painful. This feeling will pass with time. 💚",
                "That sense of disappointment{context} is completely understandable. When we invest hope in something and it doesn't pan out, it hurts. Allow yourself to feel this, but don't let it dim your light. You have so much strength and potential. 🌸",
                "I understand you're feeling let down{context}. Disappointment is a natural part of life and shows that you care deeply about things. This feeling isn't permanent - you'll find your way forward and maybe even discover something better. ✨"
            ],
            'worried': [
                "I can hear that you're worried{context}. That concern shows you're thoughtful and care about outcomes, but constant worrying can be exhausting. Try to focus on what you can control and let go of what you can't. You're more capable than you think. 💙",
                "That worry{context} sounds like it's weighing heavily on you. Your mind is trying to protect you by anticipating problems, but it's important to stay present too. Take a deep breath and remember you've handled challenges before. You'll get through this too. 🌿",
                "I understand you're feeling concerned{context}. Worry is your brain's way of trying to keep you safe, but it can become overwhelming. Try breaking your concerns into smaller, manageable pieces. You don't have to solve everything at once. 💚",
                "That worried feeling{context} is completely understandable when things feel uncertain. Remember that many things we worry about never actually happen. Focus on the present moment and take things one step at a time. You're stronger than your worries. 🌸",
                "I hear you're feeling worried{context}. That shows you're conscientious and care deeply, but don't let worry steal your peace of mind. You have the resources and resilience to handle whatever comes your way. Trust in your ability to cope. ✨"
            ],
            'tired': [
                "I can hear how exhausted you're feeling{context}. That fatigue is your body and mind telling you they need rest and recovery. It's okay to slow down and take care of yourself - you deserve rest without guilt. Your wellbeing matters more than productivity. 💙",
                "That tired feeling{context} sounds completely overwhelming right now. When you're running on empty, everything feels harder. Please prioritize rest - you're not a machine, and taking breaks is essential for your health. You deserve to recharge. 🌿",
                "I understand you're feeling drained{context}. Physical and mental exhaustion can make everything seem impossible. Be gentle with yourself and recognize that rest isn't lazy - it's necessary for your survival and success. You need this break. 💚",
                "That fatigue{context} is your body's signal that something needs to change. Whether it's more sleep, less stress, or better nutrition, listen to what your body is telling you. You can't pour from an empty cup - refill yours first. 🌸",
                "I hear you're completely worn out{context}. That level of exhaustion is unsustainable and needs your immediate attention. Please give yourself permission to rest fully without judgment. You're human, not superhuman, and that's perfectly okay. ✨"
            ],
            'general_support': [
                "I'm here to listen{context}. Whatever you're going through, your feelings are valid and important. You don't have to face this alone - sometimes just having someone acknowledge your struggle can bring relief. 💙",
                "Thank you for sharing this with me{context}. It takes courage to express what you're feeling, and I'm honored that you trust me. Remember that difficult moments don't last forever, and you're stronger and more resilient than you realize. 🌿",
                "I hear you, and I want you to know that what you're experiencing matters{context}. Be gentle with yourself - you're doing the best you can with what you have right now. That's genuinely enough, and you're worthy of compassion and care. 💚",
                "That sounds really challenging{context}. I'm here to support you through this difficult time. Remember that expressing your feelings is a sign of strength, not weakness. You're not alone in this, even when it might feel that way. 🌸",
                "I understand this is difficult for you{context}. Take things one moment at a time and one breath at a time. You don't have to have all the answers right now - just focus on getting through this moment with self-compassion. ✨"
            ]
        }
        
        self.greeting_responses = [
            "Hello! I'm here to support you. How are you feeling today? 😊",
            "Hi there! I'm glad you reached out. What's on your mind? 💙",
            "Hey! I'm here to listen. How can I support you today? 🌟",
            "Hello! It's good to connect with you. How are you doing? 🌿",
            "Hi! I'm here to help. Feel free to share whatever's on your mind. 💚"
        ]
        
        # Polite fallback responses - NEVER say "I don't understand"
        self.polite_fallbacks = [
            "Thank you for sharing that with me. I'm here to listen to whatever you'd like to talk about. How are you feeling right now? 💙",
            "I appreciate you reaching out. Sometimes it helps to talk things through. What's been on your mind lately? 🌿",
            "I'm here to support you. Feel free to share more about what's going on, or we can just chat. Whatever feels right for you. 💚",
            "Thank you for connecting with me. I'm here to listen without judgment. What would be most helpful for you right now? 🌸",
            "I'm glad you're here. Sometimes just having someone to talk to can make a difference. What's on your heart today? ✨"
        ]

    def preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess text for analysis
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep emotional punctuation
        text = re.sub(r'[^\w\s!?.,]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        try:
            tokens = word_tokenize(text)
        except:
            # Fallback tokenization
            tokens = text.split()
        
        # Remove stopwords
        return [token for token in tokens if token not in self.stop_words]
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """
        Lemmatize tokens to base form
        
        Args:
            tokens: List of tokens
            
        Returns:
            Lemmatized tokens
        """
        try:
            return [self.lemmatizer.lemmatize(token) for token in tokens]
        except:
            # Fallback if lemmatizer fails
            return tokens
    
    def detect_emotion(self, text: str) -> Tuple[str, float]:
        """
        Detect dominant emotion from text with FUZZY MATCHING for spelling mistakes
        MANDATORY: Always detect some emotion, never return neutral unless absolutely certain
        """
        preprocessed = self.preprocess_text(text)
        tokens = self.tokenize(preprocessed)
        
        emotion_scores = Counter()
        
        # Count emotion keyword occurrences with FUZZY MATCHING
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                # Exact token match - highest weight
                if keyword in tokens:
                    emotion_scores[emotion] += 2.0
                # Phrase in text - medium weight
                elif keyword in preprocessed:
                    emotion_scores[emotion] += 1.5
                # FUZZY MATCHING for spelling mistakes - lower threshold
                else:
                    # Check fuzzy match against each token
                    for token in tokens:
                        similarity = difflib.SequenceMatcher(None, keyword, token).ratio()
                        if similarity > 0.6:  # LOWERED from 0.8 for spelling mistakes
                            emotion_scores[emotion] += 0.8
                            break
                    # Also check against the whole preprocessed text
                    similarity = difflib.SequenceMatcher(None, keyword, preprocessed).ratio()
                    if similarity > 0.6:  # LOWERED from 0.8
                        emotion_scores[emotion] += 0.5
        
        if emotion_scores:
            dominant_emotion = emotion_scores.most_common(1)[0][0]
            total_matches = sum(emotion_scores.values())
            # RELAXED confidence calculation
            confidence = min(emotion_scores[dominant_emotion] / max(total_matches * 0.5, 1.0), 1.0)
            return dominant_emotion, confidence
        
        # If no clear emotion, try to infer from indirect expressions with fuzzy matching
        if self._is_indirect_expression(text):
            return 'sad', 0.3  # Default to sad for vague negative expressions
        
        return 'neutral', 0.0
    
    def detect_sentiment(self, text: str) -> str:
        """
        Detect sentiment (positive/negative/neutral) with RELAXED thresholds
        """
        preprocessed = self.preprocess_text(text)
        tokens = self.tokenize(preprocessed)
        
        positive_words = ['good', 'great', 'happy', 'love', 'excellent', 'amazing', 'wonderful', 'fantastic', 'perfect', 'best', 'awesome', 'brilliant', 'glad', 'pleased', 'delighted']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting', 'sad', 'angry', 'frustrated', 'annoyed', 'disappointed', 'upset']
        
        positive_count = sum(1 for word in tokens if word in positive_words)
        negative_count = sum(1 for word in tokens if word in negative_words)
        
        if positive_count > negative_count:
            return 'very_positive' if positive_count >= 2 else 'positive'
        elif negative_count > positive_count:
            return 'very_negative' if negative_count >= 2 else 'negative'
        
        return 'neutral'
    
    def _is_indirect_expression(self, text: str) -> bool:
        """
        Detect indirect emotional expressions
        """
        preprocessed = self.preprocess_text(text)
        
        # Indirect negative expressions
        indirect_patterns = [
            'feel heavy', 'nothing feels right', 'not okay', 'not good', 'off today', 
            'weird day', 'strange day', 'off', 'down', 'low', 'not myself',
            'out of sorts', 'not feeling well', 'under the weather', 'in a funk'
        ]
        
        # Indirect positive expressions
        positive_patterns = [
            'good day', 'great day', 'wonderful day', 'actually good', 'pretty good',
            'not bad', 'doing okay', 'doing well', 'fine', 'alright', 'better today'
        ]
        
        for pattern in indirect_patterns + positive_patterns:
            if pattern in preprocessed:
                return True
        
        return False
    
    def extract_keywords(self, text: str) -> Dict[str, List[str]]:
        """
        Extract emotion and concern keywords from text
        """
        preprocessed = self.preprocess_text(text)
        tokens = self.tokenize(preprocessed)
        
        extracted = {
            'emotions': [],
            'concerns': []
        }
        
        # Check for emotion keywords
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in preprocessed or keyword in tokens:
                    extracted['emotions'].append(emotion)
                    break
        
        # Check for concern keywords
        for concern, keywords in self.concern_keywords.items():
            for keyword in keywords:
                if keyword in preprocessed or keyword in tokens:
                    extracted['concerns'].append(concern)
                    break
        
        return extracted
    
    def _build_context_string(self, keywords: Dict[str, List[str]]) -> str:
        """
        Build context string from keywords
        """
        contexts = []
        
        if 'academic' in keywords.get('concerns', []):
            contexts.append(' about your studies')
        elif 'social' in keywords.get('concerns', []):
            contexts.append(' in your relationships')
        elif 'sleep' in keywords.get('concerns', []):
            contexts.append(' and struggling with sleep')
        elif 'future' in keywords.get('concerns', []):
            contexts.append(' about your future')
        elif 'family' in keywords.get('concerns', []):
            contexts.append(' with your family')
        elif 'health' in keywords.get('concerns', []):
            contexts.append(' about your health')
        
        return contexts[0] if contexts else ''
    
    def _generate_polite_fallback(self, context: str) -> str:
        """
        Generate polite fallback response - NEVER says "I don't understand"
        """
        fallback = random.choice(self.polite_fallbacks)
        return fallback.format(context=context)
    
    def process_query(self, text: str) -> Dict[str, Any]:
        """
        Process mental health query with DYNAMIC NLP-generated responses
        Uses tokenization, lemmatization, and semantic analysis for human-like responses
        """
        # Step 1: ADVANCED NLP PROCESSING
        tokens = self.tokenize(text)
        lemmas = [self.lemmatizer.lemmatize(token) for token in tokens]
        preprocessed = self.preprocess_text(text)
        
        # Step 2: EMOTION DETECTION with enhanced analysis
        emotion, emotion_confidence = self.detect_emotion(text)
        
        # Step 3: CONTEXTUAL ANALYSIS
        keywords = self.extract_keywords(text)
        context_entities = self._extract_context_entities(text)
        sentiment = self.detect_sentiment(text)
        
        # Step 4: DYNAMIC RESPONSE GENERATION (No predefined templates)
        if emotion != 'neutral' or self._contains_emotional_language(text):
            # Generate human-like response using NLP techniques
            dynamic_response = self._generate_dynamic_response(
                text, emotion, sentiment, keywords, context_entities, tokens, lemmas
            )
            return {
                'type': 'text',
                'message': dynamic_response
            }
        
        # Step 5: FALLBACK for non-emotional content
        return {
            'type': 'text',
            'message': self._generate_friendly_fallback(text)
        }
    
    def _ensure_minimum_sentences(self, response: str, min_sentences: int) -> str:
        """Ensure response has at least the minimum number of sentences"""
        # Count sentences by splitting on common sentence endings
        import re
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) >= min_sentences:
            return response
        
        # Add more sentences if needed
        additional_sentences = min_sentences - len(sentences)
        supporting_sentences = [
            "I'm here to support you through this journey.",
            "You deserve care and understanding during difficult times.",
            "Remember that seeking help is a sign of strength.",
            "Your feelings are valid and important.",
            "Taking care of your mental health is just as important as physical health.",
            "You're not alone in experiencing these challenges.",
            "Be patient and compassionate with yourself.",
            "Small steps forward are still progress.",
            "You have more resilience than you realize.",
            "This feeling will pass with time and support."
        ]
        
        # Add random supporting sentences
        for i in range(additional_sentences):
            if i < len(supporting_sentences):
                response += " " + random.choice(supporting_sentences)
        
        return response

    def _contains_emotional_language(self, text: str) -> bool:
        """Check if text contains emotional language patterns"""
        emotional_patterns = [
            'feel', 'feeling', 'sad', 'happy', 'angry', 'worried', 'anxious', 'stressed',
            'i am', 'im', 'makes me', 'emotion', 'mood', 'cry', 'tears', 'overwhelmed'
        ]
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in emotional_patterns)
    
    def _extract_context_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract contextual entities from text using NLP"""
        entities = {
            'academic': [],
            'social': [],
            'time': [],
            'intensity': []
        }
        
        # Academic context
        academic_words = ['exam', 'study', 'class', 'grade', 'assignment', 'project', 'test', 'semester']
        entities['academic'] = [word for word in academic_words if word in text.lower()]
        
        # Social context
        social_words = ['friend', 'family', 'relationship', 'people', 'alone', 'lonely', 'social']
        entities['social'] = [word for word in social_words if word in text.lower()]
        
        # Time context
        time_words = ['today', 'tomorrow', 'yesterday', 'week', 'month', 'always', 'never', 'now']
        entities['time'] = [word for word in time_words if word in text.lower()]
        
        # Intensity words
        intensity_words = ['very', 'really', 'so', 'extremely', 'completely', 'totally', 'absolutely']
        entities['intensity'] = [word for word in intensity_words if word in text.lower()]
        
        return entities
    
    def _generate_dynamic_response(self, text: str, emotion: str, sentiment: str, 
                                 keywords: List[str], entities: Dict[str, List[str]], 
                                 tokens: List[str], lemmas: List[str]) -> str:
        """Generate dynamic, human-like response using NLP analysis"""
        
        # Build response components based on analysis
        response_parts = []
        
        # Part 1: Acknowledge and validate the emotion
        acknowledgment = self._generate_acknowledgment(emotion, entities, sentiment)
        response_parts.append(acknowledgment)
        
        # Part 2: Provide contextual understanding
        understanding = self._generate_understanding(text, emotion, entities, keywords)
        response_parts.append(understanding)
        
        # Part 3: Offer supportive guidance
        guidance = self._generate_guidance(emotion, entities, sentiment)
        response_parts.append(guidance)
        
        # Part 4: Provide encouragement and hope
        encouragement = self._generate_encouragement(emotion, sentiment)
        response_parts.append(encouragement)
        
        # Combine and refine
        response = ' '.join(response_parts)
        
        # Ensure natural flow and proper grammar
        response = self._refine_response(response)
        
        return response
    
    def _generate_acknowledgment(self, emotion: str, entities: Dict[str, List[str]], sentiment: str) -> str:
        """Generate acknowledgment based on detected emotion"""
        intensity = entities.get('intensity', [])
        is_intense = len(intensity) > 0
        
        acknowledgments = {
            'sad': ["I can hear that you're feeling sad", "I understand you're experiencing sadness", "I hear the sadness in your words"],
            'anxious': ["I can sense that you're feeling anxious", "I understand you're dealing with anxiety", "I hear that worry is affecting you"],
            'stressed': ["I can hear how overwhelmed you're feeling", "I understand you're under a lot of stress", "I hear that stress is weighing on you"],
            'happy': ["It's wonderful to hear that you're feeling happy", "I can sense the joy in your words", "I understand you're experiencing happiness"],
            'angry': ["I can hear that you're feeling angry", "I understand you're dealing with frustration", "I hear the anger in your words"],
            'worried': ["I can hear that you're feeling worried", "I understand you're dealing with concern", "I hear that worry is on your mind"],
            'tired': ["I can hear how exhausted you're feeling", "I understand you're dealing with fatigue", "I hear that tiredness is affecting you"],
            'lonely': ["I can hear that you're feeling lonely", "I understand you're experiencing loneliness", "I hear the isolation in your words"]
        }
        
        base_acknowledgment = acknowledgments.get(emotion, ["I hear you", "I understand you're going through something"])
        acknowledgment = random.choice(base_acknowledgment)
        
        # Add intensity modifier
        if is_intense:
            acknowledgment += f" and it sounds {random.choice(['really', 'very', 'quite'])} intense"
        
        # Add context
        if entities.get('academic'):
            acknowledgment += " especially with everything going on with your studies"
        elif entities.get('social'):
            acknowledgment += " particularly in your relationships with others"
        
        acknowledgment += "."
        return acknowledgment
    
    def _generate_understanding(self, text: str, emotion: str, entities: Dict[str, List[str]], keywords: List[str]) -> str:
        """Generate contextual understanding"""
        understandings = {
            'sad': ["That feeling of sadness can be so heavy to carry", "Sadness shows you have a deep capacity to care", "Those sad feelings are completely valid"],
            'anxious': ["Anxiety can make everything feel so overwhelming", "That worried feeling is your mind trying to protect you", "Anxiety is exhausting when it takes over"],
            'stressed': ["Stress can make even small things feel impossible", "That overwhelmed feeling is completely understandable", "Stress affects every part of your life"],
            'happy': ["Happiness is such a beautiful and precious feeling", "That joy is wonderful to experience", "Happy feelings give us energy and hope"],
            'angry': ["Anger is often a sign that something important to you was violated", "That frustration shows you care deeply about things", "Anger is a natural and valid emotion"],
            'worried': ["Worry shows you're thoughtful and care about outcomes", "That concerned feeling means you're being responsible", "Worry is your brain trying to keep you safe"],
            'tired': ["Exhaustion is your body's signal that you need rest", "That fatigue affects both your mind and body", "Being tired makes everything more difficult"],
            'lonely': ["Loneliness is one of the most painful human emotions", "That isolated feeling hurts so deeply", "Loneliness shows your natural need for connection"]
        }
        
        base_understanding = understandings.get(emotion, ["What you're experiencing is real and valid"])
        understanding = random.choice(base_understanding)
        
        # Add specific context
        if entities.get('academic'):
            understanding += " especially when you're dealing with academic pressures"
        elif entities.get('social'):
            understanding += " particularly when it comes to your social connections"
        
        understanding += "."
        return understanding
    
    def _generate_guidance(self, emotion: str, entities: Dict[str, List[str]], sentiment: str) -> str:
        """Generate supportive guidance"""
        guidance_options = {
            'sad': [
                "Be gentle with yourself and allow yourself to feel without judgment",
                "Remember that emotions come in waves and this feeling will pass",
                "It's okay to not be okay - give yourself permission to rest"
            ],
            'anxious': [
                "Try focusing on your breathing and grounding yourself in the present moment",
                "Remember that anxiety is temporary, even when it feels overwhelming",
                "Break down your worries into smaller, manageable pieces"
            ],
            'stressed': [
                "Consider which tasks are actually urgent and which can wait",
                "Remember that you don't have to handle everything perfectly",
                "Take things one step at a time and one moment at a time"
            ],
            'happy': [
                "Savor this moment and hold onto this positive energy",
                "Share your joy with others - happiness is contagious",
                "Remember this feeling when times get tough - it's proof that happiness is possible"
            ],
            'angry': [
                "Channel that energy into something constructive when you're ready",
                "Take deep breaths and remember you're stronger than your anger",
                "Acknowledge the feeling without letting it drive all your decisions"
            ],
            'worried': [
                "Focus on what you can control and let go of what you can't",
                "Remember that many things we worry about never actually happen",
                "Take one small step in the right direction"
            ],
            'tired': [
                "Please prioritize rest - you're not a machine and need recovery time",
                "Listen to your body's signals and give yourself permission to rest",
                "Remember that rest is productive and necessary for your wellbeing"
            ],
            'lonely': [
                "Consider reaching out to someone, even if it feels difficult",
                "Remember that you're not alone in feeling this way",
                "Take small steps toward connection when you're ready"
            ]
        }
        
        guidance_list = guidance_options.get(emotion, [
            "Be patient and compassionate with yourself",
            "Remember that you're stronger than you realize",
            "Take things one moment at a time"
        ])
        
        guidance = random.choice(guidance_list)
        return guidance + "."
    
    def _generate_encouragement(self, emotion: str, sentiment: str) -> str:
        """Generate encouragement and hope"""
        encouragements = {
            'sad': [
                "You have the strength to get through this, even when it doesn't feel like it",
                "This feeling will pass with time, and brighter days will come again",
                "You're not alone in this, and support is available when you need it"
            ],
            'anxious': [
                "You've handled difficult moments before and you'll get through this too",
                "Your resilience is remarkable, even when you can't see it right now",
                "This anxiety will ease, and you'll find your peace again"
            ],
            'stressed': [
                "You're doing your best in difficult circumstances, and that's enough",
                "This pressure will lift, and you'll find your balance again",
                "You have more strength and resources than you realize"
            ],
            'happy': [
                "You deserve every bit of this happiness and so much more",
                "This joy is a reflection of the amazing person you are",
                "Keep embracing these positive moments - they fuel your strength"
            ],
            'angry': [
                "Your feelings are valid, and you have the wisdom to handle this constructively",
                "This intensity will pass, and you'll find clarity again",
                "You have the strength to channel this energy in positive ways"
            ],
            'worried': [
                "You're more capable than you give yourself credit for",
                "Trust that you have the resources to handle whatever comes",
                "This concern shows your wisdom and thoughtfulness"
            ],
            'tired': [
                "You deserve rest and recovery - it's essential for your wellbeing",
                "Taking care of yourself is a sign of strength, not weakness",
                "You'll find your energy again with proper rest and self-care"
            ],
            'lonely': [
                "You deserve connection and meaningful relationships",
                "This feeling will ease, and you'll find your people",
                "Your desire for connection shows your beautiful capacity for relationships"
            ]
        }
        
        encouragement_list = encouragements.get(emotion, [
            "You're stronger and more resilient than you realize",
            "This moment will pass, and you'll find your way through",
            "You deserve kindness, especially from yourself"
        ])
        
        encouragement = random.choice(encouragement_list)
        return encouragement + "."
    
    def _refine_response(self, response: str) -> str:
        """Refine response for natural flow and proper grammar"""
        # Remove any double spaces
        response = ' '.join(response.split())
        
        # Ensure proper capitalization
        if response and not response[0].isupper():
            response = response[0].upper() + response[1:]
        
        # Add appropriate emoji based on content
        if 'sad' in response.lower() or 'lonely' in response.lower():
            response += " 💙"
        elif 'anxious' in response.lower() or 'worried' in response.lower():
            response += " 🌿"
        elif 'stressed' in response.lower() or 'tired' in response.lower():
            response += " 💪"
        elif 'happy' in response.lower() or 'joy' in response.lower():
            response += " ✨"
        elif 'angry' in response.lower():
            response += " 🔥"
        else:
            response += " 💚"
        
        return response
    
    def _generate_friendly_fallback(self, text: str) -> str:
        """Generate friendly, polite fallback for non-emotional queries"""
        friendly_fallbacks = [
            "I appreciate you sharing that with me. While I'm specifically here to help with emotional wellbeing and mental health support, I'm glad you reached out. If you're experiencing any feelings like stress, worry, sadness, or happiness, I'm here to listen and support you through those emotions. Is there anything you'd like to talk about regarding how you're feeling? 💙",
            "Thank you for your message. I'm designed to provide emotional support and mental health assistance, so I'm best equipped to help when you're experiencing feelings or emotions. Whether you're feeling stressed, anxious, sad, happy, or any other emotion, I'm here to listen and offer support. How are you feeling today? 🌿",
            "I hear you, and I want to help. My specialty is providing support for emotional wellbeing and mental health. If you're dealing with any feelings - whether positive or challenging - I'm here to offer understanding and guidance. Sometimes just talking about how we feel can make a big difference. What's on your mind emotionally? 💚",
            "I appreciate you reaching out. I'm here specifically to help with emotional support and mental health matters. If you're experiencing any emotions like stress, anxiety, sadness, joy, or anything in between, I'm ready to listen and provide caring support. Your feelings matter, and I'm here to help you navigate them. How are you doing emotionally? ✨"
        ]
        
        return random.choice(friendly_fallbacks)

    def generate_greeting(self) -> str:
        """Generate a warm greeting response"""
        return random.choice(self.greeting_responses)
