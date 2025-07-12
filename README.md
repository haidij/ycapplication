# 🚀 YC Coach - AI-Powered Y Combinator Application Assistant

> An intelligent coaching tool that helps entrepreneurs craft compelling Y Combinator application responses using AI-powered feedback and proven examples.

[![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20Bedrock%20%7C%20S3-orange)](https://aws.amazon.com/)
[![AI](https://img.shields.io/badge/AI-Claude%203.5%20Sonnet-blue)](https://www.anthropic.com/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-green)]()

## ✨ Features

### 🎯 **Intelligent Coaching**
- **Focused Guidance**: Specialized coaching for the core YC question: *"What is your company going to make?"*
- **Contextual Feedback**: Get personalized advice tailored to your specific business idea
- **Iterative Improvement**: Refine your product description through conversational coaching
- **YC Best Practices**: Built on proven application strategies and successful examples

### 🤖 **AI-Powered Analysis**
- **Claude 3.5 Sonnet**: Advanced AI model for nuanced business understanding
- **Real-time Responses**: Instant feedback on your application answers
- **Expert Guidance**: Coaching based on 30+ successful YC applications from [Shizune's YC Examples](https://shizune.co/yc-application-examples)

### 🌐 **Modern Architecture**
- **Serverless**: Scalable AWS infrastructure
- **Global CDN**: Fast loading worldwide via CloudFront
- **Responsive Design**: Works on desktop and mobile

## 🏗️ Architecture

```
User Browser → CloudFront CDN → S3 Static Hosting → JavaScript App
                                        ↓
API Gateway → AWS Lambda → Amazon Bedrock → Claude 3.5 Sonnet
```

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Vanilla JavaScript | Interactive chat interface |
| **API** | AWS API Gateway | RESTful API endpoints |
| **Compute** | AWS Lambda | Serverless request processing |
| **AI** | Amazon Bedrock | Claude 3.5 Sonnet integration |
| **Hosting** | S3 + CloudFront | Global static site delivery |

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Access to Amazon Bedrock (Claude models)
- Python 3.9+

### Deployment

1. **Clone and navigate to the project**:
   ```bash
   git clone <your-repo-url>
   cd yc-coach
   ```

2. **Set up access password**:
   ```bash
   echo "your-desired-password" > app_password.txt
   ```
   *Note: This file is excluded from git for security*

3. **Deploy to AWS**:
   ```bash
   python3 deploy_with_login.py
   ```

4. **Access your application**:
   - Go to your CloudFront URL (provided after deployment)
   - Enter the password you set in `app_password.txt`
   - Start coaching with personalized YC application guidance

### 🔐 **Login System**
- **Password Protection**: App requires authentication before access
- **Session Persistence**: Stay logged in during browser session
- **Secure Storage**: Password stored locally, never committed to git
- **Easy Management**: Update password by editing `app_password.txt` and redeploying

## ⚠️ Important Usage Notes

### AWS Bedrock Rate Limiting
**Amazon Bedrock has built-in rate limiting to prevent abuse.** You may experience throttling if you send messages too quickly.

**Recommended Usage:**
- ⏱️ **Wait 30+ seconds between messages** for optimal experience
- 🚫 **Avoid rapid-fire testing** - this will trigger throttling errors
- ✅ **Normal conversation pace** works perfectly for real usage
- 🔄 **If throttled**: Wait 1-2 minutes before trying again

### Current Limitations
**⚠️ Single Question Focus**: The current version is optimized for the core YC question: *"What is your company going to make? Please describe your product and what it does or will do."* 

While the AI can handle follow-up questions and refinements about your product description, it's specifically designed around this primary application question.

**Why This Happens:**
- AWS Bedrock protects against abuse with usage limits
- Free tier accounts have lower limits than paid accounts
- This is normal AWS behavior, not a bug in the application

**For Real Users:**
- Typical conversation patterns won't hit these limits
- The 30-second guideline ensures smooth operation
- Production usage rarely encounters throttling

## 📁 Project Structure

```
yc-coach/
├── 📁 frontend/              # Web application
│   ├── 📄 index.html         # Main HTML interface with login
│   ├── 📄 app.js             # JavaScript application logic
│   └── 📄 style.css          # UI styling and responsive design
├── 📁 lambda/                # AWS Lambda function
│   └── 📄 lambda_function.py # Bedrock integration and API logic
├── 📁 scripts/               # Utility and setup scripts
├── 📄 deploy_with_login.py   # Main deployment automation
├── 📄 system_prompt.txt      # AI coaching instructions (30+ examples)
├── 📄 app_password.txt       # Access password (not in git)
├── 📄 README.md              # This documentation
└── 📄 .gitignore             # Version control exclusions
```

## ⚙️ Configuration

### AWS Services Required
- **Amazon Bedrock**: Claude 3.5 Sonnet model access
- **AWS Lambda**: Serverless compute
- **API Gateway**: REST API management
- **S3**: Static website hosting
- **CloudFront**: Global content delivery
- **IAM**: Appropriate service permissions

### Environment Setup
The application automatically configures:
- API Gateway endpoints
- Lambda function permissions
- S3 bucket policies
- CloudFront distributions
- CORS settings

## 🛠️ Development

### Local Development
1. **Edit frontend files** in `frontend/` directory
2. **Modify Lambda function** in `lambda/lambda_function.py`
3. **Update AI coaching prompt** in `system_prompt.txt`
4. **Change access password** in `app_password.txt`

### Deployment
```bash
# Deploy all changes including login system
python3 deploy_with_login.py

# Wait for CloudFront cache invalidation (5-10 minutes)
# Test your changes at the CloudFront URL
```

### Password Management
```bash
# Update password
echo "new-password-2025" > app_password.txt

# Redeploy to apply changes
python3 deploy_with_login.py
```

### Debugging
- Check AWS CloudWatch logs for Lambda function errors
- Use browser Developer Tools to inspect API calls
- Monitor API Gateway metrics for performance
- Test login functionality in incognito mode

## 💡 Usage Tips

### Getting the Best Coaching
- **Be specific**: Describe your product and target market clearly
- **Focus on the core question**: *"What is your company going to make? Please describe your product and what it does or will do."*
- **Iterate**: Use the AI's questions to refine your product description
- **Address feedback**: Respond to specific questions about your business model, target market, and value proposition
- **Patience**: Allow 30+ seconds between messages to avoid throttling

### Optimal Approach
1. **Start with your initial product description**
2. **Answer the AI's follow-up questions** about specifics
3. **Refine based on feedback** about clarity and market focus
4. **Build a compelling narrative** around what you're making

### Common Issues
- **"Too many requests" error**: Wait 1-2 minutes, then try again
- **Same response repeatedly**: Clear browser cache and hard refresh
- **Slow responses**: Normal for AI processing, typically 2-5 seconds

## 🔒 Security

### Access Control
- 🔐 **Password Protection**: Application requires authentication before access
- 🔑 **Local Password Storage**: Password stored in `app_password.txt` (excluded from git)
- 🚪 **Session Management**: Login persists during browser session
- 🔄 **Easy Password Updates**: Change password by editing file and redeploying

### Infrastructure Security
- ✅ **No hardcoded credentials** in repository
- ✅ **AWS IAM roles** for service authentication
- ✅ **Environment variables** for sensitive configuration
- ✅ **CORS protection** on API endpoints
- ✅ **HTTPS encryption** via CloudFront

### Best Practices
- 🔒 **Password file excluded** from version control
- 🛡️ **Session-based authentication** (no persistent tokens)
- 🔐 **Secure deployment process** with proper credential handling

## 📊 Performance

- **Response Time**: 2-5 seconds typical (AI processing)
- **Availability**: 99.9% (AWS SLA)
- **Scalability**: Serverless auto-scaling
- **Global**: CloudFront edge locations worldwide
- **Rate Limits**: AWS Bedrock throttling applies

## 🎯 About the Coaching Content

This application uses a carefully crafted coaching prompt based on **30+ successful Y Combinator applications** sourced from [Shizune's YC Application Examples](https://shizune.co/yc-application-examples). 

**The coaching methodology includes:**
- ✅ Proven patterns from successful applications
- ✅ Common mistakes to avoid
- ✅ Specific guidance for different business types
- ✅ Iterative improvement strategies

**Note**: The core prompt and examples are stable and don't require updates, as they're based on established successful patterns.

## 🤝 Contributing

Improvements to the user interface, deployment process, and documentation are welcome. The core AI coaching prompt is based on proven examples and remains stable.

## 📄 License

This project is for educational and personal use in preparing Y Combinator applications.

---

<div align="center">

**Built with ❤️ for aspiring entrepreneurs**

*Remember: Wait 30+ seconds between messages to avoid AWS Bedrock throttling*

</div>
