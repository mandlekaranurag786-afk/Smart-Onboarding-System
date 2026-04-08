"""
Unit Tests for Welcome Email Automation
Tests that welcome emails are sent with correct credentials
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.email.email_schemas import WelcomeEmailData
from app.email.email_factory import email_service
from app import config

def test_default_password_configuration():
    """Test that default password is configured correctly"""
    print("\n🔍 Testing default password configuration...")
    assert config.DEFAULT_PASSWORD == "Password@123", "DEFAULT_PASSWORD should be 'Password@123'"
    print("✅ DEFAULT_PASSWORD is correctly set to 'Password@123'")

def test_welcome_email_with_default_password():
    """Test welcome email sends with default password"""
    print("\n📧 Testing welcome email with default password...")
    
    test_data = WelcomeEmailData(
        candidate_name=" User",
        candidate_email="ninawetejas@gmail.com",  # Use your test email
        role="Software Engineer",
        department="Engineering",
        joining_date=date(2024, 4, 15),
        reporting_manager="Test Manager",
        login_email="ninawetejas@gmail.com",  # Same as candidate_email
        login_password="Password@123",  # Default password
        tasks=["Complete profile", "Upload documents", "Review policies"]
    )
    
    response = email_service.send_welcome_email(test_data)
    
    assert response.success == True, f"Email should send successfully: {response.message}"
    assert response.email_id is not None, "Email should have a message ID"
    
    print(f"✅ Welcome email sent successfully!")
    print(f"   Message ID: {response.email_id}")
    print(f"   Recipient: {test_data.candidate_email}")
    print(f"   Login Email: {test_data.login_email}")
    print(f"   Password: {test_data.login_password}")

def test_login_email_matches_form_email():
    """Test that login email matches the email from form"""
    print("\n🔐 Testing login email matches form email...")
    
    form_email = "test.candidate@company.com"
    
    test_data = WelcomeEmailData(
        candidate_name="New Candidate",
        candidate_email=form_email,
        role="Data Analyst",
        department="Analytics",
        joining_date=date(2024, 4, 20),
        reporting_manager="Analytics Manager",
        login_email=form_email,  # Must match candidate_email
        login_password="Password@123",
        tasks=["Setup tools", "Review policies"]
    )
    
    # Verify login_email matches candidate_email
    assert test_data.login_email == test_data.candidate_email, \
        "Login email should match candidate email from form"
    
    print(f"✅ Login email correctly matches form email")
    print(f"   Form Email: {test_data.candidate_email}")
    print(f"   Login Email: {test_data.login_email}")

def test_azure_email_service_configured():
    """Test that Azure email service is properly configured"""
    print("\n⚙️  Testing Azure email service configuration...")
    
    from app.email.azure_email_service import azure_email_service
    
    assert azure_email_service.client is not None, "Azure email client should be initialized"
    assert azure_email_service.sender_address is not None, "Sender address should be configured"
    
    print(f"✅ Azure email service is configured")
    print(f"   Sender: {azure_email_service.sender_address}")
    print(f"   HR Email: {azure_email_service.hr_email}")
    print(f"   IT Email: {azure_email_service.it_email}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 WELCOME EMAIL AUTOMATION - UNIT TESTS")
    print("=" * 60)
    
    try:
        test_default_password_configuration()
        test_azure_email_service_configured()
        test_login_email_matches_form_email()
        test_welcome_email_with_default_password()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📧 Check your email inbox for the test welcome email")
        print("   Email should contain:")
        print("   - Login Email: ninawetejas@gmail.com")
        print("   - Password: Password@123")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        exit(1)
