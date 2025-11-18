param([string]$Root,[int]$MinImageMB=5,[switch]$Apply)
$ErrorActionPreference='SilentlyContinue'
if(-not $Root -or $Root -eq ''){$Root=Split-Path -LiteralPath $PSCommandPath -Parent | Split-Path -Parent}
$Root=($Root -replace '\"','').Trim();try{$Root=[IO.Path]::GetFullPath($Root)}catch{}
$apply=$Apply.IsPresent
if($Root -match '\s-Apply(?::\$true|\s|$)'){$Root=($Root -replace '\s-Apply(?::\$true|\s|$)','').Trim();$apply=$true}
$mode=if($apply){"APPLY (DELETE)"}else{"DRY-RUN (PREVIEW DELETE)"}
Write-Host "";Write-Host "=== Polar Ninja One-Click PRUNE ===";Write-Host ("Root : "+$Root);Write-Host ("Mode : "+$mode);Write-Host ""
function Get-Size($p){if(-not(Test-Path $p)){return 0};try{(Get-ChildItem -LiteralPath $p -Recurse -File|Measure-Object Length -Sum).Sum}catch{0}}
function Human($b){if($b -lt 1KB){"{0:N0} B" -f $b}elseif($b -lt 1MB){"{0:N2} KB" -f ($b/1KB)}elseif($b -lt 1GB){"{0:N2} MB" -f ($b/1MB)}else{"{0:N2} GB" -f ($b/1GB)}}
function DelDir($p){if(-not(Test-Path $p)){return 0};$sz=Get-Size $p;if($apply){Write-Host ("  delete "+$p);try{Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction SilentlyContinue}catch{}}else{Write-Host ("  [DRY] delete "+$p+"  ("+(Human $sz)+")")};$sz}
function DelFile($f){if(-not(Test-Path $f -PathType Leaf)){return 0};$sz=(Get-Item -LiteralPath $f).Length;if($apply){Write-Host ("  delete "+$f);try{Remove-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue}catch{}}else{Write-Host ("  [DRY] delete "+$f+"  ("+(Human $sz)+")")};$sz}
function DelPat($root,$pat){$t=0;Get-ChildItem -LiteralPath $root -Recurse -Directory -Force -ErrorAction SilentlyContinue|?{$_.Name -like $pat}|%{$t+=(DelDir $_.FullName)};$t}
$logDir=Join-Path $Root "logs\cleanup_reports";New-Item -ItemType Directory -Force -Path $logDir|Out-Null;$stamp=Get-Date -Format "yyyyMMdd-HHmmss";$log=Join-Path $logDir ("PRUNE_"+$stamp+".txt")
"PRUNE @ $(Get-Date) Mode="+$mode|Out-File -LiteralPath $log -Encoding UTF8;$pre=Get-Size $Root;Add-Content -LiteralPath $log -Value ("PRE size: "+(Human $pre))
$freed=0;$freed+=DelDir (Join-Path $Root "venv");$freed+=DelDir (Join-Path $Root ".venv");$freed+=DelDir (Join-Path $Root "dist");$freed+=DelDir (Join-Path $Root "build")
$freed+=DelPat $Root "__pycache__";$freed+=DelPat $Root ".pytest_cache";$freed+=DelPat $Root ".mypy_cache";$freed+=DelDir (Join-Path (Join-Path $Root "assets") "archive")
$assets=Join-Path $Root "assets";$min=$MinImageMB*1MB
if(Test-Path $assets){Get-ChildItem -LiteralPath $assets -Recurse -File -Filter *.wav -ErrorAction SilentlyContinue|%{$freed+=(DelFile $_.FullName)}
Get-ChildItem -LiteralPath $assets -Recurse -File -Include *.png,*.jpg,*.jpeg -ErrorAction SilentlyContinue|?{$_.Length -ge $min -and ($_.Name.ToLower() -notlike 'ui_*')}|%{$freed+=(DelFile $_.FullName)}}
$logs=Join-Path $Root "logs";if(Test-Path $logs){Get-ChildItem -LiteralPath $logs -Recurse -File -ErrorAction SilentlyContinue|?{$_.LastWriteTime -lt (Get-Date).AddDays(-14)}|%{$freed+=(DelFile $_.FullName)}}
Get-ChildItem -LiteralPath $Root -File -Filter *.zip -ErrorAction SilentlyContinue|?{$_.Name -notlike "*OneClick*"}|%{$freed+=(DelFile $_.FullName)}
$post=$pre;if($apply){$post=Get-Size $Root};Add-Content -LiteralPath $log -Value ("Freed (approx): "+(Human $freed));Add-Content -LiteralPath $log -Value ("POST size: "+(Human $post))
Add-Content -LiteralPath $log -Value ("Log end @ "+(Get-Date));Write-Host "";Write-Host ("Freed (approx): "+(Human $freed));Write-Host ("PRE  size     : "+(Human $pre));Write-Host ("POST size     : "+(Human $post));Write-Host "";Write-Host "Done. Detailed log:";Write-Host ("  "+$log);Write-Host ""
