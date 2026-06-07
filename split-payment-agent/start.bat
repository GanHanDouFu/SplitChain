@echo off
start "" "http://localhost:8080"
cd /d "%~dp0demo"
python -m http.server 8080
