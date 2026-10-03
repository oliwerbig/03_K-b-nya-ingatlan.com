Write-Host "Starting final render and export..."
& .\.venv\Scripts\python.exe run_and_export_all.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "Export completed successfully. Committing to git..."
    git add .
    git commit -m "Phase 5 Complete: Full 100% TDK Optionals implemented with bugfixes"
    git push
    Write-Host "Successfully pushed to GitHub Pages!"
} else {
    Write-Host "Export failed with exit code $LASTEXITCODE"
}
