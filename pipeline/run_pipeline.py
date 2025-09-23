#!/usr/bin/env python3
"""
Bit-by-Bit Newsletter Pipeline Runner
Main script to execute the pipeline steps.
"""

import sys
import argparse
from pathlib import Path

# Add pipeline to Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils import initialize_logger, load_pipeline_config
from steps import RSSGatheringStep


def main():
    """Main pipeline execution function."""
    parser = argparse.ArgumentParser(description='Run Bit-by-Bit Newsletter Pipeline')
    parser.add_argument('--config', default='pipeline/config/pipeline_config.json',
                       help='Path to pipeline configuration file')
    parser.add_argument('--step', choices=['rss_gathering', 'all'], default='all',
                       help='Specific step to run or all steps')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    try:
        # Initialize logging
        logger = initialize_logger(args.config)
        if args.verbose:
            logger.logger.setLevel('DEBUG')
        
        logger.info("Starting Bit-by-Bit Newsletter Pipeline")
        logger.info(f"Configuration: {args.config}")
        logger.info(f"Step: {args.step}")
        
        # Load configuration
        config_loader = load_pipeline_config(args.config)
        logger.info("Pipeline configuration loaded successfully")
        
        # Execute steps
        if args.step == 'all' or args.step == 'rss_gathering':
            logger.info("Executing RSS gathering step")
            rss_step = RSSGatheringStep(config_loader)
            result = rss_step.execute()
            
            if result['success']:
                logger.info(f"RSS gathering completed successfully: {result['articles_collected']} articles collected")
            else:
                logger.error(f"RSS gathering failed: {result.get('error', 'Unknown error')}")
                return 1
        
        logger.info("Pipeline execution completed")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Pipeline execution interrupted by user")
        return 130
    except Exception as e:
        logger.critical(f"Pipeline execution failed: {e}", exception=e)
        return 1


if __name__ == '__main__':
    sys.exit(main())
