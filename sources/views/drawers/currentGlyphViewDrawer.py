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
        self.stackMaster = displayOptionsDrawer.StackMasterDrawer(self.RCJKI, self)
        self.powerRuler = powerRulerDrawer.PowerRulerDrawer(self.RCJKI)

    def draw(self, info):
        g = self.RCJKI.currentGlyph
        f = self.RCJKI.currentFont
        self.scale = info['scale']
        fill(.2, 0, 1, .5)
        if info['notificationName'] == "drawPreview":
            fill(0, 0, 0, 1)
        # DeepComponentDrawer(self.ui, g, f)

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

        if self.RCJKI.activeNLI:
            # if g.name in self.RCJKI.pathsGlyphs:
            layers = []
            start = g.getLayer('foreground')
            for end in g.layers:
                endName = end.layerName
                if endName == 'foreground': continue
                if len(end) == 0: continue
                if not "NLIPoints" in end.lib: continue
                layers.append(end)


            for ci, c in enumerate(g):
                for pi, p in enumerate(c.points):
                    # for layer in layers:
                    nli = g.lib["NLIPoints"]

                    for pn in nli[ci][pi]:
                        save()
                        fill(1, 0, 0, 1)
                        stroke(None)
                        oval(pn[0]-5, pn[1]-5, 10, 10)
                        restore()

                    save()
                    fill(None)
                    stroke(1, 0, 0, 1)
                    newPath()
                    moveTo((start[ci].points[pi].x, start[ci].points[pi].y))
                    curveTo(nli[ci][pi][0], nli[ci][pi][1], (p.x, p.y))
                    drawPath()
                    restore()



            # pathsGlyph = self.RCJKI.pathsGlyphs[g.name]
            # if 'paths_'+g.layerName in pathsGlyph:
            #     pathGlyph = pathsGlyph['paths_'+g.layerName]
            #     save()
            #     for c in pathGlyph:
            #         newPath()
            #         moveTo((c[0][0].x, c[0][0].y))
            #         for s in c:
            #             lineTo((s[0].x, s[0].y))
            #             for p in s:
            #                 lineTo((p.x, p.y))
            #                 if p.type =='offcurve':
            #                     save()
            #                     fill(1, 0, 0, 1)
            #                     stroke(None)
            #                     oval(p.x-5, p.y-5, 10, 10)
            #                     restore()
            #         save()
            #         fill(None)
            #         stroke(1, 0, 0, .3)     
            #         drawPath()
            #         restore()
            #     save()
            #     fill(None)
            #     stroke(1, 0, 0, 1)
            #     drawGlyph(pathGlyph)
            #     restore()
            #     restore()

        if self.RCJKI.designStep == '_deepComponentsEdition_glyphs':
            if self.RCJKI.deepComponentGlyph:
                save()
                fill(0, 0, .8, .15)
                translate(self.RCJKI.deepComponentEditionController.interface.deepComponentTranslateX, self.RCJKI.deepComponentEditionController.interface.deepComponentTranslateY)
                drawGlyph(self.RCJKI.deepComponentGlyph)
                restore()
            else:
                save()
                fill(.95, .15, .4, .8)
                drawGlyph(g)  
                restore()
        else:
            save()
            fill(None)
            drawGlyph(g)  
            restore()
            
        
        self.powerRuler.draw(self.scale)

        if self.RCJKI.inspectorController.interface is not None:
            self.RCJKI.inspectorController.setProperties()
            