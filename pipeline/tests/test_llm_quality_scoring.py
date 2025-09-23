#!/usr/bin/env python3
"""
Test script for the LLM Quality Scoring Step.
"""

import unittest
import json
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import initialize_logger, load_pipeline_config
from steps import LLMQualityScoringStep


class TestLLMQualityScoringStep(unittest.TestCase):
    def setUp(self):
        # Initialize logger for tests
        initialize_logger('pipeline/config/pipeline_config.json')
        
        # Create a dummy pipeline config for testing
        self.pipeline_config_path = Path("pipeline/config/test_pipeline_config.json")
        self.ad_detection_config_path = Path("pipeline/config/test_ad_detection_config.json")
        self.llm_quality_config_path = Path("pipeline/config/test_llm_quality_config.json")
        
        self.data_dir = Path("pipeline/data/test_raw")
        self.processed_dir = Path("pipeline/data/test_processed")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # Dummy pipeline config
        pipeline_config_content = {
            "pipeline_name": "Test Pipeline",
            "logging": {"level": "DEBUG", "file": "test_llm_quality.log"},
            "data": {
                "base_path": "pipeline/data",
                "raw_data_path": str(self.data_dir),
                "processed_data_path": str(self.processed_dir),
                "output_data_path": "pipeline/data/test_output"
            },
            "steps": {
                "ad_detection": {
                    "enabled": True, "order": 3, "description": "Test Ad Detection",
                    "config_file": str(self.ad_detection_config_path)
                },
                "llm_quality_scoring": {
                    "enabled": True, "order": 4, "description": "Test LLM Quality",
                    "config_file": str(self.llm_quality_config_path)
                }
            }
        }
        with open(self.pipeline_config_path, 'w') as f:
            json.dump(pipeline_config_content, f)

        # Dummy ad detection config (minimal, just for data paths)
        ad_detection_config_content = {
            "step_name": "ad_detection",
            "output": {"filename_prefix": "test_ad_filtered_content", "save_format": "json"}
        }
        with open(self.ad_detection_config_path, 'w') as f:
            json.dump(ad_detection_config_content, f)

        # Dummy LLM quality scoring config
        llm_quality_config_content = {
            "step_name": "llm_quality_scoring",
            "input": {"source_step": "ad_detection", "filename_prefix": "test_ad_filtered_content"},
            "output": {"filename_prefix": "test_quality_scored_content", "save_format": "json"},
            "llm": {
                "server_url": "http://localhost:11434",
                "model": "llama3.2:3b",
                "temperature": 0.3,
                "seed": 42,
                "max_tokens": 2000,
                "max_retries": 3
            },
            "scoring": {"min_quality_score": 65},
            "error_handling": {"continue_on_article_error": True, "include_on_llm_error": True}
        }
        with open(self.llm_quality_config_path, 'w') as f:
            json.dump(llm_quality_config_content, f)

        self.config_loader = load_pipeline_config(str(self.pipeline_config_path))
        self.step = LLMQualityScoringStep(self.config_loader)

    def tearDown(self):
        # Clean up dummy config and data files
        self.pipeline_config_path.unlink(missing_ok=True)
        self.ad_detection_config_path.unlink(missing_ok=True)
        self.llm_quality_config_path.unlink(missing_ok=True)
        for f in self.data_dir.glob("*"): f.unlink()
        self.data_dir.rmdir()
        for f in self.processed_dir.glob("*"): f.unlink()
        self.processed_dir.rmdir()
        Path("test_llm_quality.log").unlink(missing_ok=True)

    def _create_dummy_ad_filtered_data(self, articles_data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_ad_filtered_content_{timestamp}.json"
        filepath = self.processed_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({"articles": articles_data}, f, indent=2, ensure_ascii=False)
        return filepath

    def test_configuration_loading(self):
        """Test that configuration is loaded correctly."""
        self.assertEqual(self.step.step_name, "llm_quality_scoring")
        self.assertIsNotNone(self.step.config)
        self.assertEqual(self.step.llm_config['model'], "llama3.2:3b")
        self.assertEqual(self.step.scoring_config['min_quality_score'], 65)

    def test_text_cleaning_function(self):
        """Test the text cleaning function."""
        test_cases = [
            ("<p>Hello <strong>world</strong>!</p>", "Hello world!"),
            ("  Multiple   spaces   here  ", "Multiple spaces here"),
            ("Text with\n\nnewlines\t\tand\ttabs", "Text with newlines and tabs"),
            ("", ""),
            ("Normal text without HTML", "Normal text without HTML"),
            ("Text with [special] chars!", "Text with special chars!")
        ]
        
        for input_text, expected in test_cases:
            result = self.step._clean_text(input_text)
            self.assertEqual(result, expected)

    def test_content_truncation(self):
        """Test content truncation functionality."""
        long_content = "This is a test sentence. " * 100  # Very long content
        
        truncated = self.step._truncate_content(long_content, 100)
        
        # Should be significantly shorter
        self.assertLess(len(truncated), len(long_content))
        
        # Should end with ellipsis if truncated
        if len(truncated) < len(long_content):
            self.assertTrue(truncated.endswith("..."))
        
        # Short content should not be truncated
        short_content = "Short content"
        self.assertEqual(self.step._truncate_content(short_content, 100), short_content)


    def test_quality_metrics_calculation(self):
        """Test quality metrics calculation."""
        mock_analysis = {
            'technical_depth': 80,
            'news_value': 75,
            'clarity_readability': 85,
            'impact_relevance': 70,
            'originality': 90,
            'overall_quality': 80
        }
        
        metrics = self.step._calculate_quality_metrics(mock_analysis)
        
        self.assertEqual(metrics['scores'], mock_analysis)
        self.assertAlmostEqual(metrics['average_score'], 80.0)
        self.assertEqual(metrics['min_score'], 70)
        self.assertEqual(metrics['max_score'], 90)
        self.assertEqual(metrics['quality_level'], 'high')
        self.assertEqual(metrics['score_consistency'], 20.0)

    def test_quality_level_classification(self):
        """Test quality level classification."""
        test_cases = [
            (90, 'excellent'),
            (80, 'high'),
            (70, 'good'),
            (60, 'fair'),
            (50, 'poor')
        ]
        
        for score, expected_level in test_cases:
            mock_analysis = {
                'technical_depth': score,
                'news_value': score,
                'clarity_readability': score,
                'impact_relevance': score,
                'originality': score,
                'overall_quality': score
            }
            
            metrics = self.step._calculate_quality_metrics(mock_analysis)
            self.assertEqual(metrics['quality_level'], expected_level)

    def test_should_include_article_logic(self):
        """Test the article inclusion logic."""
        # Test high quality article
        high_quality_metrics = {'average_score': 80}
        self.assertTrue(self.step._should_include_article(high_quality_metrics))
        
        # Test low quality article
        low_quality_metrics = {'average_score': 50}
        self.assertFalse(self.step._should_include_article(low_quality_metrics))
        
        # Test borderline article
        borderline_metrics = {'average_score': 65}
        self.assertTrue(self.step._should_include_article(borderline_metrics))

    def test_no_articles_input(self):
        """Test handling of empty input."""
        self._create_dummy_ad_filtered_data([])
        result = self.step.execute()
        
        # Should handle empty input gracefully
        self.assertTrue(result['success'])
        self.assertEqual(result['articles_input'], 0)
        self.assertEqual(result['articles_passed'], 0)
        self.assertAlmostEqual(result['pass_rate'], 0.0)

    def test_prompt_generation(self):
        """Test that prompts are generated correctly."""
        article = {
            'title': 'Test Article Title',
            'content': 'This is test content for the article.'
        }
        
        prompt = self.step._create_quality_analysis_prompt(article)
        
        # Should contain article details
        self.assertIn('Test Article Title', prompt)
        self.assertIn('This is test content', prompt)
        
        # Should contain evaluation criteria
        self.assertIn('Technical Depth', prompt)
        self.assertIn('News Value', prompt)
        self.assertIn('Clarity & Readability', prompt)
        
        # Should contain JSON format specification
        self.assertIn('JSON object', prompt)
        self.assertIn('technical_depth', prompt)
        self.assertIn('overall_quality', prompt)


if __name__ == '__main__':
    unittest.main()
