param(
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"

$CondaBat = Join-Path $env:LOCALAPPDATA "miniforge3\condabin\conda.bat"
$EnvName = "prefect-gdal"
$PrefectApiUrl = "http://127.0.0.1:4200/api"

if (-not (Test-Path $CondaBat)) {
    throw "Conda nao encontrado em $CondaBat. Instale Miniforge ou ajuste o caminho no script."
}

& $CondaBat run -n $EnvName python -c "from osgeo import gdal; print(gdal.VersionInfo('--version'))"

if ($CheckOnly) {
    Write-Host "Ambiente $EnvName validado. Tratamento nao executado porque -CheckOnly foi informado."
    exit 0
}

& $CondaBat run -n $EnvName python -m prefect config set PREFECT_API_URL=$PrefectApiUrl
& $CondaBat run -n $EnvName python main.py
