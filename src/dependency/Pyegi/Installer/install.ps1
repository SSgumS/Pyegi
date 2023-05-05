$ErrorActionPreference = "Stop"

function Expand-Archive($tarFile, $dest) {
    if (-not (Get-Command Expand-7Zip -ErrorAction Ignore)) {
        Install-Package -Scope CurrentUser -Force -ProviderName PowerShellGet 7Zip4PowerShell > $null
    }

    Expand-7Zip $tarFile $dest
}

function Remove-Target-Dir($target) {
    if (-not (Test-Path -Path $target)) {
        return
    }
    $targetObj = Get-Item $target
    if ($targetObj.LinkType -eq "SymbolicLink") {
        $targetObj.Delete()
    }
    else {
        Remove-Item $target -Recurse
    }
}

function Update-Python($version, $targetFolder) {
    # download
    $fileName = "cpython-$pyVer+$packageVersion-$arch-pc-windows-msvc-shared-install_only.tar.gz"
    $url = "https://github.com/indygreg/python-build-standalone/releases/download/$packageVersion/$fileName"
    if (-not (Test-Path -Path $fileName)) {
        Invoke-WebRequest -OutFile $fileName $url
    }
    # extract
    $initialFolder = "python"
    Remove-Target-Dir $initialFolder
    Expand-Archive $fileName "."
    Remove-Item $fileName
    $tarFile = $fileName.TrimEnd(".gz")
    Expand-Archive $tarFile "."
    Remove-Item $tarFile
    # rename folder
    Remove-Target-Dir $targetFolder
    Move-Item $initialFolder $targetFolder
}

# set location to script's location
$prevPwd = $PWD
Set-Location -LiteralPath $PSScriptRoot

try {
    # specify architecture
    $is64 = [Environment]::Is64BitOperatingSystem
    $arch = "i686"
    if ($is64) {
        $arch = "x86_64"
    }
    $packageVersion = "20230116"
    $pythonVersions = "3.9.16", "3.10.9", "3.11.1"
    $pyegiPythonsDir = "$($env:APPDATA -replace "\\", "/")/Aegisub/automation/dependency/Pyegi/Pythons/"
    # set shouldUpdate
    if ($Args[0] -eq "--update-pythons") {
        $shouldUpdate = $true
    }
    else {
        $shouldUpdate = $false
    }
    # prepare environments
    Set-Location "../Pythons/"
    # read logs
    $logsFilePath = "./python-fetch.logs"
    $logsFileContent = ""
    if (Test-Path -Path $logsFilePath) {
        $logsFileContent = Get-Content -Path $logsFilePath -Raw
        $null = New-Item -Path $logsFilePath -ItemType File -Force
    }
    for ($i = 0; $i -lt $pythonVersions.Count; $i++) {
        $pyVer = $pythonVersions[$i]
        # determine folder name
        if (-not ($pyVer -match '^(?<major>\d+)\.(?<minor>\d+)')) {
            throw "Python version `"$pyVer`" is in incorrect format!"
        }
        $targetFolder = "python$($Matches.major)$($Matches.minor)"
        # check if it had been fetched before
        if (($logsFileContent -match "`n$pyVer`n") -and (Test-Path -Path $targetFolder) -and (-not $shouldUpdate)) {
            Write-Output "$`n$pyVer`n" >> $logsFilePath
            Write-Output "Skip fetching $pyVer."
            continue
        }
        # provide pythons
        $pyegiPyDir = "$pyegiPythonsDir$targetFolder/"
        if (
            (-not (Test-Path -Path $pyegiPyDir)) -or
            ($shouldUpdate -and
            (Get-ChildItem "$($pyegiPyDir)python.exe").VersionInfo.ProductVersion -ne $pyVer)
        ) {
            # update pythons
            Update-Python $pyVer $targetFolder
            $parameter = "--update-pythons"
        }
        else {
            # copy from pyegi
            Remove-Target-Dir $targetFolder
            $null = New-Item -ItemType SymbolicLink -Path $targetFolder -Target $pyegiPyDir
            $parameter = ""
        }
        # install poetry
        Invoke-Expression "./$targetFolder/python.exe -s -m pip install -U poetry~=1.4 appdirs toml"
        # write logs
        Write-Output "`n$pyVer`n" >> $logsFilePath
    }
    Set-Location ".."

    # run installer
    Set-Location "Installer"
    ../Pythons/python310/python.exe -s ./installer.py --install $parameter
}
finally {
    # set location back to the initial one
    Set-Location $prevPwd
}
