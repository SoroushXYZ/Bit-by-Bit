#!/usr/bin/env python3
"""
Bit-by-Bit Pipeline Setup & Test Script
Handles AWS setup, bucket creation, and connection testing.
"""

import boto3
import os
import sys
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime

# Add pipeline to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.env_loader import EnvLoader


class PipelineSetup:
    """Handles pipeline setup and AWS configuration."""
    
    def __init__(self):
        self.env_loader = EnvLoader()
        self.environment = self.env_loader.get_env_var('ENVIRONMENT', 'development')
        self.upload_to_aws = self.env_loader.get_env_var('UPLOAD_TO_AWS', 'true').lower() == 'true'
        
        # Validate environment
        if self.environment not in ['development', 'production']:
            print(f"❌ Invalid environment: {self.environment}")
            print("💡 Use 'development' or 'production'")
            sys.exit(1)
        
        print(f"🔧 Pipeline Setup - Environment: {self.environment}")
        print(f"📤 Upload to AWS: {self.upload_to_aws}")
        print("-" * 50)
    
    def test_aws_connection(self):
        """Test AWS S3 connection and permissions."""
        if not self.upload_to_aws:
            print("⏭️  Skipping AWS tests (UPLOAD_TO_AWS=false)")
            return True
        
        print("🔧 Testing AWS S3 Connection...")
        
        try:
            # Create S3 client
            s3_client = self._create_s3_client()
            if not s3_client:
                return False
            
            # Test basic connection
            print("📋 Testing: List S3 buckets...")
            response = s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            print(f"✅ Found {len(buckets)} buckets")
            
            return True
            
        except Exception as e:
            print(f"❌ AWS connection failed: {e}")
            return False
    
    def _create_s3_client(self):
        """Create S3 client with proper credentials."""
        try:
            # Get AWS credentials
            aws_access_key = self.env_loader.get_env_var('AWS_ACCESS_KEY_ID')
            aws_secret_key = self.env_loader.get_env_var('AWS_SECRET_ACCESS_KEY')
            aws_region = self.env_loader.get_env_var('AWS_DEFAULT_REGION', 'us-east-1')
            aws_profile = self.env_loader.get_env_var('AWS_PROFILE')
            
            print(f"🌍 AWS Region: {aws_region}")
            
            # Clean up profile name (remove comments and whitespace)
            if aws_profile:
                aws_profile = aws_profile.split('#')[0].strip()  # Remove comments
                if aws_profile and aws_profile != "Leave empty if using access keys" and aws_profile != "":
                    print(f"👤 Using AWS Profile: {aws_profile}")
                    session = boto3.Session(profile_name=aws_profile)
                    return session.client('s3', region_name=aws_region)
            
            if aws_access_key and aws_secret_key:
                print("🔑 Using AWS Access Keys")
                # Clear any existing AWS profile environment variables to avoid conflicts
                import os
                old_profile = os.environ.pop('AWS_PROFILE', None)
                old_default_profile = os.environ.pop('AWS_DEFAULT_PROFILE', None)
                
                try:
                    client = boto3.client(
                        's3',
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_key,
                        region_name=aws_region
                    )
                    return client
                finally:
                    # Restore environment variables
                    if old_profile:
                        os.environ['AWS_PROFILE'] = old_profile
                    if old_default_profile:
                        os.environ['AWS_DEFAULT_PROFILE'] = old_default_profile
            else:
                print("🔑 Using default AWS credentials")
                return boto3.client('s3', region_name=aws_region)
                
        except NoCredentialsError:
            print("❌ No AWS credentials found")
            print("💡 Please set AWS credentials in your .env file")
            return None
        except Exception as e:
            print(f"❌ Failed to create S3 client: {e}")
            return None
    
    def get_bucket_name(self):
        """Get the appropriate bucket name for current environment."""
        if self.environment == 'development':
            bucket = self.env_loader.get_env_var('AWS_S3_BUCKET_DEV')
        elif self.environment == 'production':
            bucket = self.env_loader.get_env_var('AWS_S3_BUCKET_PROD')
        
        if not bucket:
            print(f"❌ No bucket configured for environment: {self.environment}")
            print(f"💡 Set AWS_S3_BUCKET_{self.environment.upper()}=your-bucket-name in .env")
            return None
        
        return bucket
    
    def check_bucket_exists(self, bucket_name):
        """Check if S3 bucket exists."""
        if not self.upload_to_aws:
            return True
        
        try:
            s3_client = self._create_s3_client()
            if not s3_client:
                return False
            
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' exists")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ Bucket '{bucket_name}' not found")
                return False
            else:
                print(f"❌ Error checking bucket: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error checking bucket: {e}")
            return False
    
    def create_bucket(self, bucket_name):
        """Create S3 bucket if it doesn't exist."""
        if not self.upload_to_aws:
            print("⏭️  Skipping bucket creation (UPLOAD_TO_AWS=false)")
            return True
        
        try:
            s3_client = self._create_s3_client()
            if not s3_client:
                return False
            
            aws_region = self.env_loader.get_env_var('AWS_DEFAULT_REGION', 'us-east-1')
            
            print(f"🪣 Creating bucket '{bucket_name}' in region '{aws_region}'...")
            
            if aws_region == 'us-east-1':
                # us-east-1 doesn't need LocationConstraint
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': aws_region}
                )
            
            print(f"✅ Bucket '{bucket_name}' created successfully")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyExists':
                print(f"✅ Bucket '{bucket_name}' already exists")
                return True
            elif e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                print(f"✅ Bucket '{bucket_name}' already owned by you")
                return True
            else:
                print(f"❌ Failed to create bucket: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error creating bucket: {e}")
            return False
    
    def test_bucket_permissions(self, bucket_name):
        """Test read/write permissions on bucket."""
        if not self.upload_to_aws:
            print("⏭️  Skipping permission test (UPLOAD_TO_AWS=false)")
            return True
        
        try:
            s3_client = self._create_s3_client()
            if not s3_client:
                return False
            
            print(f"✍️ Testing write permissions on '{bucket_name}'...")
            
            # Test write
            test_key = f'test-connection-{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=b'Test connection from Bit-by-Bit pipeline'
            )
            print("✅ Write test successful")
            
            # Test read
            print("📖 Testing read permissions...")
            response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
            content = response['Body'].read()
            if content == b'Test connection from Bit-by-Bit pipeline':
                print("✅ Read test successful")
            else:
                print("❌ Read test failed - content mismatch")
                return False
            
            # Clean up test file
            s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            print("🧹 Cleaned up test file")
            
            return True
            
        except ClientError as e:
            print(f"❌ Permission test failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error testing permissions: {e}")
            return False
    
    def setup_all_buckets(self):
        """Setup both development and production buckets."""
        if not self.upload_to_aws:
            print("⏭️  Skipping bucket setup (UPLOAD_TO_AWS=false)")
            return True
        
        print("🪣 Setting up both development and production buckets...")
        
        # Get both bucket names
        dev_bucket = self.env_loader.get_env_var('AWS_S3_BUCKET_DEV')
        prod_bucket = self.env_loader.get_env_var('AWS_S3_BUCKET_PROD')
        
        buckets_to_setup = []
        if dev_bucket:
            buckets_to_setup.append(('development', dev_bucket))
        if prod_bucket:
            buckets_to_setup.append(('production', prod_bucket))
        
        if not buckets_to_setup:
            print("❌ No buckets configured in .env file")
            return False
        
        success = True
        for env_name, bucket_name in buckets_to_setup:
            print(f"\n🔧 Setting up {env_name} bucket: {bucket_name}")
            
            # Check if bucket exists
            if not self.check_bucket_exists(bucket_name):
                print(f"  🆕 Creating bucket '{bucket_name}'...")
                if not self.create_bucket(bucket_name):
                    print(f"  ❌ Failed to create {env_name} bucket")
                    success = False
                    continue
            else:
                print(f"  ✅ {env_name} bucket already exists")
            
            # Test permissions
            print(f"  ✍️ Testing permissions on {env_name} bucket...")
            if not self.test_bucket_permissions(bucket_name):
                print(f"  ❌ Permission test failed for {env_name} bucket")
                success = False
            else:
                print(f"  ✅ {env_name} bucket permissions verified")
        
        return success

    def run_setup(self):
        """Run complete setup process."""
        print("🚀 Starting Bit-by-Bit Pipeline Setup")
        print("=" * 50)
        
        # Step 1: Test AWS connection
        if not self.test_aws_connection():
            print("\n❌ AWS connection test failed")
            if self.upload_to_aws:
                print("💡 Set UPLOAD_TO_AWS=false to skip AWS setup")
                return False
            else:
                print("✅ Continuing without AWS (local mode)")
        
        # Step 2: Setup all buckets
        if not self.setup_all_buckets():
            print("❌ Bucket setup failed")
            return False
        
        # Step 3: Show current environment info
        current_bucket = self.get_bucket_name()
        
        print("\n🎉 Pipeline setup completed successfully!")
        print(f"📋 Current Environment: {self.environment}")
        print(f"📤 Upload to AWS: {self.upload_to_aws}")
        if self.upload_to_aws:
            print(f"🪣 Current S3 Bucket: {current_bucket}")
            print("✅ Both development and production buckets are ready")
        else:
            print("💾 Running in local mode (no AWS upload)")
        
        return True


def main():
    """Main setup function."""
    setup = PipelineSetup()
    success = setup.run_setup()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("🚀 You can now run the pipeline with: python run_pipeline.py")
        sys.exit(0)
    else:
        print("\n❌ Setup failed!")
        print("💡 Check your .env file and AWS credentials")
        sys.exit(1)


if __name__ == "__main__":
    main()
