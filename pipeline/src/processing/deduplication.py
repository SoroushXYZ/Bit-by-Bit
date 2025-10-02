"""
Step 5: Deduplication using Embeddings

This step uses sentence transformers to find similar articles and selects
the highest quality one from each group of similar articles.
"""

import json
import time
import logging
import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

# For embeddings and similarity
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class DeduplicationStep:
    """
    Deduplication Step using Sentence Transformers.
    
    This step finds similar articles using embeddings and selects the highest
    quality article from each group of similar articles.
    """
    
    def __init__(self, config_loader):
        self.step_name = "deduplication"
        self.config_loader = config_loader
        self.logger = get_logger()
        
        # Load step configuration
        self.config = self.config_loader.get_step_config(self.step_name)
        
        # Get data paths from config loader
        self.data_paths = self.config_loader.get_data_paths()
        
        # Embedding configuration
        self.embedding_config = self.config['embeddings']
        self.model_name = self.embedding_config['model_name']
        self.similarity_threshold = self.embedding_config['similarity_threshold']
        self.batch_size = self.embedding_config.get('batch_size', 50)
        
        # Deduplication configuration
        self.dedup_config = self.config['deduplication']
        self.max_articles = self.dedup_config['max_articles']
        self.quality_priority = self.dedup_config['quality_priority']
        
        # Initialize model
        self.model = None
        self.model_loaded = False
        
    def _load_input_data(self) -> List[Dict[str, Any]]:
        """Load input data from LLM quality scoring step."""
        import glob
        
        try:
            input_config = self.config['input']
            source_step = input_config['source_step']
            filename_prefix = input_config['filename_prefix']
            
            # Load fixed input file within run directory
            input_path = self.data_paths['processed']
            fixed_input = os.path.join(input_path, f"{filename_prefix}.json")
            if not os.path.exists(fixed_input):
                raise FileNotFoundError(f"Input file not found: {fixed_input}")
            self.logger.info(f"Loading input data from: {fixed_input}")
            
            with open(fixed_input, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            articles = data.get('articles', [])
            quality_results = data.get('quality_results', [])
            
            self.logger.info(f"Loaded {len(articles)} articles from input file")
            
            # Combine articles with their quality scores
            articles_with_quality = []
            for i, article in enumerate(articles):
                article_with_quality = article.copy()
                
                # Add quality information if available
                if i < len(quality_results):
                    quality_data = quality_results[i]
                    article_with_quality['quality_score'] = quality_data.get('quality_metrics', {}).get('average_score', 0)
                    article_with_quality['quality_level'] = quality_data.get('quality_metrics', {}).get('quality_level', 'unknown')
                    article_with_quality['quality_analysis'] = quality_data.get('llm_analysis', {})
                else:
                    article_with_quality['quality_score'] = 0
                    article_with_quality['quality_level'] = 'unknown'
                    article_with_quality['quality_analysis'] = {}
                
                articles_with_quality.append(article_with_quality)
            
            return articles_with_quality
            
        except Exception as e:
            self.logger.error(f"Failed to load input data: {e}")
            raise
    
    def _save_output_data(self, output_data: Dict[str, Any]) -> str:
        """Save output data to file."""
        try:
            output_config = self.config['output']
            filename_prefix = output_config['filename_prefix']
            save_format = output_config['save_format']
            
            # Use fixed filename within run directory
            filename = f"{filename_prefix}.json"
            
            # Save to processed data path
            output_path = self.data_paths['processed']
            filepath = os.path.join(output_path, filename)
            
            # Convert numpy types to Python native types for JSON serialization
            def convert_numpy_types(obj):
                """Recursively convert numpy types to Python native types."""
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {key: convert_numpy_types(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy_types(item) for item in obj]
                else:
                    return obj
            
            # Convert all numpy types before saving
            output_data_serializable = convert_numpy_types(output_data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data_serializable, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved output data to: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to save output data: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for embedding generation."""
        if not text:
            return ""
            
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove excessive punctuation but keep common punctuation
        text = re.sub(r'[^\w\s\-.,!?:;()]', '', text)
        
        return text.strip()
    
    def _load_embedding_model(self) -> bool:
        """Load the sentence transformer model."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            self.logger.error("❌ Sentence transformers not available. Install with: pip install sentence-transformers scikit-learn")
            return False
            
        try:
            self.logger.info(f"📥 Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.logger.info(f"✅ Model loaded successfully")
            
            self.model_loaded = True
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error loading model: {e}")
            return False
    
    def _prepare_text_for_embedding(self, article: Dict[str, Any]) -> str:
        """Prepare article text for embedding generation."""
        title = self._clean_text(article.get('title', ''))
        content = self._clean_text(article.get('content', ''))
        
        # Combine title and content with separator
        combined_text = f"{title} [SEP] {content}"
        
        return combined_text
    
    def _generate_embeddings(self, articles: List[Dict[str, Any]]) -> np.ndarray:
        """Generate embeddings for all articles."""
        self.logger.info("🔄 Preparing texts for embedding generation...")
        
        texts = []
        for article in articles:
            text = self._prepare_text_for_embedding(article)
            texts.append(text)
        
        self.logger.info(f"🧠 Generating embeddings for {len(texts)} articles...")
        
        # Process in batches to avoid memory issues
        embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = self.model.encode(batch, convert_to_tensor=False, show_progress_bar=False)
            embeddings.extend(batch_embeddings)
            
            if (i // self.batch_size + 1) % 10 == 0:  # Log progress every 10 batches
                self.logger.info(f"   Processed {i + len(batch)}/{len(texts)} articles")
        
        embeddings = np.array(embeddings)
        self.logger.info(f"✅ Generated embeddings: {embeddings.shape}")
        
        return embeddings
    
    def _find_similar_articles(self, embeddings: np.ndarray, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find similar articles using cosine similarity."""
        self.logger.info(f"📊 Calculating similarity matrix...")
        similarity_matrix = cosine_similarity(embeddings)
        
        self.logger.info(f"🔍 Finding similar articles with threshold > {self.similarity_threshold}...")
        
        # Track which articles have been processed
        processed = set()
        similar_groups = []
        
        for i in range(len(similarity_matrix)):
            if i in processed:
                continue
                
            # Find articles similar to article i
            similar_indices = []
            for j in range(i + 1, len(similarity_matrix)):
                if j not in processed and similarity_matrix[i][j] > self.similarity_threshold:
                    similar_indices.append(j)
            
            if similar_indices:
                # Create a group with the main article and all similar ones
                group_indices = [i] + similar_indices
                group_articles = [articles[idx] for idx in group_indices]
                
                # Add similarity scores for analysis
                for idx, article in enumerate(group_articles):
                    article['similarity_score'] = similarity_matrix[i][group_indices[idx]]
                
                similar_groups.append({
                    'main_article_index': i,
                    'similar_indices': similar_indices,
                    'articles': group_articles,
                    'max_similarity': max([similarity_matrix[i][j] for j in similar_indices]),
                    'group_size': len(group_articles)
                })
                
                # Mark all articles in this group as processed
                processed.update(group_indices)
            else:
                # Single article (no duplicates found)
                similar_groups.append({
                    'main_article_index': i,
                    'similar_indices': [],
                    'articles': [articles[i]],
                    'max_similarity': 0.0,
                    'group_size': 1
                })
                processed.add(i)
        
        return similar_groups
    
    def _select_best_article_from_group(self, group: Dict[str, Any]) -> Dict[str, Any]:
        """Select the best article from a group of similar articles."""
        articles = group['articles']
        
        if len(articles) == 1:
            return articles[0]
        
        # Sort by quality score (descending)
        if self.quality_priority:
            articles_sorted = sorted(articles, key=lambda x: x.get('quality_score', 0), reverse=True)
        else:
            # If no quality scores available, sort by similarity score (descending)
            articles_sorted = sorted(articles, key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        best_article = articles_sorted[0]
        
        # Add information about the group for analysis
        best_article['deduplication_info'] = {
            'was_duplicate': len(articles) > 1,
            'group_size': len(articles),
            'max_similarity': group['max_similarity'],
            'competing_articles': [
                {
                    'title': art['title'],
                    'feed_name': art.get('feed_name', 'Unknown'),
                    'quality_score': art.get('quality_score', 0),
                    'similarity_score': art.get('similarity_score', 0)
                }
                for art in articles[1:]  # Exclude the selected article
            ]
        }
        
        return best_article
    
    def _select_top_articles(self, unique_articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Select the top N articles based on quality scores."""
        # Sort by quality score (descending)
        sorted_articles = sorted(unique_articles, key=lambda x: x.get('quality_score', 0), reverse=True)
        
        # Take top N articles
        top_articles = sorted_articles[:self.max_articles]
        
        self.logger.info(f"📊 Selected top {len(top_articles)} articles from {len(unique_articles)} unique articles")
        
        return top_articles
    
    def execute(self) -> Dict[str, Any]:
        """Execute the deduplication step."""
        self.logger.info("🚀 Starting deduplication step")
        
        # Load embedding model
        if not self._load_embedding_model():
            return {
                'success': False,
                'error': 'Failed to load embedding model',
                'articles_input': 0,
                'articles_passed': 0,
                'pass_rate': 0.0
            }
        
        # Load input data
        articles = self._load_input_data()
        if not articles:
            self.logger.warning("⚠️ No articles found in input data")
            return {
                'success': True,
                'articles_input': 0,
                'articles_passed': 0,
                'pass_rate': 0.0,
                'message': 'No articles to process'
            }
        
        self.logger.info(f"📊 Processing {len(articles)} articles for deduplication")
        
        # Process articles
        start_time = time.time()
        
        # Generate embeddings
        embeddings = self._generate_embeddings(articles)
        
        # Find similar articles
        similar_groups = self._find_similar_articles(embeddings, articles)
        
        # Select best article from each group
        unique_articles = []
        for group in similar_groups:
            best_article = self._select_best_article_from_group(group)
            unique_articles.append(best_article)
        
        # Select top N articles
        top_articles = self._select_top_articles(unique_articles)
        
        processing_time = time.time() - start_time
        
        # Calculate statistics
        duplicate_groups = [g for g in similar_groups if g['group_size'] > 1]
        total_duplicates_found = sum(g['group_size'] - 1 for g in duplicate_groups)
        
        # Save results
        output_data = {
            'metadata': {
                'step': self.step_name,
                'timestamp': datetime.now().isoformat(),
                'processing_time_seconds': processing_time,
                'embedding_model': self.model_name,
                'similarity_threshold': self.similarity_threshold,
                'max_articles': self.max_articles
            },
            'statistics': {
                'articles_input': len(articles),
                'unique_articles_found': len(unique_articles),
                'articles_selected': len(top_articles),
                'duplicate_groups_found': len(duplicate_groups),
                'total_duplicates_removed': total_duplicates_found,
                'deduplication_rate': (total_duplicates_found / len(articles)) * 100 if articles else 0,
                'selection_rate': (len(top_articles) / len(articles)) * 100 if articles else 0
            },
            'similar_groups_analysis': [
                {
                    'group_id': i,
                    'group_size': group['group_size'],
                    'max_similarity': group['max_similarity'],
                    'selected_article': {
                        'title': group['articles'][0]['title'],
                        'feed_name': group['articles'][0].get('feed_name', 'Unknown'),
                        'quality_score': group['articles'][0].get('quality_score', 0)
                    },
                    'competing_articles': [
                        {
                            'title': art['title'],
                            'feed_name': art.get('feed_name', 'Unknown'),
                            'quality_score': art.get('quality_score', 0),
                            'similarity_score': art.get('similarity_score', 0)
                        }
                        for art in group['articles'][1:] if len(group['articles']) > 1
                    ]
                }
                for i, group in enumerate(duplicate_groups)
            ],
            'articles': top_articles
        }
        
        # Save to file
        output_file = self._save_output_data(output_data)
        
        # Log results
        self.logger.info(f"⏱️  Processing time: {processing_time:.2f} seconds")
        self.logger.info(f"📊 Deduplication results:")
        self.logger.info(f"   Input articles: {len(articles)}")
        self.logger.info(f"   Unique articles found: {len(unique_articles)}")
        self.logger.info(f"   Duplicate groups: {len(duplicate_groups)}")
        self.logger.info(f"   Duplicates removed: {total_duplicates_found}")
        self.logger.info(f"   Articles selected: {len(top_articles)}")
        
        # Show top duplicate groups
        if duplicate_groups:
            self.logger.info(f"\n🔍 Top duplicate groups found:")
            for i, group in enumerate(duplicate_groups[:5], 1):
                self.logger.info(f"   {i}. Group size: {group['group_size']}, Max similarity: {group['max_similarity']:.3f}")
                self.logger.info(f"      Selected: {group['articles'][0]['title'][:60]}...")
                for j, art in enumerate(group['articles'][1:], 1):
                    self.logger.info(f"      Removed {j}: {art['title'][:60]}... (Q:{art.get('quality_score', 0):.1f})")
        
        # Show top articles by quality
        if top_articles:
            self.logger.info(f"\n⭐ Top articles selected:")
            for i, article in enumerate(top_articles[:5], 1):
                self.logger.info(f"   {i}. Q:{article.get('quality_score', 0):.1f} - {article['title'][:70]}...")
                self.logger.info(f"      Feed: {article.get('feed_name', 'Unknown')}")
        
        self.logger.info(f"💾 Results saved to {output_file}")
        self.logger.info(f"✅ Deduplication completed: {len(top_articles)}/{len(articles)} articles selected ({output_data['statistics']['selection_rate']:.1f}%)")
        
        return {
            'success': True,
            'articles_input': len(articles),
            'articles_passed': len(top_articles),
            'unique_articles': len(unique_articles),
            'duplicates_removed': total_duplicates_found,
            'selection_rate': output_data['statistics']['selection_rate'],
            'output_file': output_file,
            'processing_time': processing_time
        }
