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

flipX = vtk.vtkImageFlip()
flipX.SetInputConnection(imageInt.GetOutputPort())
flipX.SetFilteredAxis(0)

flipY = vtk.vtkImageFlip()
flipY.SetInputConnection(imageInt.GetOutputPort())
flipY.SetFilteredAxis(1)
flipY.FlipAboutOriginOn()

imageAppend = vtk.vtkImageAppend()
imageAppend.AddInputConnection(imageInt.GetOutputPort())
#imageAppend.AddInputConnection(flipX.GetOutputPort())
#imageAppend.AddInputConnection(flipY.GetOutputPort())
imageAppend.SetAppendAxis(0)


alphaChannelFunc = vtk.vtkPiecewiseFunction()
alphaChannelFunc.AddPoint(0, 0.0)
alphaChannelFunc.AddPoint(100, 0.01)
alphaChannelFunc.AddPoint(maxvalue, 0.8)

# This class stores color data and can create color tables from a few color points.
colorFunc = vtk.vtkColorTransferFunction()
colorFunc.AddRGBPoint(0.0, 0.865, 0.865, 0.865)
colorFunc.AddRGBPoint(maxvalue, 0.2313, 0.298, 0.753)

# The previous two classes stored properties.
# Because we want to apply these properties to the volume we want to render,
# we have to store them in a class that stores volume prpoperties.
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(colorFunc)
volumeProperty.SetScalarOpacity(alphaChannelFunc)
volumeProperty.ShadeOff()
#volumeProperty.ShadeOn()
volumeProperty.SetInterpolationTypeToLinear()

# This class describes how the volume is rendered (through ray tracing).
#compositeFunction = vtk.vtkVolumeRayCastCompositeFunction()
#mapper = vtk.vtkVolumeRayCastMapper()
#mapper.SetVolumeRayCastFunction(compositeFunction)
#mapper = vtkFixedPointVolumeRayCastMapper()
#mapper = vtk.vtkVolumeTextureMapper2D()
mapper = vtk.vtkGPUVolumeRayCastMapper()
#mapper.SetBlendModeToMaximumIntensity();
#mapper.SetSampleDistance(0.1)
#mapper.SetAutoAdjustSampleDistances(0)

# Add data to the mapper
mapper.SetInputConnection(imageAppend.GetOutputPort())

# The class vtkVolume is used to pair the previously declared volume as well as the properties to be used when rendering that volume.
volume = vtk.vtkVolume()
volume.SetMapper(mapper)
volume.SetProperty(volumeProperty)

# With almost everything else ready, its time to initialize the renderer and window
renderer = vtk.vtkRenderer()
# ... set background color to white ...
renderer.SetBackground(0,0,0)
# Other colors 
# nc = vtk.vtkNamedColors()
# renderer.SetBackground(nc.GetColor3d('MidnightBlue'))

# We add the volume to the renderer ...
renderer.AddVolume(volume)

# Adding the scalar bar color palette
scalarBar = vtkScalarBarActor()
scalarBar.SetTitle("Density")
scalarBar.SetLookupTable(colorFunc);
scalarBar.SetOrientationToVertical();
scalarBar.SetPosition( 0.85, 0.7 );
scalarBar.SetPosition2( 0.1, 0.3 );
propT = vtkTextProperty()
propT.SetFontFamilyToArial()
propT.ItalicOff()
propT.BoldOn()
propL = vtkTextProperty()
propL.SetFontFamilyToArial()
propL.ItalicOff()
propL.BoldOff()
scalarBar.SetTitleTextProperty(propT);
scalarBar.SetLabelTextProperty(propL);
scalarBar.SetLabelFormat("%5.0f")

renderer.AddActor(scalarBar)

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
axes.SetXAxisLabelText("");
axes.SetZAxisLabelText("");
axes.SetYAxisLabelText("");
 
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
