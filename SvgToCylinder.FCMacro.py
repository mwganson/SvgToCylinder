# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2018 <TheMarkster>                                      *
*                                                                         *
*   This file is a supplement to the FreeCAD CAx development system.      *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU Lesser General Public License (LGPL)    *
*   as published by the Free Software Foundation; either version 2 of     *
*   the License, or (at your option) any later version.                   *
*                                                                         *
*   This software is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
*   GNU Library General Public License at http://www.gnu.org/licenses     *
*   for more details.                                                     *
*                                                                         *
*   For more information about the GNU Library General Public License     *
*   write to the Free Software Foundation, Inc., 59 Temple Place,         *
*   Suite 330, Boston, MA  02111-1307 USA                                 *
*                                                                         *
***************************************************************************
"""

#OS: Windows 10 (10.0)
#Word size of OS: 64-bit
#Word size of FreeCAD: 64-bit
#Version: 0.19.20036 (Git)
#Build type: Release
#Branch: master
#Hash: 953ae1e6e917fa6860564c80fdc1f20950a5c0ac
#Python version: 3.6.8
#Qt version: 5.12.1
#Coin version: 4.0.0a
#OCC version: 7.3.0
#Locale: English/United States (en_US)


__title__ = "SvgToCylinder"
__author__ = "TheMarkster"
__url__ = "https://github.com/mwganson/SvgToCylinder"
__Wiki__ = "https://github.com/mwganson/SvgToCylinder/blob/master/README.md"
__date__ = "2020.03.15" #year.month.date and optional a,b,c, etc. subrevision letter, e.g. 2018.10.16a
__version__ = __date__

VERSION_STRING = __title__ + ' Macro v0.' + __version__



import FreeCAD
import Draft
import importSVG
import math
from PySide import QtCore, QtGui

sel = Gui.Selection.getSelectionEx()
if sel:
    obj = sel[-1]

name= QtGui.QFileDialog.getOpenFileName(QtGui.QApplication.activeWindow(),'Select .svg file','*.svg')[0]
if not name:
    raise StandardError('Exiting, no file selected.\n')
pixmap = QtGui.QPixmap(name)
height = pixmap.height()
width = pixmap.width()
importSVG.insert(name,"Unnamed")
Gui.SendMsgToActiveView("ViewFit")

#turn the inported objects into sketches
for obj in App.ActiveDocument.Objects:
    Draft.makeSketch(obj,autoconstraints=False)
    App.ActiveDocument.removeObject(obj.Name)

#merge the sketches into a single sketch
#can be done in gui, but does not appear to be accessible via python
#so we try to do it manually by adding the geometries and constraints 
#(not that there will be any constraints, but if later we re-use this code...)
sketch = App.ActiveDocument.addObject('Sketcher::SketchObject','CombinedSketch')
for obj in App.ActiveDocument.Objects:
    if obj.Label == sketch.Name:
        continue
    if hasattr(obj,'Geometry'):    
        for geo in obj.Geometry:
            sketch.addGeometry(geo)
    if hasattr(obj,'Constraints'):
        for con in obj.Constraints:
            sketch.addConstraint(con)
    App.ActiveDocument.removeObject(obj.Label)

#make a cylinder to map the sketch to

App.ActiveDocument.addObject("Part::Cylinder","Cylinder")
App.ActiveDocument.ActiveObject.Label = "Cylinder"
App.ActiveDocument.recompute()
Gui.SendMsgToActiveView("ViewFit")
App.ActiveDocument.getObject("Cylinder").Radius = str(width/2.0/math.pi)
App.ActiveDocument.getObject("Cylinder").Height = str(height)

Gui.Selection.clearSelection()
Gui.Selection.addSelection(App.ActiveDocument.getObject('Cylinder'))
Gui.Selection.addSelection(App.ActiveDocument.getObject(sketch.Name))

#now we use ChrisG's curves workbench map sketch to curved face tool

try:
    import Sketch_On_Surface
except:
    raise StandardError('You need to install the Curves workbench before we can take this process any further.\n')

sos = Sketch_On_Surface.SoS()
sos.Activated()
App.ActiveDocument.getObject("Sketch_On_Surface").Scale = True
sketch = App.ActiveDocument.getObject("Sketch_On_Surface")
App.ActiveDocument.recompute()


#the faces will be conveniently selected for us when the draft upgrade process is complete
#we extrude them along the normal by taking the center of mass x and y values, and using z = 0
#works since we extrude symmetrically



Draft.upgrade(sketch)

sketchNames=[]
sketchNames2=[]
sel = Gui.Selection.getSelectionEx()
for obj in sel:
   
    sketchNames.append(obj.ObjectName)
    Gui.ActiveDocument.getObject(sketchNames[-1]).Visibility=False
 

for ii in range(0,len(sketchNames)):
    Draft.scale([App.ActiveDocument.getObject(sketchNames[ii])],scale=FreeCAD.Vector(0.90,0.90,1.0),center=FreeCAD.Vector(0.0,0.0,0.0),copy=True)
    sketchNames2.append(App.ActiveDocument.ActiveObject.Name)
    Gui.ActiveDocument.getObject(sketchNames2[-1]).Visibility=False

for ii in range(0,len(sketchNames)):
    App.ActiveDocument.addObject('Part::Loft','Loft')
    App.ActiveDocument.ActiveObject.Sections=[App.ActiveDocument.getObject(sketchNames[ii]), App.ActiveDocument.getObject(sketchNames2[ii]), ]
    App.ActiveDocument.ActiveObject.Solid=True

App.ActiveDocument.getObject("Cylinder").Height = str(height*10.0/9.0)
Gui.SendMsgToActiveView("ViewFit")
App.ActiveDocument.recompute()




