# YC Application Coach

A simple web app that uses the **latest Amazon Bedrock API** to coach entrepreneurs through writing their Y Combinator application, specifically the question: "What is your company going to make?"

## Architecture

- **Frontend**: Static HTML/CSS/JS hosted on S3 + CloudFront
- **Backend**: AWS Lambda function using **Amazon Bedrock API** (Claude 3.5 Sonnet v2)
- **Deployment**: Python scripts for automated setup

## New Bedrock API Features

This app uses the latest Bedrock API with:
- **Claude 3.5 Sonnet v2** (most advanced model)
- Enhanced message formatting
- Better error handling and throttling
- Token usage tracking
- Improved system prompts

## Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Python 3.7+ installed
- Access to Amazon Bedrock (Claude 3.5 Sonnet v2 recommended)

### Setup & Deployment

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test Bedrock API access**:
   ```bash
   python test_bedrock.py
   ```

3. **Run setup** (creates IAM roles and checks Bedrock access):
   ```bash
   python setup.py
   ```

4. **Deploy the application**:
   ```bash
   python deploy.py
   ```

5. **Update API URL**: After deployment, update the `apiUrl` in `frontend/app.js` with your API Gateway URL.

## Project Structure

```
YC/
├── frontend/
│   ├── index.html      # Main web interface
│   ├── style.css       # Styling
│   └── app.js          # Frontend logic with enhanced mock responses
├── lambda/
│   └── lambda_function.py  # Latest Bedrock API integration
├── setup.py            # AWS setup automation
├── deploy.py           # Deployment automation
├── test_bedrock.py     # Bedrock API testing
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Enhanced Features

### Latest Bedrock API Integration
- **Claude 3.5 Sonnet v2**: Most advanced coaching capabilities
- **Structured Prompts**: Optimized system prompts for YC coaching
- **Token Tracking**: Monitor usage and costs
- **Better Error Handling**: Specific error messages for different failure modes

### Intelligent Coaching
- **Iterative Improvement**: Multi-round coaching conversations
- **Specific Questions**: Targeted follow-ups based on YC success patterns
- **Problem-Solution Fit**: Guides users to articulate clear problem statements
- **Market Focus**: Helps identify specific target customers

## Model Fallback Strategy

The app automatically tries models in this order:
1. `claude-3-5-sonnet-20241022-v2:0` (latest, best performance)
2. `claude-3-5-sonnet-20240620-v1:0` (fallback)
3. `claude-3-sonnet-20240229-v1:0` (older fallback)

## Testing

### Local Testing with Enhanced Mocks
The frontend includes intelligent mock responses that simulate the new API:
- Open `frontend/index.html` in a browser
- Mock responses adapt based on conversation progress
- Simulates token usage and model information

### API Testing
```bash
python test_bedrock.py
```
This will:
- List available Claude models
- Test API connectivity
- Verify response format
- Show token usage

## Customization

### Adding Your 30 Examples
To incorporate your successful YC application examples:

1. Create a `examples/` directory
2. Add your examples as text files
3. Update the system prompt in `lambda/lambda_function.py`:

```python
# Add to system_prompt
SUCCESSFUL_EXAMPLES = """
Based on these successful YC applications:
[Your examples here]
"""
```

### Advanced Coaching Features
The new API enables:
- **Multi-turn conversations** with context retention
- **Structured feedback** with specific improvement areas
- **Progress tracking** through conversation stages
- **Personalized coaching** based on industry/market

## Costs (Updated for New API)

Estimated monthly costs for moderate usage:
- **S3 + CloudFront**: ~$1-5
- **Lambda**: ~$0-10 (depending on usage)
- **Bedrock (Claude 3.5 Sonnet v2)**: ~$15-75 (depending on conversation length/frequency)
- **API Gateway**: ~$1-5

*Note: Claude 3.5 Sonnet v2 is more expensive but provides significantly better coaching quality*

## Security & Performance

### New API Benefits
- **Better rate limiting** handling
- **Enhanced CORS** configuration
- **Improved error messages** for debugging
- **Token usage monitoring** for cost control

### Security Features
- Server-side API calls only
- No API keys exposed to frontend
- CORS configured for browser access
- CloudWatch logging for monitoring

## Troubleshooting

### New API Specific Issues

1. **Model Access Denied**:
   ```bash
   python test_bedrock.py  # Check available models
   ```
   - Request access to Claude 3.5 Sonnet v2 in Bedrock console

2. **API Format Errors**:
   - Check CloudWatch logs for detailed error messages
   - Verify message format matches new API requirements

3. **Token Limits**:
   - Monitor token usage in response metadata
   - Adjust max_tokens in Lambda function if needed

### Getting Help

Check AWS CloudWatch logs:
```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/yc-coach"
aws logs tail /aws/lambda/yc-coach-bedrock --follow
```

## Next Steps

- **Enhanced Analytics**: Track coaching effectiveness
- **Multi-Question Support**: Expand to other YC application questions  
- **User Accounts**: Save and resume coaching sessions
- **Export Features**: Generate final application text
- **A/B Testing**: Compare coaching approaches
