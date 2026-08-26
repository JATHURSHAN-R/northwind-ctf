FROM nginx:1.27-alpine

# Static file server for Stage 4 (Cryptography) and Stage 5 (Networking).
# No server-side code -- the ciphertext, log note, and pcap are the
# entire challenge surface, matching the stage specs.

COPY content/ /usr/share/nginx/html/
EXPOSE 80
