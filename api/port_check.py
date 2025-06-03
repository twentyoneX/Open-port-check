# vercel-port-checker/api/port_check.py

import socket
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# List of ports to check
PORTS_TO_CHECK = [
    21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 465, 587, 993, 995,
    1194, 1701, 1723, 3306, 3389, 5060, 5061, 5222, 5555, 8080
]
SCAN_TIMEOUT = 0.7  # Seconds per port - adjust as needed

def check_port(ip_address, port, timeout):
    try:
        # Create a new socket for each attempt
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        # connect_ex returns an error indicator
        result = s.connect_ex((ip_address, port))
        s.close()
        return result == 0  # 0 means connection was successful
    except socket.error as e:
        # print(f"Socket error for {ip_address}:{port} - {e}") # For debugging
        return False
    except Exception as e:
        # print(f"Generic error for {ip_address}:{port} - {e}") # For debugging
        return False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Get client IP. Vercel sets 'x-forwarded-for'.
        # The first IP in the list is usually the original client IP.
        forwarded_for = self.headers.get('x-forwarded-for')
        client_ip = None
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
        
        # Fallback if x-forwarded-for is not present (less common on Vercel)
        if not client_ip:
            client_ip = self.client_address[0]

        if not client_ip:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # Allow all origins for simplicity
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Could not determine client IP."}).encode('utf-8'))
            return

        scan_results = {}
        for port in PORTS_TO_CHECK:
            is_open = check_port(client_ip, port, SCAN_TIMEOUT)
            scan_results[str(port)] = "Open" if is_open else "Closed"

        response_data = {
            "client_ip": client_ip,
            "ports": scan_results
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        # Allow requests from any origin (Blogspot, local testing, etc.)
        # For production, you might want to restrict this to your Blogspot domain
        # or the domain where the frontend is hosted if it's not Blogspot.
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return
