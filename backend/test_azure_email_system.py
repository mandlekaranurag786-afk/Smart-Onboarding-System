"""
Comprehensive Azure Email System Test
Tests all email templates with Azure Communication Services
"""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.email.azure_email_service import azure_email_service
from app.email.email_schemas import (
    WelcomeEmailData,
    ITNotificationData,
    ManagerNotificationData,
    LaptopConfirmationData,
    HRAlertData
)


def test_azure_configuration():
    """Test if Azure email service is configured"""
    print("=" * 60)
    print("📧 Testing Azure Email Service Configuration")
    print("=" * 60)
    
    if not azure_email_service.client:
        print("❌ FAILED: Azure Communication Services not configured")
        print("\nPlease set in backend/.env:")
        print("  AZURE_COMMUNICATION_CONNECTION_STRING=<your-connection-string>")
        print("  AZURE_COMMUNICATION_SENDER_ADDRESS=<your-verified-sender>")
        return False
    
    print("✅ Azure Email client initialized")
    print(f"   Sender: {azure_email_service.sender_address}")
    print(f"   HR Email: {azure_email_service.hr_email}")
    print(f"   IT Email: {azure_email_service.it_email}")
    print()
    return True


def test_welcome_email():
    """Test welcome email via Azure"""
    print("=" * 60)
    print("📨 Test 1: Welcome Email (Azure)")
    print("=" * 60)
    
    test_data = WelcomeEmailData(
        candidate_name="John Doe",
        candidate_email="ishaanyapoddar@gmail.com",
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
    response = azure_email_service.send_welcome_email(test_data)
    
    if response.success:
        print(f"✅ SUCCESS: {response.message}")
        if response.email_id:
            print(f"   Message ID: {response.email_id}")
    else:
        print(f"❌ FAILED: {response.message}")
    
    print()
    return response.success


def test_it_notification():
    """Test IT notification email via Azure"""
    print("=" * 60)
    print("🖥️  Test 2: IT Notification (Azure)")
    print("=" * 60)
    
    test_data = ITNotificationData(
        candidate_name="John Doe",
        candidate_email="john.doe@company.com",
        role="Software Engineer",
        department="Engineering",
        joining_date=date(2024, 4, 1),
        reporting_manager="Jane Manager"
    )
    
    print(f"Sending to IT team: {azure_email_service.it_email}")
    response = azure_email_service.send_it_notification(test_data)
    
    if response.success:
        print(f"✅ SUCCESS: {response.message}")
        if response.email_id:
            print(f"   Message ID: {response.email_id}")
    else:
        print(f"❌ FAILED: {response.message}")
    
    print()
    return response.success


def test_manager_notification():
    """Test manager notification email via Azure"""
    print("=" * 60)
    print("👔 Test 3: Manager Notification (Azure)")
    print("=" * 60)
    
    test_data = ManagerNotificationData(
        manager_name="Jane Manager",
        manager_email="ishaanyapoddar@gmail.com",
        candidate_name="John Doe",
        candidate_email="john.doe@company.com",
        role="Software Engineer",
        department="Engineering",
        joining_date=date(2024, 4, 1)
    )
    
    print(f"Sending to manager: {test_data.manager_email}")
    response = azure_email_service.send_manager_notification(test_data)
    
    if response.success:
        print(f"✅ SUCCESS: {response.message}")
        if response.email_id:
            print(f"   Message ID: {response.email_id}")
    else:
        print(f"❌ FAILED: {response.message}")
    
    print()
    return response.success


def test_laptop_confirmation():
    """Test laptop confirmation email via Azure"""
    print("=" * 60)
    print("💻 Test 4: Laptop Confirmation (Azure)")
    print("=" * 60)
    
    test_data = LaptopConfirmationData(
        candidate_name="John Doe",
        candidate_email="ishaanyapoddar@gmail.com",
        candidate_id=1,
        confirmation_link_yes="http://localhost:8000/confirm-laptop/1/yes",
        confirmation_link_no="http://localhost:8000/confirm-laptop/1/no"
    )
    
    print(f"Sending to: {test_data.candidate_email}")
    response = azure_email_service.send_laptop_confirmation(test_data)
    
    if response.success:
        print(f"✅ SUCCESS: {response.message}")
        if response.email_id:
            print(f"   Message ID: {response.email_id}")
    else:
        print(f"❌ FAILED: {response.message}")
    
    print()
    return response.success


def test_hr_alert():
    """Test HR alert email via Azure"""
    print("=" * 60)
    print("🔔 Test 5: HR Alert (Azure)")
    print("=" * 60)
    
    test_data = HRAlertData(
        candidate_name="John Doe",
        candidate_email="john.doe@company.com",
        alert_type="laptop_not_received",
        message="Candidate has not confirmed laptop receipt after 3 days",
        additional_info={
            "days_elapsed": 3,
            "joining_date": "2024-04-01"
        }
    )
    
    print(f"Sending to HR: {azure_email_service.hr_email}")
    response = azure_email_service.send_hr_alert(test_data)
    
    if response.success:
        print(f"✅ SUCCESS: {response.message}")
        if response.email_id:
            print(f"   Message ID: {response.email_id}")
    else:
        print(f"❌ FAILED: {response.message}")
    
    print()
    return response.success


def test_bulk_welcome_emails():
    """Test sending multiple welcome emails concurrently via Azure"""
    print("=" * 60)
    print("📬 Test 6: Bulk Welcome Emails (Azure)")
    print("=" * 60)
    
    candidates = [
        WelcomeEmailData(
            candidate_name="Alice Smith",
            candidate_email="ishaanyapoddar@gmail.com",
            role="Product Manager",
            department="Product",
            joining_date=date(2024, 4, 1),
            reporting_manager="Bob Director",
            login_email="alice.smith@company.com",
            login_password="alice@123",
            tasks=[
                "Complete personal information form",
                "Upload required documents",
                "Review product roadmap"
            ]
        ),
        WelcomeEmailData(
            candidate_name="Bob Johnson",
            candidate_email="ishaanyapoddar@gmail.com",
            role="Data Analyst",
            department="Analytics",
            joining_date=date(2024, 4, 1),
            reporting_manager="Carol Manager",
            login_email="bob.johnson@company.com",
            login_password="bob@123",
            tasks=[
                "Complete personal information form",
                "Setup analytics tools",
                "Review data policies"
            ]
        )
    ]
    
    print(f"Sending {len(candidates)} welcome emails concurrently...")
    responses = azure_email_service.send_bulk_welcome_emails(candidates)
    
    success_count = sum(1 for r in responses if r.success)
    print(f"\n✅ Successfully sent: {success_count}/{len(candidates)}")
    print(f"❌ Failed: {len(candidates) - success_count}/{len(candidates)}")
    
    for i, response in enumerate(responses):
        candidate = candidates[i]
        if response.success:
            print(f"   ✓ {candidate.candidate_name}: {response.email_id}")
        else:
            print(f"   ✗ {candidate.candidate_name}: {response.message}")
    
    print()
    return success_count == len(candidates)


def test_multiple_recipients():
    """Test sending to multiple recipients with same template"""
    print("=" * 60)
    print("📧 Test 7: Multiple Recipients - Same Template (Azure)")
    print("=" * 60)
    
    test_data = ITNotificationData(
        candidate_name="John Doe",
        candidate_email="john.doe@company.com",
        role="Software Engineer",
        department="Engineering",
        joining_date=date(2024, 4, 1),
        reporting_manager="Jane Manager"
    )
    
    additional_recipients = ["ishaanyapoddar@gmail.com"]
    
    print(f"Sending to IT team + {len(additional_recipients)} additional recipients")
    response = azure_email_service.send_it_notification(
        test_data,
        additional_recipients=additional_recipients
    )
    
    if response.success:
        print(f"✅ SUCCESS: {response.message}")
        if response.email_id:
            print(f"   Message ID: {response.email_id}")
    else:
        print(f"❌ FAILED: {response.message}")
    
    print()
    return response.success


def main():
    """Run all Azure email tests"""
    print("\n" + "=" * 60)
    print("🚀 AZURE COMMUNICATION SERVICES EMAIL TEST SUITE")
    print("=" * 60)
    print()
    
    # Test configuration first
    if not test_azure_configuration():
        print("\n❌ Azure Email Service not configured. Exiting.")
        return
    
    # Run all tests
    results = {
        "Welcome Email": test_welcome_email(),
        "IT Notification": test_it_notification(),
        "Manager Notification": test_manager_notification(),
        "Laptop Confirmation": test_laptop_confirmation(),
        "HR Alert": test_hr_alert(),
        "Bulk Welcome Emails": test_bulk_welcome_emails(),
        "Multiple Recipients": test_multiple_recipients()
    }
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Azure email system is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check configuration and logs.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()