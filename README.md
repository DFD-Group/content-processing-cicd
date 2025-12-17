# content-processing-cicd

Monorepo for the **Content Processing** platform, including three deployable services and the CI/CD automation required to build, test, and deploy them to **Windows Server** environments.

## What’s inside

- **auth** — Issues and validates API keys (shared authorization layer for all services)
- **pdf-renderer** — REST API for PDF rendering operations
- **text2image** — FastAPI service for text-to-image generation

## CI/CD goals

- Build and package each service as a versioned artifact
- Run integration checks (including `/health` returning `"status":"UP"`)
- Deploy to **staging** and **production** using a release-based layout (`releases/` + `current/`) with rollback capability

## Target runtime

- Windows Server hosting (service-wrapped execution)
- REST endpoints exposed for all services

Monorepo services:
- auth (.NET) — 8080
- pdf-renderer (.NET) — 8081
- text2image (FastAPI) — 8082

Health:
- GET /health -> JSON contains "status":"UP"
