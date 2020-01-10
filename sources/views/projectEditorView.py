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
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import *
from mojo.roboFont import *
from mojo.drawingTools import *
from mojo.events import extractNSEvent
from mojo.UI import AllGlyphWindows
from vanilla.dialogs import getFile
from mojo.canvas import CanvasGroup
from AppKit import NSColor
import os
import random
import shutil
import copy

from views.drawers import designFrameDrawer
from views.drawers import referenceViewDrawer
from utils import files
from utils import decorators

from resources import characterSets
from resources import deepCompoMasters_AGB1_FULL
reload(designFrameDrawer)
reload(referenceViewDrawer)
reload(files)
reload(characterSets)
reload(deepCompoMasters_AGB1_FULL)
reload(decorators)

antiRecursive = decorators.antiRecursive
sheetSafety = decorators.sheetSafety

class ProjectEditorWindow(BaseWindowController):
    def __init__(self, RCJKI):
        super(ProjectEditorWindow, self).__init__()
        self.RCJKI = RCJKI
        self.w = Window((200, 0, 200, 80), 'Project')
        name = 'No Open Project'
        if self.RCJKI.project:
            name = self.RCJKI.project.name
        self.w.projectNameTextBox = TextBox((0,0,200,20), name, alignment='center')
        self.w.openProjectButton = Button((0,20,200,20), 'Open', callback=self.openProject)
        self.w.newProjectButton = Button((0,40,200,20), 'New', callback=self.newProject)
        self.w.editProjectButton = Button((0,60,200,20), 'Edit', callback=self.editProject)
        self.w.bind('close', self.windowCloses)
        self.w.editProjectButton.enable(self.RCJKI.project!=None)
        self.w.open()

    @sheetSafety
    def editProject(self, sender):
        EditProjectSheet(self)

    def newProject(self, sender):
        self.showPutFile(['roboCJKProject'], self.RCJKI.projectEditorController.saveProject, fileName='Untitled')

    def openProject(self, sender):
        self.showGetFile(['roboCJKProject'], self.RCJKI.projectEditorController.loadProject)

    def windowCloses(self, sender):
        self.RCJKI.projectEditorController.interface = None

class LockerDCEGroup(Group):

    def __init__(self, posSize, controller, step):
        super(LockerDCEGroup, self).__init__(posSize)
        self.c = controller
        self.step = step
        self.script = "Hanzi"

        self.user = None
        usersList = [d['user'] for d in self.c.parent.RCJKI.project.usersLockers['lockers']]
        if usersList:
            self.user = usersList[0]

        self.usersList = List((10, 40, 280, 65),
                usersList,
                selectionCallback = self.usersListSelectionCallback,
                drawFocusRing = False
                ) 

        ####NEW####
        self.selectedDCKey = None
        self.selectedDCVariant = None

        self.searchGlyph = SearchBox((10, 125, 193, 20),
            callback=self.searchGlyphCallback,
            sizeStyle='small'
            )

        checkBox = CheckBoxListCell()
        self.keyList = List((10, 145, 193, -40),
            self.deepComponentKeys,
            columnDescriptions = [{"title": "sel", "cell":checkBox, "width":30}, {"title": "char"}],
            selectionCallback = self.keyListSelectionCallback,
            editCallback = self.keyListEditCallback,
            drawFocusRing = False,
            showColumnTitles = False
            )

        self.getSelectedItems = Button((10, -40, 193, 20),
            "Get Selected Items",
            sizeStyle = 'small',
            callback = self.getSelectedItemsCallback
            )

        self.variantList = List((203, 145, 193, -40),
            self.deepComponentVariants,
            selectionCallback = self.variantListSelectionCallback, 
            drawFocusRing = False,
            showColumnTitles = False
            )

        self.addVariantButton = Button((203, -60, 193/2, -40),
            "+",
            callback = self.addVariantButtonCallback,
            sizeStyle = 'small'
            )

        self.removeVariantButton = Button((203+193/2, -60, 193/2, -40),
            "-",
            callback = self.removeVariantButtonCallback,
            sizeStyle = 'small'
            )

        self.extremsGlyphs = {}
        self.extremsList = TextEditor((396, 145, 193, -40),
            self.extremsDCGlyphs(None),
            callback = self.extremsListCallback
            )

        self.keyList.setSelection([])
        self.setScript()
        
    @property
    def deepComponents(self):
        return deepCompoMasters_AGB1_FULL.deepCompoMasters[self.script]

    @property
    def deepComponentKeys(self):
        if self.user is None:
            return []
        if not self.user+"\n" in [e._toDict['user'] for e in self.c.parent.RCJKI.collab.lockers]:
            userLocker = self.c.parent.RCJKI.collab._addLocker(self.user, self.step)
        else:
            userLocker = [e for e in self.c.parent.RCJKI.collab.lockers if e._toDict['user'] == self.user][0]
        # print(userLocker.glyphs[self.step])
        return [dict(sel = files.unicodeName(e) in userLocker.glyphs[self.step], char = e) for e in list(self.deepComponents.keys())]

    @property
    def deepComponentVariants(self):
        variants = []
        if self.selectedDCKey is not None:
            # print(self.selectedDCKey)
            # print(self.deepComponents[self.selectedDCKey])
            variants = [e[0] for e in list(self.deepComponents[self.selectedDCKey])]
        return variants

    
    def extremsDCGlyphs(self, char, variant = None):
        if char is not None:
            if variant is not None:
                if char not in self.extremsGlyphs:
                    self.extremsGlyphs[char] = {}
                if variant not in self.extremsGlyphs[char]:
                    extrems = ''
            
                    userLocker = [e for e in self.c.parent.RCJKI.collab.lockers if e._toDict['user'] == self.user][0]

                    if files.unicodeName(variant) in userLocker._deepComponentsEdition_glyphs:
                        extrems += "".join([chr(int(e[3:], 16)) for e in userLocker._deepComponentsEdition_glyphs[files.unicodeName(variant)]])
                    else:
                        for e in list(self.deepComponents[char]):
                            if e[0] != variant: continue
                            extrems += "".join(e)

                    # self.extremsGlyphs[char] = {}
                    self.extremsGlyphs[char][variant] = extrems
                    # elif
                    print(extrems)
                    return extrems
                else:

                    print(self.extremsGlyphs[char][variant])
                    return self.extremsGlyphs[char][variant]
        else:
            return ""

    def extremsListCallback(self, sender):
        print("coucoalkefhjoiaejfopeakdpoeau")
        self.extremsGlyphs[self.selectedDCKey][self.selectedDCVariant] = sender.get()
        print(self.extremsGlyphs[self.selectedDCKey][self.selectedDCVariant])
        self.setGlyphs(self.keyList.get())

    # def extremsListCallback(self, sender):
    #     if self.script in deepCompoMasters_AGB1_FULL.deepCompoMasters:
    #         if self.selectedChar in self.extremsGlyphs:
    #             self.extremsGlyphs[self.selectedChar] = sender.get()
        # self.setGlyphs(self.basicGlyphsList.get())

    # def getExtremsGlyphs(self, char):
    #     if char not in self.extremsGlyphs:
    #         extrems = ""
    #         if self.script in deepCompoMasters_AGB1_FULL.deepCompoMasters:
    #             if char in deepCompoMasters_AGB1_FULL.deepCompoMasters[self.script]:
    #                 for variant in deepCompoMasters_AGB1_FULL.deepCompoMasters[self.script][char]:
    #                     extrems += "".join(variant)

    #         self.extremsGlyphs[char] = extrems
    #         return extrems
    #     else:
    #         return self.extremsGlyphs[char]

    def keyListSelectionCallback(self, sender):
        self.setSelectedDCKey(sender)      

    def variantListSelectionCallback(self, sender):
        self.selectedDCVariant = None
        sel = sender.getSelection()
        if sel:
            self.selectedDCVariant = sender.get()[sel[0]]

        self.extremsList.set(self.extremsDCGlyphs(self.selectedDCKey, variant = self.selectedDCVariant))

    def setSelectedDCKey(self, sender):
        sel = sender.getSelection()
        self.selectedDCKey = None
        if sel:
            # print(sel)
            if self.deepComponentKeys[sender.getSelection()[0]]["sel"]:
                self.selectedDCKey = self.deepComponentKeys[sender.getSelection()[0]]["char"]
        # print(self.selectedDCKey)
        self.variantList.set(self.deepComponentVariants)
        self.addVariantButton.show(len(self.deepComponentVariants) != 0)
        self.removeVariantButton.show(len(self.deepComponentVariants) != 0)
        self.extremsList.set(self.extremsDCGlyphs(self.selectedDCKey, variant = self.selectedDCVariant))

    def addVariantButtonCallback(self, sender):
        pass

    def removeVariantButtonCallback(self, sender):
        pass

    # def extremsListCallback(self, sender):
    #     pass

    def keyListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.setGlyphs(sender.get())

    def setGlyphs(self, glyphlist):
        glyphs = {}
        for k in glyphlist:
            if not k["sel"]: continue
            char = k["char"]
            for variant in [e[0] for e in list(self.deepComponents[char])]:
                # print("extresm",self.extremsDCGlyphs(char, variant))
                # print("variant", variant)
                var = {files.unicodeName(variant):[files.unicodeName(e) for e in self.extremsDCGlyphs(char, variant)]}
                # print("var1", var)
                # print("var2", {files.unicodeName(variant):[files.unicodeName(e)] for e in list(self.extremsDCGlyphs(char, variant))})
                glyphs = dict(var, **glyphs)
        # print(glyphs)
        userLocker = self.c.parent.RCJKI.collab._addLocker(self.user, self.step)
        
        userLocker._setStep(self.step)
        userLocker._clearGlyphs()
        userLocker._addGlyphs(glyphs)
        userLocker._setScript(self.script)
        self.c.parent.RCJKI.project.usersLockers = self.c.parent.RCJKI.collab._toDict

        self.setSelectedDCKey(self.keyList)

    ####OLD
    def usersListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.user = sender.get()[sel[0]]

        if hasattr(self, 'scriptsRadioGroup'):
            # print(self.c.parent.RCJKI.collab._toDict)
            lockers = self.c.parent.RCJKI.collab._toDict["lockers"]
            for locker in lockers:
                if locker["user"] == self.user:
                    print(locker["script"])
                    self.script = locker["script"]
            getattr(self, 'scriptsRadioGroup').set(self.c.parent.RCJKI.project.script.index(self.script))

        self.keyList.set(self.deepComponentKeys)


    def setScript(self):
        if hasattr(self, 'scriptsRadioGroup'):
            delattr(self, 'scriptsRadioGroup')

        if len(self.c.parent.RCJKI.project.script) == 1:
            self.script = self.c.parent.RCJKI.project.script[0]

        elif len(self.c.parent.RCJKI.project.script) > 1:
            self.scriptsRadioGroup = RadioGroup(
                (300, 40, 200, 20*len(self.c.parent.RCJKI.project.script)), 
                self.c.parent.RCJKI.project.script,
                sizeStyle = "small",
                callback = self.scriptsRadioGroupCallback
                )
            self.scriptsRadioGroup.set(self.c.parent.RCJKI.project.script.index(self.script))

        self.setScriptInLocker()

    def scriptsRadioGroupCallback(self, sender):
        self.script = self.c.parent.RCJKI.project.script[sender.get()]
        self.setScriptInLocker()

    def setScriptInLocker(self):
        if hasattr(self, "user"):
            userLocker = self.c.parent.RCJKI.collab._addLocker(self.user, self.step)
            userLocker._setScript(self.script)

        self.keyList.set(self.deepComponentKeys)

    def searchGlyphCallback(self, sender):
        char = sender.get()
        glyphsList = self.deepComponentKeys
        index = [i for i, c in enumerate(glyphsList) if c["char"] in char]
        self.keyList.setSelection(index)


        # char = sender.get()
        # if len(char) > 1: return
        # glyphsList = self.deepComponentKeys
        # for i, c in enumerate(glyphsList):
        #     if c["char"] == char:
        #         self.keyList.setSelection([i])
        #         break

    def getSelectedItemsCallback(self, sender):
        basicGlyphList = self.keyList
        sel = basicGlyphList.getSelection()
        if not sel: return
        basicGlyph = copy.deepcopy(self.deepComponentKeys)
        for i in sel:
            basicGlyph[i]['sel'] = 1
        self.keyList.set(basicGlyph)

class LockerIDGroup(Group):

    def __init__(self, posSize, controller, step):
        super(LockerIDGroup, self).__init__(posSize)
        self.c = controller
        self.step = step
        self.script = "Hanzi"

        self.user = None
        usersList = [d['user'] for d in self.c.parent.RCJKI.project.usersLockers['lockers']]
        if usersList:
            self.user = usersList[0]
            # print(self.c.parent.RCJKI.project.usersLockers['lockers'][0]["user"],self.c.parent.RCJKI.project.usersLockers['lockers'][0]["script"])
            self.script = self.c.parent.RCJKI.project.usersLockers['lockers'][0]["script"]

        self.usersList = List((10, 40, 280, 65),
                usersList,
                selectionCallback = self.usersListSelectionCallback,
                drawFocusRing = False
                ) 

        ####NEW####
        self.searchGlyph = SearchBox((10, 125, 280, 20),
            callback=self.searchGlyphCallback,
            sizeStyle='small'
            )

        self.selectedChar = None

        checkBox = CheckBoxListCell()
        self.basicGlyphsList = List((10, 145, 280, -40),
            self.basicGlyphs,
            columnDescriptions = [{"title": "sel", "cell":checkBox, "width":30}, {"title": "char"}],
            selectionCallback = self.basicGlyphsListSelectionCallback,
            editCallback = self.basicGlyphsListEditCallback,
            drawFocusRing = False,
            showColumnTitles = False
            )

        self.deselectItems = Button((10, -40, 90, 20),
            "Deselect",
            sizeStyle = 'small',
            callback= self.deselectItemsCallback)
        self.getSelectedItems = Button((100, -40, 190, 20),
            "Get Selected Items",
            sizeStyle = 'small',
            callback = self.getSelectedItemsCallback
            )
        self.extremsGlyphs = {}
        self.extremsList = TextEditor((300, 145, -10, -40),
            self.getExtremsGlyphs(None),
            callback = self.extremsListCallback
            )

        self.basicGlyphsList.setSelection([])
        self.setScript()


    @property
    def basicGlyphs(self):
        if self.user is None:
            return []
        userLocker = [e for e in self.c.parent.RCJKI.collab.lockers if e._toDict['user'] == self.user][0]
        charset = characterSets.sets[self.script]['Basic']
        for c in characterSets.sets[self.script].get('DeepComponentKeys', []):
            if c in charset: continue
            charset += c
        return [dict(char = c, sel = files.unicodeName(c) in userLocker.glyphs[self.step]) for c in charset]
        # if not self.user+"\n" in [e._toDict['user'] for e in self.c.parent.RCJKI.collab.lockers]:
        #     userLocker = self.c.parent.RCJKI.collab._addLocker(self.user, self.step)
        # else:
        #     userLocker = [e for e in self.c.parent.RCJKI.collab.lockers if e._toDict['user'] == self.user][0]
        # return [dict(sel = files.unicodeName(e) in userLocker.glyphs[self.step], char = e) for e in list(self.deepComponents.keys())]

    def getSelectedItemsCallback(self, sender):
        basicGlyphList = self.basicGlyphsList
        sel = basicGlyphList.getSelection()
        if not sel: return
        basicGlyph = self.basicGlyphs
        for i in sel:
            basicGlyph[i]['sel'] = not basicGlyph[i]['sel']
        self.basicGlyphsList.set(basicGlyph)

    def deselectItemsCallback(self, sender):
        basicGlyphList = self.basicGlyphsList
        sel = basicGlyphList.getSelection()
        if not sel: return
        basicGlyph = self.basicGlyphs
        for i in sel:
            basicGlyph[i]['sel'] = 0
        self.basicGlyphsList.set(basicGlyph)
    
    def getExtremsGlyphs(self, char):
        if char not in self.extremsGlyphs:
            extrems = ""
            if self.script in deepCompoMasters_AGB1_FULL.deepCompoMasters:
                if char in deepCompoMasters_AGB1_FULL.deepCompoMasters[self.script]:
                    for variant in deepCompoMasters_AGB1_FULL.deepCompoMasters[self.script][char]:
                        extrems += "".join(variant)

            self.extremsGlyphs[char] = extrems
            return extrems
        else:
            return self.extremsGlyphs[char]

    def extremsListCallback(self, sender):
        if self.script in deepCompoMasters_AGB1_FULL.deepCompoMasters:
            if self.selectedChar in self.extremsGlyphs:
                self.extremsGlyphs[self.selectedChar] = sender.get()
        self.setGlyphs(self.basicGlyphsList.get())
                # print(deepCompoMasters_AGB1_FULL.deepCompoMasters[self.script][self.selectedChar])

    def searchGlyphCallback(self, sender):
        char = sender.get()
        glyphsList = self.basicGlyphs
        index = [i for i, c in enumerate(glyphsList) if c["char"] in char]
        self.basicGlyphsList.setSelection(index)
        # char = sender.get()
        # if len(char) > 1: return
        # glyphsList = self.basicGlyphs
        # for i, c in enumerate(glyphsList):
        #     if c["char"] == char:
        #         self.basicGlyphsList.setSelection([i])
        #         break


    # @antiRecursive
    def basicGlyphsListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.setGlyphs(sender.get())

    def setGlyphs(self, glyphsList):
        glyphs = {}
        for k in glyphsList:
            if not k["sel"]: continue
            char = k["char"]
            glyphs[files.unicodeName(char)] = [files.unicodeName(c) for c in self.getExtremsGlyphs(char)]

        userLocker = self.c.parent.RCJKI.collab._addLocker(self.user, self.step)
        
        userLocker._setStep(self.step)
        userLocker._clearGlyphs()
        userLocker._addGlyphs(glyphs)
        userLocker._setScript(self.script)
        self.c.parent.RCJKI.project.usersLockers = self.c.parent.RCJKI.collab._toDict

        
        # yield self.basicGlyphsList.set(self.basicGlyphs)

    def basicGlyphsListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.selectedChar = None
            return 
        self.selectedChar = sender.get()[sel[0]]["char"]
        
        self.extremsList.set(self.getExtremsGlyphs(self.selectedChar))
        # deepCompoMasters_AGB1_FULL


    def setScript(self):
        if hasattr(self, 'scriptsRadioGroup'):
            delattr(self, 'scriptsRadioGroup')

        if len(self.c.parent.RCJKI.project.script) == 1:
            self.script = self.c.parent.RCJKI.project.script[0]

        elif len(self.c.parent.RCJKI.project.script) > 1:
            self.scriptsRadioGroup = RadioGroup(
                (300, 40, 200, 20*len(self.c.parent.RCJKI.project.script)), 
                self.c.parent.RCJKI.project.script,
                sizeStyle = "small",
                callback = self.scriptsRadioGroupCallback
                )
            self.scriptsRadioGroup.set(self.c.parent.RCJKI.project.script.index(self.script))

        self.setScriptInLocker()

    def scriptsRadioGroupCallback(self, sender):
        self.script = self.c.parent.RCJKI.project.script[sender.get()]
        self.setScriptInLocker()

    def setScriptInLocker(self):
        if hasattr(self, "user"):
            # print(self.script)
            userLocker = self.c.parent.RCJKI.collab._addLocker(self.user, self.step)
            userLocker._setScript(self.script)

        self.basicGlyphsList.set(self.basicGlyphs)


    ####OLD
    def usersListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.user = sender.get()[sel[0]]

        if hasattr(self, 'scriptsRadioGroup'):
            # print(self.c.parent.RCJKI.collab._toDict)
            lockers = self.c.parent.RCJKI.collab._toDict["lockers"]
            for locker in lockers:
                if locker["user"] == self.user:
                    print(locker["script"])
                    self.script = locker["script"]
                    getattr(self, 'scriptsRadioGroup').set(self.c.parent.RCJKI.project.script.index(self.script))

        self.basicGlyphsList.set(self.basicGlyphs)

class LockerDGroup(Group):

    def __init__(self, posSize, controller, step):
        super(LockerDGroup, self).__init__(posSize)
        self.c = controller
        self.step = step

        self.script = "Hanzi"

        usersList = [d['user'] for d in self.c.parent.RCJKI.project.usersLockers['lockers']]
        if usersList:
            self.user = usersList[0]
            self.script = self.c.parent.RCJKI.project.usersLockers['lockers'][0]["script"]

        self.usersList = List((10, 40, 280, 65),
                usersList,
                selectionCallback = self.usersListSelectionCallback,
                drawFocusRing = False
                )        

        # self.charactersTextEditor = TextEditor((10, 125, -10, -40),
        #         self.charactersTextEditorText,
        #         callback=self.charactersTextEditorCallback)

        self.searchGlyph = SearchBox((10, 125, 280, 20),
            callback=self.searchGlyphCallback,
            sizeStyle='small'
            )

        self.selectedChar = None

        checkBox = CheckBoxListCell()
        self.basicGlyphsList = List((10, 145, 280, -40),
            self.basicGlyphs,
            columnDescriptions = [{"title": "sel", "cell":checkBox, "width":30}, {"title": "char"}],
            selectionCallback = self.basicGlyphsListSelectionCallback,
            editCallback = self.basicGlyphsListEditCallback,
            drawFocusRing = False,
            showColumnTitles = False
            )
        self.deselectItems = Button((10, -40, 90, 20),
            "Deselect",
            sizeStyle = 'small',
            callback= self.deselectItemsCallback)
        self.getSelectedItems = Button((100, -40, 280, 20),
            "Get Selected Items",
            sizeStyle = 'small',
            callback = self.getSelectedItemsCallback
            )

        self.setScript()

    @property
    def basicGlyphs(self):
        if self.user is None:
            return []
        userLocker = [e for e in self.c.parent.RCJKI.collab.lockers if e._toDict['user'] == self.user][0]
        return [dict(char = c, sel = files.unicodeName(c) in userLocker.glyphs[self.step]) for c in characterSets.sets[self.script]['Full']]

    def getSelectedItemsCallback(self, sender):
        basicGlyphList = self.basicGlyphsList
        sel = basicGlyphList.getSelection()
        if not sel: return
        basicGlyph = self.basicGlyphs
        for i in sel:
            basicGlyph[i]['sel'] = not basicGlyph[i]['sel']
        self.basicGlyphsList.set(basicGlyph)

    def deselectItemsCallback(self, sender):
        basicGlyphList = self.basicGlyphsList
        sel = basicGlyphList.getSelection()
        if not sel: return
        basicGlyph = self.basicGlyphs
        for i in sel:
            basicGlyph[i]['sel'] = 0
        self.basicGlyphsList.set(basicGlyph)

    def searchGlyphCallback(self, sender):
        char = sender.get()
        glyphsList = self.basicGlyphs
        index = [i for i, c in enumerate(glyphsList) if c["char"] in char]
        self.basicGlyphsList.setSelection(index)
        # char = sender.get()
        # if len(char) > 1: return
        # glyphsList = self.basicGlyphs
        # for i, c in enumerate(glyphsList):
        #     if c["char"] == char:
        #         self.basicGlyphsList.setSelection([i])
        #         break

    def basicGlyphsListEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        glyphs = set()
        for k in sender.get():
            if not k["sel"]: continue
            char = k["char"]
            glyphs.add(files.unicodeName(char))

        userLocker = self.c.parent.RCJKI.collab._addLocker(self.user, self.step)
        
        userLocker._setStep(self.step)
        userLocker._clearGlyphs()
        userLocker._addGlyphs(glyphs)
        userLocker._setScript(self.script)
        self.c.parent.RCJKI.project.usersLockers = self.c.parent.RCJKI.collab._toDict

        
        # yield self.basicGlyphsList.set(self.basicGlyphs)

    def basicGlyphsListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: 
            self.selectedChar = None
            return 
        self.selectedChar = sender.get()[sel[0]]["char"]
        
        # self.extremsList.set(self.getExtremsGlyphs(self.selectedChar))
        # deepCompoMasters_AGB1_FULL

    def setScript(self):
        if hasattr(self, 'scriptsRadioGroup'):
            delattr(self, 'scriptsRadioGroup')

        if len(self.c.parent.RCJKI.project.script) == 1:
            self.script = self.c.parent.RCJKI.project.script[0]

        elif len(self.c.parent.RCJKI.project.script) > 1:
            self.scriptsRadioGroup = RadioGroup(
                (300, 40, 200, 20*len(self.c.parent.RCJKI.project.script)), 
                self.c.parent.RCJKI.project.script,
                sizeStyle = "small",
                callback = self.scriptsRadioGroupCallback
                )
            self.scriptsRadioGroup.set(self.c.parent.RCJKI.project.script.index(self.script))

        self.setScriptInLocker()

    def scriptsRadioGroupCallback(self, sender):
        self.script = self.c.parent.RCJKI.project.script[sender.get()]
        self.setScriptInLocker()
        self.basicGlyphsList.set(self.basicGlyphs)

    def setScriptInLocker(self):
        if hasattr(self, "user"):
            userLocker = self.c.parent.RCJKI.collab._addLocker(self.user, self.step)
            userLocker._setScript(self.script)

    def usersListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.user = sender.get()[sel[0]]

        if hasattr(self, 'scriptsRadioGroup'):
            # print(self.c.parent.RCJKI.collab._toDict)
            lockers = self.c.parent.RCJKI.collab._toDict["lockers"]
            for locker in lockers:
                if locker["user"] == self.user:
                    # print(locker["script"])
                    self.script = locker["script"]
                    getattr(self, 'scriptsRadioGroup').set(self.c.parent.RCJKI.project.script.index(self.script))
        # self.charactersTextEditor.set(self.charactersTextEditorText)
        self.basicGlyphsList.set(self.basicGlyphs)

    @property
    def charactersTextEditorText(self):
        if hasattr(self, "user"):
            userLocker = self.c.parent.RCJKI.collab._addLocker(self.user, self.step)
            glyphs = userLocker.glyphs[self.step]
            chars = [chr(int(glyph[3:], 16)) for glyph in glyphs]
            chars.sort()
        else: chars = []
        return ''.join(chars)

    def charactersTextEditorCallback(self, sender):
        chars = sender.get()
        sel = self.usersList.getSelection()
        if not sel: return
        userLocker = self.c.parent.RCJKI.collab._addLocker(self.user, self.step)
        glyphs = [files.unicodeName(char) for char in chars]
        userLocker._setStep(self.step)
        userLocker._clearGlyphs()
        userLocker._addGlyphs(glyphs)
        userLocker._setScript(self.script)
        self.c.parent.RCJKI.project.usersLockers = self.c.parent.RCJKI.collab._toDict
        

class LockerDCIGroup(Group):

    def __init__(self, posSize, controller, step):
        super(LockerDCIGroup, self).__init__(posSize)
        self.c = controller
        self.step = step

        usersList = [d['user'] for d in self.c.parent.RCJKI.project.usersLockers['lockers']]
        if usersList:
            self.user = usersList[0]

        self.usersList = List((10, 40, 280, 65),
                usersList,
                selectionCallback = self.usersListSelectionCallback,
                drawFocusRing = False
                )        

        self.charactersTextEditor = TextEditor((10, 125, -10, -40),
                self.charactersTextEditorText,
                callback=self.charactersTextEditorCallback)

        self.script = "Hanzi"
        self.setScript()

    def setScript(self):
        if hasattr(self, 'scriptsRadioGroup'):
            delattr(self, 'scriptsRadioGroup')

        if len(self.c.parent.RCJKI.project.script) == 1:
            self.script = self.c.parent.RCJKI.project.script[0]

        elif len(self.c.parent.RCJKI.project.script) > 1:
            self.scriptsRadioGroup = RadioGroup(
                (300, 40, 200, 20*len(self.c.parent.RCJKI.project.script)), 
                self.c.parent.RCJKI.project.script,
                sizeStyle = "small",
                callback = self.scriptsRadioGroupCallback
                )
            self.scriptsRadioGroup.set(self.c.parent.RCJKI.project.script.index(self.script))

        self.setScriptInLocker()

    def scriptsRadioGroupCallback(self, sender):
        self.script = self.c.parent.RCJKI.project.script[sender.get()]
        self.setScriptInLocker()

    def setScriptInLocker(self):
        if hasattr(self, "user"):
            userLocker = self.c.parent.RCJKI.collab._addLocker(self.user, self.step)
            userLocker._setScript(self.script)

    def usersListSelectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        self.user = sender.get()[sel[0]]
        self.charactersTextEditor.set(self.charactersTextEditorText)

    @property
    def charactersTextEditorText(self):
        if hasattr(self, "user"):
            userLocker = self.c.parent.RCJKI.collab._addLocker(self.user, self.step)
            glyphs = userLocker.glyphs[self.step]
            chars = [chr(int(glyph[3:], 16)) for glyph in glyphs]
            chars.sort()
        else: chars = []
        return ''.join(chars)

    def charactersTextEditorCallback(self, sender):
        chars = sender.get()
        sel = self.usersList.getSelection()
        if not sel: return
        userLocker = self.c.parent.RCJKI.collab._addLocker(self.user, self.step)
        glyphs = [files.unicodeName(char) for char in chars]
        userLocker._setStep(self.step)
        userLocker._clearGlyphs()
        userLocker._addGlyphs(glyphs)
        userLocker._setScript(self.script)
        self.c.parent.RCJKI.project.usersLockers = self.c.parent.RCJKI.collab._toDict

class EditProjectSheet():
    def __init__(self, parent):
        self.previewFont = None
        self.previewGlyph = None
        self.parent = parent
        self.parent.sheet = Sheet((600, 400), self.parent.w)

        self.parent.sheet.projectNameEditText = EditText((10, 10, -10, 20), self.parent.RCJKI.project.name, callback=self.projectNameEditTextCallback)

        segmentedElements = ["Masters", "Lockers", "Design Frame", "Reference Viewer"]
        self.parent.sheet.projectSectionsSegmentedButton = SegmentedButton((10,40,-10,20), 
                [dict(title=e, width=577/len(segmentedElements)) for e in segmentedElements],
                callback = self.projectSectionsSegmentedButtonCallback)
        self.parent.sheet.projectSectionsSegmentedButton.set(0)

        self.parent.sheet.masterGroup = Group((0,60,-0,-30))

        l = [{'FamilyName':e.split('-')[0], 'StyleName':e.split('-')[1]} for e in self.parent.RCJKI.project.masterFontsPaths]

        self.parent.sheet.masterGroup.mastersList = List((10, 10, -10, 140), 
                l,
                columnDescriptions = [{"title": "FamilyName"}, {"title": "StyleName"}],
                drawFocusRing = False,
                selectionCallback = self.mastersListSelectionCallback,
                editCallback=self.mastersListEditCallback)

        self.parent.sheet.masterGroup.importMastersButton = Button((10, 155, 190, 20), 
                "Import",
                sizeStyle = "small",
                callback = self.importMastersButtonCallback)

        self.parent.sheet.masterGroup.createMastersButton = Button((205, 155, 190, 20), 
                "Create",
                sizeStyle = "small",
                callback = self.createMastersButtonCallback)

        self.parent.sheet.masterGroup.removeMastersButton = Button((400, 155, -10, 20), 
                "Remove",
                sizeStyle = "small",
                callback = self.removeMastersButtonCallback)

        x, y = 10, 190
        for index, script in enumerate(self.parent.RCJKI.scriptsList):
            checkBox = CheckBox(
                (x, y, 150, 20), 
                script, 
                value = script in self.parent.RCJKI.project.script,
                sizeStyle = "small",
                callback = self.scriptsCheckBoxCallback
                )
            y += 25
            if index != 0 and not index % 5:
                x += 200
                y = 190
            setattr(self.parent.sheet.masterGroup, "%sCheckBox"%script, checkBox)
        # self.parent.sheet.masterGroup.scriptsRadioGroup = RadioGroup((10, 190, 200, 60), self.parent.RCJKI.scriptsList, callback=self.scriptsRadioGroupCallback)
        # self.parent.sheet.masterGroup.scriptsRadioGroup.set(self.parent.RCJKI.scriptsList.index(self.parent.RCJKI.project.script))


        ###
        self.parent.sheet.lockerGroup = Group((0,60,-0,-30))

        segmentedElements = ["Initial Design",
                            # "Keys and Extremes", 
                            "Design",
                            "DC Edition", 
                            "DC Instantiation"
                            ]
        self.parent.sheet.lockerGroup.lockerDesignStepSegmentedButton = SegmentedButton((10, 10, -10, 20),
            [dict(title=e, width=577/len(segmentedElements)) for e in segmentedElements],
            callback = self.lockerDesignStepSegmentedButtonCallback,
            )
        self.parent.sheet.lockerGroup.lockerDesignStepSegmentedButton.set(0)

        self.parent.sheet.lockerGroup.initialDesign = LockerIDGroup((0, 0, -0, -0), self, "_initialDesign_glyphs")
        # self.parent.sheet.lockerGroup.keysAndExtrems = LockerDCIGroup((0, 0, -0, -0), self, "_keysAndExtrems_glyphs")
        # self.parent.sheet.lockerGroup.keysAndExtrems.show(0)
        self.parent.sheet.lockerGroup.design = LockerDGroup((0, 0, -0, -0), self, "_design_glyphs")
        self.parent.sheet.lockerGroup.design.show(0)
        self.parent.sheet.lockerGroup.deepComponentEdition = LockerDCEGroup((0, 0, -0, -0), self, "_deepComponentsEdition_glyphs")
        self.parent.sheet.lockerGroup.deepComponentEdition.show(0)
        self.parent.sheet.lockerGroup.deepComponentInstantiation = LockerDCIGroup((0, 0, -0, -0), self, "_deepComponentsInstantiation_glyphs")
        self.parent.sheet.lockerGroup.deepComponentInstantiation.show(0)
        
        # self.parent.sheet.lockerGroup.usersList = List((10, 40, 280, 65),
        #         [d['user'] for d in self.parent.RCJKI.project.usersLockers['lockers']],
        #         selectionCallback = self.usersListSelectionCallback,
        #         drawFocusRing = False
        #         )
        # self.parent.sheet.lockerGroup.charactersTextEditor = TextEditor((10, 125, -10, -40),
        #                             callback=self.charactersTextEditorCallback)
        ###

        self.parent.sheet.designFrameGroup = Group((0,60,-0,-30))

        self.parent.sheet.designFrameGroup.EM_Dimension_title = TextBox((10,13,200,20), 
                "EM Dimension (FU)", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.EM_DimensionX_title = TextBox((145,13,20,20), 
                "X:", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.EM_DimensionX_editText = EditText((160,10,45,20), 
                self.parent.RCJKI.project.settings['designFrame']['em_Dimension'][0], 
                callback = self.EM_DimensionX_editText_callback,
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.EM_DimensionY_title = TextBox((235,13,20,20), 
                "Y:", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.EM_DimensionY_editText = EditText((250,10,45,20), 
                self.parent.RCJKI.project.settings['designFrame']['em_Dimension'][1],
                callback = self.EM_DimensionY_editText_callback,
                sizeStyle = "small")

        self.parent.sheet.designFrameGroup.characterFace_title = TextBox((10,43,200,20), 
                "Character Face (EM%)", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.characterFacePercent_title = TextBox((208,43,30,20), 
                "%", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.characterFace_editText = EditText((160,40,45,20), 
                self.parent.RCJKI.project.settings['designFrame']['characterFace'],
                callback = self.characterFace_editText_callback,
                sizeStyle = "small")

        self.parent.sheet.designFrameGroup.overshoot_title = TextBox((10,73,200,20), 
                "Overshoot (FU)", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.overshootOutside_title = TextBox((110,73,70,20), 
                "Outside:", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.overshootOutside_editText = EditText((160,70,45,20), 
                self.parent.RCJKI.project.settings['designFrame']['overshoot'][0],
                callback = self.overshootOutside_editText_callback,
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.overshootInside_title = TextBox((210,73,60,20), 
                "Inside:", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.overshootInside_editText = EditText((250,70,45,20), 
                self.parent.RCJKI.project.settings['designFrame']['overshoot'][1],
                callback = self.overshootInside_editText_callback,
                sizeStyle = "small")

        self.parent.sheet.designFrameGroup.horizontalLine_title = TextBox((10,103,140,20), 
                "Horizontal Line (EM%)", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.horizontalLine_slider = Slider((160,100,135,20), 
                minValue = 0, maxValue = 50, value = self.parent.RCJKI.project.settings['designFrame']['horizontalLine'], 
                sizeStyle = "small",
                stopOnTickMarks = True,
                tickMarkCount = 26,
                callback = self._horizontalLine_slider_callback)

        self.parent.sheet.designFrameGroup.verticalLine_title = TextBox((10,133,140,20), 
                "Vertical Line (EM%)", 
                sizeStyle = "small")
        self.parent.sheet.designFrameGroup.verticalLine_slider = Slider((160,130,135,20), 
                minValue = 0, maxValue = 50, value = self.parent.RCJKI.project.settings['designFrame']['verticalLine'], 
                sizeStyle = "small",
                stopOnTickMarks = True,
                tickMarkCount = 26,
                callback = self._verticalLine_slider_callback)

        self.parent.sheet.designFrameGroup.customsFrames_title = TextBox((10,163,200,20), 
                "Customs Frames (EM%):", 
                sizeStyle = "small")

        slider = SliderListCell(tickMarkCount=26, stopOnTickMarks=True)

        self.parent.sheet.designFrameGroup.customsFrames_list = List((10,193,285,-30),
                self.parent.RCJKI.project.settings['designFrame']['customsFrames'],
                columnDescriptions = [{"title": "Name", "width" : 75}, 
                                    {"title": "Value", "width" : 200, "cell": slider}],
                editCallback = self._customsFrames_list_editCallback,
                drawFocusRing = False)

        self.parent.sheet.designFrameGroup.addCustomsFrames_button = Button((170,-28,62,-10),
                "+",
                callback = self._addCustomsFrames_button_callback,
                sizeStyle="small")

        self.parent.sheet.designFrameGroup.removeCustomsFrames_button = Button((232,-28,62,-10),
                "-",
                callback = self._removeCustomsFrames_button_callback,
                sizeStyle="small")

        self.parent.sheet.designFrameGroup.changeFontButton = Button((-295,-30,145,-10), 
            'Change Font', callback=self.changeFontButtonCallBack, sizeStyle="small")

        self.parent.sheet.designFrameGroup.changeGlyphButton = Button((-150,-30,145,-10), 
            'Change Glyph', callback=self.changeGlyphButtonCallBack, sizeStyle="small")

        self.fontNames = list(self.parent.RCJKI.project.masterFontsPaths.keys())
        self.selectedFontIndex = 0
        if self.fontNames:
            self.getPreviewFont()
            self.getPreviewGlyph()
        else:
            self.previewGlyph = None

        self.parent.sheet.designFrameGroup.canvas = CanvasGroup((-295,0,-10,-30), 
                delegate=ProjectCanvas("DesignFrame", self))


        ####

        self.parent.sheet.referenceViewerGroup = Group((0,60,-0,-30))

        self.parent.sheet.referenceViewerGroup.FontList_comboBox = ComboBox((10, 10, 130, 18),
                files.fontsList.get(),
                sizeStyle='small')
        self.parent.sheet.referenceViewerGroup.FontList_comboBox.set(files.fontsList.get()[0])

        self.parent.sheet.referenceViewerGroup.addReferenceFont_button = Button((150, 10, 70, 20), 
                "Add", 
                sizeStyle="small",
                callback = self._addReferenceFont_button_callback)

        self.parent.sheet.referenceViewerGroup.removeReference_button = Button((225,10,70,20),
                "Remove",
                sizeStyle="small",
                callback = self._removeReference_button_callback)

        l = [{"Font": e['font']} for e in self.parent.RCJKI.project.settings['referenceViewer']]
        self.parent.sheet.referenceViewerGroup.reference_list = List((10,35,285,125),
                l,
                columnDescriptions = [{"title": "Font"}],
                selectionCallback = self._reference_list_selectionCallback,
                drawFocusRing = False)


        self.parent.sheet.referenceViewerGroup.settings = Group((10,160,295,-0))
        self.parent.sheet.referenceViewerGroup.settings.show(0)

        y = 0

        self.parent.sheet.referenceViewerGroup.settings.size_title = TextBox((0,y,100,20),
                "Size (FU)", 
                sizeStyle = "small")
        self.parent.sheet.referenceViewerGroup.settings.size_editText = EditText((-60,y,-10,20),
                "", 
                sizeStyle = "small",
                callback = self._size_editText_callback)

        self.parent.sheet.referenceViewerGroup.settings.size_slider = Slider((90,y,-65,20),
                minValue = 0,
                maxValue = 1000,
                value = 250,
                sizeStyle = "small",
                callback = self._size_slider_callback)

        y += 30
        self.parent.sheet.referenceViewerGroup.settings.color_title = TextBox((0,y,100,20),
                "Color (FU)", 
                sizeStyle = "small")
        self.parent.sheet.referenceViewerGroup.settings.color_colorWell = ColorWell((90,y-3,-10,20),
                callback=self._color_editText_callback, 
                color=NSColor.grayColor())

        y+=30
        # self.parent.sheet.referenceViewerGroup.settings.message = Helpers.SmartTextBox((0, y, -10, 50),
        #         "To move the selected font in the canvas, press command and drag",
        #         blue = 9,
        #         green = .7,
        #         sizeStyle = 12)

        self.parent.sheet.referenceViewerGroup.canvas = CanvasGroup((-295,0,-10,-10), 
                delegate=ProjectCanvas("ReferenceViewer", self))


        ###


        self.parent.sheet.masterGroup.show(1)
        self.parent.sheet.lockerGroup.show(0)
        self.parent.sheet.designFrameGroup.show(0)
        self.parent.sheet.referenceViewerGroup.show(0)

        self.parent.sheet.saveButton = Button((-160,-30, 150, 20), 'Save', callback=self.saveSheet)
        self.parent.sheet.closeButton = Button((-320,-30, 150, 20), 'Close', callback=self.closeSheet)
        self.parent.sheet.setDefaultButton(self.parent.sheet.saveButton)

        self.parent.sheet.open()

    def getPreviewFont(self):
        if self.fontNames:
            self.previewFont = self.parent.RCJKI.projectFonts[self.fontNames[self.selectedFontIndex%len(self.fontNames)]]
            self.selectedFontIndex += 1

    def getPreviewGlyph(self):
        if self.previewFont is None:
            self.previewGlyph = None
            return
        self.previewGlyph = RGlyph()
        self.characterSets = characterSets.sets
        characterSet = ""

        for charset in "".join([d['Basic'] for d in [self.parent.RCJKI.characterSets[key] for key in self.parent.RCJKI.project.script]]):
            characterSet += charset

        glyphNames = [files.unicodeName(c) for c in characterSet if files.unicodeName(c) in self.previewFont.keys() and (len(self.previewFont[files.unicodeName(c)]) != 0 or self.previewFont[files.unicodeName(c)].components != [])]
        self.previewGlyph = None
        if self.previewFont:
            self.previewGlyph = self.previewFont[random.choice(glyphNames)]
    
    # def usersListSelectionCallback(self, sender):
    #     sel = sender.getSelection()
    #     if not sel: return
    #     user = sender.get()[sel[0]]
    #     userLocker = self.parent.RCJKI.collab._addLocker(user)
    #     glyphs = userLocker.glyphs['_DCE_glyphs']
    #     chars = [chr(int(glyph[3:], 16)) for glyph in glyphs]
    #     chars.sort()
    #     self.parent.sheet.lockerGroup.charactersTextEditor.set(''.join(chars))

    # def charactersTextEditorCallback(self, sender):
    #     chars = sender.get()
    #     sel = self.parent.sheet.lockerGroup.usersList.getSelection()
    #     if not sel: return
    #     user = self.parent.sheet.lockerGroup.usersList.get()[sel[0]]
    #     userLocker = self.parent.RCJKI.collab._addLocker(user)
    #     glyphs = ['uni'+files.normalizeUnicode(hex(ord(char))[2:].upper()) for char in chars]
    #     userLocker._setStep("_DCE_glyphs")
    #     userLocker._clearGlyphs()
    #     userLocker._addGlyphs(glyphs)
    #     self.parent.RCJKI.project.usersLockers = self.parent.RCJKI.collab._toDict
        # print(userLocker.__dict__)

    def projectSectionsSegmentedButtonCallback(self, sender):
        sel = sender.get()
        groups = [
            self.parent.sheet.masterGroup,
            self.parent.sheet.lockerGroup,
            self.parent.sheet.designFrameGroup,
            self.parent.sheet.referenceViewerGroup
            ]
        for i, e in enumerate(groups):
            e.show(i == sel)

        self.parent.RCJKI.projectEditorController.updateSheetUI()

    def lockerDesignStepSegmentedButtonCallback(self, sender):
        sel = sender.get()
        groups = [
            self.parent.sheet.lockerGroup.initialDesign,
            # self.parent.sheet.lockerGroup.keysAndExtrems,
            self.parent.sheet.lockerGroup.design,
            self.parent.sheet.lockerGroup.deepComponentEdition,
            self.parent.sheet.lockerGroup.deepComponentInstantiation
            ]
        for i, e in enumerate(groups):
            e.show(i == sel)
        self.parent.RCJKI.projectEditorController.updateSheetUI()

    def projectNameEditTextCallback(self, sender):
        self.parent.RCJKI.project.name = sender.get()

    def closeSheet(self, sender):
        self.parent.sheet.close()

    def saveSheet(self, sender):
        self.parent.RCJKI.projectEditorController.updateProject()

    def importMastersButtonCallback(self, sender):
        getFile(messageText=u"Add new UFO to Project",
                allowsMultipleSelection=True,
                fileTypes=["ufo"],
                parentWindow=self.parent.sheet,
                resultCallback=self.importMastersCallback)

    def importMastersCallback(self, paths):
        for path in paths:
            self.parent.RCJKI.projectEditorController.importFontToProject(path)
        
        self.fontNames = list(self.parent.RCJKI.project.masterFontsPaths.keys())
        self.getFonts()

    def createMastersButtonCallback(self, sender):
        self.nameMasterSheet = Sheet((220, 90), self.parent.sheet)
        self.nameMasterSheet.familyNameEditText = EditText((10, 10, 200, 22), "FamilyName")
        self.nameMasterSheet.styleNameEditText = EditText((10, 32, 200, 22), "StyleName")
        self.nameMasterSheet.CancelButton = Button((10, 60, 100, 20), "Cancel", callback=self.createMasterCancelButtonCallback)
        self.nameMasterSheet.OKButton = Button((110, 60, 100, 20), "OK", callback=self.createMasterOKButtonCallback)
        self.nameMasterSheet.open()

    def createMasterCancelButtonCallback(self, sender):
        self.nameMasterSheet.close()

    def createMasterOKButtonCallback(self, sender):
        familyName = self.nameMasterSheet.familyNameEditText.get()
        styleName = self.nameMasterSheet.styleNameEditText.get()
        self.nameMasterSheet.close()

        self.parent.RCJKI.projectEditorController.createFontToProject(familyName, styleName)
        self.fontNames.append("%s-%s"%(familyName, styleName))
        self.getFonts()

    def removeMastersButtonCallback(self, sender):
        sel = self.parent.sheet.masterGroup.mastersList.getSelection()
        if not sel: return
        rootfolder = os.path.split(self.parent.RCJKI.projectFileLocalPath)[0]
        for s in sel:
            d = self.parent.sheet.masterGroup.mastersList.get()[s]
            e = d['FamilyName']+'-'+d['StyleName']
            oldPath = os.path.join(rootfolder, 'Masters', self.parent.RCJKI.project.masterFontsPaths[e])
            shutil.rmtree(oldPath)
            del self.parent.RCJKI.project.masterFontsPaths[e]
        self.getFonts()

    def mastersListSelectionCallback(self, sender):
        sel = self.parent.sheet.masterGroup.mastersList.getSelection()
        if not sel: return
        s = sel[0]
        d = self.parent.sheet.masterGroup.mastersList.get()[s]
        self.selectedFontName = d['FamilyName'] + '-' + d['StyleName']

    def mastersListEditCallback(self, sender):
        sel = self.parent.sheet.masterGroup.mastersList.getSelection()
        if not sel: return
        col, row = sender.getEditedColumnAndRow()
        if col == -1 or row == -1: return

        familyName = sender.get()[row]['FamilyName']
        styleName = sender.get()[row]['StyleName']
        f = self.parent.RCJKI.projectFonts[self.selectedFontName]
        f.info.familyName = familyName
        f.info.styleName = styleName
        newFontName = familyName + '-' + styleName

        if newFontName not in self.parent.RCJKI.project.masterFontsPaths:
            UFOName = "%s.ufo"%newFontName
            rootfolder = os.path.split(self.parent.RCJKI.projectFileLocalPath)[0]
            savePath = os.path.join(rootfolder, 'Masters', UFOName)
            f.save(savePath)
            oldPath = os.path.join(rootfolder, 'Masters', "%s.ufo"%self.selectedFontName)
            shutil.rmtree(oldPath)
            del self.parent.RCJKI.project.masterFontsPaths[self.selectedFontName]
            self.parent.RCJKI.project.masterFontsPaths[newFontName] = UFOName
            self.parent.RCJKI.projectFonts[newFontName] = f

        self.getFonts()

    def getFonts(self):
        self.parent.RCJKI.projectEditorController.updateSheetUI()
        self.getPreviewFont()
        self.getPreviewGlyph()
        if self.parent.RCJKI.initialDesignController.interface:
            self.parent.RCJKI.initialDesignController.loadProjectFonts()

    # def scriptsRadioGroupCallback(self, sender):
    #     script = self.parent.RCJKI.scriptsList[sender.get()]
    #     self.parent.RCJKI.project.script = script

    def scriptsCheckBoxCallback(self, sender):
        scripts = []
        for script in self.parent.RCJKI.scriptsList:
            if getattr(self.parent.sheet.masterGroup, "%sCheckBox"%script).get():
                scripts.append(script)
        self.parent.RCJKI.project.script = scripts
        if self.parent.RCJKI.initialDesignController.interface:
            self.parent.RCJKI.initialDesignController.setCharacterSet()
        self.getFonts()

        self.parent.sheet.lockerGroup.initialDesign.setScript()
        self.parent.sheet.lockerGroup.design.setScript()
        self.parent.sheet.lockerGroup.deepComponentEdition.setScript()
        # self.getFonts()

        # self.parent.RCJKI.projectEditorController.updateSheetUI()
        # self.getPreviewFont()
        # self.getPreviewGlyph()
        # if self.parent.RCJKI.initialDesignController.interface:
        #     self.parent.RCJKI.initialDesignController.loadProjectFonts()

    ###

    def EM_DimensionX_editText_callback(self, sender):
        try: self.parent.RCJKI.project.settings['designFrame']['em_Dimension'][0] = int(sender.get())        
        except: sender.set(self.parent.RCJKI.project.settings['designFrame']['em_Dimension'][0])
        self.parent.sheet.designFrameGroup.canvas.update()

    def EM_DimensionY_editText_callback(self, sender):
        try: self.parent.RCJKI.project.settings['designFrame']['em_Dimension'][1]= int(sender.get())        
        except: sender.set(self.parent.RCJKI.project.settings['designFrame']['em_Dimension'][1])
        self.parent.sheet.designFrameGroup.canvas.update()

    def characterFace_editText_callback(self, sender):
        try:
            value = int(sender.get())
            if 0 <= value <= 100:
                self.parent.RCJKI.project.settings['designFrame']['characterFace'] = value        
            else:
                sender.set(self.parent.RCJKI.project.settings['designFrame']['characterFace'])
        except: sender.set(self.parent.RCJKI.project.settings['designFrame']['characterFace'])
        self.parent.sheet.designFrameGroup.canvas.update()

    def overshootOutside_editText_callback(self, sender):
        try: self.parent.RCJKI.project.settings['designFrame']['overshoot'][1] = int(sender.get())
        except: sender.set(self.parent.RCJKI.project.settings['designFrame']['overshoot'][1])
        self.parent.sheet.designFrameGroup.canvas.update()

    def overshootInside_editText_callback(self, sender):
        try: self.parent.RCJKI.project.settings['designFrame']['overshoot'][0] = int(sender.get())        
        except: sender.set(self.parent.RCJKI.project.settings['designFrame']['overshoot'][0])
        self.parent.sheet.designFrameGroup.canvas.update()

    def _horizontalLine_slider_callback(self, sender):
        self.parent.RCJKI.project.settings['designFrame']['horizontalLine'] = int(sender.get())
        self.parent.sheet.designFrameGroup.canvas.update()

    def _verticalLine_slider_callback(self, sender):
        self.parent.RCJKI.project.settings['designFrame']['verticalLine'] = int(sender.get())
        self.parent.sheet.designFrameGroup.canvas.update()

    def _customsFrames_list_editCallback(self, sender):
        l = []
        for d in sender.get():
            d2 = {}
            for k, v in d.items():
                d2[k] = v
            l.append(d2)
        self.parent.RCJKI.project.settings['designFrame']['customsFrames'] = l
        self.parent.sheet.designFrameGroup.canvas.update()

    def _addCustomsFrames_button_callback(self, sender):
        name = "Frame%i"%len(self.parent.RCJKI.project.settings['designFrame']['customsFrames'])
        self.parent.RCJKI.project.settings['designFrame']['customsFrames'].append({"Name":name})
        self.parent.sheet.designFrameGroup.customsFrames_list.set(self.parent.RCJKI.project.settings['designFrame']['customsFrames'])
        self.parent.sheet.designFrameGroup.canvas.update()

    def _removeCustomsFrames_button_callback(self, sender):
        sel = self.parent.sheet.designFrameGroup.customsFrames_list.getSelection()
        if not sel: return
        self.parent.RCJKI.project.settings['designFrame']['customsFrames'] = [e for i, e in enumerate(self.parent.RCJKI.project.settings['designFrame']['customsFrames']) if i not in sel]
        self.parent.sheet.designFrameGroup.customsFrames_list.set(self.parent.RCJKI.project.settings['designFrame']['customsFrames'])
        self.parent.sheet.designFrameGroup.canvas.update()

    def changeFontButtonCallBack(self, sender):
        self.getPreviewFont()
        self.getPreviewGlyph()
        self.parent.sheet.designFrameGroup.canvas.getNSView()._delegate.update()

    def changeGlyphButtonCallBack(self, sender):
        self.getPreviewGlyph()
        self.parent.sheet.designFrameGroup.canvas.getNSView()._delegate.update()
    ###

    def _addReferenceFont_button_callback(self, sender):
        font = self.parent.sheet.referenceViewerGroup.FontList_comboBox.get()
        if font is None or font == "": return
        # Default values
        elem = {
            "font": font,
            "size": 400,
            "x": -500,
            "y": 40,
            "color": (0, 0, 0, .56)
        }

        self.parent.RCJKI.project.settings['referenceViewer'].append(elem)
        l = [{"Font": e['font']} for e in self.parent.RCJKI.project.settings['referenceViewer']]
        self.parent.sheet.referenceViewerGroup.reference_list.set(l)
        self.parent.sheet.referenceViewerGroup.reference_list.setSelection([len(self.parent.sheet.referenceViewerGroup.reference_list) - 1])
        self.parent.sheet.referenceViewerGroup.canvas.update()

    def _removeReference_button_callback(self, sender):
        sel = self.parent.sheet.referenceViewerGroup.reference_list.getSelection()
        if sel is None: return

        def remove(l):
            return [e for i, e in enumerate(l) if i not in sel]

        self.parent.RCJKI.project.settings['referenceViewer'] = remove(self.parent.RCJKI.project.settings['referenceViewer'])
        self.parent.sheet.referenceViewerGroup.reference_list.set({"Font": e['font'] for e in self.parent.RCJKI.project.settings['referenceViewer']})

        # self.reference_list.setSelection([len(self.s.referenceViewerList) - 1])
        self.parent.sheet.referenceViewerGroup.canvas.update()

    def _reference_list_selectionCallback(self, sender):
        sel = sender.getSelection()
        if not sel:
            return
        self.parent.sheet.referenceViewerGroup.settings.show(1)
        settings = self.parent.RCJKI.project.settings['referenceViewer'][sel[0]]
        self.parent.sheet.referenceViewerGroup.settings.size_editText.set(settings["size"])
        self.parent.sheet.referenceViewerGroup.settings.size_slider.set(settings["size"])
        colors = settings["color"]
        color = NSColor.colorWithCalibratedRed_green_blue_alpha_(
            colors[0], colors[1], colors[2], colors[3])
        self.parent.sheet.referenceViewerGroup.settings.color_colorWell.set(color)

    def _size_editText_callback(self, sender):
        sel = self.parent.sheet.referenceViewerGroup.reference_list.getSelection()
        if not sel: return
        size = self.parent.RCJKI.project.settings['referenceViewer'][sel[0]]["size"]
        try: 
            size = int(sender.get())
        except: 
            sender.set(size)
        self.parent.RCJKI.project.settings['referenceViewer'][sel[0]]["size"] = size
        self.parent.sheet.referenceViewerGroup.settings.size_slider.set(size)
        self.parent.sheet.referenceViewerGroup.canvas.update()

    def _size_slider_callback(self, sender):
        sel = self.parent.sheet.referenceViewerGroup.reference_list.getSelection()
        if not sel: return
        self.parent.RCJKI.project.settings['referenceViewer'][sel[0]]["size"] = int(sender.get())
        self.parent.sheet.referenceViewerGroup.settings.size_editText.set(self.parent.RCJKI.project.settings['referenceViewer'][sel[0]]["size"])
        self.parent.sheet.referenceViewerGroup.canvas.update()

    def _color_editText_callback(self, sender):
        sel = self.parent.sheet.referenceViewerGroup.reference_list.getSelection()
        if not sel: return
        color = sender.get()
        self.parent.RCJKI.project.settings['referenceViewer'][sel[0]]["color"] = (
            color.redComponent(),
            color.greenComponent(),
            color.blueComponent(),
            color.alphaComponent(),
        )
        self.parent.sheet.referenceViewerGroup.canvas.update()


class ProjectCanvas():
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.scale = .2
        self.translateX = 215
        self.translateY = 505
        self.previewGlyph = self.parent.previewGlyph
        self.rvd = referenceViewDrawer.ReferenceViewerDraw(self.parent.parent.RCJKI)
        self.dfv = designFrameDrawer.DesignFrameDrawer(self.parent.parent.RCJKI)
        canvasWidth = 285
        canvasHeight = 270
        
        if self.name == "ReferenceViewer":
            self.scale = .15
            self.translateX = 600
            self.translateY = 300

        elif self.previewGlyph is not None and len(self.previewGlyph):
            self.translateX = ((canvasWidth/self.scale-self.previewGlyph.width)*.5 )
            self.translateY = ((canvasHeight/self.scale-(self.previewGlyph.bounds[3]-self.previewGlyph.bounds[1]))*.5 )

    def update(self):
        self.previewGlyph = self.parent.previewGlyph
        if self.name == "ReferenceViewer":
            self.parent.parent.sheet.referenceViewerGroup.canvas.update()
        else:
            self.parent.parent.sheet.designFrameGroup.canvas.update()

    def mouseDragged(self, info):
        command = extractNSEvent(info)['commandDown']
        deltaX = info.deltaX()/self.scale
        deltaY = info.deltaY()/self.scale
        if not command:
            self.translateX += deltaX
            self.translateY -= deltaY
        elif self.parent.parent.sheet.referenceViewerGroup.reference_list.getSelection() and self.name == "ReferenceViewer":
            currentSetting = self.parent.parent.RCJKI.project.settings['referenceViewer'][self.parent.parent.sheet.referenceViewerGroup.reference_list.getSelection()[0]]
            currentSetting["x"] += deltaX
            currentSetting["y"] -= deltaY
        self.update()

    def scrollWheel(self, info):
        alt = extractNSEvent(info)['optionDown']
        if not alt: return
        scaleOld = self.scale
        delta = info.deltaY()
        sensibility = .009
        scaleOld += (delta / abs(delta) * sensibility) / self.scale
        minScale = .005
        if scaleOld > minScale:
            self.scale = scaleOld
        self.update()

    def draw(self):
        try:
            scale(self.scale, self.scale)
            translate(self.translateX,self.translateY)
            strokeWidth(.4/self.scale)

            if self.name == "ReferenceViewer":
                save()
                translate(150,550)
                save()
                stroke(0)
                fill(None)
                w = self.parent.parent.RCJKI.project.settings['designFrame']['em_Dimension'][0]
                h = self.parent.parent.RCJKI.project.settings['designFrame']['em_Dimension'][0]
                
                designFrameDrawer.DesignFrameDrawer(self.parent.parent.RCJKI).draw(glyph = self.previewGlyph, scale = self.scale)
                
                restore()

                if self.previewGlyph:
                    if self.previewGlyph.name.startswith("uni"):
                        txt = chr(int(self.previewGlyph.name[3:7],16))
                    elif self.previewGlyph.unicode: 
                        txt = chr(self.previewGlyph.unicode)
                    else:
                        txt = "a"
                else:
                    txt = "a"
                
                self.rvd.draw(txt)
                restore()

            else:
                fill(.3)
                if self.previewGlyph:
                    drawGlyph(self.previewGlyph)
                self.dfv.draw(glyph = self.previewGlyph, scale = self.scale)

        except Exception as e:
            print(e)