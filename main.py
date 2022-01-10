import pathlib
import pygubu
import tkinter as tk
import tkinter.ttk as ttk
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
from tqdm import tqdm
import binascii

progFolder = getCurrFolder()
sys.path.append(progFolder)
crcHasher = FileHash('crc32')

defaultSettingsFile = path.join(progFolder, "settings.ini")

systemListStr = " ".join([
    "\"\"",
    "\"Game Boy Advance\"",
    "\"Sega Genesis\"",
    "\"Super Nintendo Entertainment System\""
])



PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "EzRO.ui"

class EzroApp:
    def __init__(self, master=None):
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

        self.initExportVars()

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
        self.Config_Region_Choice_RemoveButton_ = ttk.Button(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_RemoveButton_.configure(text='X', width='2')
        self.Config_Region_Choice_RemoveButton_.grid(column='0', padx='20', pady='10', row='0', sticky='w')
        self.Config_Region_Choice_Name_Label_ = ttk.Label(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Name_Label_.configure(text='Region Group')
        self.Config_Region_Choice_Name_Label_.grid(column='0', padx='70', pady='10', row='0', sticky='w')
        self.Config_Region_Choice_Name_Entry_ = ttk.Entry(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Name_Entry_.grid(column='0', padx='200', pady='10', row='0', sticky='w')
        self.Config_Region_Choice_Type_Label_ = ttk.Label(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Type_Label_.configure(text='Priority Type')
        self.Config_Region_Choice_Type_Label_.grid(column='0', padx='370', pady='10', row='0', sticky='w')
        self.Config_Region_Choice_Type_Combobox_ = ttk.Combobox(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Type_Combobox_.configure(state='readonly', values='"Primary" "Secondary"', width='12')
        self.Config_Region_Choice_Type_Combobox_.grid(column='0', padx='445', pady='10', row='0', sticky='w')
        self.Config_Region_Choice_Type_Combobox_.bind('<<ComboboxSelected>>', self.settings_region_setPriorityType, add='')
        self.Config_Region_Choice_Level_Label_ = ttk.Label(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Level_Label_.configure(text='Priority Level')
        self.Config_Region_Choice_Level_Label_.grid(column='0', padx='570', pady='10', row='0', sticky='w')
        self.Config_Region_Choice_Level_Combobox_ = ttk.Combobox(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Level_Combobox_.configure(state='readonly', values='"1 (low)" 2 3 4 5 6 7 8 9 "10 (high)"', width='9')
        self.Config_Region_Choice_Level_Combobox_.grid(column='0', padx='650', pady='10', row='0', sticky='w')
        self.Config_Region_Choice_Tags_Label_ = ttk.Label(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Tags_Label_.configure(text='Region/Language Tags')
        self.Config_Region_Choice_Tags_Label_.grid(column='0', padx='70', pady='10', row='1', sticky='w')
        self.Config_Region_Choice_Tags_Entry_ = ttk.Entry(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Tags_Entry_.configure(width='45')
        self.Config_Region_Choice_Tags_Entry_.grid(column='0', padx='200', pady='10', row='1', sticky='w')
        self.Config_Region_Choice_RemoveButton_Tertiary = ttk.Button(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_RemoveButton_Tertiary.configure(state='disabled', text='X', width='2')
        self.Config_Region_Choice_RemoveButton_Tertiary.grid(column='0', padx='20', pady='10', row='98', sticky='w')
        self.Config_Region_Choice_Name_Label_Tertiary = ttk.Label(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Name_Label_Tertiary.configure(text='Region Group')
        self.Config_Region_Choice_Name_Label_Tertiary.grid(column='0', padx='70', pady='10', row='98', sticky='w')
        self.Config_Region_Choice_Name_Entry_Tertiary = ttk.Entry(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Name_Entry_Tertiary.grid(column='0', padx='200', pady='10', row='98', sticky='w')
        self.Config_Region_Choice_Type_Label_Tertiary = ttk.Label(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Type_Label_Tertiary.configure(text='Priority Type')
        self.Config_Region_Choice_Type_Label_Tertiary.grid(column='0', padx='370', pady='10', row='98', sticky='w')
        self.Config_Region_Choice_Type_Combobox_Tertiary = ttk.Combobox(self.Config_Region_Frame.innerframe)
        self.Config_Region_Choice_Type_Combobox_Tertiary.configure(state='disabled', values='"Tertiary"', width='12')
        self.Config_Region_Choice_Type_Combobox_Tertiary.grid(column='0', padx='445', pady='10', row='98', sticky='w')
        self.Config_Region_AddNewRegionCategory = ttk.Button(self.Config_Region_Frame.innerframe)
        self.Config_Region_AddNewRegionCategory.configure(text='+ Add New Region Category')
        self.Config_Region_AddNewRegionCategory.grid(column='0', padx='20', pady='10', row='99', sticky='w')
        self.Config_Region_AddNewRegionCategory.configure(command=self.settings_region_addNewRegionCategory)
        self.Config_Region_Help = ttk.Button(self.Config_Region_Frame.innerframe)
        self.Config_Region_Help.configure(text='?', width='2')
        self.Config_Region_Help.grid(column='0', padx='200', pady='10', row='99', sticky='w')
        self.Config_Region_Help.configure(command=self.settings_region_help)
        self.Config_Region_Frame.configure(usemousewheel=False)
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
    
    def run(self):
        self.mainwindow.mainloop()

    def initExportVars(self):
        self.exportTabNum = 0
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

    def addSystemTab(self, systemName="New System"):
        self.Export_ScrolledFrame_.append(None)
        self.Export_ScrolledFrame_[self.exportTabNum] = ScrolledFrame(self.Export_Systems, scrolltype='both')
        self.Export_DAT_Label_.append(None)
        self.Export_DAT_Label_[self.exportTabNum] = ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_DAT_Label_[self.exportTabNum].configure(text='Input No-Intro DAT')
        self.Export_DAT_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='0', sticky='w')
        tooltip.create(self.Export_DAT_Label_[self.exportTabNum], 'The No-Intro DAT file for the current system. This contains information about each rom, which is used in both exporting and auditing.\n\nNot needed for the \"Favorites\" output type.')
        self.Export_DAT_PathChooser_.append(None)
        self.Export_DAT_PathChooser_[self.exportTabNum] = PathChooserInput(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.datFilePathChoices.append(None)
        self.datFilePathChoices[self.exportTabNum] = tk.StringVar(value='')
        self.Export_DAT_PathChooser_[self.exportTabNum].configure(mustexist='true', state='normal', textvariable=self.datFilePathChoices[self.exportTabNum], type='file')
        self.Export_DAT_PathChooser_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='0', sticky='w')
        self.Export_Romset_Label_.append(None)
        self.Export_Romset_Label_[self.exportTabNum] = ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_Romset_Label_[self.exportTabNum].configure(text='Input Romset')
        self.Export_Romset_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='1', sticky='w')
        tooltip.create(self.Export_Romset_Label_[self.exportTabNum], 'The directory containing your roms for the current system.')
        self.Export_Romset_PathChooser_.append(None)
        self.Export_Romset_PathChooser_[self.exportTabNum] = PathChooserInput(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.romsetFolderPathChoices.append(None)
        self.romsetFolderPathChoices[self.exportTabNum] = tk.StringVar(value='')
        self.Export_Romset_PathChooser_[self.exportTabNum].configure(mustexist='true', state='normal', textvariable=self.romsetFolderPathChoices[self.exportTabNum], type='directory')
        self.Export_Romset_PathChooser_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='1', sticky='w')
        self.Export_OutputDir_Label_.append(None)
        self.Export_OutputDir_Label_[self.exportTabNum] = ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_OutputDir_Label_[self.exportTabNum].configure(text='Output Directory')
        self.Export_OutputDir_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='2', sticky='w')
        tooltip.create(self.Export_OutputDir_Label_[self.exportTabNum], 'The directory that your roms will be exported to. Ideally, this should be named after the current system.')
        self.Export_OutputDir_PathChooser_.append(None)
        self.Export_OutputDir_PathChooser_[self.exportTabNum] = PathChooserInput(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.outputFolderDirectoryChoices.append(None)
        self.outputFolderDirectoryChoices[self.exportTabNum] = tk.StringVar(value='')
        self.Export_OutputDir_PathChooser_[self.exportTabNum].configure(mustexist='true', state='normal', textvariable=self.outputFolderDirectoryChoices[self.exportTabNum], type='directory')
        self.Export_OutputDir_PathChooser_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='2', sticky='w')
        self.Export_Separator_.append(None)
        self.Export_Separator_[self.exportTabNum] = ttk.Separator(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_Separator_[self.exportTabNum].configure(orient='vertical')
        self.Export_Separator_[self.exportTabNum].place(anchor='center', relheight='.95', relx='.5', rely='.5', x='0', y='0')
        self.Export_OutputType_Label_.append(None)
        self.Export_OutputType_Label_[self.exportTabNum] = ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_OutputType_Label_[self.exportTabNum].configure(text='Output Type')
        self.Export_OutputType_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='3', sticky='w')
        tooltip.create(self.Export_OutputType_Label_[self.exportTabNum], '\"All\": All roms will be exported.\n\n\"1G1R\" (1 Game 1 Rom): Only the latest revision of a single region of your choice of each game will be exported (e.g. USA Revision 2).\n\n\"Favorites\": Only specific roms from a provided text file will be exported; good for exporting a list of only your favorite roms.')
        self.Export_OutputType_Combobox_.append(None)
        self.Export_OutputType_Combobox_[self.exportTabNum] = ttk.Combobox(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.outputTypeChoices.append(None)
        self.outputTypeChoices[self.exportTabNum] = tk.StringVar(value='')
        self.Export_OutputType_Combobox_[self.exportTabNum].configure(state='readonly', textvariable=self.outputTypeChoices[self.exportTabNum], values='"All" "1G1R" "Favorites"', width='10')
        self.Export_OutputType_Combobox_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='3', sticky='w')
        self.Export_OutputType_Combobox_[self.exportTabNum].bind('<<ComboboxSelected>>', self.export_setOutputType, add='')
        self.Export_OutputType_Combobox_[self.exportTabNum].current(0)
        self.Export_1G1RRegion_Label_.append(None)
        self.Export_1G1RRegion_Label_[self.exportTabNum] = ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_1G1RRegion_Label_[self.exportTabNum].configure(text='Primary Region')
        self.Export_1G1RRegion_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='4', sticky='w')
        tooltip.create(self.Export_1G1RRegion_Label_[self.exportTabNum], 'The region used for the 1G1R export.')
        self.Export_1G1RRegion_Combobox_.append(None)
        self.Export_1G1RRegion_Combobox_[self.exportTabNum] = ttk.Combobox(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.regionChoices.append(None)
        self.regionChoices[self.exportTabNum] = tk.StringVar(value='')
        self.Export_1G1RRegion_Combobox_[self.exportTabNum].configure(state='readonly', textvariable=self.regionChoices[self.exportTabNum], values='"Placeholder 1" "Placeholder 2"', width='10')
        self.Export_1G1RRegion_Combobox_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='4', sticky='w')
        self.Export_1G1RIncludeOther_.append(None)
        self.Export_1G1RIncludeOther_[self.exportTabNum] = ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.includeOtherRegionsChoices.append(None)
        self.includeOtherRegionsChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_1G1RIncludeOther_[self.exportTabNum].configure(text='Include Games from Other Regions', variable=self.includeOtherRegionsChoices[self.exportTabNum])
        self.Export_1G1RIncludeOther_[self.exportTabNum].grid(column='0', padx='250', pady='10', row='4', sticky='w')
        tooltip.create(self.Export_1G1RIncludeOther_[self.exportTabNum], 'If enabled: In the event that a game does not contain a rom from your region (e.g. your primary region is USA but the game is a Japan-only release), a secondary region will be used according to your Region/Language Priority Order.\n\nIf disabled: In the event that a game does not contain a rom from your region, the game is skipped entirely.\n\nIf you only want to export roms from your own region, disable this.')
        self.Export_FromList_Label_.append(None)
        self.Export_FromList_Label_[self.exportTabNum] = ttk.Label(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_FromList_Label_[self.exportTabNum].configure(text='Rom List')
        self.Export_FromList_Label_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='5', sticky='w')
        tooltip.create(self.Export_FromList_Label_[self.exportTabNum], 'The text list containing your favorite roms for the current system.')
        self.Export_FromList_PathChooser_.append(None)
        self.Export_FromList_PathChooser_[self.exportTabNum] = PathChooserInput(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.romListFileChoices.append(None)
        self.romListFileChoices[self.exportTabNum] = tk.StringVar(value='')
        self.Export_FromList_PathChooser_[self.exportTabNum].configure(mustexist='true', state='normal', textvariable=self.romListFileChoices[self.exportTabNum], type='file')
        self.Export_FromList_PathChooser_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='5', sticky='w')
        self.Export_IncludeFrame_.append(None)
        self.Export_IncludeFrame_[self.exportTabNum] = ttk.Labelframe(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.Export_IncludeUnlicensed_.append(None)
        self.Export_IncludeUnlicensed_[self.exportTabNum] = ttk.Checkbutton(self.Export_IncludeFrame_[self.exportTabNum])
        self.includeUnlicensedChoices.append(None)
        self.includeUnlicensedChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_IncludeUnlicensed_[self.exportTabNum].configure(text='Unlicensed', variable=self.includeUnlicensedChoices[self.exportTabNum])
        self.Export_IncludeUnlicensed_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='0', sticky='w')
        self.Export_IncludeCompilations_.append(None)
        self.Export_IncludeCompilations_[self.exportTabNum] = ttk.Checkbutton(self.Export_IncludeFrame_[self.exportTabNum])
        self.includeCompilationsChoices.append(None)
        self.includeCompilationsChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_IncludeCompilations_[self.exportTabNum].configure(text='Compilations', variable=self.includeCompilationsChoices[self.exportTabNum])
        self.Export_IncludeCompilations_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='0', sticky='w')
        self.Export_IncludeTestPrograms_.append(None)
        self.Export_IncludeTestPrograms_[self.exportTabNum] = ttk.Checkbutton(self.Export_IncludeFrame_[self.exportTabNum])
        self.includeTestProgramsChoices.append(None)
        self.includeTestProgramsChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_IncludeTestPrograms_[self.exportTabNum].configure(text='Test Programs', variable=self.includeTestProgramsChoices[self.exportTabNum])
        self.Export_IncludeTestPrograms_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='1', sticky='w')
        self.Export_IncludeBIOS_.append(None)
        self.Export_IncludeBIOS_[self.exportTabNum] = ttk.Checkbutton(self.Export_IncludeFrame_[self.exportTabNum])
        self.includeBIOSChoices.append(None)
        self.includeBIOSChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_IncludeBIOS_[self.exportTabNum].configure(text='BIOS', variable=self.includeBIOSChoices[self.exportTabNum])
        self.Export_IncludeBIOS_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='1', sticky='w')
        self.Export_IncludeNES_.append(None)
        self.Export_IncludeNES_[self.exportTabNum] = ttk.Checkbutton(self.Export_IncludeFrame_[self.exportTabNum])
        self.includeNESChoices.append(None)
        self.includeNESChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_IncludeNES_[self.exportTabNum].configure(text='NES Ports', variable=self.includeNESChoices[self.exportTabNum])
        self.Export_IncludeNES_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='2', sticky='w')
        tooltip.create(self.Export_IncludeNES_[self.exportTabNum], 'Include Classic NES Series, Famicom Mini, Hudson Best Collection, and Kunio-kun Nekketsu Collection emulated ports.\n\nIf unsure, leave this disabled.')
        self.Export_IncludeGBAV_.append(None)
        self.Export_IncludeGBAV_[self.exportTabNum] = ttk.Checkbutton(self.Export_IncludeFrame_[self.exportTabNum])
        self.includeGBAVChoices.append(None)
        self.includeGBAVChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_IncludeGBAV_[self.exportTabNum].configure(text='GBA Video', variable=self.includeGBAVChoices[self.exportTabNum])
        self.Export_IncludeGBAV_[self.exportTabNum].grid(column='0', padx='150', pady='10', row='2', sticky='w')
        self.Export_IncludeFrame_[self.exportTabNum].configure(text='Include')
        self.Export_IncludeFrame_[self.exportTabNum].grid(column='0', padx='20', pady='10', row='6', sticky='w')
        self.Export_ExtractArchives_.append(None)
        self.Export_ExtractArchives_[self.exportTabNum] = ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.extractArchivesChoices.append(None)
        self.extractArchivesChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_ExtractArchives_[self.exportTabNum].configure(text='Extract Archives', variable=self.extractArchivesChoices[self.exportTabNum])
        self.Export_ExtractArchives_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.03', x='0', y='0')
        tooltip.create(self.Export_ExtractArchives_[self.exportTabNum], 'If enabled, any roms from your input romset that are contained in zipped archives (ZIP, 7z, etc.) will be extracted during export.\n\nUseful if your output device does not support zipped roms.\n\nIf unsure, leave this disabled.')
        self.Export_ParentFolder_.append(None)
        self.Export_ParentFolder_[self.exportTabNum] = ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.parentFolderChoices.append(None)
        self.parentFolderChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_ParentFolder_[self.exportTabNum].configure(text='Export Each Game to Parent Folder', variable=self.parentFolderChoices[self.exportTabNum])
        self.Export_ParentFolder_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.132', x='0', y='0')
        tooltip.create(self.Export_ParentFolder_[self.exportTabNum], 'If enabled, roms will be exported to a parent folder with the same name as the primary region release of your rom.\n\nFor example, \"Legend of Zelda, The (USA)\" and \"Zelda no Densetsu 1 - The Hyrule Fantasy (Japan)\" will both be exported to a folder titled \"Legend of Zelda, The\".\n\nIf unsure, leave this disabled.')
        self.Export_ParentFolder_[self.exportTabNum].configure(command=self.export_toggleSortGames)
        self.Export_SortByPrimaryRegion_.append(None)
        self.Export_SortByPrimaryRegion_[self.exportTabNum] = ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.sortByPrimaryRegionChoices.append(None)
        self.sortByPrimaryRegionChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_SortByPrimaryRegion_[self.exportTabNum].configure(text='Sort Games by Primary Region', variable=self.sortByPrimaryRegionChoices[self.exportTabNum])
        self.Export_SortByPrimaryRegion_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.234', x='0', y='0')
        tooltip.create(self.Export_SortByPrimaryRegion_[self.exportTabNum], 'If enabled, all roms will be exported to a parent folder named after the game\'s highest-priority region.\n\nFor example, Devil World (NES) has Europe and Japan releases, but not USA. If your order of region priority is USA->Europe->Japan, then all versions of Devil World (and its parent folder, if enabled) will be exported to a folder titled \"[Europe]\".\n\nIf unsure, leave this enabled.')
        self.Export_PrimaryRegionInRoot_.append(None)
        self.Export_PrimaryRegionInRoot_[self.exportTabNum] = ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.primaryRegionInRootChoices.append(None)
        self.primaryRegionInRootChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_PrimaryRegionInRoot_[self.exportTabNum].configure(text='Keep Games from Primary Region in Root', variable=self.primaryRegionInRootChoices[self.exportTabNum])
        self.Export_PrimaryRegionInRoot_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.336', x='0', y='0')
        tooltip.create(self.Export_PrimaryRegionInRoot_[self.exportTabNum], '(Only applies if \"Sort Games by Primary Region\" is enabled.)\n\nIf enabled, a region folder will NOT be created for your highest-priority region.\n\nFor example, if your order of region priority is USA->Europe->Japan, then games that have USA releases will not be exported to a [USA] folder (they will instead be placed directly in the output folder), but games that have Europe releases and not USA releases will be exported to a [Europe] folder.\n\nIf unsure, leave this enabled.')
        self.Export_OverwriteDuplicates_.append(None)
        self.Export_OverwriteDuplicates_[self.exportTabNum] = ttk.Checkbutton(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.overwriteDuplicatesChoices.append(None)
        self.overwriteDuplicatesChoices[self.exportTabNum] = tk.IntVar(value='')
        self.Export_OverwriteDuplicates_[self.exportTabNum].configure(text='Overwrite Duplicate Files', variable=self.overwriteDuplicatesChoices[self.exportTabNum])
        self.Export_OverwriteDuplicates_[self.exportTabNum].place(anchor='nw', relx='.651', rely='.438', x='0', y='0')
        tooltip.create(self.Export_OverwriteDuplicates_[self.exportTabNum], 'If enabled: If a rom in the output directory with the same name as an exported rom already exists, it will be overwritten by the new export.\n\nIf disabled: The export will not overwrite matching roms in the output directory.\n\nIf unsure, leave this disabled.')
        self.button1 = ttk.Button(self.Export_ScrolledFrame_[self.exportTabNum].innerframe)
        self.button1.configure(text='Remove System')
        self.button1.place(anchor='se', relx='1', rely='1', x='-10', y='-10')
        self.button1.configure(command=self.export_removeSystem)
        self.Export_ScrolledFrame_[self.exportTabNum].innerframe.configure(relief='groove')
        self.Export_ScrolledFrame_[self.exportTabNum].configure(usemousewheel=True)
        self.Export_ScrolledFrame_[self.exportTabNum].place(anchor='nw', relheight='.9', relwidth='.9', relx='.05', rely='.05', x='0', y='0')
        self.Export_Systems.add(self.Export_ScrolledFrame_[self.exportTabNum], text=systemName)

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
        pass

    def export_auditAllSystems(self):
        pass

    def export_exportSystem(self):
        pass

    def export_exportAllSystems(self):
        pass

    def export_auditHelp(self):
        pass

    def favorites_loadList(self):
        pass

    def favorites_addFiles(self):
        pass

    def favorites_saveList(self):
        pass

    def settings_region_setPriorityType(self, event=None):
        pass

    def settings_region_addNewRegionCategory(self, event=None):
        pass

    def settings_region_help(self, event=None):
        pass

    def settings_saveChanges(self):
        global defaultSettings
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

    def ssch(self, val): # settings_saveChangesHelper
        if val.get():
            return "True"
        else:
            return "False"

    def changeMainTab(self, event=None):
        if self.Main_Notebook.tab(self.Main_Notebook.select(), "text") == "Config":
            self.loadDefaultSettingsInSettingsTab()



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
        with open(defaultSettingsFile, 'w') as mcf:
            defaultSettings.write(mcf)

    def loadDefaultSettingsInSettingsTab(self):
        global defaultSettings
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

if __name__ == '__main__':
    root = tk.Tk()
    app = EzroApp(root)
    app.run()

