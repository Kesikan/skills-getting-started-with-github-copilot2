"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Tennis Team": {
            "description": "Competitive tennis team with tournaments and practice drills",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Basketball Club": {
            "description": "Join our basketball team for pickup games and skill development",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking through competitive debate",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Robotics Club": {
            "description": "Design and build robots for engineering competitions",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Drama Club": {
            "description": "Perform in stage productions and develop acting skills",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": []
        },
        "Art Studio": {
            "description": "Explore painting, drawing, sculpture, and other visual arts",
            "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Music Ensemble": {
            "description": "Play instruments and perform in concerts with our school orchestra",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 30,
            "participants": []
        }
    }
    
    # Clear current activities and restore original
    activities.clear()
    activities.update(original)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that all activities are present
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Tennis Team" in data
        assert len(data) == 10
    
    def test_activity_structure(self, client, reset_activities):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_activity_participants(self, client, reset_activities):
        """Test that participants are returned correctly"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup"""
        response = client.post(
            "/activities/Tennis%20Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds participant"""
        # Signup
        client.post("/activities/Tennis%20Team/signup?email=newstudent@mergington.edu")
        
        # Verify
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Tennis Team"]["participants"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that duplicate signup is rejected"""
        # Student already signed up for Chess Club
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for two activities
        response1 = client.post(
            f"/activities/Tennis%20Team/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/Basketball%20Club/signup?email={email}"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Tennis Team"]["participants"]
        assert email in data["Basketball Club"]["participants"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant"""
        # Unregister
        client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        # Verify
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
        # Verify other participant still there
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_student_not_signed_up(self, client, reset_activities):
        """Test unregister for student not signed up"""
        response = client.post(
            "/activities/Tennis%20Team/unregister?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that unregistered student can sign up again"""
        email = "michael@mergington.edu"
        
        # First unregister
        response1 = client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response1.status_code == 200
        
        # Then sign up again
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]


class TestAvailability:
    """Tests for availability calculation"""
    
    def test_availability_calculation(self, client, reset_activities):
        """Test that availability is calculated correctly"""
        response = client.get("/activities")
        data = response.json()
        
        # Tennis Team has max 16, 0 participants
        tennis = data["Tennis Team"]
        assert tennis["max_participants"] == 16
        assert len(tennis["participants"]) == 0
    
    def test_activity_full(self, client, reset_activities):
        """Test activity with participants"""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club has max 12, 2 participants
        chess = data["Chess Club"]
        assert chess["max_participants"] == 12
        assert len(chess["participants"]) == 2
        spots_left = chess["max_participants"] - len(chess["participants"])
        assert spots_left == 10
