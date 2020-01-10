"""
Copyright 2019 Black Foundry.

This file is part of Robo-CJK.

Robo-CJK is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Robo-CJK is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Robo-CJK.  If not, see <https://www.gnu.org/licenses/>.
"""
from imp import reload
from AppKit import NSCell, NSColor
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.UI import OpenGlyphWindow, AllGlyphWindows, CurrentGlyphWindow
from mojo.roboFont import *
from mojo.canvas import *
from vanilla import *
from vanilla.dialogs import askYesNo
import os
import json
from resources import deepCompoMasters_AGB1_FULL
from utils import files
from utils import git
from views import tableDelegate
from views import mainCanvas
from functools import reduce
reload(files)
reload(git)
reload(mainCanvas)
reload(deepCompoMasters_AGB1_FULL)

from utils import decorators
reload(decorators)
refreshMainCanvas = decorators.refreshMainCanvas

class DesignWindow(BaseWindowController):
    def __init__(self, controller):
        super(DesignWindow, self).__init__()
        self.controller = controller
        self.RCJKI = self.controller.RCJKI
        self.RCJKI.allFonts = []
        self.selectedGlyph = None
    
        self.w = Window((200, 0, 800, 600), 
                'Design', 
                minSize = (300,300), 
                maxSize = (2500,2000))
        
        self.w.fontsList = List((0,0,200,65),
                [],
                selectionCallback = self.fontsListSelectionCallback,
                drawFocusRing = False)

        self.w.searchGlyph = SearchBox((0, 65, 200, 20),
                placeholder="char/name",
                callback = self.searchGlyphCallback,
                sizeStyle = 'small'
                )

        self.w.glyphSetList = List((0,85,200,-260),
                [],
                columnDescriptions = [
                                {"title": "#", "width" : 20, 'editable':False},
                                {"title": "Char", "width" : 30, 'editable':False},
                                {"title": "Name", "width" : 80, 'editable':False},
                                {"title": "MarkColor", "width" : 30, 'editable':False}
                                ],
                selectionCallback = self.glyphSetListSelectionCallback,
                doubleClickCallback = self.glyphSetListdoubleClickCallback,
                # editCallback = self.glyphSetListEditCallback,
                showColumnTitles = False,
                drawFocusRing = False)

        self.w.extremsList = List((0,-260,200,-60),
                [],
                columnDescriptions = [
                                {"title": "#", "width" : 20, 'editable':False},
                                {"title": "Char", "width" : 30, 'editable':False},
                                {"title": "Name", "width" : 80, 'editable':False},
                                {"title": "MarkColor", "width" : 30, 'editable':False}
                                ],
                selectionCallback = self.extremsListSelectionCallback,
                doubleClickCallback = self.glyphSetListdoubleClickCallback,
                # editCallback = self.glyphSetListEditCallback,
                showColumnTitles = False,
                drawFocusRing = False)

        self.delegate = tableDelegate.TableDelegate.alloc().initWithMaster(self, '_design_glyphs', self.w.glyphSetList)
        tableView = self.w.glyphSetList.getNSTableView()
        tableView.setDelegate_(self.delegate)

        self.w.saveLocalFontButton = Button((0,-60,200,20), 
            'Save', 
            callback=self.saveLocalFontButtonCallback)

        self.w.pushBackButton = Button((0,-40,200,20), 
            'Push', 
            callback=self.pushBackButtonCallback)

        self.w.pullMasterGlyphsButton = Button((0,-20,200,20), 
            'Pull', 
            callback=self.pullMasterGlyphsButtonCallback)
        
        

        self.w.mainCanvas = Canvas((200,0,-0,-40), 
            delegate=mainCanvas.MainCanvas(self.RCJKI, self),
            canvasSize=(5000, 5000),
            hasHorizontalScroller=False, 
            hasVerticalScroller=False)

        self.w.colorPicker = ColorWell((200,-60,20,20),
                callback=self.colorPickerCallback, 
                color=NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 0))

        
        self.w.fontsList.setSelection([])

        self.dummyCell = NSCell.alloc().init()
        self.dummyCell.setImage_(None)

        self.w.bind('close', self.windowCloses)
        self.w.bind("became main", self.windowBecameMain)
        self.w.open()

    def searchGlyphCallback(self, sender):
        t = sender.get()
        if t.startswith("uni"):
            code = t.split("uni")[1]
            if code:
                try:
                    char = chr(int(code, 16))
                except: return
            else: return
        elif len(t) > 1:
            return
        else: char = t
        glyphList = self.w.glyphSetList.get()
        for i, e in enumerate(glyphList):
            if e["Char"] == char:
                self.w.glyphSetList.setSelection([i])
                break

    @refreshMainCanvas
    def saveLocalFontButtonCallback(self, sender):
        self.RCJKI.saveAllSubsetFonts()
        # self.w.mainCanvas.update()
        
    @refreshMainCanvas
    def pullMasterGlyphsButtonCallback(self, sender):
        self.RCJKI.designController.pullMastersGlyphs()
        # self.w.mainCanvas.update()

    def pushBackButtonCallback(self, sender):
        rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
        gitEngine = git.GitEngine(rootfolder)
        user = gitEngine.user()
        List = self.RCJKI.collab._userLocker(user).glyphs[self.RCJKI.designStep]
        
        # glyphsList = list(List.keys()) + list(reduce(lambda x, y: x + y, list(List.values())))
        # print(glyphsList)
        self.RCJKI.designController.injectGlyphsBack(List, user)

    def colorPickerCallback(self, sender):
        if self.RCJKI.currentGlyph is None: return
        color = sender.get()
        r = color.redComponent()
        g = color.greenComponent()
        b = color.blueComponent()
        a = color.alphaComponent()
    
        self.RCJKI.currentGlyph.markColor = (r, g, b, a)
        self.controller.updateGlyphSetList()

    def fontsListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            self.RCJKI.currentFont = None
            self.w.glyphSetList.setSelection([])
            self.w.glyphSetList.set([])
            self.selectedGlyph = None
            return
        self.RCJKI.currentFont = self.RCJKI.allFonts[sel[0]][self.controller.fontsList[sel[0]]]
        self.controller.updateGlyphSetList()

    # def glyphSetListEditCallback(self, sender):
    #     if not sender.getSelection(): return

    #     myLocker = self.RCJKI.collab._userLocker(self.RCJKI.user)
    #     if myLocker:
    #         self.RCJKI.lockedGlyphs = myLocker._allOtherLockedGlyphs
    #         self.RCJKI.reservedGlyphs = myLocker.glyphs
    #     else:
    #         myLocker = self.RCJKI.collab._addLocker(self.RCJKI.user)

        # self.RCJKI.projectEditorController.saveCollabToFile()
        # self.RCJKI.projectEditorController.pushRefresh()


    def glyphSetListdoubleClickCallback(self, sender):
        if not sender.getSelection(): return
        if self.selectedGlyphName not in self.RCJKI.currentFont:
            self.RCJKI.currentGlyph = self.RCJKI.currentFont.newGlyph(self.selectedGlyphName)
        self.RCJKI.currentGlyph.width = self.RCJKI.project.settings['designFrame']['em_Dimension'][0]
        self.RCJKI.openGlyphWindow(self.RCJKI.currentGlyph)

    def extremsListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.selectedGlyphName = sender.get()[sel[0]]['Name']
        self.resetCurrentGlyph()

    def glyphSetListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.selectedGlyphName = sender.get()[sel[0]]['Name']
        self.selectedChar = sender.get()[sel[0]]['Char']




        # self.extremsList = []
        rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
        gitEngine = git.GitEngine(rootfolder)
        user = gitEngine.user()
        userGlyphsList = self.RCJKI.collab._userLocker(user).glyphs[self.RCJKI.designStep]
        # if self.selectedGlyphName in userGlyphsList:
        #     for name in userGlyphsList[self.selectedGlyphName]:
        #         char = chr(int(name[3:], 16))
        #         self.extremsList.append(({'#':'', 'Char':char, 'Name':name, 'MarkColor':''}))
            
        
        # self.w.extremsList.setSelection([])
        # self.w.extremsList.set(self.extremsList)


        # self.extremsList = []
        # for script in self.RCJKI.project.script:
        #     for keys2extrems in [deepCompoMasters_AGB1_FULL.deepCompoMasters[script]]:
        #         if self.selectedChar in keys2extrems:
        #             for variants in keys2extrems[self.selectedChar]:
        #                 for variant in variants:
        #                     name = files.unicodeName(variant)
        #                     self.extremsList.append(({'#':'', 'Char':variant, 'Name':name, 'MarkColor':''}))
        # self.w.extremsList.setSelection([])
        # self.w.extremsList.set(self.extremsList)
        
        self.resetCurrentGlyph()

    @refreshMainCanvas
    def resetCurrentGlyph(self):
        if self.selectedGlyphName in self.RCJKI.currentFont:
            self.RCJKI.currentGlyph = self.RCJKI.currentFont[self.selectedGlyphName]
            if self.RCJKI.currentGlyph.markColor is None:
                r, g, b, a = 0, 0, 0, 0
            else: 
                r, g, b, a = self.RCJKI.currentGlyph.markColor
            self.w.colorPicker.set(NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, a))
        else:
            self.RCJKI.currentGlyph = None
        # self.w.mainCanvas.update()

    def windowCloses(self, sender):
        # askYesNo('Do you want to save fonts?', "Without saving you'll loose unsaved modification", alertStyle = 2, parentWindow = None, resultCallback = self.yesnocallback)
        if CurrentGlyphWindow() is not None:
            CurrentGlyphWindow().close()
        self.RCJKI.currentGlyphWindow = None
        self.RCJKI.designController.interface = None

    def yesnocallback(self, yes):
        if yes:
            self.RCJKI.saveAllSubsetFonts()

    @refreshMainCanvas
    def windowBecameMain(self, sender):
        sel = self.w.glyphSetList.getSelection()
        if not sel: return
        self.selectedGlyphName = self.w.glyphSetList.get()[sel[0]]['Name']
        if self.selectedGlyphName in self.RCJKI.currentFont:
            self.RCJKI.currentGlyph = self.RCJKI.currentFont[self.selectedGlyphName]
        else:
            self.RCJKI.currentGlyph = None
        self.RCJKI.inspectorController.updateViews()
        # self.w.mainCanvas.update()

    def tableView_dataCellForTableColumn_row_(self, tableView, tableColumn, row, designStep, glist):
        self.RCJKI.tableView_dataCellForTableColumn_row_(tableView, tableColumn, row, self.w, glist, designStep, self.RCJKI.currentFont)