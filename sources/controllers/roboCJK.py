from mojo.events import addObserver, removeObserver, extractNSEvent, installTool, uninstallTool
from imp import reload

from utils import interpolation
reload(interpolation)

from views import roboCJKView, sheets
reload(roboCJKView)
reload(sheets)

from resources import characterSets, chars2deepCompo
reload(characterSets)
reload(chars2deepCompo)

charsets = characterSets.characterSets
CG2DC = chars2deepCompo.Chars2DC

from utils import files
reload(files)

from utils import gitEngine as git
reload(git)

from views import drawer
reload(drawer)

from views import canvasGroups
reload(canvasGroups)

from views import popover
reload(popover)

from models import deepComponent
reload(deepComponent)

from tools import transformationTool
reload(transformationTool)

import os
from mojo.UI import UpdateCurrentGlyphView, CurrentGlyphWindow
import mojo.drawingTools as mjdt
from mojo.roboFont import *

import math

from utils import decorators
reload(decorators)
refresh = decorators.refresh
lockedProtect = decorators.lockedProtect

class RoboCJKController(object):

    def __init__(self):
        self.observers = False
        self.drawer = drawer.Drawer(self)
        self.transformationTool = transformationTool.TransformationTool(self)
        # installTool(self.transformationTool)

        self.locked = False

        self.atomicView = canvasGroups.AtomicView(
            self,
            posSize = (20, 0, 300, -20), 
            delegate = self
            )
        self.deepComponentView = canvasGroups.DCCG_View(
            self,
            posSize = (20, 0, 300, -20), 
            delegate = self
            )

        self.characterGlyphView = canvasGroups.DCCG_View(
            self,
            posSize = (20, 0, 300, -20), 
            delegate = self
            )

        self.sliderValue = None
        self.sliderName = None
        self.copy = []
        self.px, self.py = 0,0

    def get(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        return None

    @property
    def isAtomic(self):
        return self.currentGlyph.type == 'atomicElement'

    @property
    def isDeepComponent(self):
        return self.currentGlyph.type == 'deepComponent'

    @property
    def isCharacterGlyph(self):
        return self.currentGlyph.type == 'characterGlyph'
        
    def toggleWindowController(self, add = True):
        windowController = self.roboCJKView.w.getNSWindowController()
        windowController.setShouldCloseDocument_(True)
        document = self.currentFont.shallowDocument()
        if add:
            document.addWindowController_(windowController)
            return
        document.removeWindowController_(windowController)
        
    def _launchInterface(self):
        self.roboCJKView = roboCJKView.RoboCJKView(self)

    def setGitEngine(self):
        global gitEngine
        gitEngine = git.GitEngine(self.projectRoot)
        self.user = gitEngine.user()

    def toggleObservers(self, forceKill=False):
        if self.observers or forceKill:
            removeObserver(self, "fontDidSave")
            removeObserver(self, "glyphAdditionContextualMenuItems")
            # removeObserver(self, "glyphWindowWillOpen")
            removeObserver(self, "glyphWindowWillClose")
            removeObserver(self, "draw")
            removeObserver(self, "drawPreview")
            removeObserver(self, "spaceCenterDraw")
            removeObserver(self, "currentGlyphChanged")
            removeObserver(self, "mouseDown")
            removeObserver(self, "mouseUp")
            removeObserver(self, "keyDown")
            removeObserver(self, "didUndo")
        else:
            addObserver(self, "fontDidSave", "fontDidSave")
            addObserver(self, "glyphAdditionContextualMenuItems", "glyphAdditionContextualMenuItems")
            # addObserver(self, "glyphWindowWillOpen", "glyphWindowWillOpen")
            addObserver(self, "glyphWindowWillClose", "glyphWindowWillClose")
            addObserver(self, "observerDraw", "draw")
            addObserver(self, "observerDrawPreview", "drawPreview")
            addObserver(self, "observerspaceCenterDraw", "spaceCenterDraw")
            addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
            addObserver(self, "mouseDown", "mouseDown")
            addObserver(self, "mouseUp", "mouseUp")
            addObserver(self, "keyDown", "keyDown")
            addObserver(self, "didUndo", "didUndo")
        self.observers = not self.observers

    def fontDidSave(self, info):
        if self.currentFont:
            self.currentFont.save()
        else:
            print('no font object')

    def didUndo(self, info):
        self.updateDeepComponent()

    def observerspaceCenterDraw(self, info):
        _rglyph = info['glyph']
        glyphName = _rglyph.name
        glyph = self.currentFont[glyphName]
        if glyph.type == 'deepComponent':
            preview = glyph.generateDeepComponent(glyph, False)
            mjdt.save()
            for d in preview:
                for a in d.values():
                    mjdt.drawGlyph(a[0])
            mjdt.restore()
        elif glyph.type == 'characterGlyph':
            preview = glyph.generateCharacterGlyph(glyph, False)
            mjdt.save()
            for deepComponent in preview:
                for instance in deepComponent.values():
                    for atomicElement in instance[1]:
                        for AEInstance in atomicElement.values():
                            mjdt.drawGlyph(AEInstance[0])
            mjdt.restore()
        else:
            return

    @refresh
    def updateDeepComponent(self):
        self.currentGlyph.computeDeepComponentsPreview()
        if self.isAtomic: return
        self.currentGlyph.computeDeepComponents()

    def glyphWindowWillClose(self, notification):
        self.window.removeGlyphEditorSubview(self.atomicView)
        self.window.removeGlyphEditorSubview(self.deepComponentView)
        self.window.removeGlyphEditorSubview(self.characterGlyphView)

    @lockedProtect
    def currentGlyphChanged(self, notification):
        glyph = notification['glyph']
        if glyph is None: return
        self.currentGlyph = self.currentFont[glyph.name]
        d = self.currentGlyph._glyphVariations
        self.currentGlyph.sourcesList = [
            {"Axis":axisName, "Layer":layerName, "PreviewValue":0.5} for axisName, layerName in  d.items()
            ]
        self.currentViewSourceList.set(self.currentGlyph.sourcesList)
        if self.currentGlyph.type =='atomicElement':
            uninstallTool(self.transformationTool)
        else:
            installTool(self.transformationTool)
        self.showCanvasGroups()
        self.addSubView()
        self.updateDeepComponent()

    @property 
    def currentViewSourceList(self):
        if self.isAtomic:
            return self.atomicView.atomicElementsList
        elif self.isDeepComponent:
            return self.deepComponentView.sourcesList
        elif self.isCharacterGlyph:
            return self.characterGlyphView.sourcesList
    @property 
    def currentViewSliderList(self):
        if self.isDeepComponent:
            return self.deepComponentView.slidersList
        elif self.isCharacterGlyph:
            return self.characterGlyphView.slidersList

    @refresh
    def addSubView(self):
        self.window = CurrentGlyphWindow()
        if self.window is None: return
        # add the view to the GlyphEditor
        self.showCanvasGroups()
        if self.isAtomic: 
            self.window.addGlyphEditorSubview(self.atomicView)
            self.updateListInterface()
            return
        elif self.isDeepComponent:
            self.window.addGlyphEditorSubview(self.deepComponentView)
            self.deepComponentView.setUI()
            self.updateListInterface()
            return
        elif self.isCharacterGlyph:
            self.window.addGlyphEditorSubview(self.characterGlyphView)
            self.characterGlyphView.setUI()
            self.updateListInterface()
            return

    def showCanvasGroups(self):
        self.atomicView.show(self.isAtomic)
        self.deepComponentView.show(self.isDeepComponent)
        self.characterGlyphView.show(self.isCharacterGlyph)

    def draw(self):
        mjdt.save()
        mjdt.translate(0, 200)
        mjdt.fill(.15)

        def drawGlyph(g):
            mjdt.save()
            mjdt.fill(0)
            mjdt.scale(.15, .15)
            mjdt.translate(150, abs(self.currentFont._RFont.info.descender))
            mjdt.drawGlyph(g)  
            mjdt.restore()

        if self.isAtomic:
            if self.currentGlyph.preview is None: return
            mjdt.save()
            mjdt.scale(.15, .15)
            mjdt.translate(150, abs(self.currentFont._RFont.info.descender))
            mjdt.drawGlyph(self.currentGlyph.preview)  
            mjdt.restore()
        elif self.isDeepComponent:
            mjdt.save()
            mjdt.translate(0, 100)
            for i, d in enumerate(self.currentGlyph.preview):
                for atomicInstanceGlyph in d.values():
                    if atomicInstanceGlyph[0] is None: continue
                    drawGlyph(atomicInstanceGlyph[0])
            mjdt.restore()
        elif self.isCharacterGlyph:
            mjdt.save()
            mjdt.translate(0, 100)
            for i, e in enumerate(self.currentGlyph.preview):
                for dcCoord, l in e.values():
                    for dcAtomicElements in l:
                        for atomicInstanceGlyph, _, _ in dcAtomicElements.values():
                            drawGlyph(atomicInstanceGlyph)

            # for i, atomicInstanceGlyph in self.currentGlyph._getAtomicInstanceGlyph(self.currentGlyph.preview):
            #     if atomicInstanceGlyph[0] is None: continue
            #     drawGlyph(atomicInstanceGlyph[0])
            # for i, e in enumerate(self.currentGlyph.preview):
            #     for dcName, (dcCoord, l) in e.items():
            #         for dcAtomicElements in l:
            #             for atomicInstanceGlyph in dcAtomicElements.values():
            #                 if atomicInstanceGlyph[0] is None: continue
            #                 drawGlyph(atomicInstanceGlyph[0])
            mjdt.restore()
        mjdt.restore()

    def observerDraw(self, notification):
        self.showCanvasGroups()
        if hasattr(self.currentGlyph, 'type'):
            self.drawer.draw(notification)

    def observerDrawPreview(self, notification):
        if self.currentGlyph is None: return
        self.drawer.draw(notification, color=(0, 0, 0, 1))

    @refresh
    def mouseDown(self, point):
        if self.isAtomic:
            return
        event = extractNSEvent(point)
        if not event["shiftDown"]:
            self.currentGlyph.selectedElement = []
        try: self.px, self.py = point['point'].x, point['point'].y
        except: return
        self.currentGlyph.pointIsInside((self.px, self.py), event["shiftDown"])
        self.currentViewSliderList.set([])
        if self.currentGlyph.selectedElement: 
            self.setListWithSelectedElement()

            if point['clickCount'] == 2:
                popover.EditPopoverAlignTool(
                    self, 
                    point['point'], 
                    self.currentGlyph
                    )

    def setListWithSelectedElement(self):
        if self.isDeepComponent:
            element = self.deepComponentView
        elif self.isCharacterGlyph:
            element = self.characterGlyphView

        l = []
        if len(self.currentGlyph.selectedElement) == 1:
            for axisName, value in self.currentGlyph.selectedElementCoord.items():
                l.append({'Axis':axisName, 'PreviewValue':value})
        element.slidersList.set(l)
        self.sliderValue = None

    @refresh
    def mouseUp(self, info):
        if self.isAtomic:
            return
        try: x, y = info['point'].x, info['point'].y
        except: return
        self.currentViewSliderList.set([])
        self.currentGlyph.selectionRectTouch(
            *sorted([x, self.px]), 
            *sorted([y, self.py])
            )
        if self.currentGlyph.selectedElement:
            self.setListWithSelectedElement()
            
    @refresh
    def keyDown(self, info):
        if self.isAtomic:
            return
        event = extractNSEvent(info)
        try:
            character = info["event"].characters()
        except: return
        modifiers = [
            event['shiftDown'] != 0, 
            event['capLockDown'] != 0,
            event['optionDown'] != 0,
            event['controlDown'] != 0,
            event['commandDown'] != 0,
            ]
        arrowX = 0
        arrowY = 0

        if event['down']:
            arrowY = -1
        elif event['up']:
            arrowY = 1
        elif event['left']:
            arrowX = -1
        elif event['right']:
            arrowX = 1
            
        inputKey = [arrowX, arrowY]

        if self.isAtomic: return

        if character == ' ':
            self.currentGlyph.selectedSourceAxis = None
            self.updateDeepComponent()
            self.currentViewSourceList.setSelection([])

        self.currentGlyph.keyDown((modifiers, inputKey, character))

    def opaque(self):
        return False

    def acceptsFirstResponder(self):
        return False

    def acceptsMouseMoved(self):
        return True

    def becomeFirstResponder(self):
        return False

    def resignFirstResponder(self):
        return False

    def shouldDrawBackground(self):
        return False

    def glyphAdditionContextualMenuItems(self, notification):
        menuItems = []
        if self.isAtomic:
            item = ('Attach Layer to Atomic Element', self.addLayerToAtomicElement)
            menuItems.append(item)
        elif self.isDeepComponent:
            item = ('Add Atomic Element', self.addAtomicElement)
            menuItems.append(item)
            if self.currentGlyph.selectedElement:
                item = ('Remove Selected Atomic Element', self.removeAtomicElement)
                menuItems.append(item)
        elif self.isCharacterGlyph:
            item = ('Add Deep Component', self.addDeepComponent)
            menuItems.append(item)
            if self.currentGlyph.selectedElement:
                item = ('Remove Selected Deep Component', self.removeDeepComponent)
                menuItems.append(item)
        notification["additionContextualMenuItems"].extend(menuItems)

    def addAtomicElement(self, sender):
        sheets.SelectAtomicElementSheet(self, self.currentFont.atomicElementSet)

    def addDeepComponent(self, sender):
        sheets.SelectDeepComponentSheet(self, self.currentFont.deepComponentSet)

    def removeAtomicElement(self, sender):
        self.currentGlyph.removeAtomicElement()
        self.updateDeepComponent()

    def removeDeepComponent(self, sender):
        self.currentGlyph.removeDeepComponentAtIndexToGlyph()
        self.updateDeepComponent()
 
    def addLayerToAtomicElement(self, sender):
        availableLayers = [l for l in self.currentGlyph._RGlyph.layers if l.layer.name!='foreground']
        if [l for l in self.currentGlyph._RGlyph.layers if l.name != 'foreground']:
            sheets.SelectLayerSheet(self, availableLayers)

    @lockedProtect
    @refresh
    def updateListInterface(self):
        l = []
        if self.isAtomic:
            for axisName, layerName in self.currentGlyph._glyphVariations.items():
                l.append({"Axis":axisName, "Layer":layerName, "PreviewValue":.5})
            
        elif self.isDeepComponent:
            if self.currentGlyph._glyphVariations:
                l = [{'Axis':axis, 'PreviewValue':0.5} for axis in self.currentGlyph._glyphVariations]
            
        elif self.isCharacterGlyph:
            if self.currentGlyph._glyphVariations:
                l = [{'Axis':axis, 'PreviewValue':0.5} for axis in self.currentGlyph._glyphVariations.keys()]

        self.currentViewSourceList.set(l)
        self.currentGlyph.sourcesList = l

