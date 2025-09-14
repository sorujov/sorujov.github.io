# PowerShell Script to Create New Mathematical Statistics Lecture
# Usage: ./new-lecture.ps1 02 "probability-theory" "Probability Theory and Axioms"

param(
    [Parameter(Mandatory=$true)]
    [string]$LectureNumber,
    
    [Parameter(Mandatory=$true)]
    [string]$TopicSlug,
    
    [Parameter(Mandatory=$true)]
    [string]$TopicTitle
)

# Set up paths
$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$lecturesPath = Join-Path $rootPath "lectures\math-stat-1"
$templatePath = Join-Path $lecturesPath "_template"
$newLecturePath = Join-Path $lecturesPath "$LectureNumber-$TopicSlug"

# Validate inputs
if ($LectureNumber -notmatch '^\d{2}$') {
    Write-Error "Lecture number must be two digits (e.g., '02', '03')"
    exit 1
}

if (Test-Path $newLecturePath) {
    Write-Error "Lecture directory already exists: $newLecturePath"
    exit 1
}

# Create new lecture directory
Write-Host "Creating new lecture directory: $newLecturePath"
New-Item -ItemType Directory -Path $newLecturePath -Force

# Copy template files
Write-Host "Copying template files..."
Copy-Item -Path "$templatePath\*" -Destination $newLecturePath -Recurse

# Update HTML title
$htmlPath = Join-Path $newLecturePath "index.html"
$htmlContent = Get-Content $htmlPath -Raw
$htmlContent = $htmlContent -replace "Combinatorial Analysis: The Art of Counting", $TopicTitle
$htmlContent = $htmlContent -replace '<h1 class="main-title">Combinatorial Analysis</h1>', "<h1 class=`"main-title`">$TopicTitle</h1>"
Set-Content -Path $htmlPath -Value $htmlContent

Write-Host ""
Write-Host "✅ New lecture created successfully!"
Write-Host ""
Write-Host "📁 Location: lectures/math-stat-1/$LectureNumber-$TopicSlug/"
Write-Host "🌐 URL: /lectures/math-stat-1/$LectureNumber-$TopicSlug/index.html"
Write-Host ""
Write-Host "📝 Next steps:"
Write-Host "1. Edit index.html to add your lecture content"
Write-Host "2. Update app.js with your interactive elements"
Write-Host "3. Update _pages/math-stat-1-lectures.md to add the new lecture"
Write-Host "4. Test the lecture locally"
Write-Host "5. Commit and push: git add -A && git commit -m 'Add Lecture $LectureNumber: $TopicTitle' && git push"
Write-Host ""