from instagram_private_api import Client, ClientCompatPatch
from typing import Dict, Any
import os
from dotenv import load_dotenv
import time
import json
from database_handler import DatabaseHandler
import random
from threading import Lock
from human_response_generator import HumanResponseGenerator

class RateLimiter:
    def __init__(self, calls_per_second=1):
        self.calls_per_second = calls_per_second
        self.last_call = 0
        self.lock = Lock()

    def wait(self):
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_call
            if time_since_last < (1.0 / self.calls_per_second):
                time.sleep((1.0 / self.calls_per_second) - time_since_last)
            self.last_call = time.time()

class InstagramMessageAPI:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.api = None
        self.db = DatabaseHandler()
        self.last_message_time = 0
        self.message_lock = Lock()
        self.human_generator = HumanResponseGenerator()
        self.rate_limiter = RateLimiter(calls_per_second=1)
        self.connect()

    def connect(self):
        """Establish connection to Instagram"""
        try:
            self.api = Client(self.username, self.password)
            print("Successfully connected to Instagram")
        except Exception as e:
            print(f"Failed to connect to Instagram: {str(e)}")
            raise

    def get_pending_messages(self) -> list:
        """Fetch pending direct messages"""
        try:
            inbox = self.api.direct_v2_inbox()
            threads = inbox['inbox']['threads']
            pending_messages = []
            
            for thread in threads:
                if thread['pending']:
                    messages = thread['items']
                    for message in messages:
                        pending_messages.append({
                            'thread_id': thread['thread_id'],
                            'user_id': thread['users'][0]['pk'],
                            'username': thread['users'][0]['username'],
                            'message': message['text'] if 'text' in message else '',
                            'timestamp': message['timestamp']
                        })
            
            return pending_messages
        except Exception as e:
            print(f"Error fetching messages: {str(e)}")
            return []

    def send_message(self, thread_id: str, message: str) -> bool:
        """Send a message with rate limiting"""
        try:
            self.rate_limiter.wait()
            with self.message_lock:
                current_time = time.time()
                time_since_last = current_time - self.last_message_time
                
                if time_since_last < 1:
                    time.sleep(1 - time_since_last)

                # Start typing indicator
                self.api.direct_v2_indicate_activity(
                    thread_id=thread_id,
                    activity_indicator_id=1
                )

                # Simulate typing
                char_count = len(message)
                typing_duration = char_count / random.uniform(30, 80)
                time.sleep(typing_duration)

                # Send message
                self.api.direct_v2_send(
                    text=message,
                    thread_ids=[thread_id]
                )

                self.last_message_time = time.time()

                # Stop typing indicator after a short delay
                time.sleep(random.uniform(0.5, 1.5))
                self.api.direct_v2_indicate_activity(
                    thread_id=thread_id,
                    activity_indicator_id=0
                )

                print(f"Message sent: {message[:30]}...")
                return True

        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False

    def handle_message(self, message_data: Dict[str, Any]) -> None:
        """Handle incoming messages"""
        message_text = message_data['message'].lower()
        thread_id = message_data['thread_id']
        user_id = message_data['user_id']
        
        user_context = self.db.get_user_context(user_id)
        self._update_context(user_id, message_text, user_context)
        
        response, response_id = self.db.find_best_response(message_text, user_id)
        self.db.log_conversation(user_id, message_text, response)
        
        success = self.send_message(thread_id, response)
        self.db.update_response_stats(response_id, success)
        
        if time.time() % 3600 < 60:  # Learn every hour
            self.db.learn_from_conversations()

    def _update_context(self, user_id: str, message: str, current_context: dict):
        """Update user context"""
        context = current_context['context']
        state = 'initial'
        
        if 'price' in message.lower():
            context['topic'] = 'pricing'
            state = 'awaiting_details'
        elif 'help' in message.lower():
            context['topic'] = 'support'
            state = 'follow_up'
        elif any(word in message.lower() for word in ['thanks', 'thank you', 'bye']):
            state = 'closing'
        
        self.db.update_user_context(user_id, context, state, message)

    def start_message_loop(self, check_interval: int = 60):
        """Start the message monitoring loop"""
        print("Starting message monitoring...")
        consecutive_errors = 0
        
        while True:
            try:
                messages = self.get_pending_messages()
                for message in messages:
                    self.handle_message(message)
                consecutive_errors = 0  # Reset error count on success
                time.sleep(check_interval)
                
            except Exception as e:
                consecutive_errors += 1
                print(f"Error in message loop: {str(e)}")
                
                # Attempt reconnection if multiple errors occur
                if consecutive_errors >= 3:
                    print("Multiple errors detected. Attempting to reconnect...")
                    try:
                        self.connect()
                        consecutive_errors = 0
                    except Exception as conn_error:
                        print(f"Reconnection failed: {str(conn_error)}")
                        
                time.sleep(min(check_interval * consecutive_errors, 300))  # Exponential backoff up to 5 minutes