@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
echo ===== Ripon Cash Memo Studio - EXE build =====

set "PY=py -3"
where py >nul 2>nul
if errorlevel 1 set "PY=python"
%PY% --version
if errorlevel 1 goto nopy

if not exist venv %PY% -m venv venv
if errorlevel 1 goto fail
call venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto fail

echo ----- running tests -----
python -m unittest discover -s tests -t .
if errorlevel 1 echo WARNING: some tests failed, continuing with the build anyway.

echo ----- building EXE -----
pyinstaller --noconfirm --clean cash_memo_studio.spec
if errorlevel 1 goto fail

echo.
echo ONE-FILE EXE ready: dist\RiponCashMemoStudio.exe

set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" goto noinno
echo ----- building installer -----
"%ISCC%" installer.iss
echo Installer: Output\RiponCashMemoStudio_Setup.exe
goto end

:noinno
echo Inno Setup 6 not found, skipping the installer. Install it from jrsoftware.org to also get a Setup.exe
goto end

:nopy
echo Python is not installed. Install Python 3.11 from python.org and tick Add to PATH, then run this file again.
goto end

:fail
echo.
echo BUILD FAILED. Copy the red or error lines above and send them.

:end
echo.
pause
