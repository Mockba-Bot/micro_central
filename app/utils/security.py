from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

# Load environment variables from the specified .env file
load_dotenv(dotenv_path=".env.micro.central")

# Load or generate the key
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")  # Store this securely in your .env file

if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY not found in environment variables!")

cipher = Fernet(ENCRYPTION_KEY)

def encrypt(data: str) -> str:
    """Encrypts a string."""
    if data is None:
        return None
    return cipher.encrypt(data.encode()).decode()

def decrypt(data: str) -> str:
    """Decrypts a string."""
    if data is None:
        return None
    return cipher.decrypt(data.encode()).decode()
