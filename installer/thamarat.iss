; Thamarat ERP Inno Setup Script
; Windows Installer Configuration

#define MyAppName "Thamarat ERP"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "NexaGuard_Ye AI Solutions"
#define MyAppURL "https://nexaguard-ye.com"
#define MyAppExeName "Thamarat ERP.exe"

[Setup]
AppId={{E8B9C2D4-1F3A-5B7E-9D2C-8A6F4E1B3D7A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE.txt
OutputDir=.\Output
OutputBaseFilename=Thamarat-Setup-{#MyAppVersion}
SetupIconFile=..\electron\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Backend files
Source: "..\backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs
; Frontend build
Source: "..\frontend\build\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs
; Electron files
Source: "..\electron\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Auto-start with Windows (optional)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "ThamaratERP"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Create data directory
    ForceDirectories(ExpandConstant('{userappdata}\Thamarat'));
  end;
end;
