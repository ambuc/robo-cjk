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
import os
from mojo.roboFont import *
from mojo.UI import PostBannerNotification
from views import designView
from resources import deepCompoMasters_AGB1_FULL
from utils import files
from utils import git
reload(designView)
reload(files)
reload(git)
reload(deepCompoMasters_AGB1_FULL)

class DesignController(object):
    def __init__(self, RCJKI):
        self.RCJKI = RCJKI
        self.interface = None
        self.characterSet = None
        # self.characterSet = None
        self.fontsList = []
        
    def launchDesignInterface(self):
        self.setCharacterSet()
        if not self.interface:
            self.RCJKI.resetController()
            self.RCJKI.designStep = "_design_glyphs"
            self.interface = designView.DesignWindow(self)
            self.loadProjectFonts()

    def setCharacterSet(self):
        rootfolder = os.path.split(self.RCJKI.projectFileLocalPath)[0]
        gitEngine = git.GitEngine(rootfolder)
        user = gitEngine.user()
        LockedGlyphsList = self.RCJKI.collab._userLocker(user).glyphs["_design_glyphs"]

        self.characterSet = "".join([self.RCJKI.characterSets[key]['Basic'] for key in self.RCJKI.project.script])
        self.characterSet += "".join([chr(int(e.split('uni')[1], 16)) for e in LockedGlyphsList if e not in self.characterSet])
        # self.characterSet += "".join([c for c in files.unique(toAdd) if c not in self.characterSet])

    def loadProjectFonts(self):
        self.fontsList = []
        self.RCJKI.allFonts = []
        
        for name, file in self.RCJKI.project.masterFontsPaths.items():
            path = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Masters', file)
            designSavepath = os.path.join(os.path.split(self.RCJKI.projectFileLocalPath)[0], 'Temp', 'Design', "".join(self.RCJKI.project.script), file)
            if not os.path.isdir(designSavepath):
                files.makepath(designSavepath)
                f = OpenFont(path, showInterface=False)
                nf = NewFont(familyName=f.info.familyName, styleName=f.info.styleName, showInterface=False)

                for c in self.characterSet:
                    glyphName = files.unicodeName(c)
                    if glyphName in f.keys():
                        
                        # # nf.newGlyph(glyphName)
                        # # nf[glyphName] = f[glyphName]     
                        # nf[glyphName].update()
                        nf.insertGlyph(f[glyphName])
                        
                            
                        # print(len(f[glyphName]), len(nf[glyphName]))
                nf.glyphOrder = [files.unicodeName(c) for c in self.characterSet]
                # f.close()
                nf.update()
                nf.save(designSavepath)
                # f.close()
                # self.RCJKI.allFonts.append({name:nf})
                # self.fontsList.append(name)
            else:
                nf = OpenFont(designSavepath, showInterface=False)
                f = OpenFont(path, showInterface=False)

                glyph0rder = []
                go = nf.glyphOrder
                for c in self.characterSet:
                    glyphName = files.unicodeName(c)
                    if not glyphName in glyph0rder:
                        glyph0rder.append(glyphName)
                        
                    if glyphName not in nf.keys() and glyphName in f.keys():
                        nf.insertGlyph(f[glyphName])

                    elif glyphName not in nf.keys():
                        nf.newGlyph(glyphName)
                        # if glyphName in f.keys():
                        #     nf.insertGlyph(f[glyphName])

                toDel = [n for n in go if chr(int(n[3:], 16)) not in self.characterSet]
                for n in toDel:
                    nf.removeGlyph(n)

                nf.glyphOrder = glyph0rder
                nf.save()


            self.RCJKI.allFonts.append({name:nf})
            self.fontsList.append(name)
            f.close()

        if self.interface:
            self.interface.w.fontsList.set(self.fontsList)

    def refreshCollabFromFile(self):
        head, tail = os.path.split(self.RCJKI.projectFileLocalPath)
        title, ext = tail.split('.')
        tail = title + '.roboCJKCollab'
        collabFilePath = os.path.join(head, tail)
        collabFile = open(collabFilePath, 'r')
        d = json.load(collabFile)
        for lck in d['lockers']:
            self.RCJKI.collab._addLocker(lck['user'], self.RCJKI.designStep)
        for lck in d['lockers']:
            locker = self.RCJKI.collab._userLocker(lck['user'])
            locker._addGlyphs(lck['glyphs'])

    def updateGlyphSetList(self):
        self.interface.w.glyphSetList.set(self.RCJKI.getGlyphSetList(self.characterSet, self.RCJKI.designStep))

    def injectGlyphsBack(self, glyphs, user):
        self.RCJKI.injectGlyphsBack(glyphs, user, self.RCJKI.designStep)
        self.RCJKI.saveProjectFonts()

    def pullMastersGlyphs(self):
        glyphs = []
        for c in self.characterSet:
            glyphName = files.unicodeName(c)
            if glyphName not in self.RCJKI.reservedGlyphs[self.RCJKI.designStep]:
                glyphs.append(glyphName)

        self.RCJKI.pullMastersGlyphs(glyphs, self.RCJKI.designStep)