# RC-55: bounded RRECollector v0.4.19-only deployment to LEGION's verified OneDrive AddOns root.
# Preflight by default. Use -Deploy after strict source package validation.
param([switch]$Deploy)
$ErrorActionPreference = "Stop"
if ([Environment]::MachineName -ne "LEGION") { throw "WRONG_MACHINE: only LEGION is authorized" }
$repo = Split-Path -Parent $PSScriptRoot
$source = Join-Path $repo "addons\RRECollector"
$target = Join-Path ([Environment]::GetFolderPath("UserProfile")) "OneDrive\Documents\Rift\Interface\AddOns\RRECollector"
$names = @("core.lua", "context.lua", "abilities.lua", "capabilities.lua",
    "candidate_catalog.lua", "candidates.lua", "wire.lua", "ui.lua", "main.lua",
    "README.md", "RiftAddon.toc")
if ((Split-Path -Leaf $target) -ne "RRECollector" -or
    (Split-Path -Leaf (Split-Path -Parent $target)) -ne "AddOns") {
    throw "INVALID_ADDON_TARGET"
}
if (-not (Test-Path -LiteralPath $source -PathType Container) -or
    -not (Test-Path -LiteralPath $target -PathType Container)) {
    throw "MISSING_ADDON_DIRECTORY: source=$source target=$target"
}
foreach ($name in $names) {
    if (-not (Test-Path -LiteralPath (Join-Path $source $name) -PathType Leaf) -or
        -not (Test-Path -LiteralPath (Join-Path $target $name) -PathType Leaf)) {
        throw "MISSING_EXPECTED_FILE: $name"
    }
}
$installedToc = [IO.File]::ReadAllText((Join-Path $target "RiftAddon.toc"))
$sourceToc = [IO.File]::ReadAllText((Join-Path $source "RiftAddon.toc"))
if ($installedToc -notmatch 'Version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"') { throw "INVALID_INSTALLED_VERSION" }
$oldVersion = $Matches[1]
if ($sourceToc -notmatch 'Version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"') { throw "INVALID_SOURCE_VERSION" }
$newVersion = $Matches[1]
Write-Output "Machine=LEGION; target=$target; installed=$oldVersion; source=$newVersion; files=$($names.Count)"
if ($newVersion -ne "0.4.19") { throw "UNEXPECTED_RELEASE_VERSION: $newVersion" }
# Enforce the strict manifest, source-version, module-order and package checks
# in both preflight and deploy modes; a successful copy alone is not a load proof.
$gateOutput = & node.exe (Join-Path $repo "tools\verify-rrecollector-package.mjs") 2>&1
if ($LASTEXITCODE -ne 0) { throw "SOURCE_PACKAGE_GATE_FAILED: $gateOutput" }
Write-Output "SOURCE_PACKAGE_VERIFIED=$newVersion"
if (-not $Deploy) { Write-Output "PREFLIGHT_OK_NO_FILES_CHANGED"; exit 0 }
$backup = Join-Path $repo ("artifacts\RRECollector-installed-v" + ($oldVersion -replace '\.', '') +
    "-LEGION-" + (Get-Date -Format "yyyyMMdd-HHmmss-fff"))
[void](New-Item -ItemType Directory -Path $backup -ErrorAction Stop)
$priorHashes = @{}
$releaseHashes = @{}
foreach ($name in $names) {
    $installedFile = Join-Path $target $name
    $sourceFile = Join-Path $source $name
    $priorHashes[$name] = (Get-FileHash -LiteralPath $installedFile -Algorithm SHA256).Hash.ToLowerInvariant()
    $releaseHashes[$name] = (Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash.ToLowerInvariant()
    Copy-Item -LiteralPath $installedFile -Destination (Join-Path $backup $name) -ErrorAction Stop
    $backupHash = (Get-FileHash -LiteralPath (Join-Path $backup $name) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($backupHash -ne $priorHashes[$name]) { throw "BACKUP_MISMATCH: $name" }
}
Write-Output "BACKUP_VERIFIED=$backup; files=$($names.Count)"
$changed = @()
try {
    # The manifest is last so the game never sees a new TOC before new source files.
    foreach ($name in $names) {
        Copy-Item -LiteralPath (Join-Path $source $name) -Destination (Join-Path $target $name) -Force -ErrorAction Stop
        $actual = (Get-FileHash -LiteralPath (Join-Path $target $name) -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $releaseHashes[$name]) { throw "INSTALL_MISMATCH: $name" }
        $changed += $name
    }
} catch {
    $deploymentError = $_
    foreach ($name in $names) {
        Copy-Item -LiteralPath (Join-Path $backup $name) -Destination (Join-Path $target $name) -Force -ErrorAction Stop
        $restored = (Get-FileHash -LiteralPath (Join-Path $target $name) -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($restored -ne $priorHashes[$name]) { throw "ROLLBACK_FAILED: $name; initial error=$deploymentError" }
    }
    throw "INSTALL_FAILED_AND_BACKUP_RESTORED: $deploymentError"
}
$receipt = [ordered]@{ machine="LEGION"; release=$newVersion; previous=$oldVersion;
    destination=$target; backup=$backup; installedFiles=$changed; sourceHashes=$releaseHashes;
    installedParity=$true; runtimeUiVerified=$false; generatedAtUtc=[DateTime]::UtcNow.ToString("o") }
$receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $backup "deployment-receipt.json") -Encoding UTF8
Write-Output "INSTALLED_VERIFIED=$newVersion; files=$($changed.Count); runtimeUiVerified=false"
