#Requires -Version 5.0

<#
	.SYNOPSIS
	Motor de remocao do Microsoft Edge integrado ao Lynch FPS Boost.
#>

param (
	[switch]$UninstallEdge,
	[switch]$InstallEdge,
	[switch]$InstallWebView,
	[switch]$RemoveEdgeData,
	[switch]$KeepAppX,
	[switch]$NonInteractive
)

$version = '1.9.5'

$ProgressPreference = 'SilentlyContinue'
$sys32 = [Environment]::GetFolderPath('System')
$windir = [Environment]::GetFolderPath('Windows')
$env:path = "$windir;$sys32;$sys32\Wbem;$sys32\WindowsPowerShell\v1.0;" + $env:path
$baseKey = 'HKLM:\SOFTWARE' + $(if ([Environment]::Is64BitOperatingSystem) { '\WOW6432Node' }) + '\Microsoft'
$msedgeExe = "$([Environment]::GetFolderPath('ProgramFilesx86'))\Microsoft\Edge\Application\msedge.exe"
$edgeUWP = "$windir\SystemApps\Microsoft.MicrosoftEdge_8wekyb3d8bbwe"

if ($NonInteractive -and (!$UninstallEdge -and !$InstallEdge -and !$InstallWebView)) {
	$NonInteractive = $false
}
if ($InstallEdge -and $UninstallEdge) {
	throw "You can't use both -InstallEdge and -UninstallEdge as arguments."
}

function Pause ($message = 'Press Enter to exit') {
	if (!$NonInteractive) { $null = Read-Host $message }
}

enum LogLevel {
	Success
	Info
	Warning
	Error
	Critical
}
function Write-Status {
	param (
		[Parameter(Mandatory = $true)]
		[ValidateNotNullOrEmpty()]
		[string]$Text,
		[LogLevel]$Level = 'Info',
		[switch]$Exit,
		[string]$ExitString = 'Press Enter to exit',
		[int]$ExitCode = 1 
	)

	$colour = @(
		'Green',
		'White',
		'Yellow',
		'Red',
		'Red'
	)[$([LogLevel].GetEnumValues().IndexOf($Level))]

	$Text -split "`n" | ForEach-Object {
		Write-Host "[$($Level.ToString().ToUpper())] $_" -ForegroundColor $colour
	}

	if ($Exit) {
		Write-Output ''
		Pause $ExitString
		exit $ExitCode
	}
}

function InternetCheck {
	# Trava de internet removida pelo Lynch Hub para evitar o congelamento fantasma do IE.
	return $true
}

function DeleteIfExist($Path) {
	if (Test-Path $Path) {
		Remove-Item -Path $Path -Force -Recurse -Confirm:$false
	}
}

function Get-MsiexecAppByName {
	param(
		[Parameter(Mandatory = $true)]
		[ValidateNotNullOrEmpty()]
		[string]$Name
	)

	$uninstallKeyPath = 'Microsoft\Windows\CurrentVersion\Uninstall'
	$uninstallKeys = (Get-ChildItem -Path @(
			"HKLM:\SOFTWARE\$uninstallKeyPath",
			"HKLM:\SOFTWARE\WOW6432Node\$uninstallKeyPath",
			"HKCU:\SOFTWARE\$uninstallKeyPath",
			"HKCU:\SOFTWARE\WOW6432Node\$uninstallKeyPath"
		) -ErrorAction SilentlyContinue) -match '\{\b[A-Fa-f0-9]{8}(?:-[A-Fa-f0-9]{4}){3}-[A-Fa-f0-9]{12}\b\}'

	$edges = @()
	foreach ($key in $uninstallKeys.PSPath) {
		if (((Get-ItemProperty -Path $key).DisplayName -like "*$Name*") -and ((Get-ItemProperty -Path $key).UninstallString -like '*MsiExec.exe*')) {
			$edges += Split-Path -Path $key -Leaf
		}
	}

	return $edges
}

# True if it's installed
function EdgeInstalled {
	Test-Path $msedgeExe
}

function KillEdgeProcesses {
	$ErrorActionPreference = 'SilentlyContinue'
	foreach ($service in (Get-Service -Name '*edge*' | Where-Object { $_.DisplayName -like '*Microsoft Edge*' }).Name) {
		Stop-Service -Name $service -Force
	}
	foreach (
		$process in
		(Get-Process | Where-Object { ($_.Path -like "$([Environment]::GetFolderPath('ProgramFilesX86'))\Microsoft\*") -or ($_.Name -like '*msedge*') }).Id
	) {
		Stop-Process -Id $process -Force
	}
	$ErrorActionPreference = 'Continue'	
}

function RemoveEdgeChromium([bool]$AlreadyUninstalled) {
	Write-Status -Text 'Trying to find Edge uninstallers...'

	# get Edge MsiExec uninstallers
	$msis = Get-MsiexecAppByName -Name 'Microsoft Edge'

	# find using common locations - used as a backup
	function UninstallStringFail {
		if ($msis.Count -le 0) {
			Write-Status -Text "Couldn't parse uninstall string for Edge. Trying to find uninstaller manually." -Level Warning
		}

		$script:edgeUninstallers = @()
		'LocalApplicationData', 'ProgramFilesX86', 'ProgramFiles' | ForEach-Object {
			$folder = [Environment]::GetFolderPath($_)
			$script:edgeUninstallers += Get-ChildItem "$folder\Microsoft\Edge*\setup.exe" -Recurse -ErrorAction SilentlyContinue |
			Where-Object { ($_ -like '*Edge\Application*') -or ($_ -like '*SxS\Application*') }
		}
	}

	# find using Registry
	$uninstallKeyPath = "$baseKey\Windows\CurrentVersion\Uninstall\Microsoft Edge"
	$uninstallString = (Get-ItemProperty -Path $uninstallKeyPath -ErrorAction SilentlyContinue).UninstallString
	if ([string]::IsNullOrEmpty($uninstallString) -and ($msis.Count -le 0)) {
		$uninstallString = $null
		UninstallStringFail
	}
 else {
		# split uninstall string for path & args
		$uninstallPath, $uninstallArgs = $uninstallString -split '"', 3 |
		Where-Object { $_ } |
		ForEach-Object { [System.Environment]::ExpandEnvironmentVariables($_.Trim()) }

		# check if fully qualified (should normally be), otherwise it could be null or something in the working dir
		if (![System.IO.Path]::IsPathRooted($uninstallPath) -or !(Test-Path $uninstallPath -PathType Leaf)) {
			$uninstallPath = $null
			UninstallStringFail
		}
	}

	# throw if installers aren't found
	if (($msis.Count -le 0) -and ($script:edgeUninstallers.Count -le 0) -and !$uninstallPath) {
		$uninstallError = @{
			Text     = 'Failed to find uninstaller! ' + $(if ($AlreadyUninstalled) {
					'This likely means Edge is already uninstalled.'
				}
				else {
					"The uninstall can't continue. :("
				})
			Level    = if ($AlreadyUninstalled) { 'Warning' } else { 'Critical' }
			Exit     = $true
			ExitCode = 2
		}
		Write-Status @uninstallError
	}
 else {
		Write-Status 'Found Edge uninstallers.'
	}

	# toggles an EU region - this is because anyone in the EEA can uninstall Edge
	function ToggleEURegion([bool]$Enable) {
		$geoKey = 'Registry::HKEY_USERS\.DEFAULT\Control Panel\International\Geo'

		# sets Geo to France, which is in the EEA
		$values = @{
			'Name'   = 'FR'
			'Nation' = '84'
		}
		$geoChange = 'EdgeSaved'

		if ($Enable) {
			$values.GetEnumerator() | ForEach-Object {
				Rename-ItemProperty -Path $geoKey -Name $_.Key -NewName "$($_.Key)$geoChange" -Force
				Set-ItemProperty -Path $geoKey -Name $_.Key -Value $_.Value -Force
			}
		}
		else {
			$values.GetEnumerator() | ForEach-Object {
				Remove-ItemProperty -Path $geoKey -Name $_.Key -Force -ErrorAction SilentlyContinue
				Rename-ItemProperty -Path $geoKey -Name "$($_.Key)$geoChange" -NewName $_.Key -Force -ErrorAction SilentlyContinue
			}
		}
	}

	function ModifyRegionJSON {
		$cleanup = $false
		$script:integratedServicesPath = "$sys32\IntegratedServicesRegionPolicySet.json"

		if (Test-Path $integratedServicesPath) {
			$cleanup = $true
			try {
				$admin = [System.Security.Principal.NTAccount]$(New-Object System.Security.Principal.SecurityIdentifier('S-1-5-32-544')).Translate([System.Security.Principal.NTAccount]).Value

				$acl = Get-Acl -Path $integratedServicesPath
				$script:backup = [System.Security.AccessControl.FileSecurity]::new()
				$script:backup.SetSecurityDescriptorSddlForm($acl.Sddl)
				$acl.SetOwner($admin)
				$rule = New-Object System.Security.AccessControl.FileSystemAccessRule($admin, 'FullControl', 'Allow')
				$acl.AddAccessRule($rule)
				Set-Acl -Path $integratedServicesPath -AclObject $acl

				$integratedServices = Get-Content $integratedServicesPath | ConvertFrom-Json
				($integratedServices.policies | Where-Object { ($_.'$comment' -like '*Edge*') -and ($_.'$comment' -like '*uninstall*') }).defaultState = 'enabled'
				$modifiedJson = $integratedServices | ConvertTo-Json -Depth 100

				$script:backupIntegratedServicesName = "IntegratedServicesRegionPolicySet.json.$([System.IO.Path]::GetRandomFileName())"
				Rename-Item $integratedServicesPath -NewName $script:backupIntegratedServicesName -Force
				Set-Content $integratedServicesPath -Value $modifiedJson -Force -Encoding UTF8
			}
			catch {
				Write-Error "Failed to modify region policies. $_"
			}
		}
		else {
			Write-Status -Text "'$integratedServicesPath' not found." -Level Warning
		}

		return $cleanup
	}

	function UninstallEdge {
		foreach ($msi in $msis) {
			Write-Status 'Uninstalling Edge using Windows Installer...'
			Start-Process -FilePath 'msiexec.exe' -ArgumentList "/qn /X$(Split-Path -Path $msi -Leaf) REBOOT=ReallySuppress /norestart" -Wait
		}

		if ($uninstallPath) {
			Start-Process -Wait -FilePath $uninstallPath -ArgumentList "$uninstallArgs --force-uninstall" -WindowStyle Hidden
		}
		else {
			foreach ($setup in $edgeUninstallers) {
				if (Test-Path $setup) {
					$sulevel = ('--system-level', '--user-level')[$setup -like '*\AppData\Local\*']
					Start-Process -Wait $setup -ArgumentList "--uninstall --msedge $sulevel --channel=stable --verbose-logging --force-uninstall"
				}
			}
		}

		return EdgeInstalled
	}

	function GlobalRemoveMethods {
		Write-Status "Using method $method..." -Level Warning

		Remove-ItemProperty -Path "$baseKey\EdgeUpdate\ClientState\{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}" -Name 'experiment_control_labels' -Force -ErrorAction SilentlyContinue

		$devKeyPath = "$baseKey\EdgeUpdateDev"
		if (!(Test-Path $devKeyPath)) { New-Item -Path $devKeyPath -ItemType 'Key' -Force | Out-Null }
		Set-ItemProperty -Path $devKeyPath -Name 'AllowUninstall' -Value '' -Type String -Force
	
		Write-Status 'Terminating Microsoft Edge processes...'
		KillEdgeProcesses
	}

	$fail = $true
	$method = 1
	function CleanupMsg { Write-Status "Cleaning up after method $method..." }
	while ($fail) {
		switch ($method) {
			1 {
				GlobalRemoveMethods
				if (!(Test-Path "$edgeUWP\MicrosoftEdge.exe")) {
					New-Item $edgeUWP -ItemType Directory -ErrorVariable cleanup -ErrorAction SilentlyContinue | Out-Null
					New-Item "$edgeUWP\MicrosoftEdge.exe" -ErrorAction SilentlyContinue | Out-Null
					$cleanup = $true
				}
				$fail = UninstallEdge
				if ($cleanup) {
					CleanupMsg
					Remove-Item $edgeUWP -Force -ErrorAction SilentlyContinue -Recurse
				}
			}
			2 {
				GlobalRemoveMethods
				$envPath = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
				try {
					Set-ItemProperty -Path $envPath -Name 'windir' -Value '' -Type ExpandString
					$env:windir = [System.Environment]::GetEnvironmentVariable('windir', [System.EnvironmentVariableTarget]::Machine)
					$fail = UninstallEdge
				}
				finally {
					CleanupMsg
					Set-ItemProperty -Path $envPath -Name 'windir' -Value '%SystemRoot%' -Type ExpandString
				}
			}
			3 {
				GlobalRemoveMethods
				ToggleEURegion $true
				$fail = UninstallEdge
				CleanupMsg
				ToggleEURegion $false
			}
			4 {
				GlobalRemoveMethods
				$cleanup = ModifyRegionJSON
				$fail = UninstallEdge
				if ($cleanup) {
					CleanupMsg
					Remove-Item $integratedServicesPath -Force
					Rename-Item "$sys32\$backupIntegratedServicesName" -NewName $integratedServicesPath -Force
					Set-Acl -Path $integratedServicesPath -AclObject $backup
				}
			}
			default {
				Write-Status 'The uninstall methods failed for the Edge installers found. Nothing else can be done.' -Level Critical -Exit -ExitCode 3
			}
		}

		$method++
	}
	Write-Status 'Successfully removed Edge! :)' -Level Success

	"$([Environment]::GetFolderPath('Desktop'))\Microsoft Edge.lnk",
	"$([Environment]::GetFolderPath('CommonStartMenu'))\Microsoft Edge.lnk" | ForEach-Object { DeleteIfExist $_ }

	if ((Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' -Name 'ShowCopilotButton' -ErrorAction SilentlyContinue).'ShowCopilotButton' -eq 1) {
		Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
	}
}

function RemoveEdgeAppX {
	$SID = (New-Object System.Security.Principal.NTAccount([Environment]::UserName)).Translate([Security.Principal.SecurityIdentifier]).Value

	$appxStore = '\SOFTWARE\Microsoft\Windows\CurrentVersion\Appx\AppxAllUserStore'
	$pattern = "HKLM:$appxStore\InboxApplications\Microsoft.MicrosoftEdge_*_neutral__8wekyb3d8bbwe"
	$edgeAppXKey = (Get-Item -Path $pattern).PSChildName
	if (Test-Path "$pattern") { reg delete "HKLM$appxStore\InboxApplications\$edgeAppXKey" /f | Out-Null }

	New-Item -Path "HKLM:$appxStore\EndOfLife\$SID\Microsoft.MicrosoftEdge_8wekyb3d8bbwe" -Force | Out-Null
	Get-AppxPackage -Name Microsoft.MicrosoftEdge | Remove-AppxPackage | Out-Null
	Remove-Item -Path "HKLM:$appxStore\EndOfLife\$SID\Microsoft.MicrosoftEdge_8wekyb3d8bbwe" -Force | Out-Null
}

function InstallEdgeChromium {
	InternetCheck

	$temp = mkdir (Join-Path $([System.IO.Path]::GetTempPath()) $(New-Guid))
	$msi = "$temp\edge.msi"
	$msiLog = "$temp\edgeMsi.log"
	
	if ([Environment]::Is64BitOperatingSystem) {
		$arm = ((Get-CimInstance -Class Win32_ComputerSystem).SystemType -match 'ARM64') -or ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64')
		$archString = ('x64', 'arm64')[$arm]
	}
 else {
		$archString = 'x86'
	}
	
	Write-Status 'Requesting from the Microsoft Edge Update API...'
	try {
		try {
			$edgeUpdateApi = (Invoke-WebRequest 'https://edgeupdates.microsoft.com/api/products' -UseBasicParsing).Content | ConvertFrom-Json
		}
		catch {
			Write-Status "Failed to request from EdgeUpdate API!
Error: $_" -Level Critical -Exit -ExitCode 4
		}

		$edgeItem = ($edgeUpdateApi | Where-Object { $_.Product -eq 'Stable' }).Releases |
		Where-Object { $_.Platform -eq 'Windows' -and $_.Architecture -eq $archString } |
		Where-Object { $_.Artifacts.Count -ne 0 } | Select-Object -First 1
		
		if ($null -eq $edgeItem) {
			Write-Status 'Failed to parse EdgeUpdate API! No matching artifacts found.' -Level Critical -Exit
		}

		$hashAlg = $edgeItem.Artifacts.HashAlgorithm | ForEach-Object { if ([string]::IsNullOrEmpty($_)) { 'SHA256' } else { $_ } }
		foreach ($var in @{
				link     = $edgeItem.Artifacts.Location
				hash     = $edgeItem.Artifacts.Hash
				version  = $edgeItem.ProductVersion
				sizeInMb = [math]::round($edgeItem.Artifacts.SizeInBytes / 1Mb)
				released = Get-Date $edgeItem.PublishedTime
			}.GetEnumerator()) {
			$val = $var.Value | Select-Object -First 1
			if ($val.Length -le 0) {
				Set-Variable -Name $var.Key -Value 'Undefined'
				if ($var.Key -eq 'link') { throw 'Failed to parse download link!' }
			}
			else {
				Set-Variable -Name $var.Key -Value $val
			}
		}
	}
 catch {
		Write-Status "Failed to parse Microsoft Edge from `"$link`"!
Error: $_" -Level Critical -Exit -ExitCode 5
	}
	Write-Status 'Parsed Microsoft Edge Update API!' -Level Success
	
	Write-Host "`nDownloading Microsoft Edge:" -ForegroundColor Cyan
	@(
		@('Released on: ', $released),
		@('Version: ', "$version (Stable)"),
		@('Size: ', "$sizeInMb Mb")
	) | Foreach-Object {
		Write-Host ' - ' -NoNewline -ForegroundColor Magenta
		Write-Host $_[0] -NoNewline -ForegroundColor Yellow
		Write-Host $_[1]
	}
	
	Write-Output ''
	try {
		if ($null -eq (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
			Write-Status "Couldn't find cURL, using Invoke-WebRequest, which is slower..." -Level Warning
			Invoke-WebRequest -Uri $link -Output $msi -UseBasicParsing
		}
		else {
			curl.exe -#L "$link" -o "$msi"
		}
	}
 catch {
		Write-Status "Failed to download Microsoft Edge from `"$link`"!
Error: $_" -Level Critical -Exit -ExitCode 6
	}
	Write-Output ''
	
	if ($hash -eq 'Undefined') {
		Write-Status "Not verifying hash as it's undefined, download might have failed." -Level Warning
	}
 else {
		Write-Status 'Verifying download by checking its hash...'
		if ((Get-FileHash -LiteralPath $msi -Algorithm $hashAlg).Hash -eq $hash) {
			Write-Status 'Verified the Microsoft Edge installer!' -Level Success
		}
		else {
			Write-Status 'Edge installer hash does not match. The installer might be corrupted. Continuing anyways...' -Level Error
		}
	}
	
	Write-Status 'Installing Microsoft Edge...'
	Start-Process -FilePath 'msiexec.exe' -ArgumentList "/i `"$msi`" /l `"$msiLog`" /quiet" -Wait
	
	if (!(Test-Path $msiLog)) {
		Write-Status "Couldn't find installer log at `"$msiLog`"! This likely means it failed." -Level Critical -Exit -ExitCode 7
	}
	
	Write-Status -Text "Installer log path: `"$msiLog`""
	if ($null -eq ($(Get-Content $msiLog) -like '*Product: Microsoft Edge -- * completed successfully.*')) {
		Write-Status "Can't find success string from Edge install log - it seems like the install was a failure." -Level Error -Exit -ExitCode 8
	}

	Write-Status -Text 'Installed Microsoft Edge!' -Level Success
}

function InstallWebView {
	InternetCheck

	$dlPath = "$((Join-Path $([System.IO.Path]::GetTempPath()) $(New-Guid)))-webview2.exe"
	$link = 'https://go.microsoft.com/fwlink/p/?LinkId=2124703'

	Write-Status 'Downloading Edge WebView...'
	try {
		if ($null -eq (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
			Write-Status "Couldn't find cURL, using Invoke-WebRequest, which is slower..." -Level Warning
			Invoke-WebRequest -Uri $link -Output $dlPath -UseBasicParsing
		}
		else {
			curl.exe -Ls "$link" -o "$dlPath"
		}
	}
 catch {
		Write-Status "Failed to download Edge WebView from `"$link`"!
Error: $_" -Level Critical -Exit -ExitCode 9
	}

	Write-Status 'Installing Edge WebView...'
	Start-Process -FilePath "$dlPath" -ArgumentList '/silent /install' -Wait

	Write-Status 'Installed Edge WebView!' -Level Success
}

if ([Security.Principal.WindowsIdentity]::GetCurrent().User.Value -eq 'S-1-5-18') {
	Write-Status "This script can't be ran as TrustedInstaller/SYSTEM.
Please relaunch this script under a regular admin account." -Level Critical -Exit
}
else {
	if (!([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
		if ($PSBoundParameters.Count -le 0 -and !$args) {
			Start-Process cmd "/c PowerShell -NoP -EP Bypass -File `"$PSCommandPath`"" -Verb RunAs
			exit
		}
		else {
			throw 'This script must be run as an administrator.'
		}
	}
}

$edgeInstalled = EdgeInstalled
if (!$UninstallEdge -and !$InstallEdge -and !$InstallWebView) {
	$host.UI.RawUI.WindowTitle = "Lynch FPS Boost - Motor Edge"	

	$RemoveEdgeData = $false
	while (!$continue) {
		Clear-Host
		$description = 'This script removes or installs Microsoft Edge.'
		Write-Host "$description`n" -ForegroundColor Blue
		Write-Host @'
To select an option, type its number.
To perform an action, also type its number.
'@ -ForegroundColor Yellow

		Write-Host "`nEdge is currently detected as: " -NoNewline -ForegroundColor Green
		Write-Host "$(@('Uninstalled', 'Installed')[$edgeInstalled])" -ForegroundColor Cyan

		Write-Host "`n$('-' * $description.Length)" -ForegroundColor Magenta

		if ($RemoveEdgeData) { $colourData = 'Green'; $textData = 'Selected' } else { $colourData = 'Red'; $textData = 'Unselected' }

		Write-Host "`nOptions:"
		Write-Host "[1] Remove Edge User Data ($textData)" -ForegroundColor $colourData
		
		Write-Host "`nActions:"
		Write-Host @'
[2] Uninstall Edge
[3] Install Edge
[4] Install WebView
[5] Install both Edge & WebView
'@ -ForegroundColor Cyan

		$userInput = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

		switch ($userInput.VirtualKeyCode) {
			49 {
				$RemoveEdgeData = !$RemoveEdgeData
			}
			50 {
				$UninstallEdge = $true
				$continue = $true
			}
			51 {
				$InstallEdge = $true
				$continue = $true
			}
			52 {
				$InstallWebView = $true
				$continue = $true
			}
			53 {
				$InstallWebView = $true
				$InstallEdge = $true
				$continue = $true
			}
		}
	}

	Clear-Host
}

if ($UninstallEdge) {
	Write-Status 'Uninstalling Edge Chromium...'
	RemoveEdgeChromium $(!$edgeInstalled)
	if ($null -ne (Get-AppxPackage -Name Microsoft.MicrosoftEdge)) {
		if ($KeepAppX) {
			Write-Status 'AppX Edge is being left, there might be a stub...' -Level Warning
		}
		else {
			Write-Status 'Uninstalling AppX Edge...' -Level Warning
			RemoveEdgeAppx
		}
	}
	Write-Output ''
}

if ($RemoveEdgeData) {
	KillEdgeProcesses
	DeleteIfExist "$([Environment]::GetFolderPath('LocalApplicationData'))\Microsoft\Edge"
	Write-Status 'Removed any existing Edge Chromium user data.'
	Write-Output ''
}

if ($InstallEdge) {
	InstallEdgeChromium
	Write-Output ''
}
if ($InstallWebView) {
	InstallWebView
	Write-Output ''
}

Write-Host 'Completed.' -ForegroundColor Cyan
if ($NonInteractive) { exit }
Pause
