from flask import Flask, render_template, request, redirect
import requests
import datetime
import json
import os

app = Flask(__name__)

LOG_FILE = 'visits.json'

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

def log_visit(ip,
