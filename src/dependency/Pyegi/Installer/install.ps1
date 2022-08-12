$ErrorActionPreference = "Stop"

function Expand-Archive($tarFile, $dest) {
    if (-not (Get-Command Expand-7Zip -ErrorAction Ignore)) {
        Install-Package -Scope CurrentUser -Force -ProviderName PowerShellGet 7Zip4PowerShell > $null
    }

    Expand-7Zip $tarFile $dest
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
    # prepare environments
    Set-Location "../Pythons"
    for ($i = 0; $i -lt $pythonVersions.Count; $i++) {
        $pyVer = $pythonVersions[$i]
        # download
        $fileName = "cpython-$pyVer+$packageVersion-$arch-pc-windows-msvc-shared-install_only.tar.gz"
        $url = "https://github.com/indygreg/python-build-standalone/releases/download/$packageVersion/$fileName"
        if (!(Test-Path -Path $fileName)) {
            Invoke-WebRequest -OutFile $fileName $url
        }
        # extract
        $initialFolder = "python"
        if (Test-Path -Path $initialFolder) {
            Remove-Item $initialFolder -Recurse
        }
        Expand-Archive $fileName "."
        Remove-Item $fileName
        $tarFile = $fileName.TrimEnd(".gz")
        Expand-Archive $tarFile "."
        Remove-Item $tarFile
        # rename folder
        if (!($pyVer -match '^(?<major>\d+)\.(?<minor>\d+)')) {
            throw "Python version `"$pyVer`" is in incorrect format!"
        }
        $targetFolder = "python$($Matches.major)$($Matches.minor)"
        if (Test-Path -Path $targetFolder) {
            Remove-Item $targetFolder -Recurse
        }
        Move-Item $initialFolder $targetFolder
        # install poetry
        Invoke-Expression "./$targetFolder/python.exe -s -m pip install -U poetry~=1.1.14 appdirs toml"
    }
    Set-Location ".."

    # run installer
    Set-Location "Installer"
    ../Pythons/python39/python.exe -s ./installer.py --install
}
finally {
    # set location back to the initial one
    Set-Location $prevPwd
}
