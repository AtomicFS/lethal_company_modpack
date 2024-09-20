# Lethal Company Modpack

I am not a creator, nor do I own any of these assets. This is merely a collection of mods to share with friends in convenient manner.

To use this, just place it into game directory. If you are using git to clone this repository make sure git-lfs is installed and enabled.

Sources to all of the files can be found in a `.mods/mods.txt` text file.


## Branches
- `master` branch contains no active mods (provices vanilla game)
- `9e` branch contains a selection of active mods


## Location

If you have installed Steam via Flatpak, then the path is:

```shell
~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Lethal Company/
```


## Installation

Go to the direcotry with the game and run:
- `git init`
- clone:
	- with HTTP: `git remote add origin https://github.com/AtomicFS/lethal_company_modpack.git`
	- with SSH: `git remote add origin git@github.com:AtomicFS/lethal_company_modpack.git`
- `git fetch -a`
- `git checkout master`

The resulting directory structure should look something like this:

```shell
~/.var/.../Lethal Company/
├── .git
├── .gitattributes
├── .gitignore
├── 'Lethal Company_Data'
├── 'Lethal Company.exe'
├── .mods
├── MonoBleedingEdge
├── nvngx_dlss.dll
├── NVUnityPlugin.dll
├── README.md
├── UnityCrashHandler64.exe
└── UnityPlayer.dll
```

In case the Flatpak installation does not apply the mods right away, follow this [guide](https://docs.bepinex.dev/articles/advanced/proton_wine.html)


## Python script

Run as any script:

```shell
./update_mods.py
```

It will produce following directories:

- `new-mod-dir`
  - final product, should be copied into the game directory
- `old`
  - stores old versions of mods and `new-mod-dir`
- `up-to-date-mods`
  - local copy of mods so that they do not have to be downloaded every time

### Dependencies

The python script has following dependencies:

- python-requests

And following optional dependencies:

- python-requests-cache
  - handy for development since it caches HTTP requests


## Troubleshooting

### Linux + SWAY
If you are using more than one screen, you might have a problem with mouse not working. If that is the case remove all unused output from your SWAY configuration (~/.config/sway/config) and reload SWAY (by default: SUPER+SHIFT+C).
