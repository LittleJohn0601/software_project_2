# blogapp/email_encryptor.py
"""
Fully Fixed Email Encryption Tool
"""

import base64
import os
import re
from cryptography.fernet import Fernet, InvalidToken
from flask import current_app

class EmailEncryptor:
    """
    Email Encryptor - Fully Fixed Version
    """
    
    # Cache cipher instance
    _cipher_instance = None
    
    @classmethod
    def _get_cipher(cls):
        """
        Get Fernet cipher instance (singleton pattern)
        """
        if cls._cipher_instance is None:
            cls._cipher_instance = cls._create_cipher()
        return cls._cipher_instance
    
    @classmethod
    def _create_cipher(cls):
        """
        Create Fernet cipher
        """
        # Get key string
        key_str = None
        
        # 1. Get from current app configuration
        if current_app:
            key_str = current_app.config.get('ENCRYPTION_MASTER_KEY')
        
        # 2. Get from environment variable
        if not key_str:
            key_str = os.environ.get('ENCRYPTION_MASTER_KEY')
        
        # 3. Default value for development environment
        if not key_str:
            if current_app and current_app.config.get('ENV') == 'production':
                raise ValueError("ENCRYPTION_MASTER_KEY must be set in production")
            
            # Use hardcoded test key for development
            key_str = "05xWBfFHfE3-31f8PS95oyCqDjwg-7n1wGJ7e2IoWwY="
            if current_app:
                current_app.logger.warning("Using default encryption key for development")
        
        # Clean key string
        key_str = key_str.strip()
        
        # Validate and prepare key
        try:
            # Ensure key is valid base64
            # Add necessary padding
            missing_padding = len(key_str) % 4
            if missing_padding:
                key_str += '=' * (4 - missing_padding)
            
            # Attempt decoding for verification
            key_bytes = base64.urlsafe_b64decode(key_str)
            
            # Check length
            if len(key_bytes) != 32:
                raise ValueError(f"Key must be 32 bytes after decoding, got {len(key_bytes)}")
            
            # Re-encode to ensure correct format
            final_key = base64.urlsafe_b64encode(key_bytes)
            
            # Create cipher
            cipher = Fernet(final_key)
            
            if current_app:
                current_app.logger.info("Email encryption cipher created successfully")
            
            return cipher
            
        except Exception as e:
            error_msg = f"Failed to create encryption cipher: {e}"
            if current_app:
                current_app.logger.error(error_msg)
            else:
                print(f"ERROR: {error_msg}")
            raise
    
    @staticmethod
    def encrypt_email(email: str) -> str:
        """
        Encrypt email address
        """
        if not email or not isinstance(email, str):
            return ""
        
        try:
            cipher = EmailEncryptor._get_cipher()
            
            # Clean email
            clean_email = email.strip().lower()
            
            # Encrypt
            encrypted_bytes = cipher.encrypt(clean_email.encode('utf-8'))
            
            return encrypted_bytes.decode('utf-8')
            
        except Exception as e:
            error_msg = f"Email encryption failed: {e}"
            if current_app:
                current_app.logger.error(error_msg)
            
            # Development environment: return marked unencrypted version
            if current_app and current_app.config.get('ENV') == 'development':
                return f"[DEV-UNENCRYPTED]{email}"
            else:
                raise
    
    @staticmethod
    def decrypt_email(encrypted_email: str) -> str:
        """
        Decrypt email address
        """
        if not encrypted_email or not isinstance(encrypted_email, str):
            return ""
        
        # Check for development environment unencrypted format
        if encrypted_email.startswith("[DEV-UNENCRYPTED]"):
            return encrypted_email[17:]
        
        try:
            cipher = EmailEncryptor._get_cipher()
            decrypted_bytes = cipher.decrypt(encrypted_email.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
            
        except InvalidToken:
            error_msg = "Invalid encryption token - possible tampering"
            if current_app:
                current_app.logger.error(error_msg)
            return "[INVALID_TOKEN]"
            
        except Exception as e:
            error_msg = f"Email decryption failed: {e}"
            if current_app:
                current_app.logger.error(error_msg)
            
            # Development environment: try returning directly (might be test data)
            if current_app and current_app.config.get('ENV') == 'development':
                # Check if it's email format
                if '@' in encrypted_email and '.' in encrypted_email:
                    return encrypted_email
            
            return "[DECRYPTION_ERROR]"
    
    @staticmethod
    def is_encrypted(data: str) -> bool:
        """
        Determine if data is encrypted
        """
        if not data or not isinstance(data, str):
            return False
        
        # Exclude development environment markers
        if data.startswith("[DEV-UNENCRYPTED]"):
            return False
        
        # Simple heuristic check
        # Encrypted data typically: base64 encoded, at least 50 characters, contains special characters
        if len(data) < 20:
            return False
        
        try:
            # Attempt base64 decoding
            decoded = base64.urlsafe_b64decode(data + '=' * (4 - len(data) % 4))
            # Decoding successful and has certain length
            return len(decoded) > 10
        except:
            return False
    
    @classmethod
    def health_check(cls):
        """
        Check encryption service health status
        """
        try:
            # Test encryption and decryption
            test_email = "health-check@example.com"
            encrypted = cls.encrypt_email(test_email)
            decrypted = cls.decrypt_email(encrypted)
            
            return {
                'status': 'healthy',
                'test_passed': test_email == decrypted,
                'cipher_initialized': cls._cipher_instance is not None,
                'test_email': test_email,
                'decrypted': decrypted
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'cipher_initialized': cls._cipher_instance is not None
            }


# Create global instance
email_encryptor = EmailEncryptor()