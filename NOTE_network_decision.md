# Implementation note: network topology simplification

The Assignment 1 diagram showed Stage 6 on a strictly firewalled
"internal segment" reachable only *from* the challenge-hosts segment,
implying a pivot step. But Stage 6's actual spec never asked players to
pivot — it just says "log in via SSH with the credentials from Stage 5."

Rather than silently drift from the approved design, here's the concrete
resolution used in this build: all challenge hosts (Stages 1-6) sit on
one `challenge_net` that the player VPN endpoint can reach directly —
this matches what the stage specs actually ask players to do. The
"internal segment" idea from the diagram is kept alive in spirit by
giving Stage 6 a stricter per-container security profile (no exposed
ports except SSH, dropped capabilities, no egress) rather than a
separate unreachable network tier.

If your group wants *true* pivoting as a stretch feature (more faithful
to the original diagram, more advanced for players), that's a clean
add-on later: put Stage 6 on its own `internal_net`, and require players
to route through a chisel/SSH tunnel from the Stage 3 portal container.
Flagging this now so it's a deliberate choice, not a silent change.
