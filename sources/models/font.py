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
from fontTools.ufoLib.glifLib import readGlyphFromString
from xml.etree import ElementTree as ET
from mojo.roboFont import *
import json
import os
import copy

from imp import reload
from utils import decorators, files, locker
# reload(decorators)
# reload(locker)
gitCoverage = decorators.gitCoverage
from utils import interpolation
# reload(interpolation)
from models import atomicElement, deepComponent, characterGlyph
# reload(atomicElement)
# reload(deepComponent)
# reload(characterGlyph)


class Font():

    def __init__(self, fontPath, gitUserName, gitPassword, gitHostLocker, gitHostLockerPassword, privateLocker):
        self.fontPath = fontPath
        
        self.locker = locker.Locker(fontPath, gitUserName, gitPassword, gitHostLocker, gitHostLockerPassword, privateLocker)
        name = os.path.split(fontPath)[1].split('.')[0]
        self._RFont = NewFont(
            familyName=name, 
            styleName='Regular', 
            showUI = False
            )
        fontFilePath = '{}.ufo'.format(os.path.join(fontPath, name))
        self._RFont.save(fontFilePath)
        self._glyphs = {}

        if 'fontLib.json' in os.listdir(self.fontPath):
            libPath = os.path.join(self.fontPath, 'fontLib.json')
            with open(libPath, 'r') as file:
                f = json.load(file)
            for k, v in f.items():
                self._RFont.lib[k] = v

        self.defaultGlyphWidth = self._RFont.lib.get("rorocjk.defaultGlyphWidth", 1000)

        self.getGlyphs()
        self.createLayersFromVariationAxis()

    def __iter__(self):
        for name in self._RFont.keys():
            yield self[name]

    def __getitem__(self, name):
        return self._glyphs[self._RFont[name]]

    def __len__(self):
        return len(self._RFont)

    def __contains__(self, name):
        return name in self._RFont

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<RCJKFontObject '%s',  path='%s', %s atomicElements, %s deepComponents, %s characterGlyphs>"%(self.fontPath.split("/")[-1], self.fontPath, len(self.atomicElementSet), len(self.deepComponentSet), len(self.characterGlyphSet))

    def keys(self):
        return self._RFont.keys()

    def glyphSet(self):
        return self.atomicElementSet + self.deepComponentSet + self.characterGlyphSet

    def shallowDocument(self):
        return self._RFont.shallowDocument()

    @property
    def _fontLayers(self):
        return [l.name for l in self._RFont.layers if l.name != 'foreground']

    @property
    def currentState(self):
        AE_empty = 0
        AE_maxName = ""
        AE_maxNumber = 0
        AE_averageVariation = []
        for n in self.atomicElementSet:
            glyph = self[n]
            if len(glyph._glyphVariations) > AE_maxNumber:
                AE_maxNumber = len(glyph._glyphVariations)
                AE_maxName = n
            if glyph._glyphVariations:
                AE_averageVariation.append(len(glyph._glyphVariations))
            if not len(glyph):
                AE_empty += 1
        DC_empty = 0
        DC_designed = 0
        DC_designedUnique = set()
        DC_designedVariant = 0
        DC_maxName = ""
        DC_maxNumber = 0
        DC_averageVariation = []
        for n in self.deepComponentSet:
            glyph = self[n]
            if not glyph._deepComponents:
                DC_empty += 1
            else:
                DC_designedVariant += 1
                DC_designedUnique.add(n.split("_")[1])
            if len(glyph._glyphVariations) > DC_maxNumber:
                DC_maxNumber = len(glyph.glyphVariations)
                DC_maxName = n
            if glyph._glyphVariations:
                DC_averageVariation.append(len(glyph._glyphVariations))

        CG_withDC = 0
        CG_withOutlines = 0
        CG_mixed = 0
        CG_withVariation = 0
        CG_withoutVariation = 0
        CG_withVariationanddeepcomponents = 0
        CG_empty = 0
        for n in self.characterGlyphSet:
            glyph = self[n]
            if glyph._deepComponents:
                CG_withDC += 1
            if len(glyph):
                CG_withOutlines += 1
            if glyph._deepComponents and len(glyph):
                CG_mixed += 1
            if glyph._glyphVariations:
                CG_withVariation += 1
            if glyph._glyphVariations and glyph._deepComponents and not len(glyph):
                CG_withVariationanddeepcomponents += 1
            else:
                CG_withoutVariation += 1
            if not glyph._deepComponents and not len(glyph):
                CG_empty += 1
        string = f"""
        Current state of {self.fontPath.split('/')[-1]}:\n
          • AtomicElements :
            \t - {AE_empty} are empty,
            \t - maximum of glyph variation: '{AE_maxName}' with {AE_maxNumber} axis,
            \t - average of glyph variation: {round(sum(AE_averageVariation)/len(AE_averageVariation), 2)} axis,
            \t - total: {len(self.atomicElementSet)} atomicElements,\n
          • DeepComponents :
            \t - {len(DC_designedUnique)} unique designed,
            \t - {DC_designedVariant} designed (with variants),
            \t - {DC_empty} are empty,
            \t - maximum of glyph variation: '{DC_maxName}' with {DC_maxNumber} axis,
            \t - average of glyph variation: {round(sum(DC_averageVariation)/len(DC_averageVariation), 2)} axis,
            \t - total: {len(self.deepComponentSet)} deepComponents,\n
          • CharacterGlyphs :
            \t - {CG_withDC} with deep components,
            \t - {CG_withOutlines} with outlines,
            \t - {CG_mixed} are mixed,
            \t - {CG_withVariation} with glyph variation,
            \t - {CG_withVariationanddeepcomponents} with glyph variation and deep components,
            \t - {CG_withoutVariation} without glyph variation,
            \t - {CG_empty} are empty,
            \t - total: {len(self.characterGlyphSet)} characterGlyphs,\n
        """
        return string

    def createLayersFromVariationAxis(self):
        if not self._RFont.lib.get('robocjk.fontVariations', ""): return
        for variation in self._RFont.lib['robocjk.fontVariations']:
            if variation not in [x.name for x in self._RFont.layers]:
                self._RFont.newLayer(variation)

    def getGlyph(self, glyph):
        fileName = files.userNameToFileName(glyph.name)
        if glyph.type == "deepComponent":
            self.addGlyph(
                deepComponent.DeepComponent(glyph.name), 
                fileName, 
                "foreground"
                )
        elif glyph.type == "characterGlyph":
            self.addGlyph(
                characterGlyph.CharacterGlyph(glyph.name), 
                fileName, 
                "foreground"
                )
        elif glyph.type == "atomicElement":
            self.addGlyph(
                atomicElement.AtomicElement(glyph.name), 
                fileName, 
                "foreground"
                )
            # print("getglyph")

        if glyph.type in ["atomicElement", "characterGlyph"]:
            layerNames = glyph._glyphVariations.layerNames
            path = os.path.join(self.fontPath, glyph.type)
            for layerName in layerNames:
                layerPath = os.path.join(path, layerName)

                if layerName not in self._fontLayers:
                    self._RFont.newLayer(layerName)

                paths = os.listdir(layerPath)
                for glifFile in filter(lambda x: x.endswith(".glif"), paths):
                    layerfileName = glifFile.split('.glif')[0]
                    if glyph.type == "atomicElement":
                        self.addGlyph(
                            atomicElement.AtomicElement(glyph.name), 
                            layerfileName, 
                            layerName
                            )
                    else:
                        self.addGlyph(
                            characterGlyph.CharacterGlyph(glyph.name), 
                            layerfileName, 
                            layerName
                            )

    def getGlyphs(self):
        for glyphName in self.deepComponentSet:
            fileName = files.userNameToFileName(glyphName)
            self.addGlyph(
                deepComponent.DeepComponent(glyphName), 
                fileName, 
                "foreground"
                )
            # self[glyphName].save()
            # self[glyphName]._RGlyph.lib.clear()
            # self[glyphName]._RGlyph.lib.update(self[glyphName].lib)

        for glyphName in self.characterGlyphSet:
            fileName = files.userNameToFileName(glyphName)
            self.addGlyph(
                characterGlyph.CharacterGlyph(glyphName), 
                fileName, 
                "foreground"
                )
            # self[glyphName].save()
            # self[glyphName]._RGlyph.lib.clear()
            # self[glyphName]._RGlyph.lib.update(self[glyphName].lib)

        for glyphName in self.atomicElementSet:
            fileName = files.userNameToFileName(glyphName)
            self.addGlyph(
                atomicElement.AtomicElement(glyphName), 
                fileName, 
                "foreground"
                )
            # self[glyphName].save()
            # self[glyphName]._RGlyph.lib.clear()
            # self[glyphName]._RGlyph.lib.update(self[glyphName].lib)
        # paths = [os.path.join(self.fontPath, 'atomicElement'), os.path.join(self.fontPath, 'characterGlyph')]
        glyphtypes = ["atomicElement", "characterGlyph"]
        for glyphtype in glyphtypes:
            path = os.path.join(self.fontPath, glyphtype)
            for layerPath in [f.path for f in os.scandir(path) if f.is_dir()]:
                layerName = os.path.split(layerPath)[1]
                if layerName not in self._fontLayers:
                    self._RFont.newLayer(layerName)

                for glifFile in filter(lambda x: x.endswith(".glif"), os.listdir(layerPath)):
                    layerfileName = glifFile.split('.glif')[0]
                    if glyphtype == "atomicElement":
                        self.addGlyph(
                            atomicElement.AtomicElement(glyphName), 
                            layerfileName, 
                            layerName
                            )
                    else:
                        self.addGlyph(
                            characterGlyph.CharacterGlyph(glyphName), 
                            layerfileName, 
                            layerName
                            )
        # self.save()

    def newGLIF(self, glyphType, glyphName):
        if glyphType == 'atomicElement':
            emptyGlyph = atomicElement.AtomicElement(glyphName)

        elif glyphType == 'deepComponent':
            emptyGlyph = deepComponent.DeepComponent(glyphName)
            
        elif glyphType == 'characterGlyph':
            emptyGlyph = characterGlyph.CharacterGlyph(glyphName)
        
        emptyGlyph.name = glyphName
        txt = emptyGlyph.dumpToGLIF()
        fileName = files.userNameToFileName(glyphName)
        path = os.path.join(self.fontPath, glyphType, "%s.glif"%fileName)
        files.makepath(path)
        with open(path, "w", encoding = "utf-8") as file:
            file.write(txt)
        return (emptyGlyph, fileName)

    def duplicateGLIF(self, glyphName, glyphNamePath, newGlyphName, newGlyphNamePath):
        fileName = files.userNameToFileName(glyphName)

        tree = copy.deepcopy(ET.parse(glyphNamePath))
        root = tree.getroot()
        root.set("name", newGlyphName)
        string = ET.tostring(root).decode("utf-8")

        newFileName = files.userNameToFileName(newGlyphName)

        tree.write(open(newGlyphNamePath, "w"), encoding = 'unicode')
        # with open(newGlyphNamePath, "w") as file:
        #     file.write(string)

    def addGlyph(self, glyph, fileName, layerName):
        if layerName == 'foreground':
            glifPath = os.path.join(self.fontPath, glyph.type, "%s.glif"%fileName)
        else:
            glifPath = os.path.join(self.fontPath, glyph.type, layerName, "%s.glif"%fileName)
        tree = ET.parse(glifPath)
        root = tree.getroot()
        # print("addglyph")
        self.insertGlyph(glyph, ET.tostring(root), layerName)
        # print("insertglyph")
        self[glyph.name].save()
        self[glyph.name]._RGlyph.lib.clear()
        self[glyph.name]._RGlyph.lib.update(self[glyph.name].lib)
        # print("addglyph done")

    def insertGlyph(self, glyph, string, layerName):  
        if glyph is None: return
        glyph.setParent(self)
        pen = glyph.naked().getPointPen()
        readGlyphFromString(string, glyph.naked(), pen)
        layer = self._RFont.getLayer(layerName)
        layer.insertGlyph(glyph)
        self._glyphs[layer[glyph.name]] = glyph
        glyph._initWithLib()

    @property
    def atomicElementSet(self):
        return self._returnGlyphsList('atomicElement')

    @property
    def deepComponentSet(self):
        return self._returnGlyphsList('deepComponent')

    @property
    def characterGlyphSet(self):
        return self._returnGlyphsList('characterGlyph')

    def _returnGlyphsList(self, glyphType):
        if self.fontPath is None: return []
        l = []
        files.makepath(os.path.join(self.fontPath, glyphType, 'folder.proofer'))
        listDir = os.listdir(os.path.join(self.fontPath, glyphType))
        for glifFile in filter(lambda x: x.endswith(".glif"), listDir):
            glifPath = os.path.join(self.fontPath, glyphType, glifFile)
            tree = ET.parse(glifPath)
            root = tree.getroot()
            glyphName = root.get('name')
            l.append(glyphName)
        return sorted(l)

    def newGlyph(self, glyphType, glyphName = "newGlyph"):
        self.addGlyph(*self.newGLIF(glyphType, glyphName), "foreground")

    @gitCoverage(msg = 'duplicate Glyph')
    def duplicateGlyph(self, glyphName:str, newGlyphName:str):
        glyphType = self[glyphName].type

        filename = files.userNameToFileName(glyphName)
        newFileName = files.userNameToFileName(newGlyphName)

        glyphPath = os.path.join(self.fontPath, glyphType, "%s.glif"%filename)
        newGlyphPath = os.path.join(self.fontPath, glyphType, "%s.glif"%newFileName)

        if glyphType == "deepComponent":
            new_glyph = deepComponent.DeepComponent(newGlyphName)
        elif glyphType == "atomicElement":
            new_glyph = atomicElement.AtomicElement(newGlyphName)
        elif glyphType == "characterGlyph":
            new_glyph = characterGlyph.CharacterGlyph(newGlyphName)

        self.duplicateGLIF(glyphName, glyphPath, newGlyphName, newGlyphPath)
        self.addGlyph(new_glyph, newFileName, "foreground")

        for _, layers, _ in os.walk(os.path.join(self.fontPath, glyphType)):
            for layer in layers:
                layerDirectory = os.path.join(self.fontPath, glyphType, layer)
                if "%s.glif"%filename in os.listdir(layerDirectory) and "%s.glif"%newFileName not in os.listdir(layerDirectory):
                    layerGlyphPath = os.path.join(layerDirectory, "%s.glif"%filename)
                    newLayerGlyphPath = os.path.join(layerDirectory, "%s.glif"%newFileName)

                    self.duplicateGLIF(glyphName, layerGlyphPath, newGlyphName, newLayerGlyphPath)
                    self.addGlyph(new_glyph, newFileName, layer)

        self.getGlyph(self[newGlyphName])

    @gitCoverage(msg = 'remove Glyph')
    def removeGlyph(self, glyphName:str): 
        # return
        fileName = "%s.glif"%files.userNameToFileName(glyphName)
        glyph = self[glyphName]
        glyphType = glyph.type
        if fileName in os.listdir(os.path.join(self.fontPath, glyphType)):
            path = os.path.join(self.fontPath, glyphType, fileName)
            os.remove(path)
            folderPath = os.path.join(self.fontPath, glyphType)
            for _, layers, _ in os.walk(folderPath):
                for layer in layers:
                    if fileName in os.listdir(os.path.join(folderPath, layer)):
                        layerPath = os.path.join(folderPath, layer, fileName)
                        os.remove(layerPath)

        self._RFont.removeGlyph(glyphName)
        for layer in self._RFont.layers:
            if glyphName in layer.keys():
                layer.removeGlyph(glyphName) 
        self.locker.removeFiles([glyphName])        

    @gitCoverage(msg = 'font save')
    def save(self):
        self._RFont.save()
    
        libPath = os.path.join(self.fontPath, 'fontLib.json')
        with open(libPath, "w") as file:
            lib = self._RFont.lib.asDict()
            del lib["public.glyphOrder"]
            file.write(json.dumps(lib,
                indent=4, separators=(',', ': ')))

        for rglyph in self._RFont.getLayer('foreground'):
            if not self.locker.userHasLock(rglyph): continue
            glyph = self[rglyph.name]
            glyph.save()
            glyphType = glyph.type
            rglyph = glyph._RGlyph
            rglyph.lib.update(glyph.lib)
            txt = rglyph.dumpToGLIF()
            fileName = "%s.glif"%files.userNameToFileName(glyph.name)
            path = os.path.join(self.fontPath, glyphType, fileName)

            with open(path, "w", encoding = "utf-8") as file:
                file.write(txt)

            for layerName in self._fontLayers:
                f = self._RFont.getLayer(layerName)
                if glyph.name in f:
                    # layerglyph = self._glyphs[f[glyph.name]]
                    layerglyph = f[glyph.name]
                    # layerglyph.save()
                    txt = layerglyph.dumpToGLIF()
                    fileName = "%s.glif"%files.userNameToFileName(layerglyph.name)
                    path = os.path.join(self.fontPath, glyphType, layerName, fileName)
                    files.makepath(path)
                    with open(path, "w", encoding = "utf-8") as file:
                        file.write(txt)

        self._hanziExportUFO()

    def _hanziExportUFO(self):
        return
        font = NewFont(familyName = "hanzi", styleName = "Regular", showUI = False)
        for rglyph in self._RFont.getLayer('foreground'):
            glyph = self[rglyph.name]
            glyph.save()
            glyphType = glyph.type
            rglyph = glyph._RGlyph
            rglyph.lib.update(glyph.lib)
            font.insertGlyph(rglyph)

            for layerName in self._fontLayers:
                f = self._RFont.getLayer(layerName)
                font.newLayer(layerName)
                if glyph.name in f:
                    layerglyph = f[glyph.name]
                    layer = font.getLayer(layerName)
                    layer.insertGlyph(f[glyph.name])

        font.save(os.path.join(self.fontPath, "hanziUFO.ufo"))

    def renameGlyph(self, oldName, newName):
        if not self.locker.userHasLock(self[oldName]): return False
        self.save()
        print(oldName,newName)
        f = self._RFont.getLayer('foreground')
        if newName in f.keys(): return False
        self[oldName].name = newName
        f[oldName].name = newName
        glyph = f[newName]
        txt = glyph.dumpToGLIF()
        fileName = "%s.glif"%files.userNameToFileName(glyph.name)
        oldFileName = "%s.glif"%files.userNameToFileName(oldName)
        glyphType = self[glyph.name].type
        newPath = os.path.join(self.fontPath, glyphType, fileName)
        oldPath = os.path.join(self.fontPath, glyphType, oldFileName)

        if glyphType == "atomicElement":
            for n in self.deepComponentSet:
                dcg = self[n]
                for ae in dcg._deepComponents:
                    if ae.name == oldName:
                        ae.name = newName
            
        elif glyphType == "deepComponent":
            for n in self.characterGlyphSet:
                dcg = self[n]
                for ae in dcg._deepComponents:
                    if ae.name == oldName:
                        ae.name = newName
 
        with open(newPath, "w", encoding = "utf-8") as file:
            file.write(txt)
        os.remove(oldPath)
        for layerName in self._fontLayers:
            f = self._RFont.getLayer(layerName)
            if oldName not in f: continue
            f[oldName].name = newName
            glyph = f[newName]
            newPath = os.path.join(self.fontPath, glyphType, layerName, fileName)
            oldPath = os.path.join(self.fontPath, glyphType, layerName, oldFileName)
            with open(newPath, "w", encoding = "utf-8") as file:
                file.write(txt)
            os.remove(oldPath)

        self.locker.changeLockName(oldName, newName)
        return True
