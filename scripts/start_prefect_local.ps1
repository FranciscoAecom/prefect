param(
    [switch]$ResetDatabase,
    [switch]$StopExisting,
    [string]$DataLakeBase = "L:\Secure_DCS\BRBLH1PINFW001\COE_Digital\coe_digital_data"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$LogDir = Join-Path $ProjectRoot ".prefect-logs"
$PrefectApiUrl = "http://127.0.0.1:4200/api"

if (-not (Test-Path $Python)) {
    throw "Ambiente .venv nao encontrado em $Python. Execute 'uv sync' antes de iniciar o Prefect local."
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Stop-PrefectLocalProcesses {
    $normalizedProjectRoot = $ProjectRoot.ToLowerInvariant()
    Get-CimInstance Win32_Process |
        Where-Object {
            $commandLine = ($_.CommandLine -as [string])
            $normalizedCommandLine = if ($commandLine) { $commandLine.ToLowerInvariant() } else { "" }
            $normalizedCommandLine -and
            $normalizedCommandLine.Contains($normalizedProjectRoot) -and
            (
                $normalizedCommandLine.Contains("prefect server start") -or
                $normalizedCommandLine.Contains("scripts\serve.py")
            )
        } |
        ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
            Write-Host "Processo Prefect local encerrado: $($_.ProcessId)"
        }
}

function Wait-PrefectApi {
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "$PrefectApiUrl/health" -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                return
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    throw "API do Prefect nao ficou saudavel em 60 segundos."
}

if ($StopExisting -or $ResetDatabase) {
    Stop-PrefectLocalProcesses
}

$env:PYTHONIOENCODING = "utf-8"
$env:DATA_LAKE_BASE = $DataLakeBase
Write-Host "DATA_LAKE_BASE definido: $env:DATA_LAKE_BASE"

if ($ResetDatabase) {
    & $Python -m prefect server database reset -y --no-prompt
}

$server = Start-Process -FilePath $Python `
    -ArgumentList @("-m", "prefect", "server", "start", "--host", "127.0.0.1", "--port", "4200") `
    -WorkingDirectory $ProjectRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $LogDir "server.out.log") `
    -RedirectStandardError (Join-Path $LogDir "server.err.log") `
    -PassThru
Write-Host "Prefect server iniciado: PID=$($server.Id)"

Wait-PrefectApi

& $Python -m prefect config set PREFECT_API_URL=$PrefectApiUrl
& $Python scripts\prefect_admin.py set-default-variables
& $Python scripts\prefect_admin.py set-default-blocks
& $Python scripts\prefect_admin.py set-default-work-pools

$deployments = @(
    @{ Name = "scheduled-treatment"; Out = "serve-scheduled-treatment.out.log"; Err = "serve-scheduled-treatment.err.log" },
    @{ Name = "data-download"; Out = "serve-data-download.out.log"; Err = "serve-data-download.err.log" },
    @{ Name = "data-publish"; Out = "serve-data-publish.out.log"; Err = "serve-data-publish.err.log" }
)

foreach ($deployment in $deployments) {
    $process = Start-Process -FilePath $Python `
        -ArgumentList @("scripts\serve.py", $deployment.Name) `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogDir $deployment.Out) `
        -RedirectStandardError (Join-Path $LogDir $deployment.Err) `
        -PassThru
    Write-Host "Deployment $($deployment.Name) iniciado: PID=$($process.Id)"
}

Start-Sleep -Seconds 8
& $Python scripts\prefect_admin.py create-download-automation
& $Python scripts\prefect_admin.py create-treatment-publish-automation

Write-Host "Prefect local pronto: http://127.0.0.1:4200"
