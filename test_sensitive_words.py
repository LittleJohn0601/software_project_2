#!/usr/bin/env python3
# test_sensitive_words.py
# Test sensitive word filter functionality

from blogapp import create_app
from blogapp.utils.sensitive_word_filter import (
    contains_sensitive_word,
    find_sensitive_words,
    validate_text
)


def test_sensitive_words():
    """Test sensitive word detection"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🔍 Sensitive Word Filter Test")
        print("=" * 60)
        
        # Test cases
        test_cases = [
            # (text, should_contain_sensitive_word, description)
            ("Hello World Factory", False, "Normal factory name"),
            ("北京钢铁厂", False, "Normal Chinese factory name"),
            ("Fuck Factory", True, "English profanity"),
            ("毛泽东工厂", True, "Chinese sensitive word"),
            ("test@example.com", False, "Normal email"),
            ("fuck@example.com", True, "Email with profanity"),
            ("MyPassword123", False, "Normal password"),
            ("nazi123", True, "Password with sensitive word"),
            ("上海浦东新区", False, "Normal location"),
            ("terrorist location", True, "Location with sensitive word"),
            ("Steel Manufacturing", False, "Normal industry type"),
            ("drug industry", True, "Industry with sensitive word"),
        ]
        
        passed = 0
        failed = 0
        
        for text, should_fail, description in test_cases:
            has_sensitive = contains_sensitive_word(text)
            found_words = find_sensitive_words(text)
            is_valid, error_msg = validate_text(text, "测试字段")
            
            # Check if result matches expectation
            if should_fail:
                if has_sensitive and not is_valid:
                    print(f"✅ PASS - {description}")
                    print(f"   Text: '{text}'")
                    print(f"   Found: {found_words}")
                    print(f"   Error: {error_msg}")
                    passed += 1
                else:
                    print(f"❌ FAIL - {description}")
                    print(f"   Text: '{text}'")
                    print(f"   Expected: Should contain sensitive word")
                    print(f"   Got: has_sensitive={has_sensitive}, is_valid={is_valid}")
                    failed += 1
            else:
                if not has_sensitive and is_valid:
                    print(f"✅ PASS - {description}")
                    print(f"   Text: '{text}'")
                    passed += 1
                else:
                    print(f"❌ FAIL - {description}")
                    print(f"   Text: '{text}'")
                    print(f"   Expected: Should NOT contain sensitive word")
                    print(f"   Got: has_sensitive={has_sensitive}, found={found_words}")
                    failed += 1
            
            print()
        
        print("=" * 60)
        print(f"📊 Test Results: {passed}/{passed + failed} passed")
        if failed == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ {failed} test(s) failed")
        print("=" * 60)


if __name__ == '__main__':
    test_sensitive_words()
