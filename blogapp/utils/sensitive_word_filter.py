# blogapp/utils/sensitive_word_filter.py
# Sensitive word filter utility for content moderation

import xml.etree.ElementTree as ET
import os
import re
from flask import current_app


class SensitiveWordFilter:
    """
    Sensitive word filter using Aho-Corasick algorithm for efficient matching.
    Loads sensitive words from XML file and checks user input.
    """
    
    _words = None
    _pattern = None
    
    @classmethod
    def _load_words(cls):
        """Load sensitive words from XML file"""
        if cls._words is not None:
            return
        
        cls._words = set()
        
        # Get XML file path (relative to project root)
        # current_app.root_path points to blogapp directory
        # We need to go up one level to reach project root
        project_root = os.path.dirname(current_app.root_path)
        xml_path = os.path.join(
            project_root,
            'data',
            'xml',
            'dirtywords.xml'
        )
        
        if not os.path.exists(xml_path):
            current_app.logger.warning(f"⚠️  Sensitive words file not found: {xml_path}")
            return
        
        try:
            # Parse XML
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Extract all words
            for word_elem in root.findall('dirtyword'):
                word = word_elem.get('word', '').strip()
                if word:
                    cls._words.add(word.lower())  # Store in lowercase for case-insensitive matching
            
            # Build regex pattern for efficient matching with word boundaries
            if cls._words:
                # Escape special regex characters
                escaped_words = [re.escape(word) for word in cls._words]
                # Use word boundaries \b for English words, but not for Chinese
                # For mixed matching, we check if word contains only ASCII
                patterns = []
                for word in escaped_words:
                    # Check if word is ASCII (English)
                    if all(ord(c) < 128 for c in word.replace('\\', '')):
                        # English word - use flexible boundaries (not just \b)
                        # Match if surrounded by non-letter characters or start/end
                        patterns.append(r'(?<![a-zA-Z])' + word + r'(?![a-zA-Z])')
                    else:
                        # Chinese or mixed - no word boundaries
                        patterns.append(word)
                
                cls._pattern = re.compile('|'.join(patterns), re.IGNORECASE)
            
            current_app.logger.info(f"✅ Loaded {len(cls._words)} sensitive words")
            
        except Exception as e:
            current_app.logger.error(f"❌ Failed to load sensitive words: {e}")
            cls._words = set()
    
    @classmethod
    def contains_sensitive_word(cls, text: str) -> bool:
        """
        Check if text contains any sensitive words.
        
        Args:
            text: The text to check
            
        Returns:
            True if sensitive word found, False otherwise
        """
        if not text:
            return False
        
        cls._load_words()
        
        if not cls._words or not cls._pattern:
            return False
        
        # Use regex for fast matching
        return cls._pattern.search(text) is not None
    
    @classmethod
    def find_sensitive_words(cls, text: str) -> list:
        """
        Find all sensitive words in text.
        
        Args:
            text: The text to check
            
        Returns:
            List of sensitive words found
        """
        if not text:
            return []
        
        cls._load_words()
        
        if not cls._words or not cls._pattern:
            return []
        
        # Find all matches
        matches = cls._pattern.findall(text)
        return list(set(matches))  # Remove duplicates
    
    @classmethod
    def validate_text(cls, text: str, field_name: str = "content") -> tuple:
        """
        Validate text and return result.
        
        Args:
            text: The text to validate
            field_name: Name of the field being validated (for error message)
            
        Returns:
            Tuple of (is_valid: bool, error_message: str or None)
        """
        if not text:
            return True, None
        
        found_words = cls.find_sensitive_words(text)
        
        if found_words:
            # Mask sensitive words in error message
            masked_words = [word[0] + '*' * (len(word) - 1) for word in found_words]
            error_msg = f"{field_name} contains sensitive words: {', '.join(masked_words)}"
            return False, error_msg
        
        return True, None


# Convenience functions
def contains_sensitive_word(text: str) -> bool:
    """Check if text contains sensitive words"""
    return SensitiveWordFilter.contains_sensitive_word(text)


def validate_text(text: str, field_name: str = "content") -> tuple:
    """Validate text and return (is_valid, error_message)"""
    return SensitiveWordFilter.validate_text(text, field_name)


def find_sensitive_words(text: str) -> list:
    """Find all sensitive words in text"""
    return SensitiveWordFilter.find_sensitive_words(text)
