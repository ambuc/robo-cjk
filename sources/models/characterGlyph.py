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
from mojo.roboFont import *
from imp import reload
from models import glyph, component, glyphPreview
# reload(glyph)
# reload(component)
# reload(glyphPreview)
from utils import interpolation, decorators
# reload(interpolation)
Glyph = glyph.Glyph
glyphAddRemoveUndo = decorators.glyphAddRemoveUndo
from models import deepComponent
# reload(deepComponent)

DeepComponentNamed = component.DeepComponentNamed
DeepComponents = component.DeepComponents
Axes = component.Axes
VariationGlyphs = component.VariationGlyphs

import copy

# Deprecated keys
# deepComponentsKeyOld = 'robocjk.characterGlyph.deepComponents'
glyphVariationsKey = 'robocjk.fontVariationGlyphs'

# Actual keys
deepComponentsKey = 'robocjk.deepComponents'
axesKey = 'robocjk.axes'
variationGlyphsKey = 'robocjk.variationGlyphs'

class CharacterGlyph(Glyph):
    def __init__(self, name):
        super().__init__()
        self._deepComponents = DeepComponents()
        self._axes = Axes()
        self._glyphVariations = VariationGlyphs()
        self.selectedSourceAxis = None
        self.computedDeepComponents = []
        self.computedDeepComponentsVariation = []
        self.selectedElement = []
        self.name = name
        self.type = "characterGlyph"
        self.outlinesPreview = None
        self.preview = glyphPreview.CharacterGlyphPreview(self)

        # lib = RLib()
        # lib[deepComponentsKey] = copy.deepcopy(self._deepComponents)
        # lib[glyphVariationsKey] = copy.deepcopy(self._glyphVariations)
        # self.stackUndo_lib = [lib]
        # self.indexStackUndo_lib = 0
        self._setStackUndo()
        self.save()

    @property
    def foreground(self):
        return self._RFont[self.name].getLayer('foreground')

    @property
    def deepComponents(self):
        return self._deepComponents

    @property
    def glyphVariations(self):
        return self._glyphVariations

    def _initWithLib(self, lib=None):
        try:
            if lib:
                if variationGlyphsKey not in lib.keys():
                    deepComponents = lib[deepComponentsKey]
                    variationGlyphs = lib[glyphVariationsKey]
                else:
                    deepComponents = lib[deepComponentsKey]
                    variationGlyphs = lib[variationGlyphsKey]
                axes = lib.get(axesKey)
            else:
                if variationGlyphsKey not in self._RGlyph.lib.keys(): 
                    deepComponents = self._RGlyph.lib[deepComponentsKey]
                    variationGlyphs = self._RGlyph.lib[glyphVariationsKey]
                else:
                    deepComponents = self._RGlyph.lib[deepComponentsKey]
                    variationGlyphs = self._RGlyph.lib[variationGlyphsKey]
                axes = self._RGlyph.lib.get(axesKey)
            if axes:
                self._deepComponents = DeepComponents(deepComponents)
                self._axes = Axes(axes)
                self._glyphVariations = VariationGlyphs(variationGlyphs)
            else:
                self._deepComponents = DeepComponents(deepComponents)
                self._axes = Axes()      
                self._axes._init_with_old_format(variationGlyphs)
                self._glyphVariations = VariationGlyphs()
                self._glyphVariations._init_with_old_format(variationGlyphs)

            # if glyphVariationsKey in lib:
            #     del lib[glyphVariationsKey]
            # if glyphVariationsKey in self._RGlyph.lib:
            #     del self._RGlyph.lib[glyphVariationsKey]
        except:
            self._deepComponents = DeepComponents()
            self._axes = Axes()   
            self._glyphVariations = VariationGlyphs()

    def duplicateSelectedElements(self):
        for selectedElement in self._getSelectedElement():
            if selectedElement.get("name"):
                self.addDeepComponentNamed(selectedElement["name"], copy.deepcopy(selectedElement))

    def updateDeepComponentCoord(self, nameAxis, value):
        try:
            if self.selectedSourceAxis is not None:
                self._glyphVariations[self.selectedSourceAxis][self.selectedElement[0]].coord[nameAxis] = value
            else:
                self._deepComponents[self.selectedElement[0]].coord[nameAxis]=value
        except: pass

    def removeVariationAxis(self, name):
        self._glyphVariations.removeAxis(name)

    @glyphAddRemoveUndo
    def addDeepComponentNamed(self, deepComponentName, items = False):
        if not items:
            d = DeepComponentNamed(deepComponentName)
            for axis in self.currentFont[deepComponentName]._glyphVariations.axes:
                d.coord.add(axis, self.currentFont[deepComponentName]._glyphVariations[axis].minValue)
        else:
            d = items
            d.name = deepComponentName

        self._deepComponents.addDeepComponent(d)
        self._glyphVariations.addDeepComponent(d)

        self.preview.computeDeepComponentsPreview(update = False)
        self.preview.computeDeepComponents(update = False)

        # font = self.getParent()
        # glyph = font[self.name]
        # font.writeGlif(glyph)


    def addCharacterGlyphNamedVariationToGlyph(self, name):
        if name in self._glyphVariations.axes: return
        self._glyphVariations.addAxis(name, self._deepComponents)

    @glyphAddRemoveUndo
    def removeDeepComponentAtIndexToGlyph(self):
        if not self.selectedElement: return
        self.removeDeepComponents(self.selectedElement)
        self.selectedElement = []

    def save(self):
        color = self.markColor
        self.lib.clear()
        lib = RLib()

        # for axis, variations in self._glyphVariations.items():
        #     variations.layerName = axis
        #     try:
        #         axisGlyph = self._RFont.getLayer(variations.layerName)[self.name]
        #         variations.writeOutlines(axisGlyph)
        #         variations.setAxisWidth(axisGlyph.width)
        #     except:
        #         pass

        # lib[deepComponentsKeyOld] = self._deepComponents.getList()
        # lib[glyphVariationsKey] = self._glyphVariations.getDict()

        lib[deepComponentsKey] = self._deepComponents.getList()
        lib[axesKey] = self._axes.getList()
        lib[variationGlyphsKey] = self._glyphVariations.getDict()

        # del lib[glyphVariationsKey]
        self.lib.update(lib)
        self.markColor = color