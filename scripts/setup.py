#!/usr/bin/env python3
"""
Simple setup script for YC Coach app
This handles the AWS setup step by step
"""
import boto3
import json
import time
from botocore.exceptions import ClientError

class YCCoachSetup:
    def __init__(self):
        self.iam = boto3.client('iam')
        self.sts = boto3.client('sts')
        
    def get_account_id(self):
        """Get current AWS account ID"""
        try:
            return self.sts.get_caller_identity()['Account']
        except Exception as e:
            print(f"Error getting account ID: {e}")
            return None
    
    def create_lambda_role(self):
        """Create IAM role for Lambda function"""
        account_id = self.get_account_id()
        if not account_id:
            return None
            
        role_name = 'lambda-bedrock-execution-role'
        
        # Trust policy for Lambda
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            # Create the role
            print(f"Creating IAM role: {role_name}")
            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Execution role for YC Coach Lambda function'
            )
            
            # Attach basic Lambda execution policy
            self.iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            # Create and attach Bedrock policy
            bedrock_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "bedrock:InvokeModel"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            
            policy_name = 'BedrockInvokePolicy'
            self.iam.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(bedrock_policy),
                Description='Policy to allow Lambda to invoke Bedrock models'
            )
            
            self.iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=f'arn:aws:iam::{account_id}:policy/{policy_name}'
            )
            
            role_arn = f'arn:aws:iam::{account_id}:role/{role_name}'
            print(f"✓ IAM role created: {role_arn}")
            
            # Wait for role to be available
            print("Waiting for role to be available...")
            time.sleep(10)
            
            return role_arn
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                print(f"✓ IAM role {role_name} already exists")
                return f'arn:aws:iam::{account_id}:role/{role_name}'
            else:
                print(f"Error creating IAM role: {e}")
                return None
    
    def check_bedrock_access(self):
        """Check if latest Bedrock models are accessible"""
        try:
            bedrock = boto3.client('bedrock', region_name='us-east-1')
            models = bedrock.list_foundation_models()
            
            # Check for Claude 3.5 Sonnet v2 (latest)
            claude_35_v2 = [m for m in models['modelSummaries'] 
                           if 'claude-3-5-sonnet-20241022-v2' in m['modelId']]
            
            # Check for Claude 3.5 Sonnet (fallback)
            claude_35 = [m for m in models['modelSummaries'] 
                        if 'claude-3-5-sonnet' in m['modelId']]
            
            # Check for Claude 3 Sonnet (older fallback)
            claude_3 = [m for m in models['modelSummaries'] 
                       if 'claude-3-sonnet' in m['modelId']]
            
            if claude_35_v2:
                print("✓ Bedrock Claude 3.5 Sonnet v2 (latest) is available")
                return True
            elif claude_35:
                print("✓ Bedrock Claude 3.5 Sonnet is available")
                print("ℹ️  Consider requesting access to Claude 3.5 Sonnet v2 for best performance")
                return True
            elif claude_3:
                print("✓ Bedrock Claude 3 Sonnet is available")
                print("ℹ️  Consider upgrading to Claude 3.5 Sonnet for better performance")
                return True
            else:
                print("⚠️  No Claude models found. You need to request access in the Bedrock console.")
                print("   Recommended: Claude 3.5 Sonnet v2")
                return False
                
        except Exception as e:
            print(f"⚠️  Error checking Bedrock access: {e}")
            print("You may need to enable Bedrock in your AWS account.")
            return False
    
    def update_deploy_script(self, role_arn):
        """Update the deploy_fixed.py script with the correct role ARN"""
        try:
            deploy_file = 'deploy.py'
            
            with open(deploy_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace the placeholder role ARN
            updated_content = content.replace(
                'arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-bedrock-execution-role',
                role_arn
            )
            
            # Also replace any account ID placeholders
            account_id = self.get_account_id()
            if account_id:
                updated_content = updated_content.replace(
                    'YOUR_ACCOUNT_ID',
                    account_id
                )
            
            with open(deploy_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✓ Updated {deploy_file} with correct role ARN")
            
        except Exception as e:
            print(f"Error updating deploy script: {e}")
            print("You can manually update the role ARN in deploy_fixed.py")
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 Setting up YC Coach app...")
        print("=" * 50)
        
        # Check Bedrock access
        print("1. Checking Bedrock access...")
        self.check_bedrock_access()
        
        # Create IAM role
        print("\n2. Creating IAM role...")
        role_arn = self.create_lambda_role()
        
        if role_arn:
            self.update_deploy_script(role_arn)
            
            print("\n✅ Setup complete!")
            print("\nNext steps:")
            print("1. Run: python deploy_fixed.py")
            print("2. Update frontend/app.js with your API Gateway URL")
            print("3. Test your application")
            
        else:
            print("\n❌ Setup failed. Please check your AWS credentials and permissions.")

if __name__ == "__main__":
    setup = YCCoachSetup()
    setup.run_setup()
