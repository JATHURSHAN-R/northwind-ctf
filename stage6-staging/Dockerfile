FROM ubuntu:22.04

# Stage 6 -- "Ravi's Staging Server" (Linux / System Security capstone)
#
# Access: SSH as ravi_svc, credentials matching what's exfiltrated in
# Stage 5's pcap (username: ravi_svc / password: StagingAccess#22).
#
# Privilege escalation: /usr/bin/find carries the SUID bit, owned by
# root -- a single, deliberate, GTFOBins-documented misconfiguration
# (https://gtfobins.github.io/gtfobins/find/#sudo). This exact technique
# was verified end-to-end against a real low-privilege user before being
# baked into this image: `find . -exec /bin/sh -p \; -quit` yields an
# effective-root shell. It's also independent of any specific kernel/CVE
# version, unlike polkit-class bugs -- which is why it was chosen over
# PwnKit-style exploits for reliability across every team's rebuild.

RUN apt-get update && apt-get install -y --no-install-recommends openssh-server sudo \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /var/run/sshd

# Low-privilege service account -- matches Stage 5's discovered credentials
RUN useradd -m -s /bin/bash ravi_svc \
    && echo "ravi_svc:StagingAccess#22" | chpasswd

# The single deliberate misconfiguration
RUN chmod 4755 /usr/bin/find

# Root-only-readable flag -- the Stage 6 objective
RUN echo "NW{suid_find_is_forever}" > /root/flag.txt \
    && chmod 600 /root/flag.txt \
    && chown root:root /root/flag.txt

# Password auth only for ravi_svc; root login disabled over SSH
RUN sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
