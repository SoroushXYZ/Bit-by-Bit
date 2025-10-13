#!/usr/bin/env python3
"""
Test script for the Bit-by-Bit Backend API.
"""

import requests
import json
import sys
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Test an API endpoint."""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except requests.exceptions.ConnectionError:
        return {
            "endpoint": endpoint,
            "method": method,
            "error": "Connection failed - is the server running?",
            "success": False
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "error": str(e),
            "success": False
        }

def main():
    """Run API tests."""
    print("🧪 Testing Bit-by-Bit Backend API")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ("/", "GET"),
        ("/health", "GET"),
        ("/data/runs", "GET"),
        ("/data/stats", "GET"),
        ("/data/update", "POST"),
    ]
    
    results = []
    for endpoint, method in endpoints:
        print(f"\n🔍 Testing {method} {endpoint}")
        result = test_endpoint(endpoint, method)
        results.append(result)
        
        if result["success"]:
            print(f"  ✅ Status: {result['status_code']}")
            if "data" in result and isinstance(result["data"], dict):
                # Show key info from response
                if "total_runs" in result["data"]:
                    print(f"  📊 Total runs: {result['data']['total_runs']}")
                if "status" in result["data"]:
                    print(f"  📋 Status: {result['data']['status']}")
        else:
            print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
    
    # Test specific run endpoint if we have runs
    runs_result = next((r for r in results if r["endpoint"] == "/data/runs"), None)
    if runs_result and runs_result["success"] and runs_result["data"].get("total_runs", 0) > 0:
        print(f"\n🔍 Testing specific run endpoint")
        run_id = runs_result["data"]["runs"][0]["run_id"]
        run_result = test_endpoint(f"/data/runs/{run_id}?summary=true", "GET")
        results.append(run_result)
        
        if run_result["success"]:
            print(f"  ✅ Run {run_id} data retrieved")
        else:
            print(f"  ❌ Failed to get run data: {run_result.get('error')}")
    
    # Summary
    successful_tests = sum(1 for r in results if r["success"])
    total_tests = len(results)
    
    print(f"\n📊 Test Summary:")
    print(f"  ✅ Successful: {successful_tests}/{total_tests}")
    print(f"  ❌ Failed: {total_tests - successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
