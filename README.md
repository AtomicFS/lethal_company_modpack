# Lethal Company Modpack

I am not a creator, nor do I own any of these assets. This is merely a collection of mods to share with friends in convenient manner.

To use this, just place it into game directory. If you are using git to clone this repository make sure git-lfs is installed and enabled.

Sources to all of the files can be found in a `.mods/mods.txt` text file.

## Location

If you have installed Steam via Flatpak, then the path is:

```shell
~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Lethal Company/
```

The resulting directory structure should look something like this:

```shell
~/.var/.../Lethal Company/
├── .git/
├── .mods/
│   ├── update_mods.py
│   └── ...
├── BepInEx/
├── icon.png
├── Lethal Company_Data/
├── Lethal Company.exe
├── MonoBleedingEdge/
└── ...
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
