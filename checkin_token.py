#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cookie Token Extraction Helper for GitHub Actions (Multi-Account Support)

This script extracts individual cookie tokens from multiple full cookie strings
(separated by newlines) and saves them in the required JSON format for the check-in script.

Usage:
    python get_tokens_helper.py
    
For GitHub Actions: Set LEAFLOW_COOKIES environment variable with each account's cookie on a new line.
For local testing: Use the hardcoded multi-line cookie string in this file.
"""

import json
import os
from urllib.parse import unquote

def parse_cookie_string(cookie_string):
    """
    Parse a single cookie string into a dictionary.
    
    Args:
        cookie_string: Raw cookie string from browser for one account.
        
    Returns:
        Dictionary of cookie name-value pairs.
    """
    cookies = {}
    
    # Split by semicolon and process each cookie
    for cookie in cookie_string.split(';'):
        cookie = cookie.strip()
        if '=' in cookie:
            # Split only on first = to handle values with =
            name, value = cookie.split('=', 1)
            cookies[name.strip()] = value.strip()
    
    return cookies

def create_config_from_cookies(all_cookies_list):
    """
    Create the configuration structure from a list of parsed cookies.
    
    Args:
        all_cookies_list: A list where each item is a dictionary of cookies for one account.
        
    Returns:
        Configuration dictionary.
    """
    accounts = []
    for cookies in all_cookies_list:
        account_entry = {
            "token_data": {
                "cookies": cookies
            }
        }
        accounts.append(account_entry)

    config = {
        "settings": {
            "log_level": "INFO",
            "retry_delay": 3,
            "timeout": 30,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        },
        "accounts": accounts
    }
    
    return config

def main():
    """
    Main function to extract tokens and create config file for multiple accounts.
    """
    
    # For GitHub Actions: Read from environment variable
    multi_cookie_string = os.environ.get('LEAFLOW_COOKIES', '')
    
    # For local testing: Hardcoded multi-line cookie string
    if not multi_cookie_string:
        multi_cookie_string = """
# 在这里粘贴第一个账号的Cookie
cookie_key1=value1; another_key1=value_abc

# 在这里粘贴第二个账号的Cookie
cookie_key2=value2; another_key2=value_xyz
"""
    
    if not multi_cookie_string.strip():
        print("❌ No cookie string provided!")
        print("For GitHub Actions: Set LEAFLOW_COOKIES environment variable")
        print("For local testing: Add cookie strings to this script")
        return False

    # Split the multi-line string into a list of individual cookie strings
    # Filter out any empty lines that might result from extra newlines
    account_cookie_strings = [line.strip() for line in multi_cookie_string.strip().split('\n') if line.strip()]

    if not account_cookie_strings:
        print("❌ Cookie string was provided, but no valid lines found after stripping.")
        return False

    print(f"🚀 Found {len(account_cookie_strings)} account(s) to process.")
    
    all_accounts_cookies = []
    
    # Loop through each account's cookie string
    for i, cookie_string in enumerate(account_cookie_strings):
        print(f"\n📝 Parsing cookies for Account #{i + 1}...")
        
        # Parse the cookie string for the current account
        cookies = parse_cookie_string(cookie_string)
        
        if not cookies:
            print(f"⚠️ Warning: No cookies found for Account #{i + 1}. Skipping.")
            continue

        all_accounts_cookies.append(cookies)
        
        # Display found cookies for verification
        print(f"✅ Found {len(cookies)} cookies for Account #{i + 1}:")
        for name in list(cookies.keys())[:3]: # Show first 3 cookies for brevity
            value_preview = cookies[name][:20] + "..." if len(cookies[name]) > 20 else cookies[name]
            print(f"  - {name}: {value_preview}")

    # Create configuration from the list of all parsed cookies
    config = create_config_from_cookies(all_accounts_cookies)
    
    # Save to file
    output_file = "config.accounts.json"
    print(f"\n💾 Saving configuration for {len(all_accounts_cookies)} account(s) to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuration saved successfully!")
    print(f"📄 You can now run: python checkin_token.py")
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
