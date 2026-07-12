"""
Project 2: Backend API Development — User Management API
DecodeLabs Full Stack Internship

Data model and routes follow the exact patterns shown in the training deck:

  JSON model (slide "The Neurotransmitter: JSON"):
    {
      "user": {
        "id": 101,
        "profile": {
          "role": "admin"
        }
      }
    }

  RESTful naming (slide "The Language of Nerves: RESTful Naming"):
    GET  /users              <- list users
    POST /users              <- create user
    GET  /users/{id}/posts   <- nested resource
    GET  /first-name         <- flat, noun-based single-field routes (illustrative)

Also demonstrates:
- GET / POST / PUT / DELETE (the four HTTP methods from the deck)
- Syntactic + semantic ("Gatekeeper Rule") validation
- Correct, meaningful HTTP status codes
- Centralized error handling
"""

from flask import Flask, jsonify, request
from datetime import datetime, timezone
import itertools

app = Flask(__name__)

# ---------------------------------------------------------------------------
# In-memory "databases"
# ---------------------------------------------------------------------------

users_db = {}       # id -> {id, first_name, last_name, email, profile: {role, bio}, created_at, updated_at}
posts_db = {}       # id -> {id, user_id, title, content, created_at}

user_id_counter = itertools.count(1)
post_id_counter = itertools.count(1)

VALID_ROLES = {"admin", "user", "moderator"}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def error_response(message, code):
    """Consistent error envelope — the Gatekeeper Rule: never trust the client."""
    return jsonify({"error": True, "message": message}), code


# ---------------------------------------------------------------------------
# Validation — two layers, exactly as shown on "The Gatekeeper Rule" slide
# ---------------------------------------------------------------------------

def validate_user_payload(data, partial=False):
    """
    Layer 1 (syntactic): is the shape/type correct?
    Layer 2 (semantic):  is the value logically valid (e.g. role is a real role)?
    Returns (cleaned_data, error_message_or_None).
    """
    if data is None or not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    cleaned = {}

    if "first_name" in data or not partial:
        first_name = data.get("first_name")
        if not isinstance(first_name, str) or not first_name.strip():
            return None, "Field 'first_name' is required and must be a non-empty string"
        cleaned["first_name"] = first_name.strip()

    if "last_name" in data or not partial:
        last_name = data.get("last_name")
        if not isinstance(last_name, str) or not last_name.strip():
            return None, "Field 'last_name' is required and must be a non-empty string"
        cleaned["last_name"] = last_name.strip()

    if "email" in data or not partial:
        email = data.get("email")
        if not isinstance(email, str) or "@" not in email:
            return None, "Field 'email' is required and must be a valid email address"
        cleaned["email"] = email.strip().lower()

    # Nested "profile" object — mirrors the deck's user -> profile -> role structure
    if "profile" in data or not partial:
        profile = data.get("profile", {})
        if not isinstance(profile, dict):
            return None, "Field 'profile' must be an object"

        role = profile.get("role", "user")
        if role not in VALID_ROLES:
            return None, f"Field 'profile.role' must be one of {sorted(VALID_ROLES)}"

        bio = profile.get("bio")
        if bio is not None and not isinstance(bio, str):
            return None, "Field 'profile.bio' must be a string"

        cleaned["profile"] = {"role": role, "bio": bio}

    return cleaned, None


def validate_post_payload(data):
    if data is None or not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return None, "Field 'title' is required and must be a non-empty string"

    content = data.get("content")
    if content is not None and not isinstance(content, str):
        return None, "Field 'content' must be a string"

    return {"title": title.strip(), "content": content}, None


def serialize_user(user_id, user):
    return {"id": user_id, **user}


def serialize_post(post_id, post):
    return {"id": post_id, **post}


# ---------------------------------------------------------------------------
# Routes — GET /users, POST /users, GET /users/{id}/posts (per the deck)
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    """Simple health check endpoint."""
    return jsonify({"message": "DecodeLabs User API is alive", "status": "ok"})


@app.get("/users")
def get_users():
    """GET /users — list all users. Safe & idempotent.
    Optional query param: ?role=admin|user|moderator
    """
    role_filter = request.args.get("role")
    if role_filter and role_filter not in VALID_ROLES:
        return error_response(f"Query param 'role' must be one of {sorted(VALID_ROLES)}", 400)

    items = [serialize_user(uid, u) for uid, u in users_db.items()]
    if role_filter:
        items = [u for u in items if u["profile"]["role"] == role_filter]
    return jsonify(items), 200


@app.get("/users/<int:user_id>")
def get_user(user_id):
    """GET /users/{id} — retrieve a single user. 404 if it doesn't exist."""
    user = users_db.get(user_id)
    if user is None:
        return error_response(f"User with id {user_id} not found", 404)
    return jsonify(serialize_user(user_id, user)), 200


@app.post("/users")
def create_user():
    """POST /users — create a new user. Unsafe & non-idempotent."""
    data = request.get_json(silent=True)
    cleaned, err = validate_user_payload(data, partial=False)
    if err:
        return error_response(err, 400)

    user_id = next(user_id_counter)
    timestamp = now_iso()
    user = {
        "first_name": cleaned["first_name"],
        "last_name": cleaned["last_name"],
        "email": cleaned["email"],
        "profile": cleaned["profile"],
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    users_db[user_id] = user
    return jsonify(serialize_user(user_id, user)), 201


@app.put("/users/<int:user_id>")
def update_user(user_id):
    """PUT /users/{id} — update fields on an existing user.
    Semantic validation: the user must actually exist (404 if not)."""
    if user_id not in users_db:
        return error_response(f"User with id {user_id} not found", 404)

    data = request.get_json(silent=True)
    cleaned, err = validate_user_payload(data, partial=True)
    if err:
        return error_response(err, 400)

    user = users_db[user_id]
    user.update(cleaned)
    user["updated_at"] = now_iso()
    users_db[user_id] = user
    return jsonify(serialize_user(user_id, user)), 200


@app.delete("/users/<int:user_id>")
def delete_user(user_id):
    """DELETE /users/{id} — remove a user. 204 No Content on success."""
    if user_id not in users_db:
        return error_response(f"User with id {user_id} not found", 404)
    del users_db[user_id]
    return "", 204


# --- Nested resource, exactly like the deck's "GET /users/{id}/posts" example ---

@app.get("/users/<int:user_id>/posts")
def get_user_posts(user_id):
    """GET /users/{id}/posts — list all posts belonging to one user."""
    if user_id not in users_db:
        return error_response(f"User with id {user_id} not found", 404)
    items = [serialize_post(pid, p) for pid, p in posts_db.items() if p["user_id"] == user_id]
    return jsonify(items), 200


@app.post("/users/<int:user_id>/posts")
def create_user_post(user_id):
    """POST /users/{id}/posts — create a post owned by that user."""
    if user_id not in users_db:
        return error_response(f"User with id {user_id} not found", 404)

    data = request.get_json(silent=True)
    cleaned, err = validate_post_payload(data)
    if err:
        return error_response(err, 400)

    post_id = next(post_id_counter)
    post = {
        "user_id": user_id,
        "title": cleaned["title"],
        "content": cleaned["content"],
        "created_at": now_iso(),
    }
    posts_db[post_id] = post
    return jsonify(serialize_post(post_id, post)), 201


# ---------------------------------------------------------------------------
# Global error handlers — catch anything that slips past route-level checks
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return error_response("Resource not found", 404)


@app.errorhandler(405)
def method_not_allowed(e):
    return error_response("Method not allowed on this endpoint", 405)


@app.errorhandler(500)
def server_error(e):
    return error_response("Internal server error", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
