# Compile all .tex files in this folder to PDF then SVG.
# Requires: MiKTeX (pdflatex) + pdftocairo (ships with MiKTeX).
# Output PDFs land in this folder; SVGs go to ../generated/.

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$out  = Join-Path (Split-Path $root -Parent) 'generated'
New-Item -ItemType Directory -Force -Path $out | Out-Null

Get-ChildItem -Path $root -Filter '*.tex' | ForEach-Object {
    $name = $_.BaseName
    Write-Host "==> $name"
    Push-Location $root
    & pdflatex -interaction=nonstopmode -halt-on-error "$name.tex" *> "$name.buildlog"
    Pop-Location

    if (Test-Path (Join-Path $root "$name.pdf")) {
        & pdftocairo -svg (Join-Path $root "$name.pdf") (Join-Path $out "$name.svg")
        Write-Host "    OK -> $out\$name.svg"
    } else {
        Write-Warning "    FAILED — see $name.buildlog"
    }
}

# Tidy aux files
Get-ChildItem -Path $root -Include *.aux,*.log,*.buildlog -Recurse | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "Done."
