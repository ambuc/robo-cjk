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
from views import deepComponentInstantiationView
import os
from utils import files
from utils import git
from mojo.roboFont import *
from mojo.UI import PostBannerNotification
from AppKit import *
from resources import deepCompoMasters_AGB1_FULL
from resources import deepCompo2Chars
from resources import chars2deepCompo
from utils import interpolations

reload(deepComponentInstantiationView)
reload(deepCompoMasters_AGB1_FULL)
reload(deepCompo2Chars)
reload(chars2deepCompo)
reload(interpolations)

class DeepComponentInstantiationController(object):

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.interface = None
        self.characterSet = None
        self.fontsList = []

        self.RCJKI.char2DC = {}
        

        """
        MASTER FONTS
        MASTER DEEP COMPONENTS FONTS (with all dc keys)

        MINI UNICODE DEEP COMPONENTS FONTS (with unicode characters from locker list, and associated extrems versions) -> KeyAndExtremeCharacters
        MINI DEEP COMPONENTS FONTS (with DCNamed glyphs from locker list) -> DeepComponentsGlyphs -> only these glyphs will be injected back

        """

    def char2DC(self):
        # c2dc = {}
        # for dc, chars in deepCompo2Chars.DC2Chars[self.script].items():
        #     for char in chars:
        #         if char not in c2dc:
        #             c2dc[char] = []
        #         # if dc in c2dc[char]: continue
        #         c2dc[char].append(dc)
        self.RCJKI.char2DC = chars2deepCompo.Chars2DC[self.script]
        # print(deepCompo2Chars.DC2Chars[self.script])

    def launchDeepComponentInstantiationInterface(self):
        self.setCharacterSet()
        if not self.interface:
            self.RCJKI.resetController()
            self.interface = deepComponentInstantiationView.DeepComponentInstantiationWindow(self)
            self.loadProjectFonts()
            self.RCJKI.designStep = '_deepComponentsInstantiation_glyphs'

        self.char2DC()

    @property    
    def script(self):
        return self.RCJKI.collab._userLocker(self.RCJKI.user).script

    def setCharacterSet(self):
        # script = self.RCJKI.collab._userLocker(self.RCJKI.user).script
        # self.characterSet = "".join(self.RCJKI.characterSets[script]['DeepComponentKeys'])
        self.characterSet = ""
        self.characterSet += "".join([k for k in self.RCJKI.characterSets[self.script]['Basic'] if k not in self.characterSet])
        self.characterSet += "".join([chr(int(k[3:],16)) for k in self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs['_deepComponentsInstantiation_glyphs'] if k not in self.characterSet])
        # print(self.characterSet)
        # print(self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs['_deepComponentsInstantiation_glyphs'])
        # print(self.characterSet, deepCompoMasters_AGB1_FULL.Hanzi)

    def getDCVariant(self, selectedKey, dcFont):
        selectedKeyCode = files.normalizeUnicode(hex(ord(selectedKey))[2:].upper())
        DCV = list(filter(lambda n: selectedKeyCode in n.split('_'), dcFont.keys()))
        return [dict(Char = chr(int(n.split("_")[1],16)), Name = n) for n in sorted(DCV)]

    def getFrozenDC(self):
        tempFDC = NewFont(showUI = False)
        DCGlyphsList = []
        for FDC, layersInfos in self.interface.selectedDeepComponentGlyph.lib["DeepComponents"].items():
            tempFDC.newGlyph(FDC)
            tempFDC[FDC].appendGlyph(interpolations.deepolation(RGlyph(), self.interface.selectedDeepComponentGlyph, layersInfos))
            tempFDC[FDC].width = self.RCJKI.project.settings['designFrame']['em_Dimension'][0]
            DCGlyphsList.append(tempFDC[FDC])

        self.interface.w.frozenDCGroup.frozenDCList.set(DCGlyphsList)

    def getSlidersInfos(self, layerName, value):
        g = self.interface.selectedDeepComponentGlyph.getLayer(layerName)
        emDimensions = self.RCJKI.project.settings['designFrame']['em_Dimension']
        pdfData = self.RCJKI.getLayerPDFImage(g, emDimensions)

        d = {'Layer': layerName,
            'Image': NSImage.alloc().initWithData_(pdfData),
            'Values': value,
            # 'NLI': 'NLI'
            }
        return d

    def setSlider(self):
        self.RCJKI.layersInfos = {}
        self.interface.slidersValuesList = []

        layers = [l.name for l in list(filter(lambda l: len(self.interface.selectedDeepComponentGlyph.getLayer(l.name)), self.RCJKI.fonts2DCFonts[self.RCJKI.currentFont].layers))]
        for layerName in layers:
            if layerName == "foreground": continue
            value = 0

            self.interface.slidersValuesList.append(self.getSlidersInfos(layerName, value))
            self.RCJKI.layersInfos[layerName] = value

    def setCurrentGlyphLib(self):
        if "DeepComponentsInfos" not in self.RCJKI.currentGlyph.lib:
            self.RCJKI.currentGlyph.lib["DeepComponentsInfos"]=[]
            for e in self.interface.currentGlyphComposition:
                name = e["Name"]
                char = e["Char"]
                dcFont = self.RCJKI.fonts2DCFonts[self.RCJKI.currentFont]
                # print(self.controller.getDCVariant(char, dcFont))
                self.RCJKI.currentGlyph.lib["DeepComponentsInfos"].append(
                    dict(
                        DeepComponentName = self.getDCVariant(char, dcFont)[0]["Name"],
                        DeepComponentInstance = {}
                        )
                    # {self.controller.getDCVariant(char, dcFont)[0]["Name"]:{}}
                    )

    def updateGlyphSetList(self):
        l = []
        if self.RCJKI.currentFont is not None:
            later = []
            for c in self.characterSet:
                name = files.unicodeName(c)
                code = c
                sequence = ({
                            '#':'', 
                            'Char':code, 
                            'Name':name, 
                            'MarkColor':''
                            })
                if name in self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs['_deepComponentsInstantiation_glyphs']:
                    l.append(sequence)
                else:
                    later.append(sequence)
            l += later
        self.interface.w.glyphSetList.set(l)


    def getDeepComponentsInstances(self):
        instances = []
        """
        [{'DeepComponentName': 'DC_8279_00', 'DeepComponentInstance': {'Name': 'DC_05', 'offset': (0, 0)}}, {'DeepComponentName': 'DC_79BE_00', 'DeepComponentInstance': {}}, {'DeepComponentName': 'DC_722B_00', 'DeepComponentInstance': {}}, {'DeepComponentName': 'DC_5189_00', 'DeepComponentInstance': {}}]
        """
        # print(self.RCJKI.currentGlyph.lib['DeepComponentsInfos'])
        if self.RCJKI.currentGlyph is not None:
            for dc in self.RCJKI.currentGlyph.lib['DeepComponentsInfos']:
                dci = dc["DeepComponentInstance"]
                name = dc["DeepComponentName"]
                # print("--------------")
                if not "Name" in dci: 
                    instances.append(RGlyph())
                else:
                    dcGlyph = self.RCJKI.fonts2DCFonts[self.RCJKI.currentFont][name]
                    layersInfos = dcGlyph.lib["DeepComponents"][dci["Name"]]
                    # print(dcGlyph.lib["DeepComponents"][dci["Name"]])
                    # print("--------------\n")
                    DCG = interpolations.deepolation(RGlyph(), 
                            dcGlyph.getLayer("foreground"), 
                            # self.pathsGlyphs, 
                            layersInfos)
                    x, y = dci["offset"]
                    DCG.moveBy((x, y))
                    instances.append(DCG)
        # for DC in self.RCJKI.currentGlyph.lib['DeepComponentsInfos']:
        #     # name = "uni"
        #     name = DC["DeepComponentName"]
        #     print(self.RCJKI.fonts2DCFonts[self.RCJKI.currentFont][name].lib["DeepComponents"])
        # print(instances)
        self.RCJKI.DeepComponentsInstances = instances

        # return instances


    def saveSubsetFonts(self):
        for f in self.RCJKI.fonts2DCFonts.values():
            f.save()
        for font in self.RCJKI.allFonts:
            for f in font.values():
                f.save()
            
        PostBannerNotification("Fonts saved", "")

    def pushDCMasters(self):
        # return
        # print(self.RCJKI.currentGlyph.lib['DeepComponentsInfos'], '\n')
        lockedGlyphsList = self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs['_deepComponentsInstantiation_glyphs']
        DeepCompoNames = set()
        for name in lockedGlyphsList:
            glyph = self.RCJKI.currentFont[name]
            DeepCompoInfos = self.RCJKI.currentFont[name].lib.get("DeepComponentsInfos", [])
            for e in DeepCompoInfos:
                DeepCompoNames.add(e["DeepComponentName"])
        print(DeepCompoNames)

        # rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
        # gitEngine = git.GitEngine(rootfolder)
        # gitEngine.pull()

        # script = self.RCJKI.collab._userLocker(self.RCJKI.user).script
        # DCMasterPaths = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'DeepComponents', script)

        # for DCMasterPath in os.listdir(DCMasterPaths):
        #     if not DCMasterPath.endswith('.ufo'): continue

        #     DCM = OpenFont(os.path.join(DCMasterPaths, DCMasterPath), showInterface = False)
        #     for font in list(self.RCJKI.fonts2DCFonts.values()):
        #         if font.path.split("/")[-1] == DCMasterPath:
        #             DCG = font

        #     fontLayers = lambda font: [l.name for l in font.layers]

        #     reservedGlyphs = self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs["_deepComponentsInstantiation_glyphs"]
        #     lockedGlyphs = self.RCJKI.collab._userLocker(self.RCJKI.user)._allOtherLockedGlyphs["_deepComponentsInstantiation_glyphs"]

        #     self.merge(reservedGlyphs, DCG, DCM, fontLayers(DCG))
        #     self.merge(lockedGlyphs, DCM, DCG, fontLayers(DCM))

        #     DCM.save()
        #     DCM.close()
        #     DCG.save()
            
        # stamp = "Masters Fonts Saved"
        # gitEngine.commit(stamp)
        # gitEngine.push()
        # PostBannerNotification('Git Push', stamp)

    # def injectGlyphsBack(self, glyphs, user):
    #     self.RCJKI.injectGlyphsBack(glyphs, user)
    #     self.RCJKI.saveProjectFonts()

    
    # def pullDCMasters(self):
    #     rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
    #     gitEngine = git.GitEngine(rootfolder)
    #     gitEngine.pull()

    #     script = self.RCJKI.collab._userLocker(self.RCJKI.user).script
    #     DCMasterPaths = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'DeepComponents', script)

    #     for DCMasterPath in os.listdir(DCMasterPaths):
    #         if not DCMasterPath.endswith('.ufo'): continue

    #         DCM = OpenFont(os.path.join(DCMasterPaths, DCMasterPath), showInterface = False)
    #         for font in list(self.RCJKI.fonts2DCFonts.values()):
    #             if font.path.split("/")[-1] == DCMasterPath:
    #                 DCG = font

    #         DCMLayers = [l.name for l in DCM.layers]
    #         lockedGlyphs = self.RCJKI.collab._userLocker(self.RCJKI.user)._allOtherLockedGlyphs["_deepComponentsEdition_glyphs"]

    #         self.merge(lockedGlyphs, DCM, DCG, DCMLayers)

    # def merge(self, glyphs, font1, font2, fontlayers):
    #     for name in glyphs:
    #         glyphset = list(filter(lambda g: name[3:] in g.name, font1))
    #         for g in glyphset:
    #             font2.insertGlyph(font1[g.name])
    #             for layer in fontlayers:
    #                 if len(font1[g.name].getLayer(layer)):
    #                     font2.getLayer(layer).insertGlyph(font1[g.name].getLayer(layer))

    # def pushDCMasters(self):
    #     rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
    #     gitEngine = git.GitEngine(rootfolder)
    #     gitEngine.pull()

    #     script = self.RCJKI.collab._userLocker(self.RCJKI.user).script
    #     DCMasterPaths = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'DeepComponents', script)

    #     for DCMasterPath in os.listdir(DCMasterPaths):
    #         if not DCMasterPath.endswith('.ufo'): continue

    #         DCM = OpenFont(os.path.join(DCMasterPaths, DCMasterPath), showInterface = False)
    #         for font in list(self.RCJKI.fonts2DCFonts.values()):
    #             if font.path.split("/")[-1] == DCMasterPath:
    #                 DCG = font

    #         fontLayers = lambda font: [l.name for l in font.layers]

    #         reservedGlyphs = self.RCJKI.collab._userLocker(self.RCJKI.user).glyphs["_deepComponentsEdition_glyphs"]
    #         lockedGlyphs = self.RCJKI.collab._userLocker(self.RCJKI.user)._allOtherLockedGlyphs["_deepComponentsEdition_glyphs"]

    #         self.merge(reservedGlyphs, DCG, DCM, fontLayers(DCG))
    #         self.merge(lockedGlyphs, DCM, DCG, fontLayers(DCM))

    #         DCM.save()
    #         DCM.close()
    #         DCG.save()
            
    #     stamp = "Masters Fonts Saved"
    #     gitEngine.commit(stamp)
    #     gitEngine.push()
    #     PostBannerNotification('Git Push', stamp)

    def loadProjectFonts(self):
        self.fontsList = []
        # self.RCJKI.allFonts = []
        self.RCJKI.fonts2DCFonts = {}
        self.RCJKI.DCFonts2Fonts = {}
        # print(self.RCJKI.collab._userLocker(self.RCJKI.user).script)

        script = self.RCJKI.collab._userLocker(self.RCJKI.user).script
        for name, file in self.RCJKI.project.masterFontsPaths.items():

            path = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Masters', file)

            Masterspath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Masters', file)
            # DCpath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'DeepComponents', script, file)

            deepComponentGlyphsSubsetSavepath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Temp', 'DeepComponents', script, "DeepComponentsGlyphs", file)
            deepComponentGlyphsMasterSavepath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'DeepComponents', script, file)

            f = OpenFont(path, showInterface=False)

            #### MASTER DEEP COMPONENTS FONT -> DeepComponents/*script*/*.ufo
            if not os.path.isdir(deepComponentGlyphsMasterSavepath):
                files.makepath(deepComponentGlyphsMasterSavepath)

                masterDeepComponentsGlyphs = NewFont(familyName=f.info.familyName, styleName=f.info.styleName, showInterface=False)

                for i in range(30):
                    masterDeepComponentsGlyphs.newLayer(str(i))

                masterDCFonts = "".join([self.RCJKI.characterSets[key]['DeepComponentKeys'] for key in self.RCJKI.project.script])
                for masterDCFont in masterDCFonts:
                    glyphName = "DC_"+files.normalizeUnicode(hex(ord(masterDCFont))[2:].upper())

                    for script in self.RCJKI.project.script:
                        if masterDCFont in deepCompoMasters_AGB1_FULL.deepCompoMasters[script]:
                            for i in range(len(deepCompoMasters_AGB1_FULL.deepCompoMasters[script][masterDCFont])):
                                gname = glyphName + "_%s"%str(i).zfill(2)
                                masterDeepComponentsGlyphs.newGlyph(gname)
                                masterDeepComponentsGlyphs[gname].width = self.RCJKI.project.settings['designFrame']['em_Dimension'][0]
                for glyph in masterDeepComponentsGlyphs:
                    for i in range(30):
                        masterDeepComponentsGlyphs.getLayer(str(i)).insertGlyph(glyph)
                        masterDeepComponentsGlyphs.getLayer(str(i))[glyph.name].width = self.RCJKI.project.settings['designFrame']['em_Dimension'][0]

                masterDeepComponentsGlyphs.save(deepComponentGlyphsMasterSavepath)
            else:
                masterDeepComponentsGlyphs = OpenFont(deepComponentGlyphsMasterSavepath, showInterface = False)

            #### KEYS AND EXTREMES CHARACTERS -> Temp/DeepComponents/Edition/*script*/KeyAndExtremeCharacters/*.ufo

            MastersFont = OpenFont(Masterspath, showInterface=False)

            self.RCJKI.allFonts.append({name:MastersFont})
            self.fontsList.append(name)

            #### DEEP COMPONENTS GLYPHS -> Temp/DeepComponents/Edition/*script*/DeepComponentsGlyphs/*.ufo
            if not os.path.isdir(deepComponentGlyphsSubsetSavepath):
                files.makepath(deepComponentGlyphsSubsetSavepath)

                deepComponentsGlyphs = OpenFont(deepComponentGlyphsMasterSavepath, showInterface = False)
                deepComponentsGlyphs.save(deepComponentGlyphsSubsetSavepath)

            else:
                deepComponentsGlyphs = OpenFont(deepComponentGlyphsSubsetSavepath, showInterface=False)

            self.RCJKI.fonts2DCFonts[MastersFont] = deepComponentsGlyphs
            self.RCJKI.DCFonts2Fonts[deepComponentsGlyphs] = MastersFont

            f.close()
            masterDeepComponentsGlyphs.close()

        if self.interface:
            self.interface.w.fontsList.set(self.fontsList)

