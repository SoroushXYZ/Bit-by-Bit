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
from src.processing.github_trending_processing import GitHubTrendingProcessor
from src.gridding import ComponentPlacer
from src.database import DatabaseWriter


def main():
    """Main pipeline execution function."""
    parser = argparse.ArgumentParser(description='Run Bit-by-Bit Newsletter Pipeline - Restructured')
    parser.add_argument('--config', default='config/pipeline_config.json',
                       help='Path to pipeline configuration file')
    parser.add_argument('--step', choices=[
        'data_collection', 'processing', 'gridding', 'database', 'all',
        'content_filtering', 'ad_detection', 'llm_quality_scoring', 
        'deduplication', 'article_prioritization', 'summarization', 'newsletter_generation',
        'github_trending_processing'
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
            
            # Initialize processing steps
            content_filter = ContentFilteringStep(config_loader)
            ad_detector = AdDetectionStep(config_loader)
            llm_scorer = LLMQualityScoringStep(config_loader)
            deduplicator = DeduplicationStep(config_loader)
            prioritizer = ArticlePrioritizationStep(config_loader)
            summarizer = SummarizationStep(config_loader)
            newsletter_gen = NewsletterGenerationStep(config_loader)
            
            # Execute processing pipeline
            logger.info("  🔍 Running content filtering...")
            filter_result = content_filter.execute()
            if not filter_result['success']:
                logger.error(f"  ❌ Content filtering failed: {filter_result.get('error')}")
                return 1
            logger.info(f"  ✅ Content filtering: {filter_result.get('articles_processed', 0)} articles processed")
            
            logger.info("  🚫 Running ad detection...")
            ad_result = ad_detector.execute()
            if not ad_result['success']:
                logger.error(f"  ❌ Ad detection failed: {ad_result.get('error')}")
                return 1
            logger.info(f"  ✅ Ad detection: {ad_result.get('articles_passed', 0)} articles passed")
            
            logger.info("  🤖 Running LLM quality scoring...")
            llm_result = llm_scorer.execute()
            if not llm_result['success']:
                logger.error(f"  ❌ LLM quality scoring failed: {llm_result.get('error')}")
                return 1
            logger.info(f"  ✅ LLM quality scoring: {llm_result.get('articles_passed', 0)} articles passed")
            
            logger.info("  🔄 Running deduplication...")
            dedup_result = deduplicator.execute()
            if not dedup_result['success']:
                logger.error(f"  ❌ Deduplication failed: {dedup_result.get('error')}")
                return 1
            logger.info(f"  ✅ Deduplication: {dedup_result.get('duplicates_removed', 0)} duplicates removed")
            
            logger.info("  📊 Running article prioritization...")
            priority_result = prioritizer.execute()
            if not priority_result['success']:
                logger.error(f"  ❌ Article prioritization failed: {priority_result.get('error')}")
                return 1
            logger.info(f"  ✅ Article prioritization: {priority_result.get('articles_prioritized', 0)} articles prioritized")
            
            logger.info("  📝 Running summarization...")
            summary_result = summarizer.execute()
            if not summary_result['success']:
                logger.error(f"  ❌ Summarization failed: {summary_result.get('error')}")
                return 1
            logger.info(f"  ✅ Summarization: {summary_result.get('articles_summarized', 0)} articles summarized")
            
            logger.info("  📰 Running newsletter generation...")
            newsletter_result = newsletter_gen.execute()
            if not newsletter_result['success']:
                logger.error(f"  ❌ Newsletter generation failed: {newsletter_result.get('error')}")
                return 1
            logger.info(f"  ✅ Newsletter generation: {newsletter_result.get('newsletter_created', False)} newsletter created")
        
        # GitHub trending processing (part of full pipeline)
        if args.step == 'all':
            logger.info("🐙 Running GitHub trending processing...")
            github_processor = GitHubTrendingProcessor(config_loader)
            github_result = github_processor.process()
            if not github_result['success']:
                logger.error(f"❌ GitHub trending processing failed: {github_result.get('error')}")
                return 1
            logger.info(f"✅ GitHub trending processing: {github_result.get('processed_count', 0)} repositories processed")
        
        # Individual processing steps
        if args.step == 'content_filtering':
            logger.info("🔍 Running content filtering step only")
            content_filter = ContentFilteringStep(config_loader)
            filter_result = content_filter.execute()
            if not filter_result['success']:
                logger.error(f"❌ Content filtering failed: {filter_result.get('error')}")
                return 1
            logger.info(f"✅ Content filtering: {filter_result.get('articles_processed', 0)} articles processed")
        
        elif args.step == 'ad_detection':
            logger.info("🚫 Running ad detection step only")
            ad_detector = AdDetectionStep(config_loader)
            ad_result = ad_detector.execute()
            if not ad_result['success']:
                logger.error(f"❌ Ad detection failed: {ad_result.get('error')}")
                return 1
            logger.info(f"✅ Ad detection: {ad_result.get('articles_passed', 0)} articles passed")
        
        elif args.step == 'llm_quality_scoring':
            logger.info("🤖 Running LLM quality scoring step only")
            llm_scorer = LLMQualityScoringStep(config_loader)
            llm_result = llm_scorer.execute()
            if not llm_result['success']:
                logger.error(f"❌ LLM quality scoring failed: {llm_result.get('error')}")
                return 1
            logger.info(f"✅ LLM quality scoring: {llm_result.get('articles_passed', 0)} articles passed")
        
        elif args.step == 'deduplication':
            logger.info("🔄 Running deduplication step only")
            deduplicator = DeduplicationStep(config_loader)
            dedup_result = deduplicator.execute()
            if not dedup_result['success']:
                logger.error(f"❌ Deduplication failed: {dedup_result.get('error')}")
                return 1
            logger.info(f"✅ Deduplication: {dedup_result.get('duplicates_removed', 0)} duplicates removed")
        
        elif args.step == 'article_prioritization':
            logger.info("📊 Running article prioritization step only")
            prioritizer = ArticlePrioritizationStep(config_loader)
            priority_result = prioritizer.execute()
            if not priority_result['success']:
                logger.error(f"❌ Article prioritization failed: {priority_result.get('error')}")
                return 1
            logger.info(f"✅ Article prioritization: {priority_result.get('articles_prioritized', 0)} articles prioritized")
        
        elif args.step == 'summarization':
            logger.info("📝 Running summarization step only")
            summarizer = SummarizationStep(config_loader)
            summary_result = summarizer.execute()
            if not summary_result['success']:
                logger.error(f"❌ Summarization failed: {summary_result.get('error')}")
                return 1
            logger.info(f"✅ Summarization: {summary_result.get('articles_summarized', 0)} articles summarized")
        
        elif args.step == 'newsletter_generation':
            logger.info("📰 Running newsletter generation step only")
            newsletter_gen = NewsletterGenerationStep(config_loader)
            newsletter_result = newsletter_gen.execute()
            if not newsletter_result['success']:
                logger.error(f"❌ Newsletter generation failed: {newsletter_result.get('error')}")
                return 1
            logger.info(f"✅ Newsletter generation: {newsletter_result.get('newsletter_created', False)} newsletter created")
        
        elif args.step == 'github_trending_processing':
            logger.info("🐙 Running GitHub trending processing step only")
            github_processor = GitHubTrendingProcessor(config_loader)
            github_result = github_processor.process()
            if not github_result['success']:
                logger.error(f"❌ GitHub trending processing failed: {github_result.get('error')}")
                return 1
            logger.info(f"✅ GitHub trending processing: {github_result.get('processed_count', 0)} repositories processed")
        
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