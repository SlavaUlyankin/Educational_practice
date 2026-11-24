param([Parameter(Mandatory=$true)][string]$InputDocx,[Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open((Resolve-Path -LiteralPath $InputDocx).Path, $false, $false)
    $document.Repaginate()
    foreach ($table in $document.TablesOfContents) { $table.Update() }
    $document.Repaginate()
    foreach ($table in $document.TablesOfContents) { $table.UpdatePageNumbers() }
    $document.Save()
    $document.ExportAsFixedFormat([System.IO.Path]::GetFullPath($OutputPdf), 17)
    Write-Output "Updated $($document.TablesOfContents.Count) table(s) of contents and exported PDF"
}
finally {
    if ($null -ne $document) { $document.Close(0) }
    if ($null -ne $word) { $word.Quit() }
}
