from pathlib import Path
import shutil, zipfile, re, sys

if len(sys.argv) != 3:
    raise SystemExit("usage: build_v010.py INPUT_V091_ZIP OUTPUT_V010_ZIP")

input_zip = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
work = Path("release_work_v010").resolve()
if work.exists():
    shutil.rmtree(work)
work.mkdir(parents=True)
with zipfile.ZipFile(input_zip, "r") as z:
    z.extractall(work)

launchers = list(work.rglob("BauerVonNebenan_Launcher.ps1"))
if not launchers:
    raise SystemExit("input package contains no BauerVonNebenan_Launcher.ps1")
src_root = launchers[0].parent
build_root = Path("release_build_v010/BauerVonNebenan").resolve()
if build_root.parent.exists():
    shutil.rmtree(build_root.parent)
shutil.copytree(src_root, build_root)

launcher = build_root/'BauerVonNebenan_Launcher.ps1'
text = launcher.read_text(encoding='utf-8')

old_header = """# Bauer von Nebenan - Agriculture Science Launcher v0.9.1
# PowerShell 5.1+ (Windows) / PowerShell 7+ (macOS)

$ErrorActionPreference = 'Stop'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$script:UseColors = $true
$script:LauncherVersion = '0.9.1'
"""
new_header = """# Bauer von Nebenan - Agriculture Science Launcher v0.10.0
# PowerShell 5.1+ (Windows) / PowerShell 7+ (macOS)

param(
    # When Steam starts Start_BauerVonNebenan.bat with %command%, all unnamed
    # arguments land here. The first entry is the original game executable.
    [Parameter(Position=0, ValueFromRemainingArguments=$true)]
    [string[]]$SteamCommand,

    # Used internally when the self-updater has to carry a Steam command across
    # the launcher restart without losing quotes/spaces.
    [string]$SteamCommandBase64 = ''
)

$ErrorActionPreference = 'Stop'
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$script:UseColors = $true
$script:LauncherVersion = '0.10.0'

if (-not [string]::IsNullOrWhiteSpace($SteamCommandBase64)) {
    try {
        $decodedJson = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($SteamCommandBase64))
        $SteamCommand = @($decodedJson | ConvertFrom-Json)
    } catch {
        Write-Warning 'Steam-Startbefehl aus dem Update-Handoff konnte nicht gelesen werden. Verwende normale Startkonfiguration.'
        $SteamCommand = @()
    }
}
$script:SteamCommand = @($SteamCommand | Where-Object { $null -ne $_ })
"""
if old_header not in text:
    raise SystemExit('header block not found')
text = text.replace(old_header,new_header,1)

needle = """function Show-PathError {
"""
helpers = r'''function Get-SteamCommandBase64 {
    if (-not $script:SteamCommand -or $script:SteamCommand.Count -eq 0) { return '' }
    $json = ConvertTo-Json -InputObject @($script:SteamCommand) -Compress
    return [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($json))
}

function Resolve-LaunchTarget {
    param(
        [string]$LaunchMode,
        [string]$ConfiguredGameExe
    )

    $mode = if ([string]::IsNullOrWhiteSpace($LaunchMode)) { 'Auto' } else { $LaunchMode.Trim() }
    $steamAvailable = ($script:SteamCommand -and $script:SteamCommand.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace([string]$script:SteamCommand[0]))

    switch ($mode.ToLowerInvariant()) {
        'auto' {
            if ($steamAvailable) {
                return [pscustomobject]@{ UseSteam=$true; GameExe=[string]$script:SteamCommand[0]; Mode='Steam' }
            }
            return [pscustomobject]@{ UseSteam=$false; GameExe=$ConfiguredGameExe; Mode='Config' }
        }
        'steam' {
            if (-not $steamAvailable) {
                throw 'LaunchMode=Steam wurde gesetzt, aber Steam hat keinen Original-Startbefehl uebergeben.'
            }
            return [pscustomobject]@{ UseSteam=$true; GameExe=[string]$script:SteamCommand[0]; Mode='Steam' }
        }
        'config' {
            return [pscustomobject]@{ UseSteam=$false; GameExe=$ConfiguredGameExe; Mode='Config' }
        }
        default {
            Write-ColorLine ("[LAUNCH-WARNUNG] Unbekannter LaunchMode '{0}'. Verwende Auto." -f $mode) Yellow
            if ($steamAvailable) {
                return [pscustomobject]@{ UseSteam=$true; GameExe=[string]$script:SteamCommand[0]; Mode='Steam' }
            }
            return [pscustomobject]@{ UseSteam=$false; GameExe=$ConfiguredGameExe; Mode='Config' }
        }
    }
}

'''
if needle not in text:
    raise SystemExit('Show-PathError needle missing')
text = text.replace(needle,helpers+needle,1)

pattern = re.compile(r"function Start-LS25 \{.*?\n\}\n\n\n# -------------------------- REMOTE UPDATE",re.S)
m = pattern.search(text)
if not m:
    raise SystemExit('Start-LS25 block not found')
new_func = r'''function Start-LS25 {
    param(
        [string]$GameExe,
        [string]$ProcessName,
        [bool]$CloseWhenRunning,
        [bool]$UseSteamCommand = $false
    )
    Write-Host ''
    Write-ColorLine '[LAUNCH] Landwirtschaft wird initialisiert...' Cyan

    if ($UseSteamCommand) {
        if (-not $script:SteamCommand -or $script:SteamCommand.Count -eq 0) {
            throw 'Steam-Startmodus wurde gewaehlt, aber kein Steam-Befehl ist vorhanden.'
        }

        $steamExe = [string]$script:SteamCommand[0]
        $steamArgs = @()
        if ($script:SteamCommand.Count -gt 1) {
            $steamArgs = @($script:SteamCommand[1..($script:SteamCommand.Count - 1)])
        }

        Write-ColorLine '[STEAM] Originalen Steam-Startbefehl erkannt.' Green
        Write-ColorLine ("[STEAM] Starte: {0}" -f $steamExe) DarkGray
        if ($steamArgs.Count -gt 0) {
            Start-Process -FilePath $steamExe -ArgumentList $steamArgs | Out-Null
        } else {
            Start-Process -FilePath $steamExe | Out-Null
        }
    } elseif ($IsMacOS -and $GameExe.EndsWith('.app', [StringComparison]::OrdinalIgnoreCase)) {
        & /usr/bin/open $GameExe
        if ($LASTEXITCODE -ne 0) {
            throw "macOS konnte die konfigurierte .app nicht starten: $GameExe"
        }
    } else {
        Start-Process -FilePath $GameExe | Out-Null
    }

    if (-not $CloseWhenRunning) { return }
    Write-ColorLine '[LAUNCH] Warte auf Farming Simulator 25...' DarkGray
    $deadline = (Get-Date).AddSeconds(45)
    do {
        Start-Sleep -Milliseconds 500
        $proc = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($proc) {
            Write-ColorLine '[LAUNCH] Farming Simulator 25 erkannt. Launcher beendet sich.' Green
            Start-Sleep -Milliseconds 700
            return
        }
    } while ((Get-Date) -lt $deadline)
    Write-ColorLine '[WARNUNG] Spielprozess wurde nach 45 Sekunden nicht erkannt.' Yellow
    Write-ColorLine 'Der Launcher beendet sich trotzdem; die Landwirtschaft muss nun selbst klarkommen.' DarkGray
}


# -------------------------- REMOTE UPDATE'''
text = text[:m.start()] + new_func + text[m.end():]
text = text.replace("'User-Agent'='BauerVonNebenan-AgricultureScience/0.9.1'", "'User-Agent'='BauerVonNebenan-AgricultureScience/0.10.0'")

old = """    $helperCopy = Join-Path $tempRoot 'BauerVonNebenan_Updater.ps1'
    Copy-Item -LiteralPath $updater -Destination $helperCopy -Force

    if ($IsMacOS) {
"""
new = """    $helperCopy = Join-Path $tempRoot 'BauerVonNebenan_Updater.ps1'
    Copy-Item -LiteralPath $updater -Destination $helperCopy -Force
    $steamHandoff = Get-SteamCommandBase64

    if ($IsMacOS) {
"""
if old not in text:
    raise SystemExit('self update helper block missing')
text = text.replace(old,new,1)

old_mac = """        [void]$psi.ArgumentList.Add('-OldPid')
        [void]$psi.ArgumentList.Add([string]$PID)
        [void][System.Diagnostics.Process]::Start($psi)
    } else {
        $engine = 'powershell.exe'
        $args = @('-NoLogo','-NoProfile','-ExecutionPolicy','Bypass','-File',("`\"{0}`\"" -f $helperCopy),'-CurrentRoot',("`\"{0}`\"" -f $ScriptRoot),'-NewRoot',("`\"{0}`\"" -f $newRoot),'-OldPid',$PID)
        Start-Process -FilePath $engine -ArgumentList $args | Out-Null
    }
"""
new_mac = """        [void]$psi.ArgumentList.Add('-OldPid')
        [void]$psi.ArgumentList.Add([string]$PID)
        if (-not [string]::IsNullOrWhiteSpace($steamHandoff)) {
            [void]$psi.ArgumentList.Add('-SteamCommandBase64')
            [void]$psi.ArgumentList.Add($steamHandoff)
        }
        [void][System.Diagnostics.Process]::Start($psi)
    } else {
        $engine = 'powershell.exe'
        $args = @('-NoLogo','-NoProfile','-ExecutionPolicy','Bypass','-File',("`\"{0}`\"" -f $helperCopy),'-CurrentRoot',("`\"{0}`\"" -f $ScriptRoot),'-NewRoot',("`\"{0}`\"" -f $newRoot),'-OldPid',$PID)
        if (-not [string]::IsNullOrWhiteSpace($steamHandoff)) {
            $args += @('-SteamCommandBase64',$steamHandoff)
        }
        Start-Process -FilePath $engine -ArgumentList $args | Out-Null
    }
"""
if old_mac not in text:
    raise SystemExit('self update args block missing')
text = text.replace(old_mac,new_mac,1)

old = """$LaunchGame = Convert-ToBool (Get-ConfigValue $config 'Launcher' 'LaunchGame' 'true') $true
$LaunchDelay = [int](Get-ConfigValue $config 'Launcher' 'LaunchDelay' '5')
"""
new = """$LaunchGame = Convert-ToBool (Get-ConfigValue $config 'Launcher' 'LaunchGame' 'true') $true
$LaunchMode = Get-ConfigValue $config 'Launcher' 'LaunchMode' 'Auto'
$LaunchDelay = [int](Get-ConfigValue $config 'Launcher' 'LaunchDelay' '5')
"""
if old not in text:
    raise SystemExit('launch config block missing')
text = text.replace(old,new,1)

old = """Test-ConfiguredPaths $GameExe $ModFolder $ShowBootSequence

$remoteManifest = $null
"""
new = """try {
    $launchTarget = Resolve-LaunchTarget -LaunchMode $LaunchMode -ConfiguredGameExe $GameExe
} catch {
    Show-PathError 'LaunchMode' $LaunchMode $_.Exception.Message
}
$EffectiveGameExe = [string]$launchTarget.GameExe
$UseSteamCommand = [bool]$launchTarget.UseSteam

if ($UseSteamCommand) {
    Write-ColorLine '[STEAM] Start durch Steam erkannt. Originalbefehl wird nach dem Mod-Check verwendet.' Cyan
} elseif ($LaunchMode.ToLowerInvariant() -eq 'auto') {
    Write-ColorLine '[LAUNCH] Kein Steam-Handoff erkannt. Verwende GameExe aus config.ini.' DarkGray
}

Test-ConfiguredPaths $EffectiveGameExe $ModFolder $ShowBootSequence

$remoteManifest = $null
"""
if old not in text:
    raise SystemExit('path validation call missing')
text = text.replace(old,new,1)
text = text.replace("Start-LS25 $GameExe $GameProcessName $CloseWhenGameRunning", "Start-LS25 $EffectiveGameExe $GameProcessName $CloseWhenGameRunning $UseSteamCommand",1)
launcher.write_text(text,encoding='utf-8')

updater = build_root/'BauerVonNebenan_Updater.ps1'
ut = updater.read_text(encoding='utf-8')
ut = ut.replace("[Parameter(Mandatory=$true)][int]$OldPid\n)", "[Parameter(Mandatory=$true)][int]$OldPid,\n    [string]$SteamCommandBase64 = ''\n)",1)

old_restart = """    $launcher = Join-Path $CurrentRoot 'BauerVonNebenan_Launcher.ps1'
    if ($IsMacOS) {
        $engine = (Get-Command pwsh -ErrorAction Stop).Source

        # Preserve the full launcher path as one argument on macOS.
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $engine
        $psi.UseShellExecute = $false
        [void]$psi.ArgumentList.Add('-NoProfile')
        [void]$psi.ArgumentList.Add('-File')
        [void]$psi.ArgumentList.Add($launcher)
        [void][System.Diagnostics.Process]::Start($psi)
    } else {
        Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoLogo','-NoProfile','-ExecutionPolicy','Bypass','-File',("`\"{0}`\"" -f $launcher)) | Out-Null
    }
"""
new_restart = """    $launcher = Join-Path $CurrentRoot 'BauerVonNebenan_Launcher.ps1'
    if ($IsMacOS) {
        $engine = (Get-Command pwsh -ErrorAction Stop).Source
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $engine
        $psi.UseShellExecute = $false
        [void]$psi.ArgumentList.Add('-NoProfile')
        [void]$psi.ArgumentList.Add('-File')
        [void]$psi.ArgumentList.Add($launcher)
        if (-not [string]::IsNullOrWhiteSpace($SteamCommandBase64)) {
            [void]$psi.ArgumentList.Add('-SteamCommandBase64')
            [void]$psi.ArgumentList.Add($SteamCommandBase64)
        }
        [void][System.Diagnostics.Process]::Start($psi)
    } else {
        $restartArgs = @('-NoLogo','-NoProfile','-ExecutionPolicy','Bypass','-File',("`\"{0}`\"" -f $launcher))
        if (-not [string]::IsNullOrWhiteSpace($SteamCommandBase64)) {
            $restartArgs += @('-SteamCommandBase64',$SteamCommandBase64)
        }
        Start-Process -FilePath 'powershell.exe' -ArgumentList $restartArgs | Out-Null
    }
"""
if old_restart not in ut:
    raise SystemExit('updater restart block missing')
ut = ut.replace(old_restart,new_restart,1)
updater.write_text(ut,encoding='utf-8')

bat = r'''@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul

title Bauer von Nebenan - Agriculture Science

rem When Steam launch options contain:
rem   "C:\Path\To\Start_BauerVonNebenan.bat" %command%
rem %* contains Steam's original Farming Simulator command.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0BauerVonNebenan_Launcher.ps1" %*
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
    echo.
    echo ================================================================
    echo   AGRICULTURE SCIENCE // UNERWARTETER LAUNCHER-FEHLER
    echo ================================================================
    echo.
    echo Der Launcher wurde mit Fehlercode %EXITCODE% beendet.
    echo Das Fenster bleibt offen, damit die Forschungsabteilung
    echo den roten Text diesmal auch tatsaechlich lesen kann.
    echo.
    echo WISSENSCHAFTLICHE BEWERTUNG:
    echo   Irgendetwas ist fuer'n Arsch. Diesmal eventuell unser Code.
    echo.
    pause
)

exit /b %EXITCODE%
'''
(build_root/'Start_BauerVonNebenan.bat').write_text(bat,encoding='utf-8',newline='\r\n')

config = build_root/'config.ini'
ct = config.read_text(encoding='utf-8')
ct = ct.replace("# Spiel nach erfolgreicher Pruefung automatisch starten\nLaunchGame=true\n\n# Countdown", "# Spiel nach erfolgreicher Pruefung automatisch starten\nLaunchGame=true\n\n# Auto = Steam-Originalbefehl verwenden, wenn Steam ihn uebergibt; sonst GameExe.\n# Steam = Steam-Handoff erzwingen. Config = immer GameExe verwenden.\nLaunchMode=Auto\n\n# Countdown",1)
config.write_text(ct,encoding='utf-8')

readme = build_root/'README.txt'
rt = readme.read_text(encoding='utf-8')
steam_section = r'''

STEAM WRAPPER (WINDOWS) - v0.10.0
--------------------------------
Der Launcher kann jetzt direkt zwischen Steam und Farming Simulator 25 geschaltet werden.

Steam -> Eigenschaften -> Allgemein -> Startoptionen:

  "C:\PFAD\ZU\BauerVonNebenan\Start_BauerVonNebenan.bat" %command%

Mit LaunchMode=Auto erkennt Agriculture Science den von Steam uebergebenen
Originalbefehl. Nach dem Mod-/Update-Check wird exakt dieser Spielstart verwendet.
Wird der Launcher normal per Doppelklick gestartet, faellt Auto auf GameExe aus
der config.ini zurueck.

LaunchMode-Werte:
  Auto   = Steam bevorzugen, sonst config.ini
  Steam  = Steam-Handoff zwingend erforderlich
  Config = Steam ignorieren und GameExe verwenden

Hinweis: macOS-Steam-Wrapper ist noch experimentell und in dieser Version nicht aktiviert.
'''
if 'STEAM WRAPPER (WINDOWS)' not in rt:
    rt += steam_section
readme.write_text(rt,encoding='utf-8')

manifest_example = build_root/'repo_templates/manifest.json.example'
if manifest_example.exists():
    me = manifest_example.read_text(encoding='utf-8')
    me = re.sub(r'"version"\s*:\s*"0\.9\.0"', '"version": "0.10.0"', me)
    me = me.replace('v0.9.0/BauerVonNebenan_AgricultureScience_Launcher_v0.9.zip','v0.10.0/BauerVonNebenan_AgricultureScience_Launcher_v0.10.0.zip')
    manifest_example.write_text(me,encoding='utf-8')

gs = build_root/'GITHUB_SETUP.txt'
gst = gs.read_text(encoding='utf-8')
gst = gst.replace('v0.9.0','v0.10.0').replace('v0.9.zip','v0.10.0.zip')
gs.write_text(gst,encoding='utf-8')

if out.exists():
    out.unlink()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(build_root.rglob("*")):
        if p.is_file():
            z.write(p, (Path("BauerVonNebenan") / p.relative_to(build_root)).as_posix())

with zipfile.ZipFile(out, "r") as z:
    launcher_text = z.read("BauerVonNebenan/BauerVonNebenan_Launcher.ps1").decode("utf-8")
    assert "$script:LauncherVersion = '0.10.0'" in launcher_text
    assert "LaunchMode" in launcher_text
    assert "SteamCommandBase64" in launcher_text
print(out)
