# RRE shared offline RIFT executable update analyzer.
# Never launches, controls, modifies or updates RIFT; creates a new reports directory only.
[CmdletBinding()]
param(
    [string]$BaselinePath = 'C:\work\RIFT-Build-Baselines\1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8\rift_x64.exe',
    [string]$CurrentPath = 'C:\Program Files (x86)\Glyph\Games\RIFT\Live\rift_x64.exe',
    [string]$PythonExecutable = 'C:\Python314\python.exe',
    [string]$ExpectedBaselineSha256 = '1935a05c9db6d468e34e0055014a4a99c1b5afceb1695884e24600f5c20a4be8',
    [string]$AnchorManifest = '',
    [string]$ReportDirectory = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

try {
    $scriptPath = Join-Path $PSScriptRoot 'rift_update_analyzer.py'
    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
        throw "Missing analyzer: $scriptPath"
    }
    if (-not (Test-Path -LiteralPath $PythonExecutable -PathType Leaf)) {
        throw "Python executable missing: $PythonExecutable. Supply -PythonExecutable explicitly."
    }
    if (-not (Test-Path -LiteralPath $BaselinePath -PathType Leaf)) {
        throw "Baseline executable missing: $BaselinePath"
    }
    if (-not (Test-Path -LiteralPath $CurrentPath -PathType Leaf)) {
        throw "Current executable missing: $CurrentPath"
    }
    if ([string]::IsNullOrWhiteSpace($AnchorManifest)) {
        $AnchorManifest = Join-Path $PSScriptRoot 'rift_update_anchors.json'
    }
    if (-not (Test-Path -LiteralPath $AnchorManifest -PathType Leaf)) {
        throw "SHA-pinned anchor manifest missing: $AnchorManifest"
    }
    if ([string]::IsNullOrWhiteSpace($ReportDirectory)) {
        $root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
        $suffix = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss') + '-' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
        $ReportDirectory = Join-Path $root ("artifacts\rift-update-analyzer-" + $suffix)
    }
    [Console]::WriteLine('HOST=' + [Environment]::MachineName)
    [Console]::WriteLine('REPORT_DIR=' + $ReportDirectory)
    $cliArgs = @(
        '-B', $scriptPath,
        '--before', $BaselinePath,
        '--after', $CurrentPath,
        '--output-dir', $ReportDirectory,
        '--expected-before-sha', $ExpectedBaselineSha256,
        '--anchors', $AnchorManifest
    )
    & $PythonExecutable @cliArgs
    $result = $LASTEXITCODE
    if ($result -notin @(0, 2, 3)) {
        [Console]::Error.WriteLine("Unexpected analyzer exit $result; treating as inspection ERROR")
        exit 3
    }
    exit $result
}
catch {
    [Console]::Error.WriteLine("RRE update analyzer ERROR: " + $_.Exception.Message)
    exit 3
}
