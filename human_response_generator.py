import random
import time
from typing import List, Tuple

class HumanResponseGenerator:
    def __init__(self):
        self.emoji_frequency = 0.3
        self.typing_speed = (30, 80)
        
        self.greetings = [
            "Hey there! 👋",
            "Hi! How are you?",
            "Hello! Nice to hear from you",
            "Hey! What can I help you with?",
            "Hi there! How's your day going?"
        ]
        
        self.thinking_phrases = [
            "Let me check that for you...",
            "One moment please...",
            "Looking into this...",
            "Just checking the details...",
            "Give me a second..."
        ]
        
        self.acknowledgments = [
            "I see",
            "Got it",
            "I understand",
            "Makes sense",
            "Ah, okay"
        ]
        
        self.typos = {
            'i': 'u',
            'your': 'youre',
            'there': 'their',
            'hello': 'helo',
            'please': 'plz'
        }

    def simulate_typing_delay(self, message: str):
        char_count = len(message)
        words = message.split()
        
        chars_per_second = random.uniform(self.typing_speed[0], self.typing_speed[1])
        base_delay = char_count / chars_per_second
        
        if len(words) > 5:
            base_delay += random.uniform(0.5, 1.5)
            
        time.sleep(base_delay)

    def humanize_message(self, message: str, context: dict) -> str:
        words = message.split()
        
        if context.get('previous_messages'):
            if random.random() < 0.4:
                message = f"{random.choice(self.acknowledgments)}! {message}"
        
        if len(words) > 8 or '?' in message:
            if random.random() < 0.3:
                message = f"{random.choice(self.thinking_phrases)} {message}"
        
        if random.random() < 0.05:
            for correct, typo in self.typos.items():
                if correct in message.lower() and random.random() < 0.3:
                    message = message.replace(correct, typo)
                    message += f"\n*{correct}"
                    break
        
        return message

    def generate_response(self, intent: str, context: dict) -> str:
        if intent == 'greeting':
            return random.choice(self.greetings)
            
        if intent == 'pricing':
            responses = [
                "The pricing depends on what you're looking for. What specific services interest you?",
                "I can definitely help with pricing! What exactly would you like to know about?",
                "Sure thing! Could you tell me more about what you're interested in? That'll help me give you the right pricing info"
            ]
            return random.choice(responses)
            
        if intent == 'help':
            responses = [
                "I'd love to help! What seems to be the issue?",
                "Of course! What are you having trouble with?",
                "Sure thing! What kind of help do you need?"
            ]
            return random.choice(responses)
            
        return None