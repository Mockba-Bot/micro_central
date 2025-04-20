import jwt
from datetime import datetime, timedelta, timezone
from web3 import Web3
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path=".env.micro.central")

# Encryption setup
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY not found in environment variables!")
cipher = Fernet(ENCRYPTION_KEY)

# JWT setup
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 12

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

def create_jwt_token(wallet_address: str) -> str:
    """Create JWT token for authenticated wallet address."""
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        "wallet": wallet_address,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    """Verify JWT token and return payload if valid."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def verify_metamask_signature(wallet_address: str, signature: str, message: str) -> bool:
    """Verify MetaMask signature matches wallet address."""
    message_hash = Web3().keccak(text=f"\x19Ethereum Signed Message:\n{len(message)}{message}")
    try:
        signer = Web3().eth.account.recover_message(
            {'message': message, 'signature': signature}
        )
        return signer.lower() == wallet_address.lower()
    except:
        return False
