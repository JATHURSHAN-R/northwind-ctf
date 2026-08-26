FROM nginx:1.27-alpine

# Static evidence server for Stage 1 (OSINT) and Stage 2 (Steganography).
# No server-side code, no database -- minimal attack surface beyond the
# intended clues, per the stage specs.

COPY site/ /usr/share/nginx/html/

# Nginx runs as non-root inside this image by default on the alpine variant's
# unprivileged config; keep read_only + cap_drop at the compose level too.
EXPOSE 80
