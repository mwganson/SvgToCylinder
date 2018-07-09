"""
SvgToCylinder - a macro to map an svg file to the face of a cylinder.
By <TheMarkster>

Requires installation of the Curves workbench by ChrisG (from the Tools -> Addon Manager)

"""


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

App.ActiveDocument.removeObject('use12') #invalid for some reason, so chuck it

#turn the inported objects into sketches
for obj in App.ActiveDocument.Objects:
    Draft.makeSketch(obj,autoconstraints=True)
    App.ActiveDocument.removeObject(obj.Name)

#merge the sketches into a single sketch
#can be done in gui, but does not appear to be accessible via python
#so we try to do it manually by adding the geometries and constraints 
#(not that there will be any constraints, but if later we re-use this code...)
sketch = App.ActiveDocument.addObject('Sketcher::SketchObject','CombinedSketch')
for obj in App.ActiveDocument.Objects:
    if obj.Label == sketch.Name:
        continue
    for geo in obj.Geometry:
        sketch.addGeometry(geo)
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
    f.Dir = App.Vector(obj.Object.Shape.CenterOfMass.x,obj.Object.Shape.CenterOfMass.y,0)
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




