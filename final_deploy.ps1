Write-Host "Starting final render and export of all 16 notebooks..."
& .\.venv\Scripts\python.exe run_and_export_all.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "Export completed successfully. Committing to git..."
    git add .
    git commit -m "TDK v1.2: Complete variable dictionary (NB00), Railway zone clarification (NB04), Unified Hedonics (NB05/07), GWR Map & Subplots (NB10), ML Widget & Scenario matrix (NB11), Executive Master Dashboard (NB15)"
    git push
    Write-Host "Successfully pushed to GitHub Pages!"
} else {
    Write-Host "Export failed with exit code $LASTEXITCODE"
}
