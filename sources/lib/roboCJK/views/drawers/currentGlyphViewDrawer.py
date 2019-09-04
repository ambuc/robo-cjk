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
from mojo.drawingTools import *
from mojo.roboFont import *
from views.drawers import interpolaviourDrawer, displayOptionsDrawer, referenceViewDrawer, designFrameDrawer, powerRulerDrawer
# from views.DeepComponentDrawer import DeepComponentDrawer
reload(designFrameDrawer)
reload(referenceViewDrawer)
reload(interpolaviourDrawer)
reload(displayOptionsDrawer)
reload(powerRulerDrawer)

class CurrentGlyphViewDrawer():

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        # self.fonts = []
        # for t in self.RCJKI.allFonts:
        #     for _ , f in t.items():
        #         self.fonts.append(f)
        self.dfd = designFrameDrawer.DesignFrameDrawer(self.RCJKI)
        self.rvd = referenceViewDrawer.ReferenceViewerDraw(self.RCJKI)
        self.stackMaster = displayOptionsDrawer.StackMasterDrawer(self.RCJKI)
        self.powerRuler = powerRulerDrawer.PowerRulerDrawer(self.RCJKI)

    def draw(self, info):
        g = self.RCJKI.currentGlyph
        f = self.RCJKI.currentFont
        self.scale = info['scale']
        fill(.2, 0, 1, .5)
        if info['notificationName'] == "drawPreview":
            fill(0, 0, 0, 1)
        # DeepComponentDrawer(self.ui, g, f)
        if self.RCJKI.settings["showDesignFrame"]:
            if not (info['notificationName'] == "drawPreview") or (info['notificationName'] == "drawPreview") == self.RCJKI.settings["designFrame"]["drawPreview"]:
                self.dfd.draw(
                    glyph = g,
                    mainFrames = self.RCJKI.settings['designFrame']['showMainFrames'], 
                    secondLines = self.RCJKI.settings['designFrame']['showSecondLines'], 
                    customsFrames = self.RCJKI.settings['designFrame']['showCustomsFrames'], 
                    proximityPoints = self.RCJKI.settings['designFrame']['showproximityPoints'],
                    translate_secondLine_X = self.RCJKI.settings['designFrame']['translate_secondLine_X'], 
                    translate_secondLine_Y = self.RCJKI.settings['designFrame']['translate_secondLine_Y'],
                    scale = self.scale
                    )
            
        if self.RCJKI.settings["referenceViewer"]["onOff"]:
            if g.name.startswith("uni"):
                char = chr(int(g.name[3:7],16))
            elif g.unicode: 
                char = chr(g.unicode)
            else:
                char = ""
            if not (info['notificationName'] == "drawPreview") or (info['notificationName'] == "drawPreview") == self.RCJKI.settings["referenceViewer"]["drawPreview"]:
                self.rvd.draw(char) 

        if self.RCJKI.settings["stackMasters"]:
            self.stackMaster.draw(g, preview = info['notificationName'] == "drawPreview")

        self.powerRuler.draw(self.scale)

        if self.RCJKI.inspectorController.interface is not None:
            self.RCJKI.inspectorController.setProperties()
            