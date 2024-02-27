#!/bin/bash

set -Eeuo pipefail

# This script should simplify modding of Lethal Company without installing any WiNdOWs oNlY sTuPiD StUfF
#
# In Lethal Company directory:
#   - run the script
#   - copy and replace old files in game direcotry with the new content in .mods
#
# If you have installed Steam via Flatpak, then the path is:
#   ~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Lethal Company/
GAMEDIR="$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Lethal Company"

# List of mods
declare -a MODS=(
	"https://thunderstore.io/c/lethal-company/p/2018/LC_API/"
	"https://thunderstore.io/c/lethal-company/p/BepInEx/BepInExPack/"
	"https://thunderstore.io/c/lethal-company/p/RugbugRedfern/Skinwalkers/"
	"https://thunderstore.io/c/lethal-company/p/notnotnotswipez/MoreCompany/"
	"https://thunderstore.io/c/lethal-company/p/Suskitech/AlwaysHearActiveWalkies/"
		"https://thunderstore.io/c/lethal-company/p/FlipMods/ReservedItemSlotCore/"
	"https://thunderstore.io/c/lethal-company/p/FlipMods/ReservedFlashlightSlot/"
	"https://thunderstore.io/c/lethal-company/p/FlipMods/ReservedWalkieSlot/"
	"https://thunderstore.io/c/lethal-company/p/LethalResonance/LETHALRESONANCE/"
		"https://thunderstore.io/c/lethal-company/p/no00ob/LCSoundTool/"
		"https://thunderstore.io/c/lethal-company/p/Hardy/LCMaxSoundsFix/"
		"https://thunderstore.io/c/lethal-company/p/Clementinise/CustomSounds/"
	"https://thunderstore.io/c/lethal-company/p/Owen3H/IntroTweaks/"
	"https://thunderstore.io/c/lethal-company/p/Sligili/More_Emotes/"
		"https://thunderstore.io/c/lethal-company/p/Ozone/Runtime_Netcode_Patcher/"
	"https://thunderstore.io/c/lethal-company/p/LethalPlugging/LethalHaptics/"
	"https://thunderstore.io/c/lethal-company/p/KoderTeh/Boombox_Controller/"
	"https://thunderstore.io/c/lethal-company/p/SnoopCave/I_need_more_Bullets/"
	"https://thunderstore.io/c/lethal-company/p/sunnobunno/LandMineFartReverb/"
	"https://thunderstore.io/c/lethal-company/p/LB3/ChineseJester/"
	"https://thunderstore.io/c/lethal-company/p/QuFix/Lidl_Suit/"
		"https://thunderstore.io/c/lethal-company/p/x753/More_Suits/"
	"https://thunderstore.io/c/lethal-company/p/rileyzzz/Skibidi_Toilet/"
		"https://thunderstore.io/c/lethal-company/p/Evaisa/LethalLib/"
		"https://thunderstore.io/c/lethal-company/p/Evaisa/HookGenPatcher/"
	"https://thunderstore.io/c/lethal-company/p/HoffmanTV/angry_british_bug/"
	"https://thunderstore.io/c/lethal-company/p/PanHouse/LethalClunk/"
	"https://thunderstore.io/c/lethal-company/p/MetalPipeSFX/HornMoan/"
	"https://thunderstore.io/c/lethal-company/p/x753/Peepers/"
)

#==============================
# Do not edit below this point
#==============================

cd "${GAMEDIR}"
OLDDIR="old"
mkdir -p .mods/${OLDDIR}
cd .mods

for MOD in "${MODS[@]}"; do
	NAME=$( echo "${MOD}" | \
		sed -E 's/.*\/p\///g' | \
		sed -E 's/\/$//g' | \
		sed -E 's/\//-/g'
	)
	echo "mod:        ${NAME}"
	DOWNLOAD_LINK=$( curl --silent "${MOD}" | \
		grep "/package/download/" | \
		sed -E 's/.*https/https/g' | \
		sed -E 's/[\/]?".*//g'
	)
	VERSION=$( echo "${DOWNLOAD_LINK}" | sed -E 's/.*\///g' )
	echo "version:    ${VERSION}"

	MODNAME="${NAME}-${VERSION}"
	FILENAME="${MODNAME}.zip"

	# Move old mods into old dir
	if [ -f "${NAME}"*.zip ]; then
		mv ${NAME}* "${OLDDIR}/"
	fi

	# Check if mod is already downloaded
	if [ -f "${OLDDIR}/${FILENAME}" ]; then
		echo "  mod already exists"
		continue
	fi
	echo "  downloading"
	
	# Donwload and unzip
	wget --quiet --continue --output-document="${MODNAME}.zip" "${DOWNLOAD_LINK}"
	unar --quiet "${MODNAME}.zip"
done
