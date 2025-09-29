#!/usr/bin/env python3
"""
Test script for content filtering step.
"""

import sys
from pathlib import Path

# Add pipeline to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import initialize_logger, load_pipeline_config
from steps import ContentFilteringStep


def test_content_filtering():
    """Test the content filtering step."""
    print("🧪 Testing Content Filtering Step")
    
    try:
        # Initialize logging
        logger = initialize_logger('pipeline/config/pipeline_config.json')
        logger.info("Starting content filtering test")
        
        # Load configuration
        config_loader = load_pipeline_config('pipeline/config/pipeline_config.json')
        
        # Create and execute content filtering step
        filtering_step = ContentFilteringStep(config_loader)
        result = filtering_step.execute()
        
        # Print results
        print(f"\n📊 Test Results:")
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Articles Input: {result.get('articles_input', 0)}")
            print(f"   Articles Passed: {result.get('articles_passed', 0)}")
            print(f"   Articles Rejected: {result.get('articles_rejected', 0)}")
            print(f"   Pass Rate: {result.get('pass_rate', 0):.1f}%")
            print(f"   Output File: {result.get('output_file', 'None')}")
            
            # Show filter breakdown
            if 'filter_statistics' in result:
                stats = result['filter_statistics']
                print(f"\n📈 Filter Breakdown:")
                for filter_name, breakdown in stats.get('filter_breakdown', {}).items():
                    passed = breakdown.get('passed', 0)
                    rejected = breakdown.get('rejected', 0)
                    total = passed + rejected
                    pass_rate = (passed / total * 100) if total > 0 else 0
                    print(f"   {filter_name}: {passed}/{total} ({pass_rate:.1f}%)")
            
            print("\n✅ Content filtering test completed successfully!")
            return True
        else:
            print(f"\n❌ Content filtering test failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        return False


if __name__ == '__main__':
    success = test_content_filtering()
    sys.exit(0 if success else 1)
