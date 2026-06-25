# Full build pipeline for CertifiedTestApplication (Linux x64)
# Usage: .\build.ps1 [-Clean] [-Build] [-Bundle]
#   With no params: runs all steps in order
param(
    [switch]$Clean,
    [switch]$Build,
    [switch]$Bundle
)

$ErrorActionPreference = "Stop"

$basePath = "C:\git\CertifiedTestApplication"
$runtime = "linux-x64"
$appName = "CertifiedTestApplication"
$releaseDir = "$basePath\release\$runtime"
$csprojPath = "$basePath\$appName.csproj"

# Run all if no switches
$runAll = -not $Clean -and -not $Build -and -not $Bundle

# --- 1. Clean ---
if ($runAll -or $Clean) {
    Write-Host "`n=== CLEAN ===" -ForegroundColor Cyan
    $cleanPaths = @(
        "$basePath\release"
        "$basePath\admin\cta.zip"
    )

    foreach ($path in $cleanPaths) {
        if (Test-Path $path) {
            if (Test-Path $path -PathType Container) {
                Remove-Item "$path\*" -Recurse -Force -ErrorAction SilentlyContinue
            } else {
                Remove-Item $path -Force -ErrorAction SilentlyContinue
            }
            Write-Host "clean: $path" -ForegroundColor Green
        }
    }
}

# --- 2. Build + ZIP app binary ---
if ($runAll -or $Build) {
    Write-Host "`n=== BUILD $runtime ===" -ForegroundColor Cyan

    dotnet publish $csprojPath -c Release -r $runtime --self-contained true `
        -p:PublishSingleFile=true -p:EnableCompressionInSingleFile=true `
        -o $releaseDir

    $appZip = Join-Path $releaseDir "$appName.zip"
    if (Test-Path $appZip) { Remove-Item $appZip }

    Write-Host "Archiving $appName.zip..." -ForegroundColor Yellow

    Push-Location $releaseDir
    try {
        $filesToZip = @()
        if (Test-Path $appName) { $filesToZip += $appName }
        if (Test-Path "appsettings.json") { $filesToZip += "appsettings.json" }
        if (Test-Path "wwwroot") { $filesToZip += "wwwroot" }
        Get-ChildItem "$appName.staticwebassets.endpoints.json" -ErrorAction SilentlyContinue | ForEach-Object { $filesToZip += $_.Name }

        Add-Type -AssemblyName "System.IO.Compression.FileSystem"
        $zipArchive = [System.IO.Compression.ZipFile]::Open($appZip, "Create")

        foreach ($item in $filesToZip) {
            if (Test-Path $item -PathType Container) {
                $files = Get-ChildItem $item -Recurse
                foreach ($file in $files) {
                    if (-not $file.PSIsContainer) {
                        $relativeName = $file.FullName.Substring($releaseDir.Length + 1).Replace('\', '/')
                        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zipArchive, $file.FullName, $relativeName)
                    }
                }
            } else {
                $relativeName = $item.Replace('\', '/')
                [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zipArchive, (Join-Path $releaseDir $item), $relativeName)
            }
        }
        $zipArchive.Dispose()
    }
    finally {
        Pop-Location
    }
    Write-Host "Done: $appZip" -ForegroundColor Green
}

# --- 3. Bundle (scripts + app files) ---
if ($runAll -or $Bundle) {
    Write-Host "`n=== CREATE DEPLOY BUNDLE ===" -ForegroundColor Cyan

    $bundlePath = Join-Path $basePath "admin\cta.zip"

    $filesToInclude = @(
        "$basePath\admin\bash\install.sh",
        "$basePath\admin\bash\1_install_system.sh",
        "$basePath\admin\bash\2_update_system.sh",
        "$basePath\admin\bash\3_start_services.sh",
        "$basePath\admin\bash\4_status_services.sh",
        "$basePath\admin\bash\5_stop_services.sh"
        "$basePath\admin\bash\6_create_service.sh"
        "$basePath\admin\bash\7_setup_postgresqll.sh"
        "$basePath\admin\bash\8_check-dependencies.sh"
    )

    if (Test-Path $bundlePath) { Remove-Item $bundlePath }

    Add-Type -AssemblyName "System.IO.Compression.FileSystem"
    $zipArchive = [System.IO.Compression.ZipFile]::Open($bundlePath, "Create")

    try {
        foreach ($filePath in $filesToInclude) {
            if (Test-Path $filePath) {
                $fileName = Split-Path $filePath -Leaf
                Write-Host "Adding: $fileName" -ForegroundColor Yellow
                [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zipArchive, $filePath, $fileName)
            } else {
                Write-Warning "File not found, skipping: $filePath"
            }
        }

        $appZip = Join-Path $releaseDir "$appName.zip"
        if (Test-Path $appZip) {
            Write-Host "Adding: $appName.zip" -ForegroundColor Yellow
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zipArchive, $appZip, "$appName.zip")
        } else {
            Write-Warning "App zip not found, skipping: $appZip"
        }

        $jsonDir = Join-Path $basePath "json"
        if (Test-Path $jsonDir) {
            $tmpJsonZip = Join-Path $env:TEMP "json.zip"
            if (Test-Path $tmpJsonZip) { Remove-Item $tmpJsonZip }
            [System.IO.Compression.ZipFile]::CreateFromDirectory($jsonDir, $tmpJsonZip)
            Write-Host "Adding: json.zip" -ForegroundColor Yellow
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zipArchive, $tmpJsonZip, "json.zip")
            Remove-Item $tmpJsonZip
        } else {
            Write-Warning "json folder not found, skipping"
        }
    }
    finally {
        $zipArchive.Dispose()
    }

    Write-Host "`nBundle created: $bundlePath" -ForegroundColor Green
    Write-Host "Copy to server with: scp $bundlePath root@server:/tmp/" -ForegroundColor Gray
}
