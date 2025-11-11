"""
HTTP File Server - Lab 1
A simple HTTP server that serves HTML, PNG, and PDF files from a specified directory.
Supports directory listing for nested directories.
"""

import socket
import sys
import os
import time
from urllib.parse import unquote
from datetime import datetime


class HTTPServer:
    """Simple HTTP/1.1 File Server"""
    
    MIME_TYPES = {
        '.html': 'text/html',
        '.htm': 'text/html',
        '.png': 'image/png',
        '.pdf': 'application/pdf',
    }
    
    def __init__(self, host='0.0.0.0', port=8081, directory='.', request_delay=0):
        """
        Initialize the HTTP server
        
        Args:
            host: Host address to bind to
            port: Port number to listen on
            directory: Root directory to serve files from
            request_delay: Artificial delay per request (for testing)
        """
        self.host = host
        self.port = port
        self.directory = os.path.abspath(directory)
        self.server_socket = None
        self.request_delay = request_delay
        
        if not os.path.exists(self.directory):
            raise ValueError(f"Directory '{self.directory}' does not exist")
        
        print(f"[INFO] Server initialized")
        print(f"[INFO] Serving directory: {self.directory}")
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
                print(f"[CONNECTION] New connection from {client_address[0]}:{client_address[1]}")
                self.handle_request(client_socket, client_address)
        except KeyboardInterrupt:
            print("\n[INFO] Server shutting down...")
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def handle_request(self, client_socket, client_address):
        """
        Handle a single HTTP request
        
        Args:
            client_socket: Socket connected to the client
            client_address: Tuple containing client IP and port
        """
        try:
            # Artificial delay for testing (simulates work)
            if self.request_delay > 0:
                time.sleep(self.request_delay)
            
            # Receive the request
            request_data = client_socket.recv(4096).decode('utf-8')
            
            if not request_data:
                return
            
            # Parse the request
            lines = request_data.split('\r\n')
            request_line = lines[0]
            print(f"[REQUEST] {request_line}")
            
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
            self.serve_path(client_socket, path)
            
        except Exception as e:
            print(f"[ERROR] Error handling request: {e}")
            try:
                self.send_error(client_socket, 500, "Internal Server Error")
            except:
                pass
        finally:
            client_socket.close()
    
    def serve_path(self, client_socket, path):
        """
        Serve a file or directory listing
        
        Args:
            client_socket: Socket connected to the client
            path: Requested path (relative to root directory)
        """
        # Remove leading slash and resolve path
        if path.startswith('/'):
            path = path[1:]
        
        # Handle root path
        if path == '':
            path = 'index.html'
        
        # Construct full file path
        full_path = os.path.normpath(os.path.join(self.directory, path))
        
        # Security check: prevent directory traversal
        if not full_path.startswith(self.directory):
            self.send_error(client_socket, 403, "Forbidden")
            return
        
        # Check if path exists
        if not os.path.exists(full_path):
            self.send_error(client_socket, 404, "Not Found")
            return
        
        # If it's a directory, serve directory listing
        if os.path.isdir(full_path):
            self.serve_directory_listing(client_socket, full_path, path)
            return
        
        # If it's a file, serve the file
        self.serve_file(client_socket, full_path)
    
    def serve_file(self, client_socket, file_path):
        """
        Serve a file to the client
        
        Args:
            client_socket: Socket connected to the client
            file_path: Full path to the file to serve
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
            print(f"[RESPONSE] 200 OK - Served file: {os.path.basename(file_path)} ({len(body)} bytes)")
            
        except Exception as e:
            print(f"[ERROR] Error reading file: {e}")
            self.send_error(client_socket, 500, "Internal Server Error")
    
    def serve_directory_listing(self, client_socket, dir_path, url_path):
        """
        Generate and serve a directory listing page
        
        Args:
            client_socket: Socket connected to the client
            dir_path: Full path to the directory
            url_path: URL path (for generating links)
        """
        try:
            # Get directory contents
            entries = os.listdir(dir_path)
            entries.sort()
            
            # Separate directories and files
            dirs = [e for e in entries if os.path.isdir(os.path.join(dir_path, e))]
            files = [e for e in entries if os.path.isfile(os.path.join(dir_path, e))]
            
            # Generate HTML
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Directory Listing: /{url_path}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
        }}
        .container {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        ul {{
            list-style-type: none;
            padding: 0;
        }}
        li {{
            padding: 8px;
            border-bottom: 1px solid #eee;
        }}
        li:hover {{
            background-color: #f0f0f0;
        }}
        a {{
            text-decoration: none;
            color: #007acc;
            font-size: 16px;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .dir {{
            font-weight: bold;
        }}
        .dir::before {{
            content: "📁 ";
        }}
        .file::before {{
            content: "📄 ";
        }}
        .parent {{
            margin-bottom: 20px;
        }}
        .parent a {{
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Directory Listing: /{url_path}</h1>
"""
            
            # Add parent directory link if not at root
            if url_path and url_path != '':
                parent_path = '/'.join(url_path.split('/')[:-1])
                if parent_path:
                    parent_path = '/' + parent_path
                else:
                    parent_path = '/'
                html += f'        <div class="parent"><a href="{parent_path}">⬆️ Parent Directory</a></div>\n'
            
            html += '        <ul>\n'
            
            # Add directories
            for d in dirs:
                link = f"/{url_path}/{d}" if url_path else f"/{d}"
                html += f'            <li class="dir"><a href="{link}/">{d}/</a></li>\n'
            
            # Add files
            for f in files:
                link = f"/{url_path}/{f}" if url_path else f"/{f}"
                size = os.path.getsize(os.path.join(dir_path, f))
                size_str = self.format_size(size)
                html += f'            <li class="file"><a href="{link}">{f}</a> <span style="color: #999; font-size: 14px;">({size_str})</span></li>\n'
            
            html += """        </ul>
    </div>
</body>
</html>"""
            
            body = html.encode('utf-8')
            self.send_response(client_socket, 200, "OK", "text/html", body)
            print(f"[RESPONSE] 200 OK - Served directory listing: /{url_path} ({len(dirs)} dirs, {len(files)} files)")
            
        except Exception as e:
            print(f"[ERROR] Error generating directory listing: {e}")
            self.send_error(client_socket, 500, "Internal Server Error")
    
    def format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
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
        response += f"Server: Python-HTTP-Server/1.0\r\n"
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
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{status_code} {status_text}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 100px;
            background-color: #f5f5f5;
        }}
        .error-container {{
            background-color: white;
            padding: 40px;
            border-radius: 5px;
            display: inline-block;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #d9534f;
            font-size: 48px;
            margin: 0;
        }}
        p {{
            color: #666;
            font-size: 18px;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <h1>{status_code}</h1>
        <p>{status_text}</p>
    </div>
</body>
</html>"""
        
        body = html.encode('utf-8')
        self.send_response(client_socket, status_code, status_text, "text/html", body)
        print(f"[RESPONSE] {status_code} {status_text}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python server.py <directory> [--delay <seconds>]")
        print("Example: python server.py ./collection")
        print("Example: python server.py ./collection --delay 1")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    # Parse delay argument
    request_delay = 0
    if '--delay' in sys.argv:
        idx = sys.argv.index('--delay')
        if idx + 1 < len(sys.argv):
            request_delay = float(sys.argv[idx + 1])
    
    try:
        server = HTTPServer(host='0.0.0.0', port=8081, directory=directory, request_delay=request_delay)
        server.start()
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
