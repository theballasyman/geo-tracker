from flask import Flask, render_template, request, redirect
import requests
import datetime
import json
import os

app = Flask(__name__)

LOG_FILE = 'visits.json'

# Create file if missing
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        json.dump([], f)

def get_country_info(ip):
    if ip in ['127.0.0.1', '::1'] or ip.startswith('192.168.'):
        return "Local", "🏠"
    
    try:
        resp = requests.get(f"https://api.country.is/{ip}", timeout=5)
        data = resp.json()
        code = data.get('country', '??')
        flag = ''.join(chr(ord(c) + 127397) for c in code.upper())
        return code, flag
    except:
        return "Unknown", "🌍"

def log_visit(ip, country_code, flag, path):
    visits = []
    try:
        with open(LOG_FILE, 'r') as f:
            visits = json.load(f)
    except:
        pass
    
    visits.append({
        'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'ip': ip,
        'country': country_code,
        'flag': flag,
        'path': path
    })
    
    visits = visits[-50:]
    
    with open(LOG_FILE, 'w') as f:
        json.dump(visits, f, indent=2)
    
    print(f"Visit logged: {flag} {country_code} | IP: {ip} → {path}")

@app.route('/')
def index():
    ip = request.remote_addr
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
    
    country_code, flag = get_country_info(ip)
    log_visit(ip, country_code, flag, '/')
    
    return render_template('index.html', flag=flag, country=country_code, ip=ip)

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
        'track': 'https://example.com'  # change if you want
    }
    
    target = redirects.get(short_code.lower())
    if not target:
        return "<h1>404 - Link not found 😢</h1>", 404
    
    ip = request.remote_addr
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
    
    country_code, flag = get_country_info(ip)
    log_visit(ip, country_code, flag, f'/go/{short_code}')
    
    return redirect(target)

# Remove the if __name__ block completely for production (Gunicorn doesn't use it)

# if __name__ == '__main__':
#     app.run(debug=True)
