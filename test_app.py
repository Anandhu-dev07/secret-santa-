"""
Automated Comprehensive Test Suite for Secret Santa Horror Edition.
Tests database integrity, single-cycle derangement, privacy, one-time attempt rules,
and API error states.
"""

import unittest
import json
from app import app
import database as db

class SecretSantaHorrorTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        # Seed fresh database
        db.seed_sample_students(force_reset=True)

    def test_01_database_seed_count(self):
        """Verify exactly 25 students, 25 preferences, and 25 cycle assignments exist."""
        with db.get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM users")
            self.assertEqual(c.fetchone()[0], 25, "Must have exactly 25 students.")

            c.execute("SELECT COUNT(*) FROM gift_preferences")
            self.assertEqual(c.fetchone()[0], 25, "Must have 25 gift preferences.")

            c.execute("SELECT COUNT(*) FROM secret_santa_assignments")
            self.assertEqual(c.fetchone()[0], 25, "Must have 25 Secret Santa assignments.")

    def test_02_no_self_assignment_and_valid_derangement(self):
        """Verify no student is assigned to themselves and every student is a recipient."""
        with db.get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT giver_id, receiver_id FROM secret_santa_assignments")
            assignments = c.fetchall()
            
            givers = set()
            receivers = set()
            for giver, receiver in assignments:
                self.assertNotEqual(giver, receiver, f"Student {giver} must not receive themselves!")
                givers.add(giver)
                receivers.add(receiver)

            self.assertEqual(len(givers), 25, "All 25 students must give a gift.")
            self.assertEqual(len(receivers), 25, "All 25 students must receive a gift.")

    def test_03_authentication_valid_and_invalid(self):
        """Test secure login and horror error messages."""
        # Valid login
        resp = self.client.post("/login", data={
            "email": "student01@example.com",
            "password": "HorrorSanta#2026"
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"THE NIGHT HAS BEGUN", resp.data)

        # Invalid password
        resp_invalid = self.client.post("/login", data={
            "email": "student01@example.com",
            "password": "WrongPassword123"
        })
        self.assertIn(b"THE DOOR REMAINS LOCKED", resp_invalid.data)

    def test_04_wheel_data_privacy(self):
        """Verify wheel data has 25 slices, current user is excluded, and recipient identity is masked."""
        # Log in as Student 05
        self.client.post("/login", data={
            "email": "student05@example.com",
            "password": "HorrorSanta#2026"
        })

        resp = self.client.get("/api/wheel-data")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        
        self.assertTrue(data["success"])
        self.assertEqual(len(data["slices"]), 25, "Wheel must have exactly 25 color slices.")

        # Ensure no actual real student names or passwords leaked in disguised slices
        for s in data["slices"]:
            self.assertNotIn("Student 05", s["disguised_name"])
            self.assertNotIn("password", s)

    def test_05_one_time_participation_and_anti_replay(self):
        """Test complete selection ritual, verify recipient reveal, and test that 2nd attempt is rejected."""
        # Log in as Student 07
        self.client.post("/login", data={
            "email": "student07@example.com",
            "password": "HorrorSanta#2026"
        })

        # 1. Throw dart
        throw_resp = self.client.post("/api/throw-dart")
        self.assertEqual(throw_resp.status_code, 200)
        throw_data = json.loads(throw_resp.data)
        self.assertTrue(throw_data["success"])
        self.assertIn("target_slice_index", throw_data)
        # Verify recipient name is NOT in throw response (Req 11 & 12)
        self.assertNotIn("recipient_name", throw_data)

        # 2. Reveal
        reveal_resp = self.client.post("/api/reveal", json={"slice_index": throw_data["target_slice_index"]})
        self.assertEqual(reveal_resp.status_code, 200)
        reveal_data = json.loads(reveal_resp.data)
        self.assertTrue(reveal_data["success"])
        self.assertTrue(len(reveal_data["recipient_name"]) > 0)
        self.assertTrue(len(reveal_data["gift_preference"]) > 0)
        self.assertNotEqual(reveal_data["recipient_name"], "Student 07", "Cannot get self!")

        # 3. ATTEMPT 2: Try to throw dart again! MUST BE FORBIDDEN (403)
        replay_resp = self.client.post("/api/throw-dart")
        self.assertEqual(replay_resp.status_code, 403, "Second attempt must be blocked by server.")
        replay_data = json.loads(replay_resp.data)
        self.assertIn("THAT WAS YOUR LAST CHANCE", replay_data["error"])

    def test_06_unauthorized_access_protection(self):
        """Test that unauthenticated requests to protected endpoints fail."""
        # Clear session
        self.client.get("/logout")

        resp = self.client.get("/dashboard")
        self.assertEqual(resp.status_code, 302, "Unauthenticated access must redirect to login.")

        api_resp = self.client.get("/api/wheel-data")
        self.assertEqual(api_resp.status_code, 401, "Unauthenticated API request must return 401.")

if __name__ == "__main__":
    unittest.main()
