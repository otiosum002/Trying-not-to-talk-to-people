from instagram_api import InstagramMessageAPI
import keyboard
import threading
import sys
import time

def check_for_exit():
    """Monitor for '9' key press"""
    keyboard.wait('9')
    print("\nTermination key (9) pressed. Shutting down bot...")
    sys.exit(0)

def main():
    bot = None
    try:
        bot = InstagramMessageAPI()
        print("Bot is running. Press '9' to terminate the bot.")
        
        exit_thread = threading.Thread(target=check_for_exit, daemon=True)
        exit_thread.start()
        
        bot.start_message_loop()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except SystemExit:
        print("Bot shutdown complete")
    except Exception as e:
        print(f"Bot stopped due to error: {str(e)}")
    finally:
        if bot:
            print("Cleaning up and saving data...")
            time.sleep(1)
            print("Bot terminated successfully")

if __name__ == "__main__":
    main() 