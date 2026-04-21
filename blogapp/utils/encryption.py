# blogapp/utils/encryption.py
from cryptography.fernet import Fernet
from flask import current_app
import base64
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    """数据库字段加密管理器，基于 Fernet 对称加密"""
    
    _cipher = None
    
    @classmethod
    def _get_cipher(cls):
        if cls._cipher is None:
            key = current_app.config.get('ENCRYPTION_MASTER_KEY')
            
            if not key:
                logger.warning("未设置加密密钥")
                key = Fernet.generate_key().decode()
                logger.warning(f"临时密钥: {key}")
            
            if isinstance(key, str):
                key = key.encode()
            
            try:
                cls._cipher = Fernet(key)
            except Exception as e:
                logger.error(f"密钥初始化失败: {e}")
                raise ValueError("密钥格式错误")
        
        return cls._cipher
    
    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """加密文本"""
        if not plaintext:
            return plaintext
        
        try:
            cipher = cls._get_cipher()
            encrypted_bytes = cipher.encrypt(plaintext.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"加密失败: {e}")
            raise
    
    @classmethod
    def decrypt(cls, encrypted_text: str) -> str:
        """解密文本"""
        if not encrypted_text:
            return encrypted_text
        
        try:
            cipher = cls._get_cipher()
            decrypted_bytes = cipher.decrypt(encrypted_text.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"解密失败: {e}")
            logger.warning("返回原始数据")
            return encrypted_text
    
    @classmethod
    def generate_key(cls) -> str:
        """生成新密钥"""
        return Fernet.generate_key().decode()


def encrypt_field(value: str) -> str:
    return EncryptionManager.encrypt(value)


def decrypt_field(value: str) -> str:
    return EncryptionManager.decrypt(value)


def generate_encryption_key() -> str:
    return EncryptionManager.generate_key()
