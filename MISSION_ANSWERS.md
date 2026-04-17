# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. API key is hardcoded directly in the code (security risk).
2. Debug mode is enabled (`debug=True`), which is unsafe for production.
3. The port is hardcoded to 8000, not allowing environment injection.
4. There is no `/health` check endpoint for load balancers.
5. Shutdown is abrupt without graceful termination of running requests.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcoded | Environment Variables | Security & flexibility across environments |
| Secrets | In source | In .env / Secrets Manager | Prevents credential leaks on GitHub |
| Port    | Fixed (8000) | Env `$PORT` | Cloud providers dynamically assign ports |
| Health check | None | `/health` endpoint | Lets Load Balancer know when app is ready |
| Shutdown | Abrupt | Graceful (SIGTERM) | Prevents losing data for ongoing requests |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: `python:3.11-slim` (a lightweight version of Python).
2. Working directory: `/build` for builder stage, `/app` for runtime stage.
3. Why COPY requirements.txt first? To cache the dependency installation layer, saving time on subsequent builds.
4. CMD vs ENTRYPOINT: ENTRYPOINT defines the executable, while CMD provides the default arguments.

### Exercise 2.3: Image size comparison
- Develop: ~350 MB (Single stage, root capabilities included)
- Production: ~150 MB (Multi-stage build, slim image, no cache)
- Difference: ~57% reduction in size.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://test-deploy-production-e257.up.railway.app
- Screenshot: [See DEPLOYMENT.md and screenshots folder]

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- With no API Key: Returned `401 Unauthorized`.
- With valid API Key: Returned `200 OK` and the answer.
- Rate limits test: After 10 rapid requests, it returned `429 Too Many Requests`.

### Exercise 4.4: Cost guard implementation
- Approach: Used Redis to store and increment a monthly cost tracker by `user_id` (`budget:{user_id}:{YYYY-MM}`). Extracted limits from `MONTHLY_BUDGET_USD` config. If added cost exceeds budget, FastAPI returns an HTTP exception preventing execution.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- Health checks: Added `/health` for liveness and `/ready` mapped to Redis pings for readiness checks.
- Graceful Shutdown: Added a signal handler (`signal.SIGTERM`) to stop accepting requests and drain existing connections before dying.
- Stateless: Moved all agent memory/conversation history into a central Redis instance so any load-balanced pod can serve any user transparently.