from __future__ import print_function
import h5py
import numpy as np
from vtk import *

hf = h5py.File('data/charge-plasma-000026.h5','r')
#hf = h5py.File('data/charge-beam-driver-000026.h5','r')
#hf = h5py.File('data/charge-He-electrons-000026.h5','r')

data = hf.get('charge')
axisz = hf.get('AXIS/AXIS1')
axisy = hf.get('AXIS/AXIS2')
axisx = hf.get('AXIS/AXIS3')

dz = (axisz[1]-axisz[0])/data.shape[2]
dy = (axisy[1]-axisy[0])/data.shape[1]
dx = (axisx[1]-axisx[0])/data.shape[0]

# This is for the spacing
skn = 1.0

print('Axis z range: [%.2f,%.2f]  Nbins = %i  dz = %.4f' % (axisz[0],axisz[1],data.shape[2],dz) )
print('Axis x range: [%.2f,%.2f]  Nbins = %i  dx = %.4f' % (axisx[0],axisx[1],data.shape[0],dx) )
print('Axis y range: [%.2f,%.2f]  Nbins = %i  dy = %.4f' % (axisy[0],axisy[1],data.shape[1],dy) )

print('Shape of the array: ', data.shape,'\nType: ',data.dtype,'\n')

# Changing to positive integer types (particle density)
# it is required by vtkVolumeRayCastMapper
npdata = np.array(data)
npdata = -100 * npdata
npdataint = np.array(npdata, dtype=np.uint8)

print('Shape of the array: ', npdataint.shape,'\nType: ',npdataint.dtype,'\n')

print('Rendering...')
            
minvalue = np.amin(npdataint)
maxvalue = np.amax(npdataint)

print('Min value = ',minvalue)
print('Max value = ',maxvalue)

# For VTK to be able to use the data, it must be stored as a VTK-image.
# This can be done by the vtkImageImport-class which
# imports raw data and stores it.
dataImporter = vtk.vtkImageImport()

# The array is converted to a string of chars and imported.
#data_string = npdataint.tostring()
#dataImporter.CopyImportVoidPointer(data_string, len(data_string))
dataImporter.SetImportVoidPointer(npdataint)

# The type of the newly imported data is set to float.
dataImporter.SetDataScalarTypeToUnsignedChar()
# Because the data that is imported only contains an intensity value,
# the importer must be told this is the case.
dataImporter.SetNumberOfScalarComponents(1)
# The following two functions describe how the data is stored
# and the dimensions of the array it is stored in.
dataImporter.SetDataExtent(0, npdataint.shape[2]-1, 0, npdataint.shape[1]-1, 0, npdataint.shape[0]-1)
dataImporter.SetWholeExtent(0, npdataint.shape[2]-1, 0, npdataint.shape[1]-1, 0, npdataint.shape[0]-1)
dataImporter.SetDataSpacing(skn*dz,skn*dy,skn*dx)
dataImporter.SetDataOrigin(skn*0.0,skn*axisy[0],skn*axisx[0])

# Operations on the data
imageInt = vtk.vtkImageCast()
imageInt.SetInputConnection(dataImporter.GetOutputPort())
imageInt.SetOutputScalarTypeToUnsignedChar()

threshold = vtk.vtkImageThreshold()
threshold.SetInputConnection(imageInt.GetOutputPort())
threshold.ThresholdBetween(110,200)
threshold.ReplaceInOn()
threshold.SetInValue(1)  # set all values in range to 1
threshold.ReplaceOutOn()
threshold.SetOutValue(0)  # set all values out range to 0
threshold.Update()

dmc = vtk.vtkDiscreteMarchingCubes()
dmc.SetInputConnection(threshold.GetOutputPort())
dmc.GenerateValues(1, 1, 1)
dmc.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(dmc.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1.0, 0.0, 0.0) # This does not change the color ??
actor.GetProperty().SetOpacity(0.1)

# With almost everything else ready, its time to initialize the renderer and window
renderer = vtk.vtkRenderer()
# ... set background color to black ...
renderer.SetBackground(0,0,0)
# Other colors 
# nc = vtk.vtkNamedColors()
# renderer.SetBackground(nc.GetColor3d('MidnightBlue'))

# We add the volume to the renderer ...
renderer.AddActor(actor)

axes = vtk.vtkAxesActor()
axes.SetShaftTypeToLine()
axes.SetTotalLength(skn*0.2*(axisx[1]-axisx[0]),skn*0.2*(axisy[1]-axisy[0]),skn*0.2*(axisz[1]-axisz[0]))
axes.SetNormalizedShaftLength(1, 1, 1)
axes.SetNormalizedTipLength(0.1, 0.1, 0.1)
propA = vtkTextProperty()
propA.SetFontFamilyToArial()
propA.ItalicOff()
propA.BoldOff()
propA.SetFontSize(1)
axisxact = axes.GetXAxisCaptionActor2D()
axisxact.SetCaptionTextProperty(propA)

# The axes are positioned with a user transform
#transform = vtk.vtkTransform()
#transform.Translate(0.0, 0.0, 0.0)
#axes.SetUserTransform(transform)
 
# the actual text of the axis label can be changed:
axes.SetXAxisLabelText("")
axes.SetZAxisLabelText("")
axes.SetYAxisLabelText("")
 
renderer.AddActor(axes)
 
window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
# ... and set window size.
window.SetSize(800, 600)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
#style = vtkInteractorStyleTrackballCamera();
#interactor.SetInteractorStyle(style);


interactor.Initialize()
interactor.Start()
