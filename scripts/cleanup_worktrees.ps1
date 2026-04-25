param(
  [switch]$Remove
)

$root = (Get-Location).Path
$pattern = 'monitor_worktree_*'
Write-Output "Scanning for worktrees named $pattern under $root"
$found = Get-ChildItem -Path $root -Directory -Filter $pattern -ErrorAction SilentlyContinue
if (-not $found) {
  Write-Output "No matching worktrees found under $root"
  exit 0
}

foreach ($d in $found) {
  Write-Output "Found: $($d.FullName)"
  if ($Remove) {
    Write-Output "Removing git worktree: $($d.FullName)"
    git worktree remove $d.FullName 2>$null
    if (Test-Path $d.FullName) {
      Remove-Item -Recurse -Force $d.FullName
      Write-Output "Deleted directory: $($d.FullName)"
    }
  } else {
    Write-Output "Run this script with -Remove to actually remove the listed worktrees."
  }
}
