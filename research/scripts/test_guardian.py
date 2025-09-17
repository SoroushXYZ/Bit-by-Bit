#!/usr/bin/env python3
"""
Test script for Guardian API data collection
Run this to test your API key and see what data we can collect
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from research.scripts.guardian_collector import GuardianCollector, test_guardian_api

def main():
    print("🚀 Bit-by-Bit Guardian API Test")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ No .env file found!")
        print("📝 Please create a .env file with your Guardian API key:")
        print("   GUARDIAN_API_KEY=your_api_key_here")
        print("\n💡 You can copy env.example to .env and add your key")
        return
    
    # Run the test
    test_guardian_api()
    
    print("\n" + "=" * 50)
    print("🎯 Next steps:")
    print("1. Add your Guardian API key to .env file")
    print("2. Run this script again to test")
    print("3. Check the data quality and relevance")
    print("4. Adjust search terms and filters as needed")

if __name__ == "__main__":
    main()
