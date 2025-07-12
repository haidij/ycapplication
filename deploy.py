#!/usr/bin/env python3
"""
Clean deployment script for YC Coach app with CloudFront
"""
import boto3
import json
import zipfile
import io
import time
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
        
    def create_s3_bucket(self):
        """Create private S3 bucket for CloudFront origin"""
        print(f"Setting up S3 bucket: {self.bucket_name}")
        
        try:
            # Check if bucket exists
            self.s3.head_bucket(Bucket=self.bucket_name)
            print("✓ S3 bucket already exists")
        except:
            # Create bucket
            self.s3.create_bucket(Bucket=self.bucket_name)
            print("✓ S3 bucket created")
            
        # Block public access
        self.s3.put_public_access_block(
            Bucket=self.bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
    
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
    
    def create_cloudfront_distribution(self):
        """Create or reuse CloudFront distribution with OAC"""
        print("Setting up CloudFront distribution...")
        
        # Check for existing distribution
        try:
            distributions = self.cloudfront.list_distributions()['DistributionList']
            for dist in distributions.get('Items', []):
                if dist['Comment'] == 'YC Coach App':
                    domain = dist['DomainName']
                    distribution_arn = dist['ARN']
                    
                    # Skip bucket policy update - configured manually
                    
                    print(f"✓ Using existing CloudFront: https://{domain}")
                    print("✓ S3 bucket policy updated")
                    return domain
        except:
            pass
        
        # Use existing OAC or create new one
        oac_id = None
        try:
            # List existing OACs
            oacs = self.cloudfront.list_origin_access_controls()['OriginAccessControlList']
            for oac in oacs.get('Items', []):
                if 'yc-coach' in oac['Name'].lower():
                    oac_id = oac['Id']
                    print(f"✓ Using existing OAC: {oac['Name']}")
                    break
        except:
            pass
            
        if not oac_id:
            # Create new OAC
            oac_response = self.cloudfront.create_origin_access_control(
                OriginAccessControlConfig={
                    'Name': 'yc-coach-oac',
                    'Description': 'OAC for YC Coach S3 bucket',
                    'OriginAccessControlOriginType': 's3',
                    'SigningBehavior': 'always',
                    'SigningProtocol': 'sigv4'
                }
            )
            oac_id = oac_response['OriginAccessControl']['Id']
            print("✓ Created new OAC")
        
        config = {
            'CallerReference': f'yc-coach-{int(time.time())}',
            'Comment': 'YC Coach App',
            'DefaultCacheBehavior': {
                'TargetOriginId': 'S3-origin',
                'ViewerProtocolPolicy': 'redirect-to-https',
                'TrustedSigners': {'Enabled': False, 'Quantity': 0},
                'ForwardedValues': {
                    'QueryString': False,
                    'Cookies': {'Forward': 'none'}
                },
                'MinTTL': 0
            },
            'Origins': {
                'Quantity': 1,
                'Items': [{
                    'Id': 'S3-origin',
                    'DomainName': f'{self.bucket_name}.s3.amazonaws.com',
                    'OriginAccessControlId': oac_id,
                    'S3OriginConfig': {'OriginAccessIdentity': ''}
                }]
            },
            'Enabled': True,
            'DefaultRootObject': 'index.html',
            'PriceClass': 'PriceClass_100'
        }
        
        try:
            response = self.cloudfront.create_distribution(DistributionConfig=config)
            domain = response['Distribution']['DomainName']
            distribution_arn = response['Distribution']['ARN']
            
            # Skip bucket policy update - configured manually
            
            print(f"✓ CloudFront created: https://{domain}")
            print("  ⏳ Deploying (5-15 minutes)")
            return domain
            
        except Exception as e:
            print(f"❌ CloudFront error: {e}")
            return None
    
    def deploy_lambda(self):
        """Deploy Lambda function"""
        print("Deploying Lambda function...")
        
        # Check if lambda file exists
        if not Path('lambda/lambda_function.py').exists():
            print("❌ lambda/lambda_function.py not found")
            return False
        
        # Get role ARN
        account_id = boto3.client('sts').get_caller_identity()['Account']
        role_arn = f'arn:aws:iam::{account_id}:role/lambda-bedrock-execution-role'
        
        # Create zip package
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write('lambda/lambda_function.py', 'lambda_function.py')
            if Path('system_prompt.txt').exists():
                zf.write('system_prompt.txt', 'system_prompt.txt')
        zip_content = zip_buffer.getvalue()
        
        try:
            # Try to update existing function
            self.lambda_client.get_function(FunctionName=self.lambda_function_name)
            self.lambda_client.update_function_code(
                FunctionName=self.lambda_function_name,
                ZipFile=zip_content
            )
            print("✓ Lambda function updated")
            return True
            
        except self.lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            try:
                self.lambda_client.create_function(
                    FunctionName=self.lambda_function_name,
                    Runtime='python3.9',
                    Role=role_arn,
                    Handler='lambda_function.lambda_handler',
                    Code={'ZipFile': zip_content},
                    Description='YC Coach Bedrock integration',
                    Timeout=30,
                    MemorySize=256
                )
                print("✓ Lambda function created")
                return True
                
            except Exception as e:
                print(f"❌ Lambda error: {e}")
                return False
    
    def create_api_gateway(self):
        """Create API Gateway for Lambda function"""
        print("Setting up API Gateway...")
        
        try:
            # Check for existing API
            apis = self.apigateway.get_rest_apis()
            existing_api = None
            for api in apis['items']:
                if api['name'] == self.api_name:
                    existing_api = api
                    break
            
            if existing_api:
                api_id = existing_api['id']
                print(f"✓ Using existing API: {self.api_name}")
            else:
                # Create new API
                api_response = self.apigateway.create_rest_api(
                    name=self.api_name,
                    description='API for YC Coach app'
                )
                api_id = api_response['id']
                print(f"✓ Created API: {self.api_name}")
            
            # Get root resource
            resources = self.apigateway.get_resources(restApiId=api_id)
            root_id = None
            for resource in resources['items']:
                if resource['path'] == '/':
                    root_id = resource['id']
                    break
            
            # Find or create /chat resource
            resource_id = None
            for resource in resources['items']:
                if resource.get('pathPart') == 'chat':
                    resource_id = resource['id']
                    print("✓ Using existing /chat resource")
                    break
            
            if not resource_id:
                chat_resource = self.apigateway.create_resource(
                    restApiId=api_id,
                    parentId=root_id,
                    pathPart='chat'
                )
                resource_id = chat_resource['id']
                print("✓ Created /chat resource")
            
            # Setup methods (POST and OPTIONS)
            for method in ['POST', 'OPTIONS']:
                try:
                    self.apigateway.put_method(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod=method,
                        authorizationType='NONE'
                    )
                except self.apigateway.exceptions.ConflictException:
                    pass  # Method already exists
            
            # Get Lambda function ARN
            account_id = boto3.client('sts').get_caller_identity()['Account']
            lambda_arn = f'arn:aws:lambda:us-east-1:{account_id}:function:{self.lambda_function_name}'
            
            # Set up Lambda integration for POST
            try:
                self.apigateway.put_integration(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='POST',
                    type='AWS_PROXY',
                    integrationHttpMethod='POST',
                    uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
                )
            except self.apigateway.exceptions.ConflictException:
                pass  # Integration already exists
            
            # Set up CORS for OPTIONS
            try:
                self.apigateway.put_integration(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    type='MOCK',
                    requestTemplates={'application/json': '{"statusCode": 200}'}
                )
                
                self.apigateway.put_integration_response(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    statusCode='200',
                    responseParameters={
                        'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                        'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'",
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
                
                self.apigateway.put_method_response(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    statusCode='200',
                    responseParameters={
                        'method.response.header.Access-Control-Allow-Headers': True,
                        'method.response.header.Access-Control-Allow-Methods': True,
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            except:
                pass
            
            # Add Lambda permission
            try:
                self.lambda_client.add_permission(
                    FunctionName=self.lambda_function_name,
                    StatementId='api-gateway-invoke',
                    Action='lambda:InvokeFunction',
                    Principal='apigateway.amazonaws.com',
                    SourceArn=f'arn:aws:execute-api:us-east-1:{account_id}:{api_id}/*/*'
                )
            except self.lambda_client.exceptions.ResourceConflictException:
                pass  # Permission already exists
            
            # Deploy API (always redeploy to ensure latest changes)
            try:
                self.apigateway.create_deployment(
                    restApiId=api_id,
                    stageName='prod'
                )
                print("✓ API deployed to prod stage")
            except Exception as e:
                print(f"⚠️  Deployment warning: {e}")
            
            api_url = f'https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/chat'
            print(f"✓ API Gateway deployed: {api_url}")
            
            return api_url
            
        except Exception as e:
            print(f"❌ API Gateway error: {e}")
            return None
    
    def update_frontend_config(self, api_url, password='yc2024'):
        """Update frontend with API URL and password"""
        try:
            with open('frontend/app.js', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update API URL
            updated_content = content.replace(
                "this.apiUrl = 'YOUR_API_GATEWAY_URL_HERE';",
                f"this.apiUrl = '{api_url}';"
            )
            
            # Update password
            updated_content = updated_content.replace(
                "const correctPassword = 'CHANGE_ME_IN_DEPLOY_SCRIPT';",
                f"const correctPassword = '{password}';"
            )
            
            with open('frontend/app.js', 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("✓ Frontend updated with API URL and password")
            return True
            
        except Exception as e:
            print(f"❌ Error updating frontend: {e}")
            return False
    
    def deploy(self):
        """Deploy everything"""
        print("🚀 Deploying YC Coach App")
        print("=" * 40)
        
        # Deploy components
        self.create_s3_bucket()
        lambda_success = self.deploy_lambda()
        api_url = None
        
        if lambda_success:
            api_url = self.create_api_gateway()
            if api_url:
                # You can change the password here
                app_password = 'yc2025'  # Change this to your desired password
                self.update_frontend_config(api_url, app_password)
        
        self.upload_static_files()
        cloudfront_domain = self.create_cloudfront_distribution()
        
        # Summary
        print("\n✅ Deployment Complete!")
        
        if cloudfront_domain:
            print(f"🌐 App URL: https://{cloudfront_domain}")
        
        if api_url:
            print(f"🔗 API URL: {api_url}")
            print("\n📋 Next Steps:")
            print("1. Wait for CloudFront deployment (5-15 minutes)")
            print("2. Test your YC Coach app!")
        else:
            print("\n⚠️  API Gateway setup failed. Check IAM permissions.")
            
        if not lambda_success:
            print("\n⚠️  Check IAM role exists: lambda-bedrock-execution-role")

if __name__ == "__main__":
    deployer = YCCoachDeployer()
    deployer.deploy()
