"""
Quick Azure Email Configuration Test
Run this to verify Azure Communication Services is properly configured
"""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.email.azure_email_service import azure_email_service
from app.email.email_schemas import WelcomeEmailData


def main():
    print("\n" + "=" * 60)
    print("🚀 AZURE EMAIL QUICK TEST")
    print("=" * 60)
    print()
    
    # Check configuration
    print("📋 Configuration Check:")
    print(f"   Connection String: {'✅ Set' if azure_email_service.connection_string else '❌ Missing'}")
    print(f"   Sender Address: {azure_email_service.sender_address or '❌ Missing'}")
    print(f"   Client Initialized: {'✅ Yes' if azure_email_service.client else '❌ No'}")
    print()
    
    if not azure_email_service.client:
        print("❌ Azure Communication Services not configured!")
        print()
        print("To configure:")
        print("1. Create Azure Communication Services resource")
        print("2. Setup Email Communication Service")
        print("3. Add to backend/.env:")
        print("   AZURE_COMMUNICATION_CONNECTION_STRING=<your-connection-string>")
        print("   AZURE_COMMUNICATION_SENDER_ADDRESS=<your-verified-sender>")
        print()
        print("📖 See AZURE_EMAIL_SETUP.md for detailed instructions")
        print("=" * 60)
        return
    
    print("✅ Azure Email Service is configured!")
    print()
    
    # Ask if user wants to send test email
    print("Would you like to send a test email? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice != 'y':
        print("\nTest cancelled.")
        print("=" * 60)
        return
    
    print("\nEnter recipient email address: ", end="")
    recipient = input().strip()
    
    if not recipient:
        print("❌ No email address provided. Test cancelled.")
        print("=" * 60)
        return
    
    print(f"\n📧 Sending test email to {recipient}...")
    print()
    
    # Send test welcome email
    test_data = WelcomeEmailData(
        candidate_name="Test User",
        candidate_email=recipient,
        role="Software Engineer",
        department="Engineering",
        joining_date=date(2024, 4, 1),
        reporting_manager="Test Manager",
        login_email="test.user@company.com",
        login_password="test@123",
        tasks=[
            "Complete personal information form",
            "Upload required documents",
            "Review company policies"
        ]
    )
    
    response = azure_email_service.send_welcome_email(test_data)
    
    if response.success:
        print("✅ SUCCESS!")
        print(f"   Message: {response.message}")
        if response.email_id:
            print(f"   Message ID: {response.email_id}")
        print()
        print("📬 Check your inbox (and spam folder) for the test email")
    else:
        print("❌ FAILED!")
        print(f"   Error: {response.message}")
        print()
        print("Troubleshooting:")
        print("- Verify connection string is correct")
        print("- Ensure sender address is verified in Azure Portal")
        print("- Check Azure Portal for email domain status")
        print("- Review logs for detailed error messages")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
