from scapy.all import Ether, IP, TCP, UDP, DNS, DNSQR, DNSRR, wrpcap
import time

RAVI_IP = "10.50.30.15"
RAVI_MAC = "02:11:22:33:44:55"
GW_MAC = "02:aa:bb:cc:dd:ee"
DROP_SERVER_IP = "203.0.113.77"
INTERNAL_MONITOR_IP = "10.50.30.1"
DNS_SERVER_IP = "10.50.30.2"

packets = []
t = time.time()

def eth_ip(src, dst, mac_src=RAVI_MAC, mac_dst=GW_MAC):
    return Ether(src=mac_src, dst=mac_dst) / IP(src=src, dst=dst)

dns_q = eth_ip(RAVI_IP, DNS_SERVER_IP) / UDP(sport=51000, dport=53) / \
    DNS(rd=1, qd=DNSQR(qname="updates.northwindlogistics.internal"))
packets.append(dns_q)
dns_r = eth_ip(DNS_SERVER_IP, RAVI_IP, mac_src=GW_MAC, mac_dst=RAVI_MAC) / \
    UDP(sport=53, dport=51000) / \
    DNS(id=dns_q[DNS].id, qr=1, qd=dns_q[DNS].qd,
        an=DNSRR(rrname="updates.northwindlogistics.internal", rdata="10.50.30.9"))
packets.append(dns_r)

seq_c, seq_s = 100, 900
hc = eth_ip(RAVI_IP, INTERNAL_MONITOR_IP)
packets.append(hc / TCP(sport=52000, dport=443, flags="S", seq=seq_c))
packets.append(eth_ip(INTERNAL_MONITOR_IP, RAVI_IP, mac_src=GW_MAC, mac_dst=RAVI_MAC) /
               TCP(sport=443, dport=52000, flags="SA", seq=seq_s, ack=seq_c+1))
packets.append(hc / TCP(sport=52000, dport=443, flags="A", seq=seq_c+1, ack=seq_s+1))
packets.append(hc / TCP(sport=52000, dport=443, flags="FA", seq=seq_c+1, ack=seq_s+1))
packets.append(eth_ip(INTERNAL_MONITOR_IP, RAVI_IP, mac_src=GW_MAC, mac_dst=RAVI_MAC) /
               TCP(sport=443, dport=52000, flags="A", seq=seq_s+1, ack=seq_c+2))

with open("backup_export.txt", "rb") as f:
    file_bytes = f.read()

http_request = (
    b"GET /backup_export.txt HTTP/1.1\r\n"
    b"Host: 203.0.113.77\r\n"
    b"User-Agent: curl/8.5.0\r\n"
    b"Accept: */*\r\n"
    b"Connection: close\r\n\r\n"
)
http_response = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: text/plain\r\n"
    b"Content-Length: " + str(len(file_bytes)).encode() + b"\r\n"
    b"Connection: close\r\n\r\n" + file_bytes
)

CSPORT = 54321
c_seq, s_seq = 1000, 5000
client = eth_ip(RAVI_IP, DROP_SERVER_IP)
server = eth_ip(DROP_SERVER_IP, RAVI_IP, mac_src=GW_MAC, mac_dst=RAVI_MAC)

packets.append(client / TCP(sport=CSPORT, dport=80, flags="S", seq=c_seq))
packets.append(server / TCP(sport=80, dport=CSPORT, flags="SA", seq=s_seq, ack=c_seq+1))
c_seq += 1
packets.append(client / TCP(sport=CSPORT, dport=80, flags="A", seq=c_seq, ack=s_seq+1))
packets.append(client / TCP(sport=CSPORT, dport=80, flags="PA", seq=c_seq, ack=s_seq+1) / http_request)
s_seq += 1
packets.append(server / TCP(sport=80, dport=CSPORT, flags="A", seq=s_seq, ack=c_seq+len(http_request)))
c_seq += len(http_request)

mid = len(http_response) // 2
chunk1, chunk2 = http_response[:mid], http_response[mid:]
packets.append(server / TCP(sport=80, dport=CSPORT, flags="PA", seq=s_seq, ack=c_seq) / chunk1)
packets.append(client / TCP(sport=CSPORT, dport=80, flags="A", seq=c_seq, ack=s_seq+len(chunk1)))
packets.append(server / TCP(sport=80, dport=CSPORT, flags="PA", seq=s_seq+len(chunk1), ack=c_seq) / chunk2)
s_seq += len(http_response)
packets.append(client / TCP(sport=CSPORT, dport=80, flags="A", seq=c_seq, ack=s_seq))
packets.append(server / TCP(sport=80, dport=CSPORT, flags="FA", seq=s_seq, ack=c_seq))
packets.append(client / TCP(sport=CSPORT, dport=80, flags="A", seq=c_seq, ack=s_seq+1))
packets.append(client / TCP(sport=CSPORT, dport=80, flags="FA", seq=c_seq, ack=s_seq+1))
packets.append(server / TCP(sport=80, dport=CSPORT, flags="A", seq=s_seq+1, ack=c_seq+1))

for i, pkt in enumerate(packets):
    pkt.time = t + i * 0.03

wrpcap("capture.pcap", packets)
print(f"Done — {len(packets)} packets written.")
