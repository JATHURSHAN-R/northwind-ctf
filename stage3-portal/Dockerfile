FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/

# Runs as a non-root user -- the app only needs to write its own sqlite
# file under /tmp, which stays writable even with cap_drop: ALL at the
# compose level (no privileged syscalls needed for a normal Flask app).
RUN useradd -m appuser
USER appuser

# Which single vulnerability is live: "sqli" or "idor" -- set in
# docker-compose.yml or an .env file. Defaults to sqli if unset.
ENV VULN_MODE=sqli
# FLASK_SECRET is supplied at runtime through Compose.

EXPOSE 5000
CMD ["python3", "app.py"]
