#ifndef AppVersion
  #define AppVersion "0.9.0"
#endif
#ifndef BuildDir
  #error BuildDir is required
#endif
#ifndef FilesDir
  #error FilesDir is required
#endif

[Setup]
AppId={{472314BD-21AB-4D13-92E3-2E2BA6CB3639}
AppName=Synapsis
AppVersion={#AppVersion}
AppPublisher=Synapsis
DefaultDirName={localappdata}\Programs\Synapsis
DefaultGroupName=Synapsis
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\Synapsis.exe
SetupIconFile={#BuildDir}\Synapsis.ico
OutputDir={#BuildDir}
OutputBaseFilename=Synapsis-Setup
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2/fast
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#FilesDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\Synapsis"; Filename: "{app}\Synapsis.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\Synapsis.exe"; Description: "Abrir Synapsis"; Flags: nowait postinstall skipifsilent
