@echo off
setlocal EnableExtensions
rem ==========================================================================
rem  push_ict_page.bat
rem  Adds, commits and pushes the "Internet in the CIS region" page
rem  (/portfolio/cis-internet/) and its data pipeline to GitHub.
rem
rem  Only the files belonging to that page are staged, so anything else you
rem  have changed in the repository is left alone.
rem  Double-click it, or run it from any folder: it moves to its own folder.
rem ==========================================================================

cd /d "%~dp0"

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

rem --- The monthly job file ------------------------------------------------
rem  Claude cannot write into .github, so the newest copy is looked for in
rem  "Claude outputs" (this repo) and then in Downloads, and copied into place
rem  whenever it differs from the one already there.
set "WF=.github\workflows\update-ict-data.yml"
set "SRC="
if exist "Claude outputs\update-ict-data.yml" set "SRC=Claude outputs\update-ict-data.yml"
if not defined SRC if exist "%USERPROFILE%\Downloads\update-ict-data.yml" set "SRC=%USERPROFILE%\Downloads\update-ict-data.yml"
if defined SRC (
    if not exist ".github\workflows" mkdir ".github\workflows"
    fc /b "%SRC%" "%WF%" >nul 2>&1
    if errorlevel 1 (
        copy /y "%SRC%" "%WF%" >nul
        echo Updated %WF% from "%SRC%"
    ) else (
        echo %WF% is already the newest version.
    )
) else (
    if not exist "%WF%" (
        echo [WARNING] %WF% is missing and no copy was found in
        echo           "Claude outputs" or Downloads.
        choice /c YN /m "Push the page without the monthly job"
        if errorlevel 2 goto :cancel
    )
)

rem --- Stage only the files that belong to the ICT page ---
set PATHS=_config.yml assets/css/main.scss _portfolio/cis-internet.md _sass/layout/_ict.scss assets/js/ict-data.js assets/data/ict data-pipeline/ict
if exist "%WF%" set PATHS=%PATHS% .github/workflows/update-ict-data.yml

git add -- %PATHS%
if errorlevel 1 (
    echo [ERROR] git add failed.
    goto :fail
)

git diff --cached --quiet
if not errorlevel 1 (
    echo Nothing new to commit for the ICT page.
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

git commit -q -m "Update ICT data page and its monthly job" ^
 -m "Page at /portfolio/cis-internet/ (CIS speeds, forecasts, Azerbaijan by city, IPv6). The job runs on the 20th of each month: fetch, verify, rebuild JSON, refit forecasts, commit, rebuild Pages." ^
 -m "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>" ^
 -m "Claude-Session: https://claude.ai/code/session_013KB7rVfW4UhRvTkm2vRSqt"
if errorlevel 1 (
    echo [ERROR] git commit failed.
    goto :fail
)
echo Committed.

:push
rem The ORCID job commits to master every day, so bring those commits in first.
echo.
echo Pulling the latest master from GitHub ...
git pull --rebase --autostash origin %BRANCH%
if errorlevel 1 (
    echo [ERROR] Pull failed. Resolve the conflict, then run: git rebase --continue
    echo         and push with: git push origin %BRANCH%
    goto :fail
)

echo Pushing ...
git push origin %BRANCH%
if errorlevel 1 (
    echo [ERROR] Push failed. If GitHub mentions "workflow" scope, your token
    echo         is not allowed to push files under .github\workflows.
    echo         Sign in again with: git credential-manager github login
    goto :fail
)

echo.
echo Done. GitHub Pages usually republishes within a few minutes:
echo   https://sorujov.net/portfolio/cis-internet/
echo To fill the data straight away, open the repository on GitHub, go to
echo Actions, choose "Update ICT data" and press "Run workflow".
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
