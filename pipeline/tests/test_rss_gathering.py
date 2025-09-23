#!/usr/bin/env python3
"""
Test script for RSS gathering step.
"""

import sys
from pathlib import Path

# Add pipeline to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import initialize_logger, load_pipeline_config
from steps import RSSGatheringStep


def test_rss_gathering():
    """Test the RSS gathering step."""
    print("🧪 Testing RSS Gathering Step")
    
    try:
        # Initialize logging
        logger = initialize_logger('pipeline/config/pipeline_config.json')
        logger.info("Starting RSS gathering test")
        
        # Load configuration
        config_loader = load_pipeline_config('pipeline/config/pipeline_config.json')
        
        # Create and execute RSS gathering step
        rss_step = RSSGatheringStep(config_loader)
        result = rss_step.execute()
        
        # Print results
        print(f"\n📊 Test Results:")
        print(f"   Success: {result['success']}")
        print(f"   Articles Collected: {result.get('articles_collected', 0)}")
        print(f"   Feeds Processed: {result.get('feeds_processed', 0)}")
        print(f"   Feeds Successful: {result.get('feeds_successful', 0)}")
        print(f"   Feeds Failed: {result.get('feeds_failed', 0)}")
        print(f"   Output File: {result.get('output_file', 'None')}")
        
        if result['success']:
            print("\n✅ RSS gathering test completed successfully!")
            return True
        else:
            print(f"\n❌ RSS gathering test failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        return False


if __name__ == '__main__':
    success = test_rss_gathering()
    sys.exit(0 if success else 1)
