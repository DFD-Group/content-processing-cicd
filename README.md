# content-processing-cicd

Monorepo for the **Content Processing** platform — three deployable services, a shared persistence library, and the CI/CD automation that builds, tests, and deploys everything to **Windows Server** environments.

## Services

| Service | Stack | Description |
|---------|-------|-------------|
| **auth** | .NET 10 / ASP.NET Core | Issues and validates API keys (shared authorisation layer) |
| **pdf-renderer** | .NET 10 / ASP.NET Core | REST API for PDF rendering operations |
| **text2image** | Python 3.14 / FastAPI | Text-to-image generation service |

All services expose `GET /health` returning `{"status":"UP"}` and run as **Windows Services** via WinSW (.NET) or Uvicorn (Python).

Current version: **0.0.1** (read from `backend/<service>/VERSION`).

## Repository layout

```
backend/
  auth/AuthService/                 # .NET auth service
  pdf-renderer/PdfRendererService/  # .NET PDF renderer
  text2image/app/                   # FastAPI service
  shared/
    persistence/                    # EF Core library (DbContext, entities, migrations)
    flyway-sql/                     # Versioned SQL applied by Flyway
    flyway.toml                     # Flyway config (dev / staging / prod environments)
.github/
  workflows/                        # CI & deploy pipelines
  actions/failure-diagnostics/      # Composite action for deploy failure logs
docs/                               # Operational documentation
plans/                              # Completed and in-progress planning docs
scripts/
  ef-migrate.py                     # Create EF migration + generate Flyway SQL
  ef-remove.py                      # Remove last EF migration + delete matching SQL
  alembic-migrate.py                # Create Alembic migration + generate Flyway SQL
  alembic-remove.py                 # Remove last Alembic migration + delete matching SQL
ContentProcessing.slnx              # .NET solution file
```

## Shared persistence

The **ContentProcessing.Persistence** library (EF Core 10 + Npgsql) defines the database model shared by the .NET services.

### Database schemas

| Schema | Tables | Purpose |
|--------|--------|---------|
| `auth` | `api_keys` | API key management |
| `app` | `pdf_to_images`, `images` | PDF-to-image job tracking |

A PostgreSQL enum `app.pdf_to_images_status` tracks job state (`Pending`, `Processing`, `Completed`, `Failed`).

### Migration workflow

Migrations are **authored** with EF Core and **applied** with Flyway:

1. `python scripts/ef-migrate.py` — runs `dotnet ef migrations add`, then generates a numbered Flyway SQL file under `backend/shared/flyway-sql/`
2. `python scripts/alembic-migrate.py` — runs `alembic revision --autogenerate`, then generates a numbered Flyway SQL file (use `--sql-only` to skip revision creation)
3. CI/CD pipelines run `flyway migrate` against the target environment (dev / staging / prod)
4. `python scripts/ef-remove.py` / `python scripts/alembic-remove.py` — reverse the last migration and delete the corresponding SQL file

## CI/CD

Four GitHub Actions workflows run on **self-hosted Windows** runners:

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| **CI (develop)** | Push / PR to `develop` | Restore, build, and publish all services; zip versioned artifacts; upload with 14-day retention |
| **Deploy dev** | After CI succeeds | Run Flyway migrations against the dev database |
| **Deploy staging** | Push to `staging` | Self-contained publish, Flyway migrate, atomic junction deploy, WinSW restart, health checks on ports 9080-9082 |
| **Deploy prod** | Push to `main` | Same as staging, targeting prod paths and health checks on ports 8080-8082 |

### Deployment model

Staging and production use a **junction-based release layout**:

```
D:\services\content-processing\<env>\
  releases\
    <VERSION+SHA>\app\   # immutable release folder
  current\               # NTFS junction pointing to the latest release
```

Each deploy creates a new release folder, switches the `current` junction atomically, and restarts the WinSW-managed service. Previous releases remain on disk for rollback.

### Health checks

| Environment | Ports |
|-------------|-------|
| Staging | 9080 (auth), 9081 (pdf-renderer), 9082 (text2image) |
| Production | 8080 (auth), 8081 (pdf-renderer), 8082 (text2image) |

## Remote database access

Remote developers reach PostgreSQL **without** exposing port 5432 on the firewall, by forwarding a local port over SSH.

```
Dev Machine → VPN → Office Network → SSH Tunnel → PostgreSQL (localhost on server)
```

1. **Connect to VPN** — establish a VPN connection to the office network
2. **Open SSH tunnel** — forward a local port (e.g. 5433) to the server's `localhost:5432`
3. **Connect to database** — point your app or tool at `localhost:5433`

Key points:

- PostgreSQL listens only on `localhost` — never publicly exposed
- SSH tunnel encrypts all traffic between the dev machine and the server
- Each database has its own dedicated PostgreSQL user
- Persistent tunnels can be configured via `~/.ssh/config` or `autossh`

> **Note:** Connection credentials, IPs, and VPN config details are stored separately — see internal documentation or ask the team lead.

## Documentation

- [PostgreSQL schema & operations](docs/postgresql.md) — self-hosted Postgres, API keys, network access, migrations, backups
- [SSH Tunnel Setup Guide](plans/completed/ssh-tunnel-postgresql-windows.md) — step-by-step SSH tunnel to PostgreSQL over VPN
- [EF Core + Flyway migration plan](plans/completed/ef-core-persistence-and-alembic.md) — persistence design decisions
- [Flyway CI/CD integration](plans/completed/flyway-migrations-ci-cd.md) — how Flyway fits into the pipelines
