#!/usr/bin/env python3
"""
Simple test script to debug Together AI API calls.
This will help us see exactly what's being returned from the API.
"""

import os
import sys
import json
from pathlib import Path

# Add the pipeline src to the path
pipeline_dir = Path(__file__).parent.parent
sys.path.insert(0, str(pipeline_dir / "src"))

# Import with proper path handling
import importlib.util
spec = importlib.util.spec_from_file_location("together_client", pipeline_dir / "src" / "utils" / "together_client.py")
together_client_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(together_client_module)

spec = importlib.util.spec_from_file_location("config_loader", pipeline_dir / "src" / "utils" / "config_loader.py")
config_loader_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_loader_module)

create_together_client = together_client_module.create_together_client
ConfigLoader = config_loader_module.ConfigLoader

def test_together_ai():
    """Test Together AI API with a simple prompt."""
    
    print("🔧 Testing Together AI API...")
    
    # Load configuration
    config_loader = ConfigLoader()
    global_config = config_loader.global_config
    
    print(f"📋 Global config loaded: {bool(global_config)}")
    
    # Get LLM config
    llm_config = global_config.get('llm', {})
    print(f"🤖 LLM config: {json.dumps(llm_config, indent=2)}")
    
    # Create Together AI client
    try:
        together_config = llm_config.get('together_ai', {})
        print(f"🔑 Together AI config: {json.dumps(together_config, indent=2)}")
        
        client = create_together_client(together_config)
        print("✅ Together AI client created successfully")
        
    except Exception as e:
        print(f"❌ Failed to create Together AI client: {e}")
        return
    
    # Test simple completion
    print("\n🧪 Testing simple completion...")
    try:
        simple_prompt = "Hello, please respond with just 'Hello World'"
        response = client.generate_completion(simple_prompt)
        print(f"📝 Simple response: {repr(response)}")
        print(f"📝 Simple response (formatted): {response}")
        
    except Exception as e:
        print(f"❌ Simple completion failed: {e}")
        return
    
    # Test JSON completion
    print("\n🧪 Testing JSON completion...")
    try:
        json_prompt = """Please respond with a simple JSON object like this:
        {
            "status": "success",
            "message": "test completed"
        }"""
        
        response = client.generate_json_completion(json_prompt)
        print(f"📝 JSON response: {repr(response)}")
        print(f"📝 JSON response (formatted): {json.dumps(response, indent=2)}")
        
    except Exception as e:
        print(f"❌ JSON completion failed: {e}")
        print(f"❌ Error type: {type(e)}")
        print(f"❌ Error args: {e.args}")
        return
    
    # Test the actual quality analysis prompt
    print("\n🧪 Testing quality analysis prompt...")
    try:
        quality_prompt = """Analyze the following article for quality and provide a JSON response:

Title: Test Article
Description: This is a test article for quality analysis
Content: This is a test article about technology and innovation.

Please provide a JSON response with the following structure:
{
    "technical_depth": 85,
    "news_value": 90,
    "clarity_readability": 92,
    "impact_relevance": 95,
    "originality": 80,
    "overall_quality": 90,
    "content_type": "news",
    "tech_relevance": "high",
    "target_audience": "intermediate",
    "key_strengths": ["strength1", "strength2"],
    "key_weaknesses": ["weakness1", "weakness2"],
    "reasoning": "brief explanation of overall assessment"
}"""
        
        response = client.generate_json_completion(quality_prompt)
        print(f"📝 Quality analysis response: {repr(response)}")
        print(f"📝 Quality analysis response (formatted): {json.dumps(response, indent=2)}")
        
    except Exception as e:
        print(f"❌ Quality analysis failed: {e}")
        print(f"❌ Error type: {type(e)}")
        print(f"❌ Error args: {e.args}")
        return
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_together_ai()
