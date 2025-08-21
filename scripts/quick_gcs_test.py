# quick_gcs_test.py - Quick GCS connection test
import os
from google.cloud import storage
from google.api_core import exceptions as gcs_exceptions
from dotenv import load_dotenv

def quick_gcs_test():
    """Quick test of GCS connection - run this first!"""
    
    # Load environment variables
    load_dotenv()
    
    print("🔧 Quick GCS Connection Test")
    print("=" * 40)
    
    # Check environment variables
    bucket_name = os.getenv('GCS_EMBEDDINGS_BUCKET')
    creds_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not bucket_name:
        print("❌ GCS_EMBEDDINGS_BUCKET not set in environment")
        print("   Set it in your .env file: GCS_EMBEDDINGS_BUCKET=your-bucket-name")
        return False
    
    print(f"📦 Testing bucket: {bucket_name}")
    
    if creds_file:
        print(f"🔑 Using credentials: {creds_file}")
        if not os.path.exists(creds_file):
            print(f"❌ Credentials file not found: {creds_file}")
            return False
    else:
        print("🔑 Using default credentials")
    
    try:
        # Initialize client
        print("\n🔄 Connecting to Google Cloud Storage...")
        client = storage.Client()
        
        # Test bucket access
        print("🔄 Testing bucket access...")
        bucket = client.bucket(bucket_name)
        bucket.reload()
        
        print(f"✅ Successfully connected to bucket: {bucket_name}")
        print(f"   📍 Location: {bucket.location}")
        print(f"   🏷️ Storage class: {bucket.storage_class}")
        
        # Test write permission
        print("\n🔄 Testing write permissions...")
        test_blob = bucket.blob('test-connection.txt')
        test_blob.upload_from_string('Connection test successful!')
        
        print("✅ Write permission confirmed")
        
        # Test read permission
        print("🔄 Testing read permissions...")
        content = test_blob.download_as_text()
        
        print("✅ Read permission confirmed")
        
        # Cleanup
        print("🔄 Cleaning up test file...")
        test_blob.delete()
        
        print("✅ Cleanup successful")
        
        print("\n🎉 GCS connection test PASSED!")
        print("✅ Your configuration is working correctly.")
        
        return True
        
    except gcs_exceptions.NotFound:
        print(f"❌ Bucket not found: {bucket_name}")
        print("   Make sure the bucket exists and you have access to it")
        return False
        
    except gcs_exceptions.Forbidden:
        print(f"❌ Access denied to bucket: {bucket_name}")
        print("   Check your service account permissions")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("   Check your credentials and bucket configuration")
        return False

if __name__ == "__main__":
    success = quick_gcs_test()
    
    if success:
        print("\n🚀 Ready to deploy your application!")
    else:
        print("\n🔧 Please fix the issues above and try again.")
    
    exit(0 if success else 1)