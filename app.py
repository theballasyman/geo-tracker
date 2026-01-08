from flask import Flask, render_template, request, redirect
import requests
import datetime
import json
import os

app = Flask(__name__)

LOG_FILE = 'visits.json'

# Create empty log file if it doesn't exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        json.dump([], f)

def get_country_info(ip):
    if ip.startswith('127.') or ip.startswith('192.168.') or ip == '::1':
        return "Local", "🏠"
    
    try:
        resp = requests.get(f"https://api.country.is/{ip}", timeout=5)
        data = resp.json()
        code = data.get('country', '??')
        flag = ''.join(chr(ord(c) + 127397) for c in code.upper())
        return code, flag
    except:
        return "Unknown", "🌍"

def log_visit(country_code, flag, path):
    visits = []
    try:
        with open(LOG_FILE, 'r') as f:
            visits = json.load(f)
    except:
        pass
    
    visits.append({
        'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'country': country_code,
        'flag': flag,
        'path': path
    })
    
    # Keep only last 50 visits
    visits = visits[-50:]
    
    with open(LOG_FILE, 'w') as f:
        json.dump(visits, f, indent=2)
    
    print(f"Visit logged: {flag} {country_code} → {path}")

@app.route('/')
def index():
    ip = request.remote_addr
    if 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For'].split(',')[0].strip()
    
    country_code, flag = get_country_info(ip)
    log_visit(country_code, flag, '/')
    
    return render_template('index.html', flag=flag, country=country_code)

@app.route('/stats')
def stats():
    visits = []
    try:
        with open(LOG_FILE, 'r') as f:
            visits = json.load(f)
    except:
        pass
    return render_template('stats.html', visits=reversed(visits))

@app.route('/go/<short_code>')
def tracker(short_code):
    redirects = {
        'google': 'https://google.com',
        'youtube': 'https://youtube.com',
        'github': 'https://github.com',
        'x': 'https://x.com',
        'reddit': 'https://reddit.com'
    }
    
    target = redirects.get(short_code.lower())
    if not target:
        return "<h1>404 - Link not found 😢</h1>", 404
    
    ip = request.remote_addr
    if 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For'].split(',')[0].strip()
    
    country_code, flag = get_country_info(ip)
    log_visit(country_code, flag, f'/go/{short_code}')
    
    return redirect(target)

if __name__ == '__main__':
    app.run(debug=True)