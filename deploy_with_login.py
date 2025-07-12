#!/usr/bin/env python3
"""
Deployment script for YC Coach app with login system
"""
import boto3
import json
import zipfile
import io
import time
import os
from pathlib import Path

class YCCoachDeployer:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.lambda_client = boto3.client('lambda')
        self.cloudfront = boto3.client('cloudfront')
        self.apigateway = boto3.client('apigateway')
        
        # Configuration
        self.bucket_name = 'yc-coach-app-static'
        self.lambda_function_name = 'yc-coach-bedrock'
        self.api_name = 'yc-coach-api'
        
    def update_frontend_config(self, api_url):
        """Update frontend with API URL and password from file"""
        print("Updating frontend configuration...")
        
        # Read password from file
        try:
            with open('app_password.txt', 'r') as f:
                password = f.read().strip()
            print("✓ Password loaded from app_password.txt")
        except FileNotFoundError:
            print("❌ app_password.txt not found! Please create this file with your desired password.")
            return False
        
        try:
            # Read app.js
            with open('frontend/app.js', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update API URL (only if it's the placeholder)
            if 'YOUR_API_GATEWAY_URL_HERE' in content:
                content = content.replace(
                    "this.apiUrl = 'YOUR_API_GATEWAY_URL_HERE';",
                    f"this.apiUrl = '{api_url}';"
                )
                print("✓ Updated API URL")
            
            # Update password (replace placeholder)
            if 'PLACEHOLDER_PASSWORD' in content:
                content = content.replace(
                    "this.correctPassword = 'PLACEHOLDER_PASSWORD';",
                    f"this.correctPassword = '{password}';"
                )
                print("✓ Updated password")
            else:
                print("⚠️  Password placeholder not found - may already be configured")
            
            # Write back to file
            with open('frontend/app.js', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✓ Frontend configuration updated")
            return True
            
        except Exception as e:
            print(f"❌ Error updating frontend: {e}")
            return False
    
    def upload_static_files(self):
        """Upload frontend files to S3"""
        print("Uploading static files...")
        
        files = [
            ('frontend/index.html', 'index.html', 'text/html'),
            ('frontend/style.css', 'style.css', 'text/css'),
            ('frontend/app.js', 'app.js', 'application/javascript')
        ]
        
        for local_file, s3_key, content_type in files:
            if Path(local_file).exists():
                self.s3.upload_file(
                    local_file, self.bucket_name, s3_key,
                    ExtraArgs={
                        'ContentType': content_type,
                        'CacheControl': 'no-cache, no-store, must-revalidate',
                        'Expires': 'Thu, 01 Jan 1970 00:00:00 GMT'
                    }
                )
                print(f"✓ {s3_key}")
            else:
                print(f"⚠️  {local_file} not found")
    
    def invalidate_cloudfront(self):
        """Invalidate CloudFront cache to ensure new files are served"""
        print("Invalidating CloudFront cache...")
        
        try:
            # Find the distribution
            distributions = self.cloudfront.list_distributions()['DistributionList']
            distribution_id = None
            
            for dist in distributions.get('Items', []):
                if 'yc-coach' in dist.get('Comment', '').lower() or 'd1uux7vlfswvgs' in dist['DomainName']:
                    distribution_id = dist['Id']
                    break
            
            if distribution_id:
                print(f"Found CloudFront distribution: {distribution_id}")
                
                invalidation = self.cloudfront.create_invalidation(
                    DistributionId=distribution_id,
                    InvalidationBatch={
                        'Paths': {
                            'Quantity': 1,
                            'Items': ['/*']  # Invalidate all files
                        },
                        'CallerReference': f'login-deployment-{int(time.time())}'
                    }
                )
                
                print(f"✅ Invalidation created: {invalidation['Invalidation']['Id']}")
                print("⏳ Wait 5-10 minutes for invalidation to complete")
                return True
                
            else:
                print("❌ Could not find CloudFront distribution")
                return False
                
        except Exception as e:
            print(f"❌ Error creating invalidation: {e}")
            return False
    
    def deploy_frontend_only(self):
        """Deploy only the frontend with login system"""
        print("🚀 Deploying YC Coach Frontend with Login...")
        print("=" * 50)
        
        # Get API URL (should already exist)
        api_url = "https://j59j74jwbg.execute-api.us-east-1.amazonaws.com/prod/chat"
        
        # Update frontend config
        if not self.update_frontend_config(api_url):
            print("❌ Frontend configuration failed")
            return
        
        # Upload static files
        self.upload_static_files()
        
        # Invalidate CloudFront cache
        self.invalidate_cloudfront()
        
        print("\n" + "=" * 50)
        print("🎉 Frontend Deployment Complete!")
        print(f"🌐 Website: [Your CloudFront URL will be displayed here]")
        print("🔐 Login required with password from app_password.txt")
        print("⏳ Wait 5-10 minutes for CloudFront to update")
        print("=" * 50)

if __name__ == "__main__":
    deployer = YCCoachDeployer()
    deployer.deploy_frontend_only()
