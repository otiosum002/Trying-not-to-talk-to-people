# Setup Requirements and Instructions

## Quick Start Guide

1. **One-Line Installation** (Copy and paste this in your terminal):
```bash
python -m pip install instagram-private-api python-dotenv keyboard pytest pytest-cov
```

## Detailed Library Installation

1. **Core Libraries**
   ```bash
   pip install instagram-private-api==1.6.0  # Instagram API handling
   pip install python-dotenv==0.19.2        # Environment variables
   pip install keyboard==0.13.5             # Keyboard monitoring
   ```

2. **Testing Libraries** (Optional)
   ```bash
   pip install pytest==7.3.1                # Testing framework
   pip install pytest-cov==4.1.0            # Test coverage
   ```

3. **Verify Installation**
   ```bash
   # Check installed packages
   pip list | grep -E "instagram|dotenv|keyboard|pytest"
   ```

## System Requirements

1. **Python Installation**
   - Download Python 3.9 or newer from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Verify installation by running:
     ```bash
     python --version
     ```

2. **Git Installation** (Optional, for cloning)
   - Download from [git-scm.com](https://git-scm.com/downloads)
   - Verify installation:
     ```bash
     git --version
     ```

## Project Setup

1. **Get the Code**
   - Option 1: Clone with Git
     ```bash
     git clone <repository-url>
     cd instagram-bot
     ```
   - Option 2: Download ZIP and extract

2. **Virtual Environment Setup**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Create Environment File**
   - Create a new file named `.env` in the project root
   - Add your Instagram credentials:
     ```env
     INSTAGRAM_USERNAME=your_instagram_username
     INSTAGRAM_PASSWORD=your_instagram_password
     ```

2. **Database Setup**
   - The database will be created automatically on first run
   - Default location: `instagram_bot.db` in project root

## Running the Bot

1. **Start the Bot**
   ```bash
   # Make sure virtual environment is activated
   python run_bot.py
   ```

2. **Verify Operation**
   - You should see:
     ```
     Successfully connected to Instagram
     Bot is running. Press '9' to terminate the bot.
     Starting message monitoring...
     ```

3. **Monitor Operation**
   - Watch console for:
     - New message notifications
     - Response confirmations
     - Any error messages

## Stopping the Bot

1. **Normal Shutdown**
   - Press '9' on your keyboard
   - Wait for confirmation message:
     ```
     Termination key (9) pressed. Shutting down bot...
     Bot shutdown complete
     Cleaning up and saving data...
     Bot terminated successfully
     ```

2. **Emergency Stop**
   - Press Ctrl+C if '9' key doesn't respond
   - Note: This may not clean up properly

## Troubleshooting

1. **Installation Issues**
   ```bash
   # Update pip
   python -m pip install --upgrade pip

   # Clean install
   pip uninstall -r requirements.txt
   pip install -r requirements.txt
   ```

2. **Permission Issues**
   - Windows: Run as Administrator
   - Linux/macOS: Use sudo if needed
     ```bash
     sudo python run_bot.py
     ```

3. **Instagram Connection Issues**
   - Verify credentials in `.env`
   - Check internet connection
   - Ensure account isn't locked/restricted

## Maintenance

1. **Regular Updates**
   ```bash
   git pull  # If using Git
   pip install -r requirements.txt
   ```

2. **Database Backup**
   - Regularly copy `instagram_bot.db`
   - Keep backups in safe location

## Safety Notes

1. Use a development Instagram account first
2. Monitor the bot's activities regularly
3. Keep credentials secure
4. Don't share your `.env` file
5. Respect Instagram's terms of service

## Support

If you encounter issues:
1. Check console output
2. Review error messages
3. Verify all setup steps
4. Check Instagram account status 