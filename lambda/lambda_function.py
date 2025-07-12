import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Lambda function using the latest Bedrock API for YC coaching conversations
    """
    
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
        
        # Enhanced coaching prompt optimized for the new API
        system_prompt = """You are an expert Y Combinator application coach with deep experience helping startups get accepted. Your specific task is to help entrepreneurs perfect their answer to: "What is your company going to make? Please describe your product and what it does or will do."

COACHING METHODOLOGY:
1. **Problem Clarity**: Ensure they clearly articulate the specific problem
2. **Solution Specificity**: Help them explain their solution concretely 
3. **Target Market**: Guide them to identify their exact customer
4. **Differentiation**: Help them explain what makes their approach unique
5. **Traction Indicators**: Encourage mention of early validation/progress

SUCCESSFUL YC ANSWERS TYPICALLY:
- Start with a relatable, specific problem statement
- Explain the solution in simple, jargon-free language
- Identify a clear target market (not "everyone")
- Show understanding of existing alternatives
- Demonstrate early traction or validation
- Are concise but comprehensive (2-4 sentences ideal)

COACHING STYLE:
- Ask specific, actionable follow-up questions
- Point out vague language and ask for concrete examples
- Be encouraging but direct about areas needing improvement
- Help them iterate toward a compelling, clear answer
- Reference what makes YC applications successful

Focus on one key improvement area per response. Ask specific questions that lead to better clarity."""

        # Prepare conversation for the new Bedrock API
        messages = []
        
        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": [{"text": msg["content"]}]
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": [{"text": user_message}]
        })
        
        # Use the latest Bedrock API with enhanced parameters
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "system": [{"text": system_prompt}],
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.9,
            "stop_sequences": ["Human:", "Assistant:"]
        }
        
        # Call Bedrock with the new API
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',  # Latest Claude 3.5 Sonnet
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
        'Access-Control-Max-Age': '86400'
    }
