#!/usr/bin/env python3
"""
Newsletter generation step for the Bit-by-Bit pipeline.
Creates clean, formatted output with pipeline visualization data.
"""

import json
import os
from src.utils.logger import get_logger
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

class NewsletterGenerationStep:
    """Generate clean newsletter output with pipeline visualization data."""
    
    def __init__(self, config_loader):
        self.config_loader = config_loader
        self.step_name = "newsletter_generation"
        self.config = self.config_loader.get_step_config(self.step_name)
        self.data_paths = self.config_loader.get_data_paths()
        self.output_dir = Path(self.data_paths['processed'])
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging (run-scoped)
        self.logger = get_logger()
        
    def execute(self) -> Dict[str, Any]:
        """Execute the newsletter generation step."""
        self.logger.info("🚀 Starting newsletter generation step")
        
        try:
            # Load summarized content
            summarized_data = self._load_summarized_content()
            if not summarized_data:
                raise Exception("No summarized content found")
            
            # Collect pipeline metadata
            pipeline_metadata = self._collect_pipeline_metadata()
            
            # Generate newsletter output
            newsletter_output = self._generate_newsletter_output(summarized_data, pipeline_metadata)
            
            # Save output
            output_file = self._save_newsletter_output(newsletter_output)
            
            # Create statistics
            stats = self._create_statistics(newsletter_output, pipeline_metadata)
            
            self.logger.info(f"✅ Newsletter generation completed: {output_file}")
            self.logger.info(f"📊 Generated {len(newsletter_output['content']['headlines'])} headlines, {len(newsletter_output['content']['secondary'])} secondary, {len(newsletter_output['content']['optional'])} optional")
            
            return {
                "success": True,
                "output_file": output_file,
                "statistics": stats,
                "metadata": {
                    "step": self.step_name,
                    "timestamp": datetime.now().isoformat(),
                    "processing_time_seconds": 0,  # This step is very fast
                    "articles_processed": len(newsletter_output['content']['headlines']) + 
                                        len(newsletter_output['content']['secondary']) + 
                                        len(newsletter_output['content']['optional'])
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Newsletter generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "step": self.step_name,
                    "timestamp": datetime.now().isoformat(),
                    "processing_time_seconds": 0
                }
            }
    
    def _load_summarized_content(self) -> Dict[str, Any]:
        """Load the most recent summarized content."""
        processed_dir = Path(self.data_paths['processed'])
        summarized_path = processed_dir / "summarized_content.json"
        
        if not summarized_path.exists():
            raise Exception("No summarized content files found")
        
        self.logger.info(f"📄 Loading summarized content from: {summarized_path.name}")
        
        with open(summarized_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _collect_pipeline_metadata(self) -> Dict[str, Any]:
        """Collect metadata from all pipeline steps."""
        metadata = {}
        processed_dir = Path(self.data_paths['processed'])
        
        # RSS Gathering - estimate from first step's input
        all_files = list(processed_dir.glob("*.json"))
        if all_files:
            first_file = min(all_files, key=os.path.getctime)
            with open(first_file, 'r', encoding='utf-8') as f:
                first_data = json.load(f)
                # Get RSS data from the first step's input
                articles_input = first_data.get('metadata', {}).get('total_articles_input', 0)
                metadata['rss_gathering'] = {
                    'articles_collected': articles_input,
                    'feeds_processed': 0,  # Unknown
                    'successful_feeds': 0,  # Unknown
                    'failed_feeds': 0,  # Unknown
                    'processing_time': 0,  # Unknown
                    'timestamp': first_data.get('metadata', {}).get('processing_timestamp', '')
                }
        
        # Content Filtering
        filtering_path = processed_dir / "filtered_content.json"
        if filtering_path.exists():
            with open(filtering_path, 'r', encoding='utf-8') as f:
                filtering_data = json.load(f)
                metadata['content_filtering'] = {
                    'articles_input': filtering_data.get('metadata', {}).get('total_articles_input', 0),
                    'articles_passed': filtering_data.get('metadata', {}).get('total_articles_passed', 0),
                    'articles_filtered': filtering_data.get('metadata', {}).get('total_articles_rejected', 0),
                    'pass_rate': filtering_data.get('metadata', {}).get('filter_pass_rate', 0),
                    'processing_time': 0,  # Not available in this file
                    'timestamp': filtering_data.get('metadata', {}).get('processing_timestamp', '')
                }
        
        # Ad Detection
        ad_detection_path = processed_dir / "ad_filtered_content.json"
        if ad_detection_path.exists():
            with open(ad_detection_path, 'r', encoding='utf-8') as f:
                ad_detection_data = json.load(f)
                metadata['ad_detection'] = {
                    'articles_input': ad_detection_data.get('statistics', {}).get('articles_input', 0),
                    'articles_passed': ad_detection_data.get('statistics', {}).get('articles_passed', 0),
                    'articles_filtered': ad_detection_data.get('statistics', {}).get('articles_filtered', 0),
                    'pass_rate': ad_detection_data.get('statistics', {}).get('pass_rate', 0),
                    'ad_percentage': ad_detection_data.get('statistics', {}).get('ad_statistics', {}).get('ad_percentage', 0),
                    'news_percentage': ad_detection_data.get('statistics', {}).get('ad_statistics', {}).get('news_percentage', 0),
                    'processing_time': ad_detection_data.get('metadata', {}).get('processing_time_seconds', 0),
                    'timestamp': ad_detection_data.get('metadata', {}).get('timestamp', '')
                }
        
        # Quality Scoring
        quality_path = processed_dir / "quality_scored_content.json"
        if quality_path.exists():
            with open(quality_path, 'r', encoding='utf-8') as f:
                quality_data = json.load(f)
                metadata['quality_scoring'] = {
                    'articles_processed': quality_data.get('statistics', {}).get('articles_input', 0),
                    'articles_passed': quality_data.get('statistics', {}).get('articles_passed', 0),
                    'articles_filtered': quality_data.get('statistics', {}).get('articles_filtered', 0),
                    'pass_rate': quality_data.get('statistics', {}).get('pass_rate', 0),
                    'processing_time': quality_data.get('metadata', {}).get('processing_time_seconds', 0),
                    'timestamp': quality_data.get('metadata', {}).get('timestamp', '')
                }
        
        # Deduplication
        dedup_path = processed_dir / "deduplicated_content.json"
        if dedup_path.exists():
            with open(dedup_path, 'r', encoding='utf-8') as f:
                dedup_data = json.load(f)
                articles_input = dedup_data.get('statistics', {}).get('articles_input', 0)
                articles_selected = dedup_data.get('statistics', {}).get('articles_selected', 0)
                duplicates_removed = dedup_data.get('statistics', {}).get('total_duplicates_removed', 0)
                reduction_percentage = dedup_data.get('statistics', {}).get('deduplication_rate', 0)
                metadata['deduplication'] = {
                    'articles_before': articles_input,
                    'articles_after': articles_selected,
                    'duplicates_removed': duplicates_removed,
                    'reduction_percentage': reduction_percentage,
                    'processing_time': dedup_data.get('metadata', {}).get('processing_time_seconds', 0),
                    'timestamp': dedup_data.get('metadata', {}).get('timestamp', '')
                }
        
        # Article Prioritization
        prioritization_path = processed_dir / "prioritized_content.json"
        if prioritization_path.exists():
            with open(prioritization_path, 'r', encoding='utf-8') as f:
                prioritization_data = json.load(f)
                metadata['prioritization'] = {
                    'articles_processed': prioritization_data.get('metadata', {}).get('articles_processed', 0),
                    'headlines_count': len(prioritization_data.get('categorization', {}).get('headlines', [])),
                    'secondary_count': len(prioritization_data.get('categorization', {}).get('secondary', [])),
                    'optional_count': len(prioritization_data.get('categorization', {}).get('optional', [])),
                    'llm_success': prioritization_data.get('metadata', {}).get('llm_success', False),
                    'fallback_used': prioritization_data.get('metadata', {}).get('fallback_used', False),
                    'processing_time': prioritization_data.get('metadata', {}).get('processing_time_seconds', 0),
                    'timestamp': prioritization_data.get('metadata', {}).get('timestamp', '')
                }
        
        # Summarization
        summarization_path = processed_dir / "summarized_content.json"
        if summarization_path.exists():
            with open(summarization_path, 'r', encoding='utf-8') as f:
                summarization_data = json.load(f)
                metadata['summarization'] = {
                    'articles_processed': summarization_data.get('metadata', {}).get('articles_processed', 0),
                    'processing_time': summarization_data.get('metadata', {}).get('processing_time_seconds', 0),
                    'llm_success_count': summarization_data.get('statistics', {}).get('llm_success_count', 0),
                    'fallback_count': summarization_data.get('statistics', {}).get('fallback_count', 0),
                    'timestamp': summarization_data.get('metadata', {}).get('timestamp', '')
                }
        
        return metadata
    
    def _generate_newsletter_output(self, summarized_data: Dict[str, Any], pipeline_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate clean newsletter output with pipeline visualization."""
        
        # Create clean newsletter format
        newsletter_output = {
            "newsletter": {
                "title": "Bit-by-Bit Tech Newsletter",
                "date": datetime.now().strftime("%B %d, %Y"),
                "generated_at": datetime.now().isoformat(),
                "pipeline_version": "1.0.0"
            },
            "content": {
                "headlines": self._format_articles(summarized_data.get('summaries', {}).get('headlines', [])),
                "secondary": self._format_articles(summarized_data.get('summaries', {}).get('secondary', [])),
                "optional": self._format_articles(summarized_data.get('summaries', {}).get('optional', []))
            },
            "pipeline_visualization": {
                "overview": self._create_pipeline_overview(pipeline_metadata),
                "data_flow": self._create_data_flow_visualization(pipeline_metadata),
                "quality_analysis": self._create_quality_analysis(summarized_data),
                "source_analysis": self._create_source_analysis(pipeline_metadata),
                "processing_stats": self._create_processing_stats(pipeline_metadata)
            },
            "metadata": {
                "total_articles_final": len(summarized_data.get('summaries', {}).get('headlines', [])) + 
                                      len(summarized_data.get('summaries', {}).get('secondary', [])) + 
                                      len(summarized_data.get('summaries', {}).get('optional', [])),
                "generation_time": datetime.now().isoformat(),
                "pipeline_steps_completed": len(pipeline_metadata)
            }
        }
        
        return newsletter_output
    
    def _format_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format articles for newsletter."""
        formatted = []
        for i, article in enumerate(articles, 1):
            formatted.append({
                "rank": i,
                "title": article.get('title', ''),
                "summary": article.get('summary', ''),
                "word_count": article.get('word_count', 0),
                "source": article.get('feed_name', ''),
                "url": article.get('original_url', ''),
                "quality_score": article.get('quality_score', 0),
                "quality_level": article.get('quality_level', ''),
                "content_source": article.get('content_source_used', ''),
                "fallback_used": article.get('fallback_used', False)
            })
        return formatted
    
    def _create_pipeline_overview(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create pipeline overview visualization data."""
        overview = {
            "total_steps": len(metadata),
            "steps_completed": list(metadata.keys()),
            "data_reduction": {
                "start": metadata.get('rss_gathering', {}).get('articles_collected', 0),
                "end": metadata.get('prioritization', {}).get('articles_processed', 0),
                "reduction_percentage": 0
            },
            "processing_time": {
                "total_seconds": sum(step.get('processing_time', 0) for step in metadata.values()),
                "breakdown": {step: data.get('processing_time', 0) for step, data in metadata.items()}
            }
        }
        
        # Calculate reduction percentage
        start = overview['data_reduction']['start']
        end = overview['data_reduction']['end']
        if start > 0:
            overview['data_reduction']['reduction_percentage'] = round((start - end) / start * 100, 1)
        
        return overview
    
    def _create_data_flow_visualization(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create data flow visualization data."""
        flow = []
        
        # RSS Gathering
        if 'rss_gathering' in metadata:
            flow.append({
                "step": "RSS Gathering",
                "input": 0,
                "output": metadata['rss_gathering']['articles_collected'],
                "processing_time": metadata['rss_gathering']['processing_time'],
                "description": f"Collected {metadata['rss_gathering']['articles_collected']} articles from {metadata['rss_gathering']['feeds_processed']} feeds"
            })
        
        # Content Filtering
        if 'content_filtering' in metadata:
            flow.append({
                "step": "Content Filtering",
                "input": metadata['content_filtering']['articles_input'],
                "output": metadata['content_filtering']['articles_passed'],
                "processing_time": metadata['content_filtering']['processing_time'],
                "description": f"Filtered {metadata['content_filtering']['articles_passed']}/{metadata['content_filtering']['articles_input']} articles ({metadata['content_filtering']['pass_rate']:.1f}% pass rate)"
            })
        
        # Ad Detection
        if 'ad_detection' in metadata:
            flow.append({
                "step": "Ad Detection",
                "input": metadata['ad_detection']['articles_input'],
                "output": metadata['ad_detection']['articles_passed'],
                "processing_time": metadata['ad_detection']['processing_time'],
                "description": f"Removed {metadata['ad_detection']['articles_filtered']} ads, kept {metadata['ad_detection']['articles_passed']} articles ({metadata['ad_detection']['pass_rate']:.1f}% pass rate)"
            })
        
        # Quality Scoring
        if 'quality_scoring' in metadata:
            flow.append({
                "step": "Quality Scoring",
                "input": metadata['quality_scoring']['articles_processed'],
                "output": metadata['quality_scoring']['articles_passed'],
                "processing_time": metadata['quality_scoring']['processing_time'],
                "description": f"Scored {metadata['quality_scoring']['articles_processed']} articles, kept {metadata['quality_scoring']['articles_passed']} ({metadata['quality_scoring']['pass_rate']:.1f}% pass rate)"
            })
        
        # Deduplication
        if 'deduplication' in metadata:
            flow.append({
                "step": "Deduplication",
                "input": metadata['deduplication']['articles_before'],
                "output": metadata['deduplication']['articles_after'],
                "processing_time": metadata['deduplication']['processing_time'],
                "description": f"Removed {metadata['deduplication']['duplicates_removed']} duplicates ({metadata['deduplication']['reduction_percentage']:.1f}% reduction)"
            })
        
        # Prioritization
        if 'prioritization' in metadata:
            flow.append({
                "step": "Prioritization",
                "input": metadata['prioritization']['articles_processed'],
                "output": metadata['prioritization']['articles_processed'],
                "processing_time": metadata['prioritization']['processing_time'],
                "description": f"Categorized into {metadata['prioritization']['headlines_count']} headlines, {metadata['prioritization']['secondary_count']} secondary, {metadata['prioritization']['optional_count']} optional"
            })
        
        # Summarization
        if 'summarization' in metadata:
            flow.append({
                "step": "Summarization",
                "input": metadata['summarization']['articles_processed'],
                "output": metadata['summarization']['articles_processed'],
                "processing_time": metadata['summarization']['processing_time'],
                "description": f"Summarized {metadata['summarization']['articles_processed']} articles for newsletter"
            })
        
        # Calculate total reduction from start to end
        total_reduction = 0
        reduction_percentage = 0
        if flow and len(flow) >= 2:
            start_count = flow[0]['output']
            end_count = flow[-1]['output']
            total_reduction = start_count - end_count
            if start_count > 0:
                reduction_percentage = round(total_reduction / start_count * 100, 1)
        
        return {
            "flow": flow,
            "total_reduction": total_reduction,
            "reduction_percentage": reduction_percentage
        }
    
    def _create_quality_analysis(self, summarized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create quality analysis visualization data."""
        all_articles = []
        for category in ['headlines', 'secondary', 'optional']:
            all_articles.extend(summarized_data.get('summaries', {}).get(category, []))
        
        if not all_articles:
            return {"error": "No articles found for quality analysis"}
        
        quality_scores = [article.get('quality_score', 0) for article in all_articles]
        quality_levels = [article.get('quality_level', '') for article in all_articles]
        
        # Calculate quality statistics
        avg_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        min_score = min(quality_scores) if quality_scores else 0
        max_score = max(quality_scores) if quality_scores else 0
        
        # Count quality levels
        level_counts = {}
        for level in quality_levels:
            level_counts[level] = level_counts.get(level, 0) + 1
        
        return {
            "total_articles": len(all_articles),
            "average_quality_score": round(avg_score, 1),
            "min_quality_score": min_score,
            "max_quality_score": max_score,
            "quality_distribution": level_counts,
            "score_range": f"{min_score}-{max_score}",
            "high_quality_percentage": round((level_counts.get('excellent', 0) + level_counts.get('high', 0)) / len(all_articles) * 100, 1) if all_articles else 0
        }
    
    def _create_source_analysis(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create source analysis visualization data."""
        if 'rss_gathering' not in metadata:
            return {"error": "RSS gathering data not available"}
        
        rss_data = metadata['rss_gathering']
        
        return {
            "total_feeds": rss_data['feeds_processed'],
            "successful_feeds": rss_data['successful_feeds'],
            "failed_feeds": rss_data['failed_feeds'],
            "success_rate": round(rss_data['successful_feeds'] / rss_data['feeds_processed'] * 100, 1) if rss_data['feeds_processed'] > 0 else 0,
            "articles_per_feed": round(rss_data['articles_collected'] / rss_data['successful_feeds'], 1) if rss_data['successful_feeds'] > 0 else 0
        }
    
    def _create_processing_stats(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create processing statistics visualization data."""
        total_time = sum(step.get('processing_time', 0) for step in metadata.values())
        
        return {
            "total_processing_time": round(total_time, 1),
            "average_time_per_step": round(total_time / len(metadata), 1) if metadata else 0,
            "slowest_step": max(metadata.items(), key=lambda x: x[1].get('processing_time', 0))[0] if metadata else None,
            "fastest_step": min(metadata.items(), key=lambda x: x[1].get('processing_time', 0))[0] if metadata else None,
            "step_breakdown": {step: round(data.get('processing_time', 0), 1) for step, data in metadata.items()}
        }
    
    def _save_newsletter_output(self, newsletter_output: Dict[str, Any]) -> str:
        """Save newsletter output to file."""
        # Use fixed filename within run directory
        output_file = self.output_dir / "newsletter_output.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(newsletter_output, f, indent=2, ensure_ascii=False)
        
        return str(output_file)
    
    def _create_statistics(self, newsletter_output: Dict[str, Any], pipeline_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create statistics for the newsletter generation step."""
        content = newsletter_output['content']
        overview = newsletter_output['pipeline_visualization']['overview']
        quality = newsletter_output['pipeline_visualization']['quality_analysis']
        
        return {
            "headlines_count": len(content['headlines']),
            "secondary_count": len(content['secondary']),
            "optional_count": len(content['optional']),
            "total_articles": len(content['headlines']) + len(content['secondary']) + len(content['optional']),
            "data_reduction_percentage": overview['data_reduction']['reduction_percentage'],
            "average_quality_score": quality['average_quality_score'],
            "high_quality_percentage": quality['high_quality_percentage'],
            "total_processing_time": overview['processing_time']['total_seconds']
        }
