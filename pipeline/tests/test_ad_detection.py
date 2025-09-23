#!/usr/bin/env python3
"""
Test script for the Advertisement Detection Step.
"""

import unittest
import json
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import initialize_logger, load_pipeline_config
from steps import AdDetectionStep


class TestAdDetectionStep(unittest.TestCase):
    def setUp(self):
        # Initialize logger for tests
        initialize_logger('pipeline/config/pipeline_config.json')
        
        # Create a dummy pipeline config for testing
        self.pipeline_config_path = Path("pipeline/config/test_pipeline_config.json")
        self.content_filtering_config_path = Path("pipeline/config/test_content_filtering_config.json")
        self.ad_detection_config_path = Path("pipeline/config/test_ad_detection_config.json")
        
        self.data_dir = Path("pipeline/data/test_raw")
        self.processed_dir = Path("pipeline/data/test_processed")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # Dummy pipeline config
        pipeline_config_content = {
            "pipeline_name": "Test Pipeline",
            "logging": {"level": "DEBUG", "file": "test_ad_detection.log"},
            "data_paths": {
                "base_path": "pipeline/data",
                "raw_data_path": str(self.data_dir),
                "processed_data_path": str(self.processed_dir),
                "output_data_path": "pipeline/data/test_output"
            },
            "steps": {
                "content_filtering": {
                    "enabled": True, "order": 2, "description": "Test Filtering",
                    "config_file": str(self.content_filtering_config_path)
                },
                "ad_detection": {
                    "enabled": True, "order": 3, "description": "Test Ad Detection",
                    "config_file": str(self.ad_detection_config_path)
                }
            }
        }
        with open(self.pipeline_config_path, 'w') as f:
            json.dump(pipeline_config_content, f)

        # Dummy content filtering config (minimal, just for data paths)
        content_filtering_config_content = {
            "step_name": "content_filtering",
            "output": {"filename_prefix": "test_filtered_content", "save_format": "json"}
        }
        with open(self.content_filtering_config_path, 'w') as f:
            json.dump(content_filtering_config_content, f)

        # Dummy ad detection config
        ad_detection_config_content = {
            "step_name": "ad_detection",
            "input": {"source_step": "content_filtering", "filename_prefix": "test_filtered_content"},
            "output": {"filename_prefix": "test_ad_filtered_content", "save_format": "json"},
            "model": {
                "name": "SoroushXYZ/distilbert-rss-ad-detection",
                "base_model": "distilbert-base-uncased",
                "training_data": "Test data",
                "performance": "Test performance"
            },
            "text_processing": {"max_length": 120},
            "classification": {"advertisement_label": "advertisement", "news_label": "news"},
            "filtering": {"min_news_confidence": 0.5},
            "error_handling": {"continue_on_article_error": True, "include_on_classification_error": True}
        }
        with open(self.ad_detection_config_path, 'w') as f:
            json.dump(ad_detection_config_content, f)

        self.config_loader = load_pipeline_config(str(self.pipeline_config_path))
        self.step = AdDetectionStep(self.config_loader)

    def tearDown(self):
        # Clean up dummy config and data files
        self.pipeline_config_path.unlink(missing_ok=True)
        self.content_filtering_config_path.unlink(missing_ok=True)
        self.ad_detection_config_path.unlink(missing_ok=True)
        for f in self.data_dir.glob("*"): f.unlink()
        self.data_dir.rmdir()
        for f in self.processed_dir.glob("*"): f.unlink()
        self.processed_dir.rmdir()
        Path("test_ad_detection.log").unlink(missing_ok=True)

    def _create_dummy_filtered_data(self, articles_data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_filtered_content_{timestamp}.json"
        filepath = self.processed_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({"articles": articles_data}, f, indent=2, ensure_ascii=False)
        return filepath

    def test_model_loading_failure_handling(self):
        """Test that the step handles model loading failures gracefully."""
        # This test will fail model loading since we don't have transformers installed in test env
        articles_data = [
            {"title": "Test Article", "url": "http://example.com/1", "content": "This is a test article.", "summary": "Test summary.", "feed_name": "Test Feed"}
        ]
        self._create_dummy_filtered_data(articles_data)
        
        result = self.step.execute()
        
        # Should fail gracefully due to model loading issues
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('model', result['error'].lower())

    def test_no_articles_input(self):
        """Test handling of empty input."""
        self._create_dummy_filtered_data([])
        result = self.step.execute()
        
        # Should handle empty input gracefully
        self.assertTrue(result['success'])
        self.assertEqual(result['articles_input'], 0)
        self.assertEqual(result['articles_passed'], 0)
        self.assertAlmostEqual(result['pass_rate'], 0.0)

    def test_text_preparation(self):
        """Test text preparation for classification."""
        articles_data = [
            {"title": "Short title", "summary": "This is a longer summary that provides more context for classification."},
            {"title": "This is a very long title that should be sufficient on its own for classification purposes", "summary": "Short summary."},
            {"title": "", "summary": "Only summary available."},
            {"title": "Title with <html> tags", "summary": "Summary with <script>alert('xss')</script> malicious content"}
        ]
        
        # Test text preparation
        for article in articles_data:
            prepared_text = self.step._prepare_text_for_classification(article)
            
            # Should be cleaned of HTML
            self.assertNotIn('<html>', prepared_text)
            self.assertNotIn('<script>', prepared_text)
            
            # Should not exceed max length
            self.assertLessEqual(len(prepared_text), 120)
            
            # Should prioritize title when available
            if article['title'] and len(article['title']) >= 50:
                self.assertIn(article['title'][:50], prepared_text)

    def test_clean_text_function(self):
        """Test the text cleaning function."""
        test_cases = [
            ("<p>Hello <strong>world</strong>!</p>", "Hello world!"),
            ("  Multiple   spaces   here  ", "Multiple spaces here"),
            ("Text with\n\nnewlines\t\tand\ttabs", "Text with newlines and tabs"),
            ("", ""),
            ("Normal text without HTML", "Normal text without HTML")
        ]
        
        for input_text, expected in test_cases:
            result = self.step._clean_text(input_text)
            self.assertEqual(result, expected)

    def test_should_include_article_logic(self):
        """Test the article inclusion logic."""
        # Mock classification results
        test_cases = [
            # (is_advertisement, confidence_score, expected_result)
            (False, 0.9, True),   # High confidence news
            (False, 0.3, False),  # Low confidence news
            (True, 0.9, False),   # High confidence ad
            (True, 0.3, False),   # Low confidence ad
        ]
        
        for is_ad, confidence, expected in test_cases:
            classification_result = {
                'is_advertisement': is_ad,
                'confidence_score': confidence
            }
            result = self.step._should_include_article(classification_result)
            self.assertEqual(result, expected, 
                           f"Failed for is_ad={is_ad}, confidence={confidence}")

    def test_configuration_loading(self):
        """Test that configuration is loaded correctly."""
        self.assertEqual(self.step.step_name, "ad_detection")
        self.assertIsNotNone(self.step.config)
        self.assertEqual(self.step.config['model']['name'], "SoroushXYZ/distilbert-rss-ad-detection")
        self.assertEqual(self.step.config['text_processing']['max_length'], 120)
        self.assertEqual(self.step.config['filtering']['min_news_confidence'], 0.5)


if __name__ == '__main__':
    unittest.main()
