#!/usr/bin/env python3

import requests
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json
import config as cfg

def save_token(token_data):
    with open(cfg.TOKEN_FILE, 'w') as file:
        json.dump(token_data, file)

def start_authentication():
    params = {
        'client_id': cfg.CLIENT_ID,
        'redirect_uri': cfg.REDIRECT_URI,
        'response_type': 'code',
        'scope': 'all'
    }
    url = requests.Request('GET', cfg.AUTHORIZE_URL, params=params).prepare().url
    webbrowser.open(url)

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/favicon.ico":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.server.path = self.path
            self.wfile.write(b'Authentication successful! You can close this window.')

def request_access_token(code):
    data = {
        'code': code,
        'client_id': cfg.CLIENT_ID,
        'client_secret': cfg.CLIENT_SECRET,
        'redirect_uri': cfg.REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(cfg.TOKEN_URL, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        return None

start_authentication()

httpd = HTTPServer(('localhost', 8000), RedirectHandler)
thread = threading.Thread(target=httpd.serve_forever)
thread.daemon = True
thread.start()

print("Waiting for authentication... Press Ctrl+C to cancel.")

try:
    httpd.handle_request()
except KeyboardInterrupt:
    print("Authentication process canceled by user.")
    exit()

try:
    code = httpd.path.split("code=")[1].split("&")[0]
except IndexError:
    print("Could not extract auth-code")
    exit()

access_token = request_access_token(code)
if access_token:
    print(access_token)
    save_token(access_token)
    print(f"Successfully saved access token to {cfg.TOKEN_FILE}")
else:
    print("Error while requesting access token.")