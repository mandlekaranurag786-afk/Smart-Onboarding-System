"""
Test the FastAPI endpoints
"""
import sys
sys.path.insert(0, 'backend')

import asyncio
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health():
    """Test health endpoint"""
    response = client.get("/health")
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200

def test_get_candidates():
    """Test get candidates"""
    response = client.get("/api/candidates/")
    print(f"\nGet candidates: {response.status_code}")
    print(f"Candidates: {len(response.json())}")
    for candidate in response.json():
        print(f"  - {candidate['name']}: {candidate['completion_percentage']}% complete")
    assert response.status_code == 200

def test_create_candidate():
    """Test create candidate"""
    new_candidate = {
        "name": "Aayush",
        "email": "aayush@konverge.ai",
        "department": "Engineering",
        "role": "Engineer",
        "joining_date": "25/03/2026",
        "reporting_manager": "Kaustubh Vartak"
    }
    
    response = client.post("/api/candidates/", json=new_candidate)
    print(f"\nCreate candidate: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Created: {data['name']}")
        print(f"ID: {data['id']}")
        print(f"Tasks: {data['total_tasks']}")
        print(f"Status: {data['status']}")
    else:
        print(f"Error: {response.text}")

def test_get_stakeholders():
    """Test get stakeholders"""
    response = client.get("/api/stakeholders/")
    print(f"\nGet stakeholders: {response.status_code}")
    print(f"Stakeholders: {len(response.json())}")
    for s in response.json():
        status = "ON LEAVE" if not s['is_available'] else "AVAILABLE"
        print(f"  - {s['name']} ({s['role']}): {status}")

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING FASTAPI ENDPOINTS")
    print("=" * 60)
    
    test_health()
    test_get_candidates()
    test_get_stakeholders()
    test_create_candidate()
    
    # Check candidates again
    test_get_candidates()
    
    print("\n" + "=" * 60)
    print("✓ API tests complete!")
    print("=" * 60)
