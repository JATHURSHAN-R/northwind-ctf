# Northwind Logistics Breach — CTF Play Box

Implementation build for IE3132 Assignment 01/02. Matches the approved
design in `CTF_Play_Box_Report.docx` (theme, stage specs, architecture).
See `NOTE_network_decision.md` for one deliberate deviation from that
diagram, made during implementation.

## Quick start

```bash
cp .env.example .env    # edit passwords/VULN_MODE first
docker compose up --build
```

| Service | URL / connection |
|---|---|
| CTFd (control layer) | http://localhost:8000 |
| Stage 1–2 (OSINT + Stego) | http://localhost:8081 |
| Stage 3 (Web) | http://localhost:8083 |
| Stage 4–5 (Crypto + Networking files) | http://localhost:8085 |
| Stage 6 (Linux capstone) | `ssh ravi_svc@localhost -p 2222` |

**CTFd itself still needs its challenges configured** through its setup
wizard and admin panel (upload each flag, wire up hints) — this build
gives you the six working challenge boxes, not the CTFd challenge
entries yet.

## Build/test status

| Stage | Status |
|---|---|
| 1 — OSINT | Built & verified — flag confirmed readable via `exiftool` on the resume PDF |
| 2 — Steganography | Built & verified — `steghide` round-trip tested (correct passphrase extracts, wrong one fails) |
| 3 — Web | Built & verified — both `VULN_MODE=sqli` and `VULN_MODE=idor` tested end-to-end; confirmed only the selected mode is exploitable |
| 4 — Cryptography | Built & verified — Vigenère cipher round-trip confirmed correct |
| 5 — Networking | Built & verified — pcap reassembly tested; the exact file Stage 6 needs extracts cleanly via a scripted "Follow TCP Stream" equivalent |
| 6 — Linux | Built & verified — the SUID `find` privesc technique was tested end-to-end against a real low-privilege user before being baked into the image |
| Full `docker compose up` | **Not yet run** — this build environment has no Docker daemon. Everything above was verified with the underlying tools directly (steghide, exiftool, Flask dev server, Scapy). Run a real `docker compose up --build` on your own machine before trusting this for the live event, per the project's own testing plan. |

## Picking Stage 3's vulnerability mode

Set in `.env`:
```
VULN_MODE=sqli   # SQL injection login bypass (username: ' OR '1'='1' -- )
VULN_MODE=idor   # IDOR — log in as 'test'/'test123', view /message/1 directly
```

## Flags (for your own answer key — don't publish this file)

| Stage | Flag |
|---|---|
| 1 | `NW{m3tadata_n3v3r_l1es}` |
| 2 | `NW{ch4ndu_kn3w_t00_much}` |
| 3 | `NW{4uth_1s_h4rd3r_th4n_1t_l00ks}` |
| 4 | `NW{legacy_ciphers_die_hard}` |
| 5 | 'NW{cleartext_exfiltration_detected}'|
| 6 | `NW{suid_find_is_forever}` |


## Known gaps / next steps

- CTFd challenges, hints, and point values aren't configured yet —
  that's manual setup through the CTFd admin UI (or scriptable via its
  API if you want that automated later).
- Stage 6's container isn't capability-restricted like the others (see
  the comment in `docker-compose.yml`) — sshd needs a broad capability
  set to manage PAM/pty/user-switching correctly, and getting a minimal
  set wrong would silently break login rather than fail loudly. Worth a
  careful hardening pass once you can test against a real container.
- WireGuard/OpenVPN participant access (from the design doc) isn't
  wired up — right now everything's reachable on `localhost` ports for
  local development. Needed before a real multi-team event.
- No automated `docker compose up` test has been run (no Docker in this
  build environment) — do this first before anything else.
