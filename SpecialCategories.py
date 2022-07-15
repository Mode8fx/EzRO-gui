from gatelib import slugify

##################################################
# START EDITING FROM LINE 29 (SpecialCategories) #
##################################################

# This is where you add special categories to further organize your roms.
# A special category allows you to automatically export roms with certain
# keywords to a specific folder, such as "[Unlicensed]" or "[BIOS]".
# You can also choose to ignore roms in a certain category during an export.
# 
# Keep in mind that any roms in a category will ONLY be exported if the category
# is enabled!

class Category:
	def __init__(self, name, keywords, description=None, exclusiveSystems=None):
		self.name = name
		self.keywords = keywords
		if not (isinstance(self.keywords, list) or isinstance(self.keywords, tuple)):
			self.keywords = [self.keywords]
		self.description = description
		self.exclusiveSystems = exclusiveSystems
		self.folderName = slugify(name)



SpecialCategories = [

	Category(
		name = "Unlicensed",
		description = "Include roms marked as Unlicensed, Pirate, or Homebrew.",
		keywords = [
			"(Homebrew",
			"(Pirate",
			"(Unl",
		],
		exclusiveSystems = None,
	),

	Category(
		name = "Unreleased",
		description = None,
		keywords = [
			"(Proto",
		],
		exclusiveSystems = None,
	),

	Category(
		name = "Compilations",
		description = None,
		keywords = [
			"2 Games in 1 -",
			"2 Games in 1! -",
			"2 Disney Games -",
			"2-in-1 Fun Pack -",
			"2 Great Games! -",
			"2 in 1 -",
			"2 in 1 Game Pack -",
			"2 Jeux en 1 -",
			"3 Games in 1 -",
			"4 Games on One Game Pak",
			"Castlevania Double Pack",
			"Combo Pack - ",
			"Crash Superpack -",
			"Crash & Spyro Superpack",
			"Crash & Spyro Super Pack",
			"Double Game! -",
			"Double Pack -",
			"Spyro Superpack -",
		],
		exclusiveSystems = None,
	),

	Category(
		name = "Misc. Programs",
		description = "Include non-game programs such as test programs, SDK files, and SNES enhancement chips.\n\nIf unsure, leave this disabled.",
		keywords = [
			"(Enhancement Chip",
			"(Program",
			"(SDK Build",
			"(Test Program",
			"Production Test Program",
			"Test Cart",
		],
		exclusiveSystems = None,
	),

	Category(
		name = "BIOS",
		description = None,
		keywords = [
			"[BIOS]",
		],
		exclusiveSystems = None,
	),

	Category(
		name = "NES Ports",
		description = "(Only applies to GBA.)\nInclude Classic NES Series, Famicom Mini, Hudson Best Collection, and Kunio-kun Nekketsu Collection emulated ports.\n\nIf unsure, leave this disabled.",
		keywords = [
			"Classic NES Series",
			"Famicom Mini",
			"Hudson Best Collection",
			"Kunio-kun Nekketsu Collection",
		],
		exclusiveSystems = ["Nintendo - Game Boy Advance"],
	),

	Category(
		name = "GBA Video",
		description = None,
		keywords = [
			"Game Boy Advance Video"
		],
		exclusiveSystems = ["Nintendo - Game Boy Advance"],
	),

]

# Specific Attributes are special keywords used when determining the best version
# of a game for 1G1R.
# They are used to denote re-releases that should be considered secondary to
# their original counterparts. As more methods of officially re-releasing games
# come into existence, this list may need to be updated.
SpecificAttributes = [
	"Virtual Console", "Switch Online", "GameCube", "Namcot Collection",
	"Namco Museum Archives", "Kiosk", "iQue", "Sega Channel", "WiiWare",
	"DLC", "Minis", "Promo", "Nintendo Channel", "Nintendo Channel, Alt",
	"DS Broadcast", "Wii Broadcast", "DS Download Station", "Dwnld Sttn",
	"Undumped Japanese Download Station", "WiiWare Broadcast",
	"Disk Writer", "Collection of Mana", "Namco Museum Archives Vol 1",
	"Namco Museum Archives Vol 2", "Castlevania Anniversary Collection",
	"Sega Smash Pack", "Steam Version", "Nintendo Switch", "NP",
	"Genesis Mini", "Mega Drive Mini", "Classic Mini"
]

# General Attributes are special keywords used when determining the best version
# of a game for 1G1R.
# Later versions of a rom are seen as more significant than earlier ones.
# (e.g. "Rev 2" is more significant than "Rev 1")
# You shouldn't have to edit this, but you're free to in case an attribute is
# missing.
GeneralAttributes = [
	"Rev", "Beta", "Demo", "Sample", "Proto", "Alt", "Earlier", "Download Station", "FW", "Reprint"
]