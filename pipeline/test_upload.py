#!/usr/bin/env python3
"""
Test script for S3 upload functionality.
"""

import sys
import json
from pathlib import Path

# Add pipeline to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config_loader import ConfigLoader
from src.upload.upload_manager import UploadManager


def test_upload_functionality():
    """Test the upload functionality."""
    print("🧪 Testing S3 Upload Functionality")
    print("=" * 50)
    
    # Initialize components
    config_loader = ConfigLoader()
    upload_manager = UploadManager(config_loader)
    
    # Test 1: Check upload status
    print("\n📊 Upload Status:")
    status = upload_manager.get_upload_status()
    print(json.dumps(status, indent=2))
    
    # Test 2: Validate setup
    print("\n🔍 Validating Upload Setup:")
    validation = upload_manager.validate_upload_setup()
    print(json.dumps(validation, indent=2))
    
    # Test 3: List uploaded runs (if any)
    print("\n📋 Existing Uploaded Runs:")
    runs = upload_manager.list_uploaded_runs()
    if runs:
        for run in runs:
            print(f"  - {run['run_id']}")
    else:
        print("  No uploaded runs found")
    
    # Test 4: Test single file upload (if upload enabled)
    if status['upload_enabled'] and status['s3_client_available']:
        print("\n📁 Testing Single File Upload:")
        
        # Create a test file
        test_file = Path('test_upload.txt')
        test_file.write_text('This is a test file for S3 upload.')
        
        try:
            result = upload_manager.upload_single_file(
                str(test_file),
                'test/test_upload.txt',
                {'test': 'true', 'timestamp': '2025-01-11'}
            )
            print(f"  Upload result: {json.dumps(result, indent=2)}")
        finally:
            # Clean up test file
            if test_file.exists():
                test_file.unlink()
    else:
        print("\n⏭️ Skipping file upload test (upload disabled or S3 not available)")
    
    print("\n✅ Upload functionality test completed!")


if __name__ == "__main__":
    test_upload_functionality()
