import pathlib
import pygubu
try:
    import Tkinter as tk
    import Tkinter.ttk as ttk
    from Tkinter.messagebox import showinfo, showerror
except:
    import tkinter as tk
    import tkinter.ttk as ttk
    from tkinter.messagebox import showinfo, showerror
from pygubu.widgets.editabletreeview import EditableTreeview
from pygubu.widgets.pathchooserinput import PathChooserInput
from pygubu.widgets.scrolledframe import ScrolledFrame
import pygubu.widgets.simpletooltip as tooltip

from os import path, mkdir, listdir, remove, walk, rename, rmdir
import re
import xml.etree.ElementTree as ET
import zipfile
import shutil
from pathlib import Path as plpath
from math import ceil
from gatelib import *
from filehash import FileHash
import configparser
from dateutil.parser import parse as dateParse
import binascii

progFolder = getCurrFolder()
sys.path.append(progFolder)
crcHasher = FileHash('crc32')

defaultSettingsFile = path.join(progFolder, "settings.ini")
regionsFile = path.join(progFolder, "regions.ini")
logFolder = path.join(progFolder, "Logs")

systemListStr = " ".join([
    "\"\"",
    "\"Atari 2600\"",
    "\"Game Boy Advance\"",
    "\"Sega Genesis\"",
    "\"Super Nintendo Entertainment System\""
])



PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "EzRO.ui"

class EzroApp:
    def __init__(self, master=None):

        # Menu Bar
        menubar = tk.Menu(root, tearoff=0)
        fileMenu = tk.Menu(menubar, tearoff=0)
        helpMenu = tk.Menu(menubar, tearoff=0)
        helpMenu.add_command(label="View Help...", command=self.menu_viewHelp)
        helpMenu.add_separator()
        helpMenu.add_command(label="About...", command=self.menu_viewAbout)
        menubar.add_cascade(label="Help", menu=helpMenu)
        root.config(menu=menubar)

        # build ui
        self.Main_Notebook = ttk.Notebook(master)
        self.Export_Frame = ttk.Frame(self.Main_Notebook)
        self.Export_System_Combobox = ttk.Combobox(self.Export_Frame)
        self.systemChoice = tk.StringVar(value='')
        self.Export_System_Combobox.configure(state='readonly', textvariable=self.systemChoice, values=systemListStr, width='50')
        self.Export_System_Combobox.place(anchor='center', relx='.425', rely='.075', x='0', y='0')
        self.Export_System_Button = ttk.Button(self.Export_Frame)
        self.Export_System_Button.configure(text='Add System')
        self.Export_System_Button.place(anchor='center', relx='.6', rely='.075', x='0', y='0')
        self.Export_System_Button.configure(command=self.export_addSystem)
        self.Export_Systems = ttk.Notebook(self.Export_Frame)

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
        self.Favorites_Frame = ttk.Frame(self.Main_Notebook)
        self.Favorites_Load = ttk.Button(self.Favorites_Frame)
        self.Favorites_Load.configure(text='Load Existing List...')
        self.Favorites_Load.place(anchor='w', relx='.1', rely='.075', x='0', y='0')
        self.Favorites_Load.configure(command=self.favorites_loadList)
        self.Favorites_System_Label = ttk.Label(self.Favorites_Frame)
        self.Favorites_System_Label.configure(text='System')
        self.Favorites_System_Label.place(anchor='w', relx='.1', rely='.15', x='0', y='0')
        self.Favorites_System_Combobox = ttk.Combobox(self.Favorites_Frame)
        self.favoritesSystemChoice = tk.StringVar(value='')
        self.Favorites_System_Combobox.configure(state='readonly', textvariable=self.favoritesSystemChoice, values=systemListStr, width='50')
        self.Favorites_System_Combobox.place(anchor='w', relx='.15', rely='.15', x='0', y='0')
        self.Favorites_List = EditableTreeview(self.Favorites_Frame)
        self.Favorites_List.place(anchor='nw', relheight='.65', relwidth='.8', relx='.1', rely='.2', x='0', y='0')
        self.Favorites_Add = ttk.Button(self.Favorites_Frame)
        self.Favorites_Add.configure(text='Add Files...')
        self.Favorites_Add.place(anchor='w', relx='.1', rely='.925', x='0', y='0')
        self.Favorites_Add.configure(command=self.favorites_addFiles)
        self.Favorites_Save = ttk.Button(self.Favorites_Frame)
        self.Favorites_Save.configure(text='Save List As...')
        self.Favorites_Save.place(anchor='e', relx='.9', rely='.925', x='0', y='0')
        self.Favorites_Save.configure(command=self.favorites_saveList)
        self.Favorites_Frame.configure(height='200', width='200')
        self.Favorites_Frame.pack(side='top')
        self.Main_Notebook.add(self.Favorites_Frame, text='Favorites')
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
        self.g_datFilePathChoices = tk.StringVar(value='')
        self.Config_Default_DATDir_PathChooser.configure(textvariable=self.g_datFilePathChoices, type='directory')
        self.Config_Default_DATDir_PathChooser.grid(column='0', padx='200', pady='10', row='0', sticky='w')
        self.Config_Default_RomsetDir_Label = ttk.Label(self.Config_Default_Frame)
        self.Config_Default_RomsetDir_Label.configure(text='Input Romset Directory')
        self.Config_Default_RomsetDir_Label.grid(column='0', padx='20', pady='10', row='1', sticky='w')
        self.Config_Default_RomsetDir_PathChooser = PathChooserInput(self.Config_Default_Frame)
        self.g_romsetFolderPath = tk.StringVar(value='')
        self.Config_Default_RomsetDir_PathChooser.configure(textvariable=self.g_romsetFolderPath, type='directory')
        self.Config_Default_RomsetDir_PathChooser.grid(column='0', padx='200', pady='10', row='1', sticky='w')
        self.Config_Default_ExtractArchives = ttk.Checkbutton(self.Config_Default_Frame)
        self.g_extractArchives = tk.IntVar(value='')
        self.Config_Default_ExtractArchives.configure(text='Extract Archives', variable=self.g_extractArchives)
        self.Config_Default_ExtractArchives.grid(column='0', padx='20', pady='10', row='2', sticky='w')
        self.Config_Default_ParentFolder = ttk.Checkbutton(self.Config_Default_Frame)
        self.g_parentFolder = tk.IntVar(value='')
        self.Config_Default_ParentFolder.configure(text='Export Each Game to Parent Folder', variable=self.g_parentFolder)
        self.Config_Default_ParentFolder.grid(column='0', padx='20', pady='10', row='3', sticky='w')
        self.Config_Default_SortByPrimaryRegion = ttk.Checkbutton(self.Config_Default_Frame)
        self.g_sortByPrimaryRegion = tk.IntVar(value='')
        self.Config_Default_SortByPrimaryRegion.configure(text='Sort Games by Primary Region', variable=self.g_sortByPrimaryRegion)
        self.Config_Default_SortByPrimaryRegion.grid(column='0', padx='20', pady='10', row='4', sticky='w')
        self.Config_Default_PrimaryRegionInRoot = ttk.Checkbutton(self.Config_Default_Frame)
        self.g_primaryRegionInRoot = tk.IntVar(value='')
        self.Config_Default_PrimaryRegionInRoot.configure(text='Keep Games from Primary Region in Root', variable=self.g_primaryRegionInRoot)
        self.Config_Default_PrimaryRegionInRoot.grid(column='0', padx='20', pady='10', row='6', sticky='w')
        self.Config_Default_OverwriteDuplicates = ttk.Checkbutton(self.Config_Default_Frame)
        self.g_overwriteDuplicates = tk.IntVar(value='')
        self.Config_Default_OverwriteDuplicates.configure(text='Overwrite Duplicate Files', variable=self.g_overwriteDuplicates)
        self.Config_Default_OverwriteDuplicates.grid(column='0', padx='20', pady='10', row='5', sticky='w')
        self.Config_Default_Include = ttk.Labelframe(self.Config_Default_Frame)
        self.Config_Default_IncludeUnlicensed = ttk.Checkbutton(self.Config_Default_Include)
        self.g_includeUnlicensed = tk.IntVar(value='')
        self.Config_Default_IncludeUnlicensed.configure(text='Unlicensed', variable=self.g_includeUnlicensed)
        self.Config_Default_IncludeUnlicensed.grid(column='0', padx='20', pady='10', row='0', sticky='w')
        self.Config_Default_IncludeCompilations = ttk.Checkbutton(self.Config_Default_Include)
        self.g_includeCompilations = tk.IntVar(value='')
        self.Config_Default_IncludeCompilations.configure(text='Compilations', variable=self.g_includeCompilations)
        self.Config_Default_IncludeCompilations.grid(column='0', padx='150', pady='10', row='0', sticky='w')
        self.Config_Default_IncludeTestPrograms = ttk.Checkbutton(self.Config_Default_Include)
        self.g_includeTestPrograms = tk.IntVar(value='')
        self.Config_Default_IncludeTestPrograms.configure(text='Test Programs', variable=self.g_includeTestPrograms)
        self.Config_Default_IncludeTestPrograms.grid(column='0', padx='20', pady='10', row='1', sticky='w')
        self.Config_Default_IncludeBIOS = ttk.Checkbutton(self.Config_Default_Include)
        self.g_includeBIOS = tk.IntVar(value='')
        self.Config_Default_IncludeBIOS.configure(text='BIOS', variable=self.g_includeBIOS)
        self.Config_Default_IncludeBIOS.grid(column='0', padx='150', pady='10', row='1', sticky='w')
        self.Config_Default_IncludeNESPorts = ttk.Checkbutton(self.Config_Default_Include)
        self.g_includeNESPorts = tk.IntVar(value='')
        self.Config_Default_IncludeNESPorts.configure(text='(GBA) NES Ports', variable=self.g_includeNESPorts)
        self.Config_Default_IncludeNESPorts.grid(column='0', padx='20', pady='10', row='2', sticky='w')
        self.Config_Default_IncludeGBAVideo = ttk.Checkbutton(self.Config_Default_Include)
        self.g_includeGBAVideo = tk.IntVar(value='')
        self.Config_Default_IncludeGBAVideo.configure(text='GBA Video', variable=self.g_includeGBAVideo)
        self.Config_Default_IncludeGBAVideo.grid(column='0', padx='150', pady='10', row='2', sticky='w')
        self.Config_Default_Include.configure(text='Include')
        self.Config_Default_Include.grid(column='0', padx='20', pady='10', row='7', sticky='w')
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
        self.Config_Region_Template_Combobox.place(anchor='e', x='965', y='495')
        self.Config_Region_Template_Apply = ttk.Button(self.Config_Region_Frame.innerframe)
        self.Config_Region_Template_Apply.configure(text='Apply Template')
        self.Config_Region_Template_Apply.place(anchor='e', x='1070', y='495')
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
        self.Main_Notebook.configure(height='675', width='1200')
        self.Main_Notebook.grid(column='0', row='0')
        # Tooltips
        tooltip.create(self.Config_Default_DATDir_Label, 'The directory containing No-Intro DAT files for each system. These contain information about each rom, which is used in both exporting and auditing.\n\nIf this is provided, the \"Export\" tab will attempt to automatically match DAT files from this directory with each system so you don\'t have to input them manually.')
        tooltip.create(self.Config_Default_RomsetDir_Label, 'The directory containing your rom directories for each system.\n\nIf this is provided, the \"Export\" tab will attempt to automatically match folders from this directory with each system so you don\'t have to input them manually.')
        tooltip.create(self.Config_Default_ExtractArchives, 'If enabled, any roms from your input romset that are contained in zipped archives (ZIP, 7z, etc.) will be extracted during export.\n\nUseful if your output device does not support zipped roms.\n\nIf unsure, leave this disabled.')
        tooltip.create(self.Config_Default_ParentFolder, 'If enabled, roms will be exported to a parent folder with the same name as the primary region release of your rom.\n\nFor example, \"Legend of Zelda, The (USA)\" and \"Zelda no Densetsu 1 - The Hyrule Fantasy (Japan)\" will both be exported to a folder titled \"Legend of Zelda, The\".\n\nIf unsure, leave this disabled.')
        tooltip.create(self.Config_Default_SortByPrimaryRegion, 'If enabled, all roms will be exported to a parent folder named after the game\'s highest-priority region.\n\nFor example, Devil World (NES) has Europe and Japan releases, but not USA. If your order of region priority is USA->Europe->Japan, then all versions of Devil World (and its parent folder, if enabled) will be exported to a folder titled \"[Europe]\".\n\nIf unsure, leave this enabled.')
        tooltip.create(self.Config_Default_PrimaryRegionInRoot, '(Only applies if \"Sort Games by Primary Region\" is enabled.)\n\nIf enabled, a region folder will NOT be created for your highest-priority region.\n\nFor example, if your order of region priority is USA->Europe->Japan, then games that have USA releases will not be exported to a [USA] folder (they will instead be placed directly in the output folder), but games that have Europe releases and not USA releases will be exported to a [Europe] folder.\n\nIf unsure, leave this enabled.')
        tooltip.create(self.Config_Default_OverwriteDuplicates, 'If enabled: If a rom in the output directory with the same name as an exported rom already exists, it will be overwritten by the new export.\n\nIf disabled: The export will not overwrite matching roms in the output directory.\n\nIf unsure, leave this disabled.')
        tooltip.create(self.Config_Default_IncludeNESPorts, '(Only applies to GBA.)\n\nInclude Classic NES Series, Famicom Mini, Hudson Best Collection, and Kunio-kun Nekketsu Collection emulated ports.')
        tooltip.create(self.Config_Default_IncludeGBAVideo, '(Only applies to GBA.)')
        # Main widget
        self.mainwindow = self.Main_Notebook
        # Other initialization
        if not path.exists(defaultSettingsFile):
            self.createDefaultSettings()
        if not path.exists(regionsFile):
            self.createRegionSettings()
    
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
        self.Export_1G1RRegion_Label_ = []
        self.Export_1G1RRegion_Combobox_ = []
        self.regionChoices = []
        self.Export_1G1RIncludeOther_ = []
        self.includeOtherRegionsChoices = []
        self.Export_FromList_Label_ = []
        self.Export_FromList_PathChooser_ = []
        self.romListFileChoices = []
        self.Export_IncludeFrame_ = []
        self.Export_IncludeUnlicensed_ = []
        self.includeUnlicensedChoices = []
        self.Export_IncludeCompilations_ = []
        self.includeCompilationsChoices = []
        self.Export_IncludeTestPrograms_ = []
        self.includeTestProgramsChoices = []
        self.Export_IncludeBIOS_ = []
        self.includeBIOSChoices = []
        self.Export_IncludeNES_ = []
        self.includeNESChoices = []
        self.Export_IncludeGBAV_ = []
        self.includeGBAVChoices = []
        self.Export_ExtractArchives_ = []
        self.extractArchivesChoices = []
        self.Export_ParentFolder_ = []
        self.parentFolderChoices = []
        self.Export_SortByPrimaryRegion_ = []
        self.sortByPrimaryRegionChoices = []
        self.Export_PrimaryRegionInRoot_ = []
        self.primaryRegionInRootChoices = []
        self.Export_OverwriteDuplicates_ = []
        self.overwriteDuplicatesChoices = []
        self.Export_DAT_Label_Tooltip_ = []
        self.Export_Romset_Label_Tooltip_ = []
        self.Export_OutputDir_Label_Tooltip_ = []
        self.Export_OutputType_Label_Tooltip_ = []
        self.Export_1G1RRegion_Label_Tooltip_ = []
        self.Export_1G1RIncludeOther_Tooltip_ = []
        self.Export_FromList_Label_Tooltip_ = []
        self.Export_IncludeUnlicensed_Tooltip_ = []
        self.Export_IncludeCompilations_Tooltip_ = []
        self.Export_IncludeTestPrograms_Tooltip_ = []
        self.Export_IncludeBIOS_Tooltip_ = []
        self.Export_IncludeNES_Tooltip_ = []
        self.Export_IncludeGBAV_Tooltip_ = []
        self.Export_ExtractArchives_Tooltip_ = []
        self.Export_ParentFolder_Tooltip_ = []
        self.Export_SortByPrimaryRegion_Tooltip_ = []
        self.Export_PrimaryRegionInRoot_Tooltip_ = []
        self.Export_OverwriteDuplicates_Tooltip_ = []
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
        self.priorityTypes = []
        self.Config_Region_Choice_Tags_Label_ = []
        self.Config_Region_Choice_Tags_Entry_ = []
        self.regionTags = []

    def addSystemTab(self, systemName="New System"):
        self.exportSystemNames.append(None)
        self.Export_ScrolledFrame_.append(None)
        self.Export_DAT_Label_.append(None)
        self.Export_DAT_PathChooser_.append(None)
        self.datFilePathChoices.append(None)
        self.Export_Romset_Label_.append(None)
        self.Export_Romset_PathChooser_.append(None)
        self.romsetFolderPathChoices.append(None)
        self.Export_OutputDir_Label_.append(None)
        self.Export_OutputDir_PathChooser_.append(None)
        self.outputFolderDirectoryChoices.append(None)
        self.Export_Separator_.append(None)
        self.Export_OutputType_Label_.append(None)
        self.Export_OutputType_Combobox_.append(None)
        self.outputTypeChoices.append(None)
        self.Export_1G1RRegion_Label_.append(None)
        self.Export_1G1RRegion_Combobox_.append(None)
        self.regionChoices.append(None)
        self.Export_1G1RIncludeOther_.append(None)
        self.includeOtherRegionsChoices.append(None)
        self.Export_FromList_Label_.append(None)
        self.Export_FromList_PathChooser_.append(None)
        self.romListFileChoices.append(None)
        self.Export_IncludeFrame_.append(None)
        self.Export_IncludeUnlicensed_.append(None)
        self.includeUnlicensedChoices.append(None)
        self.Export_IncludeCompilations_.append(None)
        self.includeCompilationsChoices.append(None)
        self.Export_IncludeTestPrograms_.append(None)
        self.includeTestProgramsChoices.append(None)
        self.Export_IncludeBIOS_.append(None)
        self.includeBIOSChoices.append(None)
        self.Export_IncludeNES_.append(None)
        self.includeNESChoices.append(None)
        self.Export_IncludeGBAV_.append(None)
        self.includeGBAVChoices.append(None)
        self.Export_ExtractArchives_.append(None)
        self.extractArchivesChoices.append(None)
        self.Export_ParentFolder_.append(None)
        self.parentFolderChoices.append(None)
        self.Export_SortByPrimaryRegion_.append(None)
        self.sortByPrimaryRegionChoices.append(None)
        self.Export_PrimaryRegionInRoot_.append(None)
        self.primaryRegionInRootChoices.append(None)
        self.Export_OverwriteDuplicates_.append(None)
        self.overwriteDuplicatesChoices.append(None)
        self.Export_RemoveSystem_.append(None)
        self.exportSystemNames[self.exportTabNum] = systemName
        self.Export_ScrolledFrame_[self.exportTabNum] = ScrolledFrame(self.Export_Systems, scrolltype='both')
        self.Export_DAT_Label_[self.exportTabNum] = ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_DAT_Label_[self.exportTabNum].configure(text='Input No-Intro DAT')
        self.Export_DAT_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='0', sticky='w')
        self.Export_DAT_PathChooser_[self.exportTabNum] = PathChooserInput(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.datFilePathChoices[self.exportTabNum] = tk.StringVar(value='')
        self.Export_DAT_PathChooser_[self.exportTabNum].configure(mustexist='true', state='normal', textvariable=self.datFilePathChoices[self.exportTabNum], type='file')
        self.Export_DAT_PathChooser_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='0', sticky='w')
        self.Export_Romset_Label_[self.exportTabNum] = ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_Romset_Label_[self.exportTabNum].configure(text='Input Romset')
        self.Export_Romset_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='1', sticky='w')
        self.Export_Romset_PathChooser_[self.exportTabNum] = PathChooserInput(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.romsetFolderPathChoices[self.exportTabNum] = tk.StringVar(value='')
        self.Export_Romset_PathChooser_[self.exportTabNum].configure(mustexist='true', state='normal', textvariable=self.romsetFolderPathChoices[self.exportTabNum], type='directory')
        self.Export_Romset_PathChooser_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='1', sticky='w')
        self.Export_OutputDir_Label_[self.exportTabNum] = ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_OutputDir_Label_[self.exportTabNum].configure(text='Output Directory')
        self.Export_OutputDir_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='2', sticky='w')
        self.Export_OutputDir_PathChooser_[self.exportTabNum] = PathChooserInput(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.outputFolderDirectoryChoices[self.exportTabNum] = tk.StringVar(value='')
        self.Export_OutputDir_PathChooser_[self.exportTabNum].configure(mustexist='true', state='normal', textvariable=self.outputFolderDirectoryChoices[self.exportTabNum], type='directory')
        self.Export_OutputDir_PathChooser_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='2', sticky='w')
        self.Export_Separator_[self.exportTabNum] = ttk.Separator(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_Separator_[self.exportTabNum].configure(orient='vertical')
        self.Export_Separator_[self.exportTabNum].place(anchor='center', relheight='.95', relx='.5', rely='.5', x='0', y='0')
        self.Export_OutputType_Label_[self.exportTabNum] = ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_OutputType_Label_[self.exportTabNum].configure(text='Output Type')
        self.Export_OutputType_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='3', sticky='w')
        self.Export_OutputType_Combobox_[self.exportTabNum] = ttk.Combobox(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.outputTypeChoices[self.exportTabNum] = tk.StringVar(value='')
        self.Export_OutputType_Combobox_[self.exportTabNum].configure(state='readonly', textvariable=self.outputTypeChoices[self.exportTabNum], values='"All" "1G1R" "Favorites"', width='10')
        self.Export_OutputType_Combobox_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='3', sticky='w')
        self.Export_OutputType_Combobox_[self.exportTabNum].bind('<<ComboboxSelected>>', self.export_setOutputType, add='')
        self.Export_OutputType_Combobox_[self.exportTabNum].current(0)
        self.Export_1G1RRegion_Label_[self.exportTabNum] = ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_1G1RRegion_Label_[self.exportTabNum].configure(text='Primary Region')
        self.Export_1G1RRegion_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='4', sticky='w')
        self.Export_1G1RRegion_Combobox_[self.exportTabNum] = ttk.Combobox(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.regionChoices[self.exportTabNum] = tk.StringVar(value='')
        self.Export_1G1RRegion_Combobox_[self.exportTabNum].configure(state='readonly', textvariable=self.regionChoices[self.exportTabNum], values='"Placeholder 1" "Placeholder 2"', width='10')
        self.Export_1G1RRegion_Combobox_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='4', sticky='w')
        self.Export_1G1RIncludeOther_[self.exportTabNum] = ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.includeOtherRegionsChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_1G1RIncludeOther_[self.exportTabNum].configure(text='Include Games from Other Regions', variable=self.includeOtherRegionsChoices[self.exportTabNum])
        self.Export_1G1RIncludeOther_[self.exportTabNum].grid(column='0', padx='250', pady='10', row='4', sticky='w')
        self.Export_FromList_Label_[self.exportTabNum] = ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_FromList_Label_[self.exportTabNum].configure(text='Rom List')
        self.Export_FromList_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='5', sticky='w')
        self.Export_FromList_PathChooser_[self.exportTabNum] = PathChooserInput(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.romListFileChoices[self.exportTabNum] = tk.StringVar(value='')
        self.Export_FromList_PathChooser_[self.exportTabNum].configure(mustexist='true', state='normal', textvariable=self.romListFileChoices[self.exportTabNum], type='file')
        self.Export_FromList_PathChooser_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='5', sticky='w')
        self.Export_IncludeFrame_[self.exportTabNum] = ttk.Labelframe(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_IncludeUnlicensed_[self.exportTabNum] = ttk.Checkbutton(self.Export_IncludeFrame_[self.exportTabNum])
        self.includeUnlicensedChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_IncludeUnlicensed_[self.exportTabNum].configure(text='Unlicensed', variable=self.includeUnlicensedChoices[self.exportTabNum])
        self.Export_IncludeUnlicensed_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='0', sticky='w')
        self.Export_IncludeCompilations_[self.exportTabNum] = ttk.Checkbutton(self.Export_IncludeFrame_[self.exportTabNum])
        self.includeCompilationsChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_IncludeCompilations_[self.exportTabNum].configure(text='Compilations', variable=self.includeCompilationsChoices[self.exportTabNum])
        self.Export_IncludeCompilations_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='0', sticky='w')
        self.Export_IncludeTestPrograms_[self.exportTabNum] = ttk.Checkbutton(self.Export_IncludeFrame_[self.exportTabNum])
        self.includeTestProgramsChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_IncludeTestPrograms_[self.exportTabNum].configure(text='Test Programs', variable=self.includeTestProgramsChoices[self.exportTabNum])
        self.Export_IncludeTestPrograms_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='1', sticky='w')
        self.Export_IncludeBIOS_[self.exportTabNum] = ttk.Checkbutton(self.Export_IncludeFrame_[self.exportTabNum])
        self.includeBIOSChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_IncludeBIOS_[self.exportTabNum].configure(text='BIOS', variable=self.includeBIOSChoices[self.exportTabNum])
        self.Export_IncludeBIOS_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='1', sticky='w')
        self.Export_IncludeNES_[self.exportTabNum] = ttk.Checkbutton(self.Export_IncludeFrame_[self.exportTabNum])
        self.includeNESChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_IncludeNES_[self.exportTabNum].configure(text='NES Ports', variable=self.includeNESChoices[self.exportTabNum])
        self.Export_IncludeNES_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='2', sticky='w')
        self.Export_IncludeGBAV_[self.exportTabNum] = ttk.Checkbutton(self.Export_IncludeFrame_[self.exportTabNum])
        self.includeGBAVChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_IncludeGBAV_[self.exportTabNum].configure(text='GBA Video', variable=self.includeGBAVChoices[self.exportTabNum])
        self.Export_IncludeGBAV_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='2', sticky='w')
        self.Export_IncludeFrame_[self.exportTabNum].configure(text='Include')
        self.Export_IncludeFrame_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='6', sticky='w')
        self.Export_ExtractArchives_[self.exportTabNum] = ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.extractArchivesChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_ExtractArchives_[self.exportTabNum].configure(text='Extract Archives', variable=self.extractArchivesChoices[self.exportTabNum])
        self.Export_ExtractArchives_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.03', x='0', y='0')
        self.Export_ParentFolder_[self.exportTabNum] = ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.parentFolderChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_ParentFolder_[self.exportTabNum].configure(text='Export Each Game to Parent Folder', variable=self.parentFolderChoices[self.exportTabNum])
        self.Export_ParentFolder_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.132', x='0', y='0')
        self.Export_ParentFolder_[self.exportTabNum].configure(command=self.export_toggleSortGames)
        self.Export_SortByPrimaryRegion_[self.exportTabNum] = ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.sortByPrimaryRegionChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_SortByPrimaryRegion_[self.exportTabNum].configure(text='Sort Games by Primary Region', variable=self.sortByPrimaryRegionChoices[self.exportTabNum])
        self.Export_SortByPrimaryRegion_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.234', x='0', y='0')
        self.Export_PrimaryRegionInRoot_[self.exportTabNum] = ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.primaryRegionInRootChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_PrimaryRegionInRoot_[self.exportTabNum].configure(text='Keep Games from Primary Region in Root', variable=self.primaryRegionInRootChoices[self.exportTabNum])
        self.Export_PrimaryRegionInRoot_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.336', x='0', y='0')
        self.Export_OverwriteDuplicates_[self.exportTabNum] = ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.overwriteDuplicatesChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_OverwriteDuplicates_[self.exportTabNum].configure(text='Overwrite Duplicate Files', variable=self.overwriteDuplicatesChoices[self.exportTabNum])
        self.Export_OverwriteDuplicates_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.438', x='0', y='0')
        self.Export_RemoveSystem_[self.exportTabNum] = ttk.Button(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_RemoveSystem_[self.exportTabNum].configure(text='Remove System')
        self.Export_RemoveSystem_[self.exportTabNum].place(anchor='se', relx='1', rely='1', x='-10', y='-10')
        self.Export_RemoveSystem_[self.exportTabNum].configure(command=self.export_removeSystem)
        self.Export_ScrolledFrame_[self.exportTabNum].innerframe.configure(relief='groove')
        self.Export_ScrolledFrame_[self.exportTabNum].configure(usemousewheel=True)
        self.Export_ScrolledFrame_[self.exportTabNum].place(anchor='nw', relheight='.9', relwidth='.9', relx='.05', rely='.05', x='0', y='0')
        self.Export_Systems.add(self.Export_ScrolledFrame_[self.exportTabNum], text=systemName)
        tooltip.create(self.Export_DAT_Label_[self.exportTabNum], 'The No-Intro DAT file for the current system. This contains information about each rom, which is used in both exporting and auditing.\n\nNot needed for the \"Favorites\" output type.')
        tooltip.create(self.Export_Romset_Label_[self.exportTabNum], 'The directory containing your roms for the current system.')
        tooltip.create(self.Export_OutputDir_Label_[self.exportTabNum], 'The directory that your roms will be exported to. Ideally, this should be named after the current system.')
        tooltip.create(self.Export_OutputType_Label_[self.exportTabNum], '\"All\": All roms will be exported.\n\n\"1G1R\" (1 Game 1 Rom): Only the latest revision of a single region of your choice of each game will be exported (e.g. USA Revision 2).\n\n\"Favorites\": Only specific roms from a provided text file will be exported; good for exporting a list of only your favorite roms.')
        tooltip.create(self.Export_1G1RRegion_Label_[self.exportTabNum], 'The region used for the 1G1R export.')
        tooltip.create(self.Export_1G1RIncludeOther_[self.exportTabNum], 'If enabled: In the event that a game does not contain a rom from your region (e.g. your primary region is USA but the game is a Japan-only release), a secondary region will be used according to your Region/Language Priority Order.\n\nIf disabled: In the event that a game does not contain a rom from your region, the game is skipped entirely.\n\nIf you only want to export roms from your own region, disable this.')
        tooltip.create(self.Export_FromList_Label_[self.exportTabNum], 'The text list containing your favorite roms for the current system.')
        tooltip.create(self.Export_IncludeNES_[self.exportTabNum], 'Include Classic NES Series, Famicom Mini, Hudson Best Collection, and Kunio-kun Nekketsu Collection emulated ports.\n\nIf unsure, leave this disabled.')
        tooltip.create(self.Export_ExtractArchives_[self.exportTabNum], 'If enabled, any roms from your input romset that are contained in zipped archives (ZIP, 7z, etc.) will be extracted during export.\n\nUseful if your output device does not support zipped roms.\n\nIf unsure, leave this disabled.')
        tooltip.create(self.Export_ParentFolder_[self.exportTabNum], 'If enabled, roms will be exported to a parent folder with the same name as the primary region release of your rom.\n\nFor example, \"Legend of Zelda, The (USA)\" and \"Zelda no Densetsu 1 - The Hyrule Fantasy (Japan)\" will both be exported to a folder titled \"Legend of Zelda, The\".\n\nIf unsure, leave this disabled.')
        tooltip.create(self.Export_SortByPrimaryRegion_[self.exportTabNum], 'If enabled, all roms will be exported to a parent folder named after the game\'s highest-priority region.\n\nFor example, Devil World (NES) has Europe and Japan releases, but not USA. If your order of region priority is USA->Europe->Japan, then all versions of Devil World (and its parent folder, if enabled) will be exported to a folder titled \"[Europe]\".\n\nIf unsure, leave this enabled.')
        tooltip.create(self.Export_PrimaryRegionInRoot_[self.exportTabNum], '(Only applies if \"Sort Games by Primary Region\" is enabled.)\n\nIf enabled, a region folder will NOT be created for your highest-priority region.\n\nFor example, if your order of region priority is USA->Europe->Japan, then games that have USA releases will not be exported to a [USA] folder (they will instead be placed directly in the output folder), but games that have Europe releases and not USA releases will be exported to a [Europe] folder.\n\nIf unsure, leave this enabled.')
        tooltip.create(self.Export_OverwriteDuplicates_[self.exportTabNum], 'If enabled: If a rom in the output directory with the same name as an exported rom already exists, it will be overwritten by the new export.\n\nIf disabled: The export will not overwrite matching roms in the output directory.\n\nIf unsure, leave this disabled.')
        self.export_setOutputType()
        if systemName != "Game Boy Advance":
            self.Export_IncludeNES_[self.exportTabNum].grid_remove()
            self.Export_IncludeGBAV_[self.exportTabNum].grid_remove()

        self.Export_Systems.select(self.exportTabNum)
        self.exportTabNum += 1

    def export_addSystem(self):
        currSystemChoice = self.systemChoice.get()
        if (currSystemChoice != ""):
            for es in self.Export_Systems.tabs(): # TODO: this doesn't work as it should
                if self.Export_Systems.tab(es, "text") == currSystemChoice:
                    return
            self.addSystemTab(currSystemChoice)
        pass

    def export_setOutputType(self, event=None):
        currIndex = self.Export_Systems.index(self.Export_Systems.select())
        currOutputType = self.outputTypeChoices[currIndex].get()
        if currOutputType == "1G1R":
            self.Export_1G1RRegion_Label_[currIndex].grid(column='0', padx='20', pady='10', row='4', sticky='w')
            self.Export_1G1RRegion_Combobox_[currIndex].grid(column='0', padx='150', pady='10', row='4', sticky='w')
            self.Export_1G1RIncludeOther_[currIndex].grid(column='0', padx='250', pady='10', row='4', sticky='w')
        else:
            self.Export_1G1RRegion_Label_[currIndex].grid_remove()
            self.Export_1G1RRegion_Combobox_[currIndex].grid_remove()
            self.Export_1G1RIncludeOther_[currIndex].grid_remove()
        if currOutputType == "Favorites":
            self.Export_FromList_Label_[currIndex].grid(column='0', padx='20', pady='10', row='5', sticky='w')
            self.Export_FromList_PathChooser_[currIndex].grid(column='0', padx='150', pady='10', row='5', sticky='w')
        else:
            self.Export_FromList_Label_[currIndex].grid_remove()
            self.Export_FromList_PathChooser_[currIndex].grid_remove()

    def export_toggleSortGames(self):
        pass

    def export_removeSystem(self):
        pass

    def export_auditSystem(self):
        # currSystemPath = self.romsetFolderPathChoices[self.Export_Systems.index(self.Export_Systems.select())]
        currSystemIndex = self.Export_Systems.index(self.Export_Systems.select())
        self.updateAndAuditVerifiedRomsets([currSystemIndex])

    def export_auditAllSystems(self):
        allSystemIndices = list([range(self.exportTabNum)])
        self.updateAndAuditVerifiedRomsets(allSystemIndices)

    def export_exportSystem(self):
        pass

    def export_exportAllSystems(self):
        pass

    def export_auditHelp(self):
        showinfo("Audit Help",
            "\"Auditing\" a system directory updates the file names of misnamed roms (and the ZIP files containing them, if applicable) to match the rom's entry in the system's No-Intro DAT. This is determined by the rom's matching checksum in the DAT, so the original name doesn't matter."
            +"\n\nThis also creates a log file indicating which roms exist in the romset, which roms are missing, and which roms are in the set that don't match anything from the DAT."
            +"\n\nIt is highly recommended that you audit a system directory whenever you update that system's No-Intro DAT.")

    ##################
    # EXPORT (Logic) #
    ##################

    def updateAndAuditVerifiedRomsets(self, systemIndices):
        global allGameNamesInDAT, romsWithoutCRCMatch, progressBar, recentlyVerified

        for currIndex in systemIndices:
            currSystemFolder = self.romsetFolderPathChoices[currIndex].get()
            currSystemName = self.exportSystemNames[currIndex]
            if not path.isdir(currSystemFolder):
                continue
            # TODO: print("\n====================\n\n"+currSystemName+"\n")
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
            if currSystemName == "Nintendo Entertainment System":
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
                    if path.basename(root) != "[Unverified]":
                        numFiles += 1
            # TODO: create progress bar here; length = numFiles
            for root, dirs, files in walk(currSystemFolder):
                for file in files:
                    if path.basename(root) != "[Unverified]":
                        # TODO: increment progress bar by 1 here
                        foundMatch = self.renamingProcess(root, file, isNoIntro, headerLength, crcToGameName, allGameNames)
            # TODO: close progress bar here
            xmlRomsInSet = [key for key in allGameNamesInDAT.keys() if allGameNamesInDAT[key] == True]
            xmlRomsNotInSet = [key for key in allGameNamesInDAT.keys() if allGameNamesInDAT[key] == False]
            self.createSystemAuditLog(xmlRomsInSet, xmlRomsNotInSet, romsWithoutCRCMatch, currSystemName)
            numNoCRC = len(romsWithoutCRCMatch)
            if numNoCRC > 0:
                #TODO: print("\nWarning: "+str(numNoCRC)+pluralize(" file", numNoCRC)+" in this system folder "+pluralize("do", numNoCRC, "es", "")+" not have a matching database entry.")
                #TODO: print("If this system folder is in your main verified rom directory, you should move "+pluralize("", numNoCRC, "this file", "these files")+" to your secondary folder; otherwise, "+pluralize("", numNoCRC, "it", "they")+" may be ignored when exporting this system's romset to another device.")
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
                pass

        self.recentlyVerified = True
        showinfo("Audit", "Audit complete.")



    def getCRC(self, filePath, headerLength=0):
        if zipfile.is_zipfile(filePath):
            with zipfile.ZipFile(filePath, 'r', zipfile.ZIP_DEFLATED) as zippedFile:
                if len(zippedFile.namelist()) > 1:
                    return False
                if headerLength == 0:
                    fileInfo = zippedFile.infolist()[0]
                    fileCRC = format(fileInfo.CRC & 0xFFFFFFFF, '08x')
                    return fileCRC.zfill(8).upper()
                else:
                    fileBytes = zippedFile.read(zippedFile.namelist()[0])
                    headerlessCRC = str(hex(binascii.crc32(fileBytes[headerLength:])))[2:]
                    return headerlessCRC.zfill(8).upper()
        else:
            if headerLength == 0:
                fileCRC = crcHasher.hash_file(filePath)
                return fileCRC.zfill(8).upper()
            with open(filePath, "rb") as unheaderedFile:
                fileBytes = unheaderedFile.read()
                headerlessCRC = str(hex(binascii.crc32(fileBytes[headerLength:])))[2:]
                return headerlessCRC.zfill(8).upper()



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
                # TODO: progressBar.write(file+" archive contains more than one file. Skipping.")
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
                            duplicateName = path.join(root, dnStart+str(i)+")")
                            if not path.exists(duplicateName):
                                break
                            i += 1
                        self.renameGame(currFilePath, duplicateName, currFileExt)
                        # TODO: progressBar.write("Duplicate found and renamed: "+duplicateName)
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
        if zipfile.is_zipfile(filePath):
            self.renameArchiveAndContent(filePath, newName)
        else:
            rename(filePath, path.join(path.dirname(filePath), newName+fileExt))
            # TODO: progressBar.write("Renamed "+path.splitext(path.basename(filePath))[0]+" to "+newName)



    def createSystemAuditLog(self, xmlRomsInSet, xmlRomsNotInSet, romsWithoutCRCMatch, currSystemName):
        xmlRomsInSet.sort()
        xmlRomsNotInSet.sort()
        romsWithoutCRCMatch.sort()

        numOverlap = len(xmlRomsInSet)
        numNotInSet = len(xmlRomsNotInSet)
        numNoCRC = len(romsWithoutCRCMatch)
        createDir(logFolder)
        auditLogFile = open(path.join(logFolder, "Audit ("+currSystemName+") ["+str(numOverlap)+" out of "+str(numOverlap+numNotInSet)+"] ["+str(numNoCRC)+" unverified].txt"), "w", encoding="utf-8", errors="replace")
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



    def renameArchiveAndContent(self, archivePath, newName):
        with zipfile.ZipFile(archivePath, 'r', zipfile.ZIP_DEFLATED) as zippedFile:
            zippedFiles = zippedFile.namelist()
            if len(zippedFiles) > 1:
                # TODO: progressBar.write("This archive contains more than one file. Skipping.")
                return
            fileExt = path.splitext(zippedFiles[0])[1]
            archiveExt = path.splitext(archivePath)[1]
            zippedFile.extract(zippedFiles[0], path.dirname(archivePath))
            currExtractedFilePath = path.join(path.dirname(archivePath), zippedFiles[0])
            newArchivePath = path.join(path.dirname(archivePath), newName+archiveExt)
            newExtractedFilePath = path.splitext(newArchivePath)[0]+fileExt
            rename(currExtractedFilePath, newExtractedFilePath)
        remove(archivePath)
        with zipfile.ZipFile(newArchivePath, 'w', zipfile.ZIP_DEFLATED) as newZip:
            newZip.write(newExtractedFilePath, arcname='\\'+newName+fileExt)
        remove(newExtractedFilePath)
        # TODO: progressBar.write("Renamed "+path.splitext(path.basename(archivePath))[0]+" to "+newName)

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
        self.priorityTypes.append(None)
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
        self.priorityTypes[self.regionNum] = tk.StringVar(value=groupType)
        self.Config_Region_Choice_Type_Combobox_[self.regionNum].configure(state='readonly', textvariable=self.priorityTypes[self.regionNum], values='"Primary" "Secondary"', width='12')
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
        pass

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
            self.priorityTypes.insert(num-1, self.priorityTypes.pop(num))
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
        self.priorityTypes.pop(num)
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
        showInfo("Region Help", "Region settings are used in organizing roms from different regions and, in the case of 1G1R exports, determining which region of a game should be exported."
            +"\n\nHover over each setting to learn more; or you can simply use one of the pre-made templates. I recommend \"English + Secondary\" (it's the default), but use whatever you want."
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
        defaultSettings = configparser.ConfigParser(allow_no_value=True)
        defaultSettings.optionxform = str
        defaultSettings.read(defaultSettingsFile)
        defaultSettings["General"] = {}
        defaultSettings["General"]["Input No-Intro DAT Directory"] = self.g_datFilePathChoices.get()
        defaultSettings["General"]["Input Romset Directory"] = self.g_romsetFolderPath.get()
        defaultSettings["Organization"] = {}
        defaultSettings["Organization"]["Extract Archives"] = self.ssch(self.g_extractArchives)
        defaultSettings["Organization"]["Export Each Game to Parent Folder"] = self.ssch(self.g_parentFolder)
        defaultSettings["Organization"]["Sort Games by Primary Region"] = self.ssch(self.g_sortByPrimaryRegion)
        defaultSettings["Organization"]["Keep Games from Primary Region in Root"] = self.ssch(self.g_primaryRegionInRoot)
        defaultSettings["Organization"]["Overwrite Duplicate Files"] = self.ssch(self.g_overwriteDuplicates)
        defaultSettings["Include"] = {}
        defaultSettings["Include"]["Unlicensed"] = self.ssch(self.g_includeUnlicensed)
        defaultSettings["Include"]["Compilations"] = self.ssch(self.g_includeCompilations)
        defaultSettings["Include"]["Test Programs"] = self.ssch(self.g_includeTestPrograms)
        defaultSettings["Include"]["BIOS"] = self.ssch(self.g_includeBIOS)
        defaultSettings["Include"]["(GBA) NES Ports"] = self.ssch(self.g_includeNESPorts)
        defaultSettings["Include"]["(GBA) GBA Video"] = self.ssch(self.g_includeGBAVideo)
        with open(defaultSettingsFile, 'w') as mcf:
            defaultSettings.write(mcf)
        regionSettings = configparser.ConfigParser(allow_no_value=True)
        regionSettings.optionxform = str
        for i in range(self.regionNum):
            regionSettings[str(i+1)] = {}
            regionSettings[str(i+1)]["Region Group"] = self.regionGroupNames[i].get()
            regionSettings[str(i+1)]["Priority Type"] = self.priorityTypes[i].get()
            regionSettings[str(i+1)]["Region/Language Tags"] = self.regionTags[i].get()
        regionSettings["Other"] = {}
        regionSettings["Other"]["Region Group"] = self.regionGroupTertiary.get()
        regionSettings["Other"]["Priority Type"] = "Tertiary"
        with open(regionsFile, 'w') as rf:
            regionSettings.write(rf)

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
        defaultSettings["Organization"]["Extract Archives"] = "False"
        defaultSettings["Organization"]["Export Each Game to Parent Folder"] = "False"
        defaultSettings["Organization"]["Sort Games by Primary Region"] = "False"
        defaultSettings["Organization"]["Keep Games from Primary Region in Root"] = "True"
        defaultSettings["Organization"]["Overwrite Duplicate Files"] = "False"
        defaultSettings["Include"] = {}
        defaultSettings["Include"]["Unlicensed"] = "True"
        defaultSettings["Include"]["Compilations"] = "True"
        defaultSettings["Include"]["Test Programs"] = "False"
        defaultSettings["Include"]["BIOS"] = "False"
        defaultSettings["Include"]["(GBA) NES Ports"] = "False"
        defaultSettings["Include"]["(GBA) GBA Video"] = "False"
        # Keywords
        defaultSettings["Keywords"] = {}
        defaultSettings["Keywords"]["Compilation"] = "|".join([
            "2 Games in 1 -", "2 Games in 1! -", "2 Disney Games -", "2-in-1 Fun Pack -",
            "2 Great Games! -", "2 in 1 -", "2 in 1 Game Pack -", "2 Jeux en 1 -",
            "3 Games in 1 -", "4 Games on One Game Pak", "Castlevania Double Pack",
            "Combo Pack - ", "Crash Superpack -", "Crash & Spyro Superpack",
            "Crash & Spyro Super Pack", "Double Game! -", "Double Pack -", "Spyro Superpack -"
            ])
        defaultSettings["Keywords"]["Specific Attributes"] = "|".join([
            "Virtual Console", "Switch Online", "GameCube", "Namcot Collection",
            "Namco Museum Archives", "Kiosk", "iQue", "Sega Channel", "WiiWare",
            "DLC", "Minis", "Promo", "Nintendo Channel", "Nintendo Channel, Alt",
            "DS Broadcast", "Wii Broadcast", "DS Download Station", "Dwnld Sttn",
            "Undumped Japanese Download Station", "WiiWare Broadcast",
            "Disk Writer", "Collection of Mana", "Namco Museum Archives Vol 1",
            "Namco Museum Archives Vol 2", "Castlevania Anniversary Collection",
            "Nintendo Switch", "NP", "Genesis Mini", "Mega Drive Mini"
            ])
        defaultSettings["Keywords"]["General Attributes"] = "|".join([
            "Rev", "Beta", "Demo", "Sample", "Proto", "Alt", "Earlier",
            "Download Station", "FW", "Reprint"
            ])
        with open(defaultSettingsFile, 'w') as dsf:
            defaultSettings.write(dsf)

    def loadConfig(self):
        global defaultSettings, regionSettings
        defaultSettings = configparser.ConfigParser(allow_no_value=True)
        defaultSettings.optionxform = str
        defaultSettings.read(defaultSettingsFile)
        self.g_datFilePathChoices.set(defaultSettings["General"]["Input No-Intro DAT Directory"])
        self.g_romsetFolderPath.set(defaultSettings["General"]["Input Romset Directory"])
        self.Config_Default_DATDir_PathChooser.configure(textvariable=self.g_datFilePathChoices, type='directory')
        self.Config_Default_RomsetDir_PathChooser.configure(textvariable=self.g_romsetFolderPath, type='directory')
        self.g_extractArchives.set(defaultSettings["Organization"]["Extract Archives"] == "True")
        self.g_parentFolder.set(defaultSettings["Organization"]["Export Each Game to Parent Folder"] == "True")
        self.g_sortByPrimaryRegion.set(defaultSettings["Organization"]["Sort Games by Primary Region"] == "True")
        self.g_primaryRegionInRoot.set(defaultSettings["Organization"]["Keep Games from Primary Region in Root"] == "True")
        self.g_overwriteDuplicates.set(defaultSettings["Organization"]["Overwrite Duplicate Files"] == "True")
        self.g_includeUnlicensed.set(defaultSettings["Include"]["Unlicensed"] == "True")
        self.g_includeCompilations.set(defaultSettings["Include"]["Compilations"] == "True")
        self.g_includeTestPrograms.set(defaultSettings["Include"]["Test Programs"] == "True")
        self.g_includeBIOS.set(defaultSettings["Include"]["BIOS"] == "True")
        self.g_includeNESPorts.set(defaultSettings["Include"]["(GBA) NES Ports"] == "True")
        self.g_includeGBAVideo.set(defaultSettings["Include"]["(GBA) GBA Video"] == "True")
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

    ########
    # MISC #
    ########

    def menu_viewHelp(self):
        showinfo("Help", "Hover over certain options for further details about them. You can also click the \"?\" button on some pages for more information.")

    def menu_viewAbout(self):
        showinfo("About", "EzRO Rom Organizer v1.00\n\nhttps://github.com/Mips96/EzRO-gui")

if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(False, False)
    root.title("EzRO")
    app = EzroApp(root)
    app.run()

