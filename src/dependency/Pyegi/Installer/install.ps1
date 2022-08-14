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
    $packageVersion = "20220802"
    $pythonVersions = "3.8.13", "3.9.13", "3.10.6"
    $pyegiPythonsDir = "$($env:APPDATA -replace "\\", "/")/Aegisub/automation/dependency/Pyegi/Pythons/"
    # prepare environments
    Set-Location "../Pythons/"
    for ($i = 0; $i -lt $pythonVersions.Count; $i++) {
        $pyVer = $pythonVersions[$i]
        # determine folder name
        if (-not ($pyVer -match '^(?<major>\d+)\.(?<minor>\d+)')) {
            throw "Python version `"$pyVer`" is in incorrect format!"
        }
        $targetFolder = "python$($Matches.major)$($Matches.minor)"
        # provide pythons
        $pyegiPyDir = "$pyegiPythonsDir$targetFolder/"
        if (
            (-not (Test-Path -Path $pyegiPyDir)) -or
            ($Args[0] -eq "--update-pythons" -and
            (Get-ChildItem "$($pyegiPyDir)python.exe").VersionInfo.ProductVersion -ne $pyVer)
        ) {
            # update pythons
            Update-Python $pyVer $targetFolder
            $parameter = "--update-pythons"
            $shouldUpdate = $true
        }
        else {
            # copy from pyegi
            Remove-Target-Dir $targetFolder
            New-Item -ItemType SymbolicLink -Path $targetFolder -Target $pyegiPyDir
            $parameter = ""
            $shouldUpdate = $false
        }
        # install poetry
        Invoke-Expression "./$targetFolder/python.exe -s -m pip install -U poetry~=1.1.14 appdirs toml"
    }
    Set-Location ".."

    # run installer
    Set-Location "Installer"
    ../Pythons/python39/python.exe -s ./installer.py --install $parameter
}
finally {
    # set location back to the initial one
    Set-Location $prevPwd
}
