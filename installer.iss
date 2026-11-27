; Inno Setup script - run after PyInstaller build (dist\RiponCashMemoStudio)
[Setup]
AppName=RIPON COMPUTER AND ELECTRONICS - Cash Memo Studio
AppVersion=1.0
AppPublisher=Ripon Computer and Electronics
DefaultDirName={autopf}\RiponCashMemoStudio
DefaultGroupName=Ripon Cash Memo Studio
OutputBaseFilename=RiponCashMemoStudio_Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=assets\app.ico

[Files]
; app icon is bundled via assets\app.ico
Source: "dist\RiponCashMemoStudio.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Ripon Cash Memo Studio"; Filename: "{app}\RiponCashMemoStudio.exe"
Name: "{autodesktop}\Ripon Cash Memo Studio"; Filename: "{app}\RiponCashMemoStudio.exe"

[Run]
Filename: "{app}\RiponCashMemoStudio.exe"; Description: "Launch now"; Flags: nowait postinstall skipifsilent
