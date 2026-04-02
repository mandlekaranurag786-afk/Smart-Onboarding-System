"""
Quick Mailgun Test Script
Tests the basic Mailgun integration
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mailgun_connection():
    """Test basic Mailgun API connection"""
    print("=" * 60)
    print("🚀 Testing Mailgun Connection")
    print("=" * 60)
    
    api_key = os.getenv("MAILGUN_API_KEY")
    domain = os.getenv("MAILGUN_DOMAIN")
    
    if not api_key or not domain:
        print("❌ FAILED: Missing MAILGUN_API_KEY or MAILGUN_DOMAIN")
        return False
    
    print(f"✅ API Key: {api_key[:20]}...")
    print(f"✅ Domain: {domain}")
    print()
    
    # Test sending a simple email
    print("📧 Sending test email...")
    
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": f"OnboardIQ <postmaster@{domain}>",
                "to": "ishaanyapoddar@gmail.com",
                "subject": "✅ Mailgun Integration Test - OnboardIQ",
                "text": "Congratulations! Your Mailgun integration is working correctly.",
                "html": """
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #4CAF50;">✅ Success!</h2>
                    <p>Your Mailgun integration with OnboardIQ is working correctly.</p>
                    <p>You can now send emails through the OnboardIQ system.</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">This is a test email from OnboardIQ by KONVERGE.AI</p>
                </body>
                </html>
                """
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: Email sent!")
            print(f"   Message ID: {result.get('id', 'N/A')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            print()
            print("📬 Check your inbox at: ishaanyapoddar@gmail.com")
            return True
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n")
    success = test_mailgun_connection()
    print("\n" + "=" * 60)
    if success:
        print("🎉 Mailgun is configured correctly!")
        print("You can now run: python test_email_system.py")
    else:
        print("⚠️  Please check your Mailgun configuration")
    print("=" * 60 + "\n")
