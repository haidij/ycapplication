import json
import boto3
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Lambda function using the latest Bedrock API for YC coaching conversations
    """
    
    # Debug: List files in Lambda environment
    print("Files in Lambda environment:")
    for file in os.listdir('.'):
        print(f"  - {file}")
    
    # Initialize Bedrock client with latest API
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    try:
        # Parse the incoming request
        body = json.loads(event['body']) if event.get('body') else {}
        user_message = body.get('message', '')
        conversation_history = body.get('history', [])
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Message is required'})
            }
        
        # Load system prompt from file
        try:
            with open('system_prompt.txt', 'r', encoding='utf-8') as f:
                system_prompt = f.read().strip()
            print(f"✓ System prompt loaded successfully ({len(system_prompt)} chars)")
        except FileNotFoundError:
            print("❌ system_prompt.txt not found - using fallback")
            # Fallback prompt if file not found
            system_prompt = """You are an expert Y Combinator application coach. Help entrepreneurs perfect their answer to: "What is your company going to make? Please describe your product and what it does or will do."
            
Ask specific questions to help them clarify their problem, solution, target market, and value proposition. Be encouraging but direct about areas needing improvement."""
        except Exception as e:
            print(f"❌ Error reading system_prompt.txt: {e}")
            system_prompt = """You are an expert Y Combinator application coach. Help entrepreneurs perfect their answer to: "What is your company going to make? Please describe your product and what it does or will do."
            
Ask specific questions to help them clarify their problem, solution, target market, and value proposition. Be encouraging but direct about areas needing improvement."""

        # Prepare conversation for the new Bedrock API
        messages = []
        
        # Add conversation history (only if it exists and is valid)
        if conversation_history and isinstance(conversation_history, list):
            for msg in conversation_history:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    messages.append({
                        "role": msg["role"],
                        "content": [{"type": "text", "text": str(msg["content"])}]
                    })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": user_message}]
        })
        
        print(f"Prepared {len(messages)} messages for Bedrock")
        
        # Ensure we have at least one message
        if not messages:
            raise Exception("No messages to send to Bedrock")
        
        # Use the latest Bedrock API with correct format
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "system": system_prompt,
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        # Call Bedrock with working model ID
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            body=json.dumps(request_body),
            contentType='application/json',
            accept='application/json'
        )
        
        # Parse response using new API format
        response_body = json.loads(response['body'].read())
        ai_response = response_body['content'][0]['text']
        
        # Enhanced response with metadata
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'response': ai_response,
                'model_used': 'claude-3-5-sonnet-v2',
                'timestamp': context.aws_request_id,
                'tokens_used': response_body.get('usage', {}).get('output_tokens', 0)
            })
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"Bedrock API error: {error_code} - {e}")
        
        if error_code == 'AccessDeniedException':
            error_msg = 'Bedrock access denied. Please check model permissions.'
        elif error_code == 'ThrottlingException':
            error_msg = 'Too many requests. Please wait a moment and try again.'
        elif error_code == 'ValidationException':
            error_msg = 'Invalid request format. Please try again.'
        else:
            error_msg = 'AI service temporarily unavailable. Please try again.'
            
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': error_msg})
        }
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': 'Internal server error'})
        }

def get_cors_headers():
    """Return CORS headers optimized for the new API"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Access-Control-Max-Age': '86400',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
