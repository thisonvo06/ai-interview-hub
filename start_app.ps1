param(
    [ValidateSet('All', 'Backend', 'Frontend', 'Stop')]
    [string]$Mode = 'All',
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$projectRoot = $PSScriptRoot
$logRoot = Join-Path $projectRoot 'logs'
$frontendUrl = 'http://127.0.0.1:5173'
$backendUrl = 'http://127.0.0.1:8000'
$startedServices = New-Object System.Collections.ArrayList
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null

function Get-CommandPath([string]$Name) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command) { return $command.Source }
    return $null
}

function Test-BackendPython([string]$Executable) {
    try {
        & $Executable -c 'import fastapi, uvicorn, sqlalchemy, alembic, pydantic_settings, jose, passlib, multipart, httpx, email_validator, websockets' 1>$null 2>$null
        return ($LASTEXITCODE -eq 0)
    } catch { return $false }
}

function Get-BackendPython {
    $venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $venvPython) {
        $pythonPath = $venvPython
    } else {
        $pythonPath = Get-CommandPath 'python.exe'
        if (-not $pythonPath) {
            $pyLauncher = Get-CommandPath 'py.exe'
            if ($pyLauncher) {
                $pythonPath = & $pyLauncher -3 -c 'import sys; print(sys.executable)'
                if ($LASTEXITCODE -ne 0) { $pythonPath = $null }
            }
        }
        if (-not $pythonPath) { throw '未找到 Python，请安装 Python 3 后重新双击启动。' }
        if (Test-BackendPython $pythonPath) { return $pythonPath }

        Write-Host '首次启动：正在创建 Python 虚拟环境……'
        & $pythonPath -m venv (Join-Path $projectRoot '.venv') | Out-Host
        if ($LASTEXITCODE -ne 0) { throw 'Python 虚拟环境创建失败。' }
        $pythonPath = $venvPython
    }

    if (-not (Test-BackendPython $pythonPath)) {
        Write-Host '首次启动：正在安装后端依赖，需要联网，请稍候……'
        & $pythonPath -m pip install -r (Join-Path $projectRoot 'backend\requirements.txt') | Out-Host
        if ($LASTEXITCODE -ne 0 -or -not (Test-BackendPython $pythonPath)) {
            throw '后端依赖安装失败，请检查网络后重新双击启动。'
        }
    }
    return $pythonPath
}

function Test-Port([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $connection = $client.ConnectAsync('127.0.0.1', $Port)
        return ($connection.Wait(500) -and $client.Connected)
    } catch { return $false }
    finally { $client.Dispose() }
}

function Test-ServiceReady([string]$Name) {
    try {
        if ($Name -eq 'backend') {
            $response = Invoke-WebRequest -UseBasicParsing -Uri "$backendUrl/" -TimeoutSec 2
            $health = $response.Content | ConvertFrom-Json
            return ($health.status -eq 'online' -and $health.project -like '*AI Interview Hub*')
        }
        $response = Invoke-WebRequest -UseBasicParsing -Uri "$frontendUrl/" -TimeoutSec 2
        return ($response.StatusCode -eq 200 -and $response.Content -match '/@vite/client' -and $response.Content -match '/src/main.ts')
    } catch { return $false }
}

function Stop-OwnedService([string]$Name) {
    $pidPath = Join-Path $logRoot "$Name.pid"
    if (-not (Test-Path -LiteralPath $pidPath)) { return }
    $record = Get-Content -LiteralPath $pidPath -Raw | ConvertFrom-Json
    $ownedProcess = Get-Process -Id ([int]$record.process_id) -ErrorAction SilentlyContinue
    if ($ownedProcess -and $ownedProcess.StartTime.ToUniversalTime().Ticks -eq [long]$record.start_ticks) {
        Stop-Process -Id $ownedProcess.Id -Force
        Write-Host "已关闭 $Name 服务。"
    }
    Remove-Item -LiteralPath $pidPath -Force
}

function Start-AppService([string]$Name, [string]$Executable, [string[]]$Arguments, [string]$Directory) {
    $stdoutPath = Join-Path $logRoot "$Name.log"
    $stderrPath = Join-Path $logRoot "$Name-error.log"
    $serviceProcess = Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $Directory -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
    $pidPath = Join-Path $logRoot "$Name.pid"
    $record = @{ process_id = $serviceProcess.Id; start_ticks = $serviceProcess.StartTime.ToUniversalTime().Ticks }
    $record | ConvertTo-Json | Set-Content -LiteralPath $pidPath -Encoding UTF8
    [void]$startedServices.Add($Name)

    $deadline = (Get-Date).AddSeconds(60)
    do {
        $serviceProcess.Refresh()
        if ($serviceProcess.HasExited) {
            throw "$Name 服务退出，请查看日志：$stderrPath"
        }
        if (Test-ServiceReady $Name) {
            Write-Host "$Name 服务已就绪。"
            return
        }
        Start-Sleep -Milliseconds 500
    } while ((Get-Date) -lt $deadline)
    throw "$Name 服务启动超时，请查看日志：$stderrPath"
}

try {
    if ($Mode -eq 'Stop') {
        Stop-OwnedService 'frontend'
        Stop-OwnedService 'backend'
        Write-Host '关闭完成。'
        exit 0
    }

    Write-Host '正在启动智面仓……'
    if ($Mode -in @('All', 'Backend')) {
        if (Test-Port 8000) {
            if (-not (Test-ServiceReady 'backend')) { throw '8000 端口被其他程序占用，请释放端口后重试。' }
            Write-Host '后端已在运行。'
        } else {
            $pythonPath = Get-BackendPython
            Start-AppService 'backend' $pythonPath @('-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000') (Join-Path $projectRoot 'backend')
        }
    }

    if ($Mode -in @('All', 'Frontend')) {
        if (Test-Port 5173) {
            if (-not (Test-ServiceReady 'frontend')) { throw '5173 端口被其他程序占用，请释放端口后重试。' }
            Write-Host '前端已在运行。'
        } else {
            $nodePath = Get-CommandPath 'node.exe'
            if (-not $nodePath) { throw '未找到 Node.js，请安装后重新双击启动。' }
            $frontendRoot = Join-Path $projectRoot 'frontend'
            $vitePath = Join-Path $frontendRoot 'node_modules\vite\bin\vite.js'
            if (-not (Test-Path -LiteralPath $vitePath)) {
                $npmPath = Get-CommandPath 'npm.cmd'
                if (-not $npmPath) { throw '未找到 npm，请重新安装 Node.js 后重试。' }
                Write-Host '首次启动：正在安装前端依赖，需要联网，请稍候……'
                Push-Location $frontendRoot
                try {
                    & $npmPath ci
                    if ($LASTEXITCODE -ne 0) { throw '前端依赖安装失败，请检查网络后重试。' }
                } finally { Pop-Location }
            }
            Start-AppService 'frontend' $nodePath @(('"{0}"' -f $vitePath), '--host', '127.0.0.1', '--port', '5173', '--strictPort') $frontendRoot
        }
    }

    if ($Mode -eq 'Backend') {
        $openUrl = "$backendUrl/docs"
    } else {
        $openUrl = $frontendUrl
    }
    if (-not $NoBrowser) { Start-Process -FilePath $openUrl }
    Write-Host "启动成功：$openUrl"
    Write-Host '服务在后台运行。双击“一键关闭.bat”可停止服务。'
} catch {
    foreach ($serviceName in $startedServices) {
        try { Stop-OwnedService $serviceName } catch { }
    }
    Write-Host "启动失败：$($_.Exception.Message)" -ForegroundColor Red
    Write-Host "日志目录：$logRoot"
    exit 1
}
