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
from fontTools.ufoLib.glifLib import readGlyphFromString, writeGlyphToString
from fontTools.pens.recordingPen import RecordingPen
from mojo.roboFont import *
from imp import reload
from models import glyph, component
from utils import interpolation, decorators
reload(decorators)
reload(interpolation)
reload(glyph)
reload(component)
glyphUndo = decorators.glyphUndo
import copy
Glyph = glyph.Glyph
DictClass = component.DictClass
VariationGlyphs = component.VariationGlyphs

# Deprecated key 
glyphVariationsKey = 'robocjk.atomicElement.glyphVariations'

# Actual key
variationGlyphsKey = 'robocjk.variationGlyphs'

# class LayerInfo(DictClass):

#     def __init__(self, layerName:str, minValue:int = 0, maxValue:int = 1, content = []):
#         super().__init__()
#         self.layerName = layerName
#         self.minValue = minValue
#         self.maxValue = maxValue
#         self.content = []

#     def writeContent(self, glyph):
#         pen = RecordingPen()
#         glyph.draw(pen)
#         self.content = pen.value

#     def __str__(self):
#         return str(self.layerName)

#     def __repr__(self):
#         return str(self)

#     def _toDict(self):
#         return {x:getattr(self, x) for x in vars(self)}

# class GlyphVariations(DictClass):
    
#     def __init__(self, **kwargs):
#         super().__init__()
#         for k, v in kwargs.items():
#             if isinstance(v, str):
#                 setattr(self, k, LayerInfo(v))
#             else:
#                 setattr(self, k, LayerInfo(**v))

#     def addAxis(self, axisName: str, layerName: str):
#         """
#         Add new axis 
#         """
#         if isinstance(layerName, str):
#             setattr(self, axisName, LayerInfo(layerName))
#         else:
#             setattr(self, axisName, LayerInfo(**layerName))

#     def removeAxis(self, axisName: str):
#         """
#         Remove a variation axis
#         """
#         if not hasattr(self, axisName):
#             return
#         delattr(self, axisName)
        
#     @property
#     def axes(self):
#         return self.keys()
        
#     @property
#     def layers(self):
#         return self.values()

#     def _toDict(self):
#         return {x:getattr(self, x)._toDict() for x in vars(self)}

class AtomicElement(Glyph):
    def __init__(self, name):
        super().__init__()
        self._glyphVariations = VariationGlyphs()
        self.name = name
        self.type = "atomicElement"
        self.save()

    @property
    def foreground(self):
        return self.currentFont._RFont[self.name].getLayer('foreground')
    
    @property
    def glyphVariations(self):
        return self._glyphVariations
    
    def _initWithLib(self):
        if variationGlyphsKey not in self._RGlyph.lib.keys():
            self._glyphVariations = VariationGlyphs(dict(self._RGlyph.lib[glyphVariationsKey]))
        else:
            self._glyphVariations = VariationGlyphs(dict(self._RGlyph.lib[variationGlyphsKey]))

    def addGlyphVariation(self, newAxisName, newLayerName):
        self._glyphVariations.addAxis(newAxisName, layerName = newLayerName)

        glyph = AtomicElement(self.name)
        txt = self.currentFont._RFont.getLayer(newLayerName)[self.name].dumpToGLIF()
        self.currentFont.insertGlyph(glyph, txt, newLayerName)

        ################ DEPENDENCY WITH DEEPCOMPONENTS ################
        #                             |                                #
        #                             V                                #
        ################################################################

        # for name in self.currentFont.deepComponentSet:
        #     g = self.currentFont[name]
        #     g.addVariationAxisToAtomicElementNamed(newAxisName, self.name)

    def removeGlyphVariation(self, axisName):
        self._glyphVariations.removeAxis(axisName)

        ################ DEPENDENCY WITH DEEPCOMPONENTS ################
        #                             |                                #
        #                             V                                #
        ################################################################

        # for name in self.currentFont.deepComponentSet:
        #     g = self.currentFont[name]
        #     g.removeVariationAxisToAtomicElementNamed(axisName, self.name)

    def computeDeepComponentsPreview(self):
        layersInfos = {}
        for d in self.sourcesList:
            # layer = str(self._glyphVariations[d['Axis']])
            layer = self._glyphVariations[d['Axis']].layerName
            value = d['PreviewValue']
            # print("----")
            # print(layer, type(layer))
            # print(self._glyphVariations[d['Axis']], type(self._glyphVariations[d['Axis']]))
            # print("----")
            # try:
            layersInfos[layer] = value
            # except:
            #     print("I'm here")
            #     layersInfos[layer["layerName"]] = value
        self.preview = interpolation.deepolation(
            RGlyph(), 
            self.foreground, 
            layersInfos
            )

    def save(self):
        self.lib.clear()
        lib = RLib()
        
        for variations in self._glyphVariations.values():
            layersNames = [x.name for x in self.getParent()._RFont.layers]
            if variations.layerName not in layersNames:
                continue
            variations.writeOutlines(self.currentFont._RFont.getLayer(variations.layerName)[self.name])
    
        lib[glyphVariationsKey] = self._glyphVariations.getDict()
        lib[variationGlyphsKey] = self._glyphVariations.getDict()

        self.lib.update(lib)