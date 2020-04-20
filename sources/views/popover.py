"""
Copyright 2020 Black Foundry.

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
from mojo.events import getActiveEventTool
from vanilla import *
from AppKit import NSColor, NSNoBorder, NumberFormatter
import copy
from utils import decorators
reload(decorators)
glyphTransformUndo = decorators.glyphTransformUndo

transparentColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 1, 0)
numberFormatter = NumberFormatter()

def makeEmptyPopover(size, pos, view):
    p = Popover(size)
    if not hasattr(p, "_bindings"):
        p._bindings = {}
    offsetX, offsetY = view.offset()
    return (p, (pos.x+offsetX, pos.y+offsetY))

class EditPopover(object):
    def __init__(self, size, point):
        eventTool = getActiveEventTool()
        p,v = makeEmptyPopover(size, point, eventTool.getNSView())
        p.controller = self
        self._popover = p
        self._viewPos = v

    @property
    def relativeRect(self):
        x,y = self._viewPos
        return (x-2, y-2, 4, 4)

    @property
    def popover(self):
        return self._popover

    def close(self):
        self.popover.close()

    def open(self):
        self.popover.open(
            parentView=getActiveEventTool().getNSView(), 
            relativeRect=self.relativeRect
            )

def editTextAesthetic(element):
    element.getNSTextField().setBordered_(False)
    element.getNSTextField().setDrawsBackground_(False)
    element.getNSTextField().setFocusRingType_(1)

def buttonAsthetic(element):
    element.getNSButton().setFocusRingType_(1)
    element.getNSButton().setBackgroundColor_(transparentColor)
    element.getNSButton().setBordered_(False)

def tryfunc(func):
    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
            self.RCJKI.updateDeepComponent()
        except:
            pass
    return wrapper

def resetDict(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        lib = self.getLib()
        lib[self.glyph.selectedElement[0]] = self.infos
    return wrapper


class EditPopoverAlignTool(EditPopover):

    def __init__(self, RCJKI, point, glyph):
        super(EditPopoverAlignTool, self).__init__((170,190), point)
        self.RCJKI = RCJKI
        self.glyph = glyph

        lib = self.getLib()
        self.infos = lib[self.glyph.selectedElement[0]]

        y = 10
        if self.infos.get("name"):
            self.popover.Title = TextBox(
                (5, y, -5, 20), 
                self.infos["name"], 
                sizeStyle = "small", 
                alignment = 'center'
                )
            y += 25
        self.popover.xTextBox = TextBox(
            (10, y, 20, 20), 
            "x:", 
            sizeStyle = "mini"
            )
        self.popover.xEditText = EditText(
            (30, y, 30, 20), 
            self.infos["x"], 
            sizeStyle = "mini",
            callback = self.xCallback
            )
        editTextAesthetic(self.popover.xEditText)

        self.popover.scalexTextBox = TextBox(
            (70, y, 20, 20), 
            "↔:", 
            sizeStyle = "mini"
            )
        self.popover.scalexEditText = EditText(
            (90, y, 30, 20), 
            self.infos["scalex"]*1000, 
            sizeStyle = "mini",
            formatter = numberFormatter, 
            callback = self.scalexCallback
            )
        editTextAesthetic(self.popover.scalexEditText)

        self.popover.rotationTextBox = TextBox(
            (120, y, 20, 20), 
            "⟳:", 
            sizeStyle = "mini"
            )

        self.popover.rotationEditText = EditText(
            (140, y, 30, 20), 
            self.infos["rotation"], 
            sizeStyle = "mini",
            callback = self.rotationCallback
            )
        editTextAesthetic(self.popover.rotationEditText)
        y += 20
        self.popover.yTextBox = TextBox(
            (10, y, 20, 20), 
            "y:", 
            sizeStyle = "mini"
            )
        self.popover.yEditText = EditText(
            (30, y, 30, 20), 
            self.infos["y"], 
            sizeStyle = "mini",
            callback = self.yCallback
            )
        editTextAesthetic(self.popover.yEditText)

        self.popover.scaleyTextBox = TextBox(
            (70, y, 20, 20), 
            "↕:", 
            sizeStyle = "mini"
            )
        self.popover.scaleyEditText = EditText(
            (90, y, 30, 20), 
            self.infos["scaley"]*1000, 
            sizeStyle = "mini",
            formatter = numberFormatter, 
            callback = self.scaleyCallback
            )

        editTextAesthetic(self.popover.scaleyEditText)

        y+=20

        self.popover.coord = List(
            (10,y, -10, -30),
            [dict(layer = k, value = v) for k, v in self.infos["coord"].items()],
            columnDescriptions = [
                {"title": "layer", "editable" : False},
                {"title": "value"},
                ],
            showColumnTitles=False,
            allowsMultipleSelection=False,
            editCallback = self.coordEditCallback,
            rowHeight=17.0,
            drawFocusRing = False
            )
        tableView = self.popover.coord.getNSTableView()
        tableView.setUsesAlternatingRowBackgroundColors_(False)
        tableView.setBackgroundColor_(transparentColor)
        scrollView = self.popover.coord.getNSScrollView()
        scrollView.setDrawsBackground_(False)
        scrollView.setBorderType_(NSNoBorder)

        self.popover.copy = SquareButton(
            (10, -30, 75, -10),
            "copy",
            callback = self.copyCallback,
            sizeStyle = "small"
            )
        buttonAsthetic(self.popover.copy)

        self.popover.paste = SquareButton(
            (85, -30, 75, -10),
            "paste",
            callback = self.pasteCallback,
            sizeStyle = "small"
            )
        buttonAsthetic(self.popover.paste)

        self.open()

    def getLib(self):
        if self.RCJKI.isDeepComponent and self.glyph.computedAtomicInstances:
            return self.RCJKI.currentGlyph._atomicElements
            
        elif self.RCJKI.isDeepComponent and self.glyph.computedAtomicSelectedSourceInstances:
            return self.RCJKI.currentGlyph._glyphVariations[self.glyph.selectedSourceAxis]
            
        if self.RCJKI.isCharacterGlyph and self.glyph.computedDeepComponents:
            return self.RCJKI.currentGlyph._deepComponents
            
        elif self.RCJKI.isCharacterGlyph and self.glyph.computedDeepComponentsVariation:
            return self.RCJKI.currentGlyph._glyphVariations[self.glyph.selectedSourceAxis]

    def copyCallback(self, sender):
        self.RCJKI.copy = [self.sourceAxis, copy.deepcopy(self.infos)]

    @property
    def sourceAxis(self):
        if self.glyph.selectedSourceAxis is not None:
            return self.glyph.selectedSourceAxis
        return "Foreground"

    @tryfunc
    @resetDict
    def pasteCallback(self, sender):
        source, c = copy.deepcopy(self.RCJKI.copy)
        self.infos["scalex"] = c["scalex"]
        self.infos["scaley"] = c["scaley"]
        self.infos["rotation"] = c["rotation"]
        if source != self.sourceAxis:
            self.infos["x"] = c["x"]
            self.infos["y"] = c["y"]
            self.infos["coord"] = c["coord"]
        if self.infos.get("name") == c.get("name"):
            self.infos["coord"] = c["coord"]

    @tryfunc
    @resetDict
    @glyphTransformUndo
    def xCallback(self, sender):
        self.infos["x"] = int(sender.get())
        
    @tryfunc
    @resetDict
    @glyphTransformUndo
    def yCallback(self, sender):
        self.infos["y"] = int(sender.get())

    @tryfunc
    @resetDict
    @glyphTransformUndo
    def scalexCallback(self, sender):
        self.infos["scalex"] = int(sender.get()) / 1000

    @tryfunc
    @resetDict
    @glyphTransformUndo
    def scaleyCallback(self, sender):
        self.infos["scaley"] = int(sender.get()) / 1000

    @tryfunc
    @resetDict
    @glyphTransformUndo
    def rotationCallback(self, sender):
        self.infos["rotation"] = float(sender.get())

    @tryfunc
    @resetDict
    @glyphTransformUndo
    def coordEditCallback(self, sender):
        sel = sender.getSelection()
        if not sel: return
        d = {e["layer"]:float(str(e["value"]).replace(',','.')) for e in sender.get()}
        self.infos["coord"] = d
