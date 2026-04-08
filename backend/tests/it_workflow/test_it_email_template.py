"""
Test script for IT Equipment Allocation Email Template
"""
from app.email.email_templates import render_it_equipment_allocation_email
from app.config import BACKEND_URL, FRONTEND_URL
import os

def test_email_rendering():
    """Test email template rendering"""
    print("Testing IT Equipment Allocation Email Template...")
    print("=" * 60)
    
    # Test data
    test_data = {
        'candidate_name': 'John Doe',
        'candidate_email': 'john.doe@company.com',
        'role': 'Software Engineer',
        'department': 'Engineering',
        'joining_date': '2024-01-15',
        'reporting_manager': 'Jane Smith',
        'task_token': '123_1704902400_a1b2c3d4e5f6',
        'backend_url': BACKEND_URL or 'http://localhost:8000'
    }
    
    print("\nTest Data:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    # Render email
    try:
        email_html = render_it_equipment_allocation_email(**test_data)
        
        print("\n✓ Email rendered successfully")
        print(f"  Email length: {len(email_html)} characters")
        
        # Verify required elements are present
        required_elements = [
            'IT Setup Required',
            test_data['candidate_name'],
            test_data['candidate_email'],
            test_data['role'],
            test_data['department'],
            test_data['joining_date'],
            test_data['reporting_manager'],
            test_data['task_token'],
            'Allocation Complete',
            'Need More Time',
            'token=',
            'response='
        ]
        
        print("\nVerifying required elements:")
        all_present = True
        for element in required_elements:
            if element in email_html:
                print(f"  ✓ {element}")
            else:
                print(f"  ✗ {element} - MISSING!")
                all_present = False
        
        if all_present:
            print("\n✅ All required elements present in email")
        else:
            print("\n❌ Some elements missing from email")
            return False
        
        # Save to file for manual inspection
        output_file = 'test_it_email_output.html'
        with open(output_file, 'w') as f:
            f.write(email_html)
        print(f"\n📄 Email saved to: {output_file}")
        print("   Open this file in a browser to preview the email")
        
        # Extract and display button URLs
        print("\nAction Button URLs:")
        if 'token=' in email_html:
            import re
            urls = re.findall(r'href="([^"]*token=[^"]*)"', email_html)
            for i, url in enumerate(urls, 1):
                print(f"  {i}. {url}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error rendering email: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("IT Equipment Allocation Email Template Test")
    print("=" * 60)
    
    success = test_email_rendering()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")
    print("=" * 60)
