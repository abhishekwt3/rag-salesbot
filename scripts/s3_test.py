# s3_diagnosis.py - Diagnose S3 connection issues
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check AWS environment variables"""
    print("🔍 Checking AWS Environment Variables:")
    
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_REGION',
        'S3_EMBEDDINGS_BUCKET'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var:
                display_value = value[:8] + "..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing variables: {missing_vars}")
        return False
    
    return True

def test_aws_credentials():
    """Test AWS credentials"""
    print("\n🔑 Testing AWS Credentials:")
    
    try:
        # Test credentials with STS
        sts_client = boto3.client(
            'sts',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'ap-south-1')
        )
        
        identity = sts_client.get_caller_identity()
        print(f"  ✅ AWS Account: {identity.get('Account')}")
        print(f"  ✅ User ARN: {identity.get('Arn')}")
        return True
        
    except NoCredentialsError:
        print("  ❌ AWS credentials not found")
        return False
    except ClientError as e:
        print(f"  ❌ AWS credential error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

def test_s3_access():
    """Test S3 access and bucket permissions"""
    print("\n🪣 Testing S3 Access:")
    
    bucket_name = os.getenv('S3_EMBEDDINGS_BUCKET', 'storeofvectors')
    region = os.getenv('AWS_REGION', 'ap-south-1')
    
    print(f"  📍 Bucket: {bucket_name}")
    print(f"  📍 Region: {region}")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=region
        )
        
        # Test 1: Check if bucket exists and is accessible
        print("\n  🧪 Test 1: Checking bucket existence...")
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"  ✅ Bucket '{bucket_name}' exists and is accessible")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"  ❌ Bucket '{bucket_name}' does not exist")
                return False
            elif error_code == '403':
                print(f"  ❌ Access denied to bucket '{bucket_name}' (403 Forbidden)")
                print("     This means the bucket exists but you don't have permission")
                return False
            else:
                print(f"  ❌ Error checking bucket: {e}")
                return False
        
        # Test 2: Check bucket location
        print("\n  🧪 Test 2: Checking bucket location...")
        try:
            location = s3_client.get_bucket_location(Bucket=bucket_name)
            bucket_region = location['LocationConstraint'] or 'us-east-1'
            print(f"  📍 Bucket region: {bucket_region}")
            
            if bucket_region != region:
                print(f"  ⚠️ Region mismatch! Client: {region}, Bucket: {bucket_region}")
                return False
            else:
                print(f"  ✅ Region matches: {region}")
                
        except ClientError as e:
            print(f"  ❌ Cannot get bucket location: {e}")
            return False
        
        # Test 3: Test list permissions
        print("\n  🧪 Test 3: Testing list permissions...")
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            print(f"  ✅ List permission granted")
        except ClientError as e:
            print(f"  ❌ List permission denied: {e}")
            return False
        
        # Test 4: Test put permissions
        print("\n  🧪 Test 4: Testing put permissions...")
        try:
            test_key = 'test/connection_test.txt'
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=b'Connection test',
                ContentType='text/plain'
            )
            print(f"  ✅ Put permission granted")
            
            # Clean up test object
            s3_client.delete_object(Bucket=bucket_name, Key=test_key)
            print(f"  ✅ Delete permission granted")
            
        except ClientError as e:
            print(f"  ❌ Put/Delete permission denied: {e}")
            return False
        
        print("\n  🎉 All S3 tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ S3 client creation failed: {e}")
        return False

def suggest_solutions():
    """Suggest solutions based on common issues"""
    print("\n💡 Common Solutions:")
    
    print("\n1. **Bucket doesn't exist:**")
    print("   Create the bucket in AWS Console or using AWS CLI:")
    print("   aws s3 mb s3://storeofvectors --region ap-south-1")
    
    print("\n2. **Wrong region:**")
    print("   Update your AWS_REGION environment variable to match bucket region")
    
    print("\n3. **Insufficient permissions:**")
    print("   Your AWS user/role needs these S3 permissions:")
    print("   - s3:GetBucketLocation")
    print("   - s3:ListBucket")
    print("   - s3:GetObject")
    print("   - s3:PutObject")
    print("   - s3:DeleteObject")
    
    print("\n4. **IAM Policy Example:**")
    print("   {")
    print('     "Version": "2012-10-17",')
    print('     "Statement": [')
    print("       {")
    print('         "Effect": "Allow",')
    print('         "Action": [')
    print('           "s3:GetBucketLocation",')
    print('           "s3:ListBucket"')
    print("         ],")
    print('         "Resource": "arn:aws:s3:::storeofvectors"')
    print("       },")
    print("       {")
    print('         "Effect": "Allow",')
    print('         "Action": [')
    print('           "s3:GetObject",')
    print('           "s3:PutObject",')
    print('           "s3:DeleteObject"')
    print("         ],")
    print('         "Resource": "arn:aws:s3:::storeofvectors/*"')
    print("       }")
    print("     ]")
    print("   }")

def main():
    """Run all diagnostics"""
    print("🚀 S3 Connection Diagnostic Tool")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed")
        suggest_solutions()
        return
    
    # Test credentials
    if not test_aws_credentials():
        print("\n❌ AWS credentials test failed")
        suggest_solutions()
        return
    
    # Test S3 access
    if not test_s3_access():
        print("\n❌ S3 access test failed")
        suggest_solutions()
        return
    
    print("\n✅ All tests passed! S3 connection should work.")

if __name__ == "__main__":
    main()