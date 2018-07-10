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

#OS: Windows 10
#Word size of OS: 64-bit
#Word size of FreeCAD: 64-bit
#Version: 0.17.13509 (Git)
#Build type: Release
#Branch: releases/FreeCAD-0-17
#Hash: 0258808ccb6ba3bd5ea9312f79cd023f1a8671b7
#Python version: 2.7.14
#Qt version: 4.8.7
#Coin version: 4.0.0a
#OCC version: 7.2.0
#Locale: English/UnitedStates (en_US)

__title__ = "FCBmpImport"
__author__ = "TheMarkster"
__url__ = "https://github.com/mwganson/SvgToCylinder"
__Wiki__ = "https://github.com/mwganson/SvgToCylinder/blob/master/README.md"
__date__ = "2018.07.09" #year.month.date and optional a,b,c, etc. subrevision letter, e.g. 2018.10.16a
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

#use Draft.upgrade to turn the edges from the Sketch_On_Surface object into faces
Draft.upgrade(sketch)

#the faces will be conveniently selected for us when the draft upgrade process is complete
#we extrude them along the normal by taking the center of mass x and y values, and using z = 0
#works since we extrude symmetrically

sel = Gui.Selection.getSelectionEx()
for obj in sel:
    
    f = App.ActiveDocument.addObject('Part::Extrusion', 'Extrude')

    f.Base = App.ActiveDocument.getObject(obj.ObjectName)
    f.DirMode = "Custom"
    f.Dir = App.Vector(obj.Object.Shape.CenterOfMass.x,obj.Object.Shape.CenterOfMass.y,0).normalize()
    f.DirLink = None
    f.LengthFwd = 10.000000000000000
    f.LengthRev = 0.000000000000000
    f.Solid = False
    f.Reversed = False
    f.Symmetric = True
    f.TaperAngle = 0.000000000000000
    f.TaperAngleRev = 0.000000000000000
    Gui.ActiveDocument.Extrude.ShapeColor=Gui.ActiveDocument.Face.ShapeColor
    Gui.ActiveDocument.Extrude.LineColor=Gui.ActiveDocument.Face.LineColor
    Gui.ActiveDocument.Extrude.PointColor=Gui.ActiveDocument.Face.PointColor
    f.Base.ViewObject.hide()


Gui.SendMsgToActiveView("ViewFit")
App.ActiveDocument.recompute()




