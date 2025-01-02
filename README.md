# EzRO

EzRO is a GUI-based rom organizer that allows you to export your local romsets in an organized manner, using a variety of options and settings.
 
By providing a [No-Intro](https://datomatic.no-intro.org/) Parent-Clone DAT file for each system, you can take a local romset (full or partial) and export a curated copy; you can convert a full set into 1G1R for your region, group different releases of a single game together into one folder, automatically unzip roms for emulators that don’t support zipped roms, and more.

<img src="https://github.com/Mode8fx/EzRO-gui/blob/main/screenshots/screenshot%201.png" />

## Features

- Export Full, 1G1R, or Favorites sets for each system
- Create custom region priorities, or choose from a list of defaults
- A wide variety of optional settings
    - Skip games from non-primary regions in 1G1R sets (e.g. skip non-English games)
    - Export all versions of a single game (regions, revisions, etc.) into a single shared folder named after the most significant version
    - Unzip all zipped roms
    - Put games from non-primary regions into a sub-folder named after the region
    - Skip unlicensed, unreleased, BIOS, GBA Video, and more
- Minimize time spent opening folders; save your default rom/DAT file input directories to automatically detect system folders
- Use different settings for each system and save your configs to reload later
- Audit your romsets to automatically rename misnamed roms and know which roms are missing
- Test Export for small storage devices: See how much disk space an export would use before actually exporting

## Questions

### “EzRO”?
“Easy Rom Organizer”. I’ve made multiple iterations of this rom organizer in the past, but this is the first one that uses a GUI.
### What does [insert option here] do?
Move your mouse over pretty much anything and you’ll see a detailed explanation of what it is.
### What is 1G1R? How is it determined?
1G1R, or "1 Game 1 Rom", is an option that allows you to input multiple versions of a game (such as multiple region releases or revisions) and only export the "most significant" version.
Generally speaking, this means the following:
- The highest priority region according to your region settings
- The latest revision/version within this region
- Beta/Prototype/Unlicensed versions of a game are given lower priority
- Rereleases (Virtual Console, etc.) are given lower priority
- Worldwide roms that do not contain a language from your primary region (common in modern collections of older games) are given lower priority
### Can I add my own keywords for 1G1R identification?
Yes. These are included in `settings.ini`, and you can add your own:
- `Compilation`: Compilation releases start with these keywords, such as "Spyro Superpack"
- `Specific Attributes`: These represent specific rereleases of games, such as "Virtual Console" or "Genesis Mini"
- `General Attributes`: These are similar to Specific Attributes, but they cover any attribute that starts with these keywords (e.g. "Rev" covers "Rev 1", "Rev 2", "Rev A", etc.)
### Can I add my own systems to the list? Can I add new nicknames to existing systems?
Yes, you can do both of these by editing `SystemNames.py` (just follow the format that's already in the file).
### Can I add my own special categories in addition to the existing ones like Unlicensed and Unreleased?
Yes. The categories are included in `SpecialCategories.py`, and you can edit them or add your own.
### What DAT files should I use?
This program was designed for use with No-Intro's Parent-Clone DAT files. These can be found on No-Intro's DAT-o-MATIC, specifically the [Daily Downloads](https://datomatic.no-intro.org/?page=download&op=daily) page. At the top of the page, select the Type `P/C XML`, then click "Request". You should be taken to a Download page, which provides a full set of current DAT files. For NES, use the headerless DAT.
### Are disc-based systems supported?
For the most part, no. Since there are many different methods of compressing (or not compressing) games from these systems, and because Redump DAT files are structured differently than No-Intro (and frankly, they contain less information), they are not supported at this time. This could change in the future, but don't count on it.
### Are arcade-based systems supported?
No. For that, you're *much* better off using something like [Clrmamepro](https://mamedev.emulab.it/clrmamepro/) instead.
### I have a feature request/bug report!
Leave an [issue](https://github.com/Mode8fx/EzRO-gui/issues) and I’ll look into it.

## Example Output

For example, using the default settings, your local romset containing:
```
C:/Roms/Sega Genesis/My Game 1 (USA).zip
C:/Roms/Sega Genesis/My Game 1 (USA) (Rev 1).zip
C:/Roms/Sega Genesis/My Game 1 (Europe).zip
C:/Roms/Sega Genesis/My Game 1 (Japan).zip
C:/Roms/Sega Genesis/My Game 2 (Europe).zip
C:/Roms/Sega Genesis/My Game 2 (Japan).zip
C:/Roms/Sega Genesis/My Game 3 (Japan).zip
C:/Roms/Sega Genesis/My Game 4 (China).zip
```
... provided you have a DAT file for the system:
```
C:/No-Intro Database/Sega Genesis.dat
```
... can be copied and sorted as:
```
F:/Roms/Sega Genesis/My Game 1/My Game 1 (USA).zip
F:/Roms/Sega Genesis/My Game 1/My Game 1 (USA) (Rev 1).zip
F:/Roms/Sega Genesis/My Game 1/My Game 1 (Europe).zip
F:/Roms/Sega Genesis/My Game 1/My Game 1 (Japan).zip
F:/Roms/Sega Genesis/My Game 2/My Game 2 (Europe).zip
F:/Roms/Sega Genesis/My Game 2/My Game 2 (Japan).zip
F:/Roms/Sega Genesis/[Japan]/My Game 3/My Game 3 (Japan).zip
F:/Roms/Sega Genesis/[Japan]/My Game 3/My Game 3 (China).zip
F:/Roms/Sega Genesis/[Other (non-English)]/My Game 4/My Game 4 (China).zip
```
By default, English-speaking regions and roms with the ("En") tag make up the primary region group. All versions of My Game 1 and My Game 2 are stored in the root folder since a version of each game exists within the primary region group. All versions of My Game 3 are stored in the [Japan] folder since the Japan region group is that game's best valid region. Since the only region represented by My Game 4 is China, and China is not part of a region group, it goes into the miscellaneous [Other (non-English)] folder. Additionally, as previously mentioned, games with primary region group releases are not exported to a region folder; however, this behavior can be altered by disabling the default "Do Not Create Folder for Primary Region" option, resulting in the following:
```
F:/Roms/Sega Genesis/[USA]/My Game 1/My Game 1 (USA).zip
F:/Roms/Sega Genesis/[USA]/My Game 1/My Game 1 (USA) (Rev 1).zip
F:/Roms/Sega Genesis/[USA]/My Game 1/My Game 1 (Europe).zip
F:/Roms/Sega Genesis/[USA]/My Game 1/My Game 1 (Japan).zip
F:/Roms/Sega Genesis/[Europe]/My Game 2/My Game 2 (Europe).zip
F:/Roms/Sega Genesis/[Europe]/My Game 2/My Game 2 (Japan).zip
F:/Roms/Sega Genesis/[Japan]/My Game 3/My Game 3 (Japan).zip
F:/Roms/Sega Genesis/[Other (non-English)]/My Game 4/My Game 4 (China).zip
```

## Credits/Compilation
In addition to the Python libraries shown in [requirements.txt](https://github.com/Mode8fx/EzRO-gui/blob/main/requirements.txt), EzRO also uses [ttkScrollableNotebook by muhammeteminturgut](https://github.com/muhammeteminturgut/ttkScrollableNotebook). This library and its license have been included in the release version of EzRO.

## Legal Disclaimer
This is not a rom downloader, nor does it include any information on how to obtain roms. You are responsible for legally obtaining your own roms for use with this program.
