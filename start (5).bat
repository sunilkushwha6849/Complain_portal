@echo off
title GrievAI Portal - Server
color 0A
echo.
echo  =====================================================
echo   GrievAI Portal - Starting...
echo  =====================================================
echo.

:: Move to this file's folder
cd /d "%~dp0"
echo  Folder: %CD%
echo.

:: Python check
python --version
if errorlevel 1 (
    color 0C
    echo.
    echo  ERROR: Python nahi mila!
    echo  https://www.python.org/downloads/ se install karo
    echo  Install mein "Add Python to PATH" tick karna
    echo.
    pause
    exit
)

echo.
echo  [1/3] Flask install ho raha hai...
pip install flask flask-cors python-dotenv
echo.
echo  [2/3] Dependencies complete!
echo.
echo  [3/3] Server start ho raha hai...
echo.
echo  =====================================================
echo   Browser mein kholein: http://localhost:8000
echo  =====================================================
echo.

python app.py

echo.
echo  =====================================================
echo   Server band ho gaya ya error aaya!
echo   Upar wala error message copy karke bhejo
echo  =====================================================
echo.
pause
