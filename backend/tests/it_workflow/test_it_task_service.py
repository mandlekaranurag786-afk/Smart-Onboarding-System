"""
Test script for IT Task Service
"""
from app.services import ITTaskService
from app.database import create_db_session
from app.models import Task, ITTeamMember

def test_token_generation():
    """Test token generation"""
    print("Testing token generation...")
    
    # Generate multiple tokens
    tokens = set()
    for i in range(10):
        token = ITTaskService.generate_response_token(task_id=i, candidate_id=100+i)
        tokens.add(token)
        print(f"  Token {i+1}: {token}")
    
    # Verify uniqueness
    assert len(tokens) == 10, "Tokens should be unique"
    print("✓ All tokens are unique")
    
    # Verify format
    for token in tokens:
        parts = token.split('_')
        assert len(parts) == 3, "Token should have 3 parts"
        assert parts[0].isdigit(), "First part should be task_id"
        assert parts[1].isdigit(), "Second part should be timestamp"
        assert len(parts[2]) == 16, "Third part should be 16-char hash"
    print("✓ All tokens have correct format")
    print()

def test_token_validation():
    """Test token validation"""
    print("Testing token validation...")
    
    db = create_db_session()
    try:
        # Get a task from database
        task = db.query(Task).first()
        if not task:
            print("⚠ No tasks in database, skipping validation test")
            return
        
        # Generate and assign token
        token = ITTaskService.generate_response_token(task.id, 1)
        task.it_response_token = token
        db.commit()
        print(f"  Assigned token to task {task.id}: {token}")
        
        # Validate the token
        validated_task = ITTaskService.validate_token(token, db)
        assert validated_task is not None, "Token should be valid"
        assert validated_task.id == task.id, "Should return correct task"
        print(f"✓ Token validated successfully for task {task.id}")
        
        # Test invalid token
        invalid_task = ITTaskService.validate_token("invalid_token_123", db)
        assert invalid_task is None, "Invalid token should return None"
        print("✓ Invalid token correctly rejected")
        
        # Test empty token
        empty_task = ITTaskService.validate_token("", db)
        assert empty_task is None, "Empty token should return None"
        print("✓ Empty token correctly rejected")
        print()
        
    finally:
        db.close()

def test_it_team_verification():
    """Test IT team member verification"""
    print("Testing IT team member verification...")
    
    db = create_db_session()
    try:
        # Get IT team members from database
        members = db.query(ITTeamMember).all()
        print(f"  Found {len(members)} IT team members in database")
        
        if members:
            # Test authorized email
            authorized_email = members[0].email
            is_authorized = ITTaskService.verify_it_team_member(authorized_email, db)
            assert is_authorized, "Known IT team member should be authorized"
            print(f"✓ Authorized email verified: {authorized_email}")
        
        # Test unauthorized email
        is_unauthorized = ITTaskService.verify_it_team_member("random@example.com", db)
        assert not is_unauthorized, "Random email should not be authorized"
        print("✓ Unauthorized email correctly rejected")
        
        # Test empty email
        is_empty = ITTaskService.verify_it_team_member("", db)
        assert not is_empty, "Empty email should not be authorized"
        print("✓ Empty email correctly rejected")
        print()
        
    finally:
        db.close()

def test_button_response_processing():
    """Test button response processing"""
    print("Testing button response processing...")
    
    db = create_db_session()
    try:
        # Get a task
        task = db.query(Task).filter(Task.it_response_token.isnot(None)).first()
        if not task:
            print("⚠ No tasks with tokens, skipping response processing test")
            return
        
        # Get IT team member
        it_member = db.query(ITTeamMember).first()
        if not it_member:
            print("⚠ No IT team members, skipping response processing test")
            return
        
        print(f"  Testing with task {task.id} and IT member {it_member.email}")
        
        # Test unauthorized response
        result = ITTaskService.process_button_response(
            token=task.it_response_token,
            response="complete",
            responder_email="unauthorized@example.com",
            responder_name="Unauthorized User",
            message="Test",
            db=db
        )
        assert not result["success"], "Unauthorized response should fail"
        assert result["error_code"] == "UNAUTHORIZED"
        print("✓ Unauthorized response correctly rejected")
        
        # Test invalid token
        result = ITTaskService.process_button_response(
            token="invalid_token",
            response="complete",
            responder_email=it_member.email,
            responder_name=it_member.name,
            message="Test",
            db=db
        )
        assert not result["success"], "Invalid token should fail"
        assert result["error_code"] == "INVALID_TOKEN"
        print("✓ Invalid token correctly rejected")
        
        print()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("IT Task Service Test Suite")
    print("=" * 60)
    print()
    
    test_token_generation()
    test_token_validation()
    test_it_team_verification()
    test_button_response_processing()
    
    print("=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
