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


def refreshMainCanvas(func):
    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
            self.w.mainCanvas.update()
        except Exception as e:
            raise e
    return wrapper


def antiRecursive(an = 0, defret = None, initial = []):
    class decorate:
        def __init__(self):
            self.cs=initial
            
        def __call__(self, func):
            def wrapper(*args, **kwargs):
                id = args[an]
                if id in self.cs:
                    return defret
                else:
                    self.cs.append(id)
                    x = func(*args, **kwargs)
                    self.cs.remove(id)
                    return x
            return wrapper
    return decorate()
    

def sheetSafety(func):
    def caller(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except Exception as e:
            try:
                self.w.close()
            except Exception:
                pass
            raise e
    return caller