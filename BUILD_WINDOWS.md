# EXE বানানোর সহজ উপায় (Windows)
**উপায় ১ (নিজের পিসিতে):** Python 3.11 (64-bit, "Add to PATH" টিক দিয়ে) ইনস্টল করুন -> প্রজেক্ট ফোল্ডারে `build_exe.bat` ডাবল ক্লিক করুন -> শেষে `dist\RiponCashMemoStudio\RiponCashMemoStudio.exe` (Inno Setup 6 থাকলে `Output\RiponCashMemoStudio_Setup.exe` ও হবে)।
**উপায় ২ (পিসি ছাড়া, ফ্রি):** প্রজেক্টটা GitHub repo-তে আপলোড করুন -> Actions -> "Build Windows EXE" -> Run workflow -> শেষে Artifacts থেকে EXE ও Setup ডাউনলোড করুন (`.github/workflows/build-windows.yml`)।
EXE ফোল্ডারটা (শুধু .exe নয়, পুরো ফোল্ডার) অন্য পিসিতে কপি করলেই চলবে; Python লাগবে না।

---
# Build on Windows 10/11
1. Install Python 3.11+ (64-bit), then in the project folder: `py -m venv venv && venv\Scripts\activate && pip install -r requirements.txt`
2. Download Noto Sans Bengali (Google Fonts, OFL licence) and copy `NotoSansBengali-Regular.ttf` / `NotoSansBengali-Bold.ttf` into `assets\fonts\`.
3. Run `python -m unittest discover -s tests -t .` then `python app.py` to try it.
4. Build: `pyinstaller cash_memo_studio.spec` -> `dist\RiponCashMemoStudio\`
5. Installer: install Inno Setup, open `installer.iss`, Compile -> `Output\RiponCashMemoStudio_Setup.exe`
Data is stored in `%APPDATA%\RiponCashMemoStudio\` (database + backups).
