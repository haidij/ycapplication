#!/usr/bin/env python3
"""
Simple deployment script for YC Coach app
"""
import boto3
import json
import zipfile
import os
from pathlib import Path

class YCCoachDeployer:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.lambda_client = boto3.client('lambda')
        self.apigateway = boto3.client('apigateway')
        self.cloudfront = boto3.client('cloudfront')
        
        # Configuration
        self.bucket_name = 'yc-coach-app-static'
        self.lambda_function_name = 'yc-coach-bedrock'
        self.api_name = 'yc-coach-api'
        
    def create_s3_bucket(self):
        """Create S3 bucket for static website hosting"""
        try:
            print(f"Creating S3 bucket: {self.bucket_name}")
            self.s3.create_bucket(Bucket=self.bucket_name)
            
            # Enable static website hosting
            website_config = {
                'IndexDocument': {'Suffix': 'index.html'},
                'ErrorDocument': {'Key': 'error.html'}
            }
            self.s3.put_bucket_website(
                Bucket=self.bucket_name,
                WebsiteConfiguration=website_config
            )
            
            # Make bucket public for static hosting
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                    }
                ]
            }
            self.s3.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            print(f"✓ S3 bucket created and configured")
            
        except Exception as e:
            print(f"Error creating S3 bucket: {e}")
    
    def deploy_lambda(self):
        """Deploy Lambda function for Bedrock integration"""
        try:
            print("Creating Lambda function...")
            
            # Create deployment package
            with zipfile.ZipFile('lambda_function.zip', 'w') as zip_file:
                zip_file.write('lambda/lambda_function.py', 'lambda_function.py')
            
            with open('lambda_function.zip', 'rb') as zip_file:
                zip_content = zip_file.read()
            
            # Create Lambda function
            response = self.lambda_client.create_function(
                FunctionName=self.lambda_function_name,
                Runtime='python3.9',
                Role='arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-bedrock-execution-role',  # You'll need to create this
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='YC Coach Bedrock integration',
                Timeout=30,
                MemorySize=256
            )
            
            print(f"✓ Lambda function created: {response['FunctionArn']}")
            
            # Clean up
            os.remove('lambda_function.zip')
            
        except Exception as e:
            print(f"Error deploying Lambda: {e}")
    
    def upload_static_files(self):
        """Upload static files to S3"""
        try:
            print("Uploading static files...")
            
            # Upload HTML file
            self.s3.upload_file(
                'frontend/index.html',
                self.bucket_name,
                'index.html',
                ExtraArgs={'ContentType': 'text/html'}
            )
            
            # Upload CSS file
            self.s3.upload_file(
                'frontend/style.css',
                self.bucket_name,
                'style.css',
                ExtraArgs={'ContentType': 'text/css'}
            )
            
            # Upload JS file
            self.s3.upload_file(
                'frontend/app.js',
                self.bucket_name,
                'app.js',
                ExtraArgs={'ContentType': 'application/javascript'}
            )
            
            print("✓ Static files uploaded")
            
        except Exception as e:
            print(f"Error uploading static files: {e}")
    
    def deploy_all(self):
        """Deploy the entire application"""
        print("🚀 Starting YC Coach deployment...")
        
        self.create_s3_bucket()
        self.deploy_lambda()
        self.upload_static_files()
        
        website_url = f"http://{self.bucket_name}.s3-website-us-east-1.amazonaws.com"
        print(f"\n✅ Deployment complete!")
        print(f"Website URL: {website_url}")
        print(f"\nNext steps:")
        print(f"1. Create IAM role: lambda-bedrock-execution-role")
        print(f"2. Set up API Gateway to connect to Lambda")
        print(f"3. Update frontend with API Gateway URL")

if __name__ == "__main__":
    deployer = YCCoachDeployer()
    deployer.deploy_all()
