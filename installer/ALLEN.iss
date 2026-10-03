#define ProductVersion "1.0.0"
#define ProductName "ALLEN"
#define SourceDir AddBackslash(ExtractFileDir(SourcePath)) + ".."
#define AppPackage AddBackslash(SourceDir) + "dist\ALLEN"
#define ModelPackage AddBackslash(SourceDir) + "dist\model-pack\Qwen3.5-0.8B-Q8_0.gguf"
#define AppIcon AddBackslash(SourceDir) + "frontend\assets\allen.ico"

[Setup]
AppId={{6C8849C9-2349-44CB-B68B-A5A683078B77}
AppName={#ProductName}
AppVersion={#ProductVersion}
AppPublisher=Universidad del Istmo
DefaultDirName={autopf}\ALLEN
DefaultGroupName=ALLEN
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
OutputDir={#SourceDir}\dist\installer
OutputBaseFilename=ALLEN_Setup
SetupIconFile={#AppIcon}
UninstallDisplayIcon={app}\ALLEN.exe
Compression=lzma2/fast
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
CloseApplications=yes
RestartApplications=no
Uninstallable=yes
VersionInfoVersion={#ProductVersion}
VersionInfoProductName=ALLEN
VersionInfoDescription=Instalador de ALLEN con inteligencia artificial local
VersionInfoCompany=Universidad del Istmo

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Dirs]
Name: "{commonappdata}\ALLEN"; Permissions: users-modify
Name: "{commonappdata}\ALLEN\logs"; Permissions: users-modify
Name: "{commonappdata}\ALLEN\models"; Permissions: users-modify

[Registry]
Root: HKLM; Subkey: "SOFTWARE\ALLEN"; Flags: uninsdeletekey

[Files]
Source: "{#AppPackage}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#ModelPackage}"; DestDir: "{commonappdata}\ALLEN\models"; Flags: ignoreversion
Source: "{#SourceDir}\dist\model-pack\LICENSE-Apache-2.0.txt"; DestDir: "{app}\licenses"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\ALLEN\ALLEN"; Filename: "{app}\ALLEN.exe"; WorkingDir: "{app}"; IconFilename: "{#AppIcon}"
Name: "{autodesktop}\ALLEN"; Filename: "{app}\ALLEN.exe"; WorkingDir: "{app}"; IconFilename: "{#AppIcon}"
Name: "{autoprograms}\ALLEN\Desinstalar ALLEN"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\allen_register.exe"; Parameters: '--install-root "{app}" --version "{#ProductVersion}" --llama-server "{app}\runtime\llama\llama-server.exe" --model "{commonappdata}\ALLEN\models\Qwen3.5-0.8B-Q8_0.gguf"'; Flags: runhidden waituntilterminated; StatusMsg: "Registrando instalación local de ALLEN..."
Filename: "{sys}\explorer.exe"; Parameters: '/select,"{commonappdata}\ALLEN\activation-request.allen"'; Description: "Abrir solicitud de activación para enviarla al administrador de licencias"; Flags: postinstall shellexec skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
var
  RemoveAllenData: Boolean;

function InitializeUninstall(): Boolean;
begin
  RemoveAllenData := MsgBox('¿También deseas eliminar el modelo local, la licencia, la configuración y el progreso de este equipo?', mbConfirmation, MB_YESNO) = idYes;
  Result := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if (CurUninstallStep = usPostUninstall) and RemoveAllenData then
    DelTree(ExpandConstant('{commonappdata}\ALLEN'), True, True, True);
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
    WizardForm.FinishedLabel.Caption := 'ALLEN se instaló con el modelo local y registró este equipo. Para habilitar el inicio, envía ProgramData\ALLEN\activation-request.allen al administrador de licencias y guarda el license.allen firmado que recibas en ProgramData\ALLEN. Después abre ALLEN desde el acceso directo.';
end;
