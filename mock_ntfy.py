"""Mock ntfy server for testing."""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime


class MockNtfyHandler(BaseHTTPRequestHandler):
    """Simple mock ntfy server for testing."""

    def do_POST(self):
        """Handle POST requests (publish messages)."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        title = self.headers.get('Title', 'Notification')
        priority = self.headers.get('Priority', 'default')
        tags = self.headers.get('Tags', '')

        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] NOTIFICATION RECEIVED")
        print(f"{'='*60}")
        print(f"Title: {title}")
        print(f"Priority: {priority}")
        print(f"Tags: {tags}")
        print(f"Message:\n{body}")
        print(f"{'='*60}\n")

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {"id": "test123", "time": int(datetime.now().timestamp())}
        self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        """Handle GET requests (health check, subscribe, etc)."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Mock ntfy server running')

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 80), MockNtfyHandler)
    print("Mock ntfy server starting on port 80...")
    print("Waiting for notifications...\n")
    server.serve_forever()
