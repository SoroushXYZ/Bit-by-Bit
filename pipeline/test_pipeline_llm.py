#!/usr/bin/env python3
"""
Test that mimics the exact pipeline LLM call to debug the 'success' error.
"""

import json
from src.utils.together_client import create_together_client
from src.utils.config_loader import ConfigLoader

# Load configuration
config_loader = ConfigLoader()
global_config = config_loader.global_config
llm_config = global_config.get('llm', {})
together_config = llm_config.get('together_ai', {})

# Create client
client = create_together_client(together_config)

# Test a quality analysis prompt (exactly as the pipeline does)
test_article = {
    'title': 'Test Article',
    'description': 'This is a test',
    'content': 'This is test content about technology.'
}

prompt = f"""Analyze the following article for content quality. Provide scores and assessment in JSON format.

Title: {test_article['title']}
Description: {test_article['description']}
Content: {test_article['content'][:500]}

Provide your response as a JSON object with this exact structure:
{{
    "technical_depth": <score 0-100>,
    "news_value": <score 0-100>,
    "clarity_readability": <score 0-100>,
    "impact_relevance": <score 0-100>,
    "originality": <score 0-100>,
    "overall_quality": <score 0-100>,
    "content_type": "<news|tutorial|analysis|opinion>",
    "tech_relevance": "<high|medium|low>",
    "target_audience": "<beginner|intermediate|advanced>",
    "key_strengths": ["<strength1>", "<strength2>"],
    "key_weaknesses": ["<weakness1>", "<weakness2>"],
    "reasoning": "<brief explanation of overall assessment>"
}}

Focus on content that would be valuable for tech professionals, entrepreneurs, and tech enthusiasts. Be strict with quality standards."""

print("🧪 Testing LLM quality analysis call...")
print(f"📝 Prompt length: {len(prompt)} characters")

try:
    response = client.generate_json_completion(prompt)
    print(f"\n✅ SUCCESS!")
    print(f"📝 Response type: {type(response)}")
    print(f"📝 Response: {json.dumps(response, indent=2)}")
    
except Exception as e:
    print(f"\n❌ FAILED!")
    print(f"❌ Error type: {type(e)}")
    print(f"❌ Error message: {e}")
    print(f"❌ Error args: {e.args}")
    print(f"❌ Error repr: {repr(e)}")
    
    import traceback
    print("\n📋 Full traceback:")
    traceback.print_exc()

