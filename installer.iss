#define MyAppName "BiCP"
#define MyAppVersion "1.2.0"
#define MyAppPublisher "BiCP"
#define MyAppExeName "BiCP.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\BiCP

OutputDir=installer
OutputBaseFilename=BiCP-{#MyAppVersion}-Setup

Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\BiCP\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\BiCP"; Filename: "{app}\BiCP.exe"
Name: "{autodesktop}\BiCP"; Filename: "{app}\BiCP.exe"

[Run]
Filename: "{app}\BiCP.exe"; Description: "Launch BiCP"; Flags: nowait postinstall skipifsilent