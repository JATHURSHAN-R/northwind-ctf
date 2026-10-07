# Northwind Logistics Breach - CTF Play Box

A Docker-based Capture the Flag lab. The scenario follows a fictional logistics company through six challenges covering information gathering, hidden data, web security, cryptography, network analysis and Linux security.

The project uses Docker Compose for the challenge environment and CTFd for challenge entries, flag submission and scoring. Use it only in an isolated, authorized lab.

## Challenge overview

| Stage | Domain | Target difficulty |
|---|---|---|
| 1 | OSINT / information gathering | Easy |
| 2 | Steganography | Easy |
| 3 | Web application security | Moderate |
| 4 | Cryptography | Moderate |
| 5 | Network traffic analysis | Moderate-Hard |
| 6 | Linux system security | Hard - capstone |

Difficulty labels describe the intended progression.

Flags use the format `NW{...}`. Exact flags and solution details are omitted from this README. Challenge source files and Git history can still contain answers, so this repository should be treated as implementation material for lab operators and may reveal challenge solutions.

## Requirements

- Docker Engine or Docker Desktop running Linux containers.
- Docker Compose v2 (`docker compose`).
- Git, a web browser and an SSH client.
- Internet access for the initial image downloads and build dependencies.
- Available local ports: 8000, 8081, 8083, 8085 and 2222.
- No conflicting Docker or host routes for `172.18.0.0/16` and `172.19.0.0/16`.

## Setup and run

Clone the project and create the local environment file:

```bash
git clone https://github.com/JATHURSHAN-R/northwind-ctf.git
cd northwind-ctf
cp .env.example .env
```

Edit `.env` before starting:

| Variable | Purpose |
|---|---|
| `CTFD_DB_PASSWORD` | CTFd database user's password; replace the example value. |
| `CTFD_DB_ROOT_PASSWORD` | MariaDB root password; replace the example value. |
| `FLASK_SECRET` | Set a long, random application secret. |
| `VULN_MODE` | Stage 3 mode: `sqli` or `idor`. Select the mode for your lab. |

Keep the real `.env` out of version control. Set database passwords before the first database initialization; editing them later does not automatically change users in an existing database volume.

Build and start the services:

```bash
docker compose up -d --build
docker compose ps
```

The database may take time to initialize. Container status alone does not prove that the application is ready. Check the browser and review service logs if startup is incomplete:

```bash
docker compose logs --tail=100 ctfd ctfd_db
```

| Service | Local address |
|---|---|
| CTFd | http://127.0.0.1:8000 |
| Stages 1-2 | http://127.0.0.1:8081 |
| Stage 3 | http://127.0.0.1:8083 |
| Stages 4-5 | http://127.0.0.1:8085 |
| Stage 6 SSH service | Host `127.0.0.1`, port `2222` |

These addresses refer to the machine running Docker. If Docker runs inside a VM, access the services from that VM or use a private access arrangement. The repository does not configure participant VPN access.

## CTFd configuration and persistence

CTFd configuration is stored separately from the source code. A fresh clone starts without existing challenge entries, accounts or scores.

On a new installation, complete CTFd setup and either restore an existing CTFd export or configure the six challenges through the admin interface. Include each challenge's description, category, points, flag validation, hints and any intended prerequisites.

Compose uses named volumes for:

- `ctfd_db_data`: accounts, challenge configuration, submissions and scores in MariaDB.
- `ctfd_uploads`: uploaded challenge files.

These volumes are not Git-tracked files. Back up the database and uploaded files before migrating or deleting the installation. Keep exports containing account or answer data private.

## Architecture and isolation

| Component | Configuration in this repository |
|---|---|
| Challenge network | Internal Docker bridge, `172.18.0.0/16`; shared by all challenge services. |
| Platform network | Separate Docker bridge, `172.19.0.0/16`; used by CTFd, MariaDB and Redis. |
| Published services | Host ports bind to `127.0.0.1`. |
| Static challenge services | Read-only root filesystems, temporary writable mounts and an explicit capability set. |
| Stage 3 | Runs as a non-root application user and drops all Linux capabilities. |
| Stage 6 | Does not define `cap_drop`; explicitly sets `no-new-privileges:false` for its intentionally vulnerable lab behavior. |

Containers share the host kernel. Run the lab in a dedicated VM and keep its services off public networks. The platform network is not configured as an internal network.

All challenge services share one network; Stage 6 is not on a separate network tier. The table above reflects the current configuration in `docker-compose.yml`.

## Stop, restart and recovery

### Stop and start without clearing progress

```bash
docker compose stop
docker compose start
```

This preserves containers and their state. It is not a challenge reset.

### Recreate challenge containers

The challenge services have no named persistent data volumes in the current Compose file. Recreating them replaces their writable container state with the state defined by their images:

```bash
docker compose up -d --build --force-recreate --no-deps stage1-2-evidence stage3-portal stage4-5-files stage6-staging
```

This affects all challenge services and disconnects active challenge sessions. It preserves CTFd's database and uploads, including existing solves and scores. Resetting participant progress is a separate platform operation.

This recreation procedure is derived from the Compose configuration; it has not been independently verified.

### Remove the stack while preserving CTFd data

```bash
docker compose down
docker compose up -d --build
```

Named volumes remain when `down` is used without `-v`. CTFd progress therefore remains. **Do not add `-v` unless you deliberately intend to delete the platform's database and uploads and have a tested backup.**

Rebuilding from changed source can change the challenge baseline. Use the same recorded commit when testing repeatable recovery.

## Monitoring

Useful operational checks include:

```bash
docker compose ps
docker compose logs --tail=100
docker stats --no-stream
```

Review logs for sensitive lab or account data before sharing them.

## External components

The repository uses Docker/Compose, CTFd, MariaDB, Redis, Nginx, Python/Flask, Ubuntu and OpenSSH. Challenge preparation also uses tools such as ReportLab and Scapy; the existing project notes refer to ExifTool and steghide for validation.

The current CTFd image uses the `latest` tag. For repeatable deployments, pin a tested image version or digest.
