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
from functools import reduce

steps = {
        "_initialDesign_glyphs": 
            "dict", 
        "_design_glyphs": 
            "set", 
        "_deepComponentsEdition_glyphs": 
            "dict",
        "_deepComponentsInstantiation_glyphs": 
            "set",
        }   

scriptFallback = "Hanzi"

class RoboCJKCollab(object):
    def __init__(self):
        self._lockers = []
        self._user = ''

    @property
    def lockers(self):
        return [locker for locker in self._lockers]
    
    def _userLocker(self, user):
        l = list(filter(lambda locker: locker.user == user, self._lockers))
        if not l: return False
        return l[0]

    def _addLocker(self, user, glyphs={}, step=list(steps.keys())[0]):
        if user not in [locker.user for locker in self._lockers]:
            locker = Locker(self, user)
            l = Locker(self, user)
            l._setStep(step)
            l._addGlyphs(glyphs)
            self._lockers.append(l)
        else:
            locker = self._userLocker(user)
        return locker

    @property
    def _toDict(self):
        return {e: [l._toDict for l in getattr(self, e)] for e in dir(self) if not e.startswith('_')}

    def _fromDict(self, d):
        lockers = d['lockers']
        for locker in lockers:
            for step in locker['glyphs']:
                userLocker = self._addLocker(user = locker['user'], 
                    glyphs = locker['glyphs'][step], 
                    step = step
                    )
                userLocker._setStep(step)
                userLocker._setScript(locker['script'])
                userLocker._clearGlyphs()
                userLocker._addGlyphs(locker['glyphs'][step])

class Locker(object):
    def __init__(self, controller, user):
        self._controller = controller
        self.user = user
        self.script = scriptFallback

        for step, obj in steps.items():
            if obj == "set": setattr(self, step, set())
            elif obj == "dict": setattr(self, step, dict())

    @property
    def _allOtherLockedGlyphs(self):
        s = dict()
        for locker in self._controller._lockers:
            for step in steps:
                for glyph in getattr(locker, step):
                    if step not in s.keys(): s[step] = set()
                    if not self.glyphs[step]: continue

                    if glyph not in self.glyphs[step]:
                        s[step].add(glyph)

                if isinstance(getattr(locker, step), dict):
                    for glyph in getattr(locker, step).keys():
                        if self.glyphs[step].keys():
                            if glyph not in reduce(lambda x, y: x + y, list(self.glyphs[step].keys())):
                                s[step].add(glyph)

                    for value in getattr(locker, step).values():
                        for glyph in value:
                            if self.glyphs[step].values():
                                if glyph not in reduce(lambda x, y: x + y, list(self.glyphs[step].values())):
                                    s[step].add(glyph)
        return s
    
    @property
    def glyphs(self):
        return {step : list(getattr(self, step)) if isinstance(getattr(self, step), set) else getattr(self, step) for step in steps}

    def _addGlyphs(self, glyphs):

        if steps[self._step] == "set":
            for glyph in glyphs:
                if self._step in self._allOtherLockedGlyphs and glyph in self._allOtherLockedGlyphs[self._step]: continue
                getattr(self, self._step).add(glyph)


        elif steps[self._step] == "dict":

            for glyph, values in glyphs.items(): 
                if self._step in self._allOtherLockedGlyphs:
                    if glyph in self._allOtherLockedGlyphs[self._step]: continue
                    values = [v for v in values if v not in self._allOtherLockedGlyphs[self._step]]
                getattr(self, self._step)[glyph] = values
        # print(self._allOtherLockedGlyphs)

    def _clearGlyphs(self):
        if hasattr(self, self._step):
            delattr(self, self._step)

        if steps[self._step] == "set":
            setattr(self, self._step, set())

        elif steps[self._step] == "dict":
            setattr(self, self._step, dict())

    def _removeGlyphs(self, glyphs):
        for glyph in glyphs:
            if glyph in getattr(self, self._step):
                if steps[self._step] == "set":
                    getattr(self, self._step).remove(glyph)

                elif steps[self._step] == "dict":
                    del getattr(self, self._step)[glyph]

    def _setStep(self, step):
        self._step = step

    def _setScript(self, script):
        self.script = script

    @property
    def _toDict(self):
        return {e: getattr(self, e) for e in dir(self) if not e.startswith('_')}



import random
def testCollab(users):
    collab = RoboCJKCollab()
    for user in users:
        collab._addLocker(user)
    for locker in collab.lockers:
        l = ['glyph_%s'%random.randint(0, 10) for i in range(3)]
        locker._addGlyphs(l)
    for locker in collab.lockers:
        print(locker.user, 'locked:', locker._allOtherLockedGlyphs)

    # print(collab.__dict__["_lockers"][0].__dict__)
    print(collab._toDict)

if __name__ == "__main__":
    testCollab(['user1', 'user2', 'user3'])

