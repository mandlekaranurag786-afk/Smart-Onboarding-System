"""
Verify IT email configuration
"""
import sys
sys.path.insert(0, '/tmp/tmp.yMEqJqxqQo/backend')

from app import config

print("=" * 60)
print("IT Email Configuration Verification")
print("=" * 60)

print(f"\n1. IT Email Address: {config.IT_EMAIL}")
print(f"2. HR Email Address: {config.HR_EMAIL}")
print(f"3. Admin Email Address: {config.ADMIN_EMAIL}")
print(f"4. Backend URL: {config.BACKEND_URL}")
print(f"5. Frontend URL: {config.FRONTEND_URL}")

print(f"\n6. Azure Email Configuration:")
print(f"   - Sender Address: {config.AZURE_COMMUNICATION_SENDER_ADDRESS}")
print(f"   - Connection String: {'Configured' if config.AZURE_COMMUNICATION_CONNECTION_STRING else 'NOT configured'}")

print("\n" + "=" * 60)

if config.IT_EMAIL:
    print("✓ IT_EMAIL is configured correctly")
else:
    print("✗ IT_EMAIL is NOT configured - emails will fail!")

if config.AZURE_COMMUNICATION_CONNECTION_STRING and config.AZURE_COMMUNICATION_SENDER_ADDRESS:
    print("✓ Azure email service is configured")
else:
    print("✗ Azure email service is NOT configured")

print("=" * 60)
