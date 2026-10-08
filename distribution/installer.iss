#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#ifndef SourceDir
  #define SourceDir "..\dist\ALLEN"
#endif
#ifndef OutputDir
  #define OutputDir "..\artifacts"
#endif

[Setup]
AppId={{A81A2D5C-0F53-4F5A-94D4-9A9F6AF5EAAA}
AppName=ALLEN
AppVersion={#MyAppVersion}
AppPublisher=ALLEN
DefaultDirName={localappdata}\Programs\ALLEN
DefaultGroupName=ALLEN
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#OutputDir}
OutputBaseFilename=ALLEN-{#MyAppVersion}-Setup-Windows-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\ALLEN.exe
VersionInfoVersion={#MyAppVersion}
VersionInfoProductName=ALLEN
VersionInfoProductVersion={#MyAppVersion}

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\ALLEN"; Filename: "{app}\ALLEN.exe"
Name: "{autoprograms}\Eliminar ALLEN completamente"; Filename: "{app}\Eliminar ALLEN completamente.bat"; WorkingDir: "{app}"
Name: "{autodesktop}\ALLEN"; Filename: "{app}\ALLEN.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ALLEN.exe"; Description: "Abrir ALLEN"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function InitializeUninstall(): Boolean;
begin
  Result := True;
  MsgBox(
    'La desinstalación elimina la aplicación, pero conserva tus perfiles, progreso y copias locales en %LOCALAPPDATA%\ALLEN.',
    mbInformation,
    MB_OK
  );
end;
