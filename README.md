# SvgToCylinder

Run the macro without any open document.  It will ask you to select the .svg file you wish to import.  It creates a cylinder with the appropriate height and radius (more or less) and then maps the imported .svg file (as a sketch) to the face of the cylinder, using tools from the Curves workbench, which is a prerequisite for using the macro.

There is an online image converter that can create .svg files here:

<a href="https://image.online-convert.com/convert-to-svg">https://image.online-convert.com/convert-to-svg</a>

Limitations:

<strike>The extruded objects are extruded using the Part workbench Extrude tool, extruded in a custom direction equal to the normalized center of mass of the object (with z = 0) such that the extrude direction is always facing into the center of the cylinder (or even if it is backwards, no problem since we extrude symmetric to the plane).  The problem comes in with shapes that wrap around too much of the cylinder, which can lead to self-intersections since the direction of the extrusion is the same for all parts of the shape, regardless of where it is on the cylinder.  Fusing the extrude objects together works, but then cutting the fusion from the cylinder will fail in these cases.  You can check all of the extruded objects with Part CheckGeometry tool (with BOPCheck enabled -- Tools -> Edit Parameters -> Preferences -> Mod -> Part -> CheckGeometry -> RunBOPCheck = true) and (if they're not critical to the project) delete the ones that come up showing self-intersections.  You can also try changing the extrude length forward property to a smaller value (down from the default: 10mm), which might (but probably won't) help.</strike>  Now fixed as of 2018.07.18.

