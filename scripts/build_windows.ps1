param(
    [string]$DistPath = "dist\windows",
    [string]$WorkPath = "build\pyinstaller"
)

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."

Write-Host "Building ced executable to $DistPath" -ForegroundColor Cyan

python -m PyInstaller "$ProjectRoot\ced.spec" `
    --distpath "$DistPath" `
    --workpath "$WorkPath" `
    --clean `
    --noconfirm

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Build completed successfully!" -ForegroundColor Green
    Write-Host "Executable located at: $DistPath\ced\" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ Build failed." -ForegroundColor Red
    exit $LASTEXITCODE
}
