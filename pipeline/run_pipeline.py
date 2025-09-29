#!/usr/bin/env python3
"""
Bit-by-Bit Newsletter Pipeline Runner - Restructured Version
Main script to execute the pipeline steps with new modular structure.
"""

import sys
import argparse
from pathlib import Path

# Add pipeline to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import initialize_logger, load_pipeline_config
from src.data_collection import RSSGatheringStep, GitHubTrendingCollector, StockDataCollector
from src.processing import (
    ContentFilteringStep, AdDetectionStep, LLMQualityScoringStep, 
    DeduplicationStep, ArticlePrioritizationStep, SummarizationStep, 
    NewsletterGenerationStep
)
from src.gridding import ComponentPlacer
from src.database import DatabaseWriter


def main():
    """Main pipeline execution function."""
    parser = argparse.ArgumentParser(description='Run Bit-by-Bit Newsletter Pipeline - Restructured')
    parser.add_argument('--config', default='config/pipeline_config.json',
                       help='Path to pipeline configuration file')
    parser.add_argument('--step', choices=[
        'data_collection', 'processing', 'gridding', 'database', 'all'
    ], default='all', help='Specific step to run or all steps')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    try:
        # Initialize logging
        logger = initialize_logger(args.config)
        if args.verbose:
            logger.logger.setLevel('DEBUG')
        
        logger.info("🚀 Starting Bit-by-Bit Newsletter Pipeline - Restructured")
        logger.info(f"Configuration: {args.config}")
        logger.info(f"Step: {args.step}")
        
        # Load configuration
        config_loader = load_pipeline_config(args.config)
        logger.info("Pipeline configuration loaded successfully")
        
        # Initialize components
        rss_gatherer = RSSGatheringStep(config_loader)
        github_collector = GitHubTrendingCollector(config_loader)
        stock_collector = StockDataCollector(config_loader)
        component_placer = ComponentPlacer(config_loader)
        database_writer = DatabaseWriter(config_loader)
        
        # Execute steps
        if args.step == 'all' or args.step == 'data_collection':
            logger.info("📡 Executing data collection step")
            
            # Collect RSS data
            logger.info("  📰 Collecting RSS data...")
            rss_result = rss_gatherer.execute()
            if rss_result['success']:
                logger.info(f"  ✅ RSS: {rss_result['articles_collected']} articles collected")
            else:
                logger.error(f"  ❌ RSS collection failed: {rss_result.get('error')}")
                return 1
            
            # Collect GitHub data
            logger.info("  🐙 Collecting GitHub trending data...")
            github_result = github_collector.collect()
            if github_result['success']:
                logger.info(f"  ✅ GitHub: {github_result['collected_count']} repositories collected")
            else:
                logger.error(f"  ❌ GitHub collection failed: {github_result.get('error')}")
                return 1
            
            # Collect stock data
            logger.info("  📈 Collecting stock data...")
            stock_result = stock_collector.collect()
            if stock_result['success']:
                logger.info(f"  ✅ Stocks: {stock_result['collected_count']} stocks collected")
            else:
                logger.error(f"  ❌ Stock collection failed: {stock_result.get('error')}")
                return 1
        
        if args.step == 'all' or args.step == 'processing':
            logger.info("⚙️ Executing processing step")
            # TODO: Implement processing pipeline with existing steps
            logger.info("  📝 Processing step - using existing pipeline steps")
        
        if args.step == 'all' or args.step == 'gridding':
            logger.info("🎯 Executing gridding step")
            # TODO: Implement component placement
            logger.info("  📐 Gridding step - component placement")
        
        if args.step == 'all' or args.step == 'database':
            logger.info("💾 Executing database step")
            # TODO: Implement database operations
            logger.info("  🗄️ Database step - data persistence")
        
        logger.info("✅ Pipeline execution completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Pipeline execution interrupted by user")
        return 130
    except Exception as e:
        logger.critical(f"Pipeline execution failed: {e}", exception=e)
        return 1


if __name__ == '__main__':
    sys.exit(main())