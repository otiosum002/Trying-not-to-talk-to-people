# Instagram Auto-Response Bot

A sophisticated Instagram bot that handles direct messages with human-like responses. Features context-aware conversations, natural typing patterns, and automatic learning from interactions.

## 🌟 Features

- 🤖 Automated DM responses with human-like behavior
- 💬 Context-aware conversations
- ⌨️ Natural typing patterns and delays
- 📝 Conversation memory and learning
- 🔄 Automatic message monitoring
- ⚡ Smart rate limiting
- 🛑 Easy termination (press '9')
- 🔒 Thread-safe operations
- 📊 Response success tracking

## 🚀 Quick Start

1. **Clone and Setup**
```bash
git clone <repository-url>
cd instagram-bot
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

2. **Configure**
```bash
# Create .env file and add your credentials
echo "INSTAGRAM_USERNAME=your_username" > .env
echo "INSTAGRAM_PASSWORD=your_password" >> .env
```

3. **Run**
```bash
python run_bot.py
```

## 📋 Requirements

- Python 3.9+
- Instagram account
- Required packages:
  - instagram-private-api==1.6.0
  - python-dotenv==0.19.2
  - keyboard==0.13.5

## 🔧 Configuration

### Environment Variables (.env)
```env
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
```

### Database
- SQLite database (auto-created)
- Stores:
  - Conversation history
  - User contexts
  - Response patterns
  - Success metrics

## 🤖 Bot Behavior

### Message Handling
- Detects message intent
- Maintains conversation context
- Generates human-like responses
- Simulates typing patterns
- Uses natural language variations

### Rate Limiting
- 1 message per second maximum
- Natural typing delays
- Random response timing
- Automatic cooldown periods

### Learning Capability
- Learns from conversations
- Adapts responses based on success
- Maintains context per user
- Improves over time

## 🎮 Controls

### Starting
```bash
python run_bot.py
```

### Monitoring
Watch for:
- Connection status
- Message notifications
- Response confirmations
- Error messages

### Stopping
- Press '9' for clean shutdown
- Ctrl+C for emergency stop

## 🔒 Safety Features

1. Rate limiting
2. Thread safety
3. Error handling
4. Safe shutdown
5. Data persistence
6. Credential protection

## 🛠️ Development

### Testing
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=.
```

### Project Structure
```
instagram-bot/
├── run_bot.py              # Entry point
├── instagram_api.py        # API handling
├── database_handler.py     # Data management
├── human_response_generator.py  # Response generation
├── requirements.txt        # Dependencies
├── .env                   # Configuration
└── tests/                 # Test files
```

## ⚠️ Important Notes

1. Use a development Instagram account first
2. Monitor the bot's activities
3. Keep credentials secure
4. Respect Instagram's terms of service
5. Regular database backups recommended

## 🔍 Troubleshooting

### Common Issues
1. Connection errors
   - Check internet connection
   - Verify credentials
   - Check account status

2. Rate limiting
   - Bot handles automatically
   - Check console for warnings

3. Authentication issues
   - Verify .env configuration
   - Check account status
   - Disable 2FA for testing

## 📝 License

[Your License Here]

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📮 Support

For issues:
- Check existing issues
- Create detailed bug reports
- Include console output
- Describe steps to reproduce

## 📢 Disclaimer

This bot is for educational purposes. Use responsibly and in accordance with Instagram's terms of service.