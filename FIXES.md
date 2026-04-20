# FIXES.md — Bug Report & Resolutions

All bugs found in the starter repository, documented with file, line number, problem, and fix.

---

## BUG 1
**File:** `api/main.py`
**Line:** 6
**Problem:** Redis host hardcoded to `localhost`. Inside Docker containers, services communicate via service names on a shared network, not localhost. This causes a connection failure at runtime.
**Fix:** Replaced with `os.getenv("REDIS_HOST", "redis")` so the host is configurable via environment variable with a sensible default.

---

## BUG 2
**File:** `api/main.py`
**Line:** 6
**Problem:** Redis password defined in `.env` as `REDIS_PASSWORD` but never passed to the Redis client. If Redis requires authentication, all operations fail silently with an auth error.
**Fix:** Added `password=os.getenv("REDIS_PASSWORD", None)` to the Redis constructor.

---

## BUG 3
**File:** `api/main.py`
**Line:** 4
**Problem:** `os` module imported but never used for Redis configuration, indicating the env var integration was incomplete.
**Fix:** `os.getenv()` now used for `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, and `QUEUE_NAME`.

---

## BUG 4
**File:** `worker/worker.py`
**Line:** 5
**Problem:** Redis host hardcoded to `localhost`. Same issue as Bug 1 — fails inside Docker containers.
**Fix:** Replaced with `os.getenv("REDIS_HOST", "redis")` and added password and port from environment variables.

---

## BUG 5
**File:** `worker/worker.py`
**Line:** 4
**Problem:** `signal` module imported but never used. The worker had no SIGTERM handler, meaning Docker could kill it mid-job on container stop, leaving jobs permanently stuck in `queued` state.
**Fix:** Added a `handle_sigterm` function and registered it with `signal.signal(signal.SIGTERM, handle_sigterm)`. The main loop now checks a `shutdown` flag and exits cleanly.

---

## BUG 6
**File:** `frontend/app.js`
**Line:** 5
**Problem:** API URL hardcoded to `http://localhost:8000`. Inside Docker, the frontend container cannot reach the API container via localhost — it must use the Docker service name.
**Fix:** Replaced with `process.env.API_URL || "http://api:8000"` so it is configurable via environment variable.

---

## BUG 7
**File:** `api/.env`
**Line:** 1-2
**Problem:** `.env` file containing real credentials (`REDIS_PASSWORD=supersecretpassword123`) was committed to the repository. This is a critical security violation — secrets in git history are permanently exposed.
**Fix:** Added `.env` and `**/.env` to `.gitignore`. Removed `api/.env` from git tracking with `git rm --cached api/.env`. Created `.env.example` with placeholder values for all required variables.

---

## BUG 8
**File:** `api/main.py`
**Line:** 14-15
**Problem:** When a job ID is not found, the endpoint returns `{"error": "not found"}` with HTTP status 200. This is incorrect — callers cannot distinguish a successful empty response from an error. The frontend polling loop would spin indefinitely.
**Fix:** Replaced with `raise HTTPException(status_code=404, detail="Job not found")` for proper HTTP semantics.

---

## BUG 9
**File:** `worker/requirements.txt`
**Line:** 1
**Problem:** `redis` listed with no version pin. Unpinned dependencies install the latest version at build time, breaking reproducibility and risking silent incompatibilities between builds.
**Fix:** Pinned to `redis==5.0.1`.

---

## BUG 10
**File:** `api/requirements.txt`
**Line:** 1-3
**Problem:** `fastapi`, `uvicorn`, and `redis` all listed with no version pins. Same reproducibility issue as Bug 9.
**Fix:** Pinned to `fastapi==0.110.0`, `uvicorn==0.29.0`, `redis==5.0.1`.

---

## BUG 11
**File:** `frontend/package.json`
**Line:** entire file
**Problem:** No `engines` field specifying required Node.js version. Different Node versions can produce different behaviour, breaking reproducibility.
**Fix:** Added `"engines": { "node": ">=18.0.0" }` to lock the minimum Node version.

---

## BUG 12
**File:** `api/main.py` line 13, `worker/worker.py` line 24
**Problem:** Queue name `"job"` hardcoded in both the API and worker. If either side changes the name independently, jobs are silently lost with no error. Also, the original name `"job"` (singular) is inconsistent and non-descriptive.
**Fix:** Both services now read from `os.getenv("QUEUE_NAME", "jobs")`, making the queue name configurable and consistent.