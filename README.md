# Project 2: The Nervous System
### Backend API Development — DecodeLabs Full Stack Internship

> "Project 1 was the skin. Project 2 is the life." — *DecodeLabs Training Kit*

If Project 1 (the frontend) was the **skin** — what the user sees and touches —
this project is the **nervous system**: the brain that processes logic, and
the nerves (API endpoints) that carry signals between the client and the server.
This repo is a working **User Management API** built to satisfy every
requirement of that milestone, using the exact vocabulary and architecture
taught in the training kit.

Built with **Python + Flask**. Every endpoint has been run, tested manually,
and covered by an automated test suite — this isn't just a spec, it's
confirmed working code.

---

## Project structure

```
nervous-system-api/
├── app.py              # The API — all routes, validation, and logic
├── requirements.txt    # Dependencies
├── tests/
│   └── test_api.py     # Automated test suite (15 tests, all passing)
├── .gitignore
└── README.md
```

---

## Architecture: The Nervous System Metaphor

The training deck maps backend concepts onto human anatomy. Here's how each
piece of that metaphor shows up literally in this codebase:

| Deck Concept | Anatomical Metaphor | Where it lives in `app.py` |
|---|---|---|
| **IPO Model** | Input → Process → Output, the system's "pulse" | Every route: request in → validation/logic → JSON response out |
| **The Synaptic Gap** | Client and server communicating across "the network void" | JSON request/response bodies crossing the client–server boundary |
| **Statelessness** | The nervous system's ability to regenerate/restart independently | No server-side session — every request is self-contained |
| **The Gatekeeper Rule** | The blood-brain barrier — "Never Trust the Client" | `validate_user_payload()` — a two-layer check before anything touches the "brain" (the data store) |
| **HTTP Methods** | The "anatomy of action" | `GET` (safe/idempotent), `POST` (creation), `PUT` (update), `DELETE` (removal) |
| **RESTful Naming** | "The Language of Nerves" — resources are nouns, methods are verbs | `/users`, `/users/{id}/posts` — never `/getUsers` |
| **JSON** | "The Neurotransmitter" — the signal carried across the synapse | The `user → profile → role` shape used throughout |
| **Status Codes** | "The Server's Tone" — communicating state without forcing the client to guess | 200 / 201 / 204 / 400 / 404 used precisely, not just "200 for everything" |
| **Autonomic Defense** | Self-healing, isolating failure | Centralized error handlers + a full automated test suite |
| **Documentation** | "The Blueprint" | This README — because "if it isn't documented, it doesn't exist" |

### The Gatekeeper Rule in detail

The deck describes validation as a **blood-brain barrier** with two layers.
This API implements both, in order, before any data reaches storage:

1. **Syntactic validation** — *Is the format correct?* Is `email` actually a
   string containing `@`? Is `profile` an object, not a string or number?
2. **Semantic validation** — *Is the logic valid?* Is `profile.role` one of
   the real, allowed roles (`admin`, `user`, `moderator`)? Does the user ID
   in the URL actually exist in the system?

A request that fails either layer never reaches the data store — it's
rejected at the gate with a `400` and a clear message, exactly like the
"Malformed Data / Pathogens" being blocked at the barrier in the deck's
diagram.

---

## Getting Started (step-by-step)

### 1. Get the files onto your computer
Download this repo (or clone it — see below) into a folder, e.g.
`nervous-system-api/`.

If you downloaded a `.zip`, extract it first. Sometimes extracting creates a
nested folder — if so, go one level deeper until you see `app.py` directly.

```bash
git clone https://github.com/YOUR-USERNAME/nervous-system-api.git
cd nervous-system-api
```

### 2. Open a terminal in that folder

**Windows (Command Prompt or PowerShell):**
```bash
cd Downloads\nervous-system-api
```

**Mac/Linux (Terminal):**
```bash
cd ~/Downloads/nervous-system-api
```

Confirm the files are there:
```bash
dir        # Windows
ls         # Mac/Linux
```
You should see `app.py`, `requirements.txt`, and a `tests/` folder directly.

### 3. Install the dependencies
```bash
pip install -r requirements.txt
```

If this fails later with `ModuleNotFoundError: No module named 'flask'`, it
usually means `pip` and `python` point to different installations. Fix it by
being explicit:
```bash
python -m pip install -r requirements.txt
```
(On Mac/Linux, you may need `python3 -m pip install -r requirements.txt`.)

### 4. Run the automated tests (optional but recommended)
```bash
python -m unittest discover tests -v
```
You should see all 15 tests pass:
```
Ran 15 tests in 0.028s
OK
```

### 5. Start the server (bring the nervous system online)
```bash
python app.py
```
You should see:
```
 * Running on http://127.0.0.1:8000
```
**Leave this terminal window open** — this is your live server.

### 6. Send it a signal (test it manually)

**Easiest option — your browser.** Visit:
```
http://127.0.0.1:8000/
```
You should see:
```json
{"message": "DecodeLabs User API is alive", "status": "ok"}
```
Then:
```
http://127.0.0.1:8000/users
```
This returns `[]` until you create a user — that's correct, not an error.

**Using curl in a second terminal (for POST/PUT/DELETE):**

*Mac/Linux/Windows Command Prompt:*
```bash
curl -X POST http://127.0.0.1:8000/users -H "Content-Type: application/json" -d "{\"first_name\":\"Martina\",\"last_name\":\"Plantijn\",\"email\":\"martina@decodelabs.tech\",\"profile\":{\"role\":\"admin\",\"bio\":\"Backend lead\"}}"
```

*Windows PowerShell:* `curl` here is aliased to `Invoke-WebRequest`, and even
`curl.exe` can mangle the `-d` JSON string depending on your PowerShell
version, leading to errors like `unmatched close brace/bracket in URL
position`. The reliable fix is to skip curl entirely and use PowerShell's
own native command instead:
```powershell
$body = @{
    first_name = "Martina"
    last_name = "Plantijn"
    email = "martina@decodelabs.tech"
    profile = @{ role = "admin"; bio = "Backend lead" }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/users" -Method Post -Body $body -ContentType "application/json"
```
This builds the JSON as a PowerShell object first, so there's no manual
quote-escaping to get wrong — confirmed working.

**Prefer a GUI?** Use [Postman](https://www.postman.com/downloads/) or
Insomnia: set the method, paste the URL, and put JSON in **Body → raw → JSON**.

### 7. Stop the server
Go back to the terminal running it and press `Ctrl+C`.

---

## Endpoints ("The Nerves")

| Method | Path                     | Description                             | Success Code |
|--------|--------------------------|------------------------------------------|--------------|
| GET    | `/`                      | Health check                              | 200          |
| GET    | `/users`                 | List all users (optional `?role=`)        | 200          |
| GET    | `/users/<id>`            | Get one user                              | 200          |
| POST   | `/users`                 | Create a user                             | 201          |
| PUT    | `/users/<id>`            | Update a user (partial update)            | 200          |
| DELETE | `/users/<id>`            | Delete a user                             | 204          |
| GET    | `/users/<id>/posts`      | List a user's posts (nested resource)     | 200          |
| POST   | `/users/<id>/posts`      | Create a post owned by that user          | 201          |

Valid `profile.role` values: `admin`, `user`, `moderator`.

## Example requests

**Create a user** (the `user → profile → role` shape from the deck's JSON slide):

*curl (Mac/Linux/Windows CMD):*
```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{
        "first_name": "Martina",
        "last_name": "Plantijn",
        "email": "martina@decodelabs.tech",
        "profile": { "role": "admin", "bio": "Backend lead" }
      }'
# -> 201 Created
```

*PowerShell:*
```powershell
$body = @{
    first_name = "Martina"
    last_name = "Plantijn"
    email = "martina@decodelabs.tech"
    profile = @{ role = "admin"; bio = "Backend lead" }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/users" -Method Post -Body $body -ContentType "application/json"
```

**Get all users, optionally filtered by role:**

*curl:*
```bash
curl http://127.0.0.1:8000/users
curl "http://127.0.0.1:8000/users?role=admin"
```

*PowerShell:*
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/users" -Method Get
Invoke-RestMethod -Uri "http://127.0.0.1:8000/users?role=admin" -Method Get
```

**Update a user's role:**

*curl:*
```bash
curl -X PUT http://127.0.0.1:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"profile": {"role": "moderator"}}'
```

*PowerShell:*
```powershell
$body = @{ profile = @{ role = "moderator" } } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/users/1" -Method Put -Body $body -ContentType "application/json"
```

**Create and list a user's posts (nested resource):**

*curl:*
```bash
curl -X POST http://127.0.0.1:8000/users/1/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "Project 2 shipped", "content": "Backend API is live"}'

curl http://127.0.0.1:8000/users/1/posts
```

*PowerShell:*
```powershell
$body = @{ title = "Project 2 shipped"; content = "Backend API is live" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/users/1/posts" -Method Post -Body $body -ContentType "application/json"

Invoke-RestMethod -Uri "http://127.0.0.1:8000/users/1/posts" -Method Get
```

**Delete a user:**

*curl:*
```bash
curl -X DELETE http://127.0.0.1:8000/users/1
# -> 204 No Content
```

*PowerShell:*
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/users/1" -Method Delete
```

## Error handling ("Communicating State: The Server's Tone")

| Status | Meaning       | When it happens                              |
|--------|---------------|-----------------------------------------------|
| 400    | Bad Request   | Missing/invalid fields (syntactic/semantic validation fails) |
| 404    | Not Found     | User (or post) ID doesn't exist                |
| 405    | Method Not Allowed | Wrong HTTP verb for that route            |
| 500    | Server Error  | Unexpected failure                             |

Every error returns a consistent JSON shape:
```json
{ "error": true, "message": "User with id 999 not found" }
```

## Test coverage

`tests/test_api.py` covers, per HTTP method:

- **Create**: valid user creation, missing-field rejection (syntactic),
  invalid-role rejection (semantic), invalid-email rejection
- **Read**: empty list, 404 on missing user, successful lookup, role filtering
- **Update**: successful partial update, 404 on missing user
- **Delete**: successful deletion + confirms follow-up GET returns 404,
  404 on deleting a nonexistent user
- **Nested resource**: creating/listing a user's posts, 404 for posts under
  a nonexistent user

Run them with:
```bash
python -m unittest discover tests -v
```

## What's intentionally out of scope for this milestone

The deck's "Autonomic Defense" slide covers Authentication (AuthN) and
Authorization (AuthZ) as core backend concepts — but Project 2's actual
requirements (create endpoints, handle input, validate basic data) don't
call for auth. This API is deliberately open with no login layer. That's a
Project 3+ concern, listed below.

## Next steps (Project 3 territory)

- Swap the in-memory `users_db` / `posts_db` dicts for a real database (SQLite/PostgreSQL).
- Add Authentication (AuthN) and Authorization (AuthZ) — currently anyone can hit any endpoint.
- Add rate limiting (429) and pagination on `GET /users`.
- Add circuit breakers for resilience under repeated failures, per the deck's "Autonomic Defense" slide.

---

## Closing note

*"Build with Integrity. Validate Everything. Communicate Clearly. Respect
the Architecture."* — DecodeLabs Training Kit
