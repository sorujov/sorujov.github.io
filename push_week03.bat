@echo off
setlocal EnableExtensions
rem ==========================================================================
rem  push_week03.bat
rem  Adds, commits and pushes week 3's two lecture decks and the course-page
rem  row that links to them.
rem
rem  Only those files are staged, so anything else you have changed in the
rem  repository is left alone. Double-click it, or run it from any folder:
rem  it moves to its own folder.
rem
rem  For week 4, copy this file and change the six SET lines below. Nothing
rem  else in it is week-specific.
rem
rem  The WeBWorK sets are NOT pushed and cannot be: useful_skills\ is in
rem  .gitignore, which is deliberate -- the problems and their answer keys do
rem  not belong on a public GitHub Pages site.
rem ==========================================================================

cd /d "%~dp0"

set "LECTDIR=lectures\math-stat-1-fall-2026"
set "DECK1=05-conditional-probability\conditional_probability_lecture5"
set "DECK2=06-two-laws-of-probability\two_laws_of_probability_lecture6"
set "PDF1=05-conditional-probability\week03ps1-practice.pdf"
set "PDF2=06-two-laws-of-probability\week03ps2-practice.pdf"
set "COURSEPAGE=_teaching\2026-fall-mathematical-statistics-I.md"

where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] git is not installed or not on PATH.
    goto :fail
)

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo [ERROR] %CD% is not a git repository.
    goto :fail
)

for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set "BRANCH=%%b"
echo Repository : %CD%
echo Branch     : %BRANCH%
if /i not "%BRANCH%"=="master" (
    echo [WARNING] You are not on master. GitHub Pages publishes from master.
    choice /c YN /m "Continue on %BRANCH% anyway"
    if errorlevel 2 goto :cancel
)
echo.

rem --- Has the deck actually been rendered? --------------------------------
rem  The .qmd alone is not a deck. Pushing it without its HTML leaves the
rem  Slides pill on the course page pointing at a 404 in front of three
rem  sections, so this is a stop, not a warning.
set "MISSING="
if not exist "%LECTDIR%\%DECK1%.html" set "MISSING=%MISSING% %DECK1%.html"
if not exist "%LECTDIR%\%DECK2%.html" set "MISSING=%MISSING% %DECK2%.html"
if not exist "%LECTDIR%\%DECK1%_files" set "MISSING=%MISSING% %DECK1%_files\"
if not exist "%LECTDIR%\%DECK2%_files" set "MISSING=%MISSING% %DECK2%_files\"
if defined MISSING (
    echo [ERROR] These have not been rendered yet:
    for %%m in (%MISSING%) do echo           %%m
    echo.
    echo         Render both decks first:
    echo           quarto render "%LECTDIR%\%DECK1%.qmd" --to revealjs
    echo           quarto render "%LECTDIR%\%DECK2%.qmd" --to revealjs
    goto :fail
)

rem --- Sweep the stale hashed theme stylesheets ----------------------------
rem  Every edit to slide-fit.scss makes Quarto emit a new hashed stylesheet
rem  and leave the previous one behind. Keep only the one the HTML references;
rem  the rest are untracked junk that would otherwise be committed.
echo Sweeping stale theme stylesheets ...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop';" ^
  "foreach ($d in @('%DECK1%','%DECK2%')) {" ^
  "  $html = Join-Path '%LECTDIR%' ($d + '.html');" ^
  "  $dir  = Join-Path '%LECTDIR%' ($d + '_files\libs\revealjs\dist\theme');" ^
  "  if (-not (Test-Path $dir)) { continue }" ^
  "  $keep = [regex]::Matches((Get-Content $html -Raw), 'quarto-[0-9a-f]{32}\.css') | ForEach-Object { $_.Value } | Sort-Object -Unique;" ^
  "  if (-not $keep) { Write-Host ('  no hashed theme referenced by ' + $d + '.html - left alone'); continue }" ^
  "  Get-ChildItem $dir -Filter 'quarto-*.css' | Where-Object { $keep -notcontains $_.Name } | ForEach-Object { Remove-Item $_.FullName; Write-Host ('  removed ' + $_.Name) }" ^
  "}"
if errorlevel 1 (
    echo [WARNING] The stylesheet sweep did not finish. Check for orphans with
    echo           git status before you answer the prompt below.
)
echo.

rem --- Are the practice PDFs there? ----------------------------------------
rem  These are what the Problems pill on the course page points at. Without
rem  them the decks are still worth pushing; the course page is not.
set "PUSHPAGE=1"
if not exist "%LECTDIR%\%PDF1%" set "PUSHPAGE=0"
if not exist "%LECTDIR%\%PDF2%" set "PUSHPAGE=0"
if "%PUSHPAGE%"=="0" (
    echo [WARNING] One or both practice PDFs are missing:
    echo             %LECTDIR%\%PDF1%
    echo             %LECTDIR%\%PDF2%
    echo           The course page's "Problems" pills would 404, so the course
    echo           page will be left out of this push. Export them with
    echo           export_pdf.py --no-solutions and run this again to add it.
    echo.
)

rem --- Stage only what belongs to week 3 -----------------------------------
set PATHS="%LECTDIR%/05-conditional-probability" "%LECTDIR%/06-two-laws-of-probability"
if "%PUSHPAGE%"=="1" set PATHS=%PATHS% "%COURSEPAGE%"

git add -- %PATHS%
if errorlevel 1 (
    echo [ERROR] git add failed.
    goto :fail
)

git diff --cached --quiet
if not errorlevel 1 (
    echo Nothing new to commit for week 3.
    goto :push
)

echo Files to be committed:
git diff --cached --stat
echo.
choice /c YN /m "Commit and push these files"
if errorlevel 2 (
    git reset -q -- %PATHS%
    goto :cancel
)

git commit -q -m "Add week 3 lectures: conditional probability and the two laws" ^
 -m "Lecture 5 (23 September, Wackerly 2.7) on conditional probability and the independence of events, and lecture 6 (26 September, Wackerly 2.8) on the multiplicative and additive laws. Both decks carry an executing R chunk, an OJS explorable, the think-pair-share timer and four quiz questions." ^
 -m "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>" ^
 -m "Claude-Session: https://claude.ai/code/session_015tmcBvdeeRMPaazGN8io9n"
if errorlevel 1 (
    echo [ERROR] git commit failed.
    goto :fail
)
echo Committed.

:push
rem The ORCID job commits to master every day, so bring those commits in first.
echo.
echo Pulling the latest %BRANCH% from GitHub ...
git pull --rebase --autostash origin %BRANCH%
if errorlevel 1 (
    echo [ERROR] Pull failed. Resolve the conflict, then run: git rebase --continue
    echo         and push with: git push origin %BRANCH%
    goto :fail
)

echo Pushing ...
git push origin %BRANCH%
if errorlevel 1 (
    echo [ERROR] Push failed.
    goto :fail
)

echo.
echo Done. GitHub Pages usually republishes within a few minutes:
echo   https://sorujov.net/lectures/math-stat-1-fall-2026/%DECK1:\=/%.html
echo   https://sorujov.net/lectures/math-stat-1-fall-2026/%DECK2:\=/%.html
echo.
echo Open one of them and move a slider before Wednesday. A deck that works on
echo loopback can still be broken by the site build.
if "%PUSHPAGE%"=="0" (
    echo.
    echo The course page was NOT pushed, because the practice PDFs are missing.
)
goto :end

:cancel
echo Cancelled. Nothing was pushed.
goto :end

:fail
echo.
echo Stopped because of the error above.

:end
echo.
pause
endlocal
