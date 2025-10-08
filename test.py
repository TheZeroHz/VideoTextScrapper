#!/usr/bin/env python3
"""
N.A.M.O.R. Setup Diagnostic Tool
Checks if everything is configured correctly
"""

import os
import sys
import socket

print("="*60)
print("N.A.M.O.R. x BUBT HUB - Setup Diagnostic")
print("="*60)
print()

# Check 1: Python Version
print("✓ Checking Python version...")
version = sys.version_info
if version.major >= 3 and version.minor >= 8:
    print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
else:
    print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
print()

# Check 2: Required Files
print("✓ Checking required files...")
files_to_check = [
    'app.py',
    'templates/index.html',
    'requirements.txt'
]

all_files_exist = True
for file in files_to_check:
    if os.path.exists(file):
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} (MISSING!)")
        all_files_exist = False
print()

# Check 3: Required Modules
print("✓ Checking Python modules...")
required_modules = [
    'flask',
    'flask_cors',
    'speech_recognition',
    'pydub',
    'yt_dlp'
]

all_modules_installed = True
for module in required_modules:
    try:
        __import__(module.replace('_', ''))
        print(f"  ✅ {module}")
    except ImportError:
        print(f"  ❌ {module} (NOT INSTALLED!)")
        all_modules_installed = False
print()

# Check 4: FFmpeg
print("✓ Checking FFmpeg...")
import subprocess
try:
    result = subprocess.run(['ffmpeg', '-version'], 
                          capture_output=True, 
                          text=True, 
                          timeout=5)
    if result.returncode == 0:
        version_line = result.stdout.split('\n')[0]
        print(f"  ✅ FFmpeg installed ({version_line.split()[2]})")
    else:
        print(f"  ❌ FFmpeg not working properly")
except FileNotFoundError:
    print(f"  ❌ FFmpeg NOT FOUND!")
    print(f"     Install from: https://ffmpeg.org")
except Exception as e:
    print(f"  ⚠️  Could not check FFmpeg: {e}")
print()

# Check 5: Port Availability
print("✓ Checking port 8888...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 8888))
if result == 0:
    print(f"  ⚠️  Port 8888 is ALREADY IN USE!")
    print(f"     Stop other services or change port in app.py")
else:
    print(f"  ✅ Port 8888 is available")
sock.close()
print()

# Check 6: Network Info
print("✓ Network Information...")
hostname = socket.gethostname()
try:
    local_ip = socket.gethostbyname(hostname)
    print(f"  📡 Hostname: {hostname}")
    print(f"  📡 Local IP: {local_ip}")
    print(f"  📡 Server will be at: http://{local_ip}:8888")
except:
    print(f"  ⚠️  Could not determine local IP")
print()

# Check 7: Uploads Directory
print("✓ Checking uploads directory...")
if os.path.exists('uploads'):
    print(f"  ✅ uploads/ directory exists")
else:
    print(f"  ⚠️  uploads/ directory missing (will be created)")
    try:
        os.makedirs('uploads')
        print(f"  ✅ Created uploads/ directory")
    except Exception as e:
        print(f"  ❌ Could not create uploads/: {e}")
print()

# Final Summary
print("="*60)
print("SUMMARY")
print("="*60)

issues = []
if version.major < 3 or version.minor < 8:
    issues.append("Upgrade Python to 3.8+")
if not all_files_exist:
    issues.append("Missing required files")
if not all_modules_installed:
    issues.append("Install missing modules: pip install -r requirements.txt")

if issues:
    print("❌ ISSUES FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    print()
    print("Fix these issues before running the server!")
else:
    print("✅ ALL CHECKS PASSED!")
    print()
    print("You can now start the server:")
    print("   python app.py")
    print()
    print("Then open your browser:")
    print("   http://localhost:8888")

print("="*60)
