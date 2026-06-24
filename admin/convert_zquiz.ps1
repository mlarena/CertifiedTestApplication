# Convert zquiz txt files to JSON format for CertifiedTestApplication
$ErrorActionPreference = "Stop"

$basePath = "C:\git\CertifiedTestApplication"
$quizDir = "$basePath\zquiz"
$outputDir = "$basePath\json"

$files = Get-ChildItem "$quizDir\*.txt" | Sort-Object { [int]($_.BaseName -replace 'z_','') }

foreach ($file in $files) {
    Write-Host "Processing: $($file.Name)" -ForegroundColor Cyan

    $lines = Get-Content $file.FullName -Encoding UTF8
    $title = $lines[0].Trim()

    # Pre-process: remove replacement blocks (lines with "ЗАМЕНА" and following question)
    $cleanLines = @()
    $skipCount = 0
    foreach ($line in $lines) {
        if ($skipCount -gt 0) {
            $skipCount--
            continue
        }
        $trimmed = $line.Trim()
        if ($trimmed -match '^\d+\.\s' -and $trimmed.Contains([char]0x0417)) {
            # Replacement question marker like "31. ЗАМЕНА..."
            $skipCount = 7  # skip marker + question + 4 answers + correct answer + blank
            continue
        }
        if ($trimmed.StartsWith([string]([char]0x0417) + [string]([char]0x0410) + [string]([char]0x041c) + [string]([char]0x0415) + [string]([char]0x041d) + [string]([char]0x0410))) {
            # Standalone "ЗАМЕНА ВОПРОСА" line
            $skipCount = 7
            continue
        }
        $cleanLines += $line
    }

    $questions = @()
    $qNum = 0

    $i = 1
    while ($i -lt $cleanLines.Count) {
        $line = $cleanLines[$i].Trim()

        if ($line -eq '') { $i++; continue }

        # Match question: "N. Question text"
        if ($line -match '^\d+\.\s+(.+)') {
            $qNum++
            $questionText = $matches[1].Trim()
            $answers = @()
            $correctLetters = @()
            $i++

            while ($i -lt $cleanLines.Count) {
                $aline = $cleanLines[$i].Trim()
                if ($aline -match '^([a-d])\)\s+(.+)') {
                    $letter = $matches[1]
                    $answerText = $matches[2].Trim()
                    $answers += @{ Text = $answerText; Letter = $letter; IsCorrect = $false }
                    $i++
                }
                elseif ($aline.Contains(':')) {
                    $answerPart = $aline.Substring($aline.IndexOf(':') + 1).Trim()
                    if ($answerPart -match '^([a-d](?:\s*,\s*[a-d])*)') {
                        $correctLetters = $matches[1] -split '\s*,\s*'
                        $i++
                        break
                    }
                    else {
                        $i++
                    }
                }
                else {
                    $i++
                }
            }

            foreach ($ans in $answers) {
                if ($correctLetters -contains $ans.Letter) {
                    $ans.IsCorrect = $true
                }
            }

            $correctCount = ($answers | Where-Object { $_.IsCorrect }).Count
            if ($correctCount -gt 1) { $qType = 2 } else { $qType = 1 }

            $questions += @{
                Text = $questionText
                Type = $qType
                Order = $qNum
                Answers = @($answers | ForEach-Object {
                    @{
                        Text = $_.Text
                        IsCorrect = $_.IsCorrect
                        NumericValue = $null
                    }
                })
            }
        }
        else {
            $i++
        }
    }

    $test = @{
        Title = $title
        Description = ""
        TimeLimit = 600
        CanReturnToQuestion = $true
        Questions = $questions
    }

    $jsonFileName = $file.BaseName + ".json"
    $jsonPath = Join-Path $outputDir $jsonFileName
    $json = $test | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($jsonPath, $json, [System.Text.Encoding]::UTF8)

    Write-Host "  -> $jsonFileName ($($questions.Count) questions)" -ForegroundColor Green
}

Write-Host "`nDone! Created $($files.Count) JSON files in $outputDir" -ForegroundColor Cyan
