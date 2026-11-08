import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PHOTON_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Handler(BaseHTTPRequestHandler):
    seen = []

    def do_GET(self):
        Handler.seen.append(self.path)
        if self.path == '/':
            body = b'<html><body><a href="/next">next</a><script src="/app.js"></script></body></html>'
            self._respond(200, 'text/html', body)
        elif self.path == '/next':
            self._respond(200, 'text/html', b'<html><body>next</body></html>')
        elif self.path == '/app.js':
            self._respond(200, 'application/javascript', b'var endpoint = "/api/v1/users";')
        else:
            self._respond(404, 'text/html', b'<html><body>not found</body></html>')

    def _respond(self, status, content_type, body):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class LevelZeroTest(unittest.TestCase):
    def _run(self, level):
        Handler.seen = []
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            output_dir = tempfile.mkdtemp(prefix='photon-test-')
            proc = subprocess.run(
                [
                    sys.executable,
                    os.path.join(PHOTON_DIR, 'photon.py'),
                    '-u', 'http://127.0.0.1:%d/' % server.server_address[1],
                    '-l', str(level),
                    '-o', 'output',
                ],
                cwd=output_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
        finally:
            server.shutdown()
            thread.join()
        return proc, list(Handler.seen)

    def test_level_zero_fetches_only_the_target(self):
        proc, seen = self._run(0)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(seen, ['/'])

    def test_level_two_still_follows_links(self):
        proc, seen = self._run(2)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn('/next', seen)


if __name__ == '__main__':
    unittest.main()
