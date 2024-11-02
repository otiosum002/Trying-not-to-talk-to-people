from instagram_api import InstagramMessageAPI

def test_connection():
    try:
        bot = InstagramMessageAPI()
        print("✅ Connection successful!")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 