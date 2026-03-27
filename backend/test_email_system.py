"""
Quick test script for email system
Run this to verify email configuration
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.email.email_service import email_service
from app.email.email_schemas import (
    WelcomeEmailData,
    ITNotificationData,
    ManagerNotificationData,
    LaptopConfirmationData,
    HRAlertData
)


def test_email_configuration():
    """Test if email service is configured"""
    print("=" * 60)
    print("📧 Testing Email Service Configuration")
    print("=" * 60)
    
    if not email_service.client:
        print("❌ FAILED: SendGrid API key not configured")
        print("\nPlease set SENDGRID_API_KEY in backend/.env file")
        return False
    
    print("✅ SendGrid client initialized")
    print(f"   From: {email_service.from_email}")
    print(f"   HR Email: {email_service.hr_email}")
    print(f"   IT Email: {email_service.it_email}")
    print()
    return True


def test_welcome_email():
    """Test welcome email"""
    print("=" * 60)
    print("📨 Test 1: Welcome Email")
    print("=" * 60)
    
    test_data = WelcomeEmailData(
        candidate_name="John Doe",
        candidate_email="ishaanyapoddar@gmail.com",  # Change to your test email
        role="Software Engineer",
        department="Engineering",
        joining_date=date(2024, 4, 1),
        reporting_manager="Jane Manager",
        login_email="john.doe@company.com",
        login_password="john@123",
        tasks=[
            "Complete personal information form",
            "Upload required documents",
            "Review company policies",
            "Complete IT security training",
            "Setup email and tools"
        ]
    )
    
    print(f"Sending to: {test_data.candidate_email}")
    response = email_service.send_welcome_email(test_data)
    
    if response.success:
        print(f"✅ SUCCESS: {response.message}")
        if response.email_id:
            print(f"   Email ID: {response.email_id}")
    else:
        print(f"❌ FAILED: {response.message}")
    
    print()
    return response.success


def test_it_notification():
    """Test IT notification email"""
    print("=" * 60)
    print("🖥️  Test 2: IT Notification")
    print("=" * 60)
    
    test_data = ITNotificationData(
        candidate_name="John Doe",
        candidate_email="john.doe@company.com",
        role="Software Engineer",
        department="Engineering",
        joining_date=date(2024, 4, 1),
        reporting_manager="Jane Manager"
    )
    
    print(f"Sending to: {email_service.it_email}")
    response = email_service.send_it_notification(test_data)
    
    if response.success:
        print(f"✅ SUCCESS: {response.message}")
    else:
        print(f"❌ FAILED: {response.message}")
    
    print()
    return response.success


def test_manager_notification():
    """Test manager notification email"""
    print("=" * 60)
    print("👔 Test 3: Manager Notification")
    print("=" * 60)
    
    test_data = ManagerNotificationData(
        manager_name="Jane Manager",
        manager_email="ishaanyapoddar@gmail.com",  # Change to your test email
        candidate_name="John Doe",
        candidate_email="john.doe@company.com",
        role="Software Engineer",
        department="Engineering",
        joining_date=date(2024, 4, 1)
    )
    
    print(f"Sending to: {test_data.manager_email}")
    response = email_service.send_manager_notification(test_data)
    
    if response.success:
        print(f"✅ SUCCESS: {response.message}")
    else:
        print(f"❌ FAILED: {response.message}")
    
    print()
    return response.success


def test_laptop_confirmation():
    """Test laptop confirmation email"""
    print("=" * 60)
    print("💻 Test 4: Laptop Confirmation")
    print("=" * 60)
    
    test_data = LaptopConfirmationData(
        candidate_name="John Doe",
        candidate_email="ishaanyapoddar@gmail.com",  # Change to your test email
        candidate_id=1,
        confirmation_link_yes="http://localhost:8000/api/emails/laptop-confirm/1/yes",
        confirmation_link_no="http://localhost:8000/api/emails/laptop-confirm/1/no"
    )
    
    print(f"Sending to: {test_data.candidate_email}")
    response = email_service.send_laptop_confirmation(test_data)
    
    if response.success:
        print(f"✅ SUCCESS: {response.message}")
    else:
        print(f"❌ FAILED: {response.message}")
    
    print()
    return response.success


def test_hr_alert():
    """Test HR alert email"""
    print("=" * 60)
    print("🔔 Test 5: HR Alert")
    print("=" * 60)
    
    test_data = HRAlertData(
        candidate_name="John Doe",
        candidate_email="john.doe@company.com",
        alert_type="laptop_not_received",
        message="John Doe has not received their laptop yet. Please follow up with IT team.",
        additional_info={
            "Joining Date": "2024-04-01",
            "Days Since Joining": "3",
            "Status": "Pending"
        }
    )
    
    print(f"Sending to: {email_service.hr_email}")
    response = email_service.send_hr_alert(test_data)
    
    if response.success:
        print(f"✅ SUCCESS: {response.message}")
    else:
        print(f"❌ FAILED: {response.message}")
    
    print()
    return response.success


def main():
    """Run all tests"""
    print("\n")
    print("🚀 OnboardIQ Email System Test Suite")
    print("=" * 60)
    print()
    
    # Test configuration
    if not test_email_configuration():
        print("\n❌ Configuration test failed. Please fix configuration first.")
        return
    
    print("\n⚠️  WARNING: This will send real emails!")
    print("Make sure to update test email addresses in this script.")
    response = input("\nContinue with email tests? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n✋ Tests cancelled.")
        return
    
    print("\n")
    
    # Run tests
    results = {
        "Welcome Email": test_welcome_email(),
        "IT Notification": test_it_notification(),
        "Manager Notification": test_manager_notification(),
        "Laptop Confirmation": test_laptop_confirmation(),
        "HR Alert": test_hr_alert()
    }
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    print()
    
    if passed == total:
        print("🎉 All tests passed! Email system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    print()


if __name__ == "__main__":
    main()
