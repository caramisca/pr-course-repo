"""
HTTP File Server - Lab 2 (Multithreaded with Request Counter and Rate Limiting)
A multithreaded HTTP server that serves HTML, PNG, and PDF files from a specified directory.
Features:
- Thread pool for handling concurrent connections
- Request counter (with race condition demo and fix)
- Rate limiting by client IP (thread-safe)
"""

import socket
import sys
import os
from urllib.parse import unquote
from datetime import datetime
import threading
import time
from collections import defaultdict
from threading import Lock


class RequestCounter:
    """Thread-safe request counter for tracking file access"""
    
    def __init__(self, use_lock=True):
        """
        Initialize request counter
        
        Args:
            use_lock: If True, use lock for thread-safety. If False, demonstrate race condition.
        """
        self.counts = defaultdict(int)
        self.use_lock = use_lock
        self.lock = Lock() if use_lock else None
    
    def increment(self, path, delay=0):
        """
        Increment counter for a given path
        
        Args:
            path: File/directory path
            delay: Artificial delay to force race condition (for demo)
        """
        if self.use_lock:
            with self.lock:
                current = self.counts[path]
                if delay > 0:
                    time.sleep(delay)  # Simulate work
                self.counts[path] = current + 1
        else:
            # Naive implementation - prone to race conditions
            current = self.counts[path]
            if delay > 0:
                time.sleep(delay)  # Force interleaving
            self.counts[path] = current + 1
    
    def get_count(self, path):
        """Get current count for a path"""
        if self.use_lock:
            with self.lock:
                return self.counts[path]
        else:
            return self.counts[path]
    
    def get_all_counts(self):
        """Get all counts (returns a copy)"""
        if self.use_lock:
            with self.lock:
                return dict(self.counts)
        else:
            return dict(self.counts)


class RateLimiter:
    """Thread-safe rate limiter based on client IP"""
    
    def __init__(self, requests_per_second=5):
        """
        Initialize rate limiter
        
        Args:
            requests_per_second: Maximum requests allowed per second per IP
        """
        self.requests_per_second = requests_per_second
        self.lock = Lock()
        # Track request timestamps for each IP
        self.request_times = defaultdict(list)
    
    def is_allowed(self, client_ip):
        """
        Check if request from client IP is allowed based on rate limit
        
        Args:
            client_ip: Client IP address
            
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        with self.lock:
            current_time = time.time()
            
            # Remove timestamps older than 1 second
            self.request_times[client_ip] = [
                t for t in self.request_times[client_ip]
                if current_time - t < 1.0
            ]
            
            # Check if we're under the rate limit
            if len(self.request_times[client_ip]) < self.requests_per_second:
                self.request_times[client_ip].append(current_time)
                return True
            else:
                return False
    
    def get_stats(self, client_ip):
        """Get current request count for an IP in the last second"""
        with self.lock:
            current_time = time.time()
            recent_requests = [
                t for t in self.request_times[client_ip]
                if current_time - t < 1.0
            ]
            return len(recent_requests)


class HTTPServer:
    """Multithreaded HTTP/1.1 File Server"""
    
    MIME_TYPES = {
        '.html': 'text/html',
        '.htm': 'text/html',
        '.png': 'image/png',
        '.pdf': 'application/pdf',
    }
    
    def __init__(self, host='0.0.0.0', port=8080, directory='.', 
                 max_workers=10, use_lock=True, enable_rate_limit=True,
                 rate_limit_rps=10, request_delay=0):
        """
        Initialize the HTTP server
        
        Args:
            host: Host address to bind to
            port: Port number to listen on
            directory: Root directory to serve files from
            max_workers: Maximum number of worker threads
            use_lock: If True, use locks for thread-safety (else demonstrate race conditions)
            enable_rate_limit: Enable rate limiting feature
            rate_limit_rps: Requests per second limit per IP
            request_delay: Artificial delay per request (for testing)
        """
        self.host = host
        self.port = port
        self.directory = os.path.abspath(directory)
        self.server_socket = None
        self.max_workers = max_workers
        self.request_delay = request_delay
        
        # Request counter
        self.counter = RequestCounter(use_lock=use_lock)
        
        # Rate limiter
        self.enable_rate_limit = enable_rate_limit
        self.rate_limiter = RateLimiter(requests_per_second=rate_limit_rps) if enable_rate_limit else None
        
        if not os.path.exists(self.directory):
            raise ValueError(f"Directory '{self.directory}' does not exist")
        
        print(f"[INFO] Server initialized")
        print(f"[INFO] Serving directory: {self.directory}")
        print(f"[INFO] Thread pool size: {self.max_workers}")
        print(f"[INFO] Thread-safe locks: {'ENABLED' if use_lock else 'DISABLED (DEMO MODE)'}")
        print(f"[INFO] Rate limiting: {'ENABLED' if enable_rate_limit else 'DISABLED'} ({rate_limit_rps} req/s per IP)")
        if request_delay > 0:
            print(f"[INFO] Artificial delay: {request_delay}s per request (for testing)")
    
    def start(self):
        """Start the HTTP server and listen for connections"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        print(f"[INFO] Server listening on {self.host}:{self.port}")
        print(f"[INFO] Press Ctrl+C to stop the server\n")
        
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                
                # Create a new thread to handle this request
                thread = threading.Thread(
                    target=self.handle_request,
                    args=(client_socket, client_address),
                    daemon=True
                )
                thread.start()
                
        except KeyboardInterrupt:
            print("\n[INFO] Server shutting down...")
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def handle_request(self, client_socket, client_address):
        """
        Handle a single HTTP request in a separate thread
        
        Args:
            client_socket: Socket connected to the client
            client_address: Tuple containing client IP and port
        """
        client_ip = client_address[0]
        thread_id = threading.current_thread().name
        
        try:
            print(f"[CONNECTION] Thread {thread_id}: New connection from {client_ip}:{client_address[1]}")
            
            # Check rate limit
            if self.enable_rate_limit and not self.rate_limiter.is_allowed(client_ip):
                print(f"[RATE_LIMIT] Thread {thread_id}: Blocked {client_ip} - rate limit exceeded")
                self.send_error(client_socket, 429, "Too Many Requests")
                return
            
            # Artificial delay for testing concurrent requests
            if self.request_delay > 0:
                time.sleep(self.request_delay)
            
            # Receive the request
            request_data = client_socket.recv(4096).decode('utf-8')
            
            if not request_data:
                return
            
            # Parse the request
            lines = request_data.split('\r\n')
            request_line = lines[0]
            print(f"[REQUEST] Thread {thread_id}: {request_line}")
            
            # Parse the request line
            parts = request_line.split()
            if len(parts) < 2:
                self.send_error(client_socket, 400, "Bad Request")
                return
            
            method = parts[0]
            path = unquote(parts[1])  # Decode URL encoding
            
            # Only support GET requests
            if method != 'GET':
                self.send_error(client_socket, 405, "Method Not Allowed")
                return
            
            # Serve the requested resource
            self.serve_path(client_socket, path, thread_id)
            
        except Exception as e:
            print(f"[ERROR] Thread {thread_id}: Error handling request: {e}")
            try:
                self.send_error(client_socket, 500, "Internal Server Error")
            except:
                pass
        finally:
            client_socket.close()
    
    def serve_path(self, client_socket, path, thread_id):
        """
        Serve a file or directory listing
        
        Args:
            client_socket: Socket connected to the client
            path: Requested path (relative to root directory)
            thread_id: Thread identifier for logging
        """
        # Remove leading slash and resolve path
        if path.startswith('/'):
            path = path[1:]
        
        # Remove trailing slash for directories (but keep track for later)
        if path.endswith('/') and path != '':
            path = path[:-1]
        
        # Construct full file path
        full_path = os.path.normpath(os.path.join(self.directory, path))
        
        # Security check: prevent directory traversal
        if not full_path.startswith(self.directory):
            self.send_error(client_socket, 403, "Forbidden")
            return
        
        # Check if path exists
        if not os.path.exists(full_path):
            # Special case: if path is empty and doesn't exist, try index.html
            if path == '':
                path = 'index.html'
                full_path = os.path.normpath(os.path.join(self.directory, path))
                if not os.path.exists(full_path):
                    self.send_error(client_socket, 404, "Not Found")
                    return
            else:
                self.send_error(client_socket, 404, "Not Found")
                return
        
        # Increment request counter for this path (normalized without trailing slash)
        # Use small delay for race condition demo if locks disabled
        delay = 0.001 if not self.counter.use_lock else 0
        self.counter.increment(path, delay=delay)
        
        # If it's a directory, serve directory listing
        if os.path.isdir(full_path):
            self.serve_directory_listing(client_socket, full_path, path, thread_id)
            return
        
        # If it's a file, serve the file
        self.serve_file(client_socket, full_path, thread_id)
    
    def serve_file(self, client_socket, file_path, thread_id):
        """
        Serve a file to the client
        
        Args:
            client_socket: Socket connected to the client
            file_path: Full path to the file to serve
            thread_id: Thread identifier for logging
        """
        # Get file extension and MIME type
        _, ext = os.path.splitext(file_path)
        content_type = self.MIME_TYPES.get(ext.lower())
        
        if content_type is None:
            self.send_error(client_socket, 415, "Unsupported Media Type")
            return
        
        try:
            # Read file content
            if content_type.startswith('text'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                body = content.encode('utf-8')
            else:
                with open(file_path, 'rb') as f:
                    body = f.read()
            
            # Send response
            self.send_response(client_socket, 200, "OK", content_type, body)
            print(f"[RESPONSE] Thread {thread_id}: 200 OK - Served file: {os.path.basename(file_path)} ({len(body)} bytes)")
            
        except Exception as e:
            print(f"[ERROR] Thread {thread_id}: Error reading file: {e}")
            self.send_error(client_socket, 500, "Internal Server Error")
    
    def serve_directory_listing(self, client_socket, dir_path, url_path, thread_id):
        """
        Generate and serve a directory listing page with request counts
        
        Args:
            client_socket: Socket connected to the client
            dir_path: Full path to the directory
            url_path: URL path (for generating links)
            thread_id: Thread identifier for logging
        """
        try:
            # Get directory contents
            entries = os.listdir(dir_path)
            entries.sort()
            
            # Separate directories and files
            dirs = [e for e in entries if os.path.isdir(os.path.join(dir_path, e))]
            files = [e for e in entries if os.path.isfile(os.path.join(dir_path, e))]
            
            # Get all request counts
            all_counts = self.counter.get_all_counts()
            
            # Generate HTML with hacker-style design
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>/{url_path if url_path else 'root'}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', 'Monaco', monospace;
            background: #000000;
            color: #0f0;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .terminal {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            border: 2px solid #0f0;
            padding: 15px;
            margin-bottom: 20px;
            background: #001100;
            box-shadow: 0 0 10px #0f0;
        }}
        
        .prompt {{
            color: #0f0;
            font-weight: bold;
            font-size: 18px;
            text-shadow: 0 0 5px #0f0;
        }}
        
        .path {{
            color: #00ff00;
            font-weight: bold;
            margin-left: 10px;
        }}
        
        .command {{
            margin-top: 10px;
            color: #0f0;
        }}
        
        .parent {{
            margin-bottom: 15px;
            padding: 10px;
            border-left: 3px solid #0f0;
            background: #001100;
        }}
        
        .parent a {{
            color: #00ff00;
            text-decoration: none;
            font-weight: bold;
            text-shadow: 0 0 3px #0f0;
        }}
        
        .parent a:hover {{
            color: #00ff00;
            text-shadow: 0 0 8px #0f0;
        }}
        
        .listing {{
            border: 2px solid #0f0;
            background: #000;
            box-shadow: 0 0 15px #0f0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: #003300;
            color: #00ff00;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            border-bottom: 2px solid #0f0;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-size: 14px;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #003300;
        }}
        
        tr:hover {{
            background: #002200;
            box-shadow: inset 0 0 10px #0f0;
        }}
        
        a {{
            color: #0f0;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.2s;
            text-shadow: 0 0 2px #0f0;
        }}
        
        a:hover {{
            color: #00ff00;
            text-shadow: 0 0 10px #0f0, 0 0 20px #0f0;
            letter-spacing: 1px;
        }}
        
        .dir {{
            font-weight: bold;
        }}
        
        .dir::before {{
            content: "[DIR] ";
            color: #00ff00;
            font-weight: bold;
        }}
        
        .file::before {{
            content: "[FILE] ";
            color: #0f0;
        }}
        
        .hits {{
            color: #00ff00;
            font-weight: bold;
            text-align: right;
            font-family: 'Courier New', monospace;
            text-shadow: 0 0 3px #0f0;
        }}
        
        .hits::before {{
            content: "► ";
        }}
        
        .footer {{
            margin-top: 20px;
            padding: 15px;
            border: 2px solid #0f0;
            background: #001100;
            text-align: center;
            color: #0f0;
            font-size: 12px;
            box-shadow: 0 0 10px #0f0;
        }}
        
        .blink {{
            animation: blink 1s infinite;
        }}
        
        @keyframes blink {{
            0%, 50% {{ opacity: 1; }}
            51%, 100% {{ opacity: 0; }}
        }}
        
        .scan {{
            animation: scan 2s infinite;
            background: linear-gradient(transparent 0%, #0f0 50%, transparent 100%);
            height: 2px;
            width: 100%;
            position: fixed;
            top: 0;
            left: 0;
            opacity: 0.1;
        }}
    </style>
</head>
<body>
    <div class="scan"></div>
    <div class="terminal">
        <div class="header">
            <div class="prompt">root@http-server:<span class="path">/{url_path if url_path else '~'}</span><span class="blink">▊</span></div>
            <div class="command">$ ls -lah</div>
        </div>
"""
            
            # Add parent directory link if not at root
            if url_path and url_path != '':
                parent_path = '/'.join(url_path.split('/')[:-1])
                if parent_path:
                    parent_path = '/' + parent_path
                else:
                    parent_path = '/'
                html += f'        <div class="parent"><a href="{parent_path}">◄ cd ..</a></div>\n'
            
            html += """        <div class="listing">
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th style="width: 150px; text-align: right;">Access Count</th>
                </tr>
            </thead>
            <tbody>
"""
            
            # Add directories
            for d in dirs:
                # Generate link with trailing slash for directories
                if url_path and url_path != '':
                    link = f"/{url_path}/{d}"
                    item_path = f"{url_path}/{d}"
                else:
                    link = f"/{d}"
                    item_path = d
                
                hits = all_counts.get(item_path, 0)
                html += f'                <tr><td class="dir"><a href="{link}/">{d}/</a></td><td class="hits">{hits}</td></tr>\n'
            
            # Add files
            for f in files:
                if url_path and url_path != '':
                    link = f"/{url_path}/{f}"
                    item_path = f"{url_path}/{f}"
                else:
                    link = f"/{f}"
                    item_path = f
                
                hits = all_counts.get(item_path, 0)
                html += f'                <tr><td class="file"><a href="{link}">{f}</a></td><td class="hits">{hits}</td></tr>\n'
            
            html += """            </tbody>
        </table>
        </div>
        
        <div class="footer">
            <span class="blink">●</span> HTTP Server v2.0 | Thread-Safe | Rate Limited | {len(dirs)} directories | {len(files)} files <span class="blink">●</span>
        </div>
    </div>
</body>
</html>"""
            
            body = html.encode('utf-8')
            self.send_response(client_socket, 200, "OK", "text/html", body)
            print(f"[RESPONSE] Thread {thread_id}: 200 OK - Served directory listing: /{url_path} ({len(dirs)} dirs, {len(files)} files)")
            
        except Exception as e:
            print(f"[ERROR] Thread {thread_id}: Error generating directory listing: {e}")
            self.send_error(client_socket, 500, "Internal Server Error")
    
    def send_response(self, client_socket, status_code, status_text, content_type, body):
        """
        Send HTTP response to client
        
        Args:
            client_socket: Socket connected to the client
            status_code: HTTP status code
            status_text: HTTP status text
            content_type: MIME type of the response body
            body: Response body as bytes
        """
        response = f"HTTP/1.1 {status_code} {status_text}\r\n"
        response += f"Content-Type: {content_type}\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += f"Server: Python-Multithreaded-HTTP-Server/2.0\r\n"
        response += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        
        client_socket.sendall(response.encode('utf-8') + body)
    
    def send_error(self, client_socket, status_code, status_text):
        """
        Send HTTP error response to client
        
        Args:
            client_socket: Socket connected to the client
            status_code: HTTP status code
            status_text: HTTP status text
        """
        # Special styling for 429 Rate Limit error
        if status_code == 429:
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{status_code} {status_text}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', 'Monaco', monospace;
            background: #000000;
            color: #ff0000;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .error-container {{
            max-width: 800px;
            width: 100%;
            border: 3px solid #ff0000;
            padding: 40px;
            background: #0a0000;
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.5),
                        inset 0 0 20px rgba(255, 0, 0, 0.1);
            animation: pulse-border 2s infinite;
        }}
        
        @keyframes pulse-border {{
            0%, 100% {{ box-shadow: 0 0 30px rgba(255, 0, 0, 0.5), inset 0 0 20px rgba(255, 0, 0, 0.1); }}
            50% {{ box-shadow: 0 0 50px rgba(255, 0, 0, 0.8), inset 0 0 30px rgba(255, 0, 0, 0.2); }}
        }}
        
        .terminal-header {{
            border-bottom: 2px solid #ff0000;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }}
        
        .prompt {{
            color: #ff0000;
            font-size: 14px;
            text-shadow: 0 0 5px #ff0000;
        }}
        
        h1 {{
            font-size: 72px;
            color: #ff0000;
            text-align: center;
            margin: 20px 0;
            text-shadow: 0 0 20px #ff0000, 0 0 40px #ff0000;
            font-weight: bold;
            letter-spacing: 5px;
        }}
        
        .error-title {{
            text-align: center;
            font-size: 24px;
            color: #ff6666;
            margin-bottom: 30px;
            text-transform: uppercase;
            letter-spacing: 3px;
        }}
        
        .error-message {{
            background: #1a0000;
            border-left: 3px solid #ff0000;
            padding: 20px;
            margin: 20px 0;
            font-size: 16px;
            line-height: 1.6;
        }}
        
        .error-message p {{
            margin: 10px 0;
            color: #ff9999;
        }}
        
        .warning-icon {{
            text-align: center;
            font-size: 48px;
            margin: 20px 0;
            animation: blink 1s infinite;
        }}
        
        @keyframes blink {{
            0%, 50% {{ opacity: 1; }}
            51%, 100% {{ opacity: 0.3; }}
        }}
        
        .details {{
            margin-top: 25px;
            padding: 15px;
            background: #0d0000;
            border: 1px solid #ff0000;
            font-size: 14px;
        }}
        
        .details-title {{
            color: #ff6666;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        
        .details-item {{
            color: #ff9999;
            margin: 5px 0;
            padding-left: 20px;
        }}
        
        .details-item::before {{
            content: "► ";
            color: #ff0000;
            margin-right: 5px;
        }}
        
        .retry-info {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            border: 1px dashed #ff0000;
            color: #ff9999;
            font-size: 14px;
        }}
        
        .countdown {{
            font-size: 24px;
            color: #ff0000;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .scan {{
            animation: scan 2s infinite;
            background: linear-gradient(transparent 0%, #ff0000 50%, transparent 100%);
            height: 2px;
            width: 100%;
            position: fixed;
            top: 0;
            left: 0;
            opacity: 0.2;
        }}
        
        @keyframes scan {{
            0% {{ top: 0; }}
            100% {{ top: 100%; }}
        }}
    </style>
</head>
<body>
    <div class="scan"></div>
    <div class="error-container">
        <div class="terminal-header">
            <div class="prompt">root@http-server:~$ access_denied</div>
        </div>
        
        <div class="warning-icon">⚠</div>
        
        <h1>{status_code}</h1>
        
        <div class="error-title">{status_text}</div>
        
        <div class="error-message">
            <p><strong>ACCESS RATE EXCEEDED</strong></p>
            <p>You have sent too many requests in a short period of time.</p>
            <p>The server has temporarily blocked your IP address to prevent overload.</p>
        </div>
        
        <div class="details">
            <div class="details-title">Rate Limit Details:</div>
            <div class="details-item">Maximum: 5 requests per second per IP</div>
            <div class="details-item">Your IP has exceeded this limit</div>
            <div class="details-item">Status: BLOCKED</div>
        </div>
        
        <div class="retry-info">
            <div>Please wait a moment before retrying</div>
            <div class="countdown">⏳ Wait 1 second</div>
            <div>Then try your request again</div>
        </div>
    </div>
</body>
</html>"""
        else:
            # Default error page for other errors (404, 403, 500, etc.)
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{status_code} {status_text}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', 'Monaco', monospace;
            background: #000000;
            color: #d9534f;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .error-container {{
            text-align: center;
            border: 2px solid #d9534f;
            padding: 50px;
            background: #0a0000;
            box-shadow: 0 0 20px rgba(217, 83, 79, 0.3);
            max-width: 600px;
        }}
        
        h1 {{
            color: #d9534f;
            font-size: 72px;
            margin: 0;
            text-shadow: 0 0 10px #d9534f;
        }}
        
        p {{
            color: #ff9999;
            font-size: 20px;
            margin-top: 20px;
        }}
        
        .home-link {{
            margin-top: 30px;
            display: inline-block;
            color: #d9534f;
            text-decoration: none;
            border: 1px solid #d9534f;
            padding: 10px 20px;
            transition: all 0.3s;
        }}
        
        .home-link:hover {{
            background: #d9534f;
            color: #000;
            box-shadow: 0 0 15px #d9534f;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <h1>{status_code}</h1>
        <p>{status_text}</p>
        <a href="/" class="home-link">← Return to Home</a>
    </div>
</body>
</html>"""
        
        body = html.encode('utf-8')
        self.send_response(client_socket, status_code, status_text, "text/html", body)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python server.py <directory> [options]")
        print("\nOptions:")
        print("  --no-lock              Disable locks (demonstrate race conditions)")
        print("  --no-rate-limit        Disable rate limiting")
        print("  --rate-limit <rps>     Set rate limit (requests per second per IP)")
        print("  --delay <seconds>      Add artificial delay per request (for testing)")
        print("\nExamples:")
        print("  python server.py ./collection")
        print("  python server.py ./collection --no-lock")
        print("  python server.py ./collection --delay 1")
        print("  python server.py ./collection --rate-limit 3")
        sys.exit(1)
    
    directory = sys.argv[1]
    use_lock = '--no-lock' not in sys.argv
    enable_rate_limit = '--no-rate-limit' not in sys.argv
    
    # Parse rate limit
    rate_limit_rps = 5
    if '--rate-limit' in sys.argv:
        idx = sys.argv.index('--rate-limit')
        if idx + 1 < len(sys.argv):
            rate_limit_rps = int(sys.argv[idx + 1])
    
    # Parse delay
    request_delay = 0
    if '--delay' in sys.argv:
        idx = sys.argv.index('--delay')
        if idx + 1 < len(sys.argv):
            request_delay = float(sys.argv[idx + 1])
    
    try:
        server = HTTPServer(
            host='0.0.0.0',
            port=8080,
            directory=directory,
            use_lock=use_lock,
            enable_rate_limit=enable_rate_limit,
            rate_limit_rps=rate_limit_rps,
            request_delay=request_delay
        )
        server.start()
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
