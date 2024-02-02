import pathlib
import pygubu
try:
    import Tkinter as tk
    import Tkinter.ttk as ttk
    from Tkinter.messagebox import showinfo, showerror, askyesno, askokcancel
    from Tkinter import Toplevel
    from Tkinter.filedialog import askopenfilename, asksaveasfilename
except:
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter.messagebox import showinfo, showerror, askyesno, askokcancel
    from tkinter import Toplevel
    from tkinter.filedialog import askopenfilename, asksaveasfilename
from Libraries.ttkScrollableNotebook.ScrollableNotebook import *
from pygubu.widgets.editabletreeview import EditableTreeview
from pygubu.widgets.pathchooserinput import PathChooserInput
from pygubu.widgets.scrolledframe import ScrolledFrame
import pygubu.widgets.simpletooltip as tooltip
import traceback

from os import path, mkdir, listdir, remove, walk, rename, rmdir
import re
import xml.etree.ElementTree as ET
import zipfile
import rarfile
rarfile.UNRAR_TOOL = "tools/UnRAR.exe"
import py7zr
import patoolib
import shutil
from pathlib import Path as plpath
from math import ceil
from gatelib import *
from filehash import FileHash
import configparser
from dateutil.parser import parse as dateParse
import binascii
from time import sleep
from datetime import datetime
import webbrowser

versionNum = 1.22

archiveTypes = [".zip", ".rar", ".7z"]

progFolder = getCurrFolder()
sys.path.append(progFolder)

# tk.Tk().withdraw()
noSystemNamesFileFlag = False
try:
    from SystemNames import *
except:
    noSystemNamesFileFlag = True
    from SystemNamesDefault import *

noSpecialCategoriesFileFlag = False
try:
    from SpecialCategories import *
except:
    noSpecialCategoriesFileFlag = True
    from SpecialCategoriesDefault import *
badSpecialFolderPrefixFlag = (specialFolderPrefix != slugify(specialFolderPrefix, stripValue=False).lstrip())
specialFolderPrefix = slugify(specialFolderPrefix, stripValue=False).lstrip()
badSpecialFolderSuffixFlag = (specialFolderSuffix != slugify(specialFolderSuffix, stripValue=False).rstrip())
specialFolderSuffix = slugify(specialFolderSuffix, stripValue=False).rstrip()
specialCategoriesGeneral = [sc for sc in SpecialCategories if sc.exclusiveSystems is None]
specialCategoriesExclusive = [sc for sc in SpecialCategories if sc.exclusiveSystems is not None]

crcHasher = FileHash('crc32')

defaultSettingsFile = path.join(progFolder, "settings.ini")
regionsFile = path.join(progFolder, "regions.ini")
logFolder = path.join(progFolder, "Logs")

systemListStr = "\"\" "+" ".join(["\""+sn+"\"" for sn in systemNamesDict.keys() if systemNamesDict[sn][0] != "Advanced"])



PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "EzRO.ui"

class EzroApp:
    def __init__(self, master=None):

        # Menu Bar
        menubar = tk.Menu(tk_root, tearoff=0)
        fileMenu = tk.Menu(menubar, tearoff=0)
        helpMenu = tk.Menu(menubar, tearoff=0)
        helpMenu.add_command(label="View Help...", command=self.menu_viewHelp)
        helpMenu.add_separator()
        helpMenu.add_command(label="About...", command=self.menu_viewAbout)
        helpMenu.add_command(label="External Libraries...", command=self.menu_viewExternalLibraries)
        helpMenu.add_command(label="Get No-Intro DAT Files...", command=self.menu_getDATFiles)
        menubar.add_cascade(label="Help", menu=helpMenu)
        tk_root.config(menu=menubar)

        # build ui
        self.Main_Notebook = ttk.Notebook(master)
        self.Export_Frame = ttk.Frame(self.Main_Notebook)
        self.Export_System_Combobox = ttk.Combobox(self.Export_Frame)
        self.systemChoice = tk.StringVar(value='')
        self.Export_System_Combobox.configure(state='readonly', textvariable=self.systemChoice, values=systemListStr, width='50', height=25)
        self.Export_System_Combobox.place(anchor='e', relx='.375', rely='.075', x='0', y='0')
        self.Export_System_Button = ttk.Button(self.Export_Frame)
        self.Export_System_Button.configure(text='Add System')
        self.Export_System_Button.place(anchor='e', relx='.45', rely='.075', x='0', y='0')
        self.Export_System_Button.configure(command=self.export_addSystem)
        self.Export_ShowAdvancedSystems = ttk.Checkbutton(self.Export_Frame)
        self.showAdvancedSystems = tk.IntVar(value=False)
        self.Export_ShowAdvancedSystems.configure(text='Show Advanced Systems', variable=self.showAdvancedSystems)
        self.Export_ShowAdvancedSystems.place(anchor='w', relx='.46', rely='.075', x='0', y='0')
        self.Export_ShowAdvancedSystems.configure(command=self.export_toggleAdvancedSystems)
        self.Export_SaveLayout_Button = ttk.Button(self.Export_Frame)
        self.Export_SaveLayout_Button.configure(text='Save System Tabs')
        self.Export_SaveLayout_Button.place(anchor='e', relx='.78', rely='.075', x='0', y='0')
        self.Export_SaveLayout_Button.configure(command=self.export_saveSystemLoadout)
        self.Export_LoadLayout_Button = ttk.Button(self.Export_Frame)
        self.Export_LoadLayout_Button.configure(text='Load System Tabs')
        self.Export_LoadLayout_Button.place(anchor='w', relx='.80', rely='.075', x='0', y='0')
        self.Export_LoadLayout_Button.configure(command=self.export_loadSystemLoadout)
        self.Export_Systems = ScrollableNotebook(self.Export_Frame, wheelscroll=True, tabmenu=True)

        self.initVars()

        self.Export_Systems.configure(height='200', width='200')
        self.Export_Systems.place(anchor='nw', relheight='.7', relwidth='.9', relx='.05', rely='.15', x='0', y='0')
        self.Export_AuditThis = ttk.Button(self.Export_Frame)
        self.Export_AuditThis.configure(text='Audit This System')
        self.Export_AuditThis.place(anchor='w', relx='.05', rely='.925', x='0', y='0')
        self.Export_AuditThis.configure(command=self.export_auditSystem)
        self.Export_AuditAll = ttk.Button(self.Export_Frame)
        self.Export_AuditAll.configure(text='Audit All Open Systems')
        self.Export_AuditAll.place(anchor='w', relx='.15', rely='.925', x='0', y='0')
        self.Export_AuditAll.configure(command=self.export_auditAllSystems)
        self.Export_TestExport = ttk.Checkbutton(self.Export_Frame)
        self.isTestExport = tk.IntVar(value=False)
        self.Export_TestExport.configure(text='Test Export', variable=self.isTestExport)
        self.Export_TestExport.place(anchor='e', relx='.72', rely='.925', x='0', y='0')
        self.Export_TestExport.configure(command=self.export_toggleTestExport)
        self.Export_ExportThis = ttk.Button(self.Export_Frame)
        self.Export_ExportThis.configure(text='Export This System')
        self.Export_ExportThis.place(anchor='e', relx='.825', rely='.925', x='0', y='0')
        self.Export_ExportThis.configure(command=self.export_exportSystem)
        self.Export_ExportAll = ttk.Button(self.Export_Frame)
        self.Export_ExportAll.configure(text='Export All Open Systems')
        self.Export_ExportAll.place(anchor='e', relx='.95', rely='.925', x='0', y='0')
        self.Export_ExportAll.configure(command=self.export_exportAllSystems)
        self.Export_AuditHelp = ttk.Button(self.Export_Frame)
        self.Export_AuditHelp.configure(text='?', width='2')
        self.Export_AuditHelp.place(anchor='w', relx='.275', rely='.925', x='0', y='0')
        self.Export_AuditHelp.configure(command=self.export_auditHelp)
        self.Export_Frame.configure(height='200', width='200')
        self.Export_Frame.pack(side='top')
        self.Main_Notebook.add(self.Export_Frame, text='Export')
        # Favorites Tab is unused
        # self.Favorites_Frame = ttk.Frame(self.Main_Notebook)
        # self.Favorites_Load = ttk.Button(self.Favorites_Frame)
        # self.Favorites_Load.configure(text='Load Existing List...')
        # self.Favorites_Load.place(anchor='w', relx='.1', rely='.075', x='0', y='0')
        # self.Favorites_Load.configure(command=self.favorites_loadList)
        # self.Favorites_System_Label = ttk.Label(self.Favorites_Frame)
        # self.Favorites_System_Label.configure(text='System')
        # self.Favorites_System_Label.place(anchor='w', relx='.1', rely='.15', x='0', y='0')
        # self.Favorites_System_Combobox = ttk.Combobox(self.Favorites_Frame)
        # self.favoritesSystemChoice = tk.StringVar(value='')
        # self.Favorites_System_Combobox.configure(state='readonly', textvariable=self.favoritesSystemChoice, values=systemListStr, width='50')
        # self.Favorites_System_Combobox.place(anchor='w', relx='.15', rely='.15', x='0', y='0')
        # self.Favorites_List = EditableTreeview(self.Favorites_Frame)
        # self.Favorites_List.place(anchor='nw', relheight='.65', relwidth='.8', relx='.1', rely='.2', x='0', y='0')
        # self.Favorites_Add = ttk.Button(self.Favorites_Frame)
        # self.Favorites_Add.configure(text='Add Files...')
        # self.Favorites_Add.place(anchor='w', relx='.1', rely='.925', x='0', y='0')
        # self.Favorites_Add.configure(command=self.favorites_addFiles)
        # self.Favorites_Save = ttk.Button(self.Favorites_Frame)
        # self.Favorites_Save.configure(text='Save List As...')
        # self.Favorites_Save.place(anchor='e', relx='.9', rely='.925', x='0', y='0')
        # self.Favorites_Save.configure(command=self.favorites_saveList)
        # self.Favorites_Frame.configure(height='200', width='200')
        # self.Favorites_Frame.pack(side='top')
        # self.Main_Notebook.add(self.Favorites_Frame, text='Favorites')
        self.Config_Frame = ttk.Frame(self.Main_Notebook)
        self.Config_Default_SaveChanges = ttk.Button(self.Config_Frame)
        self.Config_Default_SaveChanges.configure(text='Save Changes')
        self.Config_Default_SaveChanges.place(anchor='e', relx='.95', rely='.925', x='0', y='0')
        self.Config_Default_SaveChanges.configure(command=self.settings_saveChanges)
        self.Config_Notebook = ttk.Notebook(self.Config_Frame)
        self.Config_Default_Frame = ttk.Frame(self.Config_Notebook)
        self.Config_Default_DATDir_Label = ttk.Label(self.Config_Default_Frame)
        self.Config_Default_DATDir_Label.configure(text='Input No-Intro DAT Directory')
        self.Config_Default_DATDir_Label.grid(column='0', padx='20', pady='10', row='0', sticky='w')
        self.Config_Default_DATDir_PathChooser = PathChooserInput(self.Config_Default_Frame)
        self.g_datFilePath = tk.StringVar(value='')
        self.Config_Default_DATDir_PathChooser.configure(textvariable=self.g_datFilePath, type='directory')
        self.Config_Default_DATDir_PathChooser.grid(column='0', ipadx='75', padx='200', pady='10', row='0', sticky='w')
        self.Config_Default_RomsetDir_Label = ttk.Label(self.Config_Default_Frame)
        self.Config_Default_RomsetDir_Label.configure(text='Input Romset Directory')
        self.Config_Default_RomsetDir_Label.grid(column='0', padx='20', pady='10', row='1', sticky='w')
        self.Config_Default_RomsetDir_PathChooser = PathChooserInput(self.Config_Default_Frame)
        self.g_romsetFolderPath = tk.StringVar(value='')
        self.Config_Default_RomsetDir_PathChooser.configure(textvariable=self.g_romsetFolderPath, type='directory')
        self.Config_Default_RomsetDir_PathChooser.grid(column='0', ipadx='75', padx='200', pady='10', row='1', sticky='w')
        self.Config_Default_IncludeOtherRegions = ttk.Checkbutton(self.Config_Default_Frame)
        self.g_includeOtherRegions = tk.IntVar(value=False)
        self.Config_Default_IncludeOtherRegions.configure(text='(1G1R) Include Games from Non-Primary Regions', variable=self.g_includeOtherRegions)
        self.Config_Default_IncludeOtherRegions.grid(column='0', padx='20', pady='10', row='2', sticky='w')
        self.Config_Default_Include = ttk.Labelframe(self.Config_Default_Frame)
        self.Config_Default_IncludeSpecial = []
        self.g_includeSpecial = []
        for i in range(len(SpecialCategories)):
            self.Config_Default_IncludeSpecial.append(ttk.Checkbutton(self.Config_Default_Include))
            self.g_includeSpecial.append(tk.IntVar(value=False))
            self.Config_Default_IncludeSpecial[i].configure(text=SpecialCategories[i].name, variable=self.g_includeSpecial[i])
            currCol = i%3
            currRow = i//3
            self.Config_Default_IncludeSpecial[i].grid(column=currCol, padx=10, pady=10, row=currRow, sticky='w')
        self.Config_Default_Include.configure(text='Include')
        self.Config_Default_Include.grid(column='0', padx='20', pady='10', row='3', sticky='w')
        self.Config_Default_Separator = ttk.Separator(self.Config_Default_Frame)
        self.Config_Default_Separator.configure(orient='vertical')
        self.Config_Default_Separator.place(anchor='center', relheight='.95', relx='.5', rely='.5', x='0', y='0')
        self.Config_Default_ExtractArchives = ttk.Checkbutton(self.Config_Default_Frame)
        self.g_extractArchives = tk.IntVar(value=False)
        self.Config_Default_ExtractArchives.configure(text='Extract Compressed Roms', variable=self.g_extractArchives)
        self.Config_Default_ExtractArchives.place(anchor='nw', relx='.651', rely='.03', x='0', y='0')
        self.Config_Default_ParentFolder = ttk.Checkbutton(self.Config_Default_Frame)
        self.g_parentFolder = tk.IntVar(value=False)
        self.Config_Default_ParentFolder.configure(text='Create Game Folder for Each Game', variable=self.g_parentFolder)
        self.Config_Default_ParentFolder.place(anchor='nw', relx='.651', rely='.132', x='0', y='0')
        self.Config_Default_SortByPrimaryRegion = ttk.Checkbutton(self.Config_Default_Frame)
        self.g_sortByPrimaryRegion = tk.IntVar(value=False)
        self.Config_Default_SortByPrimaryRegion.configure(text='Create Region Folders', variable=self.g_sortByPrimaryRegion)
        self.Config_Default_SortByPrimaryRegion.place(anchor='nw', relx='.651', rely='.234', x='0', y='0')
        self.Config_Default_PrimaryRegionInRoot = ttk.Checkbutton(self.Config_Default_Frame)
        self.g_primaryRegionInRoot = tk.IntVar(value=False)
        self.Config_Default_PrimaryRegionInRoot.configure(text='Do Not Create Folder for Primary Regions', variable=self.g_primaryRegionInRoot)
        self.Config_Default_PrimaryRegionInRoot.place(anchor='nw', relx='.651', rely='.336', x='0', y='0')
        self.Config_Default_SpecialCategoryFolder = ttk.Checkbutton(self.Config_Default_Frame)
        self.g_specialCategoryFolder = tk.IntVar(value=False)
        self.Config_Default_SpecialCategoryFolder.configure(text='Create Folders for Special Categories', variable=self.g_specialCategoryFolder)
        self.Config_Default_SpecialCategoryFolder.place(anchor='nw', relx='.651', rely='.438', x='0', y='0')
        self.Config_Default_LetterFolder = ttk.Checkbutton(self.Config_Default_Frame)
        self.g_letterFolder = tk.IntVar(value=False)
        self.Config_Default_LetterFolder.configure(text='Create Letter Folders', variable=self.g_letterFolder)
        self.Config_Default_LetterFolder.place(anchor='nw', relx='.651', rely='.540', x='0', y='0')
        self.Config_Default_OverwriteDuplicates = ttk.Checkbutton(self.Config_Default_Frame)
        self.g_overwriteDuplicates = tk.IntVar(value=False)
        self.Config_Default_OverwriteDuplicates.configure(text='Overwrite Duplicate Files', variable=self.g_overwriteDuplicates)
        self.Config_Default_OverwriteDuplicates.place(anchor='nw', relx='.651', rely='.642', x='0', y='0')
        self.Config_Default_Frame.configure(height='200', width='200')
        self.Config_Default_Frame.pack(side='top')
        self.Config_Notebook.add(self.Config_Default_Frame, text='Default Settings')
        self.Config_Region_Frame = ScrolledFrame(self.Config_Notebook, scrolltype='vertical')
        self.Config_Region_Choice_RemoveButton_Tertiary = ttk.Button(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_RemoveButton_Tertiary.configure(state='disabled', text='X', width='2')
        self.Config_Region_Choice_RemoveButton_Tertiary.grid(column='0', padx='20', pady='10', row='98', sticky='w')
        self.Config_Region_Choice_Name_Label_Tertiary = ttk.Label(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Name_Label_Tertiary.configure(text='Region Group')
        self.Config_Region_Choice_Name_Label_Tertiary.grid(column='0', padx='130', pady='10', row='98', sticky='w')
        self.Config_Region_Choice_Name_Entry_Tertiary = ttk.Entry(self.Config_Region_Frame.innerframe)
        self.regionGroupTertiary = tk.StringVar(value='')
        self.Config_Region_Choice_Name_Entry_Tertiary.configure(textvariable=self.regionGroupTertiary)
        self.Config_Region_Choice_Name_Entry_Tertiary.grid(column='0', padx='220', pady='10', row='98', sticky='w')
        self.Config_Region_Choice_Type_Label_Tertiary = ttk.Label(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Type_Label_Tertiary.configure(text='Priority Type')
        self.Config_Region_Choice_Type_Label_Tertiary.grid(column='0', padx='380', pady='10', row='98', sticky='w')
        self.Config_Region_Choice_Type_Combobox_Tertiary = ttk.Combobox(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Type_Combobox_Tertiary.configure(state='disabled', values='"Tertiary"', width='12')
        self.Config_Region_Choice_Type_Combobox_Tertiary.grid(column='0', padx='465', pady='10', row='98', sticky='w')
        self.Config_Region_Choice_Type_Combobox_Tertiary.current(0)
        self.Config_Region_AddNewRegionCategory = ttk.Button(self.Config_Region_Frame.innerframe)
        self.Config_Region_AddNewRegionCategory.configure(text='+ Add New Region Category')
        self.Config_Region_AddNewRegionCategory.grid(column='0', padx='20', pady='10', row='99', sticky='w')
        self.Config_Region_AddNewRegionCategory.configure(command=self.settings_region_addNewRegionCategory)
        self.Config_Region_Help = ttk.Button(self.Config_Region_Frame.innerframe)
        self.Config_Region_Help.configure(text='?', width='2')
        self.Config_Region_Help.grid(column='0', padx='200', pady='10', row='99', sticky='w')
        self.Config_Region_Help.configure(command=self.settings_region_help)
        self.Config_Region_Template_Combobox = ttk.Combobox(self.Config_Region_Frame.innerframe)
        self.templateChoice = tk.StringVar(value='')
        self.Config_Region_Template_Combobox.configure(state='readonly', textvariable=self.templateChoice, values='"" "English" "English + Secondary" "English (USA Focus)" "English (Europe Focus)" "Japanese" "Japanese + Secondary"')
        self.Config_Region_Template_Combobox.place(anchor='e', x=int(960*screenHeightMult), y=int(470*screenHeightMult))
        self.Config_Region_Template_Apply = ttk.Button(self.Config_Region_Frame.innerframe)
        self.Config_Region_Template_Apply.configure(text='Apply Template')
        self.Config_Region_Template_Apply.place(anchor='e', x=int(1065*screenHeightMult), y=int(470*screenHeightMult))
        self.Config_Region_Template_Apply.configure(command=self.config_region_applyTemplate)
        self.Config_Region_Frame.configure(usemousewheel=True)
        self.Config_Region_Frame.pack(side='top')
        self.Config_Notebook.add(self.Config_Region_Frame, text='Region Settings')
        self.Config_Notebook.configure(height='200', width='200')
        self.Config_Notebook.place(anchor='nw', relheight='.8', relwidth='.9', relx='.05', rely='.05', x='0', y='0')
        self.Config_Frame.configure(height='200', width='200')
        self.Config_Frame.pack(side='top')
        self.Main_Notebook.add(self.Config_Frame, text='Config')
        self.Main_Notebook.bind('<<NotebookTabChanged>>', self.changeMainTab, add='')
        # self.Main_Notebook.configure(height=int(675*screenHeightMult), width=int(1200*screenHeightMult))
        self.Main_Notebook.grid(column='0', row='0')
        self.Main_Notebook.place(relheight='1', relwidth='1')
        if noSystemNamesFileFlag:
            showerror("EzRO", "Valid SystemNames.py file not found. Using default system list.")
        if noSpecialCategoriesFileFlag:
            showerror("EzRO", "Valid SpecialCategories.py file not found. Using default categories list.")
        if badSpecialFolderPrefixFlag:
            showerror("EzRO", "Warning: Invalid special folder prefix. Please change it in SpecialCategories.py.\n\nFor now, prefix has temporarily been changed to \""+specialFolderPrefix+"\".")
        if badSpecialFolderSuffixFlag:
            showerror("EzRO", "Warning: Invalid special folder suffix. Please change it in SpecialCategories.py.\n\nFor now, suffix has temporarily been changed to \""+specialFolderSuffix+"\".")
        # Tooltips
        tooltip.create(self.Export_ShowAdvancedSystems, 'Show systems that are difficult or uncommon to emulate, and systems that often do not make use of No-Intro DAT files.')
        tooltip.create(self.Export_TestExport, 'For testing; if enabled, roms will NOT be exported. This allows you to see how many roms would be exported and how much space they would take up without actually exporting anything.\n\nIf unsure, leave this disabled.')
        tooltip.create(self.Config_Default_DATDir_Label, 'The directory containing No-Intro DAT files for each system. These contain information about each rom, which is used in both exporting and auditing.\n\nIf this is provided, the \"Export\" tab will attempt to automatically match DAT files from this directory with each system so you don\'t have to input them manually.')
        tooltip.create(self.Config_Default_RomsetDir_Label, 'The directory containing your rom directories for each system.\n\nIf this is provided, the \"Export\" tab will attempt to automatically match folders from this directory with each system so you don\'t have to input them manually.')
        tooltip.create(self.Config_Default_ExtractArchives, 'If enabled, any roms from your input romset that are contained in zipped archives (ZIP, RAR, 7z) will be extracted during export.\n\nUseful if your output device does not support zipped roms.\n\nIf unsure, leave this disabled.')
        tooltip.create(self.Config_Default_ParentFolder, 'If enabled, each rom will be exported to a parent folder with the same name as its primary region release.\n\nFor example, \"Legend of Zelda, The (USA)\" and \"Zelda no Densetsu 1 - The Hyrule Fantasy (Japan)\" will both be exported to a folder titled \"Legend of Zelda, The\".\n\nIf \"Create Region Folders\" or \"Create Letter Folders\" is enabled, the game folder will be placed according to the game\'s highest-priority region.')
        tooltip.create(self.Config_Default_SortByPrimaryRegion, 'If enabled, each rom will be exported to a parent folder named after its highest-priority region.\n\nFor example, if your order of region priority is USA->Europe->Japan, then \"Golden Sun (USA, Europe)\" will be exported to a folder titled \"'+specialFolderPrefix+'USA'+specialFolderSuffix+'\".')
        tooltip.create(self.Config_Default_PrimaryRegionInRoot, '(Only applies if \"Create Region Folders\" is enabled.)\n\nIf enabled, a region folder will NOT be created for your primary regions.\n\nFor example, if you have Europe set as a primary region, then Europe roms will not be exported to a [Europe] folder, and will instead be placed directly in the output folder.\n\nIf unsure, leave this enabled.')
        tooltip.create(self.Config_Default_SpecialCategoryFolder, 'If enabled, all exported roms that are part of a special category (Unlicensed, Unreleased, etc.) will be exported to a parent folder named after that category. There will be multiple nested folders if a game belongs to multiple special categories.\n\nIf unsure, leave this enabled.')
        tooltip.create(self.Config_Default_LetterFolder, 'If enabled, each rom will be exported to a parent folder named after its first letter.\n\nFor example, \"Castlevania (USA)\" will be exported to a [C] folder.\n\nIf unsure, leave this disabled.')
        tooltip.create(self.Config_Default_OverwriteDuplicates, 'If enabled: If a rom in the output directory with the same name as an exported rom already exists, it will be overwritten by the new export.\n\nIf disabled: The export will not overwrite matching roms in the output directory.\n\nIf unsure, leave this disabled.')
        tooltip.create(self.Config_Default_IncludeOtherRegions, '(Only applies to 1G1R export.)\n\nIf enabled: In the event that a game does not contain a rom from your region (e.g. your primary region is USA but the game is a Japan-only release), a secondary region will be used according to your Region/Language Priority Order.\n\nIf disabled: In the event that a game does not contain a rom from your region, the game is skipped entirely.\n\nIf you only want to export roms from your own region, disable this.')
        for i in range(len(SpecialCategories)):
            if SpecialCategories[i].description is not None:
                tooltip.create(self.Config_Default_IncludeSpecial[i], SpecialCategories[i].description)
        tooltip.create(self.Config_Region_Choice_Name_Label_Tertiary, 'The name of the region group. If \"Create Region Folders\" is enabled, then games marked as one of this group\'s region tags will be exported to a folder named after this group, surround by brackets (e.g. [World], [USA], etc).')
        tooltip.create(self.Config_Region_Choice_Type_Label_Tertiary, 'The type of region group.\n\nPrimary: The most significant region; 1G1R exports will prioritize this. If there are multiple Primary groups, then higher groups take priority.\n\nSecondary: \"Backup\" regions that will not be used in a 1G1R export unless no Primary-group version of a game exists, and \"Include Games from Non-Primary Regions\" is also enabled. If there are multiple Secondary groups, then higher groups take priority.\n\nTertiary: Any known region/language tag that is not part of a Primary/Secondary group is added to the Tertiary group by default. This is functionally the same as a Secondary group.')
        # Main widget
        self.mainwindow = self.Main_Notebook
        master.protocol("WM_DELETE_WINDOW", sys.exit) # Why does this not work automatically?
        # Other initialization
        self.isExport = True
        if not path.exists(defaultSettingsFile):
            self.createDefaultSettings()
        if not path.exists(regionsFile):
            self.createRegionSettings()
        self.loadConfig()

    def run(self):
        self.mainwindow.mainloop()

    #########################
    # EXPORT (GUI Handling) #
    #########################

    def initVars(self):
        self.recentlyVerified = False
        self.exportTabNum = 0
        self.exportSystemNames = []
        self.Export_ScrolledFrame_ = []
        self.Export_DAT_Label_ = []
        self.Export_DAT_PathChooser_ = []
        self.datFilePathChoices = []
        self.Export_Romset_Label_ = []
        self.Export_Romset_PathChooser_ = []
        self.romsetFolderPathChoices = []
        self.Export_OutputDir_Label_ = []
        self.Export_OutputDir_PathChooser_ = []
        self.outputFolderDirectoryChoices = []
        self.Export_Separator_ = []
        self.Export_OutputType_Label_ = []
        self.Export_OutputType_Combobox_ = []
        self.outputTypeChoices = []
        self.Export_includeOtherRegions_ = []
        self.includeOtherRegionsChoices = []
        self.Export_FromList_Label_ = []
        self.Export_FromList_PathChooser_ = []
        self.romListFileChoices = []
        self.Export_IncludeFrame_ = []
        self.Export_IncludeSpecial_ = []
        self.includeSpecialChoices = []
        for i in range(len(SpecialCategories)):
            self.Export_IncludeSpecial_.append([])
            self.includeSpecialChoices.append([])
        self.Export_ExtractArchives_ = []
        self.extractArchivesChoices = []
        self.Export_ParentFolder_ = []
        self.parentFolderChoices = []
        self.Export_SortByPrimaryRegion_ = []
        self.sortByPrimaryRegionChoices = []
        self.Export_SpecialCategoryFolder_ = []
        self.Export_LetterFolder_ = []
        self.specialCategoryFolderChoices = []
        self.letterFolderChoices = []
        self.Export_PrimaryRegionInRoot_ = []
        self.primaryRegionInRootChoices = []
        self.Export_OverwriteDuplicates_ = []
        self.overwriteDuplicatesChoices = []
        self.Export_RemoveSystem_ = []
        self.regionNum = 0
        self.Config_Region_Choice_RemoveButton_ = []
        self.Config_Region_Choice_UpButton_ = []
        self.Config_Region_Choice_DownButton_ = []
        self.Config_Region_Choice_Name_Label_ = []
        self.Config_Region_Choice_Name_Entry_ = []
        self.regionGroupNames = []
        self.Config_Region_Choice_Type_Label_ = []
        self.Config_Region_Choice_Type_Combobox_ = []
        self.regionPriorityTypes = []
        self.Config_Region_Choice_Tags_Label_ = []
        self.Config_Region_Choice_Tags_Entry_ = []
        self.regionTags = []

    def export_toggleAdvancedSystems(self):
        global systemListStr
        if self.showAdvancedSystems.get():
            systemListStr = "\"\" "+" ".join(["\""+sn+"\"" for sn in systemNamesDict.keys()])
        else:
            systemListStr = "\"\" "+" ".join(["\""+sn+"\"" for sn in systemNamesDict.keys() if systemNamesDict[sn][0] != "Advanced"])
        self.Export_System_Combobox.configure(values=systemListStr)

    def addSystemTab(self, systemName="New System", datFilePath="", romsetFolderPath="", outputFolderDirectory="",
            outputType="All", includeOtherRegions=False, romList="", includeSpecial=[], extractArchives=False,
            parentFolder=False, sortByPrimaryRegion=False, primaryRegionInRoot=False, specialCategoryFolder=False,
            letterFolder=False, overwriteDuplicates=False):
        self.exportSystemNames.append(systemName)
        self.Export_ScrolledFrame_.append(ScrolledFrame(self.Export_Systems, scrolltype='both'))
        self.Export_DAT_Label_.append(ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.Export_DAT_Label_[self.exportTabNum].configure(text='Input No-Intro DAT')
        self.Export_DAT_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='0', sticky='w')
        self.Export_DAT_PathChooser_.append(PathChooserInput(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.setSystemDAT(systemName, datFilePath)
        self.Export_DAT_PathChooser_[self.exportTabNum].configure(mustexist='true', state='normal', textvariable=self.datFilePathChoices[self.exportTabNum], type='file', filetypes=[('DAT Files', '*.dat')])
        self.Export_DAT_PathChooser_[self.exportTabNum].grid(column='0', ipadx='90', padx='150', pady='10', row='0', sticky='w')
        self.Export_Romset_Label_.append(ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.Export_Romset_Label_[self.exportTabNum].configure(text='Input Romset')
        self.Export_Romset_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='1', sticky='w')
        self.Export_Romset_PathChooser_.append(PathChooserInput(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.setInputRomsetDir(systemName, romsetFolderPath)
        self.Export_Romset_PathChooser_[self.exportTabNum].configure(mustexist='true', state='normal', textvariable=self.romsetFolderPathChoices[self.exportTabNum], type='directory')
        self.Export_Romset_PathChooser_[self.exportTabNum].grid(column='0', ipadx='90', padx='150', pady='10', row='1', sticky='w')
        self.Export_OutputDir_Label_.append(ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.Export_OutputDir_Label_[self.exportTabNum].configure(text='Output Directory')
        self.Export_OutputDir_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='2', sticky='w')
        self.Export_OutputDir_PathChooser_.append(PathChooserInput(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.outputFolderDirectoryChoices.append(tk.StringVar(value=''))
        self.outputFolderDirectoryChoices[self.exportTabNum].set(outputFolderDirectory)
        self.Export_OutputDir_PathChooser_[self.exportTabNum].configure(mustexist='true', state='normal', textvariable=self.outputFolderDirectoryChoices[self.exportTabNum], type='directory')
        self.Export_OutputDir_PathChooser_[self.exportTabNum].grid(column='0', ipadx='90', padx='150', pady='10', row='2', sticky='w')
        self.Export_Separator_.append(ttk.Separator(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.Export_Separator_[self.exportTabNum].configure(orient='vertical')
        self.Export_Separator_[self.exportTabNum].place(anchor='center', relheight='.95', relx='.5', rely='.5', x='0', y='0')
        self.Export_OutputType_Label_.append(ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.Export_OutputType_Label_[self.exportTabNum].configure(text='Output Type')
        self.Export_OutputType_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='3', sticky='w')
        self.Export_OutputType_Combobox_.append(ttk.Combobox(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.outputTypeChoices.append(tk.StringVar(value=''))
        self.outputTypeChoices[self.exportTabNum].set(outputType)
        self.Export_OutputType_Combobox_[self.exportTabNum].configure(state='readonly', textvariable=self.outputTypeChoices[self.exportTabNum], values='"All" "1G1R" "Favorites"', width='10')
        self.Export_OutputType_Combobox_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='3', sticky='w')
        self.Export_OutputType_Combobox_[self.exportTabNum].bind('<<ComboboxSelected>>', self.export_setOutputType, add='')
        if outputType == "1G1R":
            self.Export_OutputType_Combobox_[self.exportTabNum].current(1)
        elif outputType == "Favorites":
            self.Export_OutputType_Combobox_[self.exportTabNum].current(2)
        else:
            self.Export_OutputType_Combobox_[self.exportTabNum].current(0)
        self.Export_includeOtherRegions_.append(ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.includeOtherRegionsChoices.append(tk.IntVar(value=includeOtherRegions))
        self.Export_includeOtherRegions_[self.exportTabNum].configure(text='Include Games from Non-Primary Regions', variable=self.includeOtherRegionsChoices[self.exportTabNum])
        self.Export_includeOtherRegions_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='4', sticky='w')
        self.Export_FromList_Label_.append(ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.Export_FromList_Label_[self.exportTabNum].configure(text='Rom List')
        self.Export_FromList_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='5', sticky='w')
        self.Export_FromList_PathChooser_.append(PathChooserInput(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.romListFileChoices.append(tk.StringVar(value=''))
        self.romListFileChoices[self.exportTabNum].set(romList)
        self.Export_FromList_PathChooser_[self.exportTabNum].configure(mustexist='true', state='normal', textvariable=self.romListFileChoices[self.exportTabNum], type='file', filetypes=[('Text Files', '*.txt')])
        self.Export_FromList_PathChooser_[self.exportTabNum].grid(column='0', ipadx='90', padx='150', pady='10', row='5', sticky='w')
        self.Export_IncludeFrame_.append(ttk.Labelframe(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        numSkipped = 0
        for i in range(len(SpecialCategories)):
            self.Export_IncludeSpecial_.append([])
            self.includeSpecialChoices.append([])
            self.Export_IncludeSpecial_[i].append(ttk.Checkbutton(self.Export_IncludeFrame_[self.exportTabNum]))
            if len(includeSpecial) > i:
                self.includeSpecialChoices[i].append(tk.IntVar(value=includeSpecial[i]))
            else:
                self.includeSpecialChoices[i].append(tk.IntVar(value=False))
            self.Export_IncludeSpecial_[i][self.exportTabNum].configure(text=SpecialCategories[i].name, variable=self.includeSpecialChoices[i][self.exportTabNum])
            if SpecialCategories[i].exclusiveSystems is not None and systemName not in SpecialCategories[i].exclusiveSystems:
                numSkipped += 1
            else:
                currCol = (i-numSkipped)%3
                currRow = (i-numSkipped)//3
                self.Export_IncludeSpecial_[i][self.exportTabNum].grid(column=currCol, padx=10, pady=10, row=currRow, sticky='w')
        self.Export_IncludeFrame_[self.exportTabNum].configure(text='Include')
        self.Export_IncludeFrame_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='6', sticky='w')
        self.Export_ExtractArchives_.append(ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.extractArchivesChoices.append(tk.IntVar(value=extractArchives))
        self.Export_ExtractArchives_[self.exportTabNum].configure(text='Extract Compressed Roms', variable=self.extractArchivesChoices[self.exportTabNum])
        self.Export_ExtractArchives_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.03', x='0', y='0')
        self.Export_ParentFolder_.append(ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.parentFolderChoices.append(tk.IntVar(value=parentFolder))
        self.Export_ParentFolder_[self.exportTabNum].configure(text='Create Game Folder for Each Game', variable=self.parentFolderChoices[self.exportTabNum])
        self.Export_ParentFolder_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.132', x='0', y='0')
        self.Export_SortByPrimaryRegion_.append(ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.sortByPrimaryRegionChoices.append(tk.IntVar(value=sortByPrimaryRegion))
        self.Export_SortByPrimaryRegion_[self.exportTabNum].configure(text='Create Region Folders', variable=self.sortByPrimaryRegionChoices[self.exportTabNum])
        self.Export_SortByPrimaryRegion_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.234', x='0', y='0')
        self.Export_SortByPrimaryRegion_[self.exportTabNum].configure(command=self.export_togglePrimaryRegionInRoot)
        self.Export_PrimaryRegionInRoot_.append(ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.primaryRegionInRootChoices.append(tk.IntVar(value=primaryRegionInRoot))
        self.Export_PrimaryRegionInRoot_[self.exportTabNum].configure(text='Do Not Create Folder for Primary Regions', variable=self.primaryRegionInRootChoices[self.exportTabNum])
        self.Export_PrimaryRegionInRoot_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.336', x='0', y='0')
        self.Export_SpecialCategoryFolder_.append(ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.specialCategoryFolderChoices.append(tk.IntVar(value=specialCategoryFolder))
        self.Export_SpecialCategoryFolder_[self.exportTabNum].configure(text='Create Folders for Special Categories', variable=self.specialCategoryFolderChoices[self.exportTabNum])
        self.Export_SpecialCategoryFolder_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.438', x='0', y='0')
        self.Export_LetterFolder_.append(ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.letterFolderChoices.append(tk.IntVar(value=letterFolder))
        self.Export_LetterFolder_[self.exportTabNum].configure(text='Create Letter Folders', variable=self.letterFolderChoices[self.exportTabNum])
        self.Export_LetterFolder_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.540', x='0', y='0')
        self.Export_OverwriteDuplicates_.append(ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.overwriteDuplicatesChoices.append(tk.IntVar(value=overwriteDuplicates))
        self.Export_OverwriteDuplicates_[self.exportTabNum].configure(text='Overwrite Duplicate Files', variable=self.overwriteDuplicatesChoices[self.exportTabNum])
        self.Export_OverwriteDuplicates_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.642', x='0', y='0')
        self.Export_RemoveSystem_.append(ttk.Button(self.Export_ScrolledFrame_[self.exportTabNum].innerframe))
        self.Export_RemoveSystem_[self.exportTabNum].configure(text='Remove System')
        self.Export_RemoveSystem_[self.exportTabNum].place(anchor='se', relx='1', rely='1', x='-10', y='-10')
        self.Export_RemoveSystem_[self.exportTabNum].configure(command=self.export_removeSystem)
        # self.Export_ScrolledFrame_[self.exportTabNum].innerframe.configure(relief='groove')
        self.Export_ScrolledFrame_[self.exportTabNum].configure(usemousewheel=True)
        self.Export_ScrolledFrame_[self.exportTabNum].place(anchor='nw', relheight='.9', relwidth='.9', relx='.05', rely='.05', x='0', y='0')
        self.Export_Systems.add(self.Export_ScrolledFrame_[self.exportTabNum], text=systemName)
        tooltip.create(self.Export_DAT_Label_[self.exportTabNum], 'The No-Intro DAT file for the current system. This contains information about each rom, which is used in both exporting and auditing.\n\nNot needed for the \"Favorites\" output type.')
        tooltip.create(self.Export_Romset_Label_[self.exportTabNum], 'The directory containing your roms for the current system.')
        tooltip.create(self.Export_OutputDir_Label_[self.exportTabNum], 'The directory that your roms will be exported to. Ideally, this should be named after the current system.')
        tooltip.create(self.Export_OutputType_Label_[self.exportTabNum], '\"All\": All roms will be exported.\n\n\"1G1R\" (1 Game 1 Rom): Only the latest revision of the highest-priority region group of each game will be exported (e.g. USA Revision 2). See "Region Settings" in Config for more information.\n\n\"Favorites\": Only specific roms from a provided text file will be exported; good for exporting a list of only your favorite roms.')
        tooltip.create(self.Export_includeOtherRegions_[self.exportTabNum], 'If enabled: In the event that a game does not contain a rom from your region (e.g. your primary region is USA but the game is a Japan-only release), a secondary region will be used according to your Region/Language Priority Order.\n\nIf disabled: In the event that a game does not contain a rom from your region, the game is skipped entirely.\n\nIf you only want to export roms from your own region, disable this.')
        tooltip.create(self.Export_FromList_Label_[self.exportTabNum], 'The text list containing your favorite roms for the current system.')
        for i in range(len(SpecialCategories)):
            if SpecialCategories[i].description is not None:
                tooltip.create(self.Export_IncludeSpecial_[i][self.exportTabNum], SpecialCategories[i].description)
        tooltip.create(self.Export_ExtractArchives_[self.exportTabNum], 'If enabled, any roms from your input romset that are contained in zipped archives (ZIP, RAR, 7z) will be extracted during export.\n\nUseful if your output device does not support zipped roms.\n\nIf unsure, leave this disabled.')
        tooltip.create(self.Export_ParentFolder_[self.exportTabNum], 'If enabled, each rom will be exported to a parent folder with the same name as its primary region release.\n\nFor example, \"Legend of Zelda, The (USA)\" and \"Zelda no Densetsu 1 - The Hyrule Fantasy (Japan)\" will both be exported to a folder titled \"Legend of Zelda, The\".\n\nIf \"Create Region Folders\" or \"Create Letter Folders\" is enabled, the game folder will be placed according to the game\'s highest-priority region.')
        tooltip.create(self.Export_SortByPrimaryRegion_[self.exportTabNum], 'If enabled, each rom will be exported to a parent folder named after its highest-priority region.\n\nFor example, if your order of region priority is USA->Europe->Japan, then \"Golden Sun (USA, Europe)\" will be exported to a folder titled \"'+specialFolderPrefix+'USA'+specialFolderSuffix+'\".')
        tooltip.create(self.Export_SpecialCategoryFolder_[self.exportTabNum], 'If enabled, all exported roms that are part of a special category (Unlicensed, Unreleased, etc.) will be exported to a parent folder named after that category. There will be multiple nested folders if a game belongs to multiple special categories.\n\nIf unsure, leave this enabled.')
        tooltip.create(self.Export_LetterFolder_[self.exportTabNum], 'If enabled, each rom will be exported to a parent folder named after its first letter.\n\nFor example, \"Castlevania (USA)\" will be exported to a [C] folder.\n\nIf unsure, leave this disabled.')
        tooltip.create(self.Export_PrimaryRegionInRoot_[self.exportTabNum], '(Only applies if \"Create Region Folders\" is enabled.)\n\nIf enabled, a region folder will NOT be created for your primary regions.\n\nFor example, if you have Europe set as a primary region, then Europe roms will not be exported to a [Europe] folder, and will instead be placed directly in the output folder.\n\nIf unsure, leave this enabled.')
        tooltip.create(self.Export_OverwriteDuplicates_[self.exportTabNum], 'If enabled: If a rom in the output directory with the same name as an exported rom already exists, it will be overwritten by the new export.\n\nIf disabled: The export will not overwrite matching roms in the output directory.\n\nIf unsure, leave this disabled.')


        self.Export_Systems.select(self.exportTabNum)
        self.export_setOutputType()
        self.export_togglePrimaryRegionInRoot()
        self.exportTabNum += 1

    def setSystemDAT(self, systemName, datFilePath):
        self.datFilePathChoices.append(tk.StringVar(value=''))
        if datFilePath != "":
            self.datFilePathChoices[self.exportTabNum].set(datFilePath)
            return
        if self.ssdHelper(systemName):
            return
        alternateSystemNames = systemNamesDict.get(systemName)[1]
        if alternateSystemNames is not None:
            for name in alternateSystemNames:
                if self.ssdHelper(name):
                    return

    def ssdHelper(self, name):
        datDir = self.g_datFilePath.get()
        currSystemDAT = path.join(datDir, name+".dat").replace("\\", "/")
        if path.isfile(currSystemDAT):
            self.datFilePathChoices[self.exportTabNum].set(currSystemDAT)
            return True
        if path.isdir(datDir):
            expectedName = currSystemDAT.lower()
            parenthesesKeeper = r'\1' if "(" in name else ''
            for df in listdir(datDir):
                currSystemDAT = path.join(datDir, df).replace("\\", "/")
                if re.sub(r'(\s*\([^)]*\)).*', parenthesesKeeper, currSystemDAT).lower()+".dat" == expectedName:
                    self.datFilePathChoices[self.exportTabNum].set(currSystemDAT)
                    return True
        return False

    def setInputRomsetDir(self, systemName, romsetFolderPath):
        self.romsetFolderPathChoices.append(tk.StringVar(value=''))
        if romsetFolderPath != "":
            self.romsetFolderPathChoices[self.exportTabNum].set(romsetFolderPath)
            return
        if self.sirdHelper(systemName):
            return
        alternateSystemNames = systemNamesDict.get(systemName)[1]
        if alternateSystemNames is not None:
            for name in alternateSystemNames:
                if self.sirdHelper(name):
                    return

    def sirdHelper(self, name):
        currSystemInputDir = path.join(self.g_romsetFolderPath.get(), name).replace("\\", "/")
        if path.isdir(currSystemInputDir):
            self.romsetFolderPathChoices[self.exportTabNum].set(currSystemInputDir)
            return True
        if " - " in name:
            currSystemInputDir = path.join(self.g_romsetFolderPath.get(), name.replace(" - ", " ")).replace("\\", "/")
            if path.isdir(currSystemInputDir):
                self.romsetFolderPathChoices[self.exportTabNum].set(currSystemInputDir)
                return True
        return False

    def export_saveSystemLoadout(self):
        if self.exportTabNum > 0:
            loadoutFile = asksaveasfilename(defaultextension='.txt', filetypes=[("Text Files", '*.txt')],
                initialdir=path.join(progFolder, "System Loadouts"),
                title="Save System Tabs")
            if loadoutFile == "":
                return
            loadout = configparser.ConfigParser(allow_no_value=True)
            loadout.optionxform = str
            for i in range(len(self.exportSystemNames)):
                loadout[self.exportSystemNames[i]] = {}
                loadout[self.exportSystemNames[i]]["Input No-Intro DAT"] = self.datFilePathChoices[i].get()
                loadout[self.exportSystemNames[i]]["Input Romset"] = self.romsetFolderPathChoices[i].get()
                loadout[self.exportSystemNames[i]]["Output Directory"] = self.outputFolderDirectoryChoices[i].get()
                loadout[self.exportSystemNames[i]]["Output Type"] = self.outputTypeChoices[i].get()
                loadout[self.exportSystemNames[i]]["Include Games from Non-Primary Regions"] = str(self.includeOtherRegionsChoices[i].get())
                loadout[self.exportSystemNames[i]]["Rom List"] = self.romListFileChoices[i].get()
                for j in range(len(SpecialCategories)):
                    if (SpecialCategories[j].exclusiveSystems is None) or (self.exportSystemNames[i] in SpecialCategories[j].exclusiveSystems):
                        loadout[self.exportSystemNames[i]]["Include "+SpecialCategories[j].name] = str(self.includeSpecialChoices[j][i].get())
                loadout[self.exportSystemNames[i]]["Extract Compressed Roms"] = str(self.extractArchivesChoices[i].get())
                loadout[self.exportSystemNames[i]]["Create Game Folder for Each Game"] = str(self.parentFolderChoices[i].get())
                loadout[self.exportSystemNames[i]]["Create Region Folders"] = str(self.sortByPrimaryRegionChoices[i].get())
                loadout[self.exportSystemNames[i]]["Do Not Create Folder for Primary Region"] = str(self.primaryRegionInRootChoices[i].get())
                loadout[self.exportSystemNames[i]]["Create Folders for Special Categories"] = str(self.specialCategoryFolderChoices[i].get())
                loadout[self.exportSystemNames[i]]["Create Letter Folders"] = str(self.letterFolderChoices[i].get())
                loadout[self.exportSystemNames[i]]["Overwrite Duplicate Files"] = str(self.overwriteDuplicatesChoices[i].get())
            with open(loadoutFile, 'w') as lf:
                loadout.write(lf)

    def keyValIsTrue(self, k, v):
        return k.get(v) == "True"

    def export_loadSystemLoadout(self):
        if self.exportTabNum > 0:
            if not askyesno("EzRO", "This will replace your current system loadout. Continue?"):
                return
        loadoutFile = askopenfilename(filetypes=[("System Loadouts", "*.txt")])
        if loadoutFile == "":
            return
        if self.exportTabNum > 0:
            while self.exportTabNum > 0:
                self.export_removeSystem()
        loadout = configparser.ConfigParser(allow_no_value=True)
        loadout.optionxform = str
        loadout.read(loadoutFile)
        for key in loadout.keys():
            if key in systemNamesDict.keys():
                curr_includeSpecial = [loadout[key].get("Include "+cat.name) == "1" for cat in SpecialCategories]
                self.addSystemTab(systemName=key, datFilePath=loadout[key]["Input No-Intro DAT"], romsetFolderPath=loadout[key]["Input Romset"], outputFolderDirectory=loadout[key]["Output Directory"],
                    outputType=loadout[key]["Output Type"], includeOtherRegions=loadout[key]["Include Games from Non-Primary Regions"], romList=loadout[key]["Rom List"],
                    includeSpecial=curr_includeSpecial, extractArchives=loadout[key]["Extract Compressed Roms"], parentFolder=loadout[key]["Create Game Folder for Each Game"],
                    sortByPrimaryRegion=loadout[key]["Create Region Folders"], primaryRegionInRoot=loadout[key]["Do Not Create Folder for Primary Region"],
                    specialCategoryFolder=loadout[key]["Create Folders for Special Categories"], letterFolder=loadout[key]["Create Letter Folders"], overwriteDuplicates=loadout[key]["Overwrite Duplicate Files"])

    def export_addSystem(self):
        currSystemChoice = self.systemChoice.get()
        if (currSystemChoice.replace("-","").replace("=","") != ""):
            for es in self.Export_Systems.tabs():
                if self.Export_Systems.tab(es, "text") == currSystemChoice:
                    return
            self.addSystemTab(systemName=currSystemChoice, datFilePath="", romsetFolderPath="", outputFolderDirectory="",
                outputType="All", includeOtherRegions=self.g_includeOtherRegions.get(), romList="",
                includeSpecial=[self.g_includeSpecial[i].get() for i in range(len(self.g_includeSpecial))], extractArchives=False, parentFolder=self.g_parentFolder.get(),
                sortByPrimaryRegion=self.g_sortByPrimaryRegion.get(), primaryRegionInRoot=self.g_primaryRegionInRoot.get(),
                specialCategoryFolder=self.g_specialCategoryFolder.get(), letterFolder=self.g_letterFolder.get(), overwriteDuplicates=self.g_overwriteDuplicates.get())

    def export_setOutputType(self, event=None):
        currIndex = self.Export_Systems.index("current")
        currOutputType = self.outputTypeChoices[currIndex].get()
        if currOutputType == "1G1R":
            self.Export_includeOtherRegions_[currIndex].grid(column='0', padx='20', pady='10', row='4', sticky='w')
        else:
            self.Export_includeOtherRegions_[currIndex].grid_remove()
        if currOutputType == "Favorites":
            self.Export_FromList_Label_[currIndex].grid(column='0', padx='20', pady='10', row='5', sticky='w')
            self.Export_FromList_PathChooser_[currIndex].grid(column='0', padx='150', pady='10', row='5', sticky='w')
        else:
            self.Export_FromList_Label_[currIndex].grid_remove()
            self.Export_FromList_PathChooser_[currIndex].grid_remove()

    def export_togglePrimaryRegionInRoot(self):
        currSystemIndex = self.Export_Systems.index("current")
        if self.sortByPrimaryRegionChoices[currSystemIndex].get():
            self.Export_PrimaryRegionInRoot_[currSystemIndex].configure(state='enabled')
        else:
            self.Export_PrimaryRegionInRoot_[currSystemIndex].configure(state='disabled')

    def export_removeSystem(self):
        currSystemIndex = self.Export_Systems.index("current")

        self.Export_Systems.forget(self.Export_Systems.tabs()[currSystemIndex])

        self.exportSystemNames.pop(currSystemIndex)
        self.Export_ScrolledFrame_.pop(currSystemIndex)
        self.Export_DAT_Label_.pop(currSystemIndex)
        self.Export_DAT_PathChooser_.pop(currSystemIndex)
        self.datFilePathChoices.pop(currSystemIndex)
        self.Export_Romset_Label_.pop(currSystemIndex)
        self.Export_Romset_PathChooser_.pop(currSystemIndex)
        self.romsetFolderPathChoices.pop(currSystemIndex)
        self.Export_OutputDir_Label_.pop(currSystemIndex)
        self.Export_OutputDir_PathChooser_.pop(currSystemIndex)
        self.outputFolderDirectoryChoices.pop(currSystemIndex)
        self.Export_Separator_.pop(currSystemIndex)
        self.Export_OutputType_Label_.pop(currSystemIndex)
        self.Export_OutputType_Combobox_.pop(currSystemIndex)
        self.outputTypeChoices.pop(currSystemIndex)
        self.Export_includeOtherRegions_.pop(currSystemIndex)
        self.includeOtherRegionsChoices.pop(currSystemIndex)
        self.Export_FromList_Label_.pop(currSystemIndex)
        self.Export_FromList_PathChooser_.pop(currSystemIndex)
        self.romListFileChoices.pop(currSystemIndex)
        self.Export_IncludeFrame_.pop(currSystemIndex)
        for i in range(len(SpecialCategories)):
            self.Export_IncludeSpecial_[i].pop(currSystemIndex)
            self.includeSpecialChoices[i].pop(currSystemIndex)
        self.Export_ExtractArchives_.pop(currSystemIndex)
        self.extractArchivesChoices.pop(currSystemIndex)
        self.Export_ParentFolder_.pop(currSystemIndex)
        self.parentFolderChoices.pop(currSystemIndex)
        self.Export_SortByPrimaryRegion_.pop(currSystemIndex)
        self.sortByPrimaryRegionChoices.pop(currSystemIndex)
        self.Export_PrimaryRegionInRoot_.pop(currSystemIndex)
        self.primaryRegionInRootChoices.pop(currSystemIndex)
        self.Export_SpecialCategoryFolder_.pop(currSystemIndex)
        self.Export_LetterFolder_.pop(currSystemIndex)
        self.specialCategoryFolderChoices.pop(currSystemIndex)
        self.letterFolderChoices.pop(currSystemIndex)
        self.Export_OverwriteDuplicates_.pop(currSystemIndex)
        self.overwriteDuplicatesChoices.pop(currSystemIndex)
        self.Export_RemoveSystem_.pop(currSystemIndex)

        self.exportTabNum -= 1
        if currSystemIndex < self.exportTabNum:
            self.Export_Systems.select(currSystemIndex)
        elif currSystemIndex > 0:
            self.Export_Systems.select(currSystemIndex - 1)

    def export_auditSystem(self):
        if self.exportTabNum > 0:
            currSystemIndex = [self.Export_Systems.index("current")]
            if self.auditCheck(currSystemIndex):
                self.openAuditWindow(numSystems=1, systemIndexList=currSystemIndex)

    def export_auditAllSystems(self):
        if self.exportTabNum > 0:
            allSystemIndices = list(range(self.exportTabNum))
            if self.auditCheck(allSystemIndices):
                self.openAuditWindow(numSystems=len(allSystemIndices), systemIndexList=allSystemIndices)

    def auditCheck(self, systemIndices):
        failureMessage = ""
        for ind in systemIndices:
            currSystemName = self.exportSystemNames[ind]
            currSystemDAT = self.datFilePathChoices[ind].get()
            currSystemFolder = self.romsetFolderPathChoices[ind].get()
            if currSystemDAT == "":
                failureMessage += currSystemName+":\nMissing DAT file.\n\n"
            elif not path.isfile(currSystemDAT):
                failureMessage += currSystemName+":\nInvalid DAT file (file not found).\n\n"
            else:
                tree = ET.parse(currSystemDAT)
                treeRoot = tree.getroot()
                systemNameFromDAT = treeRoot.find("header").find("name").text
                if systemNameFromDAT is None or systemNameFromDAT == "":
                    failureMessage += currSystemName+":\nInvalid DAT file (Parent-Clone DAT is required).\n\n"
                if systemNameFromDAT != currSystemName+" (Parent-Clone)":
                    if systemNameFromDAT.startswith(currSystemName) and "(Parent-Clone)" in systemNameFromDAT: # the found DAT is *probably* correct (e.g N64 has "(BigEndian)" in the name, so this is needed)
                        pass
                    else:
                        failureMessage += currSystemName+":\nDAT header mismatched; this is likely the incorrect DAT file.\nExpected: \""+currSystemName+" (Parent-Clone)\" (or something similar)\nGot: \""+systemNameFromDAT+"\".\n\n"
            if currSystemFolder == "":
                failureMessage += currSystemName+":\nMissing input romset.\n\n"
            elif not path.isdir(currSystemFolder):
                failureMessage += currSystemName+":\nInvalid input romset (directory not found).\n\n"
        if failureMessage == "":
            return True
        showerror("Invalid Parameters", "Please fix the following issues before attempting an audit:\n\n"+failureMessage.strip())
        return False

    def openAuditWindow(self, numSystems, systemIndexList):
        self.systemIndexList = systemIndexList
        self.auditInProgress = False
        self.Audit_Window = Toplevel()
        self.Audit_Window.title("EzRO Audit")
        self.Audit_Frame = ttk.Frame(self.Audit_Window)
        self.Audit_MainProgress_Label = ttk.Label(self.Audit_Frame)
        if numSystems == 1:
            self.Audit_MainProgress_Label.configure(text='Preparing to audit system: '+self.exportSystemNames[systemIndexList[0]])
        else:
            self.Audit_MainProgress_Label.configure(text='Preparing to audit '+str(numSystems)+' systems')
        self.Audit_MainProgress_Label.place(anchor='center', relx='.5', rely='.05', x='0', y='0')
        self.Audit_MainProgress_Bar = ttk.Progressbar(self.Audit_Frame)
        self.Audit_MainProgress_Bar.configure(maximum=numSystems, orient='horizontal')
        self.Audit_MainProgress_Bar.place(anchor='center', relwidth='.9', relx='.5', rely='.11', x='0', y='0')
        self.Audit_SubProgress_Bar = ttk.Progressbar(self.Audit_Frame)
        self.Audit_SubProgress_Bar.configure(maximum='100', orient='horizontal')
        self.Audit_SubProgress_Bar.place(anchor='center', relwidth='.9', relx='.5', rely='.17', x='0', y='0')
        self.SubProgress_TextField = tk.Text(self.Audit_Frame)
        self.SubProgress_TextField.configure(autoseparators='true', blockcursor='false', height='10', insertontime='0')
        self.SubProgress_TextField.configure(insertwidth='0', state='disabled', tabstyle='tabular', takefocus=False)
        self.SubProgress_TextField.configure(width='50', wrap='word')
        self.SubProgress_TextField.place(anchor='n', relheight='.62', relwidth='.9', relx='.5', rely='.23', x='0', y='0')
        self.Audit_StartButton = ttk.Button(self.Audit_Frame)
        self.audit_startButtonText = tk.StringVar(value='Start Audit')
        self.Audit_StartButton.configure(text='Start Audit', textvariable=self.audit_startButtonText)
        self.Audit_StartButton.place(anchor='center', relx='.4', rely='.925', x='0', y='0')
        self.Audit_StartButton.configure(command=self.audit_startAudit)
        self.Audit_CancelButton = ttk.Button(self.Audit_Frame)
        self.audit_cancelButtonText = tk.StringVar(value='Cancel')
        self.Audit_CancelButton.configure(text='Cancel', textvariable=self.audit_cancelButtonText)
        self.Audit_CancelButton.place(anchor='center', relx='.6', rely='.925', x='0', y='0')
        self.Audit_CancelButton.configure(command=self.audit_cancelAudit)
        self.Audit_Frame.configure(height='200', width='200')
        self.Audit_Frame.place(anchor='nw', relheight='1', relwidth='1', relx='0', rely='0', x='0', y='0')
        self.Audit_Window.configure(height=int(600*screenHeightMult), width=int(800*screenHeightMult))
        self.Audit_Window.grab_set()
        self.Audit_Window.protocol("WM_DELETE_WINDOW", self.audit_cancelAudit)

    def audit_startAudit(self):
        self.Audit_StartButton.configure(state='disabled')
        self.updateAndAuditVerifiedRomsets(self.systemIndexList)

    def audit_cancelAudit(self):
        if self.auditInProgress:
            if askyesno("EzRO Audit", "Cancel the audit?"):
                # self.auditInProgress = False
                # self.Audit_Window.destroy()
                self.cancelledAudit = True
        else:
            self.Audit_Window.destroy()
            # self.cancelledAudit = True

    def export_exportSystem(self):
        if self.exportTabNum > 0:
            currSystemIndex = [self.Export_Systems.index("current")]
            if self.exportCheck(currSystemIndex):
                self.openExportWindow(numSystems=1, systemIndexList=currSystemIndex)

    def export_exportAllSystems(self):
        if self.exportTabNum > 0:
            allSystemIndices = list(range(self.exportTabNum))
            if self.exportCheck(allSystemIndices):
                self.openExportWindow(numSystems=len(allSystemIndices), systemIndexList=allSystemIndices)

    def exportCheck(self, systemIndices):
        failureMessage = ""
        warningMessage = ""
        for ind in systemIndices:
            currSystemName = self.exportSystemNames[ind]

            currSystemDAT = self.datFilePathChoices[ind].get()
            if currSystemDAT == "":
                failureMessage += currSystemName+":\nMissing DAT file.\n"
            elif not path.isfile(currSystemDAT):
                failureMessage += currSystemName+":\nInvalid DAT file (file not found).\n"
            else:
                try:
                    tree = ET.parse(currSystemDAT)
                    treeRoot = tree.getroot()
                    systemNameFromDAT = treeRoot.find("header").find("name").text
                    if systemNameFromDAT is None or systemNameFromDAT == "":
                        failureMessage += currSystemName+":\nInvalid DAT file (Parent-Clone DAT is required).\n\n"
                    if systemNameFromDAT != currSystemName+" (Parent-Clone)":
                        if systemNameFromDAT.startswith(currSystemName) and "(Parent-Clone)" in systemNameFromDAT: # the found DAT is *probably* correct (e.g N64 has "(BigEndian)" in the name, so this is needed)
                            pass
                        else:
                            failureMessage += currSystemName+":\nDAT header mismatched; this is likely the incorrect DAT file.\nExpected: \""+currSystemName+" (Parent-Clone)\" (or something similar)\nGot: \""+systemNameFromDAT+"\".\n\n"
                except:
                    failureMessage += currSystemName+":\nInvalid DAT file (Parent-Clone DAT is required).\n\n"

            currSystemFolder = self.romsetFolderPathChoices[ind].get()
            if currSystemFolder == "":
                failureMessage += currSystemName+":\nMissing input romset.\n\n"
            elif not path.isdir(currSystemFolder):
                failureMessage += currSystemName+":\nInvalid input romset (directory not found).\n\n"

            currOutputFolder = self.outputFolderDirectoryChoices[ind].get()
            if currOutputFolder == "":
                failureMessage += currSystemName+":\nMissing output directory.\n\n"
            elif not path.isdir(currOutputFolder):
                failureMessage += currSystemName+":\nInvalid output directory (directory not found).\n\n"

            if (not (currSystemFolder == "" or currOutputFolder == "")) and (currSystemFolder == currOutputFolder):
                failureMessage += currSystemName+":\nInput and output directories are the same.\n\n"

            currOutputType = self.outputTypeChoices[ind].get()
            if currOutputType == "Favorites":
                currFavoritesList = self.romListFileChoices[ind].get()
                if currFavoritesList == "":
                    failureMessage += currSystemName+":\nMissing Favorites rom list.\n\n"
                elif not path.isfile(currFavoritesList):
                    failureMessage += currSystemName+":\nInvalid Favorites rom list (file not found).\n\n"

        for i in range(len(self.outputFolderDirectoryChoices)):
            currOutputDir = self.outputFolderDirectoryChoices[i]
            for j in range(i+1, len(self.outputFolderDirectoryChoices)):
                otherOutputDir = self.outputFolderDirectoryChoices[j]
                if currOutputDir == otherOutputDir:
                    warningMessage += self.exportSystemNames[i]+" and "+self.exportSystemNames[j]+":\nThese two systems have the same output directory.\n\nYou may want to create a different directory for each system so their games don't get mixed up.\n\n"
                    break
            if warningMessage != "":
                break

        if warningMessage != "":
            showinfo("Warning", warningMessage.strip())

        if failureMessage == "":
            return True
        showerror("Invalid Parameters", "Please fix the following issues before attempting an export:\n\n"+failureMessage.strip())
        return False

    def openExportWindow(self, numSystems, systemIndexList):
        self.systemIndexList = systemIndexList
        self.exportInProgress = False
        self.Export_Window = Toplevel()
        if self.isExport:
            self.Export_Window.title("EzRO Export")
        else:
            self.Export_Window.title("EzRO Test Export")
        self.Export_Frame = ttk.Frame(self.Export_Window)
        self.Export_MainProgress_Label = ttk.Label(self.Export_Frame)
        if numSystems == 1:
            if self.isExport:
                self.Export_MainProgress_Label.configure(text='Preparing to export system: '+self.exportSystemNames[systemIndexList[0]])
            else:
                self.Export_MainProgress_Label.configure(text='Preparing to test export of system: '+self.exportSystemNames[systemIndexList[0]])
        else:
            if self.isExport:
                self.Export_MainProgress_Label.configure(text='Preparing to export '+str(numSystems)+' systems')
            else:
                self.Export_MainProgress_Label.configure(text='Preparing to test export of '+str(numSystems)+' systems')
        self.Export_MainProgress_Label.place(anchor='center', relx='.5', rely='.05', x='0', y='0')
        self.Export_MainProgress_Bar = ttk.Progressbar(self.Export_Frame)
        self.Export_MainProgress_Bar.configure(maximum=numSystems, orient='horizontal')
        self.Export_MainProgress_Bar.place(anchor='center', relwidth='.9', relx='.5', rely='.11', x='0', y='0')
        self.Export_SubProgress_Bar = ttk.Progressbar(self.Export_Frame)
        self.Export_SubProgress_Bar.configure(maximum='100', orient='horizontal')
        self.Export_SubProgress_Bar.place(anchor='center', relwidth='.9', relx='.5', rely='.17', x='0', y='0')
        self.SubProgress_TextField = tk.Text(self.Export_Frame)
        self.SubProgress_TextField.configure(autoseparators='true', blockcursor='false', height='10', insertontime='0')
        self.SubProgress_TextField.configure(insertwidth='0', state='disabled', tabstyle='tabular', takefocus=False)
        self.SubProgress_TextField.configure(width='50', wrap='word')
        self.SubProgress_TextField.place(anchor='n', relheight='.62', relwidth='.9', relx='.5', rely='.23', x='0', y='0')
        self.Export_StartButton = ttk.Button(self.Export_Frame)
        self.export_startButtonText = tk.StringVar(value='Start Export')
        self.Export_StartButton.configure(text='Start Export', textvariable=self.export_startButtonText)
        self.Export_StartButton.place(anchor='center', relx='.4', rely='.925', x='0', y='0')
        self.Export_StartButton.configure(command=self.export_startExport)
        self.Export_CancelButton = ttk.Button(self.Export_Frame)
        self.export_cancelButtonText = tk.StringVar(value='Cancel')
        self.Export_CancelButton.configure(text='Cancel', textvariable=self.export_cancelButtonText)
        self.Export_CancelButton.place(anchor='center', relx='.6', rely='.925', x='0', y='0')
        self.Export_CancelButton.configure(command=self.export_cancelExport)
        self.Export_Frame.configure(height='200', width='200')
        self.Export_Frame.place(anchor='nw', relheight='1', relwidth='1', relx='0', rely='0', x='0', y='0')
        self.Export_Window.configure(height=int(600*screenHeightMult), width=int(800*screenHeightMult))
        self.Export_Window.grab_set()
        self.Export_Window.protocol("WM_DELETE_WINDOW", self.export_cancelExport)

    def export_startExport(self):
        self.Export_StartButton.configure(state='disabled')
        self.mainExport(self.systemIndexList)

    def export_cancelExport(self):
        # Cancelling an export early causes an error in tkinter (writing to a progressbar/text field/etc. that no longer exists) but it doesn't actually affect anything
        if self.exportInProgress:
            if askyesno("EzRO Export", "Cancel the export?"):
                # self.exportInProgress = False
                # self.Export_Window.destroy()
                self.cancelledExport = True
        else:
            self.Export_Window.destroy()
            # self.cancelledExport = True

    def export_toggleTestExport(self):
        self.isExport = not self.isTestExport.get()

    def export_auditHelp(self):
        showinfo("Audit Help",
            "\"Auditing\" a system directory updates the file names of misnamed roms (and the ZIP files containing them, if applicable) to match the rom's entry in the system's No-Intro DAT. This is determined by the rom's matching checksum in the DAT, so the original name doesn't matter."
            +"\n\nThis also creates a log file indicating which roms exist in the romset, which roms are missing, and which roms are in the set that don't match anything from the DAT."
            +"\n\nIt is highly recommended that you audit a system directory whenever you update that system's No-Intro DAT.")

    def writeTextToSubProgress(self, text):
        self.SubProgress_TextField.configure(state='normal')
        self.SubProgress_TextField.insert(tk.END, text)
        self.SubProgress_TextField.configure(state='disabled')

    #################
    # AUDIT (Logic) #
    #################

    def updateAndAuditVerifiedRomsets(self, systemIndices):
        global allGameNamesInDAT, romsWithoutCRCMatch, progressBar

        self.auditInProgress = True
        self.cancelledAudit = False
        self.Audit_MainProgress_Label.configure(text='Auditing...')
        self.Audit_MainProgress_Bar['value'] = 0
        isFirstSystem = True
        for currIndex in systemIndices:
            self.Audit_SubProgress_Bar['value'] = 0
            currSystemName = self.exportSystemNames[currIndex]
            currSystemFolder = self.romsetFolderPathChoices[currIndex].get()
            if not path.isdir(currSystemFolder):
                continue
            if isFirstSystem:
                isFirstSystem = False
            else:
                self.writeTextToSubProgress("========================================\n\n")
            self.Audit_MainProgress_Label.configure(text="Auditing system: "+currSystemName)
            self.writeTextToSubProgress("Auditing system: "+currSystemName+"\n\n")
            isNoIntro = True
            currSystemDAT = self.datFilePathChoices[currIndex].get()
            tree = ET.parse(currSystemDAT)
            treeRoot = tree.getroot()
            allGameFields = treeRoot[1:]
            crcToGameName = {}
            allGameNames = []
            for game in allGameFields:
                gameName = game.get("name")
                allGameNames.append(gameName)
                try:
                    gameCRC = game.find("rom").get("crc").upper()
                except:
                    gameCRC = None
                if gameCRC not in crcToGameName.keys():
                    crcToGameName[gameCRC] = []
                crcToGameName[gameCRC].append(gameName)
            if currSystemName == "Nintendo - Nintendo Entertainment System":
                headerLength = 16
            else:
                headerLength = 0
            allGameNamesInDAT = {}
            for gameName in allGameNames:
                allGameNamesInDAT[gameName] = False
            romsWithoutCRCMatch = []
            numFiles = 0
            for root, dirs, files in walk(currSystemFolder):
                for file in files:
                    if path.basename(root) != specialFolderPrefix+"Unverified"+specialFolderSuffix:
                        numFiles += 1
            self.Audit_SubProgress_Bar.configure(maximum=str(numFiles))
            for root, dirs, files in walk(currSystemFolder):
                for file in files:
                    if path.basename(root) != specialFolderPrefix+"Unverified"+specialFolderSuffix:
                        foundMatch = self.renamingProcess(root, file, isNoIntro, headerLength, crcToGameName, allGameNames)
                        self.Audit_SubProgress_Bar['value'] += 1
                        tk_root.update() # a full update() (as opposed to update_idletasks()) allows us to check if the Cancel button was clicked, allowing a safe early exit
                    if self.cancelledAudit:
                        break
                if self.cancelledAudit:
                    break
            xmlRomsInSet = [key for key in allGameNamesInDAT.keys() if allGameNamesInDAT[key] == True]
            xmlRomsNotInSet = [key for key in allGameNamesInDAT.keys() if allGameNamesInDAT[key] == False]
            self.createSystemAuditLog(xmlRomsInSet, xmlRomsNotInSet, romsWithoutCRCMatch, currSystemName)
            numNoCRC = len(romsWithoutCRCMatch)
            if numNoCRC > 0:
                self.writeTextToSubProgress("NOTICE: "+str(numNoCRC)+pluralize(" file", numNoCRC)+" in this system folder "+pluralize("do", numNoCRC, "es", "")+" not have a matching entry in the provided DAT file.\n")
                self.writeTextToSubProgress(pluralize("", numNoCRC, "This file", "These files")+" may be ignored when exporting this system's romset.\n\n")
                # if moveUnverified == 1:
                #     numMoved = 0
                #     unverifiedFolder = path.join(currSystemFolder, "[Unverified]")
                #     createDir(unverifiedFolder)
                #     for fileName in romsWithoutCRCMatch:
                #         try:
                #             rename(path.join(currSystemFolder, fileName), path.join(unverifiedFolder, fileName))
                #             numMoved += 1
                #         except:
                #             pass
                #     print("Moved "+str(numMoved)+" of these file(s) to \"[Unverified]\" subfolder in system directory.")
            self.Audit_MainProgress_Bar['value'] += 1
            tk_root.update_idletasks()

        self.recentlyVerified = True
        self.writeTextToSubProgress("Done.")
        self.Audit_MainProgress_Label.configure(text="Audit complete.")
        self.audit_cancelButtonText.set("Finish")
        self.auditInProgress = False

    def getCRC_ZIP_RAR(self, zippedFile, headerLength=0):
        if len(zippedFile.namelist()) > 1:
            return False
        if headerLength == 0:
            fileInfo = zippedFile.infolist()[0]
            return format(fileInfo.CRC, '08x')
        else:
            fileBytes = zippedFile.read(zippedFile.namelist()[0])
            return str(hex(binascii.crc32(fileBytes[headerLength:])))[2:]

    def getCRC_7Z(self, zippedFile, headerLength=0):
        if len(zippedFile.getnames()) > 1:
            return False
        if headerLength == 0:
            fileInfo = zippedFile.list()[0]
            return format(fileInfo.crc32, '08x')
        else:
            zippedFilesDict = zippedFile.read(zippedFile.getnames()[0])
            fileBytes = list(zippedFilesDict.values())[0].read()
            return str(hex(binascii.crc32(fileBytes[headerLength:])))[2:]

    def getCRC_File(self, filePath, headerLength=0):
        if headerLength == 0:
            return crcHasher.hash_file(filePath)
        with open(filePath, "rb") as unheaderedFile:
            fileBytes = unheaderedFile.read()
            return str(hex(binascii.crc32(fileBytes[headerLength:])))[2:]

    def getCRC(self, filePath, headerLength=0):
        fileExt = path.splitext(filePath)[1]
        if fileExt == ".zip":
            with zipfile.ZipFile(filePath, 'r', zipfile.ZIP_DEFLATED) as zippedFile:
                fileCRC = self.getCRC_ZIP_RAR(zippedFile, headerLength)
        elif fileExt == ".rar":
            with rarfile.RarFile(filePath, 'r') as zippedFile:
                fileCRC = self.getCRC_ZIP_RAR(zippedFile, headerLength)
        elif fileExt == ".7z":
            with py7zr.SevenZipFile(filePath, 'r') as zippedFile:
                fileCRC = self.getCRC_7Z(zippedFile, headerLength)
        else:
            fileCRC = self.getCRC_File(filePath, headerLength)
        if fileCRC is False:
            return False
        return fileCRC.zfill(8).upper()

    def renamingProcess(self, root, file, isNoIntro, headerLength, crcToGameName, allGameNames):
        global allGameNamesInDAT, romsWithoutCRCMatch
        currFilePath = path.join(root, file)
        currFileName, currFileExt = path.splitext(file)
        if not path.isfile(currFilePath): # this is necessary
            romsWithoutCRCMatch.append(file)
            return
        foundMatch = False
        if isNoIntro:
            currFileCRC = self.getCRC(currFilePath, headerLength)
            if not currFileCRC:
                self.writeTextToSubProgress(file+" archive contains more than one file. Skipping.\n\n")
                romsWithoutCRCMatch.append(file)
                return
            matchingGameNames = crcToGameName.get(currFileCRC)
            if matchingGameNames is not None:
                if not currFileName in matchingGameNames:
                    currFileIsDuplicate = True
                    for name in matchingGameNames:
                        currPossibleMatchingGame = path.join(root, name+currFileExt)
                        if not path.exists(currPossibleMatchingGame):
                            self.renameGame(currFilePath, name, currFileExt)
                            allGameNamesInDAT[name] = True
                            currFileIsDuplicate = False
                            break
                        elif self.getCRC(currPossibleMatchingGame, headerLength) != currFileCRC: # If the romset started with a rom that has a name in the database, but with the wrong hash (e.g. it's called "Doom 64 (USA)", but it's actually something else)
                            self.renameGame(currPossibleMatchingGame, name+" (no match)", currFileExt)
                            self.renameGame(currFilePath, name, currFileExt)
                            self.renamingProcess(root, name+" (no match)", isNoIntro, headerLength, crcToGameName, allGameNames)
                            allGameNamesInDAT[name] = True
                            currFileIsDuplicate = False
                            break
                    if currFileIsDuplicate:
                        dnStart = matchingGameNames[0]+" (copy) ("
                        i = 1
                        while True:
                            duplicateName = dnStart+str(i)+")"
                            duplicatePath = path.join(root, duplicateName+currFileExt)
                            if not path.exists(duplicatePath):
                                break
                            i += 1
                        self.renameGame(currFilePath, duplicateName, currFileExt)
                        self.writeTextToSubProgress("Duplicate found and renamed: "+duplicateName+"\n\n")
                else:
                    allGameNamesInDAT[currFileName] = True
                foundMatch = True
        else:
            if currFileName in allGameNames:
                allGameNamesInDAT[currFileName] = True
                foundMatch = True
        if not foundMatch:
            romsWithoutCRCMatch.append(file)

    def renameGame(self, filePath, newName, fileExt):
        if fileExt in archiveTypes:
            self.renameArchiveAndContent(filePath, fileExt, newName)
        else:
            rename(filePath, path.join(path.dirname(filePath), newName+fileExt))
            self.writeTextToSubProgress("Renamed "+path.splitext(path.basename(filePath))[0]+" to "+newName+"\n\n")

    def createSystemAuditLog(self, xmlRomsInSet, xmlRomsNotInSet, romsWithoutCRCMatch, currSystemName):
        currTime = datetime.now().isoformat(timespec='seconds').replace(":", ".")
        xmlRomsInSet.sort()
        xmlRomsNotInSet.sort()
        romsWithoutCRCMatch.sort()

        numOverlap = len(xmlRomsInSet)
        numNotInSet = len(xmlRomsNotInSet)
        numNoCRC = len(romsWithoutCRCMatch)
        createDir(logFolder)
        auditLogFile = open(path.join(logFolder, currTime+" Audit ("+currSystemName+") ["+str(numOverlap)+" out of "+str(numOverlap+numNotInSet)+"] ["+str(numNoCRC)+" unverified].txt"), "w", encoding="utf-8", errors="replace")
        auditLogFile.writelines("=== "+currSystemName+" ===\n")
        auditLogFile.writelines("=== This romset contains "+str(numOverlap)+" of "+str(numOverlap+numNotInSet)+" known ROMs ===\n\n")
        if numOverlap > 0:
            auditLogFile.writelines("= CONTAINS =\n")
            for rom in xmlRomsInSet:
                auditLogFile.writelines(rom+"\n")
        if numNotInSet > 0:
            auditLogFile.writelines("\n= MISSING =\n")
            for rom in xmlRomsNotInSet:
                auditLogFile.writelines(rom+"\n")
        if numNoCRC > 0:
            auditLogFile.writelines("\n=== This romset contains "+str(numNoCRC)+pluralize(" file", numNoCRC)+" with no known database match ===\n\n")
            for rom in romsWithoutCRCMatch:
                auditLogFile.writelines(rom+"\n")
        auditLogFile.close()

    def renameArchiveAndContent_ZIP_RAR_7Z(self, zippedFile, archivePath, archiveExt, newName):
        if archiveExt in [".zip", ".rar"]:
            zippedFiles = zippedFile.namelist()
        else:
            zippedFiles = zippedFile.getnames()
        if len(zippedFiles) > 1:
            self.writeTextToSubProgress("Archive contains more than one file. Skipping.\n")
            return
        fileExt = path.splitext(zippedFiles[0])[1]
        patoolib.extract_archive(archivePath, outdir=path.dirname(archivePath))
        currExtractedFilePath = path.join(path.dirname(archivePath), zippedFiles[0])
        newArchivePath = path.join(path.dirname(archivePath), newName+archiveExt)
        newExtractedFilePath = path.splitext(newArchivePath)[0]+fileExt
        rename(currExtractedFilePath, newExtractedFilePath)
        return fileExt, newArchivePath, newExtractedFilePath

    def renameArchiveAndContent(self, archivePath, archiveExt, newName):
        if archiveExt == ".zip":
            with zipfile.ZipFile(archivePath, 'r', zipfile.ZIP_DEFLATED) as zippedFile:
                fileExt, newArchivePath, newExtractedFilePath = self.renameArchiveAndContent_ZIP_RAR_7Z(zippedFile, archivePath, archiveExt, newName)
        elif archiveExt == ".rar":
            with rarfile.RarFile(archivePath, 'r') as zippedFile:
                fileExt, newArchivePath, newExtractedFilePath = self.renameArchiveAndContent_ZIP_RAR_7Z(zippedFile, archivePath, archiveExt, newName)
        elif archiveExt == ".7z":
            with py7zr.SevenZipFile(archivePath, 'r') as zippedFile:
                fileExt, newArchivePath, newExtractedFilePath = self.renameArchiveAndContent_ZIP_RAR_7Z(zippedFile, archivePath, archiveExt, newName)
        if not path.isfile(newArchivePath):
            patoolib.create_archive(newArchivePath, [newExtractedFilePath])
        remove(archivePath)
        remove(newExtractedFilePath)
        self.writeTextToSubProgress("Renamed "+path.splitext(path.basename(archivePath))[0]+" to "+newName+"\n\n")

    ##################
    # EXPORT (Logic) #
    ##################

    def mainExport(self, systemIndices):
        global currSystemName, currSystemSourceFolder, currSystemTargetFolder, currSystemDAT, romsetCategory
        global includeOtherRegions, extractArchives, exportToGameParentFolder, sortByPrimaryRegion, primaryRegionInRoot
        global specialCategoryFolder, letterFolder, overwriteDuplicates, ignoredFolders, primaryRegions, favoritesList
        global includeSpecial, export_regionGroupNames, export_regionPriorityTypes, export_regionTags

        if not self.recentlyVerified:
            if not askyesno("EzRO Export", "If you haven't done so already, it is recommended that you update/audit your romsets whenever you export (or if this is your first time running EzRO). This will make sure your rom names match those in the No-Intro DAT files.\n\nContinue with export?"):
                return

        self.exportInProgress = True
        self.cancelledExport = False
        export_regionGroupNames = self.regionGroupNames + [self.regionGroupTertiary]
        for i in range(len(export_regionGroupNames)):
            export_regionGroupNames[i] = export_regionGroupNames[i].get()
        export_regionPriorityTypes = self.regionPriorityTypes + [tk.StringVar(value="Secondary")]
        for i in range(len(export_regionPriorityTypes)):
            export_regionPriorityTypes[i] = export_regionPriorityTypes[i].get()
        export_regionTags = self.regionTags[:]
        tertiaryTags = []
        # Not needed
        # for regionTag in ["World", "U", "USA", "E", "Europe", "United Kingdom", "En", "A", "Australia", "Ca", "Canada", "J", "Japan", "Ja", "F", "France", "Fr", "G", "Germany", "De", "S", "Spain", "Es", "I", "Italy", "It", "No", "Norway", "Br", "Brazil", "Sw", "Sweden", "Cn", "China", "Zh", "K", "Korea", "Ko", "As", "Asia", "Ne", "Netherlands", "Ru", "Russia", "Da", "Denmark", "Nl", "Pt", "Sv", "No", "Da", "Fi", "Pl"]:
        #     addToTertiary = True
        #     for rtGroup in self.regionTags:
        #         if regionTag in self.commaSplit(rtGroup.get()):
        #             addToTertiary = False
        #             break
        #     if addToTertiary:
        #         tertiaryTags.append(regionTag)
        export_regionTags.append(tk.StringVar(value=", ".join(tertiaryTags)))
        for i in range(len(export_regionTags)):
            export_regionTags[i] = export_regionTags[i].get()

        numCopiedBytesMain = 0
        self.Export_MainProgress_Bar['value'] = 0
        for currIndex in systemIndices:
            currSystemName = self.exportSystemNames[currIndex]
            if self.isExport:
                self.Export_MainProgress_Label.configure(text='Exporting system: '+currSystemName)
            else:
                self.Export_MainProgress_Label.configure(text='Testing export of system: '+currSystemName)
            self.writeTextToSubProgress("====================\n\n"+currSystemName+"\n")
            currSystemDAT = self.datFilePathChoices[currIndex].get()
            currSystemSourceFolder = self.romsetFolderPathChoices[currIndex].get()
            currSystemTargetFolder = self.outputFolderDirectoryChoices[currIndex].get()
            romsetCategory = self.outputTypeChoices[currIndex].get()
            favoritesFile = self.romListFileChoices[currIndex].get()
            includeOtherRegions = self.includeOtherRegionsChoices[currIndex].get()
            ignoredFolders = []
            includeSpecial = []
            for i in range(len(SpecialCategories)):
                includeSpecial.append(self.includeSpecialChoices[i][currIndex].get())
                if (not includeSpecial[i]) and ((SpecialCategories[i].exclusiveSystems is None) or (currSystemName in SpecialCategories[i].exclusiveSystems)):
                    ignoredFolders.append(SpecialCategories[i].name)
            extractArchives = self.extractArchivesChoices[currIndex].get()
            exportToGameParentFolder = self.parentFolderChoices[currIndex].get()
            sortByPrimaryRegion = self.sortByPrimaryRegionChoices[currIndex].get()
            primaryRegionInRoot = self.primaryRegionInRootChoices[currIndex].get()
            specialCategoryFolder = self.specialCategoryFolderChoices[currIndex].get()
            letterFolder = self.letterFolderChoices[currIndex].get()
            overwriteDuplicates = self.overwriteDuplicatesChoices[currIndex].get()
            primaryRegions = []
            for i in range(len(export_regionGroupNames)):
                if export_regionPriorityTypes[i] == "Primary":
                    primaryRegions.append(export_regionGroupNames[i])
            favoritesList = {}
            if romsetCategory == "Favorites":
                with open(favoritesFile, 'r') as ff:
                    for line in ff.readlines():
                        if line.strip() != "" and not line.startswith("#"):
                            favoritesList[line.strip()] = False
            self.checkSystemDATForClones()
            self.generateGameRomDict(currIndex)
            numCopiedBytesMain += self.copyMainRomset(currIndex)
            self.Export_MainProgress_Bar['value'] += 1
        self.writeTextToSubProgress("====================\n\nTotal Export Size: "+simplifyNumBytes(numCopiedBytesMain)+"\n\n")
        self.writeTextToSubProgress("Review the log files for more information on what files "+("were" if self.isExport else "would be")+" transferred.\n")
        self.writeTextToSubProgress("Log files are not created for systems that "+("do" if self.isExport else "would")+" not receive any new files.\n\n")
        self.recentlyVerified = True
        self.writeTextToSubProgress("Done.")
        if self.isExport:
            self.Export_MainProgress_Label.configure(text="Export complete.")
        else:
            self.Export_MainProgress_Label.configure(text="Test export complete.")
        self.export_cancelButtonText.set("Finish")
        self.exportInProgress = False

    def checkSystemDATForClones(self):
        global currSystemHasClones
        tempTree = ET.parse(currSystemDAT)
        tempTreeRoot = tempTree.getroot()
        tempAllGameFields = tempTreeRoot[1:]
        for game in tempAllGameFields:
            gameName = game.get("name")
            try:
                gameCloneOf = game.get("cloneof")
            except:
                gameCloneOf = None
            if gameCloneOf is not None:
                currSystemHasClones = True
                return
        currSystemHasClones = False

    def generateGameRomDict(self, currIndex):
        global gameRomDict, newGameRomDict, allGameFields
        gameRomDict = {}
        tree = ET.parse(currSystemDAT)
        treeRoot = tree.getroot()
        allGameFields = treeRoot[1:]
        gameNameToCloneOf = {}
        for game in allGameFields:
            gameName = game.get("name")
            try:
                gameCloneOf = game.get("cloneof")
            except:
                gameCloneOf = None
            gameNameToCloneOf[gameName] = gameCloneOf
        for file in listdir(currSystemSourceFolder):
            _, _, _, currRegionType = self.getRomsInBestRegion([path.splitext(file)[0]])
            if currRegionType != "Primary" and romsetCategory == "1G1R" and not includeOtherRegions:
                continue
            romName = path.splitext(file)[0]
            if romName in gameNameToCloneOf:
                parent = gameNameToCloneOf[romName]
                if parent is None:
                    self.addGameAndRomToDict(romName, file)
                else:
                    self.addGameAndRomToDict(parent, file)
        # Rename gameRomDict keys according to best game name
        newGameRomDict = {}
        for game in gameRomDict.keys():
            bestGameName = self.getBestGameName(gameRomDict[game])
            mergeBoth = False
            if bestGameName in newGameRomDict: # same name for two different games (Pokemon Stadium International vs. Japan)
                finalFirstGameName, finalSecondGameName, renameByAtts = self.fixDuplicateName(newGameRomDict[bestGameName], gameRomDict[game], bestGameName)
                if renameByAtts: # rename first game according to region
                    newGameRomDict[finalFirstGameName] = newGameRomDict.pop(bestGameName)
                    newGameRomDict[finalSecondGameName] = gameRomDict[game]
                else: # rename neither (merge the two together); rare, but possible, such as DS demos that have both a DS Download Station and a Nintendo Channel version
                    for rom in gameRomDict[game]: # rename one or both games according to 
                        newGameRomDict[bestGameName].append(rom)
            else:
                newGameRomDict[bestGameName] = gameRomDict[game]
        gameRomDict = newGameRomDict

    def getRomsInBestRegion(self, roms):
        romsInBestRegion = []
        bestRegionIndex = 99
        bestRegion = None
        bestRegionType = 0
        for rom in roms:
            attributeSplit = self.getAttributeSplit(rom)
            for i in range(len(export_regionGroupNames)):
                region = export_regionGroupNames[i]
                currRegionAtts = self.commaSplit(export_regionTags[i])
                regionType = (2 if export_regionPriorityTypes[i]=="Primary" else 1)
                if arrayOverlap(attributeSplit, currRegionAtts) or i==len(export_regionGroupNames)-1:
                    if regionType >= bestRegionType:
                        if i < bestRegionIndex or regionType > bestRegionType:
                            bestRegionIndex = i
                            romsInBestRegion = [rom]
                            bestRegion = region
                            bestRegionType = regionType
                        elif i == bestRegionIndex:
                            romsInBestRegion.append(rom)
                        if regionType == 2:
                            break
        bestRegionType = (None, "Secondary", "Primary")[bestRegionType]
        return romsInBestRegion, bestRegionIndex, bestRegion, bestRegionType

    def getAttributeSplit(self, name):
        mna = [s.strip() for s in re.split('\(|\)|\[|\]', path.splitext(name)[0]) if s.strip() != ""]
        if name.startswith(specialFolderPrefix+"BIOS"+specialFolderSuffix) and len(mna) > 1:
            mna[:2] = [specialFolderPrefix+"BIOS"+specialFolderSuffix+" "+mna[1]]
        mergeNameArray = []
        mergeNameArray.append(mna[0])
        if len(mna) > 1:
            for i in range(1, len(mna)):
                if not ("," in mna[i] or "+" in mna[i]):
                    mergeNameArray.append(mna[i])
                else:
                    arrayWithComma = [s.strip() for s in re.split('\,|\+', mna[i]) if s.strip() != ""]
                    for att2 in arrayWithComma:
                        mergeNameArray.append(att2)
        return mergeNameArray

    def commaSplit(self, string):
        if string.strip() == "":
            return [] # otherwise, it would return [""]
        return [s.strip() for s in string.split(",")]

    def barSplit(self, string):
        if string.strip() == "":
            return [] # otherwise, it would return [""]
        return [s.strip() for s in string.split("|")]

    def addGameAndRomToDict(self, game, rom):
        global gameRomDict
        if game not in gameRomDict.keys():
            gameRomDict[game] = []
        gameRomDict[game].append(rom)

    def getBestGameName(self, roms):
        bestRom, _, _ = self.getBestRom(roms)
        atts = self.getAttributeSplit(bestRom)
        return atts[0].rstrip(".")

    def getBestRom(self, roms):
        romsInBestRegion, _, bestRegion, bestRegionType = self.getRomsInBestRegion(roms)
        if len(romsInBestRegion) == 1:
            return romsInBestRegion[0], bestRegion, bestRegionType
        bestScore = -500
        bestRom = ""
        for rom in romsInBestRegion:
            currScore = self.getScore(rom)
            if currScore >= bestScore:
                bestScore = currScore
                bestRom = rom
        return bestRom, bestRegion, bestRegionType

    def getScore(self, rom):
        # We already know that this is only called for roms that are in the best region
        attributes = self.getAttributeSplit(rom)[1:]
        score = 100
        lastVersion = 0

        primaryRegionTags = []
        for i in range(len(export_regionGroupNames)):
            if export_regionPriorityTypes[i] == "Primary":
                primaryRegionTags += self.commaSplit(export_regionTags[i])
        while "" in primaryRegionTags:
            primaryRegionTags.remove("") # probably not needed, but just in case
        containsPrimaryLanguage = False
        containsOtherLanguage = False
        for att in attributes:
            if att.startswith("Rev") or att.startswith("Reprint"):
                try:
                    score += 15 + (15 * int(att.split()[1]))
                except:
                    score += 30
            elif att.startswith("v") and len(att) > 1 and att[1].isdigit():
                try:
                    score += float(att[1:])
                    lastVersion = float(att[1:])
                except:
                    score += lastVersion
            elif att.startswith("b") and (len(att) == 1 or att[1].isdigit()):
                if len(att) == 1:
                    score -= 30
                else:
                    try:
                        score -= (15 - float(att[1:]))
                        lastVersion = float(att[1:])
                    except:
                        score -= (15 - lastVersion)
            elif att.startswith("Beta") or att.startswith("Proto"):
                try:
                    score -= (50 - int(att.split()[1]))
                except:
                    score -= 49
            elif att.startswith("Sample") or att.startswith("Demo"):
                try:
                    score -= (90 - int(att.split()[1]))
                except:
                    score -= 89
            elif "Collection" in att:
                score -= 10
            elif att in SpecificAttributes:
                score -= 10
            elif "DLC" in att:
                score -= 10
            elif att in ["Unl", "Pirate"]:
                score -= 20
            elif att in ["En", "Ca", "Ja", "Fr", "De", "Es", "It", "No", "Br", "Sw", "Cn", "Zh", "Ko", "As", "Ne", "Ru", "Da", "Nl", "Pt", "Sv", "No", "Da", "Fi", "Pl"]:
                if att in primaryRegionTags:
                    containsPrimaryLanguage = True
                else:
                    containsOtherLanguage = True
            elif not (att in SpecificAttributes or any(att.startswith(starter) for starter in GeneralAttributes)): # a tiebreaker for any new keywords that are later added
                score -= 1
        if (not containsPrimaryLanguage) and containsOtherLanguage:
            score -= 2
        return score

    def fixDuplicateName(self, firstGameRoms, secondGameRoms, sharedName):
        global newGameRomDict
        firstBestRoms, firstRegionNum, _, _ = self.getRomsInBestRegion(firstGameRoms)
        secondBestRoms, secondRegionNum, _, _ = self.getRomsInBestRegion(secondGameRoms)
        if currSystemHasClones and (firstRegionNum != secondRegionNum):
            newFirstGameName = sharedName+" ("+export_regionGroupNames[firstRegionNum]+")"
            newSecondGameName = sharedName+" ("+export_regionGroupNames[secondRegionNum]+")"
            return newFirstGameName, newSecondGameName, True
        else:
            firstUniqueAtts, secondUniqueAtts = self.getUniqueAttributes(self.getBestRom(firstBestRoms)[0], self.getBestRom(secondBestRoms)[0])
            if len(firstUniqueAtts) > 0 or len(secondUniqueAtts) > 0:
                newFirstGameName = sharedName
                for att in firstUniqueAtts:
                    newFirstGameName += " ("+att+")"
                newSecondGameName = sharedName
                for att in secondUniqueAtts:
                    newSecondGameName += " ("+att+")"
                return newFirstGameName, newSecondGameName, True
            else:
                return None, None, False

    def getUniqueAttributes(self, firstRom, secondRom):
        firstAtts = self.getAttributeSplit(firstRom)
        firstAtts.pop(0)
        secondAtts = self.getAttributeSplit(secondRom)
        secondAtts.pop(0)
        firstUniqueAtts = []
        tempStarters = GeneralAttributes[:]
        try:
            tempStarters.remove("Proto") # Exerion
        except:
            pass
        for att in firstAtts:
            if att in secondAtts or att in SpecificAttributes or self.attIsRegion(att):
                continue
            if att.startswith("v") and len(att) > 1 and att[1].isdigit():
                continue
            if att.startswith("b") and (len(att) == 1 or att[1].isdigit()):
                continue
            if not any(att.startswith(starter) for starter in tempStarters):
                firstUniqueAtts.append(att)
        secondUniqueAtts = []
        for att in secondAtts:
            if att in firstAtts or att in SpecificAttributes or self.attIsRegion(att):
                continue
            if att.startswith("v") and len(att) > 1 and att[1].isdigit():
                continue
            if att.startswith("b") and (len(att) == 1 or att[1].isdigit()):
                continue
            if not any(att.startswith(starter) for starter in tempStarters):
                secondUniqueAtts.append(att)
        if ("Proto" in firstUniqueAtts + secondUniqueAtts) and (len(firstUniqueAtts) + len(secondUniqueAtts) > 1):
            if "Proto" in firstUniqueAtts:
                firstUniqueAtts.remove("Proto")
            elif "Proto" in secondUniqueAtts:
                secondUniqueAtts.remove("Proto")
        return firstUniqueAtts, secondUniqueAtts

    def attIsRegion(self, att):
        for tags in export_regionTags:
            if att in self.commaSplit(tags):
                return True
        return False

    def getFirstLetter(self, string):
        strippedName = string.lstrip("\'").lstrip(".")
        if len(strippedName) == 0:
            return "!"
        if strippedName[0].isalpha():
            return strippedName[0].upper()
        if strippedName[0].isnumeric():
            return "0-9"
        return strippedName[0]

    def copyMainRomset(self, currIndex):
        global gameRomDict, bestRegionForGame, currGameFolder, bestRegionIsPrimary
        global romsetCategory, favoritesList, missingFavorites
        numGames = len(gameRomDict.keys())
        self.romsCopied = []
        self.numRomsSkipped = 0
        self.romsFailed = []
        self.currNumCopiedBytes = 0
        self.Export_SubProgress_Bar.configure(maximum=str(numGames))
        self.Export_SubProgress_Bar['value'] = 0
        for game in gameRomDict.keys():
            self.Export_SubProgress_Bar['value'] += 1
            bestRom, bestRegionForGame, bestRegionType = self.getBestRom(gameRomDict[game])
            bestRegionIsPrimary = (bestRegionType == "Primary")
            currSpecialFolders = self.getSpecialFolders(bestRom)
            if arrayOverlap(currSpecialFolders, ignoredFolders):
                continue
            # Start building output path according to attributes
            currGameFolder = currSystemTargetFolder
            currGameFolder = path.join(currGameFolder, "<REGIONFOLDER>")
            # if sortByPrimaryRegion and (not (bestRegionIsPrimary and primaryRegionInRoot)):
            #     currGameFolder = path.join(currGameFolder, specialFolderPrefix+bestRegionForGame+specialFolderSuffix)
            if specialCategoryFolder:
                for folder in currSpecialFolders:
                    currGameFolder = path.join(currGameFolder, specialFolderPrefix+folder+specialFolderSuffix)
            if letterFolder:
                currGameFolder = path.join(currGameFolder, "<FIRSTLETTER>")
            if exportToGameParentFolder:
                currGameFolder = path.join(currGameFolder, game)
            if romsetCategory in ["All", "Favorites"]:
                for rom in gameRomDict[game]:
                    if romsetCategory == "All":
                        self.copyRomToTarget(rom, game)
                    elif path.splitext(rom)[0] in favoritesList.keys():
                        self.copyRomToTarget(rom, game)
                        favoritesList[path.splitext(rom)[0]] = True
            elif romsetCategory == "1G1R" or bestRegionIsPrimary:
                self.copyRomToTarget(bestRom, game)
            tk_root.update()
            if self.cancelledExport:
                break
        missingFavorites = []
        if self.isExport:
            self.writeTextToSubProgress("Copied "+str(len(self.romsCopied))+" new files.\n")
            self.writeTextToSubProgress("Skipped "+str(self.numRomsSkipped)+" files that already exist in the output directory.\n")
            self.writeTextToSubProgress("Failed to copy "+str(len(self.romsFailed))+" new files.\n")
            if romsetCategory == "Favorites":
                for rom in favoritesList.keys():
                    if favoritesList[rom] == False:
                        missingFavorites.append(rom)
                if len(missingFavorites) > 0:
                    self.writeTextToSubProgress(str(len(missingFavorites))+" roms from favorites list were not copied because they were not found in the input romset.\n")
        else:
            self.writeTextToSubProgress(str(len(self.romsCopied))+" new files would be copied.\n")
            self.writeTextToSubProgress(str(self.numRomsSkipped)+" old files would be skipped.\n")
        self.writeTextToSubProgress("Export Size: "+simplifyNumBytes(self.currNumCopiedBytes)+"\n\n")
        self.createMainCopiedLog(currIndex, "Export" if self.isExport else "Test")
        return self.currNumCopiedBytes

    # lazy copy/paste job, but it works
    def getRomRegion(self, rom):
        bestRegionIndex = 99
        bestRegion = None
        bestRegionType = 0
        attributeSplit = self.getAttributeSplit(rom)
        for i in range(len(export_regionGroupNames)):
            region = export_regionGroupNames[i]
            currRegionAtts = self.commaSplit(export_regionTags[i])
            regionType = (2 if export_regionPriorityTypes[i]=="Primary" else 1)
            if arrayOverlap(attributeSplit, currRegionAtts) or i==len(export_regionGroupNames)-1:
                if regionType >= bestRegionType:
                    if i < bestRegionIndex or regionType > bestRegionType:
                        bestRegionIndex = i
                        bestRegion = region
                        bestRegionType = regionType
                    if regionType == 2:
                        break
        # bestRegionType = (None, "Secondary", "Primary")[bestRegionType]
        return bestRegion, bestRegionType

    def copyRomToTarget(self, rom, game):
        global currGameFolder
        currGameFolderTemp = currGameFolder.replace("\\", "/")
        if sortByPrimaryRegion:
            if exportToGameParentFolder:
                if not (bestRegionIsPrimary and primaryRegionInRoot):
                    currGameFolderTemp = currGameFolderTemp.replace("<REGIONFOLDER>", specialFolderPrefix+bestRegionForGame+specialFolderSuffix)
            else:
                bestRegionForRom, bestRegionType = self.getRomRegion(rom)
                if bestRegionType < 2:
                    currGameFolderTemp = currGameFolderTemp.replace("<REGIONFOLDER>", specialFolderPrefix+bestRegionForRom+specialFolderSuffix)
        currGameFolderTemp = currGameFolderTemp.replace("/<REGIONFOLDER>", "/")
        if letterFolder:
            if exportToGameParentFolder:
                currGameFolderTemp = currGameFolderTemp.replace("<FIRSTLETTER>", self.getFirstLetter(game))
            else:
                currGameFolderTemp = currGameFolderTemp.replace("<FIRSTLETTER>", self.getFirstLetter(rom))
        sourceRomPath = path.join(currSystemSourceFolder, rom)
        targetRomPath = path.join(currGameFolderTemp, rom)
        if overwriteDuplicates or (not self.targetExists(sourceRomPath, targetRomPath)):
            try:
                createdFolder = self.isExport and createDir(currGameFolderTemp)
                fileExt = path.splitext(sourceRomPath)[1]
                if extractArchives and (fileExt in archiveTypes):
                    if fileExt == ".zip":
                        with zipfile.ZipFile(sourceRomPath, 'r', zipfile.ZIP_DEFLATED) as zippedFile:
                            if self.isExport:
                                patoolib.extract_archive(sourceRomPath, outdir=currGameFolderTemp)
                            self.currNumCopiedBytes += zippedFile.infolist()[0].file_size
                    elif fileExt == ".rar":
                        with rarfile.RarFile(sourceRomPath, 'r') as zippedFile:
                            if self.isExport:
                                patoolib.extract_archive(sourceRomPath, outdir=currGameFolderTemp)
                            self.currNumCopiedBytes += zippedFile.infolist()[0].file_size
                    elif fileExt == ".7z":
                        with py7zr.SevenZipFile(sourceRomPath, 'r') as zippedFile:
                            if self.isExport:
                                patoolib.extract_archive(sourceRomPath, outdir=currGameFolderTemp)
                            self.currNumCopiedBytes += zippedFile.list()[0].uncompressed
                else:
                    if self.isExport:
                        shutil.copy(sourceRomPath, targetRomPath)
                        self.currNumCopiedBytes += path.getsize(targetRomPath)
                    else:
                        self.currNumCopiedBytes += path.getsize(sourceRomPath)
                self.romsCopied.append(rom)
            except:
                # progressBar.write("\nFailed to copy: "+rom)
                if createdFolder and len(listdir(currGameFolderTemp)) == 0:
                    rmdir(currGameFolderTemp)
                self.romsFailed.append(rom)
        else:
            self.numRomsSkipped += 1

    def targetExists(self, sourceRomPath, targetRomPath):
        fileExt = path.splitext(sourceRomPath)[1]
        if not (extractArchives and (fileExt in archiveTypes)):
            return path.isfile(targetRomPath)
        elif fileExt == ".zip":
            with zipfile.ZipFile(sourceRomPath, 'r', zipfile.ZIP_DEFLATED) as zippedFile:
                tempTargetRomPath = path.join(path.dirname(targetRomPath), zippedFile.namelist()[0])
        elif fileExt == ".rar":
            with rarfile.RarFile(sourceRomPath, 'r') as zippedFile:
                tempTargetRomPath = path.join(path.dirname(targetRomPath), zippedFile.namelist()[0])
        elif fileExt == ".7z":
            with py7zr.SevenZipFile(sourceRomPath, 'r') as zippedFile:
                tempTargetRomPath = path.join(path.dirname(targetRomPath), zippedFile.getnames()[0])
        return path.isfile(tempTargetRomPath)

    def getSpecialFolders(self, rom):
        currSpecialFolders = []
        for category in SpecialCategories:
            if category.exclusiveSystems is None or (currSystemName in category.exclusiveSystems):
                for keyword in category.keywords:
                    if keyword in rom:
                        currSpecialFolders.append(category.name)
                        break
        return currSpecialFolders

    def createMainCopiedLog(self, currIndex, logType="Export"):
        currTime = datetime.now().isoformat(timespec='seconds').replace(":", ".")
        if len(self.romsCopied) + len(self.romsFailed) > 0:
            self.romsCopied.sort()
            self.romsFailed.sort()
            romsetLogFile = open(path.join(logFolder, currTime+" "+logType+" ("+currSystemName+") ["+str(len(self.romsCopied))+"] ["+str(len(self.romsFailed)+len(missingFavorites))+"].txt"), "w", encoding="utf-8", errors="replace")
            romsetLogFile.writelines("=== Copied "+str(len(self.romsCopied))+" new ROMs from \""+currSystemSourceFolder+"\" to \""+currSystemTargetFolder+"\" ===\n\n")
            for file in self.romsCopied:
                romsetLogFile.writelines(file+"\n")
            if len(self.romsFailed) > 0:
                romsetLogFile.writelines("\n= FAILED TO COPY =\n")
                for file in self.romsFailed:
                    romsetLogFile.writelines(file+"\n")
            if len(missingFavorites) > 0:
                romsetLogFile.writelines("\n= FAVORITES NOT FOUND IN INPUT =\n")
                for file in missingFavorites:
                    romsetLogFile.writelines(file+"\n")
            romsetLogFile.close()

    #############
    # FAVORITES #
    #############

    def favorites_loadList(self):
        pass

    def favorites_addFiles(self):
        pass

    def favorites_saveList(self):
        pass

    ##########
    # CONFIG #
    ##########

    def addRegionGroup(self, groupName="", groupType="", groupTags=""):
        self.Config_Region_Choice_RemoveButton_.append(None)
        self.Config_Region_Choice_UpButton_.append(None)
        self.Config_Region_Choice_DownButton_.append(None)
        self.Config_Region_Choice_Name_Label_.append(None)
        self.Config_Region_Choice_Name_Entry_.append(None)
        self.regionGroupNames.append(None)
        self.Config_Region_Choice_Name_Entry_.append(None)
        self.Config_Region_Choice_Type_Label_.append(None)
        self.Config_Region_Choice_Type_Combobox_.append(None)
        self.regionPriorityTypes.append(None)
        self.Config_Region_Choice_Type_Combobox_.append(None)
        self.Config_Region_Choice_Tags_Label_.append(None)
        self.Config_Region_Choice_Tags_Entry_.append(None)
        self.regionTags.append(None)
        self.Config_Region_Choice_Tags_Entry_.append(None)
        self.Config_Region_Choice_RemoveButton_[self.regionNum] = ttk.Button(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_RemoveButton_[self.regionNum].configure(text='X', width='2')
        self.Config_Region_Choice_RemoveButton_[self.regionNum].grid(column='0', padx='20', pady='10', row=self.regionNum, sticky='w')
        self.Config_Region_Choice_RemoveButton_[self.regionNum].configure(command=lambda n=self.regionNum: self.removeRegionGroup(n))
        self.Config_Region_Choice_UpButton_[self.regionNum] = ttk.Button(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_UpButton_[self.regionNum].configure(text='↑', width='2')
        self.Config_Region_Choice_UpButton_[self.regionNum].grid(column='0', padx='50', pady='10', row=self.regionNum, sticky='w')
        self.Config_Region_Choice_UpButton_[self.regionNum].configure(command=lambda n=self.regionNum: self.moveRegionGroupUp(n))
        self.Config_Region_Choice_DownButton_[self.regionNum] = ttk.Button(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_DownButton_[self.regionNum].configure(text='↓', width='2')
        self.Config_Region_Choice_DownButton_[self.regionNum].grid(column='0', padx='80', pady='10', row=self.regionNum, sticky='w')
        self.Config_Region_Choice_DownButton_[self.regionNum].configure(command=lambda n=self.regionNum: self.moveRegionGroupDown(n))
        self.Config_Region_Choice_Name_Label_[self.regionNum] = ttk.Label(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Name_Label_[self.regionNum].configure(text='Region Group')
        self.Config_Region_Choice_Name_Label_[self.regionNum].grid(column='0', padx='130', pady='10', row=self.regionNum, sticky='w')
        self.Config_Region_Choice_Name_Entry_[self.regionNum] = ttk.Entry(self.Config_Region_Frame.innerframe)
        self.regionGroupNames[self.regionNum] = tk.StringVar(value=groupName)
        self.Config_Region_Choice_Name_Entry_[self.regionNum].configure(textvariable=self.regionGroupNames[self.regionNum])
        self.Config_Region_Choice_Name_Entry_[self.regionNum].grid(column='0', padx='220', pady='10', row=self.regionNum, sticky='w')
        self.Config_Region_Choice_Type_Label_[self.regionNum] = ttk.Label(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Type_Label_[self.regionNum].configure(text='Priority Type')
        self.Config_Region_Choice_Type_Label_[self.regionNum].grid(column='0', padx='380', pady='10', row=self.regionNum, sticky='w')
        self.Config_Region_Choice_Type_Combobox_[self.regionNum] = ttk.Combobox(self.Config_Region_Frame.innerframe)
        self.regionPriorityTypes[self.regionNum] = tk.StringVar(value=groupType)
        self.Config_Region_Choice_Type_Combobox_[self.regionNum].configure(state='readonly', textvariable=self.regionPriorityTypes[self.regionNum], values='"Primary" "Secondary"', width='12')
        self.Config_Region_Choice_Type_Combobox_[self.regionNum].grid(column='0', padx='465', pady='10', row=self.regionNum, sticky='w')
        self.Config_Region_Choice_Type_Combobox_[self.regionNum].bind('<<ComboboxSelected>>', self.settings_region_setPriorityType, add='')
        if groupType == "Secondary":
            self.Config_Region_Choice_Type_Combobox_[self.regionNum].current(1)
        else:
            self.Config_Region_Choice_Type_Combobox_[self.regionNum].current(0)
        self.Config_Region_Choice_Tags_Label_[self.regionNum] = ttk.Label(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Tags_Label_[self.regionNum].configure(text='Region/Language Tags')
        self.Config_Region_Choice_Tags_Label_[self.regionNum].grid(column='0', padx='580', pady='10', row=self.regionNum, sticky='w')
        self.Config_Region_Choice_Tags_Entry_[self.regionNum] = ttk.Entry(self.Config_Region_Frame.innerframe)
        self.regionTags[self.regionNum] = tk.StringVar(value=groupTags)
        self.Config_Region_Choice_Tags_Entry_[self.regionNum].configure(textvariable=self.regionTags[self.regionNum], width='45')
        self.Config_Region_Choice_Tags_Entry_[self.regionNum].grid(column='0', padx='720', pady='10', row=self.regionNum, sticky='w')
        tooltip.create(self.Config_Region_Choice_Name_Label_[self.regionNum], 'The name of the region group. If \"Create Region Folders\" is enabled, then roms marked as one of this group\'s region tags will be exported to a folder named after this group, surround by brackets (e.g. '+specialFolderPrefix+'World'+specialFolderSuffix+', '+specialFolderPrefix+'USA'+specialFolderSuffix+', etc).')
        tooltip.create(self.Config_Region_Choice_Type_Label_[self.regionNum], 'The type of region group.\n\nPrimary: The most significant region; 1G1R exports will prioritize this. If there are multiple Primary groups, then higher groups take priority.\n\nSecondary: \"Backup\" regions that will not be used in a 1G1R export unless no Primary-group version of a game exists, and \"Include Games from Non-Primary Regions\" is also enabled. If there are multiple Secondary groups, then higher groups take priority.\n\nTertiary: Any known region/language tag that is not part of a Primary/Secondary group is added to the Tertiary group by default. This is functionally the same as a Secondary group.')
        tooltip.create(self.Config_Region_Choice_Tags_Label_[self.regionNum], 'Rom tags that signify that a rom belongs to this group (region tags like USA and Europe, language tags like En and Fr, etc). If a rom contains tags from multiple region groups, then the higher group will take priority.')

        self.regionNum += 1

    def settings_region_setPriorityType(self, event=None):
        pass

    def config_region_applyTemplate(self, event=None):
        choice = self.templateChoice.get()
        if choice != "":
            while self.regionNum > 0:
                self.removeRegionGroup(0)
            if choice == "English":
                self.addRegionGroup(groupName="World", groupType="Primary", groupTags="World")
                self.addRegionGroup(groupName="USA", groupType="Primary", groupTags="U, USA")
                self.addRegionGroup(groupName="Europe", groupType="Primary", groupTags="E, Europe, United Kingdom")
                self.addRegionGroup(groupName="Other (English)", groupType="Primary", groupTags="En, A, Australia, Ca, Canada")
                self.regionGroupTertiary.set("Other (non-English)")
            elif choice == "English + Secondary":
                self.addRegionGroup(groupName="World", groupType="Primary", groupTags="World")
                self.addRegionGroup(groupName="USA", groupType="Primary", groupTags="U, USA")
                self.addRegionGroup(groupName="Europe", groupType="Primary", groupTags="E, Europe, United Kingdom")
                self.addRegionGroup(groupName="Other (English)", groupType="Primary", groupTags="En, A, Australia, Ca, Canada")
                self.addRegionGroup(groupName="Japan", groupType="Secondary", groupTags="J, Japan, Ja")
                self.regionGroupTertiary.set("Other (non-English)")
            elif choice == "English (USA Focus)":
                self.addRegionGroup(groupName="World", groupType="Primary", groupTags="World")
                self.addRegionGroup(groupName="USA", groupType="Primary", groupTags="U, USA")
                self.addRegionGroup(groupName="Europe", groupType="Secondary", groupTags="E, Europe, United Kingdom")
                self.addRegionGroup(groupName="Other (English)", groupType="Secondary", groupTags="En, A, Australia, Ca, Canada")
                self.regionGroupTertiary.set("Other (non-English)")
            elif choice == "English (Europe Focus)":
                self.addRegionGroup(groupName="World", groupType="Primary", groupTags="World")
                self.addRegionGroup(groupName="Europe", groupType="Primary", groupTags="E, Europe, United Kingdom")
                self.addRegionGroup(groupName="USA", groupType="Secondary", groupTags="U, USA")
                self.addRegionGroup(groupName="Other (English)", groupType="Secondary", groupTags="En, A, Australia, Ca, Canada")
                self.regionGroupTertiary.set("Other (non-English)")
            elif choice == "Japanese":
                self.addRegionGroup(groupName="World", groupType="Primary", groupTags="World")
                self.addRegionGroup(groupName="Japan", groupType="Primary", groupTags="J, Japan")
                self.addRegionGroup(groupName="Other (Japanese)", groupType="Primary", groupTags="Ja")
                self.regionGroupTertiary.set("Other (non-Japanese)")
            elif choice == "Japanese + Secondary":
                self.addRegionGroup(groupName="World", groupType="Primary", groupTags="World")
                self.addRegionGroup(groupName="Japan", groupType="Primary", groupTags="J, Japan")
                self.addRegionGroup(groupName="Other (Japanese)", groupType="Primary", groupTags="Ja")
                self.addRegionGroup(groupName="USA", groupType="Secondary", groupTags="U, USA")
                self.addRegionGroup(groupName="Europe", groupType="Secondary", groupTags="E, Europe, United Kingdom")
                self.regionGroupTertiary.set("Other (non-Japanese)")

    def settings_region_addNewRegionCategory(self, event=None):
        self.addRegionGroup()

    def moveRegionGroupUp(self, num):
        if num > 0:
            self.Config_Region_Choice_RemoveButton_.insert(num-1, self.Config_Region_Choice_RemoveButton_.pop(num))
            self.Config_Region_Choice_UpButton_.insert(num-1, self.Config_Region_Choice_UpButton_.pop(num))
            self.Config_Region_Choice_DownButton_.insert(num-1, self.Config_Region_Choice_DownButton_.pop(num))
            self.Config_Region_Choice_Name_Label_.insert(num-1, self.Config_Region_Choice_Name_Label_.pop(num))
            self.Config_Region_Choice_Name_Entry_.insert(num-1, self.Config_Region_Choice_Name_Entry_.pop(num))
            self.regionGroupNames.insert(num-1, self.regionGroupNames.pop(num))
            self.Config_Region_Choice_Type_Label_.insert(num-1, self.Config_Region_Choice_Type_Label_.pop(num))
            self.Config_Region_Choice_Type_Combobox_.insert(num-1, self.Config_Region_Choice_Type_Combobox_.pop(num))
            self.regionPriorityTypes.insert(num-1, self.regionPriorityTypes.pop(num))
            self.Config_Region_Choice_Tags_Label_.insert(num-1, self.Config_Region_Choice_Tags_Label_.pop(num))
            self.Config_Region_Choice_Tags_Entry_.insert(num-1, self.Config_Region_Choice_Tags_Entry_.pop(num))
            self.regionTags.insert(num-1, self.regionTags.pop(num))
            self.refreshRegionChoicePlacement()

    def moveRegionGroupDown(self, num):
        if num < (self.regionNum - 1):
            self.moveRegionGroupUp(num+1)

    def removeRegionGroup(self, num):
        self.Config_Region_Choice_RemoveButton_[num].grid_remove()
        self.Config_Region_Choice_RemoveButton_.pop(num)
        self.Config_Region_Choice_UpButton_[num].grid_remove()
        self.Config_Region_Choice_UpButton_.pop(num)
        self.Config_Region_Choice_DownButton_[num].grid_remove()
        self.Config_Region_Choice_DownButton_.pop(num)
        self.Config_Region_Choice_Name_Label_[num].grid_remove()
        self.Config_Region_Choice_Name_Label_.pop(num)
        self.Config_Region_Choice_Name_Entry_[num].grid_remove()
        self.Config_Region_Choice_Name_Entry_.pop(num)
        self.regionGroupNames.pop(num)
        self.Config_Region_Choice_Type_Label_[num].grid_remove()
        self.Config_Region_Choice_Type_Label_.pop(num)
        self.Config_Region_Choice_Type_Combobox_[num].grid_remove()
        self.Config_Region_Choice_Type_Combobox_.pop(num)
        self.regionPriorityTypes.pop(num)
        self.Config_Region_Choice_Tags_Label_[num].grid_remove()
        self.Config_Region_Choice_Tags_Label_.pop(num)
        self.Config_Region_Choice_Tags_Entry_[num].grid_remove()
        self.Config_Region_Choice_Tags_Entry_.pop(num)
        self.regionTags.pop(num)
        self.regionNum -= 1
        self.refreshRegionChoicePlacement()

    def refreshRegionChoicePlacement(self):
        for i in range(self.regionNum):
            self.Config_Region_Choice_RemoveButton_[i].configure(command=lambda n=i: self.removeRegionGroup(n))
            self.Config_Region_Choice_UpButton_[i].configure(command=lambda n=i: self.moveRegionGroupUp(n))
            self.Config_Region_Choice_DownButton_[i].configure(command=lambda n=i: self.moveRegionGroupDown(n))
            self.Config_Region_Choice_RemoveButton_[i].grid(row=str(i))
            self.Config_Region_Choice_UpButton_[i].grid(row=str(i))
            self.Config_Region_Choice_DownButton_[i].grid(row=str(i))
            self.Config_Region_Choice_Name_Label_[i].grid(row=str(i))
            self.Config_Region_Choice_Name_Entry_[i].grid(row=str(i))
            self.Config_Region_Choice_Type_Label_[i].grid(row=str(i))
            self.Config_Region_Choice_Type_Combobox_[i].grid(row=str(i))
            self.Config_Region_Choice_Tags_Label_[i].grid(row=str(i))
            self.Config_Region_Choice_Tags_Entry_[i].grid(row=str(i))

    def settings_region_help(self, event=None):
        showinfo("Region Help", "Region settings are used in organizing roms from different regions and, in the case of 1G1R exports, determining which region of a game should be exported."
            +"\n\nHover over each setting to learn more; or you can simply use one of the pre-made templates. \"English + Secondary\" is recommended (it's the default), but use whatever you want."
            +"\n\nAny changes made on this page will be lost upon leaving the Config menu unless you click \"Save Changes\". This includes applying a template; remember to save!")

    def createRegionSettings(self):
        global regionSettings
        regionSettings = configparser.ConfigParser(allow_no_value=True)
        regionSettings.optionxform = str
        regionSettings["1"] = {}
        regionSettings["1"]["Region Group"] = "World"
        regionSettings["1"]["Priority Type"] = "Primary"
        regionSettings["1"]["Region/Language Tags"] = "World"
        regionSettings["2"] = {}
        regionSettings["2"]["Region Group"] = "USA"
        regionSettings["2"]["Priority Type"] = "Primary"
        regionSettings["2"]["Region/Language Tags"] = "U, USA"
        regionSettings["3"] = {}
        regionSettings["3"]["Region Group"] = "Europe"
        regionSettings["3"]["Priority Type"] = "Primary"
        regionSettings["3"]["Region/Language Tags"] = "E, Europe, United Kingdom"
        regionSettings["4"] = {}
        regionSettings["4"]["Region Group"] = "Other (English)"
        regionSettings["4"]["Priority Type"] = "Primary"
        regionSettings["4"]["Region/Language Tags"] = "En, A, Australia, Ca, Canada"
        regionSettings["5"] = {}
        regionSettings["5"]["Region Group"] = "Japan"
        regionSettings["5"]["Priority Type"] = "Secondary"
        regionSettings["5"]["Region/Language Tags"] = "J, Japan, Ja"
        regionSettings["Other"] = {}
        regionSettings["Other"]["Region Group"] = "Other (non-English)"
        regionSettings["Other"]["Priority Type"] = "Tertiary"
        with open(regionsFile, 'w') as rf:
            regionSettings.write(rf)

    def settings_saveChanges(self):
        global defaultSettings, regionSettings
        if not path.exists(defaultSettingsFile):
            self.createDefaultSettings()
        if not path.exists(regionsFile):
            self.createRegionSettings()

        try:
            defaultSettings = configparser.ConfigParser(allow_no_value=True)
            defaultSettings.optionxform = str
            defaultSettings.read(defaultSettingsFile)
            defaultSettings["General"] = {}
            defaultSettings["General"]["Input No-Intro DAT Directory"] = self.g_datFilePath.get()
            defaultSettings["General"]["Input Romset Directory"] = self.g_romsetFolderPath.get()
            defaultSettings["Organization"] = {}
            defaultSettings["Organization"]["Extract Compressed Roms"] = self.ssch(self.g_extractArchives)
            defaultSettings["Organization"]["Create Game Folder for Each Game"] = self.ssch(self.g_parentFolder)
            defaultSettings["Organization"]["Create Region Folders"] = self.ssch(self.g_sortByPrimaryRegion)
            defaultSettings["Organization"]["Do Not Create Folder for Primary Region"] = self.ssch(self.g_primaryRegionInRoot)
            defaultSettings["Organization"]["Create Folders for Special Categories"] = self.ssch(self.g_specialCategoryFolder)
            defaultSettings["Organization"]["Create Letter Folders"] = self.ssch(self.g_letterFolder)
            defaultSettings["Organization"]["Overwrite Duplicate Files"] = self.ssch(self.g_overwriteDuplicates)
            defaultSettings["Include"] = {}
            for i in range(len(SpecialCategories)):
                defaultSettings["Include"][SpecialCategories[i].name] = self.ssch(self.g_includeSpecial[i])
            defaultSettings["Include"]["(1G1R) Games from Other Regions"] = self.ssch(self.g_includeOtherRegions)
            with open(defaultSettingsFile, 'w') as mcf:
                defaultSettings.write(mcf)
            savedDefaultSettings = True
        except:
            savedDefaultSettings = False

        regionFailureReasons = ""
        try:
            for i in range(self.regionNum):
                if self.regionGroupNames[i].get().strip() == "":
                    regionFailureReasons += "Region group "+str(i+1)+" has no name.\n"
                elif self.regionGroupNames[i].get().strip() != slugify(self.regionGroupNames[i].get().strip()):
                    regionFailureReasons += "Region group "+str(i+1)+" has an invalid name.\n"
                else:
                    for j in range(i+1, self.regionNum):
                        if self.regionGroupNames[i].get().strip() == self.regionGroupNames[j].get().strip():
                            regionFailureReasons += "Region groups "+str(i+1)+" and "+str(j+1)+" have the same name.\n"
                tagsAreInvalid = True
                for tag in self.commaSplit(self.regionTags[i].get()):
                    if tag != "":
                        tagsAreInvalid = False
                        break
                if tagsAreInvalid:
                    regionFailureReasons += "Region group "+str(i+1)+" has invalid tag(s).\n"
            if self.regionGroupTertiary.get().strip() == "":
                regionFailureReasons += "Tertiary region group has no name.\n"
            if self.regionGroupTertiary.get().strip() != slugify(self.regionGroupTertiary.get().strip()):
                regionFailureReasons += "Tertiary region group has an invalid name.\n"
            regionFailureReasons = regionFailureReasons.strip()
            if regionFailureReasons != "":
                raise Exception("Invalid region group settings.")
            regionSettings = configparser.ConfigParser(allow_no_value=True)
            regionSettings.optionxform = str
            for i in range(self.regionNum):
                regionSettings[str(i+1)] = {}
                regionSettings[str(i+1)]["Region Group"] = self.regionGroupNames[i].get().strip()
                regionSettings[str(i+1)]["Priority Type"] = self.regionPriorityTypes[i].get()
                regionSettings[str(i+1)]["Region/Language Tags"] = self.regionTags[i].get().strip()
            regionSettings["Other"] = {}
            regionSettings["Other"]["Region Group"] = self.regionGroupTertiary.get().strip()
            regionSettings["Other"]["Priority Type"] = "Tertiary"
            with open(regionsFile, 'w') as rf:
                regionSettings.write(rf)
            savedRegionSettings = True
        except:
            savedRegionSettings = False

        if savedDefaultSettings and savedRegionSettings:
            showinfo("EzRO", "Successfully saved all settings.")
        elif savedDefaultSettings and (not savedRegionSettings):
            showerror("EzRO", "An error has occurred: Failed to save region settings.\n\nReasons:\n"+regionFailureReasons)
        elif (not savedDefaultSettings) and savedRegionSettings:
            showerror("EzRO", "An error has occurred: Failed to save default settings.")
        else:
            showerror("EzRO", "An error has occurred: Failed to save default settings and region settings.\n\nReasons:\n"+regionFailureReasons)

    def ssch(self, val): # settings_saveChangesHelper
        if val.get():
            return "True"
        else:
            return "False"

    def changeMainTab(self, event=None):
        if self.Main_Notebook.tab(self.Main_Notebook.select(), "text") == "Config":
            self.loadConfig()



    def createDefaultSettings(self):
        global defaultSettings
        defaultSettings = configparser.ConfigParser(allow_no_value=True)
        defaultSettings.optionxform = str
        defaultSettings["General"] = {}
        defaultSettings["General"]["Input No-Intro DAT Directory"] = ""
        defaultSettings["General"]["Input Romset Directory"] = ""
        defaultSettings["Organization"] = {}
        defaultSettings["Organization"]["Extract Compressed Roms"] = "False"
        defaultSettings["Organization"]["Create Game Folder for Each Game"] = "False"
        defaultSettings["Organization"]["Create Region Folders"] = "False"
        defaultSettings["Organization"]["Do Not Create Folder for Primary Region"] = "True"
        defaultSettings["Organization"]["Create Folders for Special Categories"] = "True"
        defaultSettings["Organization"]["Create Letter Folders"] = "False"
        defaultSettings["Organization"]["Overwrite Duplicate Files"] = "False"
        defaultSettings["Include"] = {}
        for i in range(len(SpecialCategories)):
            if SpecialCategories[i].name in ["Unlicensed", "Unreleased", "Compilations"]:
                defaultSettings["Include"][SpecialCategories[i].name] = "True"
            else:
                defaultSettings["Include"][SpecialCategories[i].name] = "False"
        defaultSettings["Include"]["(1G1R) Games from Other Regions"] = "True"
        with open(defaultSettingsFile, 'w') as dsf:
            defaultSettings.write(dsf)

    def loadConfig(self):
        global defaultSettings, regionSettings
        try:
            defaultSettings = configparser.ConfigParser(allow_no_value=True)
            defaultSettings.optionxform = str
            defaultSettings.read(defaultSettingsFile)
            self.g_datFilePath.set(defaultSettings["General"]["Input No-Intro DAT Directory"])
            self.g_romsetFolderPath.set(defaultSettings["General"]["Input Romset Directory"])
            self.Config_Default_DATDir_PathChooser.configure(textvariable=self.g_datFilePath, type='directory')
            self.Config_Default_RomsetDir_PathChooser.configure(textvariable=self.g_romsetFolderPath, type='directory')
            self.g_extractArchives.set(defaultSettings["Organization"]["Extract Compressed Roms"] == "True")
            self.g_parentFolder.set(defaultSettings["Organization"]["Create Game Folder for Each Game"] == "True")
            self.g_sortByPrimaryRegion.set(defaultSettings["Organization"]["Create Region Folders"] == "True")
            self.g_primaryRegionInRoot.set(defaultSettings["Organization"]["Do Not Create Folder for Primary Region"] == "True")
            self.g_specialCategoryFolder.set(defaultSettings["Organization"]["Create Folders for Special Categories"] == "True")
            self.g_letterFolder.set(defaultSettings["Organization"]["Create Letter Folders"] == "True")
            self.g_overwriteDuplicates.set(defaultSettings["Organization"]["Overwrite Duplicate Files"] == "True")
            for i in range(len(SpecialCategories)):
                try:
                    self.g_includeSpecial[i].set(defaultSettings["Include"][SpecialCategories[i].name] == "True")
                except:
                    self.g_includeSpecial[i].set(False)
            self.g_includeOtherRegions.set(defaultSettings["Include"]["(1G1R) Games from Other Regions"] == "True")
        except:
            showerror("EzRO", "Invalid settings.ini file. Delete it and reload, then a new default file will be created.")
            sys.exit()
        try:
            regionSettings = configparser.ConfigParser(allow_no_value=True)
            regionSettings.optionxform = str
            regionSettings.read(regionsFile)
            while self.regionNum > 0:
                self.removeRegionGroup(0)
            keys = list(regionSettings.keys())[1:]
            for i in range(len(keys)):
                if keys[i].isdigit():
                    self.addRegionGroup(groupName=regionSettings[str(i+1)]["Region Group"], groupType=regionSettings[str(i+1)]["Priority Type"], groupTags=regionSettings[str(i+1)]["Region/Language Tags"])
                elif keys[i] == "Other":
                    self.regionGroupTertiary.set(regionSettings["Other"]["Region Group"])
                    self.Config_Region_Choice_Name_Entry_Tertiary.configure(text=self.regionGroupTertiary)
        except:
            showerror("EzRO", "Invalid regions.ini file. Delete it and reload, then a new default file will be created.")
            sys.exit()

    ########
    # MISC #
    ########

    def menu_viewHelp(self):
        showinfo("Help", "Hover over certain options for further details about them. You can also click the \"?\" button on some pages for more information.")

    def menu_viewAbout(self):
        showinfo("About", "EzRO Rom Organizer v"+str(versionNum)+"\nhttps://github.com/Mode8fx/EzRO-gui\n\nQuestions? Bug reports? Feel free to leave an issue on the project GitHub!")

    def menu_viewExternalLibraries(self):
        showinfo("External Libraries", "ttkScrollableNotebook\nhttps://github.com/muhammeteminturgut/ttkScrollableNotebook\nLicensed under GPL-3.0")

    def menu_getDATFiles(self):
        confirmed = askokcancel("Get No-Intro DAT Files", "This will open the DAT-o-MATIC, where you can download DAT files.\n\nAt the top of the page, select the Type `P/C XML`, then click \"Request\". You should be taken to a Download page, which provides a full set of current DAT files.\n\nFor NES, use the headerless DAT.")
        if confirmed:
            webbrowser.open_new_tab("https://datomatic.no-intro.org/?page=download&op=daily")



def show_error(self, *args):
    err = traceback.format_exception(*args)
    showerror('Exception',err)

tk.Tk.report_callback_exception = show_error

if __name__ == '__main__':
    tk_root = tk.Tk()
    # screenHeight = tk_root.winfo_screenheight()
    # screenHeightMult = screenHeight / 1440.0
    tk_root.geometry('1200x675')
    # tk_root.resizable(False, False)
    tk_root.title("EzRO")
    screenHeightMult = 1
    app = EzroApp(tk_root)
    app.run()

