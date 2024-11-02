import pytest
import sqlite3
import json
from database_handler import DatabaseHandler
from datetime import datetime

@pytest.fixture
def db_handler():
    """Create a temporary database handler for testing"""
    handler = DatabaseHandler(db_path=":memory:")  # Use in-memory SQLite database
    return handler

def test_database_initialization(db_handler):
    """Test if database tables are created correctly"""
    with sqlite3.connect(db_handler.db_path) as conn:
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND (name='conversations' OR name='user_contexts')
        """)
        tables = cursor.fetchall()
        assert len(tables) == 2

def test_user_context_management(db_handler):
    """Test user context creation and retrieval"""
    user_id = "test_user_123"
    
    # Test initial context
    initial_context = db_handler.get_user_context(user_id)
    assert initial_context['state'] == 'initial'
    assert initial_context['context'] == {}
    assert initial_context['previous_messages'] == []
    
    # Test context update
    test_context = {'topic': 'pricing'}
    test_state = 'awaiting_details'
    test_message = "What are your prices?"
    
    db_handler.update_user_context(user_id, test_context, test_state, test_message)
    
    updated_context = db_handler.get_user_context(user_id)
    assert updated_context['state'] == test_state
    assert updated_context['context']['topic'] == 'pricing'
    assert test_message in updated_context['previous_messages']

def test_conversation_logging(db_handler):
    """Test conversation logging functionality"""
    user_id = "test_user_456"
    test_message = "Hello there"
    test_response = "Hi! How can I help you?"
    
    db_handler.log_conversation(user_id, test_message, test_response)
    
    with sqlite3.connect(db_handler.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE user_id = ?", (user_id,))
        conversation = cursor.fetchone()
        
        assert conversation is not None
        assert conversation[1] == user_id
        assert conversation[2] == test_message
        assert conversation[3] == test_response

def test_response_generation(db_handler):
    """Test response generation and matching"""
    message = "What time do you open?"
    user_id = "test_user_789"
    
    response, response_id = db_handler.find_best_response(message, user_id)
    assert response is not None
    assert isinstance(response, str)

def test_context_patterns(db_handler):
    """Test context pattern extraction"""
    previous_messages = [
        "What are your prices?",
        "I need help with something",
        "Can you explain this?"
    ]
    
    patterns = db_handler._get_context_patterns(previous_messages)
    assert 'pricing_context' in patterns
    assert 'help_context' in patterns

def test_conversation_flow(db_handler):
    """Test conversation flow handling"""
    user_id = "test_user_101"
    context = {'topic': 'support'}
    state = 'follow_up'
    message = "Yes, I need help with login"
    
    db_handler.update_user_context(user_id, context, state, message)
    user_context = db_handler.get_user_context(user_id)
    
    response = db_handler._handle_conversation_flow(message, user_context)
    assert response is not None

def test_learning_mechanism(db_handler):
    """Test the learning mechanism"""
    # Insert some test conversations with unhandled responses
    with sqlite3.connect(db_handler.db_path) as conn:
        cursor = conn.cursor()
        for _ in range(3):
            cursor.execute("""
                INSERT INTO conversations (user_id, message, response)
                VALUES (?, ?, ?)
            """, ("test_user", "when do you open", "I'm still learning how to respond to that."))
        conn.commit()
    
    db_handler.learn_from_conversations()
    
    # Check if a new response pattern was generated
    response, _ = db_handler.find_best_response("when do you open", "test_user")
    assert "still learning" not in response.lower() 