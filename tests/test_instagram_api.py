import pytest
from unittest.mock import Mock, patch
from instagram_api import InstagramMessageAPI

@pytest.fixture
def mock_api():
    """Create a mock Instagram API"""
    with patch('instagram_api.Client') as mock_client:
        api = InstagramMessageAPI()
        api.api = mock_client
        return api

def test_connection(mock_api):
    """Test Instagram connection"""
    assert mock_api.api is not None
    assert mock_api.db is not None

def test_message_handling(mock_api):
    """Test message handling functionality"""
    test_message = {
        'thread_id': 'test_thread',
        'user_id': 'test_user',
        'username': 'test_username',
        'message': 'Hello',
        'timestamp': '1234567890'
    }
    
    # Mock send_message method
    mock_api.send_message = Mock(return_value=True)
    
    # Handle the message
    mock_api.handle_message(test_message)
    
    # Verify that send_message was called
    mock_api.send_message.assert_called_once()

def test_context_update(mock_api):
    """Test context updating"""
    user_id = "test_user"
    message = "what are your prices?"
    current_context = {'context': {}, 'state': 'initial', 'previous_messages': []}
    
    mock_api._update_context(user_id, message, current_context)
    
    updated_context = mock_api.db.get_user_context(user_id)
    assert updated_context['state'] == 'awaiting_details'
    assert updated_context['context'].get('topic') == 'pricing'

@patch('time.sleep', return_value=None)
def test_message_loop(mock_sleep, mock_api):
    """Test message monitoring loop"""
    # Mock get_pending_messages to return one message then raise KeyboardInterrupt
    mock_api.get_pending_messages = Mock(side_effect=[
        [{'thread_id': '1', 'user_id': '1', 'message': 'test', 'username': 'test', 'timestamp': '123'}],
        KeyboardInterrupt
    ])
    
    # Mock handle_message
    mock_api.handle_message = Mock()
    
    # Run the message loop
    try:
        mock_api.start_message_loop(check_interval=1)
    except KeyboardInterrupt:
        pass
    
    # Verify that handle_message was called
    mock_api.handle_message.assert_called_once()

def test_pending_messages_fetch(mock_api):
    """Test fetching pending messages"""
    # Mock the Instagram API response
    mock_api.api.direct_v2_inbox.return_value = {
        'inbox': {
            'threads': [
                {
                    'thread_id': '123',
                    'pending': True,
                    'users': [{'pk': '456', 'username': 'test_user'}],
                    'items': [
                        {'text': 'Hello', 'timestamp': '123456789'}
                    ]
                }
            ]
        }
    }
    
    messages = mock_api.get_pending_messages()
    assert len(messages) == 1
    assert messages[0]['thread_id'] == '123'
    assert messages[0]['message'] == 'Hello'

def test_error_handling(mock_api):
    """Test error handling in message sending"""
    # Mock API to raise an exception
    mock_api.api.direct_v2_send.side_effect = Exception("Test error")
    
    result = mock_api.send_message("test_thread", "test message")
    assert result is False 