"""
Test suite for the Mergington High School Activities API.
Tests all endpoints: GET /activities, POST /signup, DELETE /participants.

Uses AAA (Arrange-Act-Assert) pattern for clear test structure.
"""
import pytest
from fastapi import status


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_200(self, client, reset_activities):
        """GET /activities should return status 200."""
        # Arrange
        # (test data is already set up by reset_activities fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_activities_returns_dict(self, client, reset_activities):
        """GET /activities should return a dictionary of activities."""
        # Arrange
        # (test data is already set up by reset_activities fixture)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_get_activities_contains_activity_details(self, client, reset_activities):
        """Each activity should have required fields."""
        # Arrange
        expected_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            for field in expected_fields:
                assert field in activity_data, f"Missing field '{field}' in {activity_name}"
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_includes_test_activities(self, client, reset_activities):
        """GET /activities should include the test activities we set up."""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity in expected_activities:
            assert activity in activities


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant_returns_200(self, client, reset_activities):
        """Signing up a new participant should return status 200."""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Gym Class"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
    
    def test_signup_new_participant_returns_success_message(self, client, reset_activities):
        """Signup response should contain a success message with email and activity name."""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Gym Class"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Signup should add the participant to the activity's participants list."""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Gym Class"
        
        # Act
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        response_after = client.get("/activities")
        activities_after = response_after.json()
        
        # Assert
        assert email in activities_after[activity]["participants"]
    
    def test_signup_duplicate_participant_returns_400(self, client, reset_activities):
        """Signing up the same participant twice should return 400."""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Gym Class"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Act - Second signup (duplicate)
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Signup for a non-existent activity should return 404."""
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_existing_participant_returns_400(self, client, reset_activities):
        """Signup of an existing participant should return 400."""
        # Arrange
        email = "emma@mergington.edu"  # Already in Programming Class
        activity = "Programming Class"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUnregisterParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_unregister_existing_participant_returns_200(self, client, reset_activities):
        """Unregistering an existing participant should return 200."""
        # Arrange
        email = "emma@mergington.edu"
        activity = "Programming Class"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
    
    def test_unregister_existing_participant_returns_success_message(self, client, reset_activities):
        """Unregister response should contain a success message."""
        # Arrange
        email = "emma@mergington.edu"
        activity = "Programming Class"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
    
    def test_unregister_removes_participant_from_activity(self, client, reset_activities):
        """Unregister should remove the participant from the activity."""
        # Arrange
        email = "emma@mergington.edu"
        activity = "Programming Class"
        
        # Verify participant is in activity before unregister
        response_before = client.get("/activities")
        activities_before = response_before.json()
        assert email in activities_before[activity]["participants"]
        
        # Act
        client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        
        # Assert - Participant should no longer be there
        response_after = client.get("/activities")
        activities_after = response_after.json()
        assert email not in activities_after[activity]["participants"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """Unregister from a non-existent activity should return 404."""
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_unregister_nonexistent_participant_returns_404(self, client, reset_activities):
        """Unregister of a non-existent participant should return 404."""
        # Arrange
        email = "nonexistent@mergington.edu"
        activity = "Programming Class"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_participant_not_in_activity_returns_404(self, client, reset_activities):
        """Unregister a participant not in the activity should return 404."""
        # Arrange
        email = "michael@mergington.edu"  # In Chess Club, not Gym Class
        activity = "Gym Class"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_signup_then_unregister_workflow(self, client, reset_activities):
        """Complete workflow: signup to activity, then unregister."""
        # Arrange
        email = "integration@mergington.edu"
        activity = "Gym Class"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert signup successful
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Act - Verify in activities
        get_response = client.get("/activities")
        activities = get_response.json()
        
        # Assert participant is in activity
        assert email in activities[activity]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        
        # Assert unregister successful
        assert unregister_response.status_code == status.HTTP_200_OK
        
        # Act - Verify removed from activities
        get_response_final = client.get("/activities")
        activities_final = get_response_final.json()
        
        # Assert participant is no longer in activity
        assert email not in activities_final[activity]["participants"]
    
    def test_multiple_signups_different_activities(self, client, reset_activities):
        """A participant should be able to sign up for multiple activities."""
        # Arrange
        email = "multi@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Gym Class"
        
        # Act - Sign up for first activity
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        
        # Assert first signup successful
        assert response1.status_code == status.HTTP_200_OK
        
        # Act - Sign up for second activity
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )
        
        # Assert second signup successful
        assert response2.status_code == status.HTTP_200_OK
        
        # Act - Verify in both activities
        get_response = client.get("/activities")
        activities = get_response.json()
        
        # Assert participant is in both activities
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]
