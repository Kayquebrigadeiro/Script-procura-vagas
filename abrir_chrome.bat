@echo off
echo Abrindo Chrome com porta de debug...
start chrome --remote-debugging-port=9222 --user-data-dir="C:\selenium_chrome_profile"
echo Chrome aberto! Agora execute: python main.py
pause
