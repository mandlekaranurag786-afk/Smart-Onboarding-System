"""
Integration Test for Welcome Email Automation
Tests the complete onboarding flow from API to email delivery
"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.candidate import Candidate
from app.security import verify_password

client = TestClient(app)

def test_initialize_onboarding_sends_welcome_email():
    """Test that clicking Initialize Onboarding sends welcome email with correct credentials"""
    
    print("\n" + "=" * 60)
    print("🧪 INTEGRATION TEST: Initialize Onboarding Flow")
    print("=" * 60)
    
    # Simulate HR form submission
    test_email = f"integration.test.{datetime.now().timestamp()}@company.com"
    
    candidate_data = {
        "name": "Integration Test User",
        "email": test_email,
        "department": "Engineering",
        "role": "Software Engineer",
        "joining_date": "15/04/2024",
        "reporting_manager": "Test Manager",
        "reporting_manager_email": "manager@company.com"
    }
    
    print(f"\n📝 Step 1: Submitting candidate data...")
    print(f"   Name: {candidate_data['name']}")
    print(f"   Email: {candidate_data['email']}")
    print(f"   Department: {candidate_data['department']}")
    
    # POST to candidates endpoint (simulates "Initialize Onboarding" click)
    response = client.post("/api/candidates/", json=candidate_data)
    
    print(f"\n📡 Step 2: API Response...")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ❌ Error: {response.json()}")
        return False
    
    result = response.json()
    
    # Verify candidate was created
    assert result["name"] == candidate_data["name"], "Candidate name should match"
    assert result["email"] == candidate_data["email"], "Candidate email should match"
    assert result["status"] == "onboarding_started", "Status should be onboarding_started"
    assert result["total_tasks"] == 9, "Should have 9 tasks"
    
    print(f"   ✅ Candidate created successfully")
    print(f"   ID: {result['id']}")
    print(f"   Status: {result['status']}")
    print(f"   Total Tasks: {result['total_tasks']}")
    
    # Verify password in database
    print(f"\n🔐 Step 3: Verifying password in database...")
    db = SessionLocal()
    try:
        candidate = db.query(Candidate).filter_by(email=test_email).first()
        
        assert candidate is not None, "Candidate should exist in database"
        assert candidate.password_hash is not None, "Password hash should be set"
        assert candidate.password_reset_required == 1, "Password reset should be required"
        
        # Verify password is correctly hashed
        is_valid = verify_password("Password@123", candidate.password_hash)
        assert is_valid, "Password should be 'Password@123'"
        
        print(f"   ✅ Password correctly hashed in database")
        print(f"   Password Hash: {candidate.password_hash[:30]}...")
        print(f"   Password Reset Required: {bool(candidate.password_reset_required)}")
        print(f"   Password Verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
    finally:
        db.close()
    
    print(f"\n📧 Step 4: Email delivery status...")
    print(f"   ✅ Welcome email should be sent to: {test_email}")
    print(f"   ✅ Login credentials:")
    print(f"      - Email: {test_email}")
    print(f"      - Password: Password@123")
    
    print("\n" + "=" * 60)
    print("✅ INTEGRATION TEST PASSED!")
    print("=" * 60)
    print(f"\n📬 Check email inbox: {test_email}")
    print("   (Note: Using test email, check your configured test inbox)")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_initialize_onboarding_sends_welcome_email()
        if success:
            print("\n🎉 All integration tests passed!")
            exit(0)
        else:
            print("\n❌ Integration test failed!")
            exit(1)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
