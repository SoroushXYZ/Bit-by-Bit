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
from steps import RSSGatheringStep, ContentFilteringStep, AdDetectionStep, LLMQualityScoringStep, DeduplicationStep, ArticlePrioritizationStep, SummarizationStep, NewsletterGenerationStep


def main():
    """Main pipeline execution function."""
    parser = argparse.ArgumentParser(description='Run Bit-by-Bit Newsletter Pipeline')
    parser.add_argument('--config', default='pipeline/config/pipeline_config.json',
                       help='Path to pipeline configuration file')
    parser.add_argument('--step', choices=['rss_gathering', 'content_filtering', 'ad_detection', 'llm_quality_scoring', 'deduplication', 'article_prioritization', 'summarization', 'newsletter_generation', 'all'], default='all',
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
        if args.step == 'newsletter_generation':
            logger.info("Executing newsletter generation step")
            newsletter_step = NewsletterGenerationStep(config_loader)
            result = newsletter_step.execute()

            if result.get('success'):
                stats = result.get('statistics', {})
                logger.info(f"Newsletter generation completed successfully:")
                logger.info(f"  📰 Headlines: {stats.get('headlines_count', 0)}")
                logger.info(f"  📋 Secondary: {stats.get('secondary_count', 0)}")
                logger.info(f"  📄 Optional: {stats.get('optional_count', 0)}")
                logger.info(f"  📈 Data Reduction: {stats.get('data_reduction_percentage', 0):.1f}%")
                logger.info(f"  🎯 Avg Quality Score: {stats.get('average_quality_score', 0)}")
                logger.info(f"  ⭐ High Quality: {stats.get('high_quality_percentage', 0):.1f}%")
                logger.info(f"  📄 Output file: {result.get('output_file', 'Unknown')}")
            else:
                logger.error(f"Newsletter generation failed: {result.get('error', 'Unknown error')}")
                return 1
        
        if args.step == 'all' or args.step == 'rss_gathering':
            logger.info("Executing RSS gathering step")
            rss_step = RSSGatheringStep(config_loader)
            result = rss_step.execute()
            
            if result['success']:
                logger.info(f"RSS gathering completed successfully: {result['articles_collected']} articles collected")
            else:
                logger.error(f"RSS gathering failed: {result.get('error', 'Unknown error')}")
                return 1
        
        if args.step == 'all' or args.step == 'content_filtering':
            logger.info("Executing content filtering step")
            filtering_step = ContentFilteringStep(config_loader)
            result = filtering_step.execute()
            
            if result['success']:
                logger.info(f"Content filtering completed successfully: {result['articles_passed']}/{result['articles_input']} articles passed ({result['pass_rate']:.1f}%)")
            else:
                logger.error(f"Content filtering failed: {result.get('error', 'Unknown error')}")
                return 1
        
        if args.step == 'all' or args.step == 'ad_detection':
            logger.info("Executing advertisement detection step")
            ad_detection_step = AdDetectionStep(config_loader)
            result = ad_detection_step.execute()
            
            if result['success']:
                logger.info(f"Ad detection completed successfully: {result['articles_passed']}/{result['articles_input']} articles passed ({result['pass_rate']:.1f}%)")
                logger.info(f"Ad statistics: {result['ad_statistics']['ad_percentage']:.1f}% ads, {result['ad_statistics']['news_percentage']:.1f}% news")
            else:
                logger.error(f"Ad detection failed: {result.get('error', 'Unknown error')}")
                return 1
        
        if args.step == 'all' or args.step == 'llm_quality_scoring':
            logger.info("Executing LLM quality scoring step")
            llm_quality_step = LLMQualityScoringStep(config_loader)
            result = llm_quality_step.execute()
            
            if result['success']:
                logger.info(f"Quality scoring completed successfully: {result['articles_passed']}/{result['articles_input']} articles passed ({result['pass_rate']:.1f}%)")
                logger.info(f"Processing time: {result['processing_time']:.1f} seconds")
            else:
                logger.error(f"Quality scoring failed: {result.get('error', 'Unknown error')}")
                return 1
        
        if args.step == 'all' or args.step == 'deduplication':
            logger.info("Executing deduplication step")
            deduplication_step = DeduplicationStep(config_loader)
            result = deduplication_step.execute()
            
            if result['success']:
                logger.info(f"Deduplication completed successfully: {result['articles_passed']}/{result['articles_input']} articles selected ({result['selection_rate']:.1f}%)")
                logger.info(f"Duplicates removed: {result['duplicates_removed']}, Unique articles: {result['unique_articles']}")
                logger.info(f"Processing time: {result['processing_time']:.1f} seconds")
            else:
                logger.error(f"Deduplication failed: {result.get('error', 'Unknown error')}")
                return 1
        
        if args.step == 'all' or args.step == 'article_prioritization':
            logger.info("Executing article prioritization step")
            prioritization_step = ArticlePrioritizationStep(config_loader)
            result = prioritization_step.execute()
            
            if result.get('statistics'):
                stats = result['statistics']
                logger.info(f"Article prioritization completed successfully:")
                logger.info(f"  📰 Headlines: {stats['headlines_count']}/{stats['target_headlines']} target")
                logger.info(f"  📋 Secondary: {stats['secondary_count']}/{stats['target_secondary']} target") 
                logger.info(f"  📄 Optional: {stats['optional_count']}")
                logger.info(f"  ✅ Categorization success rate: {stats['categorization_success_rate']:.1f}%")
                logger.info(f"  ⏱️  Processing time: {result['metadata']['processing_time_seconds']:.1f} seconds")
            else:
                logger.error(f"Article prioritization failed: {result.get('error', 'Unknown error')}")
                return 1
        
            if args.step == 'all' or args.step == 'summarization':
                logger.info("Executing summarization step")
                summarization_step = SummarizationStep(config_loader)
                result = summarization_step.execute()

                if result.get('statistics'):
                    stats = result['statistics']
                    logger.info(f"Summarization completed successfully:")
                    logger.info(f"  📰 Headlines: {stats['headlines_count']}")
                    logger.info(f"  📋 Secondary: {stats['secondary_count']}")
                    logger.info(f"  📄 Optional: {stats['optional_count']}")
                    logger.info(f"  ✅ LLM Success: {stats['llm_success_count']}/{stats['total_articles']}")
                    logger.info(f"  🔄 Fallback Used: {stats['fallback_count']}/{stats['total_articles']}")
                    logger.info(f"  ⏱️  Processing time: {result['metadata']['processing_time_seconds']:.1f} seconds")
                else:
                    logger.error(f"Summarization failed: {result.get('error', 'Unknown error')}")
                    return 1

            if args.step == 'all' or args.step == 'newsletter_generation':
                logger.info("Executing newsletter generation step")
                newsletter_step = NewsletterGenerationStep(config_loader)
                result = newsletter_step.execute()

                if result.get('success'):
                    stats = result.get('statistics', {})
                    logger.info(f"Newsletter generation completed successfully:")
                    logger.info(f"  📰 Headlines: {stats.get('headlines_count', 0)}")
                    logger.info(f"  📋 Secondary: {stats.get('secondary_count', 0)}")
                    logger.info(f"  📄 Optional: {stats.get('optional_count', 0)}")
                    logger.info(f"  📈 Data Reduction: {stats.get('data_reduction_percentage', 0):.1f}%")
                    logger.info(f"  🎯 Avg Quality Score: {stats.get('average_quality_score', 0)}")
                    logger.info(f"  ⭐ High Quality: {stats.get('high_quality_percentage', 0):.1f}%")
                    logger.info(f"  📄 Output file: {result.get('output_file', 'Unknown')}")
                else:
                    logger.error(f"Newsletter generation failed: {result.get('error', 'Unknown error')}")
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
