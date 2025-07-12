#!/usr/bin/env python3
"""
Test script for the new Bedrock API
"""
import boto3
import json
from botocore.exceptions import ClientError

def test_bedrock_api():
    """Test the latest Bedrock API with Claude 3.5 Sonnet v2"""
    
    print("🧪 Testing Bedrock API...")
    
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test message
        test_message = "I'm building a platform that helps small businesses manage their inventory better. What questions should I ask myself to improve this description for YC?"
        
        # Prepare request using new API format
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "system": [{"text": "You are a YC application coach. Help improve startup descriptions."}],
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": test_message}]
                }
            ],
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        # Try Claude 3.5 Sonnet v2 first (latest)
        models_to_try = [
            'anthropic.claude-3-5-sonnet-20241022-v2:0',
            'anthropic.claude-3-5-sonnet-20240620-v1:0',
            'anthropic.claude-3-sonnet-20240229-v1:0'
        ]
        
        for model_id in models_to_try:
            try:
                print(f"Testing model: {model_id}")
                
                response = bedrock.invoke_model(
                    modelId=model_id,
                    body=json.dumps(request_body),
                    contentType='application/json',
                    accept='application/json'
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                ai_response = response_body['content'][0]['text']
                
                print(f"✅ Success with {model_id}")
                print(f"Response preview: {ai_response[:200]}...")
                
                # Show usage info if available
                if 'usage' in response_body:
                    usage = response_body['usage']
                    print(f"Tokens used: {usage.get('output_tokens', 'N/A')}")
                
                return True
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                print(f"❌ {model_id} failed: {error_code}")
                
                if error_code == 'AccessDeniedException':
                    print(f"   Need to request access to {model_id}")
                elif error_code == 'ValidationException':
                    print(f"   Model {model_id} may not exist or format is wrong")
                
                continue
        
        print("❌ All models failed. Check your Bedrock access.")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def list_available_models():
    """List all available Bedrock models"""
    try:
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        models = bedrock.list_foundation_models()
        
        print("\n📋 Available Bedrock Models:")
        claude_models = [m for m in models['modelSummaries'] if 'claude' in m['modelId'].lower()]
        
        for model in claude_models:
            print(f"  - {model['modelId']}")
            
        return claude_models
        
    except Exception as e:
        print(f"Error listing models: {e}")
        return []

if __name__ == "__main__":
    print("🚀 Bedrock API Test Suite")
    print("=" * 40)
    
    # List available models
    models = list_available_models()
    
    if models:
        # Test API
        success = test_bedrock_api()
        
        if success:
            print("\n✅ Bedrock API is working correctly!")
            print("You can proceed with deployment.")
        else:
            print("\n❌ Bedrock API test failed.")
            print("Check your AWS permissions and model access.")
    else:
        print("\n❌ No Claude models available.")
        print("Please request access in the Bedrock console.")
