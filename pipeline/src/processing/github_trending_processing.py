"""
GitHub Trending Processing Module

This module handles processing GitHub trending repositories for newsletter integration.
Includes LLM ranking, description generation, and newsletter formatting.
"""

import sys
import json
import time
import requests
import re
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader


class GitHubTrendingProcessor:
    """Processes GitHub trending repositories for newsletter integration."""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize the GitHub trending processor."""
        self.config_loader = config_loader
        self.logger = get_logger()
        
        # Load GitHub trending specific config
        self.config = self.config_loader.get_step_config('github_trending')
        
        # Load global config for LLM settings
        self.global_config = self.config_loader.global_config
        
        # LLM settings
        self.ollama_host = self.global_config.get('llm', {}).get('ollama_host', '172.22.128.1')
        self.model_name = self.global_config.get('llm', {}).get('model', 'llama3.2:3b')
        self.api_url = f"http://{self.ollama_host}:11434/api/generate"
        
        # Set random seed for reproducible results
        random.seed(42)
        
        self.logger.info("GitHub trending processor initialized with seed 42")
    
    def _create_ranking_prompt(self, repositories: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for ranking repositories based on impact and innovation.
        
        Args:
            repositories: List of repository data
            
        Returns:
            str: Formatted prompt for LLM
        """
        prompt = """You are an expert tech analyst. Your task is to rank the provided GitHub repositories from 1–10 based on their potential impact and innovation.

Ranking criteria:
1. Innovation & Technical Merit: How novel or technically impressive is the project?
2. Potential Impact: How likely is this to influence the developer community or industry?
3. Practical Value: How useful would this be for developers?
4. Code Quality Indicators: Based on README quality and project description.
5. Trending Potential: How likely is this to continue growing in popularity?

STRICT OUTPUT RULES:
- Respond with ONLY a valid JSON object.
- Do not include markdown code blocks, explanations, comments, or extra text.
- Each repo must have a unique rank from 1–10.
- Use repo_name exactly as provided (no modifications).
- Each reason must be ≤25 words and reference one or more ranking criteria.
- overall_analysis must be ≤50 words summarizing observed quality and trends.

Required JSON format:
{
  "rankings": [
    {"rank": 1, "repo_name": "exact_repo_name", "reason": "brief explanation"},
    ...
    {"rank": 10, "repo_name": "exact_repo_name", "reason": "brief explanation"}
  ],
  "overall_analysis": "Brief summary of overall quality and trends"
}

Repositories to rank:

"""
        
        for i, repo in enumerate(repositories, 1):
            prompt += f"{i}. **{repo['repo_name']}** ({repo['primary_language']}) - {repo['stars']} stars\n"
            prompt += f"   Description: {repo['description']}\n"
            
            if repo.get('readme_preview'):
                prompt += f"   README: {repo['readme_preview']}\n"
            else:
                prompt += f"   README: Not available\n"
            prompt += "\n"
        
        return prompt
    
    def _get_llm_ranking(self, repositories: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Get ranking from LLM via Ollama.
        
        Args:
            repositories: List of repository data
            
        Returns:
            dict: LLM ranking response or None if failed
        """
        prompt = self._create_ranking_prompt(repositories)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more consistent rankings
                "top_p": 0.9,
                "max_tokens": 2000
            }
        }
        
        try:
            self.logger.info(f"🤖 Sending ranking request to Ollama at {self.ollama_host}...")
            response = requests.post(self.api_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get('response', '')
                self.logger.info(f"✅ LLM ranking response received ({len(llm_response)} characters)")
                return llm_response
            else:
                self.logger.error(f"❌ Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Connection error to Ollama: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}")
            return None
    
    def _parse_llm_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse LLM response and extract JSON ranking.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            dict: Parsed ranking data or None if failed
        """
        if not response_text:
            return None
        
        # Clean the response text
        response_text = response_text.strip()
        
        try:
            # Method 1: Try to parse the entire response as JSON
            try:
                ranking_data = json.loads(response_text)
                return ranking_data
            except:
                pass
            
            # Method 2: Try to find JSON object in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                ranking_data = json.loads(json_str)
                return ranking_data
            
            # Method 3: Try to extract from markdown code blocks
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                if end > start:
                    json_str = response_text[start:end].strip()
                    ranking_data = json.loads(json_str)
                    return ranking_data
            
            # Method 4: Try to extract from code blocks without json marker
            if '```' in response_text:
                parts = response_text.split('```')
                for part in parts:
                    part = part.strip()
                    if part.startswith('{') and part.endswith('}'):
                        try:
                            ranking_data = json.loads(part)
                            return ranking_data
                        except:
                            continue
            
            self.logger.warning("⚠️  No valid JSON found in LLM response")
            return None
                
        except json.JSONDecodeError as e:
            self.logger.warning(f"⚠️  JSON parsing error: {e}")
            return None
        except Exception as e:
            self.logger.warning(f"⚠️  Unexpected parsing error: {e}")
            return None
    
    def _create_description_prompt(self, repo_info: Dict[str, Any]) -> str:
        """
        Create a prompt for generating repository descriptions.
        
        Args:
            repo_info: Repository information
            
        Returns:
            str: Formatted prompt for LLM
        """
        prompt = f"""You are a technical writer for a developer-focused newsletter.  
Write a 1–2 sentence description of the given GitHub repository.  

Requirements:
- Maximum 25 words.  
- Simple, clear, and jargon-free.  
- Focus only on what the project does.  
- No hype, no extra details.  

Input: {repo_info['repo_name']} - {repo_info['description']}

Output: Plain text, 1–2 sentences."""
        
        return prompt
    
    def _generate_description(self, repo_info: Dict[str, Any]) -> Optional[str]:
        """
        Generate description for a single repository.
        
        Args:
            repo_info: Repository information
            
        Returns:
            str: Generated description or None if failed
        """
        prompt = self._create_description_prompt(repo_info)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "max_tokens": 150  # Keep it short
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                description = result.get('response', '').strip()
                
                # Clean up the description
                if description:
                    # Remove any markdown formatting
                    description = description.replace('**', '').replace('*', '').replace('`', '')
                    # Remove extra whitespace
                    description = ' '.join(description.split())
                    return description
            
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️  Description generation failed for {repo_info['repo_name']}: {e}")
            return None
    
    def _load_github_data(self) -> Optional[Dict[str, Any]]:
        """
        Load GitHub trending data from the most recent file.
        
        Returns:
            dict: GitHub trending data or None if not found
        """
        try:
            data_dir = Path('data/raw')
            github_files = list(data_dir.glob('github_trending_*.json'))
            
            if not github_files:
                self.logger.error("No GitHub trending data files found")
                return None
            
            # Get the most recent file
            latest_file = max(github_files, key=lambda f: f.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"Loaded GitHub data from: {latest_file}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to load GitHub data: {e}")
            return None
    
    def _prepare_repositories_for_processing(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Prepare repository data for LLM processing.
        
        Args:
            data: GitHub trending data
            
        Returns:
            List of prepared repository data
        """
        repositories = data.get('repositories', [])
        
        # Prepare data for LLM processing
        repo_data_for_llm = []
        
        for repo in repositories:
            repo_info = {
                'repo_name': repo.get('repo_name', ''),
                'primary_language': repo.get('primary_language', ''),
                'stars': int(repo.get('stars', 0)),
                'description': repo.get('description', ''),
                'readme_preview': None
            }
            
            # Add README preview if available
            if repo.get('status') == 'success' and repo.get('readme_content'):
                readme_text = str(repo['readme_content'])
                # Get first 100 words (approximate)
                words = readme_text.split()[:100]
                repo_info['readme_preview'] = ' '.join(words)
            
            repo_data_for_llm.append(repo_info)
        
        return repo_data_for_llm
    
    def _process_repositories_for_newsletter(self, repositories: List[Dict[str, Any]], 
                                           llm_ranking: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Process repositories for newsletter integration.
        
        Args:
            repositories: List of repository data
            llm_ranking: Optional LLM ranking data
            
        Returns:
            List of processed repositories for newsletter
        """
        # Determine which ranking to use
        if llm_ranking and llm_ranking.get('rankings'):
            self.logger.info("🎯 Using LLM ranking for repository order")
            # Use LLM ranking order
            ranked_repos = []
            for ranking in llm_ranking['rankings']:
                repo_name = ranking['repo_name']
                # Find the repo data
                original_repo = next((r for r in repositories if r['repo_name'] == repo_name), None)
                if original_repo:
                    ranked_repos.append(original_repo)
            
            # Add any repos that weren't in the LLM ranking
            for repo in repositories:
                if repo not in ranked_repos:
                    ranked_repos.append(repo)
                    
            repositories_to_process = ranked_repos[:5]  # Top 5 for newsletter
            ranking_source = "LLM"
            
        else:
            self.logger.info("📊 Using API ranking (by stars) for repository order")
            repositories_to_process = repositories[:5]  # Top 5 by stars
            ranking_source = "API"
        
        self.logger.info(f"📋 Processing top {len(repositories_to_process)} repositories ({ranking_source} ranking)")
        
        # Generate descriptions for newsletter
        newsletter_repos = []
        
        for i, repo in enumerate(repositories_to_process, 1):
            self.logger.info(f"📝 Processing {repo['repo_name']} ({i}/{len(repositories_to_process)})")
            
            # Try to generate description
            summary = self._generate_description(repo)
            
            if summary:
                repo_info = {
                    "rank": i,
                    "repo_name": repo['repo_name'],
                    "primary_language": repo.get('primary_language', ''),
                    "stars": repo.get('stars', 0),
                    "github_url": f"https://github.com/{repo['repo_name']}",
                    "original_description": repo['description'],
                    "summary": summary,
                    "status": "success"
                }
                newsletter_repos.append(repo_info)
                self.logger.info(f"   ✅ Generated: {summary[:80]}...")
                
                # Stop after first success for now (as per research notebook)
                break
            else:
                self.logger.warning(f"   ❌ Failed to generate description for {repo['repo_name']}")
        
        # If no successful descriptions, use fallback
        if not newsletter_repos:
            self.logger.warning("🔄 No successful descriptions, using fallback repository")
            fallback_repo = {
                "rank": 1,
                "repo_name": "bahamas10/ysap",
                "github_url": "https://github.com/bahamas10/ysap",
                "description": "Our content pipeline encountered technical difficulties. We're working to restore normal service and will have fresh trending repositories for you soon. Please come back tomorrow!",
                "status": "fallback"
            }
            newsletter_repos.append(fallback_repo)
        
        successful_count = len([r for r in newsletter_repos if r.get('status') == 'success'])
        
        self.logger.info(f"📊 Description Generation Summary:")
        self.logger.info(f"   Attempted repositories: {len(repositories_to_process)}")
        self.logger.info(f"   Successful descriptions: {successful_count}")
        self.logger.info(f"   Final result: {'Success' if successful_count > 0 else 'Fallback used'}")
        
        return newsletter_repos
    
    def process(self) -> Dict[str, Any]:
        """
        Process GitHub trending repositories for newsletter integration.
        
        Returns:
            dict: Processing results with success status and data
        """
        try:
            self.logger.info("🚀 Starting GitHub trending processing")
            
            # Load GitHub trending data
            github_data = self._load_github_data()
            if not github_data:
                self.logger.warning("⚠️  No GitHub trending data available, using fallback")
                # Create fallback data structure
                fallback_data = {
                    "metadata": {
                        "title": "Trending GitHub Repositories",
                        "subtitle": "Top repositories from the past 24 hours",
                        "generated_at": datetime.now().isoformat(),
                        "ranking_source": "Fallback",
                        "total_repositories": 1,
                        "source_data": {
                            "total_fetched": 0,
                            "total_filtered": 0,
                            "total_with_readme": 0
                        }
                    },
                    "repositories": [{
                        "rank": 1,
                        "repo_name": "bahamas10/ysap",
                        "primary_language": "Shell",
                        "stars": 642,
                        "github_url": "https://github.com/bahamas10/ysap",
                        "original_description": "You Suck at Programming - A series on programming (actually just bash scripting) on youtube, tiktok and instagram hosted by Dave Eddy.",
                        "summary": "Our content pipeline encountered technical difficulties. We're working to restore normal service and will have fresh trending repositories for you soon. Please come back tomorrow!",
                        "status": "fallback"
                    }]
                }
                
                # Save fallback data
                self._save_processed_data(fallback_data)
                
                return {
                    'success': True,
                    'processed_count': 1,
                    'data': fallback_data,
                    'metadata': fallback_data['metadata']
                }
            
            # Prepare repositories for processing
            repositories = self._prepare_repositories_for_processing(github_data)
            if not repositories:
                self.logger.warning("⚠️  No repositories found in GitHub data, using fallback")
                # Create fallback data structure
                fallback_data = {
                    "metadata": {
                        "title": "Trending GitHub Repositories",
                        "subtitle": "Top repositories from the past 24 hours",
                        "generated_at": datetime.now().isoformat(),
                        "ranking_source": "Fallback",
                        "total_repositories": 1,
                        "source_data": {
                            "total_fetched": 0,
                            "total_filtered": 0,
                            "total_with_readme": 0
                        }
                    },
                    "repositories": [{
                        "rank": 1,
                        "repo_name": "bahamas10/ysap",
                        "primary_language": "Shell",
                        "stars": 642,
                        "github_url": "https://github.com/bahamas10/ysap",
                        "original_description": "You Suck at Programming - A series on programming (actually just bash scripting) on youtube, tiktok and instagram hosted by Dave Eddy.",
                        "summary": "Our content pipeline encountered technical difficulties. We're working to restore normal service and will have fresh trending repositories for you soon. Please come back tomorrow!",
                        "status": "fallback"
                    }]
                }
                
                # Save fallback data
                self._save_processed_data(fallback_data)
                
                return {
                    'success': True,
                    'processed_count': 1,
                    'data': fallback_data,
                    'metadata': fallback_data['metadata']
                }
            
            self.logger.info(f"📊 Prepared {len(repositories)} repositories for processing")
            
            # Get LLM ranking for top repositories
            top_repos = repositories[:10]  # Top 10 for ranking
            llm_ranking = None
            
            try:
                llm_response = self._get_llm_ranking(top_repos)
                if llm_response:
                    llm_ranking = self._parse_llm_response(llm_response)
                    if llm_ranking:
                        self.logger.info("✅ LLM ranking successful")
                    else:
                        self.logger.warning("⚠️  LLM ranking parsing failed")
                else:
                    self.logger.warning("⚠️  LLM ranking request failed")
            except Exception as e:
                self.logger.warning(f"⚠️  LLM ranking error: {e}")
            
            # Process repositories for newsletter
            newsletter_repos = self._process_repositories_for_newsletter(repositories, llm_ranking)
            
            # Create final newsletter data structure
            newsletter_data = {
                "metadata": {
                    "title": "Trending GitHub Repositories",
                    "subtitle": "Top repositories from the past 24 hours",
                    "generated_at": datetime.now().isoformat(),
                    "ranking_source": "LLM" if llm_ranking else "API",
                    "total_repositories": len(newsletter_repos),
                    "source_data": {
                        "total_fetched": github_data.get('metadata', {}).get('total_fetched', 0),
                        "total_filtered": github_data.get('metadata', {}).get('total_filtered', 0),
                        "total_with_readme": github_data.get('metadata', {}).get('total_with_readme', 0)
                    }
                },
                "repositories": newsletter_repos
            }
            
            # Save processed data
            self._save_processed_data(newsletter_data)
            
            result = {
                'success': True,
                'processed_count': len(newsletter_repos),
                'data': newsletter_data,
                'metadata': newsletter_data['metadata']
            }
            
            self.logger.info(f"✅ GitHub trending processing completed: {result['processed_count']} repositories processed")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ GitHub trending processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'processed_count': 0
            }
    
    def _save_processed_data(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Save processed data to file.
        
        Args:
            data: Processed data to save
            
        Returns:
            str: Path to saved file or None if failed
        """
        try:
            # Create processed directory (intermediate processing)
            processed_dir = Path('data/processed')
            processed_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"github_trending_{timestamp}.json"
            
            output_path = processed_dir / filename
            
            # Save data
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 GitHub trending processed data saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save GitHub trending output: {e}")
            return None
