"""
Tests for the DecodeLabs Nervous System API — Project 2.

Run with:
    python -m pytest tests/
or (no pytest required):
    python -m unittest discover tests
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, users_db, posts_db, user_id_counter, post_id_counter
import itertools


class NervousSystemAPITestCase(unittest.TestCase):
    def setUp(self):
        """Reset the in-memory 'brain' before every test — each test starts clean."""
        app.config["TESTING"] = True
        self.client = app.test_client()
        users_db.clear()
        posts_db.clear()
        # Reset the id counters so tests are predictable
        import app as app_module
        app_module.user_id_counter = itertools.count(1)
        app_module.post_id_counter = itertools.count(1)

    # -- Health check -----------------------------------------------------

    def test_health_check(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["status"], "ok")

    # -- Create (POST /users) ----------------------------------------------

    def test_create_user_success(self):
        payload = {
            "first_name": "Martina",
            "last_name": "Plantijn",
            "email": "martina@decodelabs.tech",
            "profile": {"role": "admin", "bio": "Backend lead"},
        }
        resp = self.client.post("/users", json=payload)
        data = resp.get_json()
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(data["first_name"], "Martina")
        self.assertEqual(data["profile"]["role"], "admin")
        self.assertIn("id", data)

    def test_create_user_missing_title_fails_syntactic_validation(self):
        payload = {"last_name": "NoFirstName", "email": "x@decodelabs.tech", "profile": {"role": "user"}}
        resp = self.client.post("/users", json=payload)
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(resp.get_json()["error"])

    def test_create_user_invalid_role_fails_semantic_validation(self):
        payload = {
            "first_name": "Bad",
            "last_name": "Role",
            "email": "bad@decodelabs.tech",
            "profile": {"role": "superadmin"},
        }
        resp = self.client.post("/users", json=payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("role", resp.get_json()["message"])

    def test_create_user_invalid_email_fails(self):
        payload = {
            "first_name": "No",
            "last_name": "AtSign",
            "email": "not-an-email",
            "profile": {"role": "user"},
        }
        resp = self.client.post("/users", json=payload)
        self.assertEqual(resp.status_code, 400)

    # -- Read (GET /users, GET /users/<id>) ---------------------------------

    def test_get_users_empty_list(self):
        resp = self.client.get("/users")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_single_user_not_found(self):
        resp = self.client.get("/users/999")
        self.assertEqual(resp.status_code, 404)

    def test_get_single_user_found(self):
        create = self.client.post("/users", json={
            "first_name": "Alex", "last_name": "Rivera",
            "email": "alex@decodelabs.tech", "profile": {"role": "user"},
        })
        user_id = create.get_json()["id"]
        resp = self.client.get(f"/users/{user_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["first_name"], "Alex")

    def test_filter_users_by_role(self):
        self.client.post("/users", json={
            "first_name": "Admin", "last_name": "One",
            "email": "admin@decodelabs.tech", "profile": {"role": "admin"},
        })
        self.client.post("/users", json={
            "first_name": "Regular", "last_name": "User",
            "email": "user@decodelabs.tech", "profile": {"role": "user"},
        })
        resp = self.client.get("/users?role=admin")
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["profile"]["role"], "admin")

    # -- Update (PUT /users/<id>) --------------------------------------------

    def test_update_user_success(self):
        create = self.client.post("/users", json={
            "first_name": "Martina", "last_name": "Plantijn",
            "email": "martina@decodelabs.tech", "profile": {"role": "user"},
        })
        user_id = create.get_json()["id"]
        resp = self.client.put(f"/users/{user_id}", json={"profile": {"role": "moderator"}})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["profile"]["role"], "moderator")

    def test_update_nonexistent_user_returns_404(self):
        resp = self.client.put("/users/999", json={"profile": {"role": "admin"}})
        self.assertEqual(resp.status_code, 404)

    # -- Delete (DELETE /users/<id>) ------------------------------------------

    def test_delete_user_success(self):
        create = self.client.post("/users", json={
            "first_name": "Temp", "last_name": "User",
            "email": "temp@decodelabs.tech", "profile": {"role": "user"},
        })
        user_id = create.get_json()["id"]
        resp = self.client.delete(f"/users/{user_id}")
        self.assertEqual(resp.status_code, 204)

        follow_up = self.client.get(f"/users/{user_id}")
        self.assertEqual(follow_up.status_code, 404)

    def test_delete_nonexistent_user_returns_404(self):
        resp = self.client.delete("/users/999")
        self.assertEqual(resp.status_code, 404)

    # -- Nested resource: /users/<id>/posts -----------------------------------

    def test_create_and_list_user_posts(self):
        create = self.client.post("/users", json={
            "first_name": "Martina", "last_name": "Plantijn",
            "email": "martina@decodelabs.tech", "profile": {"role": "admin"},
        })
        user_id = create.get_json()["id"]

        post_resp = self.client.post(f"/users/{user_id}/posts", json={
            "title": "Project 2 shipped", "content": "Backend API is live",
        })
        self.assertEqual(post_resp.status_code, 201)

        list_resp = self.client.get(f"/users/{user_id}/posts")
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(len(list_resp.get_json()), 1)

    def test_posts_for_nonexistent_user_returns_404(self):
        resp = self.client.get("/users/999/posts")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
