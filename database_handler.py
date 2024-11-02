import sqlite3
from typing import List, Tuple, Optional
from datetime import datetime
import json
from collections import defaultdict
from human_response_generator import HumanResponseGenerator
from threading import Lock

class DatabaseHandler:
    def __init__(self, db_path: str = "instagram_bot.db"):
        self.db_path = db_path
        self.conversation_contexts = defaultdict(dict)  # Store context for each user
        self.human_generator = HumanResponseGenerator()
        self.db_lock = Lock()  # Add database lock
        self.setup_database()

    def setup_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Modify conversations table to include context
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    context TEXT,
                    was_helpful BOOLEAN DEFAULT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add table for user contexts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_contexts (
                    user_id TEXT PRIMARY KEY,
                    context TEXT,
                    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    conversation_state TEXT,
                    previous_messages TEXT
                )
            """)
            
            # Add responses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT NOT NULL,
                    response TEXT NOT NULL,
                    context TEXT,
                    usage_count INTEGER DEFAULT 0,
                    success_rate FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check and insert initial responses
            cursor.execute("SELECT COUNT(*) FROM responses")
            if cursor.fetchone()[0] == 0:
                self.insert_initial_responses()
            
            conn.commit()

    def get_user_context(self, user_id: str) -> dict:
        """Retrieve context for a specific user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT context, conversation_state, previous_messages 
                FROM user_contexts 
                WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'context': json.loads(result[0]) if result[0] else {},
                    'state': result[1],
                    'previous_messages': json.loads(result[2]) if result[2] else []
                }
            return {'context': {}, 'state': 'initial', 'previous_messages': []}

    def update_user_context(self, user_id: str, context: dict, state: str, message: str):
        """Update context for a specific user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get previous messages
            previous_messages = self.get_user_context(user_id)['previous_messages']
            previous_messages.append(message)
            if len(previous_messages) > 5:  # Keep only last 5 messages
                previous_messages = previous_messages[-5:]
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_contexts 
                (user_id, context, conversation_state, previous_messages, last_interaction)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                user_id,
                json.dumps(context),
                state,
                json.dumps(previous_messages)
            ))
            conn.commit()

    def find_best_response(self, message: str, user_id: str) -> Tuple[str, int]:
        """Find the best matching response based on message and user context"""
        message = message.lower()
        user_context = self.get_user_context(user_id)
        
        # Determine message intent
        intent = self._determine_intent(message)
        
        # Get human-like response
        human_response = self.human_generator.generate_response(intent, user_context)
        if human_response:
            # Simulate typing delay
            self.human_generator.simulate_typing_delay(human_response)
            # Make response more human-like
            human_response = self.human_generator.humanize_message(human_response, user_context)
            return human_response, 1
            
        # Check if we're in the middle of a conversation flow
        if user_context['state'] != 'initial':
            response = self._handle_conversation_flow(message, user_context)
            if response:
                return response, -1

        # Check for context-specific patterns
        context_patterns = self._get_context_patterns(user_context['previous_messages'])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # First try to match with context
            cursor.execute("""
                SELECT response, id FROM responses 
                WHERE ? LIKE '%' || pattern || '%'
                AND (context IS NULL OR context = ?)
                ORDER BY usage_count DESC, success_rate DESC
                LIMIT 1
            """, (message, json.dumps(user_context['context'])))
            
            result = cursor.fetchone()
            if result:
                return result[0], result[1]
            
            # Fallback to generic response
            return "I understand you're asking about that. Could you provide more details so I can help you better?", -1

    def _handle_conversation_flow(self, message: str, user_context: dict) -> Optional[Tuple[str, int]]:
        """Handle ongoing conversation flows"""
        state = user_context['state']
        context = user_context['context']
        
        if state == 'awaiting_details':
            return "Thanks for providing those details. Let me help you with that.", -1
        elif state == 'follow_up':
            return "Is there anything specific you'd like to know about that?", -1
        
        return None

    def _get_context_patterns(self, previous_messages: List[str]) -> List[str]:
        """Extract context patterns from previous messages"""
        patterns = []
        if previous_messages:
            # Extract key terms from previous messages
            all_text = ' '.join(previous_messages).lower()
            # Add your context extraction logic here
            if 'price' in all_text:
                patterns.append('pricing_context')
            if 'help' in all_text:
                patterns.append('help_context')
        return patterns

    def log_conversation(self, user_id: str, message: str, response: str):
        """Log a conversation interaction with context"""
        with self.db_lock:  # Add thread safety
            user_context = self.get_user_context(user_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversations 
                    (user_id, message, response, context)
                    VALUES (?, ?, ?, ?)
                """, (
                    user_id,
                    message,
                    response,
                    json.dumps(user_context['context'])
                ))
                conn.commit()

    def learn_from_conversations(self):
        """Analyze conversations to generate new response patterns"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Get recent conversations that weren't handled well
            cursor.execute("""
                SELECT message FROM conversations 
                WHERE response LIKE '%still learning%'
                GROUP BY message
                HAVING COUNT(*) >= 3
                LIMIT 10
            """)
            
            common_unhandled = cursor.fetchall()
            for message in common_unhandled:
                # Generate a new generic response for common unhandled messages
                new_response = self._generate_generic_response(message[0])
                if new_response:
                    cursor.execute("""
                        INSERT INTO responses (pattern, response)
                        VALUES (?, ?)
                    """, (message[0].lower(), new_response))
            
            conn.commit()

    def _generate_generic_response(self, message: str) -> Optional[str]:
        """Generate a generic response based on message content"""
        message = message.lower()
        
        # Simple response generation logic
        if any(word in message for word in ['when', 'what time', 'schedule']):
            return "Let me check that information for you. Could you please be more specific?"
        elif any(word in message for word in ['how', 'explain']):
            return "I'd be happy to explain that. Could you please provide more details about what you'd like to know?"
        elif any(word in message for word in ['where', 'location']):
            return "I can help you with location information. What specific location are you looking for?"
        elif '?' in message:
            return "That's a good question. Let me find the most accurate information for you."
        
        return None

    def update_response_stats(self, response_id: int, was_helpful: bool):
        """Update success rate for a response"""
        if response_id == -1:
            return
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE responses 
                SET usage_count = usage_count + 1,
                    success_rate = (success_rate * usage_count + ?) / (usage_count + 1)
                WHERE id = ?
            """, (1 if was_helpful else 0, response_id))
            conn.commit() 

    def _determine_intent(self, message: str) -> str:
        """Determine the intent of the message"""
        message = message.lower()
        
        # Greeting detection
        if any(word in message for word in ['hi', 'hello', 'hey', 'good morning', 'good evening']):
            return 'greeting'
            
        # Pricing queries
        if any(word in message for word in ['price', 'cost', 'how much', 'pricing']):
            return 'pricing'
            
        # Help requests
        if any(word in message for word in ['help', 'support', 'assist', 'how do i']):
            return 'help'
            
        return 'unknown'

    def insert_initial_responses(self):
        """Insert initial response patterns"""
        initial_responses = [
            ("hello", "Hey there! How can I help you today?"),
            ("hi", "Hi! What can I do for you?"),
            ("help", "I'd be happy to help! What do you need assistance with?"),
            ("thank", "You're welcome! Is there anything else you need?"),
            ("bye", "Take care! Have a great day!"),
            ("price", "I can help you with pricing. What specific service are you interested in?"),
            ("cost", "Let me help you with the costs. What would you like to know about?"),
            ("how", "I'd be happy to explain. What would you like to know more about?"),
            ("where", "I can help you with location information. What are you looking for?"),
            ("when", "Let me check the timing for you. What specifically would you like to know?")
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO responses (pattern, response) VALUES (?, ?)",
                initial_responses
            )
            conn.commit()