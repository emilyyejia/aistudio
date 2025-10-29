# FastAPI + Neon (Postgres) auth backend

Minimal backend providing signup and login endpoints (to wire into a frontend).

Requirements
- Python 3.9+
- A Neon Postgres connection URL (set as `NEON_DATABASE_URL` or `DATABASE_URL`)
- A `SECRET_KEY` environment variable for JWT signing

Quick start
1. Create a virtualenv and install dependencies:

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Create the `users` table in your Neon DB (use psql or any Postgres client). There's a migration SQL file at `migrations/init.sql`.

   psql "$NEON_DATABASE_URL" -f migrations/init.sql

3. Set environment variables (example using zsh):

   export NEON_DATABASE_URL="<your-neon-connection-url>"
   export SECRET_KEY="a-long-random-secret"

4. Run the server:

   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

API
- POST /signup
  - Body JSON: {"email":"you@example.com","password":"secret"}
  - Returns: user object (id, email, created_at)
- POST /login
  - Body JSON: {"email":"you@example.com","password":"secret"}
  - Returns: {"access_token": "...", "token_type":"bearer"}

Notes
- This service stores bcrypt password hashes and returns a JWT access token. The JWT is basic (HS256) and intended for frontend integration. Adjust expiration and token storage per your security needs.
- For production, set a strong `SECRET_KEY` and run behind HTTPS.

Next steps you may want me to do:
- Add token-protected endpoints and middleware to validate JWTs
- Add refresh tokens and logout
- Add tests (unit/integration) for endpoints
