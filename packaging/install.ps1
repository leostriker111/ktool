# Instala ktool desde el codigo fuente (requiere Python en el PATH).
# Copia el paquete a la carpeta de usuario, crea el comando 'kmap' y lo agrega al PATH.

$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "No se encontro Python en el PATH. Instalalo desde https://python.org y reintenta." -ForegroundColor Red
    exit 1
}

$src = Join-Path $PSScriptRoot ".."
$dir = Join-Path $env:LOCALAPPDATA "Programs\ktool"

Write-Host "Instalando ktool en: $dir"
New-Item -ItemType Directory -Force -Path $dir | Out-Null

Copy-Item -Recurse -Force (Join-Path $src "ktool") $dir
Copy-Item -Force (Join-Path $PSScriptRoot "ktool_launcher.py") $dir

$cmd = @"
@echo off
python "%~dp0ktool_launcher.py" %*
"@
Set-Content -Path (Join-Path $dir "kmap.cmd") -Value $cmd -Encoding ASCII
Set-Content -Path (Join-Path $dir "ktool.cmd") -Value $cmd -Encoding ASCII

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$dir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$dir", "User")
    Write-Host "Agregado al PATH del usuario." -ForegroundColor Green
} else {
    Write-Host "Ya estaba en el PATH."
}

Write-Host ""
Write-Host "Listo. Abre una terminal nueva y prueba:" -ForegroundColor Green
Write-Host "    kmap -e `"A'B + C`" --open"
Write-Host "    kmap gui"
