Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Say {
    param([string]$Message)

    Write-Host $Message
}

function Die {
    param([string]$Message)

    throw "error: $Message"
}

function Normalize-DirectoryForPathCompare {
    param([string]$Directory)

    $trimmed = $Directory.Trim('"')
    $trimChars = [char[]]@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)

    try {
        return ([System.IO.Path]::GetFullPath($trimmed)).TrimEnd($trimChars)
    } catch {
        return $trimmed.TrimEnd($trimChars)
    }
}

function Test-DirectoryOnPath {
    param([string]$Directory)

    if ([string]::IsNullOrWhiteSpace($env:Path)) {
        return $false
    }

    $target = Normalize-DirectoryForPathCompare -Directory $Directory
    foreach ($entry in ($env:Path -split ";")) {
        if ([string]::IsNullOrWhiteSpace($entry)) {
            continue
        }

        $candidate = Normalize-DirectoryForPathCompare -Directory $entry
        if ([string]::Equals($candidate, $target, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }

    return $false
}

function Add-DefaultBinToSessionPath {
    param([string]$InstallDir)

    if (-not (Test-DirectoryOnPath -Directory $InstallDir)) {
        if ([string]::IsNullOrEmpty($env:Path)) {
            $env:Path = $InstallDir
        } else {
            $env:Path = "$InstallDir;$env:Path"
        }

        $script:PathNote = $InstallDir
    }
}

function Find-BuildEipsOnPath {
    foreach ($commandName in @("build-eips", "build-eips.exe")) {
        $commands = @(Get-Command -Name $commandName -CommandType Application -ErrorAction SilentlyContinue)
        if ($commands.Count -gt 0) {
            return $commands[0].Source
        }
    }

    return $null
}

function Assert-InstallDirWritable {
    param([string]$InstallDir)

    $probePath = $null

    try {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
        $probeName = ".build-eips-write-test-{0}.tmp" -f ([System.Guid]::NewGuid().ToString("N"))
        $probePath = Join-Path -Path $InstallDir -ChildPath $probeName
        [System.IO.File]::WriteAllText($probePath, "")
        Remove-Item -LiteralPath $probePath -Force
        $probePath = $null
    } catch {
        Die ("install directory cannot be created or written ({0}): {1}" -f $InstallDir, $_.Exception.Message)
    } finally {
        if (($null -ne $probePath) -and (Test-Path -LiteralPath $probePath)) {
            Remove-Item -LiteralPath $probePath -Force -ErrorAction SilentlyContinue
        }
    }
}

function Install-BuildEips {
    param(
        [string]$InstallDir,
        [string]$BuildEipsPath
    )

    $releaseUrl = "https://github.com/eips-wg/preprocessor/releases/latest/download/build-eips-windows.zip"
    $tmpRoot = Join-Path -Path ([System.IO.Path]::GetTempPath()) -ChildPath ("build-eips-" + [System.Guid]::NewGuid().ToString("N"))
    $archivePath = Join-Path -Path $tmpRoot -ChildPath "build-eips-windows.zip"
    $extractDir = Join-Path -Path $tmpRoot -ChildPath "extract"

    try {
        Assert-InstallDirWritable -InstallDir $InstallDir

        New-Item -ItemType Directory -Path $extractDir -Force | Out-Null

        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

        Say "Installing build-eips from $releaseUrl"
        Invoke-WebRequest -Uri $releaseUrl -OutFile $archivePath -UseBasicParsing
        Expand-Archive -LiteralPath $archivePath -DestinationPath $extractDir -Force

        $extractedBuildEips = Join-Path -Path $extractDir -ChildPath "build-eips.exe"
        if (-not (Test-Path -LiteralPath $extractedBuildEips -PathType Leaf)) {
            Die "release archive did not contain expected build-eips.exe"
        }

        Copy-Item -LiteralPath $extractedBuildEips -Destination $BuildEipsPath -Force
        return $BuildEipsPath
    } catch {
        Die ("failed to install build-eips: {0}" -f $_.Exception.Message)
    } finally {
        if (Test-Path -LiteralPath $tmpRoot) {
            Remove-Item -LiteralPath $tmpRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

function Quote-PowerShellPath {
    param([string]$Path)

    return "'{0}'" -f ($Path -replace "'", "''")
}

if ([string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
    Die "LOCALAPPDATA is not set; cannot determine the user-local install directory"
}

$PathNote = $null

$ScriptDir = (Resolve-Path -LiteralPath $PSScriptRoot).ProviderPath
$RepoRoot = (Resolve-Path -LiteralPath (Split-Path -Path $ScriptDir -Parent)).ProviderPath
$WorkspaceRoot = (Resolve-Path -LiteralPath (Split-Path -Path $RepoRoot -Parent)).ProviderPath
$DefaultInstallDir = Join-Path -Path (Join-Path -Path $env:LOCALAPPDATA -ChildPath "build-eips") -ChildPath "bin"
$DefaultBuildEipsPath = Join-Path -Path $DefaultInstallDir -ChildPath "build-eips.exe"

Say "Active proposal repo: $RepoRoot"
Say "Workspace root: $WorkspaceRoot"
Say "If PowerShell blocks this script, run:"
Say "  powershell -ExecutionPolicy Bypass -File .\scripts\dev-setup.ps1"

$BuildEipsPath = Find-BuildEipsOnPath
if ($null -ne $BuildEipsPath) {
    Say "Using existing build-eips at $BuildEipsPath"
} elseif (Test-Path -LiteralPath $DefaultBuildEipsPath -PathType Leaf) {
    $BuildEipsPath = $DefaultBuildEipsPath
    Add-DefaultBinToSessionPath -InstallDir $DefaultInstallDir
    Say "Using existing build-eips at $BuildEipsPath"
} else {
    $BuildEipsPath = Install-BuildEips -InstallDir $DefaultInstallDir -BuildEipsPath $DefaultBuildEipsPath
    Add-DefaultBinToSessionPath -InstallDir $DefaultInstallDir
}

Say "Bootstrapping workspace at $WorkspaceRoot"
& $BuildEipsPath -C $RepoRoot workspace init $WorkspaceRoot --template --platform-dev
$WorkspaceInitExitCode = $LASTEXITCODE
if ($WorkspaceInitExitCode -ne 0) {
    Die "workspace init failed with exit code $WorkspaceInitExitCode"
}

Say "Running workspace doctor"
& $BuildEipsPath -C $RepoRoot workspace doctor
$WorkspaceDoctorExitCode = $LASTEXITCODE
if ($WorkspaceDoctorExitCode -ne 0) {
    Say "Warning: workspace doctor reported issues above. Fix them before relying on direct build-eips commands."
}

$WorkspaceDocPath = Join-Path -Path $WorkspaceRoot -ChildPath "WORKSPACE.md"
Say ""
if (Test-Path -LiteralPath $WorkspaceDocPath -PathType Leaf) {
    Say "Workspace docs: $WorkspaceDocPath (../WORKSPACE.md from this repo)"
} else {
    Say "Warning: workspace docs were not found at $WorkspaceDocPath after workspace init"
}

if ($null -ne $PathNote) {
    Say ""
    Say 'Current session $env:Path was updated with:'
    Say "  $PathNote"
    Say "To make this permanent, add that directory to your user Path in Windows Environment Variables."
}

Say ""
Say "Next commands:"
Say ("  cd {0}" -f (Quote-PowerShellPath -Path $RepoRoot))
Say "  build-eips serve"
Say "  build-eips check"
Say "  build-eips workspace doctor"
