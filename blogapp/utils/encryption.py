# blogapp/utils/encryption.py
# Database field encryption utility using Fernet symmetric encryption

from cryptography.fernet import Fernet
from flask import current_app
import base64
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Manages encryption and decryption of sensitive database fields.
    Uses Fernet (symmetric encryption) from the cryptography library.
    """
    
    _cipher = None
    
    @classmethod
    def _get_cipher(cls):
        """Get or create Fernet cipher instance"""
        if cls._cipher is None:
            key = current_app.config.get('ENCRYPTION_MASTER_KEY')
            
            if not key:
                logger.warning("⚠️  ENCRYPTION_MASTER_KEY not set! Using fallback key (NOT SECURE FOR PRODUCTION)")
                # Generate a fallback key (only for development)
                key = Fernet.generate_key().decode()
                logger.warning(f"⚠️  Generated fallback key: {key}")
                logger.warning("⚠️  Please set ENCRYPTION_MASTER_KEY in your .env file!")
            
            # Ensure key is bytes
            if isinstance(key, str):
                key = key.encode()
            
            try:
                cls._cipher = Fernet(key)
            except Exception as e:
                logger.error(f"❌ Failed to initialize encryption cipher: {e}")
                raise ValueError("Invalid encryption key. Please check ENCRYPTION_MASTER_KEY in .env")
        
        return cls._cipher
    
    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """
        Encrypt plaintext string to encrypted string.
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
        """
        if not plaintext:
            return plaintext
        
        try:
            cipher = cls._get_cipher()
            # Convert string to bytes, encrypt, then encode to string
            encrypted_bytes = cipher.encrypt(plaintext.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"❌ Encryption failed: {e}")
            raise
    
    @classmethod
    def decrypt(cls, encrypted_text: str) -> str:
        """
        Decrypt encrypted string back to plaintext.
        
        Args:
            encrypted_text: The encrypted string to decrypt
            
        Returns:
            Decrypted plaintext string
        """
        if not encrypted_text:
            return encrypted_text
        
        try:
            cipher = cls._get_cipher()
            # Convert string to bytes, decrypt, then decode to string
            decrypted_bytes = cipher.decrypt(encrypted_text.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"❌ Decryption failed: {e}")
            # Return original text if decryption fails (might be unencrypted legacy data)
            logger.warning("⚠️  Returning original text (might be unencrypted legacy data)")
            return encrypted_text
    
    @classmethod
    def generate_key(cls) -> str:
        """
        Generate a new encryption key.
        Use this to generate ENCRYPTION_MASTER_KEY for .env file.
        
        Returns:
            Base64-encoded encryption key
        """
        return Fernet.generate_key().decode()


# Convenience functions
def encrypt_field(value: str) -> str:
    """Encrypt a database field value"""
    return EncryptionManager.encrypt(value)


def decrypt_field(value: str) -> str:
    """Decrypt a database field value"""
    return EncryptionManager.decrypt(value)


def generate_encryption_key() -> str:
    """Generate a new encryption key for .env configuration"""
    return EncryptionManager.generate_key()
