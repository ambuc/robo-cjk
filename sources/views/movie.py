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
      
import math
import random
import string
import sys
import os
import functools
from fontParts.world import *
from fontParts.base import BaseGlyph
from fontTools.pens.cocoaPen import CocoaPen
from fontTools.ufoLib.pointPen import PointToSegmentPen
from pathlib import Path
from xml.etree import ElementTree as ET
from utils import files
try:
    import drawBot as db
except:
    print("DrawBot for robofont is not installed. PDF proofer need it, please install:\nhttps://github.com/typemytype/drawBotRoboFontExtension")
    pass

from imp import reload
import copy
   
class Movie:

    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        ufo = self.RCJKI.currentFont
    # ufo = RCJKFont('/Users/jeremiehornus/Documents/GIT/TYPE/gscjkrcjk/Hanzi.rcjk')
        gname = self.RCJKI.currentGlyph.name
        gnames = [gname]

        for gname in gnames:
            glyph = ufo[gname]
            self._glyphAtomicElements = glyph._deepComponents
            self._glyphVariations = glyph._glyphVariations
            # _glyphAtomicElements = list(ufo._RFont[gname].lib['robocjk.deepComponent.atomicElements'])
            # _glyphVariations =  dict(ufo._RFont[gname].lib['robocjk.deepComponent.glyphVariations'])

            axes = [axis for axis in self._glyphVariations]
            # for layer in ufo.layers:
            #     if gname in layer and layer.name not in ['foreground', 'mask']:
            #         axes.append(layer.name)
            # axes = keepCompatibleLayers(ufo[gname], axes)
            self.makeInstance(axes, gname)
                 
        #saveImage('deepcompo.gif', imageResolution=144)
        outputPath = os.path.join(self.RCJKI.currentFont.fontPath, "Proofing", '%s.mp4'%gname)
        files.makepath(outputPath)
        # outputPath = '/Users/gaetanbaehr/Documents/BlackFoundry/%s.mp4'%gname
        db.saveImage(outputPath, imageResolution=144)

    def checkEqual(self, l):
        for i, e in enumerate(l):
            for e2 in l[i+1:]:
                if e == e2: return True
        return False

    def gcd(self, a,b):
        while b:
            a,b = b, a%b
        return a

    def lcm(self, a,b):
        return a*b // self.gcd(a,b)
        
    def lcm(self, a, b):
        "Lowest common multiple"
        import math as m
        return a * b // m.gcd(a, b)

    def ilcm(self, a):
        "Iterated lowest common multiple"
        import functools as f
        return f.reduce(self.lcm, a, 1)

    def lengtha(self, a):
        return(math.sqrt(a[0]*a[0]+a[1]*a[1]))
        
    # def normalize(self, a):
    #     l = self.lengtha(a)
    #     if l == 0:
    #         l = .0000001
    #     return([a[0]/l, a[1]/l])
        
    # def _drawGlyph(self, glyph):
    #     pen = CocoaPen(glyph.getParent())
    #     glyph.draw(pen)
    #     db.drawPath(pen.path)

    def makeInstance(self, axes, gname):
        nbAxes = maxNbAxes = len(axes)
        # steps = [1, 2]
        # maxNbAxes = max(steps)
        # for nbAxes in steps:

        speeds = [min(16, int(10/nbAxes + random.random()*60/nbAxes)) for i in range(nbAxes)]
        LCM = self.ilcm(speeds)
        while ((LCM < 300 or LCM > 1200) or self.checkEqual(speeds)):
            speeds = [int(10/nbAxes + random.random()*60/nbAxes) for i in range(nbAxes)]
            LCM = self.ilcm(speeds)
            print(speeds, LCM, (LCM < 300 or LCM > 1200))
     
        alpha = 2*math.pi/maxNbAxes
        db.newDrawing()
        for g in range(LCM):

            #for axeIndex, nbAxes in enumerate(steps):

                # for start, framestep in framesteps: 
                #     count = 0 
            # for g in range(framestep):

            H = 700
            W = 700
            db.newPage(W*2, H)
            db.frameDuration(1/30)

            db.fill(1)
            db.rect(0, 0, W*2, H)

            r = W/3
            ainc = 0
            lines = []
            rands = []
            values = []
            for i in range(nbAxes):
                path = db.BezierPath()
                path.moveTo((H/2, W/2))
                line = (r*math.sin(ainc), r*math.cos(ainc))
                path.lineTo((H/2+line[0], W/2+line[1]))
                dx = line[0]*.05
                dy = line[1]*.05
                path.moveTo((H/2+line[0]-dy, W/2+line[1]+dx))
                path.lineTo((H/2+line[0]+dy, W/2+line[1]-dx))
                db.stroke(.2)
                db.strokeWidth(1.5)
                db.fill(None)
                db.drawPath(path)
                ainc += alpha
                lines.append((line,axes[i]))
                # v = getValueForAxeAtFrame(i, g, nbAxes, LCM, speeds[i])
                # values.append(v)
                rands.append([500+500*math.sin(2*math.pi*(speeds[i]*c/LCM + speeds[i])) for c in range(LCM)])
                
            db.fill(1)
            db.oval(H/2-H*.01, W/2-W*.01, H*.02, W*.02)

            patharea = db.BezierPath()
            patharea.moveTo((H/2, W/2))
            patharea.lineTo((H/2+lines[0][0][0]*rands[0][g]/1000, W/2+lines[0][0][1]*rands[0][g]/1000))
            db.fill(0, 0, 0, .1)
            db.stroke(None)
            for c, (line, lineName) in enumerate(lines):
                patharea.lineTo((H/2+line[0]*rands[c][g]/1000, W/2+line[1]*rands[c][g]/1000))
            patharea.lineTo((H/2+lines[0][0][0]*rands[0][g]/1000, W/2+lines[0][0][1]*rands[0][g]/1000))
            patharea.lineTo((H/2, W/2))
            db.drawPath(patharea)

            for c, (line, lineName) in enumerate(lines):
                db.fill(0) #1-rands[c]
                db.stroke(.2)
                db.strokeWidth(1)
                db.oval(H/2+line[0]*rands[c][g]/1000-4.5, W/2+line[1]*rands[c][g]/1000-4.5, 9, 9)
                db.fill(.2)
                ftxt = db.FormattedString(txt=lineName, font="GrtskTera-Light", fontSize=14, align="center")
                db.textBox(ftxt, (H/2+line[0]*1.3-30, W/2+line[1]*1.3-10, 60, 20))


            db.save()
            ld = []
            for j, l in enumerate(axes):
                ld.append({'Axis': l, 'PreviewValue':rands[j][g]/1000})
                
            # d = {l:rands[j][g]/1000 for (j, l) in enumerate(axes)}

            # glyph = deepolation(NewFont().newGlyph('temp'), ufo[gname], layersInfo = d)
            glyph = self.RCJKI.currentFont[gname]
            glyph.preview.computeDeepComponentsPreview(ld)
            # print(glyph)
            db.translate(W*1.15, H*.15)
            db.scale(.7*H/1000)
            db.stroke(.5)
            db.fill(None)
            db.rect(0, 0, 1000, 1000)
            db.fill(0)
            db.stroke(None)
            db.save()
            db.translate(0, 120)

            db.drawGlyph(glyph.preview.variationPreview)
    #         for aes in glyph.preview:
    #             # axis2layerName = {axisName:layerName for axisName, layerName in self.RCJKI.currentFont[aes['name']].lib['robocjk.atomicElement.glyphVariations'].items()}
                    
    #             # lInfos = {axis2layerName[axisName]:v for axisName, v in aes['coord'].items()}
    # #            print(ae['coord'])
    #             for ae in aes.values():
    #                 glyph = ae[0]
    #                 print(glyph)
    #                 db.save()
    #                 self._drawGlyph(glyph)
    #                 db.restore()
            db.restore()
            db.restore()
            caption = db.FormattedString(txt='%s-axis' %(nbAxes), font="GrtskMega-Medium", fontSize=14, align="left")
            db.textBox(caption, (10, 10, W-20, 20))
        pdfData = db.pdfImage()
