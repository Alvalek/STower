#!/usr/bin/env python3
"""
STower - Signal Tower
A high-performance, network reconnaissance tool.
Author: Alvalek
Version: 1.0.0
Description: Multi-threaded port scanner with banner grabbing and JSON export.
"""

import socket
import threading
from datetime import datetime
import argparse
import sys
from tqdm import tqdm 

class STower:
    """
    STower: Signal Tower - Network Reconnaissance Engine
    """
    def __init__(self, target, start_port=1, end_port=1024):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.open_ports = []
        self.results = []
        self.threads = []
        
    def scan_port(self, port):
        """Scan a single port with banner grabbing."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            
            result = sock.connect_ex((self.target, port))
            
            service_name = "Unknown"
            banner = None
            
            if result == 0:
                
                try:
                    sock.send(b'GET / HTTP/1.0\r\n\r\n')
                    banner_data = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    if banner_data:
                        banner = banner_data.split('\r\n')[0] 
                        if "Apache" in banner: service_name = "Apache"
                        elif "nginx" in banner: service_name = "nginx"
                        elif "Microsoft-IIS" in banner: service_name = "IIS"
                        elif "SSH" in banner: service_name = "SSH"
                except:
                    pass 
                
                self.open_ports.append(port)
                
                
                self.results.append({
                    "port": port,
                    "state": "OPEN",
                    "service": service_name,
                    "banner": banner
                })
                
                print(f"[+] Port {port}: OPEN ({service_name})")
                if banner:
                    print(f"    └─ Banner: {banner[:50]}...")
            else:
                
                pass
                
            sock.close()
            
        except socket.error:
            pass
        except Exception:
            pass
    
    def scan(self, num_threads=50):
        """Scan with progress bar and threading."""
        print(f"\n Target: {self.target}")
        print(f"Range: {self.start_port} - {self.end_port}")
        print(f"Threads: {num_threads}\n")
        
        total_ports = self.end_port - self.start_port + 1
        
        with tqdm(total=total_ports, desc="Scanning", unit="port", colour="green") as pbar:
            for port in range(self.start_port, self.end_port + 1):
                t = threading.Thread(target=self.scan_port, args=(port,))
                self.threads.append(t)
                t.start()
                
                
                if len(self.threads) >= num_threads:
                    for thread in self.threads[:num_threads]:
                        thread.join()
                    self.threads = self.threads[num_threads:]
                
                pbar.update(1) 
            
            
            for thread in self.threads:
                thread.join()
                pbar.update(1) 

        self._print_summary()

    def _print_summary(self):
        print("\n" + "="*60)
        print(f"SCAN COMPLETE")
        print(f"Open Ports Found: {len(self.open_ports)}")
        if self.open_ports:
            print(f"Ports: {self.open_ports}")
        print("="*60 + "\n")

    def export_results(self, filename, format_type="json"):
        """NEW: Export results to JSON or CSV."""
        try:
            if format_type == "json":
                with open(filename, 'w') as f:
                    json.dump(self.results, f, indent=4)
                print(f"Results saved to: {filename}")
            elif format_type == "csv":
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=["port", "state", "service", "banner"])
                    writer.writeheader()
                    writer.writerows(self.results)
                print(f"Results saved to: {filename}")
        except Exception as e:
            print(f"Error saving file: {e}")
    
    def get_service_info(self, port):
        
        services = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            443: "HTTPS",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL"
        }
        return services.get(port, "Unknown")

def grab_banner(self, port):
    """Extract service banner from open port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((self.target, port))
        sock.send(b'GET / HTTP/1.0\r\n\r\n')
        banner = sock.recv(1024).decode('utf-8', errors='ignore')
        sock.close()
        return banner.strip()
    except:
        return None

def banner():
    logo = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄   ║
    ║   █  S T O W E R  -  S I G N A L  T O W E R  █   ║
    ║   █  NETWORK RECONNAISSANCE ENGINE v1.0.0    █   ║
    ║   ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀   ║
    ║                                                       ║
    ║   [!] ETHICAL NOTE: Scan only authorized targets ║
    ║   [!] WARNING: Unauthorized access is a violation of the law  ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    print(logo)
    print(f"Initialized at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)



def main():
    banner()
    
    parser = argparse.ArgumentParser(prog="STower", description="STower: High-performance network reconnaissance.")
    parser.add_argument("-t", "--target", required=True, help="Target IP or Hostname")
    parser.add_argument("-p", "--ports", default="1-1024", help="Port range (e.g., 1-1024)")
    parser.add_argument("-T", "--threads", type=int, default=50, help="Thread count")
    parser.add_argument("-o", "--output", help="Output file (e.g., results.json)")
    parser.add_argument("-f", "--format", choices=["json", "csv"], default="json", help="Output format")
    
    args = parser.parse_args()
    
    try:
        if "-" in args.ports:
            start, end = map(int, args.ports.split("-"))
        else:
            start = end = int(args.ports)
    except ValueError:
        print("❌ Invalid port range."); sys.exit(1)
        
    if start < 1 or end > 65535:
        print("❌ Ports must be 1-65535"); sys.exit(1)
        
    scanner = STower(args.target, start, end)
    scanner.scan(num_threads=args.threads)
    
    if args.output:
        scanner.export_results(args.output, args.format)

if __name__ == "__main__":
    main()
