; Instalador de ktool (Inno Setup). Toma el ejecutable que genera PyInstaller
; (dist\kmap.exe) y lo instala por usuario, agregandolo al PATH.

#define MyAppName "ktool"
#define MyAppVersion "0.2.1"
#define MyAppPublisher "Leostriker"
#define MyAppURL "https://github.com/leostriker111/ktool"

[Setup]
AppId={{B7D4F2A1-9C3E-4E6A-8F21-1A2B3C4D5E6F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\ktool
DefaultGroupName=ktool
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=Output
OutputBaseFilename=ktool-setup
Compression=lzma
SolidCompression=yes
ChangesEnvironment=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "..\dist\kmap.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ktool (interfaz grafica)"; Filename: "{app}\kmap.exe"; Parameters: "gui"
Name: "{group}\Desinstalar ktool"; Filename: "{uninstallexe}"

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; \
    ValueData: "{olddata};{app}"; Check: NeedsAddPath('{app}')

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  Param := ExpandConstant(Param);
  Result := Pos(';' + Lowercase(Param) + ';', ';' + Lowercase(OrigPath) + ';') = 0;
end;
