# Northwind Logistics Breach - CTF Play Box

An academic Capture the Flag project for **IE3132 Penetration Testing, Assignments 01 and 02**. The scenario follows a fictional logistics company through six challenges covering information gathering, hidden data, web security, cryptography, network analysis and Linux security.

The project uses Docker Compose for the challenge environment and CTFd for challenge entries, flag submission and scoring. Use it only in an isolated, authorized lab.

## Current status

The project owner has reported completing all six stages in the local environment, with flags accepted and points displayed correctly on the CTFd leaderboard.

This is a **reported local test result**, not an automated test result or proof that a fresh clone includes the configured CTFd instance. The repository contains the challenge build files, but the local CTFd database and uploads are stored in Docker volumes.

Before submission, the team still needs to attach reproducible deployment and recovery evidence, preserve the CTFd configuration, and identify each member's contribution.

## Challenge overview

| Stage | Domain | Target difficulty required by Assignment 02 |
|---|---|---|
| 1 | OSINT / information gathering | Easy |
| 2 | Steganography | Easy |
| 3 | Web application security | Moderate |
| 4 | Cryptography | Moderate |
| 5 | Network traffic analysis | Moderate-Hard |
| 6 | Linux system security | Hard - capstone |

These are the required difficulty targets. They are not independently validated ratings; playtesting and the intended solution paths must support them.

Flags use the format `NW{...}`. Exact flags and solution details are omitted from this README. Challenge source files and Git history can still contain answers, so this repository should be treated as implementation material for the team and examiner, not a spoiler-free player resource.

## Requirements

- Docker Engine or Docker Desktop running Linux containers.
- Docker Compose v2 (`docker compose`).
- Git, a web browser and an SSH client.
- Internet access for the initial image downloads and build dependencies.
- Available local ports: 8000, 8081, 8083, 8085 and 2222.
- No conflicting Docker or host routes for `172.18.0.0/16` and `172.19.0.0/16`.

Record the actual OS, Docker version, CPU, RAM and observed resource usage in the team's testing evidence. A minimum hardware specification has not yet been measured.

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
| `VULN_MODE` | Stage 3 mode: `sqli` or `idor`. Use the team's selected mode consistently. |

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

These addresses refer to the machine running Docker. If Docker runs inside a VM, access the services from that VM or use the team's documented private access arrangement. The repository does not configure participant VPN access.

## CTFd configuration and persistence

The working local CTFd instance has been reported as configured. **A fresh clone does not restore that configuration automatically.**

On a new installation, complete CTFd setup and either restore a tested team export or configure the six challenges through the admin interface. Include each challenge's description, category, points, flag validation, hints and any intended prerequisites.

Compose uses named volumes for:

- `ctfd_db_data`: accounts, challenge configuration, submissions and scores in MariaDB.
- `ctfd_uploads`: uploaded challenge files.

These volumes are not Git-tracked files. A CTFd export/import package and tested restoration instructions still need to be included in the examiner's submission material. Keep exports containing account or answer data restricted to the appropriate recipients.

Validation evidence should cover correct and incorrect flag submissions, scoring, and any configured prerequisites.

## Architecture and isolation

| Component | Configuration in this repository |
|---|---|
| Challenge network | Internal Docker bridge, `172.18.0.0/16`; shared by all challenge services. |
| Platform network | Separate Docker bridge, `172.19.0.0/16`; used by CTFd, MariaDB and Redis. |
| Published services | Host ports bind to `127.0.0.1`. |
| Static challenge services | Read-only root filesystems, temporary writable mounts and an explicit capability set. |
| Stage 3 | Runs as a non-root application user and drops all Linux capabilities. |
| Stage 6 | Does not define `cap_drop`; explicitly sets `no-new-privileges:false` for its intentionally vulnerable lab behavior. |

These are configured controls, not a completed isolation test. Containers share the host kernel; use a dedicated lab VM and verify the actual network boundaries before the demonstration. The platform network is not configured as an internal network.

All challenge services currently share one network. Stage 6 is not on a separate internal tier. The earlier [network decision note](NOTE_network_decision.md) records the topology change, but its statement that Stage 6 has dropped capabilities does not match the current Compose file. Use the configuration above when describing the implemented environment.

The team must compare this implementation with the approved Assignment 01 design and explain any differences. Do not claim VPN access, separate Stage 6 segmentation or security controls that have not been implemented.

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

This is the proposed recovery procedure derived from the Compose configuration. The team must execute and record a before/after recovery test before claiming it is verified.

### Remove the stack while preserving CTFd data

```bash
docker compose down
docker compose up -d --build
```

Named volumes remain when `down` is used without `-v`. CTFd progress therefore remains. **Do not add `-v` unless you deliberately intend to delete the platform's database and uploads and have a tested backup.**

Rebuilding from changed source can change the challenge baseline. Use the same recorded commit when testing repeatable recovery.

## Testing evidence to complete

Record the date, tester, commit, expected outcome, actual outcome and evidence for each test.

- Fresh deployment using only the submitted files and instructions.
- Completion of all six intended challenge paths.
- Correct and incorrect flag validation, points and leaderboard behavior.
- Stage dependencies and hints, where configured.
- Checks for unintended shortcuts.
- Challenge reset and CTFd backup/restoration.
- Network isolation and published-port checks.
- Resource usage and defects found, fixed and retested.
- Difficulty review against the required progression.

Useful operational checks include:

```bash
docker compose ps
docker compose logs --tail=100
docker stats --no-stream
```

Logs may contain sensitive lab or account data. Review them before adding them to public evidence. These commands support operational checks; they do not replace functional and isolation testing.

## Assignment 02 submission checklist

The brief sets a deadline of **12 October 2026**. Submit one group package named `ITXXX_ITXXX_ITXXX_ITXXX`, replacing the placeholders with the four members' index numbers.

- [ ] One MP4 demonstration, no longer than 20 minutes, with all four members.
- [ ] Deployable project files and complete setup, run and verified reset instructions.
- [ ] CTFd configuration/export and tested restoration instructions.
- [ ] All self-developed challenge-generation, solver and automation source files.
- [ ] At least one relevant self-developed script per member.
- [ ] Genuine individual contribution evidence: commits, configurations and test logs.
- [ ] Test results, recovery evidence, risk outcomes and justified design changes.
- [ ] Acknowledgements of external tools, frameworks, datasets and images.

No written report is required for this stage. Follow the approved member allocation:

| Member | Responsibility |
|---|---|
| 1 | Platform, deployment, architecture, security controls and reset. |
| 2 | Challenge Design A: at least three stages. |
| 3 | Challenge Design B: at least three stages. |
| 4 | Integration, testing, recovery evidence and design changes. |

The video must show the real running environment. Each member must introduce themselves, identify their student ID and explain their own work. The brief prohibits AI assistance during the demonstration and AI-generated explanations presented as the member's own. Use your own knowledge and brief notes, and follow the brief's recording and editing rules.

## External components

The repository uses Docker/Compose, CTFd, MariaDB, Redis, Nginx, Python/Flask, Ubuntu and OpenSSH. Challenge preparation also uses tools such as ReportLab and Scapy; the existing project notes refer to ExifTool and steghide for validation.

This list is a starting inventory, not a complete attribution record. Before submission, add the actual sources and licenses for external challenge assets and references, and record the versions used. The current CTFd image uses the `latest` tag, so future builds may differ unless the team records and pins a tested version.

## Remaining work

- Add the tested CTFd export/restoration material.
- Record fresh-deployment, reset, isolation and difficulty evidence.
- Map each member to their actual files, scripts and contributions.
- Correct the outdated Stage 6 capability statement in the separate network note.
- Complete external asset acknowledgements and the final submission package.
